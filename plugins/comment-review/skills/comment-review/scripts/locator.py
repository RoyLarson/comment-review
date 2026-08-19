"""What is the ADDRESS of this line of code.

    python locator.py --census census.json --at path:line

A reviewer is handed a FILTERED census -- the prose blocks its role rules on,
not the hundreds of empty intervals between them. When it needs to place prose
somewhere outside that set, it has a line of code in hand and needs the name of
the spot there. This answers that, and nothing else.

!! ONE QUESTION. A line number is how you ASK; an ADDRESS is how you answer.
A record naming a line as a destination is refused, because two ways to name a
place is the property this design is buying. Every extra question this grew
would be a third.

! It ANSWERS FROM THE FULL CENSUS, which is what makes a filtered one citable:
the index it returns is the index the join resolves, so a reviewer citing a
spot it never saw cites the same thing everyone else does.

! A line can sit in more than one entry -- an interval's range spans the two
CODE LINES bounding the gap, so a code line is the end of one interval and the
start of the next. Every match is printed, in census order, rather than one
being picked here. Choosing for the reviewer would be a ruling, and this tool
makes none.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from census import address  # noqa: E402  -- path shim must run first
from repo import READ_ERRORS  # noqa: E402  -- path shim must run first

# `path:line`, where the path may itself hold colons on Windows.
AT_HELP = "the line to name, as `path:line`"


def parse_at(at: str) -> tuple[str, int] | str:
    """`path:line` split on the LAST colon, or why it could not be read."""
    head, sep, tail = at.rpartition(":")
    if not sep or not tail.strip().isdigit():
        return f"--at {at!r} is not `path:line`"
    line = int(tail)
    if line < 1:
        return f"--at {at!r} names line {line} -- lines are numbered from 1"
    return (head.replace("\\", "/"), line)


def entries(census: object) -> list[dict]:
    """The census as a list, whichever shape the file carries."""
    if isinstance(census, dict):
        blocks = census.get("blocks")
        return blocks if isinstance(blocks, list) else []
    return census if isinstance(census, list) else []


def at(blocks: list[dict], path: str, line: int) -> list[tuple[int, dict]]:
    """Every entry whose range holds this line, as `(census index, entry)`.

    ! The index is 1-based and counts EVERY entry, intervals included, because
    that is the numbering the join and the record file already use.
    """
    want = path.replace("\\", "/")
    found = []
    for i, block in enumerate(blocks, 1):
        if str(block.get("path", "")).replace("\\", "/") != want:
            continue
        start, end = block.get("start"), block.get("end")
        if isinstance(start, int) and isinstance(end, int) and start <= line <= end:
            found.append((i, block))
    return found


def main() -> int:
    """Print the index and address of the spot at a line, or say there is none.

    Returns:
        0 when a spot was named, 1 when the census holds no entry for that
        line, 2 when the arguments or the census could not be read. ! The three
        are separate because a reviewer asking about a line outside the run is
        not the same as a broken census, and only the second is the run's fault.
    """
    # ! Every shipped CLI says what encoding it prints in. `vocabulary.py`
    # corrupted every em dash on a cp1252 console and exited 0, which is why
    # `tests/test_shipped_cli_encoding.py` refuses a program that prints
    # without this -- and it refused this file on its first run.
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--census", required=True, help="the census JSON")
    ap.add_argument("--at", required=True, help=AT_HELP)
    args = ap.parse_args()

    spot = parse_at(args.at)
    if isinstance(spot, str):
        print(spot)
        return 2
    path, line = spot

    try:
        census = json.loads(Path(args.census).read_text(encoding="utf-8"))
    except READ_ERRORS as e:
        print(f"CANNOT READ {args.census} ({type(e).__name__})")
        return 2
    except json.JSONDecodeError as e:
        print(f"{args.census} is not JSON ({e})")
        return 2

    blocks = entries(census)
    if not blocks:
        print(f"{args.census} carries no blocks")
        return 2

    found = at(blocks, path, line)
    if not found:
        # ! A path the census never covered and a line past its end are the
        # same answer here -- neither names a spot -- and saying which would be
        # a second question.
        print(f"no entry in the census holds {path}:{line}")
        return 1
    for index, block in found:
        print(f"{index}\t{address(block)}\t{block.get('kind', '')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
