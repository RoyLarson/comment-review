"""Stage 2, gather: every page in scope, annotated and bound into one binder.

    gather(repo, targets, revise) -> Gathering
    page_in(path, repo) -> the page one file reads as, or why not
    unaddressed_report(missing), not_gathered(handed_in, unreadable) -> text

A page is one file -- its paragraphs in order among the code they sit with --
and `flows.page_for.page_of` builds one. This walks the files in scope, builds
their pages, binds them, and runs stage 3 over the paragraphs the binder holds.
The command prints and decides the exit code; nothing here does either.

!! The chain is data. `STEPS` is the sequence, each step reads and writes one
`Gathering`, and a new producer is one more element. The other half of stage
3 -- which files name the files under review -- is `flows.referrers`, run by
its own command, not a step here.

That is the whole subject: read every file in scope as a page, and bind the
pages for the agents.

! Most of a page holds no prose -- an empty `interval`, an `undocumented`
declaration, a bare `margin`. Those are addressable, so an `add` can cite the
place its missing sentence belongs in, and nobody owes them a record. Coverage
is over the paragraphs that hold prose.

**Every file handed in is gathered, or the command errors** -- a file it could
not read or parse, or a named file no reader claims, is named in `unreadable`,
and the command exits nonzero on it, because a paragraph missing from the binder
is a paragraph nobody reviews. The exception is a source file with no reader:
the binder lists it as freeform, unopened, for the reviewers to read as it
stands.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from comment_review import exceptions
from comment_review.binder.binder import Binder, bind
from comment_review.binder.page import Page
from comment_review.concordance.code_names import (
    WALKED_TREE_ROW,
    names_in,
    no_harvester,
)
from comment_review.flows.annotations_for import annotations_for
from comment_review.flows.page_for import page_of
from comment_review.flows.read_diagnostics import format_failure
from comment_review.flows.reading_context import context_for
from comment_review.flows.source import source_of
from comment_review.machine.repo import (
    git_ls_files,
    path_index,
    relative_to,
    tracked_paths,
    walk_files,
)
from comment_review.reading.addresser import SEPARATOR
from comment_review.reading.context import ReadingContext
from comment_review.reading.coordinates import SourceCoordinates
from comment_review.reading.diagnostics import (
    DetachedDocumentation,
    ReadDiagnostic,
    ReadFailure,
)
from comment_review.reading.language import INSTALLED_REGISTRY


@dataclass
class Gathering:
    """One gather, at whatever step of `STEPS` it has reached.

    ! The gaps are lists of reasons, not raises. A file that cannot be read is
    named in `unreadable` and the command decides the exit code, so the emit
    refuses on one record rather than the walk raising mid-way.

    ! `binder` is set by the bind step and has no default. A gather that
    stopped at a gap before it has none, and reading it is an
    `AttributeError`, which is the honest answer; a placeholder binder would
    be one that says nothing was gathered.
    """

    repo: Path
    targets: list[Path]
    revise: int
    absent: bool = False
    #: what the walk found that has a language record, or that the caller named
    files: list[Path] = field(default_factory=list)
    #: files the walk came across with no record -- reported, never refused
    no_record: list[str] = field(default_factory=list)
    #: source files with no reader, repo-relative posix, sorted, each once
    freeform: list[str] = field(default_factory=list)
    #: a file in scope that produced no page, a target that matched nothing, or a
    #: freeform file outside the repository, and why
    unreadable: list[str] = field(default_factory=list)
    #: the name corpus's gap rows, from `_name_corpus`: files it could not
    #: read or parse, files no harvester reads, and the walked-tree caveat
    unread: list[str] = field(default_factory=list)
    #: what a read noted without refusing the file, one printable line per
    #: warning of the read, naming its file and line; the run proceeds and the
    #: command prints them
    warnings: list[str] = field(default_factory=list)
    pages: list[Page] = field(default_factory=list)
    binder: Binder = field(init=False)
    reading_contexts: dict[Path, ReadingContext] = field(default_factory=dict)


def _walk(g: Gathering) -> None:
    """Which files are in scope, and which targets named nothing."""
    # Each target is walked once; the matched-nothing test below reads these lists.
    by_target = {t: sorted(walk_files(t)) for t in g.targets}
    named = {t.resolve() for t in g.targets if t.is_file()}
    freeform = set()

    # This loop tells a named file from a found one. A file the caller named is
    # refused when nothing can read it; a file the walk came across is reported
    # and skipped, because a directory holds READMEs and lockfiles and refusing
    # on those makes the form unusable. A source file with no reader is neither:
    # it is listed for the reviewers, named or found, and never opened, so a
    # binary cannot fail the gather.
    for path in sorted({f for found in by_target.values() for f in found}):
        if INSTALLED_REGISTRY.for_path(path) is not None:
            g.files.append(path)
        elif INSTALLED_REGISTRY.is_freeform(path):
            rel = _repo_relative(path, g.repo)
            # A page outside the repo is refused at the write; nothing writes a
            # freeform path through that check, so it is refused here. Resolved,
            # because a path relative to the cwd can read as inside the repo.
            if not path.resolve().is_relative_to(g.repo):
                g.unreadable.append(f"{rel} (outside the repository)")
            else:
                freeform.add(rel)
        elif path.resolve() in named:
            g.files.append(path)
        else:
            g.no_record.append(path.as_posix())
    g.freeform = sorted(freeform)
    # A path argument that matched no file joins `unreadable`, so a typo errors
    # on the same rule every other gap does.
    g.unreadable.extend(
        f"{t.as_posix()} (matched no files)"
        for t, found in by_target.items()
        if not found
    )


def _pages(g: Gathering) -> None:
    """One page per file in scope, or the reason there is none."""
    for path in g.files:
        got = page_in(path, g.repo)
        if isinstance(got, str):
            g.unreadable.append(got)
            continue
        g.reading_contexts[path.resolve()] = got.reading
        g.pages.append(got)
        rel = got.path
        located = [w for w in got.read.warnings if w.span is not None]
        if located:
            coordinates = SourceCoordinates(got.text)

            # The phrase is the warning's code as words, then the owner a
            # detached doc was written for.
            g.warnings.extend(
                f"warning: {rel}:{coordinates.position(w.span.start).line}:"
                f" {w.code.replace('-', ' ')}{_owner(w)}"
                for w in located
                if w.span is not None
            )


def page_in(path: Path, repo: Path) -> Page | str:
    """One file in scope read as a page, addressed against `repo`.

    Returns:
        The page, or the reason there is none as the gather prints it.
    """
    context = context_for(path)
    if isinstance(context, ReadFailure):
        return format_failure(context, path=path.as_posix())
    source = source_of(path)
    if isinstance(source, ReadFailure):
        return format_failure(source, path=path.as_posix())
    # !! Every paragraph's path is repo-relative where its file is under `repo`;
    # one outside it keeps the path as passed, which `_repo_relative` explains.
    # It is what `--repo` is for: the binder, the file lists and every citation
    # a reviewer writes all resolve against that root, so a paragraph carrying
    # an absolute path is a paragraph no consumer can place: joined to another
    # root, an absolute right-hand side wins, and a write lands on the source
    # file.
    rel = _repo_relative(path, repo)
    # !! A path holding the separator cannot be addressed, so it is a gap and not
    # a paragraph with a broken name. `flatten` joins segments on `:`, which
    # Windows forbids in a filename; POSIX forbids only `/` and NUL, so a POSIX
    # checkout can hold `a:b.py`, whose address would be the address of `a/b.py`.
    #
    # ! It reads the repo-relative path, which is the one addressed. The absolute
    # path holds a colon on every Windows run -- the drive letter -- so checking
    # `path` here refuses the whole tree.
    if SEPARATOR in rel:
        return f"{rel} (a path may not hold '{SEPARATOR}')"
    # ! The repo-relative path goes in, so the page comes back addressed against
    # the root every citation resolves to.
    got = page_of(path, rel=rel, source=source, reading_context=context)
    if isinstance(got, ReadFailure):
        return format_failure(got, path=rel)
    return got


def _owner(warning: ReadDiagnostic) -> str:
    """The owner a detached doc was written for, as the warning line ends it."""
    if not isinstance(warning, DetachedDocumentation):
        return ""
    if warning.owner_line is None:
        return " (owner: module)"
    return f" (owner on line {warning.owner_line})"


def _annotations(g: Gathering) -> None:
    """Stage 3, over every paragraph the binder holds."""
    # The gather's one `git ls-files`; both indexes are built from it.
    rels = git_ls_files(g.repo)
    known, g.unread = _name_corpus(g.repo, tracked_paths(g.repo, rels))
    annotations_for(g.binder.paragraphs, known, path_index(g.repo, rels), g.repo)


def _name_corpus(repo: Path, tracked: set[Path] | None) -> tuple[set[str], list[str]]:
    """Every name the tree defines, and the rows naming every gap in it.

    A corpus built from raw text contains the comments being checked, so every
    obituary resolves against itself and the check always passes; the names
    come from each Python file's AST instead. A file that cannot be read or
    parsed is a gap row, because a hole in the corpus turns every symbol
    defined only there into a false obituary.

    ! Tracked files only, when git can say which. A vendored, generated or
    gitignored tree under the repo root otherwise donates its whole namespace,
    so a symbol the repo defines nowhere resolves alive. That failure is silent
    and one-sided: it can hide an obituary, and manufactures none.

    Args:
        repo: the root to harvest.
        tracked: absolute paths git reports as tracked, or None when git could
            not answer -- then the whole tree is walked and a gap row says so.

    Returns:
        The defined names, and the gap rows: `NO_HARVESTER` rows are known
        holes, the `WALKED_TREE` row is a caveat about the whole corpus, and
        any other row is a file that could not be read or parsed.
    """
    names: set[str] = set()
    unread = [WALKED_TREE_ROW] if tracked is None else []
    for path in walk_files(repo):
        if tracked is not None and path.resolve() not in tracked:
            continue
        gap = no_harvester(path)
        if gap is not None:
            unread.append(gap)
            continue
        try:
            names |= names_in(path, path.read_text(encoding="utf-8"))
        except exceptions.PARSE_ERRORS as e:
            unread.append(f"{path.as_posix()} ({type(e).__name__})")
    return names, unread


def _bind(g: Gathering) -> None:
    """The binder, with the root it was read from stated relative to the cwd."""
    # !! Relative to `Path.cwd()`. `str(repo)` on the resolved path would put
    # a native absolute path -- `C:\\Users\\<name>\\projects\\...` on Windows --
    # into an artifact that is handed to agents and kept as evidence, beside
    # `pages[].path` values that are repo-relative posix, written by
    # `_repo_relative` below.
    #
    # ! `machine.repo.relative_to` owns the two cases this line must not
    # carry: the `..` walk to a revise root outside the checkout, and two
    # different drives, where no relative path exists at all.
    root = relative_to(g.repo, Path.cwd()).as_posix()
    g.binder = bind(
        g.pages,
        read_from={"root": root, "revise": g.revise},
        absent=g.absent,
        freeform=tuple(g.freeform),
    )


#: The chain, in the order it runs. Each step reads the `Gathering` the steps
#: before it filled and writes its own fields; a new producer is a new element.
#: A step that names a gap in `unreadable` is the last one that runs.
STEPS: tuple[Callable[[Gathering], None], ...] = (_walk, _pages, _bind, _annotations)


def gather(
    repo: Path,
    targets: list[Path],
    revise: int,
    absent: bool = False,
) -> Gathering:
    """Every page under `targets`, annotated and bound, with the gaps named.

    Args:
        repo: the root every citation resolves against, resolved.
        targets: the files and directories in scope, as the caller spelled them.
        revise: the revise `repo` is -- 0 for the original, a later stage's
            number for a revise root pulled after it. Stamped into `read_from`.
        absent: carry the empty places too -- see the command's
            `--include-absent`.

    Returns:
        The `Gathering` the steps wrote to, up to the first that named a gap
        in `unreadable`. `binder` is set when no step did.
    """
    g = Gathering(repo, targets, revise, absent)
    for step in STEPS:
        step(g)
        if g.unreadable:
            break
    return g


def _repo_relative(path: Path, repo: Path) -> str:
    """`path` as `repo` sees it: posix and relative where it is under `repo`.

    Args:
        path: the file gathered.
        repo: the root every citation resolves against.

    Returns:
        The posix path relative to `repo`. A file not under `repo` keeps the
        path as it was passed, unresolved -- the command joins each argument to
        the resolved repo, so `--repo /r ../other/x.py` records `/r/../other/x.py`.
        There is no relative-to-`repo` form of such a file and inventing one with
        `..` would hand a consumer a path that escapes the root it was given, so
        it is passed through and the consumers refuse it: `flows/proof_setter.py`
        writes nothing for a page path that is not relative to the repository.
    """
    try:
        return path.resolve().relative_to(repo).as_posix()
    except ValueError:
        return path.as_posix()


def unaddressed_report(missing: list[str]) -> str:
    """What to say about a gather whose paragraphs cannot be cited.

    It names them as well as counting them: a reader has to know which file to
    look at, and the count alone sends them through the whole binder.
    """
    rows = "\n".join(f"  {line}" for line in missing)
    plural = "paragraph" if len(missing) == 1 else "paragraphs"
    return (
        f"{len(missing)} {plural} carry NO ADDRESS, so nothing can cite them\n"
        f"and the stage-5 gate would count them as nobody's:\n{rows}\n"
        "A binder with no `original_start` cannot name a gap. Re-run gather."
    )


def not_gathered(handed_in: int, unreadable: list[str]) -> str:
    """The refusal, worded once."""
    listed = "\n".join(f"    {u}" for u in unreadable)
    return (
        f"NOT GATHERED -- these are gaps, not passes:\n{listed}\n"
        f"ERROR: {len(unreadable)} of {handed_in} files handed in were not"
        " gathered. Every file is gathered or this errors."
    )
