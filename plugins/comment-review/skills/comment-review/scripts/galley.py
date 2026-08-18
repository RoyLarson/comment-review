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
    one picks the joiner a rewrite must use, and prefers CRLF on a mixed file
    so that the lines already carrying it are left alone.
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
    lines = text.splitlines()
    for start, end, replacement in sorted(edits, reverse=True):
        lines[start - 1 : end] = replacement.splitlines()
    return end_of_line.join(lines) + (
        end_of_line if text.endswith(("\n", "\r")) else ""
    )


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

    !! AN EMPTY INTERVAL IS CHECKED DIFFERENTLY, because it has no text to
    compare. What must still hold is that it is still EMPTY: every line strictly
    between its two code lines is blank. An `add` is the verdict that cites an
    interval, and its whole finding is that the gap holds no prose -- so prose
    appearing there since the census is exactly the staleness that matters.

    ! Before this, `raw_lines` being empty answered False, which refused every
    `add` in the run. It read as a stale range and was a block with nothing
    stored, and the message said the range no longer matched the census.
    """
    start, end = block["start"], block["end"]
    if start < 1 or end > len(lines) or start > end:
        return False
    if block.get("kind") == "interval":
        # ! The same lines `splice_range` returns, read the same way, so the
        # check and the write cannot disagree about which lines the gap is.
        first, last = splice_range(block)
        return all(not ln.strip() for ln in lines[first - 1 : last])
    stored = block.get("raw_lines") or []
    if not stored:
        return False
    return [ln.rstrip() for ln in lines[start - 1 : end]] == [
        ln.rstrip() for ln in stored
    ]


def splice_range(block: dict) -> tuple[int, int]:
    """The 1-based inclusive lines `splice` replaces to realise this block's edit.

    !! THE CENSUS DECIDES THIS, NOT THIS MODULE. A prose block is replaced and
    an empty interval is inserted into, and there are more kinds than those two
    -- a trailing comment shares its line with code, and a PEP 727 `Doc()` is a
    literal inside one. Branching on kind here would have to grow a case for
    each, and the census already knows which lines each block's text occupies.

    ! It reads `edit_start`/`edit_end`, falling back to `start`/`end` for a
    census taken before those existed. The fallback is why this function is
    still here rather than inlined.

    Args:
        block: one census entry.

    Returns:
        `(start, end)` for `splice`.
    """
    start = block.get("edit_start") or block["start"]
    end = block.get("edit_end")
    # ! `or` will not do for `end`: a legitimate edit range ends at 0, which is
    # the gap above the first line of a file.
    if end is None:
        end = block["end"]
    return (start, end)


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
    # Group by file, because a splice is a whole-file rewrite. The CENSUS BLOCK
    # travels with each edit: its `raw_lines` is the only record of what the
    # file said when the reviewers read it, and comparing the file to itself
    # would make the staleness check below unable to fail.
    by_path: dict[str, list[tuple[int, int, str, dict]]] = {}
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
        by_path.setdefault(block["path"], []).append(
            (block["start"], block["end"], replacement, block)
        )

    written = 0
    for rel, file_edits in sorted(by_path.items()):
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
        ranges = [(*splice_range(block), r) for _, _, r, block in file_edits]

        # ! Every block is checked against the file BEFORE anything is written,
        # so one stale range refuses its file rather than half-splicing it.
        stale = [
            (s, e) for s, e, _, block in file_edits if not block_matches(lines, block)
        ]
        clash = overlaps(ranges)
        if clash:
            print(f"REFUSED  {rel}: edits at {clash[0]} and {clash[1]} share a line")
            refused += len(file_edits)
            continue
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

        # !! REFUSE ANYTHING THAT WOULD LAND OUTSIDE `--out`. `out / rel` is
        # the source path itself when `rel` is absolute -- Python's join lets
        # an absolute right-hand side win -- and an absolute path is exactly
        # what a census taken before this was fixed carries. Measured
        # 2026-08-17: the galley overwrote the file under review, wrote nothing
        # under `--out`, and reported that it had succeeded.
        #
        # ! Checked on the RESOLVED path, so `..` inside a census path is
        # refused on the same rule rather than by a second one.
        target = (out / rel).resolve()
        if not target.is_relative_to(out):
            print(f"REFUSED  {rel}: would be written outside --out")
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
