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

from comment_review.binder.binder import Binder
from comment_review.flows.carry import carry
from comment_review.flows.page_for import page_of
from comment_review.machine import exceptions
from comment_review.machine.json_object import object_of
from comment_review.reading.addresser import SERIES


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
        "--series",
        default="",
        choices=SERIES,
        help="which place OF that line or anchor",
    )
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    try:
        binder_text = Path(args.binder).read_text(encoding="utf-8")
    except exceptions.READ_ERRORS as e:
        print(f"CANNOT READ ({type(e).__name__}) -- nothing written")
        return 2
    # !! THE LOAD IS THE FLOW'S, THE DESERIALIZE THE CONTAINER'S -- `Process:
    # #67`. One decode in and one `json.dumps` out, both at this end.
    # ! IT SAID "one `json.loads` in" UNTIL `P43`, and this file holds none:
    # `machine.json_object.object_of` is the one decode, so that the read error
    # above, the malformed-JSON refusal here and `Binder.deserialize`'s
    # not-a-binder refusal below are three steps rather than one message.
    loaded, why = object_of(binder_text, "binder")
    if why:
        print(f"CANNOT READ THE BINDER: {why} -- nothing written")
        return 2
    held, problems = Binder.deserialize(args.binder, loaded)
    if held is None:
        print(f"CANNOT READ THE BINDER: {'; '.join(problems)} -- nothing written")
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
    if updated is None:
        print(f"REFUSED: {why} -- nothing written")
        return 1

    # ! THE SERIALIZE IS THE CONTAINER'S AND THE DUMP IS THE FLOW'S.
    Path(args.binder).write_text(
        json.dumps(updated.serialize(), indent=1), encoding="utf-8", newline=""
    )
    print(f"{args.path}@{added} carried")
    return 0
