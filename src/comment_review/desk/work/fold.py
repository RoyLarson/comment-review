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
Each move's placement is decided before its places are (`decision-log.md
Process: #195`).
"""

from dataclasses import dataclass, field

from comment_review.desk.evaluate.move import moves_in
from comment_review.desk.evaluate.passes import decide
from comment_review.desk.proof.move import Move, Placement, is_open
from comment_review.desk.proof.place import Place
from comment_review.desk.proof.state import CARRIED, State
from comment_review.desk.work import events


@dataclass
class Fold:
    """One stage's places, folded to a commit or a rollback in one pass.

    The fold finds its moves on its own places (`moves_in`), so a move's two
    ends are decided as one move whoever builds the fold. `recorded` is what
    the proof last saved of each move -- its placement and the answers on it
    -- and is empty at a stage's first fold.
    """

    places: dict[str, Place]
    recorded: dict[str, Move] = field(default_factory=dict)
    turn: int = 0
    events: list = field(default_factory=list)
    committed: bool = False
    moves: dict[str, Move] = field(init=False)

    def __post_init__(self) -> None:
        """Find the moves filed on these places, keeping what `recorded` holds."""
        self.moves = moves_in(self.places, self.recorded)

    @property
    def decided(self) -> dict[str, Place]:
        """The places, if committed -- empty on a rollback, nothing to save."""
        return self.places if self.committed else {}

    @property
    def decided_moves(self) -> dict[str, Move]:
        """The moves, if committed -- empty on a rollback, nothing to save."""
        return self.moves if self.committed else {}

    def run(self) -> "Fold":
        """Decide every place, then commit or roll back.

        A place that carries advisory notes reports them beside whatever it
        came to, and the fold commits over them: an `Advised` is for the
        chief to read, not a reason to give up the round.

        A rollback reports its refusals and itself, and nothing else
        (`desk.work.events`): the refusals are gathered apart from what a
        commit reports, and only a commit reports the second list.
        """
        decide(self.places, self.moves, self.turn)
        refusals: list = []
        on_commit: list = []
        for address in sorted(self.places):
            place = self.places[address]
            if place.state is State.REFUSED:
                for role, reasons in _by_role(place.reasons).items():
                    refusals.append(events.Refused(role, address, reasons))
            elif place.state is State.TO_COME:
                # An end waiting on its move asks nothing: the move's own
                # `PlacementCarried`, below, is what is put to the roles.
                pass
            elif place.state in CARRIED:
                if asked(place):
                    on_commit.append(
                        events.CarriedForward(
                            address, place.state, place.question, asked(place)
                        )
                    )
            else:
                on_commit.append(events.Settled(address, place.text))
            # A place's notes go with what a commit reports, whatever state
            # the place came to, and nothing branches on them -- `Process:
            # #177`.
            for role, notes in _by_role(place.notes).items():
                on_commit.append(events.Advised(role, address, notes))
        for key in sorted(self.moves):
            move = self.moves[key]
            if move.placement is Placement.REFUSED:
                # The move's own reasons, once, at its own key; an end's
                # reasons were reported at that end.
                for role, reasons in _by_role(move.reasons).items():
                    refusals.append(events.Refused(role, key, reasons))
            elif is_open(move):
                on_commit.append(
                    events.PlacementCarried(
                        move.origin, move.destination, move.placement, move.owed
                    )
                )
        self.events += refusals
        if refusals:
            reasons = sum(len(one.reasons) for one in refusals)
            self.events.append(events.RolledBack(reasons))
            return self
        self.events += on_commit
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


def _by_role(reasons: tuple[str, ...]) -> dict[str, tuple[str, ...]]:
    out: dict[str, list[str]] = {}
    for reason in reasons:
        role, _, why = reason.partition(": ")
        out.setdefault(role, []).append(why)
    return {role: tuple(whys) for role, whys in out.items()}
