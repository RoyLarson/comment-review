r"""The `collate` command: its argument parsing, its report and its exit code.

    comment_review collate --stage 4c --binder B.json --out chief.json \\
        --edit-copy a.json --edit-copy b.json

The work is `flows.collate`; this is only the console face of it.

!! A MODULE DOES ONE JOB AND HAS NO CLI; A FLOW CALLS MODULES;
A COMMAND EXPOSES A FLOW. `decision-log.md Process: #12`.

!! EVERY CARRIED-FORWARD PLACE IS NAMED, NEVER COUNTED. `A-T2` of
`TODO/no-command-for-the-middle.md`: a run that settles 4 of 10 must say what
became of the other 6. ! WHAT IT DOES NOT YET DO is name the command that
CONTINUES them -- `Process: #51`'s other half, which is a later plan's, by
this plan's own scoping.
"""

import argparse
import json
import sys
from pathlib import Path

from comment_review.binder.binder import read as read_binder
from comment_review.desk.collator import UnnamedRole
from comment_review.desk.proof import MismatchedRoot
from comment_review.flows.collate import collate
from comment_review.machine import exceptions

#: Exit codes, extending `mark`'s own 0/1/2 with the two outcomes a caller
#: branches on. `main` CHECKS `got.escalations` BEFORE `got.rereads`, so a
#: run holding both reports `ESCALATIONS` (4) rather than `REREADS` (3): an
#: escalation is the stronger claim on a person's attention.
OK = 0
BROKEN = 1
UNREADABLE = 2
REREADS = 3
ESCALATIONS = 4

#: The two ways a stage cannot be reconciled at all, as against a mark that
#: broke a rule: a copy that names no role, and copies censused from different
#: roots. Both mean the SET cannot be read, so neither is routable back to one
#: role the way a `Problem` is -- they exit `BROKEN` with the reason on stderr.
#: ! BOUND TO A NAME because no `except` in a shipped file holds a tuple
#: literal; see `machine/exceptions.py`.
RECONCILE_ERRORS = (UnnamedRole, MismatchedRoot)


def _load(path: str) -> tuple[dict, str]:
    """Read one JSON object, or say why it could not be read."""
    try:
        text = Path(path).read_text(encoding="utf-8")
    except exceptions.READ_ERRORS as err:
        return {}, f"cannot read {path}: {err}"
    try:
        got = json.loads(text)
    except ValueError as err:
        return {}, f"{path} is not JSON: {err}"
    if not isinstance(got, dict):
        return {}, f"{path} is a JSON {type(got).__name__}, not an object"
    return got, ""


def main() -> int:
    """Fold one stage's returned copies, report, and say what is left.

    Returns:
        One of `OK`, `BROKEN`, `UNREADABLE`, `REREADS` or `ESCALATIONS`.
        `BROKEN` covers both a copy that broke a rule (`got.problems`) and a
        stage `RECONCILE_ERRORS` says could not be reconciled at all -- a
        raise is not a refusal, so both are caught and named on stderr
        rather than left to escape as a traceback.
    """
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", required=True, help="the stage label, e.g. 4c")
    ap.add_argument(
        "--binder", required=True, help="the binder these copies were seeded from"
    )
    ap.add_argument(
        "--edit-copy",
        action="append",
        default=[],
        metavar="PATH",
        help="one role's returned edit_copy; repeat for each",
    )
    ap.add_argument("--out", required=True, help="where to write the chief's edit_copy")
    args = ap.parse_args()

    if not args.edit_copy:
        print("collate needs at least one --edit-copy", file=sys.stderr)
        return UNREADABLE

    try:
        binder_text = Path(args.binder).read_text(encoding="utf-8")
    except exceptions.READ_ERRORS as err:
        print(f"cannot read {args.binder}: {err}", file=sys.stderr)
        return UNREADABLE
    binder, why = read_binder(binder_text)
    if why:
        print(why, file=sys.stderr)
        return UNREADABLE

    copies = []
    for path in args.edit_copy:
        copy, problem = _load(path)
        if problem:
            print(problem, file=sys.stderr)
            return UNREADABLE
        copies.append(copy)

    try:
        got = collate(args.stage, copies, binder)
    except RECONCILE_ERRORS as err:
        print(f"REFUSED: the proof could not be reconciled -- {err}", file=sys.stderr)
        return BROKEN

    for problem in got.problems:
        print(f"{problem.role} {problem.address or '(the copy)'}: {problem.message}")
    for problem in got.drift:
        print(f"{problem.role} {problem.address}: {problem.message}")
    if got.problems:
        return BROKEN

    Path(args.out).write_text(
        json.dumps(got.chief, indent=2), encoding="utf-8", newline=""
    )
    resolved = sum(len(sheet["marks"]) for sheet in got.chief["sheets"])
    print(f"{args.out}: {resolved} places resolved")

    # !! NAMED, NEVER COUNTED. Each carried-forward place prints its address
    # and every role that ruled there, so a reader can act on one without
    # re-opening the copies.
    for entry in got.escalations:
        print(f"escalated {entry['address']}: {', '.join(entry['roles'])}")
    for entry in got.rereads:
        print(f"re-read {entry['address']}: {', '.join(entry['roles'])}")

    if got.escalations:
        return ESCALATIONS
    if got.rereads:
        return REREADS
    return OK
