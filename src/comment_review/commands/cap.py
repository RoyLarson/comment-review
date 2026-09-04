r"""The `cap` command: the chief's rulings close a stage's collate.

    comment_review cap --proof P.json --binder B.json --rulings R.json \\
        --out chief.json --proof-out final.json [--repo R]

The work is `flows.turn` -- `refold`, `rule_at_cap`, `determined_chief` --
and this is only the console face of it. `Process: #78`: the task agent's
cap ends the turns; `#87`: every place still carried forward gets the chief's
own `taken_in` or `recast`, one Determined per resolved place, and the
chief's `edit_copy` is derived from the whole set.

    rulings.json   [{"address", "answer", "side", "reason", "prose"}]
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
import json
import sys
from dataclasses import replace
from pathlib import Path

from comment_review.binder.binder import Binder
from comment_review.commands.check import _load, _load_value
from comment_review.commands.collate import BROKEN, OK, UNREADABLE, _report
from comment_review.desk.determined import Answer
from comment_review.flows.collate import CannotCollate
from comment_review.flows.proof_io import load_proof, save_proof
from comment_review.flows.turn import (
    determined_chief,
    proof_after,
    refold,
    rule_at_cap,
)


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
        "--rulings",
        required=True,
        help="the chief's rulings, a list -- one per carried-forward place",
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
        for line in why:
            print(line, file=sys.stderr)
        return UNREADABLE
    loaded, problem = _load(args.binder, "binder")
    if problem:
        print(problem, file=sys.stderr)
        return UNREADABLE
    binder, why = Binder.deserialize(args.binder, loaded)
    if binder is None:
        for line in why:
            print(line, file=sys.stderr)
        return UNREADABLE
    rulings, problem = _load_value(args.rulings)
    if problem:
        print(problem, file=sys.stderr)
        return UNREADABLE
    rows: list[dict] = (
        [r for r in rulings if isinstance(r, dict)] if isinstance(rulings, list) else []
    )
    if not isinstance(rulings, list) or len(rows) != len(rulings):
        print(f"{args.rulings}: the rulings are a list of objects", file=sys.stderr)
        return UNREADABLE

    root = Path(args.repo) if args.repo else binder.root
    turn = len(proof.turns)
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
                rule_at_cap(
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
        every, chief = determined_chief(got, ruled)
    except ValueError as err:
        print(str(err))
        return BROKEN

    closed = replace(
        proof_after(got, proof.turns),
        determined=tuple(every[address] for address in sorted(every)),
    )
    # !! THE SERIALIZE IS THE CONTAINER'S AND THE DUMP IS THE FLOW'S --
    # `Process: #65`, `#67` -- the same line `collate` writes its chief with.
    Path(args.out).write_text(
        json.dumps(chief.serialize(), indent=2), encoding="utf-8", newline=""
    )
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
