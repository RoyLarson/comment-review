"""The `carry` command: its argument parsing and its exit code.

    comment_review carry --binder B.json --repo . --path m.py --cue b1
    comment_review carry --binder B.json --repo . --path m.py --line 7 --series b
    comment_review carry --binder B.json --repo . --path m.py --anchor-num 2 --series a

The work is `flows.carry`; this is only the console face of it.

!! A MODULE DOES ONE JOB AND HAS NO CLI; A FLOW CALLS MODULES;
A COMMAND EXPOSES A FLOW. Ruled 2026-08-24 -- `decision-log.md Process: #12`.
This file parses arguments, reads two files, writes one, and prints.
"""

import argparse
import json
from pathlib import Path

from comment_review.binder.binder import read as read_binder
from comment_review.flows.carry import carry
from comment_review.flows.page_for import page_of
from comment_review.machine import exceptions


def main() -> int:
    """Add one empty place to the binder, so an `add` can cite it.

    Returns:
        0 when the place was added, 1 when it could not be, 2 when an input
        could not be read.
    """
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--binder", required=True, help="the binder, rewritten in place")
    ap.add_argument("--repo", default=".", help="repo root the path resolves against")
    ap.add_argument("--path", required=True, help="the page, as the binder names it")
    ap.add_argument("--cue", default="", help="the place itself -- `b1`")
    ap.add_argument("--line", type=int, default=0, help="a line of the file")
    ap.add_argument(
        "--anchor-num",
        type=int,
        default=-1,
        dest="anchor_num",
        help="the ORDINAL of an anchor -- survives a prose edit where a line does not",
    )
    ap.add_argument(
        "--series", default="", help="which place OF that line or anchor: a, b, c or f"
    )
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    try:
        binder_text = Path(args.binder).read_text(encoding="utf-8")
    except exceptions.READ_ERRORS as e:
        print(f"CANNOT READ ({type(e).__name__}) -- nothing written")
        return 2
    held, why = read_binder(binder_text)
    if why:
        print(f"CANNOT READ THE BINDER: {why} -- nothing written")
        return 2

    page, why = page_of(repo / args.path, rel=args.path)
    if page is None:
        print(f"CANNOT READ {args.path}: {why} -- nothing written")
        return 2

    updated, added, why = carry(
        held,
        page,
        args.path,
        cue=args.cue,
        line=args.line,
        anchor_num=args.anchor_num,
        series=args.series,
    )
    if why:
        print(f"REFUSED: {why} -- nothing written")
        return 1

    Path(args.binder).write_text(
        json.dumps(updated, indent=1), encoding="utf-8", newline=""
    )
    print(f"{args.path}@{added} carried")
    return 0
