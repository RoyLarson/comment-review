r"""The `collate` command: its argument parsing, its report and its exit code.

    comment_review collate --stage 4c --binder B.json --out chief.json \\
        --edit-copy a.json --edit-copy b.json \\
        [--proof-out proof.json] [--batch-out batch1.json]

The work is `flows.bus`: this loads what the message names, sends one
`CopiesReturned`, prints the events the fold produced, and saves what a
commit left behind.

!! A MODULE DOES ONE JOB AND HAS NO CLI; A FLOW CALLS MODULES;
A COMMAND EXPOSES A FLOW. `decision-log.md Process: #12`.

!! EVERY CARRIED-FORWARD PLACE IS NAMED, NEVER COUNTED. `A-T2` of
`TODO/no-command-for-the-middle.md`: a run that settles 4 of 10 must say what
became of the other 6. ! `--proof-out` AND `--batch-out` WRITE WHAT CONTINUES
THEM -- the state between turns and the first turn's batch (`Process: #87`);
the verb that runs the turn is `TODO/no-command-for-the-middle.md` T16.

The fold commits or it rolls back, so the report is the events and nothing
else: a place the fold refused is a `Refused` and the round writes nothing,
and a place it decided is a `Settled`, a `CarriedForward` or an `Unsettlable`.
"""

import argparse
import sys
from pathlib import Path

from comment_review.desk.answers.answer import Question
from comment_review.desk.containers import EditCopy
from comment_review.desk.evaluate.state import CARRIED, State
from comment_review.desk.topology import read as read_topology
from comment_review.desk.work import events
from comment_review.flows.bus import CopiesReturned, handle
from comment_review.flows.proof_io import (
    load_binder,
    load_copy,
    save_batch,
    save_copy,
    save_proof,
)

#: Exit codes, extending `distribute`'s own 0/1/2 with the two outcomes a
#: caller branches on. `main` checks the escalation before the composition, so
#: a run holding both reports the escalation: it is the stronger claim on a
#: person's attention. `turn` and `disposition` exit these same five, since
#: all three fold through the Unit of Work and a caller branching on a code
#: branches once.
#: !! THERE WERE THREE MORE UNTIL THE FOLD BECAME A UNIT OF WORK -- `DRIFT` 5,
#: `COVERAGE` 6 and `CARRIED_AND_UNRULED` 7. Each named a finding that routed
#: back to a role without voiding the round, and there is no such finding left:
#: drift, a short shard, a place a role left unruled and a slot a role left
#: unanswered are all found before the fold opens, so each is a `Refused` and
#: the round rolls back.
OK = 0
BROKEN = 1
UNREADABLE = 2
REREADS = 3
ESCALATIONS = 4


def _refused(why: list[str]) -> int:
    """A file that is not what it says: every reason on stderr, `UNREADABLE`."""
    for line in why:
        print(line, file=sys.stderr)
    return UNREADABLE


def _for_the_human(event) -> list[str]:
    """One unsettlable place as the lines 7a asks the human from.

    Who asks and why, then the move the place is an end of where it is one.
    A move held at both ends is one entry naming both, so the author approves
    or refuses the move whole (`decision-log.md Process: #155` and `#182`);
    held at one end, the entry says which end it is, since the paragraph
    leaving is a different question from the paragraph arriving.

    Args:
        event: an `Unsettlable`, as the fold emits it -- one per move, not
            one per place.

    Returns:
        The line, and the move's own line under it where there is a move.
    """
    where = f"{event.address} and {event.partner}" if event.partner else event.address
    out = [f"unsettlable {where}: {event.role} asks the human -- {event.reason}"]
    move = event.move
    if move is None:
        return out
    if event.partner:
        out.append(
            f"  and {move.role}'s move drops the paragraph at {move.origin} and adds"
            f" it at {move.destination}, one move -- {move.reason}"
        )
    elif move.origin == event.address:
        out.append(
            f"  and {move.role}'s move drops the paragraph there -- {move.reason}"
        )
    else:
        out.append(
            f"  and {move.role}'s move from {move.origin} adds the paragraph there"
            f" -- {move.reason}"
        )
    return out


def _lines(event: object) -> list[str]:
    """One event as the lines a reader sees, or none where it reports nothing.

    `Committed` and `RolledBack` carry a count of the places decided or the
    reasons refused, and every one of those has already printed its own line.
    `Advised` has a line and a heading of its own, which `_print` writes
    after the places.
    """
    if isinstance(event, events.Refused):
        where = event.address or "(the copy)"
        return [f"{event.role} {where}: {reason}" for reason in event.reasons]
    if isinstance(event, events.CarriedForward):
        roles = ", ".join(event.roles)
        return [f"{event.state} {event.address}: {roles} ({event.question})"]
    if isinstance(event, events.Unsettlable):
        return _for_the_human(event)
    if isinstance(event, events.Settled):
        return [f"stet {event.address}"]
    if isinstance(event, events.Compacted):
        return [f"compacted {event.address}"]
    # `Advised` prints under its own heading, after the places -- see `_print`.
    return []


#: The heading the advisory notes print under. It names the one rule that
#: produces a note today -- `desk.marks.table`'s `correct` row, which is what
#: `decision-log.md Process: #163` asked for and `#177` kept advisory.
FOR_THE_CHIEF = "for the chief -- each correct below drops words its claim never named:"


def _print(out: list) -> None:
    """Every event's own lines on stdout, the advisory notes last.

    A note is for the chief and changes nothing, so it sits under its own
    heading below the places rather than between them -- and it prints on
    every path, a rollback included, because it is a fact about a mark
    whatever became of the round.
    """
    for event in out:
        for line in _lines(event):
            print(line)
    advised = [one for one in out if isinstance(one, events.Advised)]
    if advised:
        print(FOR_THE_CHIEF)
        for one in advised:
            where = one.address or "(the copy)"
            for note in one.notes:
                print(f"{one.role} {where}: {note}")


def _code_for(out: list) -> int:
    """The exit code one fold's events come to.

    A rollback is `BROKEN`: nothing was saved, and every reason is on stdout
    beside the role that owes it. Otherwise the strongest claim on a person's
    attention wins -- an escalation over a composition, and `OK` where the
    fold carried nothing forward.
    """
    if any(isinstance(one, events.RolledBack) for one in out):
        return BROKEN
    carried = [one for one in out if isinstance(one, events.CarriedForward)]
    if any(one.question is Question.ESCALATION for one in carried):
        return ESCALATIONS
    if any(one.question is Question.COMPOSITION for one in carried):
        return REREADS
    return OK


def _counted(places: tuple[dict, ...]) -> str:
    """What the written proof holds, by the state each of its places came to.

    ! IT READ `N determined, M unsettlable` OFF THE OLD FOLD'S OWN LISTS, and
    said only `N places` for one commit. A reader of the console has no other
    summary of what the round did with the places it carries, so the counts
    are read back off the states the proof records.

    Args:
        places: `MasterProof.places`, as `Place.serialize` writes each.

    Returns:
        `"N places -- S settled, U unsettlable, C carried forward"`. Settled
        is every state that is neither, which after a commit is `stands` and
        `agreed`.
    """
    states = [str(place.get("state") or "") for place in places]
    carried = sum(1 for state in states if state in CARRIED)
    unsettlable = sum(1 for state in states if state == State.UNSETTLABLE)
    return (
        f"{len(states)} places -- {len(states) - carried - unsettlable} settled,"
        f" {unsettlable} unsettlable, {carried} carried forward"
    )


def _envelope(documents: list) -> tuple[list[EditCopy], list]:
    """The copies that parse, and one `Refused` per reason the rest did not.

    !! THE ENVELOPE IS PARSED HERE AND A FAILURE IS REPORTED RATHER THAN
    RAISED -- `P21`, `decision-log.md Process: #57`. What the two boundaries
    are is stated once, in `desk/containers.py`'s module docstring. What is
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
    refused: list = []
    for path, document in documents:
        parsed, why = EditCopy.deserialize(path, document)
        if why:
            named = document.get("role") if isinstance(document, dict) else None
            who = named if isinstance(named, str) and named else path
            refused += [events.Refused(who, "", (message,)) for message in why]
        if parsed is not None:
            copies.append(parsed)
    return copies, refused


def main() -> int:
    """Fold one stage's returned copies, report, and say what is left.

    Returns:
        One of `OK`, `BROKEN`, `UNREADABLE`, `REREADS` or `ESCALATIONS`.
        `UNREADABLE` is a file or an argument that is not what it says, and
        nothing is read past it. `BROKEN` is a rollback: a document that is
        not a copy, or a place the fold refused. The chief's copy, the proof
        and the batch are written only on a commit, so a `BROKEN` run writes
        none of them.
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
    ap.add_argument(
        "--topology",
        metavar="PATH",
        help="the run's topology; with it, a dispatch of --stage that returned"
        " no copy is refused by name",
    )
    # !! THE ROOT SOURCE VERIFICATION RESOLVES A `cite` AGAINST -- `P25`. It
    # defaults to the binder's own `read_from.root`, which is the tree the
    # copies were gathered from and therefore the one their citations were
    # written against.
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
    args = ap.parse_args()

    if not args.edit_copy:
        print("collate needs at least one --edit-copy", file=sys.stderr)
        return UNREADABLE

    # !! THE LOAD IS THE FLOW'S, THE DESERIALIZE THE CONTAINER'S --
    # `decision-log.md Process: #67`. `flows.proof_io` holds both steps of
    # the read and hands the binder over as a `Binder`; a copy comes back as
    # its wire dict, and `_envelope` turns it into an `EditCopy` or into the
    # reasons it is not one.
    binder, why = load_binder(Path(args.binder))
    if binder is None:
        return _refused(why)
    documents = []
    for path in args.edit_copy:
        document, why = load_copy(Path(path))
        if why:
            return _refused(why)
        documents.append((path, document))

    # ! THE BINDER NAMES ITS OWN TREE, so a caller that already passed one does
    # not pass it twice. `read_from` is refused as absent or malformed further
    # up the chain, and `.` is what a binder read from the working directory
    # says, so it is a fallback rather than a guess.
    root = Path(args.repo) if args.repo else binder.root

    # ! THE TOPOLOGY IS OPTIONAL HERE AND THE STAGE LABEL IS NOT: without a
    # topology the fold still runs, and only the count of dispatches owed is
    # unknown (`P26`).
    dispatches = None
    if args.topology:
        stages, why = read_topology(Path(args.topology).read_text(encoding="utf-8"))
        if why:
            return _refused([why])
        dispatches = next((s for s in stages if s.name == args.stage), None)
        if dispatches is None:
            known = ", ".join(s.name for s in stages)
            return _refused(
                [f"stage {args.stage!r} is not in the topology -- it holds: {known}"]
            )

    copies, refused = _envelope(documents)
    if refused:
        out = [*refused, events.RolledBack(len(refused))]
        _print(out)
        return _code_for(out)

    out, result = handle(CopiesReturned(args.stage, copies, binder, root, dispatches))
    _print(out)
    if result is None:
        return _code_for(out)

    # !! THE SERIALIZE IS THE CONTAINER'S AND THE DUMP IS THE FLOW'S --
    # `decision-log.md Process: #65`, `#67`. The fold returns containers; the
    # wire dict is made at the save, and nowhere between.
    # ! A COMMITTED `CopiesReturned` ALWAYS CARRIES A CHIEF COPY -- the field
    # is optional because a later handler on this bus may have no copy to
    # write, and the guard is what says so rather than an assertion.
    if result.chief is not None:
        save_copy(Path(args.out), result.chief)
        resolved = sum(len(sheet.marks) for sheet in result.chief.sheets)
        print(f"{args.out}: {resolved} places resolved")

    # !! THE STATE BETWEEN TURNS IS WRITTEN WITH THE CHIEF, NOT INSTEAD OF IT.
    # `Process: #87`: the master proof carries the copies as they stand and
    # every place this fold decided, so the turn verb can answer them and fold
    # again; the chief's copy is what the write end reads today.
    if args.proof_out:
        save_proof(Path(args.proof_out), result.proof)
        print(f"{args.proof_out}: the master proof -- {_counted(result.proof.places)}")
    # ! NOTHING CARRIED FORWARD IS NO BATCH, NOT AN EMPTY ONE. A file holding
    # `{}` would be handed to roles as a turn with nothing in it.
    if args.batch_out and result.batch:
        save_batch(Path(args.batch_out), result.batch)
        sizes = ", ".join(
            f"{role} {len(slots)}" for role, slots in sorted(result.batch.items())
        )
        print(f"{args.batch_out}: turn 1's batch -- {sizes}")

    return _code_for(out)


if __name__ == "__main__":
    sys.exit(main())
