r"""The `turn` command: one turn of a stage's collate, from the console.

    comment_review turn --proof P.json --binder B.json --sent B1.json \\
        --answers block-context=a.json --answers function-context=b.json \\
        --proof-out P2.json [--batch-out B2.json] [--repo R]

The work is `flows.turn.run_turn`; this is only the console face of it.
`Process: #87`: the master proof is the state between turns, so a turn reads
one, applies every role's answers to the copies it carries, folds them again
and writes the next one -- the turn record appended, every earlier Determined
kept (`#91`), and the next batch beside it while a place is carried forward.

!! A MODULE DOES ONE JOB AND HAS NO CLI; A FLOW CALLS MODULES;
A COMMAND EXPOSES A FLOW. `decision-log.md Process: #12`.

! THE TURN NUMBER IS THE RECORD'S LENGTH PLUS ONE. Nothing on the console
names it: a proof fresh from `collate` carries no turns, so its first turn is
1, and a caller cannot replay a turn under a number the record already holds.

! THE EXIT CODES AND THE REPORT ARE `collate`'s, AND THE LOADERS ARE
`check`'s -- imported rather than re-spelled, so a caller branching on a code
branches once and a file is refused in one wording.
"""

import argparse
import sys
from pathlib import Path

from comment_review.binder.binder import Binder
from comment_review.commands.check import _load, _load_value
from comment_review.commands.collate import (
    BROKEN,
    COVERAGE,
    DRIFT,
    ESCALATIONS,
    OK,
    RECONCILE_ERRORS,
    REREADS,
    UNREADABLE,
    _report,
)
from comment_review.flows.collate import CannotCollate
from comment_review.flows.proof_io import load_proof, save_batch, save_proof
from comment_review.flows.turn import batch_for, proof_after, run_turn


def main() -> int:
    """Apply one turn's answers, fold again, and write the proof as it now stands.

    Returns:
        `collate`'s codes: `UNREADABLE` when a file is not what it says;
        `BROKEN` when a copy broke a rule, an answer would not read, or the
        set cannot be reconciled -- nothing written; else `ESCALATIONS`,
        `REREADS`, `COVERAGE`, `DRIFT` or `OK`, in that order, with the proof
        written and the next batch beside it while a place is carried forward.
    """
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--proof",
        required=True,
        help="the master proof as it stands -- `collate --proof-out`'s, or the"
        " last turn's",
    )
    ap.add_argument(
        "--binder", required=True, help="the binder the copies were seeded from"
    )
    ap.add_argument(
        "--sent",
        required=True,
        help="the batch that went out for this turn -- role -> its slots",
    )
    ap.add_argument(
        "--answers",
        action="append",
        default=[],
        metavar="ROLE=PATH",
        help="one role's answered slots, in any shape the fold reads; repeat per role",
    )
    ap.add_argument(
        "--proof-out", required=True, help="where to write the proof after this turn"
    )
    ap.add_argument(
        "--batch-out",
        metavar="PATH",
        help="where to write the next turn's batch; nothing is written when"
        " nothing is carried forward",
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
    loaded, problem = _load(args.sent, "batch")
    if problem:
        print(problem, file=sys.stderr)
        return UNREADABLE
    # ! DECLARED, NOT NARROWED -- `ty` loses an isinstance narrow at `.items()`.
    batch: dict = loaded if isinstance(loaded, dict) else {}
    sent = {
        role: list(slots) for role, slots in batch.items() if isinstance(slots, list)
    }
    if not sent:
        print(f"{args.sent}: names no role's slots", file=sys.stderr)
        return UNREADABLE
    answers: dict[str, object] = {}
    for spec in args.answers:
        role, sep, path = spec.partition("=")
        if not sep or not role or not path:
            print(f"--answers wants ROLE=PATH, got {spec!r}", file=sys.stderr)
            return UNREADABLE
        value, problem = _load_value(path)
        if problem:
            print(problem, file=sys.stderr)
            return UNREADABLE
        answers[role] = value

    root = Path(args.repo or binder.read_from.get("root") or ".")
    turn = len(proof.turns) + 1
    # ! THE WIRE DICTS, BECAUSE THE FLOW MUTATES THEM IN PLACE and folds what
    # they then hold -- `flows.turn`'s own header. The proof's copies are the
    # copies as they stood after the last fold, which is what a turn edits.
    copies = [copy.serialize() for copy in proof.edit_copies]
    earlier = {one.address: one for one in proof.determined}
    try:
        got, revisit = run_turn(
            proof.stage, copies, binder, root, sent, answers, turn, earlier
        )
    except CannotCollate as refusal:
        _report(refusal.problems)
        for one in refusal.revisit:
            for reason in one.reasons:
                print(f"{one.role} {one.where}: {reason}")
        print(
            f"REFUSED: the proof could not be reconciled -- {refusal}", file=sys.stderr
        )
        return BROKEN
    except RECONCILE_ERRORS as err:
        print(f"REFUSED: the proof could not be reconciled -- {err}", file=sys.stderr)
        return BROKEN

    _report(got.problems)
    _report(got.drift)
    _report(got.coverage)
    every = [*revisit, *got.revisit]
    for one in every:
        for reason in one.reasons:
            print(f"{one.role} {one.where}: {reason}")
    # !! AN UNREADABLE ANSWER IS `BROKEN` AND NOTHING IS WRITTEN, the same gate
    # `collate` keeps: a proof folded over a refused answer would carry the
    # refusal forward as if it were the role's ruling.
    if got.problems or got.proof is None or any(one.unreadable for one in every):
        return BROKEN

    record = {
        "turn": turn,
        "sent": sent,
        "returned": answers,
        "revisit": [one._asdict() for one in revisit],
    }
    save_proof(Path(args.proof_out), proof_after(got, (*proof.turns, record)))
    print(
        f"{args.proof_out}: the master proof after turn {turn} --"
        f" {len(got.determined)} determined, {len(got.unsettlable)} unsettlable"
    )
    for entry in got.escalations:
        print(f"escalated {entry['address']}: {', '.join(entry['roles'])}")
    for entry in got.rereads:
        print(f"re-read {entry['address']}: {', '.join(entry['roles'])}")
    if args.batch_out and (got.escalations or got.rereads):
        batch = batch_for(got)
        save_batch(Path(args.batch_out), batch)
        sizes = ", ".join(
            f"{role} {len(slots)}" for role, slots in sorted(batch.items())
        )
        print(f"{args.batch_out}: turn {turn + 1}'s batch -- {sizes}")

    if got.escalations:
        return ESCALATIONS
    if got.rereads:
        return REREADS
    if got.coverage or every:
        return COVERAGE
    if got.drift:
        return DRIFT
    return OK


if __name__ == "__main__":
    sys.exit(main())
