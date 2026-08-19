"""An address that survives the edits this tool makes.

    python addresser.py --census census.json --repo D

`census.address` names a place by LINE -- `a.py:33-34`. That is the right answer
to "where is this in the file I just read" and the wrong answer to "which place
is this", because this tool EDITS PROSE and every prose edit moves the line
numbers of the code below it. Two files differing only in comments disagree
about where the same statement is.

!! THIS RESTS ENTIRELY ON THE CENSUS BEING WHAT ROY CALLED IT, 2026-08-18: a
HASHED STATIC TABLE -- exact, constant, FULLY ENUMERATED. Take away any one of
those and the scheme collapses without saying so:

  fully enumerated  a code line missed anywhere above a place SHIFTS ITS NAME.
                    `b7` is "after the seventh code line", so a partial
                    enumeration does not fail -- it renames every place below
                    the hole, silently and consistently
  constant          the same file must count the same way twice, or two runs
                    cannot be compared, which is the whole point
  exact             a heuristic that is usually right is a table that is
                    occasionally renumbered

! And what MAKES it constant across this tool's own work is stage 7b: it proves
the executable code BYTE-IDENTICAL, so every edit moves prose and nothing else.
The code-line numbering is invariant by construction rather than by luck --
but only while the enumeration underneath it is complete.

Two forms, because a place is one of exactly two things:

    a.py@c3     ON code line 3 -- a trailing comment shares its line with code
    a.py@b3     the gap AFTER code line 3, and before code line 4

! `b0` is the gap before the first code line; `bN` after the last. A file with N
code lines has N+1 gaps, and every comment run, docstring and empty interval
sits in one of them.

!! THE SAME GAP IS THE SAME ADDRESS WHETHER PROSE FILLS IT OR NOT, which is the
property line numbers cannot give. A comment block occupying three lines and an
empty interval in the same position are both `b1` -- so a finding can say where
it belongs in a file that does not have the prose yet, and two versions of a
file can be compared place by place.

! It does NOT replace `census.address`. A reviewer reads a file and a line
number is what it has in hand; this is what a record should CARRY. Which of the
two a record cites is unruled -- see
`TODO/address-is-not-stable-under-prose-edits.md`.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from census import address  # noqa: E402  -- path shim must run first
from repo import READ_ERRORS  # noqa: E402  -- path shim must run first

ON = "c"
GAP = "b"
# A block that shares its line with code, so it sits ON one rather than between.
SHARES_ITS_LINE = ("trailing-comment",)


def code_lines_of(text: str, blocks: list[dict]) -> list[int]:
    """The 1-based line numbers holding code, in order.

    ! The same rule `census.code_lines` applies, over census entries as DICTS:
    a comment or docstring occupies its lines entirely, a trailing comment and
    an interval pass through, and a block that does not occupy its whole first
    line leaves that line as code.
    """
    occupied: set[int] = set()
    for b in blocks:
        if b.get("kind") in ("trailing-comment", "interval"):
            continue
        start, end = b.get("start"), b.get("end")
        if not isinstance(start, int) or not isinstance(end, int):
            continue
        occupied.update(range(start, end + 1))
        if not b.get("whole_lines", True):
            occupied.discard(start)
    return [
        n
        for n, line in enumerate(text.splitlines(), 1)
        if line.strip() and n not in occupied
    ]


def stable(block: dict, code: list[int]) -> str:
    """This block's address in code-line terms, or "" if it has no place.

    Args:
        block: one census entry, as a dict.
        code: the file's code lines, from `code_lines_of`.

    Returns:
        `path@cN` when the block sits ON code line N, `path@bN` when it sits in
        the gap after code line N. ! "" when the census entry carries no usable
        range -- reported by the caller, never guessed at.
    """
    path = str(block.get("path", "")).replace("\\", "/")
    start = block.get("start")
    if not isinstance(start, int):
        return ""
    if block.get("kind") in SHARES_ITS_LINE and start in code:
        return f"{path}@{ON}{code.index(start) + 1}"
    # !! THE LEADING GAP IS `b0` EVEN WHEN IT TOUCHES THE FIRST CODE LINE, and
    # this is the case a Python file hides. `end <= code[0]` means the place
    # sits at or above the first line of code, so nothing precedes it.
    #
    # ! Found on real Rust, 2026-08-18. `company.rs` opens `use std::fmt;` on
    # line 1, so its leading interval is `1-1` -- start AND end on the first
    # code line -- and the count below read that as "after code line 1". Every
    # Python file this was written against began with a blank or a docstring,
    # so the leading gap was `1-2` and the bug could not appear.
    end = block.get("end")
    if code and isinstance(end, int) and end <= code[0]:
        return f"{path}@{GAP}0"
    # !! `<=`, NOT `<`. An INTERVAL's `start` IS a bounding code line -- the
    # census names a gap by the two code lines around it -- so the gap sits
    # AFTER that line and the line must be counted. A comment or docstring
    # occupies its lines, so its `start` is never code and the two tests agree
    # there. `<` put the gap after the last statement at `b1` instead of `b2`.
    before = sum(1 for n in code if n <= start)
    return f"{path}@{GAP}{before}"


def main() -> int:
    """Print every census entry's line address beside its stable one.

    Returns:
        0 when every entry was addressed, 1 when any could not be, 2 when the
        census or a file could not be read.
    """
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--census", required=True, help="the census JSON")
    ap.add_argument("--repo", default=".", help="repo root the paths are under")
    args = ap.parse_args()

    try:
        loaded = json.loads(Path(args.census).read_text(encoding="utf-8"))
    except READ_ERRORS as e:
        print(f"CANNOT READ {args.census} ({type(e).__name__})")
        return 2
    except json.JSONDecodeError as e:
        print(f"{args.census} is not JSON ({e})")
        return 2
    blocks = loaded.get("blocks", []) if isinstance(loaded, dict) else loaded
    if not isinstance(blocks, list) or not blocks:
        print(f"{args.census} carries no blocks")
        return 2

    repo = Path(args.repo).resolve()
    code: dict[str, list[int]] = {}
    for path in sorted({str(b.get("path", "")) for b in blocks}):
        try:
            text = (repo / path).read_text(encoding="utf-8")
        except READ_ERRORS as e:
            print(f"CANNOT READ {path} ({type(e).__name__})")
            return 2
        code[path] = code_lines_of(text, [b for b in blocks if b.get("path") == path])

    unplaced = 0
    for i, block in enumerate(blocks, 1):
        where = stable(block, code.get(str(block.get("path", "")), []))
        if not where:
            unplaced += 1
        kind = block.get("kind", "")
        print(f"{i:4d}  {address(block):<40} {where or 'UNPLACED':<22} {kind}")
    if unplaced:
        print(f"\n{unplaced} entries could not be addressed.")
    return 1 if unplaced else 0


if __name__ == "__main__":
    sys.exit(main())
