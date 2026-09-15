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
        """Evaluate every place, pair a move's two ends, commit or roll back."""
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
                if place.question is Question.ESCALATION:
                    roles = tuple(sorted(place.sides))
                else:
                    roles = tuple(sorted(set(place.sides) | set(place.readers)))
                self.events.append(
                    events.CarriedForward(address, place.state, place.question, roles)
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
        if refused:
            self.events.append(events.RolledBack(refused))
            return self
        self.committed = True
        self.events.append(events.Committed(len(self.places)))
        return self


def _by_role(reasons: tuple[str, ...]) -> dict[str, tuple[str, ...]]:
    out: dict[str, list[str]] = {}
    for reason in reasons:
        role, _, why = reason.partition(": ")
        out.setdefault(role, []).append(why)
    return {role: tuple(whys) for role, whys in out.items()}
