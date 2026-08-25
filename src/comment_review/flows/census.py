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

from pathlib import Path

from comment_review.reading.lexer import Paragraph


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
