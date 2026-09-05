"""Stage 2, GATHER: every page in scope, annotated and bound into one binder.

    gather(repo, targets, revise) -> Gathering

A page is one file -- its paragraphs in order among the code they sit with --
and `flows.page_for.page_of` builds one. This walks the files in scope, builds
their pages, runs stage 3 over the paragraphs they carry, and binds the pages.
The command prints and decides the exit code; nothing here does either.

!! THE CHAIN IS DATA. `STEPS` is the sequence, each step reads and writes one
`Gathering`, and a step that does not exist yet -- `references_for`, the other
half of stage 3 -- is one more element. `TODO/census-should-be-a-chain-of-
producers.md` T2. ! It was the body of the command until this landed, which
is what `TODO/the-flow-lives-in-the-command.md` T2 named.

!! THAT IS THE WHOLE SUBJECT: take the output of every page and put it in the
form the agents read. It built one file's paragraphs AND addressed them AND
aggregated them until 2026-08-20, which is three subjects and why it ran to
1,759 lines. ! Which form reads BEST is measurable -- formats can be compared
against hazard recall -- and until one is measured no claim about it ships.
See `TODO/census-emits-no-page.md`.

! Most of a page holds no prose -- an empty `interval`, an `undocumented`
declaration, a bare `margin`. Those are ADDRESSABLE, so an `add` can cite the
place its missing sentence belongs in, and nobody owes them a record. Coverage
is over the paragraphs that HOLD prose.

**Every file handed in is gathered, or the command errors** -- a file it could
not read or parse, or whose suffix has no language record, is named in
`unreadable`, and the command exits nonzero on it, because a paragraph missing
from the binder is a paragraph nobody reviews.

! NO TIER IS REPORTED PER RUN OR STAMPED ON A PLACE, since 2026-08-24. This
counted a `tier` field on every paragraph and printed one line from it; the
field is gone -- Roy: *"their level gets dropped entirely. Not necessary and the
parser tier isn't long for this world."* ! `--languages` still lists which tier
each LANGUAGE reaches, which is a fact about the language rather than a fact
about a place, and is where to look when a file's reader could not answer.
"""

from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from pathlib import Path

from comment_review.binder.binder import Binder, bind
from comment_review.binder.page import Page
from comment_review.concordance.code_names import code_names
from comment_review.flows.annotations_for import annotations_for
from comment_review.flows.page_for import page_of, source_of
from comment_review.machine.repo import (
    path_index,
    relative_to,
    tracked_paths,
    walk_files,
)
from comment_review.reading.addresser import SEPARATOR
from comment_review.reading.lexer import language_for
from comment_review.reading.paragraph import Paragraph


@dataclass
class Gathering:
    """One gather, at whatever step of `STEPS` it has reached.

    ! THE GAPS ARE LISTS OF REASONS, NOT RAISES. A file that cannot be read is
    named in `unreadable` and the command decides the exit code, so the text
    listing and the `--json` emit refuse on one record rather than two.

    ! `binder` IS SET BY THE LAST STEP AND HAS NO DEFAULT. Reading it before
    the chain has run is an `AttributeError`, which is the honest answer; a
    placeholder binder would be one that says nothing was gathered.
    """

    repo: Path
    targets: list[Path]
    revise: int
    absent: bool = False
    #: what the walk found that has a language record, or that the caller NAMED
    files: list[Path] = field(default_factory=list)
    #: files the walk came across with no record -- reported, never refused
    no_record: list[str] = field(default_factory=list)
    #: a named file that produced no page, and why
    unreadable: list[str] = field(default_factory=list)
    #: files the name corpus could not read, from `code_names`
    unread: list[str] = field(default_factory=list)
    pages: list[Page] = field(default_factory=list)
    #: what the pages carry, flat, in page order -- see `carried`
    paragraphs: list[Paragraph] = field(default_factory=list)
    binder: Binder = field(init=False)


def _walk(g: Gathering) -> None:
    """Which files are in scope, and which targets named nothing."""
    # ! WALKED ONCE PER TARGET. The emptiness test below re-walked every tree a
    # second time to ask `not any(walk_files(t))`, which this already knows.
    by_target = {t: sorted(walk_files(t)) for t in g.targets}
    # !! NAMED, AS AGAINST FOUND -- the distinction the walk is no longer making.
    # A file the caller NAMED is refused when nothing can read it; a file the
    # walk came across is reported and skipped, because a directory holds
    # READMEs and lockfiles and refusing on those makes the form unusable.
    named = {t.resolve() for t in g.targets if t.is_file()}
    for path in sorted({f for found in by_target.values() for f in found}):
        if language_for(path) is None and path.resolve() not in named:
            g.no_record.append(path.as_posix())
        else:
            g.files.append(path)
    # A path argument that matched no file joins `unreadable`, so a typo errors
    # on the same rule every other gap does.
    g.unreadable.extend(
        f"{t.as_posix()} (matched no files)"
        for t, found in by_target.items()
        if not found
    )


def _pages(g: Gathering) -> None:
    """One page per file in scope, or the reason there is none."""
    # !! THE PAGES ARE KEPT, NOT ONLY THEIR PARAGRAPHS. A binder names the file
    # ONCE PER PAGE and the rows sit under it, so the bind needs the page --
    # while the LISTING still numbers one flat run. Both are built from this
    # same walk, which is what stops the two disagreeing about what was
    # gathered.
    for path in g.files:
        source, why = source_of(path)
        if source is None:
            g.unreadable.append(f"{path.as_posix()} ({why})")
            continue
        # !! EVERY PARAGRAPH'S PATH IS REPO-RELATIVE. It is what `--repo` is for:
        # the binder, the file lists and every citation a reviewer writes all
        # resolve against that root, so a paragraph carrying an absolute path is a
        # paragraph no consumer can place. It happened whenever the run was handed
        # absolute file arguments, which is how a task agent that resolved its
        # own paths would call this.
        #
        # !! Measured 2026-08-17 on the galley command -- `docs/history.md`: it
        # joined `out / paragraph["path"]`, and in Python an absolute right-hand
        # side WINS, so it wrote over the source file, put nothing under
        # `--out`, and printed that it had succeeded. The module whose one
        # promise is "nothing under `--repo` is touched" was editing the tree
        # under review.
        #
        # ! A file outside the repo keeps the path AS IT WAS PASSED -- see
        # `_repo_relative`, which says what that means. `flows/proof_setter.py`
        # refuses such a page rather than guessing where it belongs:
        # `repo.can_escape` reads the binder's page paths before any file is
        # opened.
        # ! HOISTED. `_repo_relative` calls `Path.resolve()`, a filesystem
        # call, and both arguments are the same for every paragraph of a file.
        # Measured 2026-08-18: 120 us a call, so one 793-paragraph file spent
        # 95 ms resolving one path 793 times.
        rel = _repo_relative(path, g.repo)
        # !! A PATH HOLDING THE SEPARATOR CANNOT BE ADDRESSED, so it is a GAP
        # and not a paragraph with a broken name. `flatten` joins segments on `:`,
        # which Windows forbids in a filename; POSIX forbids only `/` and NUL,
        # so a POSIX checkout can hold `a:b.py`, whose address would be the
        # address of `a/b.py`. That is the collision the separator was chosen to
        # end -- it was `.` until 2026-08-19, and `a/b.py` and `a.b.py` shared
        # every address they had.
        #
        # ! IT READS THE REPO-RELATIVE PATH, WHICH IS THE ONE ADDRESSED. The
        # absolute path holds a colon on every Windows run -- the drive letter
        # -- so checking `path` here refuses the whole tree.
        if SEPARATOR in rel:
            g.unreadable.append(f"{rel} (a path may not hold '{SEPARATOR}')")
            continue
        # ! THE REPO-RELATIVE PATH GOES IN, so the page comes back addressed
        # against the root every citation resolves to. It was stamped afterwards
        # for as long as `page_for` returned an unaddressed page, which is
        # the split that let a direct caller receive half a page.
        try:
            got, why = page_of(path, rel=rel, source=source)
        except Exception as e:  # a parse failure is REPORTED, as a gap
            g.unreadable.append(f"{path.as_posix()} ({type(e).__name__}: {e})")
            continue
        if got is None:
            g.unreadable.append(f"{path.as_posix()} ({why})")
            continue
        # !! AN UNPARSED PAGE IS NOT A GATHERED FILE, AND IT ARRIVED AS ONE.
        # The `except` above cannot see this: `paragraphs_stdlib` CATCHES the
        # parse failure and returns a single `unparsed` paragraph rather than
        # raising, `page_for` then gives that page no cues and no addresses,
        # and `carried` hands over only paragraphs that HAVE one -- so even the
        # paragraph reporting the refusal is filtered away. The file was read,
        # produced nothing, and the run said success.
        #
        # !! MEASURED 2026-08-29, one file per run over one nine-line control:
        # the control gathered 11 paragraphs at exit 0, while a UTF-8 BOM, a
        # syntax error, a NUL byte and an unterminated string each gathered
        # **0 paragraphs AT EXIT 0**. The same control's DECODE failures --
        # latin-1 bytes, a UTF-16 BOM -- correctly exited 1, caught upstream.
        #
        # !! SO THE RUN REFUSED WHAT IT COULD NOT DECODE AND SILENTLY SKIPPED
        # WHAT IT COULD NOT PARSE. `CLAUDE.md` states the contract the
        # asymmetry breaks -- *every file handed in is gathered or the run
        # stops* -- and a file mid-refactor with a real syntax error is the
        # common case, not an exotic one: its prose reached no reviewer while
        # stdout reported a complete run.
        #
        # ! IT JOINS `unreadable`, which is what makes it as loud as the decode
        # failure: named on both the `--json` path and the text one, and exit
        # 1 from either. The reader's own message is the reason, so the file
        # says WHY it could not be read rather than merely that it was skipped.
        refused = next((b for b in got.paragraphs if b.kind == "unparsed"), None)
        if refused is not None:
            g.unreadable.append(f"{path.as_posix()} ({refused.text})")
            continue
        g.pages.append(got)
        g.paragraphs.extend(carried(got))


def _annotations(g: Gathering) -> None:
    """Stage 3, over everything the pages carry."""
    known, g.unread = code_names([g.repo], tracked_paths(g.repo))
    annotations_for(g.paragraphs, known, path_index(g.repo), g.repo)


def _bind(g: Gathering) -> None:
    """The binder, with the root it was read from stated relative to the cwd."""
    # !! RELATIVE TO `Path.cwd()`, RULED BY ROY 2026-08-28. This wrote
    # `str(repo)` on a RESOLVED path, so on Windows it emitted
    # `C:\\Users\\<name>\\projects\\...` into an artifact that is handed to
    # agents and kept as evidence -- beside `pages[].path` values that are
    # repo-relative posix, written by `_repo_relative` above.
    #
    # ! TWO CALLERS ALREADY DISAGREED before this: the command wrote a native
    # absolute path and `tests/helpers.py` wrote a relative one, for a field
    # whose whole purpose is a later stage COMPARING a revise root against
    # the original.
    #
    # ! `relpath` RATHER THAN `Path.relative_to`, because a revise root is a
    # temporary directory OUTSIDE the checkout -- `relative_to` raises there
    # and `relpath` walks up with `..`. The reader resolves this against its
    # own cwd, which is the same cwd the run was started from.
    #
    # !! `revise` REPLACED A HARDCODED `0`, TASK 10 OF
    # `.superpowers/sdd/2026-08-28-the-mark-and-the-revise/`. `--repo` could
    # already be pointed at a revise root -- `TODO/the-flow-assumes-every-
    # role-reads-at-once.md`'s own note that every read command already
    # takes a root -- but the NUMBER stamped into `read_from` was fixed at
    # 0 regardless, so a gather over a revise still reported the ORIGINAL's
    # number: indistinguishable from having read the original. There is no
    # default revise beyond the original's own 0; a caller states it, same
    # as `--repo`.
    # ! `machine.repo.relative_to` owns the two cases this line must not
    # carry: the `..` walk to a revise root outside the checkout, and two
    # different drives, where no relative path exists at all. Both are
    # measured there.
    root = relative_to(g.repo, Path.cwd()).as_posix()
    g.binder = bind(
        g.pages, read_from={"root": root, "revise": g.revise}, absent=g.absent
    )


#: The chain, in the order it runs. Each step reads the `Gathering` the steps
#: before it filled and writes its own fields; a new producer is a new element.
STEPS: tuple[Callable[[Gathering], None], ...] = (_walk, _pages, _annotations, _bind)


def gather(
    repo: Path, targets: list[Path], revise: int, absent: bool = False
) -> Gathering:
    """Every page under `targets`, annotated and bound, with the gaps named.

    Args:
        repo: the root every citation resolves against, resolved.
        targets: the files and directories in scope, as the caller spelled them.
        revise: the revise `repo` is -- 0 for the original, a later stage's
            number for a revise root pulled after it. Stamped into `read_from`.
        absent: carry the EMPTY places too -- see the command's
            `--include-absent`.

    Returns:
        The `Gathering` every step has written to. `binder` is set.
    """
    g = Gathering(repo, targets, revise, absent)
    for step in STEPS:
        step(g)
    return g


def carried(page: Iterable[Paragraph]) -> list[Paragraph]:
    """The paragraphs a gather HANDS OVER. A fence is not one of them.

    !! LEADING IS NOT PASSED TO THE AGENTS, and it was until 2026-08-24. Roy:
    *"The leading is not something that will be passed to the agents. The same
    as the extra record attributes. It gets dropped because there is nothing to
    rule on. It is for white space."*

    !! A FENCE TAKES NO ADDRESS, WHICH IS WHY IT LEAKED IN THE FIRST PLACE. Roy,
    2026-08-24: *"You don't put an address on a fence because it is what divides
    properties. The only thing we can do is say well there was a fence here
    before we did this there should be a fence here after we did this."* An
    address is postal -- *"The cue is the street name and number, the file is
    the city, and the rest is the folder structure and computer"* -- and the
    fence between two properties has no street number. Carried anyway, it
    arrived as a row whose `address` was `""`, and every consumer downstream had
    to test for that blank to discover the row was never a place.

    ! MEASURED, before this: `gather --json` over a ten-line file emitted THREE
    such rows, and the listing printed them as `@` with no cue after it. Over
    this repo's own `src/`, 422 of 9,459 paragraphs -- every one leading.

    ! THE PAGE KEEPS THEM. A fence still has to be set back, so `Page.leading`
    holds it as the edge it is, keyed by the place it FOLLOWS, and the
    compositor reaches it there by symbol. ! Nothing is lost by dropping it
    here, because NOTHING TRANSFERS FROM THE BINDER TO THE END -- the write path
    reloads the page from disk and takes only the address as a key.

    ! THE GATE IS UNAFFECTED, AND THE REASON IS THE FILTER BELOW. `unaddressed`
    reports paragraphs that lack an address, and this function hands over only
    the paragraphs that HAVE one -- a fence's address is `""`, so it never
    reaches the population that gate counts.
    """
    return [b for b in page if b.address]


def _repo_relative(path: Path, repo: Path) -> str:
    """`path` as `repo` sees it: posix, relative, no `..`.

    Args:
        path: the file gathered.
        repo: the root every citation resolves against.

    Returns:
        The posix path relative to `repo`. ! A file NOT under `repo` keeps the
        path AS IT WAS PASSED, which may itself be relative -- run from a
        subdirectory, `--repo /r ../other/x.py` records `../other/x.py`. There
        is no relative-to-`repo` form of such a file and inventing one with
        `..` would hand a consumer a path that escapes the root it was given,
        so it is passed through unresolved and the consumers refuse it:
        `flows/proof_setter.py` writes nothing for a page path that is not
        relative to the repository.
    """
    try:
        return path.resolve().relative_to(repo).as_posix()
    except ValueError:
        return path.as_posix()


def unaddressed_report(missing: list[str]) -> str:
    """What to say about a gather whose paragraphs cannot be cited.

    ! It names them rather than counting them: a reader has to know WHICH file
    to look at, and the count alone sends them through the whole listing.
    """
    rows = "\n".join(f"  {line}" for line in missing)
    plural = "paragraph" if len(missing) == 1 else "paragraphs"
    return (
        f"{len(missing)} {plural} carry NO ADDRESS, so nothing can cite them\n"
        f"and the stage-5 gate would count them as nobody's:\n{rows}\n"
        "A binder with no `original_start` cannot name a gap. Re-run gather."
    )


def not_gathered(files: list[Path], unreadable: list[str]) -> str:
    """The refusal, worded ONCE for both output modes.

    !! The reviewers are handed the binder, so a file missing from it is
    paragraphs nobody reviews and nothing downstream notices. `--json` used to
    return 0 with a SHORT array on exactly the input the text path refused --
    and `--json --out` is the route `SKILL.md` mandates for the binder stage 5
    parses, so the coverage check then certified every paragraph accounted for
    over paragraphs that were never collected.
    """
    listed = "\n".join(f"    {u}" for u in unreadable)
    return (
        f"NOT GATHERED -- these are gaps, not passes:\n{listed}\n"
        f"ERROR: {len(unreadable)} of {len(files)} files handed in were not"
        " gathered. Every file is gathered or this errors."
    )
