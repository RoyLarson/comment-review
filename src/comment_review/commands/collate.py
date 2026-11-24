"""Collate returned edit copies and report the stage's outcome.

    comment_review collate --jacket <run-dir>/jacket.json --stage 4c
        --proof-out P [--batch-out B] [--human answers.toml]

The jacket names everything the fold reads: the stage's topology row, the
tree it was gathered from, its binder, and each copy it dispatched with that
copy's received binder. The stage must be open. A dispatched copy that is not
on disk is reported as `not returned <copy>: <role>`, one line per copy, and
nothing is folded. The proof records the copies dispatched and the copies
folded.

The report includes `Refused`, `Decided`, `CarriedForward` and
`PlacementCarried` events. Human questions are reported as `AsksTheHuman`
before folding. `Advised` notes print last, under `FOR_THE_CHIEF`.

After a committed fold, the command saves the master proof to `--proof-out`.
Use `--batch-out` to save the next turn's batch.

The report and the exit codes are `commands.report`'s, shared with `turn`,
`disposition` and `check`, and the exit codes with `mark` as well.
`NOT_RETURNED` is this command's alone.
"""

import argparse
import sys
from pathlib import Path

from comment_review.commands.report import (
    NOT_RETURNED,
    code_for,
    counted,
    human_answers,
    print_report,
    refused,
)
from comment_review.desk import report as events
from comment_review.desk.proof.edit_copy import EditCopy
from comment_review.flows.bus import CopiesReturned, Result, handle
from comment_review.flows.proof_io import (
    load_binder,
    load_copy,
    save_batch,
    save_proof,
)
from comment_review.flows.stage import UnreadableInput, stage_of


def _envelope(documents: list) -> tuple[list[EditCopy], list]:
    """The copies that parse, and one `Refused` per reason the rest did not.

    !! The envelope is parsed here and a failure is reported rather than raised.
    What the two boundaries are is stated once, in `desk/proof/__init__.py`'s
    module docstring. What is this command's own is the order and the response:
    envelope first, because a document that is not a copy has no contents to
    rule on, and every refusal printed beside whoever owes it rather than raised
    past the rest.

    ! The role may be the missing thing, so the file's own path stands in
    where the document names none -- a reader can act on that, where an empty
    column reads as a missing value.

    Args:
        documents: `(path, the wire dict)` per copy the jacket records, as
            loaded.

    Returns:
        `(the parsed copies, the refusals)`. A non-empty second half means
        the stage cannot be folded: a copy that is not a copy has rulings
        nobody can read. Folding the rest would leave one role's rulings out
        of the proof.
    """
    copies: list[EditCopy] = []
    refusals: list = []
    for path, document in documents:
        parsed, why = EditCopy.deserialize(path, document)
        if why:
            named = document.get("role") if isinstance(document, dict) else None
            who = named if isinstance(named, str) and named else path
            refusals += [events.Refused(who, "", (message,)) for message in why]
        if parsed is not None:
            copies.append(parsed)
    return copies, refusals


def main() -> int:
    """Fold one stage's returned copies, report, and say what is left.

    Returns:
        One of `OK`, `BROKEN`, `UNREADABLE`, `REREADS`, `ESCALATIONS`,
        `ASKS_THE_HUMAN` or `NOT_RETURNED`. `UNREADABLE` is a file or an
        argument that is not what it says, a stage the jacket does not hold
        open among them, and nothing is read past it. `NOT_RETURNED` is a
        copy the jacket records as dispatched that is not on disk, and nothing
        is folded. `BROKEN` is a rollback: a
        document that is not a copy, or a place the fold refused.
        `ASKS_THE_HUMAN` is a rollback holding human questions and nothing
        else. The proof and the batch are written only on a commit.
    """
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--jacket",
        required=True,
        help="the run's jacket.json; it names the stage's row, root, binder and copies",
    )
    ap.add_argument("--stage", required=True, help="the open stage to fold, e.g. 4c")
    ap.add_argument(
        "--proof-out",
        required=True,
        metavar="PATH",
        help="where to write the master proof -- the state between turns: the"
        " copies as they stand and every place this fold decided.",
    )
    ap.add_argument(
        "--batch-out",
        metavar="PATH",
        help="where to write the first turn's batch, one slot per carried-forward"
        " place per role; nothing is written when nothing is carried forward",
    )
    ap.add_argument(
        "--human",
        metavar="PATH",
        help="the human's answers file, TOML, one [[answer]] per question"
        " (Process 198)",
    )
    args = ap.parse_args()
    try:
        stage, why = stage_of(Path(args.jacket), args.stage)
    except UnreadableInput as unread:
        return refused(unread.reasons)
    if stage is None:
        return refused(why)
    missing = [one for one in stage.dispatched if not one.copy.is_file()]
    if missing:
        for one in missing:
            print(f"not returned {one.copy}: {one.role}")
        return NOT_RETURNED
    binder, why = load_binder(stage.binder)
    if binder is None:
        return refused(why)
    documents = []
    for one in stage.dispatched:
        document, why = load_copy(one.copy)
        if why:
            return refused(why)
        documents.append((str(one.copy), document))
    human, why = human_answers(args.human)
    if why:
        return refused(why)
    copies, refusals = _envelope(documents)
    if refusals:
        out = events.rollback(refusals)
        print_report(out)
        return code_for(out)
    received = []
    for one in stage.dispatched:
        got, why = load_binder(one.binder)
        if got is None:
            return refused(why)
        received.append(got)
    # The row decides what the stage admits, which places it deals and how
    # many dispatches are owed; `stage open` stamped each copy from that row.
    names = tuple(one.name for one in stage.dispatched)
    out, result = handle(
        CopiesReturned(
            args.stage,
            copies,
            binder,
            stage.root,
            stage.row,
            human,
            tuple(received),
            dispatched=names,
            returned=names,
        )
    )
    return _reported(args, out, result)


def _reported(args: argparse.Namespace, out: list, result: Result | None) -> int:
    """Print the report, save the proof and the batch on a commit; the code."""
    print_report(out)
    if result is None:
        return code_for(out)

    save_proof(Path(args.proof_out), result.proof)
    print(f"{args.proof_out}: the master proof -- {counted(result.proof.places)}")
    # ! NOTHING CARRIED FORWARD IS NO BATCH, NOT AN EMPTY ONE. A file holding
    # `{}` would be handed to roles as a turn with nothing in it.
    if args.batch_out and result.batch:
        save_batch(Path(args.batch_out), result.batch)
        sizes = ", ".join(
            f"{role} {len(slots)}" for role, slots in sorted(result.batch.items())
        )
        print(f"{args.batch_out}: turn 1's batch -- {sizes}")

    return code_for(out)


if __name__ == "__main__":
    sys.exit(main())
