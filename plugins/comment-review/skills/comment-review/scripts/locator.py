"""What is the ADDRESS of this line of code.

    python locator.py --census census.json --at path:line

A reviewer is handed a FILTERED census -- the prose paragraphs its role rules on,
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

from foliator import stable  # noqa: E402  -- path shim must run first
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
        paragraphs = census.get("paragraphs")
        return paragraphs if isinstance(paragraphs, list) else []
    return census if isinstance(census, list) else []


def at(paragraphs: list[dict], path: str, line: int) -> list[tuple[int, dict]]:
    """Every place at this line, as `(census index, entry)`.

    !! A PLACE WITH NO LINES OF ITS OWN IS FOUND BY WHERE IT WOULD INSERT, and
    that is the only way to find one. An empty `interval` and an `undocumented`
    declaration are at LINE 0 -- they occupy nothing -- so a range test can
    never match them, and those are exactly the places an `add` exists to cite.
    **Measured 2026-08-19 on a seven-line file: 4 of 9 places unreachable by any
    line, every one of them an `interval` or an `undocumented`.** An `add` above
    an ordinary statement had no sanctioned route at all: the brief says ask the
    locator, and the locator could not answer.

    ! It reads `original_start`, which is where prose WOULD go -- the same field the
    galley splices at, so the place this names is the place a write lands in.

    ! A line legitimately has SEVERAL places: the gap above it, the room beside
    it, and a declaration's absent docstring can all insert at one line. All of
    them come back, and the caller reads the KIND to tell them apart.

    ! The index is 1-based and counts EVERY entry, intervals included, because
    that is the numbering the join and the record file already use.
    """
    want = path.replace("\\", "/")
    found = []
    for i, paragraph in enumerate(paragraphs, 1):
        if str(paragraph.get("path", "")).replace("\\", "/") != want:
            continue
        start, end = paragraph.get("start"), paragraph.get("end")
        if isinstance(start, int) and isinstance(end, int) and start <= line <= end:
            found.append((i, paragraph))
            continue
        # ! Only for a place that occupies NOTHING. A place with lines is found
        # by them; matching its edit range too would return it twice for one
        # line, and return a prose paragraph for a line it does not sit on.
        if start == 0 and paragraph.get("original_start") == line:
            found.append((i, paragraph))
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

    paragraphs = entries(census)
    if not paragraphs:
        print(f"{args.census} carries no paragraphs")
        return 2

    found = at(paragraphs, path, line)
    if not found:
        # ! A path the census never covered and a line past its end are the
        # same answer here -- neither names a spot -- and saying which would be
        # a second question.
        print(f"no entry in the census holds {path}:{line}")
        return 1

    # !! THE ADDRESS IS THE ANSWER, and the line range beside it is a courtesy
    # -- where to look in the file just read. The address is what a record
    # cites, because it survives the prose edits this run is about to make.
    #
    # ! It is READ, not computed. The census stamped it while it held the file
    # open; recomputing it here needed the tree, which made this tool answer
    # differently depending on where it was run from.
    stale = False
    for index, paragraph in found:
        where = stable(paragraph)
        if not where:
            # ! NAMED, not blank. An empty column reads as "this place has no
            # address"; the truth is that this CENSUS cannot say, because it
            # predates the `original_start` the gap number is read from.
            where = "NO-ADDRESS"
            stale = paragraph.get("original_start") is None
        span = f"{paragraph.get('start')}-{paragraph.get('end')}"
        print(f"{index}\t{where}\t{span}\t{paragraph.get('kind', '')}")
    if stale:
        print(
            "\n! This census carries no `original_start`, so no address can be"
            " derived from it. Re-run census.py; the line ranges above stand."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
