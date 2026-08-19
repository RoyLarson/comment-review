"""The proposed text, SET AS FILES, so it can be read and censused like any tree.

    python galley.py --repo D --census census.json --edits edits.json --out DIR

A galley is the trial impression: the text set, but not yet made into pages, so
that it can be corrected before anything is committed. That is exactly what
this writes -- every block a stage proposes to change, spliced into a copy of
its file under `--out`. Nothing under `--repo` is touched.

!! IT RENDERS; IT DOES NOT RULE. A stage that both produced the galley and
judged it would be MARK and APPLY in one actor, which is the separation the
pipeline exists to keep.

Two things need it, and they needed the same thing:

  round 2   A re-review rules on the SYNTHESISED block -- text on no disk and
            in no census -- so `address_problem` refuses it and `edit_problem`
            measures one claim against one edit where the block now holds
            several. Censusing the galley gives that text a real address and a
            real transcription, so every check in `verdicts.py` works on it
            UNCHANGED. The alternatives were a second record shape to hold in
            sync, or a flag that turns the checks off for the one text the
            author actually approves.
  stage 7a  What lands at 7b is a block spliced into a file, and the splice is
            the first time anyone sees the two together. `git diff --no-index`
            over the galley shows the author what will land, including whether
            an adjacent block was clipped -- which a `CHANGE` cannot show,
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


def splice(text: str, edits: list[tuple[int, int, str]]) -> str:
    """`text` with each `(start, end, replacement)` put in place of those lines.

    Args:
        text: the file as it reads now.
        edits: one per block, 1-based and inclusive, in any order.

    Returns:
        The file with every edit applied.

    !! APPLIED IN DESCENDING ORDER, which is what makes the ranges mean
    anything. A replacement rarely has the same number of lines as what it
    replaces, so splicing top-down shifts every range below the one just
    written and each later edit lands further from where its census said. The
    caller has already refused overlaps, so descending order is exact.
    """
    end_of_line = line_endings(text)
    # !! KEEPENDS, so a line nobody edited is re-emitted with the ending it
    # had. Joining split lines with one ending rewrote every line in the file:
    # on a MIXED file, editing line 1 converted the untouched LF line 2 to
    # CRLF, and the `git diff --no-index` that stage 7a exists for showed both
    # as changed. Measured 2026-08-18.
    lines = text.splitlines(keepends=True)
    ended = text.endswith(("\n", "\r"))
    for start, end, replacement in sorted(edits, reverse=True):
        # ! NEW lines get the file's ending, because they have none of their
        # own. That is the only place `line_endings` is consulted now.
        lines[start - 1 : end] = [
            line + end_of_line for line in replacement.splitlines()
        ]
    out = "".join(lines)
    # ! A file that did not end in a newline still does not. An edit landing on
    # the last line, or appended after it, would otherwise add one.
    if not ended and out.endswith(end_of_line):
        out = out[: -len(end_of_line)]
    return out


def overlaps(edits: list[tuple[int, int, str]]) -> tuple[int, int] | None:
    """The first pair of edits sharing a line, or None.

    ! Two `CHANGE`s over one line have no defined result: each carries its
    surrounding block, so the second would overwrite context the first wrote.
    """
    ordered = sorted(edits)
    for (a_start, a_end, _), (b_start, _, _) in zip(ordered, ordered[1:], strict=False):
        if b_start <= a_end:
            return (a_start, b_start)
    return None


def block_matches(lines: list[str], block: dict) -> bool:
    """Does the file still read the way the census recorded this block?

    ! The census may be older than the file. Splicing a range whose content has
    moved writes the replacement over whatever is there now, which is the one
    failure a galley must not produce quietly.

    !! A BLOCK THAT HOLDS NO PROSE IS CHECKED DIFFERENTLY, because it has no
    text to compare. What must still hold is that it is still EMPTY: every line
    of its EDIT range is blank. An `add` is the verdict that cites one, and its
    whole finding is that the place holds no prose -- so prose appearing there
    since the census is exactly the staleness that matters.

    ! Both kinds go this way. An `undocumented` declaration ADDRESSES the lines
    of the declaration it documents, so comparing its stored text -- it has
    none -- against those lines refused it every time. Measured 2026-08-18: 3
    such blocks in this repo's own tree made the addresser call a fresh census
    stale.

    ! Before this, `raw_lines` being empty answered False, which refused every
    `add` in the run. It read as a stale range and was a block with nothing
    stored, and the message said the range no longer matched the census.
    """
    # !! THE EDIT RANGE, NOT THE ADDRESSING RANGE. A block is ADDRESSED by every
    # line of its share of the gap, blanks included -- every line has an address
    # -- but `raw_lines` holds only the prose. Comparing the wider range against
    # the narrower text refused every prose block in the tree.
    start, end = splice_range(block)
    # !! CHECKED BEFORE THE RANGE GUARD, because a block that holds no prose may
    # occupy NO LINE -- an absent docstring is at line 0 -- and the guard below
    # would refuse it for a range it is not entitled to have.
    if not block.get("raw_lines"):
        # ! Nothing was stored, so what must still hold is that the place is
        # still EMPTY -- every line of its edit range is blank.
        if start < 1 or end > len(lines) or start - 1 > end:
            return False
        return all(not ln.strip() for ln in lines[start - 1 : end])
    if start < 1 or end > len(lines) or start > end:
        return False
    stored = block["raw_lines"]
    return [ln.rstrip() for ln in lines[start - 1 : end]] == [
        ln.rstrip() for ln in stored
    ]


def shares_a_line_with_code(block: dict) -> bool:
    """Does code come before this block's text on its first line?

    !! A SPLICE REPLACES WHOLE LINES, so such a block cannot be spliced at all
    -- writing over its first line would delete the code that shares it. Two
    kinds reach here: a `trailing-comment`, and a block comment opened after a
    statement.

    !! IT READS THE CENSUS RATHER THAN INFERRING. This asked whether the stored
    text was a proper SUFFIX of the physical line, and that answers False for a
    trailing comment -- `blocks_stdlib` stores the whole line for one -- so the
    galley spliced over the code and printed success. Measured 2026-08-18: a
    galley read `# reworded trailing` where `z = 3  # trailing` had been.

    ! It is asked so the REFUSAL CAN SAY WHY. These blocks failed
    `block_matches` or passed it wrongly, and were reported as "no longer match
    the census" -- which sends a reader to diff a file nobody touched.

    !! A CENSUS WITHOUT THE FIELD CANNOT BE ASKED, and is refused by
    `unanswerable` before any block is spliced -- not defaulted here. The
    default was True, which reproduced the deleted statement exactly: a
    trailing comment's stored text IS the file's whole line, so the staleness
    check passes it and nothing else would have stopped the write.

    Args:
        block: one census entry. ! The FILE is not a parameter: the census is
            the sole authority on this, and a signature taking `lines` said
            the opposite of the paragraph above.

    Returns:
        True if the block's text begins or ends partway through a line of code.
    """
    return not block["whole_lines"]


def unanswerable(blocks: list[dict]) -> str | None:
    """Can this census answer what the galley has to ask of it?

    !! A CENSUS IS REFUSED WHOLE, not defaulted per block. Every per-field
    default is a guess about a file this tool is about to overwrite, and the
    one guess that was made -- `whole_lines` absent means True -- put back the
    defect the field was added to remove, because a trailing comment's stored
    text is the file's whole line and the staleness check passes it.

    ! It asks the BLOCKS rather than a version stamp, because `census.py
    --json` emits a bare list and has nowhere to put one. The field's presence
    is the version.

    Args:
        blocks: the census, as `census.py --json` emits it.

    Returns:
        One sentence naming what is missing, or None.
    """
    for field in ("whole_lines", "edit_start", "edit_end"):
        if any(field not in b for b in blocks):
            return (
                f"this census carries no `{field}` -- it predates the field that"
                " says which blocks can be spliced. Re-run census.py"
            )
    return None


def splice_range(block: dict) -> tuple[int, int]:
    """The 1-based inclusive lines `splice` replaces to realise this block's edit.

    !! THE CENSUS DECIDES THIS, NOT THIS MODULE. A prose block is replaced and
    an empty interval is inserted into, and there are more kinds than those two
    -- a trailing comment shares its line with code, and an `undocumented`
    declaration is a pure insertion. Branching on kind here would have to grow a
    case for each, and the census already knows which lines each block's text
    occupies.

    ! It reads `edit_start`/`edit_end`, falling back to `start`/`end` for a
    census taken before those existed. The fallback is why this function is
    still here rather than inlined.

    !! AN INTERVAL'S RANGE IS THE GAP'S OWN LINES, so a replacement REPLACES
    them -- blank lines included. Editing a two-blank-line gap with one line of
    prose leaves one line where three were, and the separation is gone. That is
    what an edit to that block means, and `reviewer-brief.md` tells a reviewer
    so; it is written here because the arithmetic does not show it.

    Args:
        block: one census entry.

    Returns:
        `(start, end)` for `splice`.
    """
    # ! No fallback. `unanswerable` has already refused a census without the
    # fields, so a missing one here is a bug and should raise rather than be
    # guessed at -- and the guess had a trap: `or` reads a legitimate edit
    # range ending at 0, the gap above the first line, as absent.
    return (block["edit_start"], block["edit_end"])


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
        help='JSON: {"<census index>": "<replacement block>"}',
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

    blocks = census["blocks"] if isinstance(census, dict) else census
    stale_census = unanswerable(blocks)
    if stale_census:
        print(f"CANNOT USE {args.census}: {stale_census}")
        return 2
    # Group by file, because a splice is a whole-file rewrite. The CENSUS BLOCK
    # travels with each edit: its `raw_lines` is the only record of what the
    # file said when the reviewers read it, and comparing the file to itself
    # would make the staleness check below unable to fail.
    # ! `(replacement, block)`. It held the block's `start` and `end` alongside
    # the block that carries them, and each consumer destructured away the half
    # the other used.
    by_path: dict[str, list[tuple[str, dict]]] = {}
    refused = 0
    for key, replacement in edits.items():
        try:
            index = int(key)
        except (TypeError, ValueError):
            print(f"REFUSED  block {key!r}: not a census index")
            refused += 1
            continue
        if not 1 <= index <= len(blocks):
            print(f"REFUSED  block {index}: outside the census")
            refused += 1
            continue
        block = blocks[index - 1]
        by_path.setdefault(block["path"], []).append((replacement, block))

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
        # ! The range comes from the BLOCK, not from the census numbers the
        # edit was grouped by: an interval is inserted into, not replaced.
        ranges = [(*splice_range(block), r) for r, block in file_edits]

        # ! The CHEAPER refusal first. A clash is decided from the ranges
        # alone; staleness reads every block's lines, and computing it for a
        # file already refused was work nobody could use.
        clash = overlaps(ranges)
        if clash:
            print(f"REFUSED  {rel}: edits at {clash[0]} and {clash[1]} share a line")
            refused += len(file_edits)
            continue
        # ! Every block is checked against the file BEFORE anything is written,
        # so one stale range refuses its file rather than half-splicing it.
        # ! ASKED FIRST, because it is a different refusal with a different
        # remedy: a stale range means re-census, and a partial-line block means
        # this tool cannot express the edit at all.
        partial = [
            (block["start"], block["end"])
            for _, block in file_edits
            if shares_a_line_with_code(block)
        ]
        if partial:
            where = ", ".join(f"{s}-{e}" for s, e in partial)
            print(
                f"REFUSED  {rel}: {len(partial)} block(s) share a line with code"
                f" and a splice replaces whole lines: {where}"
            )
            refused += len(file_edits)
            continue
        stale = [
            (block["start"], block["end"])
            for _, block in file_edits
            if not block_matches(lines, block)
        ]
        if stale:
            # ! NAME THE RANGES. "3 range(s) no longer match" sends a reader to
            # diff a whole file; the lines say which block to look at.
            where = ", ".join(f"{s}-{e}" for s, e in stale)
            print(
                f"REFUSED  {rel}: {len(stale)} range(s) no longer match"
                f" the census: {where}"
            )
            refused += len(file_edits)
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(splice(text, ranges), encoding="utf-8", newline="")
        print(f"galley   {rel} ({len(file_edits)} block(s))")
        written += 1

    print(f"\n{written} file(s) set, {refused} edit(s) refused -> {out}")
    # ! Nonzero when anything refused. A galley missing a block is not a galley
    # of the proposal, and censusing it would measure a text nobody proposed.
    return 1 if refused else 0


if __name__ == "__main__":
    sys.exit(main())
