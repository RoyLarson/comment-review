r"""The `turn` command: one turn of a stage's fold, from the console.

    comment_review turn --proof P.json \\
        --answers block-context=a.json --answers function-context=b.json \\
        --proof-out P2.json [--batch-out B2.json]

The work is `flows.bus`: this loads the proof and each role's answers, sends
one `AnswersReturned`, prints the events the fold produced, and saves what a
commit left behind. `Process: #87`: the master proof is the state between
turns, so a turn reads one, writes the answers onto the places it carries,
folds them again and writes the next one, with the next batch beside it while
a place is still carried forward.

!! A MODULE DOES ONE JOB AND HAS NO CLI; A FLOW CALLS MODULES;
A COMMAND EXPOSES A FLOW. `decision-log.md Process: #12`.

! THE TURN NUMBER IS THE RECORD'S, NOT THE CONSOLE'S. Nothing here names it:
a proof fresh from `collate` has no place carrying an answer, so its first
turn is 1, and a caller cannot replay a turn under a number the places
already record.

! THE EXIT CODES AND THE REPORT ARE `collate`'s, imported rather than
re-spelled, so a caller branching on a code branches once; every file is read
through `flows.proof_io`, so a refusal has one wording.

! NEITHER THE BINDER NOR THE BATCH IS READ HERE. The places on the proof
carry their own base text and say who each was put to, so what a role owes is
read off the proof rather than off the batch that went out, and no page is
opened. `--repo` is the checkout an answer's own citations resolve against,
which is verified before the fold as a mark's is (`Process: #181`).
"""

import argparse
import sys
from pathlib import Path

from comment_review.commands.collate import _code_for, _counted, _print, _refused
from comment_review.flows.bus import AnswersReturned, handle, turn_of
from comment_review.flows.proof_io import (
    load_proof,
    load_value,
    save_batch,
    save_proof,
)


def main() -> int:
    """Fold one turn's answers into the proof, report, and say what is left.

    Returns:
        One of `collate`'s codes. `UNREADABLE` is a file or an argument that
        is not what it says, and nothing is read past it. `BROKEN` is a
        rollback: an answer the fold refused, a place a role left unanswered,
        or a place the fold could not decide -- nothing is written. Otherwise
        `ESCALATIONS`, `REREADS` or `OK`, with the proof written and the next
        batch beside it while a place is carried forward.
    """
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--proof",
        required=True,
        help="the master proof as it stands -- `collate --proof-out`'s, or the"
        " last turn's",
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
        help="the checkout an answer's `sources` cite resolves against "
        "(default: the proof's own read_from.root)",
    )
    args = ap.parse_args()

    proof, why = load_proof(Path(args.proof))
    if proof is None:
        return _refused(why)
    answers: dict[str, object] = {}
    for spec in args.answers:
        role, sep, path = spec.partition("=")
        if not sep or not role or not path:
            return _refused([f"--answers wants ROLE=PATH, got {spec!r}"])
        value, why = load_value(Path(path))
        if why:
            return _refused(why)
        answers[role] = value

    # The proof names the tree its copies were gathered from, which is the one
    # their citations were written against, so a caller that passed it to
    # `gather` does not pass it again.
    root = Path(args.repo) if args.repo else Path(str(proof.read_from.get("root", ".")))
    out, result = handle(AnswersReturned(proof, answers, root))
    _print(out)
    if result is None:
        return _code_for(out)

    turn = turn_of(result.proof)
    save_proof(Path(args.proof_out), result.proof)
    print(
        f"{args.proof_out}: the master proof after turn {turn} --"
        f" {_counted(result.proof.places)}"
    )
    # ! NOTHING CARRIED FORWARD IS NO BATCH, NOT AN EMPTY ONE, as `collate`
    # has it: a file holding `{}` would be handed to roles as a turn with
    # nothing in it.
    if args.batch_out and result.batch:
        save_batch(Path(args.batch_out), result.batch)
        sizes = ", ".join(
            f"{role} {len(slots)}" for role, slots in sorted(result.batch.items())
        )
        print(f"{args.batch_out}: turn {turn + 1}'s batch -- {sizes}")

    return _code_for(out)


if __name__ == "__main__":
    sys.exit(main())
