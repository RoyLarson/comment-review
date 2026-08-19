"""The proposed text, SET AS FILES, so it can be read and censused like any tree.

    python galley.py --repo D --census census.json --edits edits.json --out DIR

A galley is the trial impression: the text set, but not yet made into pages, so
that it can be corrected before anything is committed. That is exactly what
this writes -- every paragraph a stage proposes to change, spliced into a copy of
its file under `--out`. Nothing under `--repo` is touched.

!! IT RENDERS; IT DOES NOT RULE. A stage that both produced the galley and
judged it would be MARK and APPLY in one actor, which is the separation the
pipeline exists to keep.

Two things need it, and they needed the same thing:

  round 2   A re-review rules on the SYNTHESISED paragraph -- text on no disk and
            in no census -- so `address_problem` refuses it and `edit_problem`
            measures one claim against one edit where the paragraph now holds
            several. Censusing the galley gives that text a real address and a
            real transcription, so every check in `verdicts.py` works on it
            UNCHANGED. The alternatives were a second record shape to hold in
            sync, or a flag that turns the checks off for the one text the
            author actually approves.
  stage 7a  What lands at 7b is a paragraph spliced into a file, and the splice is
            the first time anyone sees the two together. `git diff --no-index`
            over the galley shows the author what will land, including whether
            an adjacent paragraph was clipped -- which a `CHANGE` cannot show,
            because each one carries its own surrounding context.

! A SPLICE THAT CANNOT BE MADE IS REPORTED, NEVER GUESSED. A census range that
no longer matches the file, or two edits over one line, stops that file rather
than writing a galley nobody can trust.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from repo import READ_ERRORS, read_raw  # noqa: E402  -- path shim must run first


def line_endings(text: str) -> str:
    """The ending this text uses, as the joiner a rewrite must use.

    ! Taken from the file being spliced, not from the platform. A galley is
    diffed against its original; a rewrite that normalised the endings would
    report every line as changed and bury the prose edit. ! Which is why the
    caller reads with `repo.read_raw`: `read_text` would have collapsed the
    endings before this saw them.

    ! NOT `prove_unchanged.dominant_ending`, which answers a different
    question. That one names the ending a file MOSTLY uses, for a report; this
    one picks the ending to give a NEW line, and only that -- `splice` keeps
    every existing line's own ending, so on a mixed file the answer here
    decides nothing except what the replacement text is written with.
    """
    return "\r\n" if "\r\n" in text else "\n"


def splice(text: str, edits: list[tuple[int, int, int, str]]) -> str:
    """`text` with each `(start, end, column, replacement)` put in place.

    Args:
        text: the file as it reads now.
        edits: one per paragraph, 1-based and inclusive lines, in any order.
            `column` is 1-based into the FIRST line and is 0 for a paragraph
            that occupies its lines whole.

    Returns:
        The file with every edit applied.

    !! APPLIED IN DESCENDING ORDER, which is what makes the ranges mean
    anything. A replacement rarely has the same number of lines as what it
    replaces, so splicing top-down shifts every range below the one just
    written and each later edit lands further from where its census said. The
    caller has already refused overlaps, so descending order is exact.

    !! THE COLUMN IS WHAT MAKES THE `c` SERIES WRITABLE. A splice replaces whole
    lines, so a `patch` on `z = 3  # trailing` wrote `# reworded` over the
    statement -- measured 2026-08-18, in the galley a human is asked to approve.
    Keeping `line[: column - 1]` writes the prose and leaves the code. Roy,
    2026-08-19: *"c needs to be writeable. It is the reason c is not an
    extension of b."*

    ! A `drop` needs no special case, because the column is the END OF THE CODE
    and not the start of the prose: the kept head is the statement, with the
    separating whitespace already on the far side of it. A whole-line paragraph
    still loses its lines entirely, which is what an empty head means.
    """
    end_of_line = line_endings(text)
    # !! KEEPENDS, so a line nobody edited is re-emitted with the ending it
    # had. Joining split lines with one ending rewrote every line in the file:
    # on a MIXED file, editing line 1 converted the untouched LF line 2 to
    # CRLF, and the `git diff --no-index` that stage 7a exists for showed both
    # as changed. Measured 2026-08-18.
    lines = text.splitlines(keepends=True)
    ended = text.endswith(("\n", "\r"))
    for start, end, column, replacement in sorted(edits, reverse=True):
        # ! The kept head of the first line, WITHOUT its ending -- `lines` was
        # split `keepends`, so a line that still carries its CR/LF would put
        # that ending in the middle of the result whenever `column` reaches
        # past the text, which a `margin`'s column does by definition.
        head = lines[start - 1].rstrip("\r\n")[: column - 1] if column else ""
        body = replacement.splitlines()
        if body:
            body[0] = head + body[0]
        elif head:
            body = [head]
        # ! NEW lines get the file's ending, because they have none of their
        # own. That is the only place `line_endings` is consulted now.
        lines[start - 1 : end] = [line + end_of_line for line in body]
    out = "".join(lines)
    # ! A file that did not end in a newline still does not. An edit landing on
    # the last line, or appended after it, would otherwise add one.
    if not ended and out.endswith(end_of_line):
        out = out[: -len(end_of_line)]
    return out


def overlaps(edits: list[tuple[int, int, int, str]]) -> tuple[int, int] | None:
    """The first pair of edits sharing a line, or None.

    ! Two `CHANGE`s over one line have no defined result: each carries its
    surrounding paragraph, so the second would overwrite context the first wrote.
    """
    ordered = sorted(edits)
    for (a_start, a_end, _, _), (b_start, *_) in zip(
        ordered, ordered[1:], strict=False
    ):
        if b_start <= a_end:
            return (a_start, b_start)
    return None


def paragraph_matches(lines: list[str], paragraph: dict) -> bool:
    """Does the file still read the way the census recorded this paragraph?

    ! The census may be older than the file. Splicing a range whose content has
    moved writes the replacement over whatever is there now, which is the one
    failure a galley must not produce quietly.

    !! A PARAGRAPH THAT HOLDS NO PROSE IS CHECKED DIFFERENTLY, because it has no
    text to compare. What must still hold is that it is still EMPTY: every line
    of its EDIT range is blank. An `add` is the verdict that cites one, and its
    whole finding is that the place holds no prose -- so prose appearing there
    since the census is exactly the staleness that matters.

    ! Both kinds go this way. An `undocumented` declaration ADDRESSES the lines
    of the declaration it documents, so comparing its stored text -- it has
    none -- against those lines refused it every time. Measured 2026-08-18: 3
    such paragraphs in this repo's own tree made the addresser call a fresh census
    stale.

    ! Before this, `raw_lines` being empty answered False, which refused every
    `add` in the run. It read as a stale range and was a paragraph with nothing
    stored, and the message said the range no longer matched the census.
    """
    # !! THE EDIT RANGE, NOT THE ADDRESSING RANGE. A paragraph is ADDRESSED by every
    # line of its share of the gap, blanks included -- every line has an address
    # -- but `raw_lines` holds only the prose. Comparing the wider range against
    # the narrower text refused every prose paragraph in the tree.
    start, end = splice_range(paragraph)
    # !! A `c` PARAGRAPH IS CHECKED IN TWO HALVES, because the census stores both:
    # `anchor` is the code before it and `raw_lines` is everything from its
    # column on. Together they are the physical line, so this compares the file
    # against what the census SAID rather than against a guess about which of
    # them it stored -- the two tiers stored different halves, and no single
    # comparison satisfied both.
    column = paragraph.get("edit_column", 0)
    if column > 0:
        if start < 1 or end > len(lines) or start > end:
            return False
        first = lines[start - 1]
        if first[: column - 1] != paragraph.get("anchor", ""):
            return False
        stored = paragraph.get("raw_lines") or [""]
        here = [first[column - 1 :], *lines[start:end]]
        return [ln.rstrip() for ln in here] == [ln.rstrip() for ln in stored]
    # !! CHECKED BEFORE THE RANGE GUARD, because a paragraph that holds no prose may
    # occupy NO LINE -- an absent docstring is at line 0 -- and the guard below
    # would refuse it for a range it is not entitled to have.
    if not paragraph.get("raw_lines"):
        # ! Nothing was stored, so what must still hold is that the place is
        # still EMPTY -- every line of its edit range is blank.
        if start < 1 or end > len(lines) or start - 1 > end:
            return False
        return all(not ln.strip() for ln in lines[start - 1 : end])
    if start < 1 or end > len(lines) or start > end:
        return False
    stored = paragraph["raw_lines"]
    return [ln.rstrip() for ln in lines[start - 1 : end]] == [
        ln.rstrip() for ln in stored
    ]


def unanswerable(paragraphs: list[dict]) -> str | None:
    """Can this census answer what the galley has to ask of it?

    !! A CENSUS IS REFUSED WHOLE, not defaulted per paragraph. Every per-field
    default is a guess about a file this tool is about to overwrite, and the
    one guess that was made -- an absent column means "occupies whole lines" --
    put back the defect the field was added to remove, because a trailing
    comment's stored text is the file's whole line and the staleness check
    passes it.

    ! It asks the PARAGRAPHS rather than a version stamp, because `census.py
    --json` emits a bare list and has nowhere to put one. The field's presence
    is the version.

    Args:
        paragraphs: the census, as `census.py --json` emits it.

    Returns:
        One sentence naming what is missing, or None.
    """
    for field in ("edit_column", "edit_start", "edit_end"):
        if any(field not in b for b in paragraphs):
            return (
                f"this census carries no `{field}` -- it predates the field that"
                " says which paragraphs can be spliced. Re-run census.py"
            )
    return None


def splice_range(paragraph: dict) -> tuple[int, int]:
    """The 1-based inclusive lines `splice` replaces to realise this paragraph's edit.

    !! THE CENSUS DECIDES THIS, NOT THIS MODULE. A prose paragraph is replaced and
    an empty interval is inserted into, and there are more kinds than those two
    -- a trailing comment shares its line with code, and an `undocumented`
    declaration is a pure insertion. Branching on kind here would have to grow a
    case for each, and the census already knows which lines each paragraph's text
    occupies.

    ! It reads `edit_start`/`edit_end`, falling back to `start`/`end` for a
    census taken before those existed. The fallback is why this function is
    still here rather than inlined.

    !! AN INTERVAL'S RANGE IS THE GAP'S OWN LINES, so a replacement REPLACES
    them -- blank lines included. Editing a two-blank-line gap with one line of
    prose leaves one line where three were, and the separation is gone. That is
    what an edit to that paragraph means, and `reviewer-brief.md` tells a reviewer
    so; it is written here because the arithmetic does not show it.

    Args:
        paragraph: one census entry.

    Returns:
        `(start, end)` for `splice`.
    """
    # ! No fallback. `unanswerable` has already refused a census without the
    # fields, so a missing one here is a bug and should raise rather than be
    # guessed at -- and the guess had a trap: `or` reads a legitimate edit
    # range ending at 0, the gap above the first line, as absent.
    return (paragraph["edit_start"], paragraph["edit_end"])


def main() -> int:
    """Write a galley of every file an edit touches, and report what refused."""
    # A Windows console is cp1252; one non-ASCII glyph in a report kills the run.
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", default=".", help="repo root the census resolves against")
    ap.add_argument("--census", required=True, help="the JSON census these edits cite")
    ap.add_argument(
        "--edits",
        required=True,
        help='JSON: {"<census index>": "<replacement paragraph>"}',
    )
    ap.add_argument("--out", required=True, help="directory the galley is written to")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    out = Path(args.out).resolve()
    try:
        census = json.loads(Path(args.census).read_text(encoding="utf-8"))
        edits = json.loads(Path(args.edits).read_text(encoding="utf-8"))
    except READ_ERRORS as e:
        print(f"CANNOT READ ({type(e).__name__}) -- no galley written")
        return 2
    except json.JSONDecodeError as e:
        print(f"CANNOT PARSE as JSON ({e}) -- no galley written")
        return 2

    paragraphs = census["paragraphs"] if isinstance(census, dict) else census
    stale_census = unanswerable(paragraphs)
    if stale_census:
        print(f"CANNOT USE {args.census}: {stale_census}")
        return 2
    # Group by file, because a splice is a whole-file rewrite. The CENSUS PARAGRAPH
    # travels with each edit: its `raw_lines` is the only record of what the
    # file said when the reviewers read it, and comparing the file to itself
    # would make the staleness check below unable to fail.
    # ! `(replacement, paragraph)`. It held the paragraph's `start` and `end` alongside
    # the paragraph that carries them, and each consumer destructured away the half
    # the other used.
    by_path: dict[str, list[tuple[str, dict]]] = {}
    refused = 0
    for key, replacement in edits.items():
        try:
            index = int(key)
        except (TypeError, ValueError):
            print(f"REFUSED  paragraph {key!r}: not a census index")
            refused += 1
            continue
        if not 1 <= index <= len(paragraphs):
            print(f"REFUSED  paragraph {index}: outside the census")
            refused += 1
            continue
        paragraph = paragraphs[index - 1]
        by_path.setdefault(paragraph["path"], []).append((replacement, paragraph))

    written = 0
    for rel, file_edits in sorted(by_path.items()):
        # !! REFUSE ANYTHING THAT WOULD LAND OUTSIDE `--out`, BEFORE READING.
        # `out / rel` is the source path itself when `rel` is absolute --
        # Python's join lets an absolute right-hand side win -- and an absolute
        # path is exactly what a census taken before that was fixed carries.
        # Measured 2026-08-17: the galley overwrote the file under review,
        # wrote nothing under `--out`, and reported success.
        #
        # ! FIRST, because it needs neither the file nor the census. Run last,
        # it read and validated the out-of-tree file first -- so an unreadable
        # one was refused as `PermissionError`, which sends a reader to the
        # wrong problem. Checked on the RESOLVED path, so a `..` inside a
        # census path is refused by the same rule rather than a second one.
        target = (out / rel).resolve()
        if not target.is_relative_to(out):
            print(f"REFUSED  {rel}: would be written outside --out")
            refused += len(file_edits)
            continue
        source = repo / rel
        try:
            # !! READ RAW. `read_text` collapses every `\r\n` to `\n`, so
            # `line_endings` below would never see a CRLF file and every line
            # of the galley would differ from its original by its ending --
            # which is the whole thing this module is diffed for.
            text = read_raw(source)
        except READ_ERRORS as e:
            print(f"REFUSED  {rel}: {type(e).__name__}")
            refused += len(file_edits)
            continue
        lines = text.splitlines()
        # ! The range comes from the PARAGRAPH, not from the census numbers the
        # edit was grouped by: an interval is inserted into, not replaced.
        ranges = [
            (*splice_range(paragraph), paragraph["edit_column"], r)
            for r, paragraph in file_edits
        ]

        # ! The CHEAPER refusal first. A clash is decided from the ranges
        # alone; staleness reads every paragraph's lines, and computing it for a
        # file already refused was work nobody could use.
        clash = overlaps(ranges)
        if clash:
            print(f"REFUSED  {rel}: edits at {clash[0]} and {clash[1]} share a line")
            refused += len(file_edits)
            continue
        # ! Every paragraph is checked against the file BEFORE anything is written,
        # so one stale range refuses its file rather than half-splicing it.
        stale = [
            (paragraph["start"], paragraph["end"])
            for _, paragraph in file_edits
            if not paragraph_matches(lines, paragraph)
        ]
        if stale:
            # ! NAME THE RANGES. "3 range(s) no longer match" sends a reader to
            # diff a whole file; the lines say which paragraph to look at.
            where = ", ".join(f"{s}-{e}" for s, e in stale)
            print(
                f"REFUSED  {rel}: {len(stale)} range(s) no longer match"
                f" the census: {where}"
            )
            refused += len(file_edits)
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(splice(text, ranges), encoding="utf-8", newline="")
        print(f"galley   {rel} ({len(file_edits)} paragraph(s))")
        written += 1

    print(f"\n{written} file(s) set, {refused} edit(s) refused -> {out}")
    # ! Nonzero when anything refused. A galley missing a paragraph is not a galley
    # of the proposal, and censusing it would measure a text nobody proposed.
    return 1 if refused else 0


if __name__ == "__main__":
    sys.exit(main())
