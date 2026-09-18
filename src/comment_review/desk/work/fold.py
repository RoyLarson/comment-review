"""The Unit of Work: one fold over the places of a stage.

It evaluates every place, pairs a move's two ends, and commits -- every place
decided, no place refused -- or rolls back, in which case the flow saves
nothing and the events are the report. It reads no file and knows no
container of the read or write end; the flow derives the places and saves
the result (`decision-log.md Process: #171` and the design of 2026-09-14).
"""

from dataclasses import dataclass, field

from comment_review.desk.answers.answer import Question
from comment_review.desk.evaluate.passes import evaluate, pair_moves
from comment_review.desk.evaluate.place import Place
from comment_review.desk.evaluate.state import CARRIED, State
from comment_review.desk.marks.table import INSTRUCTIONS, Stance
from comment_review.desk.work import events


@dataclass
class Fold:
    """One stage's places, folded to a commit or a rollback in one pass."""

    places: dict[str, Place]
    turn: int = 0
    events: list = field(default_factory=list)
    committed: bool = False

    @property
    def decided(self) -> dict[str, Place]:
        """The places, if committed -- empty on a rollback, nothing to save."""
        return self.places if self.committed else {}

    def run(self) -> "Fold":
        """Evaluate every place, pair a move's two ends, commit or roll back.

        A place that carries advisory notes reports them beside whatever it
        came to, and the fold commits over them: an `Advised` is for the
        chief to read, not a reason to give up the round.
        """
        for place in self.places.values():
            evaluate(place, self.turn)
        pair_moves(self.places)
        refused = 0
        for address in sorted(self.places):
            place = self.places[address]
            if place.state is State.REFUSED:
                refused += 1
                for role, reasons in _by_role(place.reasons).items():
                    self.events.append(events.Refused(role, address, reasons))
            elif place.state in CARRIED:
                self.events.append(
                    events.CarriedForward(
                        address, place.state, place.question, asked(place)
                    )
                )
            elif place.state is State.UNSETTLABLE:
                for one in place.filed:
                    if (
                        INSTRUCTIONS[one.mark.instruction].pairs(one.mark)
                        is Stance.UNSETTLABLE
                    ):
                        self.events.append(
                            events.Unsettlable(address, one.role, one.mark.reason)
                        )
            else:
                self.events.append(events.Settled(address, place.text))
            # A note is reported wherever it is found, whatever the place
            # came to, and nothing branches on it -- `Process: #177`.
            for role, notes in _by_role(place.notes).items():
                self.events.append(events.Advised(role, address, notes))
        if refused:
            self.events.append(events.RolledBack(refused))
            return self
        self.committed = True
        self.events.append(events.Committed(len(self.places)))
        return self


def asked(place: Place) -> tuple[str, ...]:
    """Who a carried-forward place is put to, in role order.

    An escalation is put to the roles that proposed a text, since it asks
    each of them about the others' proposals. Anything else carried forward
    is put to those roles and to every role that read the place's page --
    Ruling R4, `decision-log.md Process: #116` and `#121`: an add is carried
    forward for every role that read its page.

    Args:
        place: a place the fold is carrying forward.

    Returns:
        The roles, sorted, so two runs over one place name them in one order.
    """
    if place.question is Question.ESCALATION:
        return tuple(sorted(place.sides))
    return tuple(sorted(set(place.sides) | set(place.readers)))


def _by_role(reasons: tuple[str, ...]) -> dict[str, tuple[str, ...]]:
    out: dict[str, list[str]] = {}
    for reason in reasons:
        role, _, why = reason.partition(": ")
        out.setdefault(role, []).append(why)
    return {role: tuple(whys) for role, whys in out.items()}
