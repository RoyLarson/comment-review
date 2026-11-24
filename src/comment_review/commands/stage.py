"""The `stage` command: open a stage of the run, or close it.

    comment_review stage open --jacket <run-dir>/jacket.json --stage 4c [--repo .]
    comment_review stage close --jacket <run-dir>/jacket.json --stage 4c --proof P

The work is `flows.stage`; this is only the console face of it.

`open` builds the stage's tree from the jacket, gathers it into
`<run-dir>/binder<stage>.json`, seeds one copy per dispatch into
`<run-dir>/copies/` and prints one line per copy. `close` records a closed
proof as the stage's.

! Exit codes. 0 the stage opened or closed; 1 refused, every reason on stderr;
2 the jacket or a closed proof cannot be read as one, on stderr, or the arguments are
not usable.
"""

import argparse
import sys
from pathlib import Path

from comment_review.flows.stage import UnreadableInput, close_stage, open_stage


def main() -> int:
    """Open or close one stage of the run the jacket records."""
    ap = argparse.ArgumentParser(description=__doc__)
    verbs = ap.add_subparsers(dest="verb", required=True)
    opening = verbs.add_parser("open", help="build, gather and seed a stage")
    closing = verbs.add_parser("close", help="record a stage's closed proof")
    for verb in (opening, closing):
        verb.add_argument("--jacket", required=True, help="the run's jacket.json")
        verb.add_argument("--stage", required=True, help="the stage, by its row name")
    opening.add_argument("--repo", default=".", help="the checkout under review")
    closing.add_argument("--proof", required=True, help="the stage's closed proof")
    args = ap.parse_args()

    jacket = Path(args.jacket)
    try:
        if args.verb == "open":
            lines, problems = open_stage(jacket, args.stage, Path(args.repo))
        else:
            lines, problems = [], close_stage(jacket, args.stage, Path(args.proof))
    except UnreadableInput as unread:
        for line in unread.reasons:
            print(line, file=sys.stderr)
        return 2
    for line in problems:
        print(line, file=sys.stderr)
    if problems:
        return 1
    for line in lines:
        print(line)
    if args.verb == "close":
        print(f"stage {args.stage!r} closed on {args.proof}")
    return 0
