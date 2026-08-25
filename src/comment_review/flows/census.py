"""Stage 2, GATHER: every PAGE in scope, formatted for the agents.

    python census.py [--repo D] [--census-only] [--json] [--out PATH] <paths>

A page is one file -- its paragraphs in order among the code they sit with --
and `page.py` builds one. This walks the files in scope, stacks their pages, and
renders them into what a reviewer reads.

!! THAT IS THE WHOLE SUBJECT. Roy, 2026-08-20: *"the census's job should be to
take the output of all of the pages and reformat it into the (most) usable
format for the agents."* It built one file's paragraphs AND addressed them AND
aggregated them until then, which is three subjects and why it ran to 1,759
lines. ! *most* is subjective and MEASURABLE -- formats can be compared -- and
until one is measured against hazard recall the word does not ship. See
`TODO/census-emits-no-page.md`.

! Most of a page holds no prose -- an empty `interval`, an `undocumented`
declaration, a bare `margin`. Those are ADDRESSABLE, so an `add` can cite the
place its missing sentence belongs in, and nobody owes them a record. Coverage
is over the paragraphs that HOLD prose.

**Every file handed in is censused, or this errors** -- a file it could not read
or parse, or whose suffix has no language record, is named and the run exits
nonzero, because a paragraph missing from the census is a paragraph nobody
reviews.

Read-only. It calls `annotate.py` on each paragraph for stage 3, and `repo.py`
for the facts about the checkout that both need.

! NO TIER IS REPORTED PER RUN OR STAMPED ON A PLACE, since 2026-08-24. This
counted a `tier` field on every paragraph and printed one line from it; the
field is gone -- Roy: *"their level gets dropped entirely. Not necessary and the
parser tier isn't long for this world."* ! `--languages` still lists which tier
each LANGUAGE reaches, which is a fact about the language rather than a fact
about a place, and is where to look when a file's reader could not answer.
"""

import ast
from pathlib import Path

from ..binder.annotate import (
    SYMBOLISH,
)
from ..machine import exceptions
from ..machine.repo import (
    EXCLUDED_DIRS,
)
from ..reading.lexer import (
    NAMED_DEFS,
    Paragraph,
    language_for,
)


def emitted_row(b: Paragraph) -> dict:
    """One paragraph as the census EMITS it, which is not how it is held.

    !! THE PROSE LEAVES AS ONE STRING, NOT AS LINES. Ruled 2026-08-24 -- Roy:
    *"LLMs and the token parsers read this as a complete and coherent statement.
    They do not read this as the same thing: ['LLMs and the token', 'parsers
    read this as a', 'complete and coherent', 'statement']. It took my phone,
    which runs a token parser, to the last word to realise I was duplicating the
    sentence."* The four reviewers ARE token parsers and prose is what they
    judge, so fragments make every role reassemble the sentence before it can
    ask whether the sentence is TRUE -- paid four times a page.

    !! AND IT IS A CHANGE TO THE EMIT ALONE. `Paragraph.raw_lines` stays a list
    in memory and nothing on the write path moves. **How an agent's answer
    reaches the page is UNDECIDED** -- see `TODO/nothing-makes-the-fair-copy.md`
    -- and a field rename that reshaped the galley would be deciding it by
    accident. ! Attempted the other way 2026-08-24 and reverted: changing the
    stored field forced `_vacate` to clear a span, which is a ruling about what
    a `drop` DOES, made to keep tests green.

    ! `annotations` is a set and JSON has none, so it leaves sorted. Same
    reason, one line up: what a row IS on disk is stated here and nowhere else.
    """
    row = vars(b) | {
        "annotations": sorted(b.annotations),
        "raw_text": "\n".join(b.raw_lines),
    }
    row.pop("raw_lines", None)
    return row


def _walk(root: Path):
    """Every file under `root`. It ENUMERATES; it classifies nothing.

    !! IT FILTERED ON `BY_EXT` AND THAT WAS A SECOND POLICY. `main` already asks
    `language_for(path) is None` and REFUSES at exit 1 -- the caller asked for
    that file -- so the same question was answered in two places with two
    different consequences, and the silent one won for a directory. MEASURED
    2026-08-22 on a two-file directory: an unsupported file NAMED exits 1, the
    same file WALKED vanished at exit 0. `every file handed in is censused or
    this errors` was true of explicit paths and false of directories.

    ! SO THE WALK STOPPED DECIDING. Whether a file with no language record is a
    refusal or a note is the CENSUS's call, and it turns on something only the
    census knows: whether the path was NAMED or merely FOUND. A directory holds
    READMEs, images and lockfiles; refusing on those makes the form unusable,
    and skipping them in silence is the false completeness this warns about.

    ! `EXCLUDED_DIRS` STAYS, because it is not the same question. It is about
    where the walk may GO -- a vendored tree is not this repo's code at all --
    rather than about what a file is once found.
    """
    if root.is_file():
        yield root
        return
    for p in sorted(root.rglob("*")):
        if p.is_file():
            # !! RELATIVE to the root being walked. Matched against `p.parts`
            # this tested every ANCESTOR too, so a checkout living anywhere
            # under a directory called `venv`, `.venv`, `node_modules`,
            # `site-packages`, `__pycache__` or `.git` excluded ITSELF.
            # Measured 2026-08-17: `code_names` harvested 0 names from a repo
            # under `.../venv/myproject`, and nothing joined `unread`, so the
            # NOT CHECKED list stayed empty and the run read as complete --
            # every `names-a-symbol` a false obituary, handed to four reviewers
            # as settled fact.
            if not EXCLUDED_DIRS.intersection(p.relative_to(root).parts):
                yield p


# The two gaps in the name corpus that are NOT read failures, named so a caller
# can tell them apart from one. Every row `code_names` returns reads alike --
# `<path> (<reason>)` -- and a reporting caller that treated all of them as
# unreadable files told a polyglot repo that six files "could not be read" and
# then instructed the reader to wait for a list that can never empty.
NO_HARVESTER = "no name harvester for"
WALKED_TREE = "name corpus built by WALKING the tree"


def code_names(
    roots: list[Path], tracked: set[Path] | None = None
) -> tuple[set[str], list[str]]:
    """Every name the tree DEFINES, harvested from the AST.

    A corpus built from raw text contains the comments being checked, so every
    obituary resolves against itself and the check always passes. Unreadable
    files are RETURNED alongside the names: a hole in the corpus turns every
    symbol defined only there into a false obituary, which fails loud and wrong.

    ! TRACKED files only, when git can say which. A vendored, generated or
    gitignored tree under the repo root otherwise donates its whole namespace,
    so a symbol the repo defines nowhere resolves ALIVE. That failure is SILENT
    and one-sided: it can hide an obituary, and manufactures none.

    Args:
        roots: directories or files to harvest.
        tracked: absolute paths git reports as tracked, or None when git could
            not answer -- in which case the whole tree is walked and the caller
            is told, so a change in coverage arrives with the result.

    Returns:
        The set of defined names, and the rows naming every gap in it. A row
        holding `NO_HARVESTER` is a KNOWN hole and a row holding `WALKED_TREE`
        is a caveat about the whole corpus; anything else is a file this
        process genuinely could not read or parse. A caller that tells the
        three apart says so with those two constants -- the three read alike as
        prose, and a caller matching on the prose reclassifies them silently
        the next time this wording changes.
    """
    names: set[str] = set()
    unread: list[str] = []
    if tracked is None:
        unread.append(
            f"{WALKED_TREE} (not a git checkout, or git unavailable) -- "
            "untracked or vendored code may mask an obituary"
        )
    for root in roots:
        for p in _walk(root):
            if tracked is not None and p.resolve() not in tracked:
                continue
            lang = language_for(p)
            # ! A non-Python file is a KNOWN hole, reported as one. Parsed as
            # Python it came back `a.go (SyntaxError)`, which reads as "your
            # file is malformed" and sends a reviewer after an invented defect.
            # Liveness in these languages needs its own harvester; this names
            # the gap until there is one.
            if lang is None or lang.name != "python":
                name = lang.name if lang else "unknown"
                unread.append(f"{p.as_posix()} ({NO_HARVESTER} {name})")
                continue
            try:
                tree = ast.parse(p.read_text(encoding="utf-8"))
            except exceptions.PARSE_ERRORS as e:
                unread.append(f"{p.as_posix()} ({type(e).__name__})")
                continue
            names.add(p.stem)
            harvest_constants = not (p.name.startswith("test_") or "tests" in p.parts)
            for node in ast.walk(tree):
                if isinstance(node, NAMED_DEFS):
                    names.add(node.name)
                elif isinstance(node, ast.Name):
                    names.add(node.id)
                elif isinstance(node, ast.Attribute):
                    names.add(node.attr)
                elif isinstance(node, ast.arg):
                    names.add(node.arg)
                elif isinstance(node, ast.alias):
                    names.add((node.asname or node.name).split(".")[0])
                elif harvest_constants and isinstance(node, ast.Constant):
                    if isinstance(node.value, str) and SYMBOLISH.match(node.value):
                        names.add(node.value)
    return names, unread


def _repo_relative(path: Path, repo: Path) -> str:
    """`path` as `repo` sees it: posix, relative, no `..`.

    Args:
        path: the file censused.
        repo: the root every citation resolves against.

    Returns:
        The posix path relative to `repo`. ! A file NOT under `repo` keeps the
        path AS IT WAS PASSED, which may itself be relative -- run from a
        subdirectory, `--repo /r ../other/x.py` records `../other/x.py`. There
        is no relative-to-`repo` form of such a file and inventing one with
        `..` would hand a consumer a path that escapes the root it was given,
        so it is passed through unresolved and the consumers refuse it:
        `galley.py` writes nothing that lands outside `--out`.
    """
    try:
        return path.resolve().relative_to(repo).as_posix()
    except ValueError:
        return path.as_posix()


def _unaddressed(missing: list[str]) -> str:
    """What to say about a census whose paragraphs cannot be cited.

    ! It names them rather than counting them: a reader has to know WHICH file
    to look at, and the count alone sends them through the whole census.
    """
    rows = "\n".join(f"  {line}" for line in missing)
    plural = "paragraph" if len(missing) == 1 else "paragraphs"
    return (
        f"{len(missing)} {plural} carry NO ADDRESS, so nothing can cite them\n"
        f"and the stage-5 gate would count them as nobody's:\n{rows}\n"
        "A census with no `original_start` cannot name a gap. Re-run census.py."
    )


def _not_censused(files: list[Path], unreadable: list[str]) -> str:
    """The refusal, worded ONCE for both output modes.

    !! The reviewers are handed the census, so a file missing from it is paragraphs
    nobody reviews and nothing downstream notices. `--json` used to return 0
    with a SHORT array on exactly the input the text path refused -- and
    `--json --out` is the route `SKILL.md` mandates for the census stage 5
    parses, so the coverage check then certified every paragraph accounted for over
    paragraphs that were never collected.
    """
    listed = "\n".join(f"    {u}" for u in unreadable)
    return (
        f"NOT CENSUSED -- these are gaps, not passes:\n{listed}\n"
        f"ERROR: {len(unreadable)} of {len(files)} files handed in were not"
        " censused. Every file is censused or this errors."
    )
