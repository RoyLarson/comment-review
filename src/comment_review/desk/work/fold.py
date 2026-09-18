"""The Unit of Work: one fold over the places of a stage.

It hands the places to `desk.evaluate.passes.decide`, which runs the passes in
their one order, and commits -- every place decided, no place refused -- or
rolls back, in which case the flow saves nothing and the events are the
report. It reads no file and knows no container of the read or write end; the
flow derives the places and saves the result (`decision-log.md Process: #171`
and the design of 2026-09-14).

! THE ORDER IS `decide`'s AND NOT THIS MODULE'S, since 2026-09-18. This ran
the passes per place and paired afterwards, which put the chief's disposition
before the pairing and made a contested move impossible to close; the sequence
lives with the passes now, where nothing can call them in another order.
"""

from dataclasses import dataclass, field

from comment_review.desk.evaluate.passes import decide
from comment_review.desk.evaluate.place import Place
from comment_review.desk.evaluate.state import CARRIED, State
from comment_review.desk.marks.table import Touch
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
        """Decide every place, then commit or roll back.

        A place that carries advisory notes reports them beside whatever it
        came to, and the fold commits over them: an `Advised` is for the
        chief to read, not a reason to give up the round.
        """
        decide(self.places, self.turn)
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
                held = _held_with(place, self.places)
                if held is None or _prints(place, held):
                    partner = held.address if held is not None else ""
                    move = _held_move(place)
                    for one in place.asking:
                        role, _, reason = one.partition(": ")
                        self.events.append(
                            events.Unsettlable(address, role, reason, partner, move)
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

    The pass that carried it forward decided this: a text is put to the roles
    that have not accepted it, and a place with no one text yet to the roles
    that hold the texts (`desk.evaluate.passes.owed_a_say`,
    `decision-log.md Process: #180`). Reading it back rather than deriving it
    again is what keeps the rule in one place.

    Args:
        place: a place the fold is carrying forward.

    Returns:
        The roles, as the pass recorded them. Empty where nothing is carried
        forward, and for a place whose record predates the field, which is
        why the batch and the unanswered check both read this one function.
    """
    return place.owed


def _held_with(place: Place, places: dict[str, Place]) -> Place | None:
    """The other end of a move held for the human at both of its ends.

    Args:
        place: an unsettlable place.
        places: the fold's places, where its partner is looked up.

    Returns:
        The partner, where the two name each other and it is held too; None
        otherwise, which is a place that stands on its own.
    """
    other = places.get(place.partner or "")
    if other is None or other.partner != place.address:
        return None
    return other if other.state is State.UNSETTLABLE else None


def _prints(place: Place, other: Place) -> bool:
    """Which end of a held move carries the entry -- the origin, where it can tell.

    The two ends are one entry (`decision-log.md Process: #155` and `#182`),
    so exactly one of them emits it. The origin is the end the paragraph
    leaves, which is where the author reads the move from; where neither end
    or both hold the origin of a move, the earlier address decides, so the
    choice is the same on every run.
    """
    mine = any(one.touch is Touch.ORIGIN for one in place.filed)
    theirs = any(one.touch is Touch.ORIGIN for one in other.filed)
    if mine != theirs:
        return mine
    return place.address < other.address


def _held_move(place: Place) -> events.HeldMove | None:
    """The move this place is an end of, as the entry names it.

    The touch says which end this is, so the two addresses come from the
    place and its partner rather than from a claim read here.
    """
    for one in place.filed:
        if not place.partner:
            continue
        if one.touch is Touch.ORIGIN:
            return events.HeldMove(
                one.role, one.mark.reason, place.address, place.partner
            )
        if one.touch is Touch.DESTINATION:
            return events.HeldMove(
                one.role, one.mark.reason, place.partner, place.address
            )
    return None


def _by_role(reasons: tuple[str, ...]) -> dict[str, tuple[str, ...]]:
    out: dict[str, list[str]] = {}
    for reason in reasons:
        role, _, why = reason.partition(": ")
        out.setdefault(role, []).append(why)
    return {role: tuple(whys) for role, whys in out.items()}
