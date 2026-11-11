"""Collate returned edit copies and report the stage's outcome.

The report includes `Refused`, `Settled`, `CarriedForward` and
`PlacementCarried` events. Human questions are reported as `AsksTheHuman`
before folding. `Advised` notes print last, under `FOR_THE_CHIEF`.

After a committed fold, the command writes the chief's copy to `--out`.
Use `--proof-out` to save the master proof and `--batch-out` to save the
next turn's batch.

The report and the exit codes are `commands.report`'s, shared with `turn`,
`disposition` and `check`.

`--pairs` names a JSON file holding the copies and their received binders,
`[{"edit_copy": PATH, "received_binder": PATH}, ...]`, for a dispatch set
too large to spell as flags on one command line. Each path is read as
written, as a flag's is.
"""

import argparse
import sys
from pathlib import Path

from comment_review.commands.report import (
    UNREADABLE,
    code_for,
    counted,
    human_answers,
    print_report,
    refused,
)
from comment_review.desk import report as events
from comment_review.desk.proof.edit_copy import EditCopy
from comment_review.desk.topology import read as read_topology
from comment_review.flows.bus import CopiesReturned, handle
from comment_review.flows.proof_io import (
    load_binder,
    load_copy,
    load_text,
    load_value,
    save_batch,
    save_copy,
    save_proof,
)


def _envelope(documents: list) -> tuple[list[EditCopy], list]:
    """The copies that parse, and one `Refused` per reason the rest did not.

    !! THE ENVELOPE IS PARSED HERE AND A FAILURE IS REPORTED RATHER THAN
    RAISED -- `P21`, `decision-log.md Process: #57`. What the two boundaries
    are is stated once, in `desk/proof/__init__.py`'s module docstring. What is
    this command's own is the ORDER and the response: envelope first, because
    a document that is not a copy has no contents to rule on, and every
    refusal printed beside whoever owes it rather than raised past the rest.

    ! THE ROLE MAY BE THE MISSING THING, so the file's own path stands in
    where the document names none -- a reader can act on that, where an empty
    column reads as a missing value.

    Args:
        documents: `(path, the wire dict)` per `--edit-copy`, as loaded.

    Returns:
        `(the parsed copies, the refusals)`. A non-empty second half means
        the stage cannot be folded: a copy that is not a copy has rulings
        nobody can read, and folding the rest would write a chief silently
        missing one role's.
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


def _pairs(path: str) -> tuple[list[str], list[str] | None, list[str]]:
    """The `--pairs` file as copy paths and received-binder paths, in order.

    Returns:
        `(copy paths, binder paths, [])`, or `([], None, problems)` where
        the file will not read or is not a list of objects each naming an
        `edit_copy` and a `received_binder` path.
    """
    value, why = load_value(Path(path))
    if why:
        return [], None, why
    keys = ("edit_copy", "received_binder")
    # Annotated `list` because a JSON value's dict has no key type to check.
    rows: list = (
        [row for row in value if isinstance(row, dict)]
        if isinstance(value, list)
        else []
    )
    if (
        not isinstance(value, list)
        or len(rows) != len(value)
        or not all(isinstance(row.get(k), str) for row in rows for k in keys)
    ):
        return [], None, [f"{path}: --pairs is a list of {{{', '.join(keys)}}} paths"]
    return (
        [row["edit_copy"] for row in rows],
        [row["received_binder"] for row in rows],
        [],
    )


def main() -> int:
    """Fold one stage's returned copies, report, and say what is left.

    Returns:
        One of `OK`, `BROKEN`, `UNREADABLE`, `REREADS`, `ESCALATIONS` or
        `ASKS_THE_HUMAN`. `UNREADABLE` is a file or an argument that is not
        what it says, and nothing is read past it. `BROKEN` is a rollback: a
        document that is not a copy, or a place the fold refused.
        `ASKS_THE_HUMAN` is a rollback holding human questions and nothing
        else. The chief's copy, the proof and the batch are written only on a
        commit, so neither rollback writes any of them.
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
    ap.add_argument(
        "--pairs",
        metavar="PATH",
        help="a JSON list of {edit_copy, received_binder} paths, in place of"
        " --edit-copy and --received-binder",
    )
    ap.add_argument(
        "--received-binder",
        action="append",
        default=None,
        metavar="PATH",
        help="one received binder per edit copy, in the same order; "
        "required for shards;"
        " without these, each copy must cover the whole stage assignment",
    )
    ap.add_argument("--out", required=True, help="where to write the chief's edit_copy")
    ap.add_argument(
        "--topology",
        metavar="PATH",
        help="the run's topology defining stage filters and dispatches; required"
        " for filtered stages and to detect missing dispatches",
    )
    ap.add_argument(
        "--repo",
        help="the checkout a `sources` cite resolves against "
        "(default: the binder's own read_from.root)",
    )
    ap.add_argument(
        "--proof-out",
        metavar="PATH",
        help="where to write the master proof -- the state between turns: the"
        " copies as they stand and every place this fold decided. Written"
        " beside the chief's copy, so not on BROKEN",
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

    copy_paths, binder_paths = args.edit_copy, args.received_binder
    if args.pairs:
        if copy_paths or binder_paths is not None:
            return refused(
                ["--pairs replaces --edit-copy and --received-binder; give one"]
            )
        copy_paths, binder_paths, why = _pairs(args.pairs)
        if why:
            return refused(why)
    if not copy_paths:
        print("collate needs at least one --edit-copy", file=sys.stderr)
        return UNREADABLE

    # !! THE LOAD IS THE FLOW'S, THE DESERIALIZE THE CONTAINER'S --
    # `decision-log.md Process: #67`. `flows.proof_io` holds both steps of
    # the read and hands the binder over as a `Binder`; a copy comes back as
    # its wire dict, and `_envelope` turns it into an `EditCopy` or into the
    # reasons it is not one.
    binder, why = load_binder(Path(args.binder))
    if binder is None:
        return refused(why)
    documents = []
    for path in copy_paths:
        document, why = load_copy(Path(path))
        if why:
            return refused(why)
        documents.append((path, document))

    # ! THE BINDER NAMES ITS OWN TREE, so a caller that already passed one does
    # not pass it twice. `read_from` is refused as absent or malformed further
    # up the chain, and `.` is what a binder read from the working directory
    # says, so it is a fallback rather than a guess.
    # `root` is where source verification resolves a `cite` (`P25`): the
    # binder's tree is the one the copies were gathered from, and so the one
    # their citations were written against.
    root = Path(args.repo) if args.repo else binder.root

    # ! THE TOPOLOGY IS OPTIONAL HERE AND THE STAGE LABEL IS NOT: without a
    # topology the fold still runs, and only the count of dispatches owed is
    # unknown (`P26`).
    dispatches = None
    if args.topology:
        text, unread = load_text(Path(args.topology))
        if text is None:
            return refused(unread)
        stages, why = read_topology(text)
        if why:
            return refused([why])
        dispatches = next((s for s in stages if s.name == args.stage), None)
        if dispatches is None:
            known = ", ".join(s.name for s in stages)
            return refused(
                [f"stage {args.stage!r} is not in the topology -- it holds: {known}"]
            )

    human, why = human_answers(args.human)
    if why:
        return refused(why)

    copies, refusals = _envelope(documents)
    if refusals:
        out = [*refusals, events.RolledBack(len(refusals))]
        print_report(out)
        return code_for(out)

    received = None
    if binder_paths is not None:
        if len(binder_paths) != len(copies):
            return refused(["each edit copy needs one received binder"])
        received = []
        for path in binder_paths:
            one, why = load_binder(Path(path))
            if one is None:
                return refused(why)
            received.append(one)

    out, result = handle(
        CopiesReturned(
            args.stage,
            copies,
            binder,
            root,
            dispatches,
            human,
            tuple(received) if received is not None else None,
        )
    )
    print_report(out)
    if result is None:
        return code_for(out)

    # !! THE SERIALIZE IS THE CONTAINER'S AND THE DUMP IS THE FLOW'S --
    # `decision-log.md Process: #65`, `#67`. The fold returns containers; the
    # wire dict is made at the save, and nowhere between.
    save_copy(Path(args.out), result.chief)
    resolved = sum(len(sheet.marks) for sheet in result.chief.sheets)
    print(f"{args.out}: {resolved} places resolved")

    # The state between turns is written with the chief, not instead of it.
    # `Process: #87`: the master proof carries the copies as they stand and
    # every place this fold decided, so the turn verb can answer them and fold
    # again; the master proof is also what the write end reads, by `proof --proof`.
    if args.proof_out:
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
