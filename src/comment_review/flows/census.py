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

from collections.abc import Iterable
from pathlib import Path

from comment_review.reading.paragraph import Paragraph


def carried(page: Iterable[Paragraph]) -> list[Paragraph]:
    """The paragraphs a census HANDS OVER. A fence is not one of them.

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

    ! MEASURED, before this: `census --json` over a ten-line file emitted THREE
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
        path: the file censused.
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
