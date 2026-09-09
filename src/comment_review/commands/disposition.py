r"""The `disposition` command: the chief's dispositions close a stage's collate.

    comment_review disposition --proof P.json --binder B.json --dispositions D.json \\
        --out chief.json --proof-out final.json [--repo R]

The work is `flows.turn` -- `refold`, `rule_at_max_turns`, `close` -- and this is
only the console face of it. `Process: #78`: the task agent's
cap ends the turns; `#87`: every place still carried forward gets the chief's
own `taken_in` or `recast`, one Determined per resolved place, and the
chief's `edit_copy` is derived from the whole set.

    dispositions.json  [{"address", "answer", "side", "reason", "prose"}]
                   answer: taken_in | recast. side: a role, or "original",
                   for a taken_in. prose: the chief's own paragraph, for a
                   recast.

!! A MODULE DOES ONE JOB AND HAS NO CLI; A FLOW CALLS MODULES;
A COMMAND EXPOSES A FLOW. `decision-log.md Process: #12`.

!! NOTHING SURVIVES THE CAP UNRULED, T17. A carried-forward place with no
ruling is refused by name, with its roles, and nothing is written -- the
refusal is the whole answer, so the caller rules and runs again.

! THE UNSETTLABLE PLACES ARE PRINTED, NOT RULED -- `Process: #90`. A
human-review query rides with the set to the end and is asked of the human
after everything else has settled; this is the end, so each is named here
for that asking, and none is on the chief's copy.
"""

import argparse
import sys
from pathlib import Path

from comment_review.commands.collate import BROKEN, OK, _refused, _report
from comment_review.desk.determined import Answer
from comment_review.flows.collate import CannotCollate
from comment_review.flows.proof_io import (
    load_binder,
    load_proof,
    load_value,
    save_copy,
    save_proof,
)
from comment_review.flows.turn import close, refold, rule_at_max_turns


def main() -> int:
    """Rule every carried-forward place, derive the chief's copy, close the proof.

    Returns:
        `UNREADABLE` when a file is not what it says; `BROKEN` when a ruling
        cannot be applied or a place is left unruled, each named, nothing
        written; `OK` with the chief's copy and the final proof written.
    """
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--proof", required=True, help="the master proof as the last turn wrote it"
    )
    ap.add_argument(
        "--binder", required=True, help="the binder the copies were seeded from"
    )
    ap.add_argument(
        "--dispositions",
        required=True,
        help="the chief's dispositions, one per carried-forward place",
    )
    ap.add_argument("--out", required=True, help="where to write the chief's edit_copy")
    ap.add_argument(
        "--proof-out",
        required=True,
        help="where to write the closed proof -- every Determined, the chief's too",
    )
    ap.add_argument(
        "--repo",
        help="the checkout a `sources` cite resolves against "
        "(default: the binder's own read_from.root)",
    )
    args = ap.parse_args()

    proof, why = load_proof(Path(args.proof))
    if proof is None:
        return _refused(why)
    binder, why = load_binder(Path(args.binder))
    if binder is None:
        return _refused(why)
    rulings, why = load_value(Path(args.dispositions))
    if why:
        return _refused(why)
    rows: list[dict] = (
        [r for r in rulings if isinstance(r, dict)] if isinstance(rulings, list) else []
    )
    if not isinstance(rulings, list) or len(rows) != len(rulings):
        return _refused(
            [f"{args.dispositions}: the dispositions are a list of objects"]
        )

    root = Path(args.repo) if args.repo else binder.root
    turn = proof.turn
    try:
        got = refold(proof, binder, root)
    except CannotCollate as refusal:
        _report(refusal.problems)
        print(
            f"REFUSED: the proof could not be reconciled -- {refusal}", file=sys.stderr
        )
        return BROKEN
    _report(got.problems)
    if got.problems or got.proof is None:
        return BROKEN

    # !! EVERY RULING IS TRIED AND EVERY REFUSAL NAMED before anything is
    # written, so one bad ruling does not hide the next -- the same reason the
    # fold stacks its problems rather than raising on the first.
    ruled = []
    refused = 0
    for i, data in enumerate(rows, 1):
        where = f"ruling {i} ({data.get('address', '?')})"
        named = data.get("answer")
        if named not in set(Answer):
            print(f"{where}: `answer` must be one of {', '.join(sorted(Answer))}")
            refused += 1
            continue
        try:
            ruled.append(
                rule_at_max_turns(
                    got,
                    str(data.get("address", "")),
                    Answer(named),
                    str(data.get("side", "")),
                    str(data.get("reason", "")),
                    turn,
                    prose=str(data.get("prose", "")),
                )
            )
        except ValueError as err:
            print(f"{where}: {err}")
            refused += 1
    if refused:
        return BROKEN
    try:
        closed, chief = close(got, ruled, proof.turns)
    except ValueError as err:
        print(str(err))
        return BROKEN

    save_copy(Path(args.out), chief)
    save_proof(Path(args.proof_out), closed)
    places = sum(len(sheet.marks) for sheet in chief.sheets)
    print(f"{args.out}: the chief's copy, {places} places")
    print(
        f"{args.proof_out}: the proof closed at turn {turn} --"
        f" {len(closed.determined)} determined, {len(closed.unsettlable)} unsettlable"
    )
    for one in closed.determined:
        print(f"{one.answer} {one.address}: {one.side} ({one.how}, turn {one.turn})")
    for place in closed.unsettlable:
        query = place.get("query", {})
        print(
            f"unsettlable {place['address']}: {query.get('role', '?')} asks the human"
            f" -- {query.get('reason', '')}"
        )
    return OK


if __name__ == "__main__":
    sys.exit(main())
