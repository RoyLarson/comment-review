"""The `addresses` command: one subcommand per question, and its exit code.

`addresses find` names the place at a line; `addresses resolve` names the lines
at an address. The work is `flows.addresses`; this turns arguments into that
flow's inputs and prints what it returns.
"""

import argparse
from pathlib import Path

from comment_review.flows.addresses import Places, Refused, lines_of, place_at
from comment_review.reading.addresser import EOF, MODULE, SERIES


def main() -> int:
    """Run one subcommand.

    Returns:
        0 when a place was named, 1 when the page has no such place, 2 when the
        question was malformed or the file could not be read as a page.
    """
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="question", required=True)

    find = sub.add_parser("find", help="the address of the place at a line")
    find.add_argument(
        "--file", required=True, metavar="PATH", help="relative to --repo"
    )
    find.add_argument(
        "--line",
        required=True,
        type=_line,
        metavar=f"N|{MODULE}|{EOF}",
        help=f"a line NUMBER of that file, or {MODULE} or {EOF} for the places no"
        " line names: the module's documentation and front matter, and the"
        " closing gap, documentation and back matter",
    )
    find.add_argument(
        "--series",
        required=True,
        choices=SERIES,
        help="which place AT that line: a the documentation of the declaration"
        " opening there, b the gap it falls in, c the room beside it, f the"
        " file's own matter",
    )

    res = sub.add_parser("resolve", help="the lines that cover an address now")
    res.add_argument("address", metavar="ADDRESS")

    for each in (find, res):
        each.add_argument("--repo", default=".", help="the repo root the file is under")
    args = ap.parse_args()

    repo = Path(args.repo)
    if args.question == "find":
        got = place_at(repo, args.file, args.line, args.series)
    else:
        got = lines_of(repo, args.address)
    if isinstance(got, Refused):
        print("\n".join(got.lines))
        return got.code
    if isinstance(got, Places):
        for address, anchor in got.found:
            print(f"{address}\t{anchor!r}")
        if len(got.found) > 1:
            print(
                f"\n{len(got.found)} places answer to line {got.line} in"
                f" `{got.series}`. Choose by ADDRESS."
            )
        return 0
    for rel, start, end, cue in got.found:
        print(f"{rel}:{start}-{end}\t{cue}")
    return 0


def _line(given: str) -> int | str:
    """`--line`'s value: a line number, or the sentinel `MODULE` or `EOF`."""
    if given in (MODULE, EOF):
        return given
    try:
        return int(given)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"{given!r} is neither a line number nor {MODULE} or {EOF}"
        ) from None
