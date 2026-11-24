"""The exit codes and the console report the fold's commands share.

`collate`, `turn` and `disposition` fold through `flows.bus` and print its
events here, so a caller branching on a code branches once. `check` exits
these codes and prints a human question as `collate` does; `mark` exits the
first three. What each code means for one command is in that command's
`main()` docstring.

`human_answers` reads the `--human` answers file that `check`, `collate`,
`disposition` and `turn` each take, and hands its problems to `refused`.

Not a command: `__main__.Command` does not name it.
"""

import sys
from pathlib import Path

from comment_review.desk import report as events
from comment_review.desk.proof.answer import Question
from comment_review.desk.proof.move import Placement
from comment_review.desk.proof.place import Place
from comment_review.desk.proof.state import CARRIED, DECIDED, State
from comment_review.flows.human import HumanAnswer, read_answers

#: Exit codes.
OK = 0
BROKEN = 1
UNREADABLE = 2
REREADS = 3
ESCALATIONS = 4
# The run paused for the person: human questions and nothing else, nothing
# saved, and the round runs again once each role has the answer.
ASKS_THE_HUMAN = 5
# A copy the stage dispatched did not come back, so no role has a line to act
# on; nothing was folded, and that dispatch is launched again.
NOT_RETURNED = 6


def refused(why: list[str]) -> int:
    """A file that is not what it says: every reason on stderr, `UNREADABLE`."""
    for line in why:
        print(line, file=sys.stderr)
    return UNREADABLE


def human_answers(path: str | None) -> tuple[tuple[HumanAnswer, ...], list[str]]:
    """The `--human` answers file, read, or the reasons it will not read.

    Args:
        path: what `--human` said, or None where it was not given.

    Returns:
        `(the answers, [])`; `((), [])` for None; `((), problems)` where the
        file cannot be opened or any section will not read -- a caller hands
        the problems to `refused`.
    """
    if path is None:
        return (), []
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        # An OSError's own string names the file it could not open.
        return (), [str(exc)]
    answers, problems = read_answers(text, path)
    if problems:
        return (), problems
    return tuple(answers), []


def lines(event: object) -> list[str]:
    """One event as the lines a reader sees, or none where it reports nothing."""
    if isinstance(event, events.AsksTheHuman):
        if event.answer:
            return [
                f"answered by the human {event.at}: {event.role} -- {event.answer};"
                f" {event.role} replaces this query with its mark or answer"
            ]
        return [
            f"asks the human {event.at}: {event.role} -- {event.question}; ask it,"
            f" record the answer in the answers file, and send it back to {event.role}"
        ]
    if isinstance(event, events.Refused):
        where = event.address or "(the copy)"
        return [
            events.refusal_line(event.role, where, reason) for reason in event.reasons
        ]
    if isinstance(event, events.CarriedForward):
        roles = ", ".join(event.roles)
        return [f"{event.state} {event.address}: {roles} ({event.question})"]
    if isinstance(event, events.PlacementCarried):
        roles = ", ".join(event.roles)
        return [
            f"{event.placement} {event.origin} -> {event.destination}:"
            f" {roles} (placement)"
        ]
    if isinstance(event, events.Decided):
        ruling = event.disposition
        if ruling is not None:
            return [
                f"{ruling.name} {event.address}: {ruling.taken_side} -- {ruling.reason}"
            ]
        return [f"decided {event.address}: {', '.join(event.stands) or 'original'}"]
    # `Committed` and `RolledBack` print nothing, and `Advised` prints under its own
    # heading, after the places -- see `print_report`.
    return []


#: The heading for advisory notes the chief reads after a committed fold.
FOR_THE_CHIEF = "for the chief -- advisory notes:"


def print_report(out: list) -> None:
    """Every event's own lines on stdout, the advisory notes last.

    A note is for the chief and changes nothing, so it sits under its own
    heading below the places rather than between them. Only a committed fold
    emits one (`desk.work.fold`), so the heading prints only over a
    committed round.
    """
    for event in out:
        for line in lines(event):
            print(line)
    advised = [one for one in out if isinstance(one, events.Advised)]
    if advised:
        print(FOR_THE_CHIEF)
        for one in advised:
            where = one.address or "(the copy)"
            for note in one.notes:
                print(f"{one.role} {where}: {note}")


def code_for(out: list) -> int:
    """The exit code one fold's events come to.

    A rollback is `UNREADABLE` where a `Refused` in `out` is `unreadable` --
    an input whose page identity will not admit -- `BROKEN` where any other
    `Refused` is, and
    `ASKS_THE_HUMAN` where it holds human questions and no refusal: the run
    is paused for the person, nothing was saved, and every question is on
    stdout beside the role that owes it.
    Otherwise the strongest claim on a person's attention wins -- an
    escalation or a contested placement (`ESCALATIONS`) over a composition or
    an open placement (`REREADS`), and `OK` where the fold carried nothing forward.
    """
    if any(isinstance(one, events.RolledBack) for one in out):
        if any(isinstance(one, events.Refused) and one.unreadable for one in out):
            return UNREADABLE
        if any(isinstance(one, events.Refused) for one in out):
            return BROKEN
        if any(isinstance(one, events.AsksTheHuman) for one in out):
            return ASKS_THE_HUMAN
        return BROKEN
    carried = [one for one in out if isinstance(one, events.CarriedForward)]
    placements = [one for one in out if isinstance(one, events.PlacementCarried)]
    if any(one.question is Question.ESCALATION for one in carried):
        return ESCALATIONS
    if any(one.placement is Placement.CONTESTED for one in placements):
        return ESCALATIONS
    if placements or any(one.question is Question.COMPOSITION for one in carried):
        return REREADS
    return OK


def counted(places: tuple[Place, ...]) -> str:
    """What the written proof holds, by the state each of its places came to.

    A reader of the console has no other summary of what the round did with
    the places it carries, so the counts are read back off the states the
    proof records.

    Args:
        places: `MasterProof.places`.

    Returns:
        `"N places -- D decided, C carried forward, T to come"`.

    Decided is counted rather than subtracted, and `desk.proof.state.DECIDED`
    is the one set of decided states both this and `flows.transcribe._unclosed`
    read.
    """
    states = [str(place.state or "") for place in places]
    carried = sum(1 for state in states if state in CARRIED)
    decided = sum(1 for state in states if state in DECIDED)
    to_come = sum(1 for state in states if state == State.TO_COME)
    return (
        f"{len(states)} places -- {decided} decided,"
        f" {carried} carried forward, {to_come} to come"
    )
