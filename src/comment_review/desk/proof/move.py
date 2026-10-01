"""A move: one placement claim over two places, and the pass that decides it.

`decision-log.md Process: #195`. A move claims that a paragraph is located
wrongly and belongs at its destination, and nothing about the wording of
either end. So its placement is one question for the pair, put to every role
that read either page, and decided here before either end's words are:

    OPEN        a reader owed a say has not answered it
    AGREED      every reader owed a say agreed, or the chief took a mover's
                side -- final; the move stays filed at both ends
    CONTESTED   a reader answered `stet`; carried forward for the chief
    WITHDRAWN   every mover withdrew it, or the chief kept the original --
                final; the filing comes off
    HELD        a human-review query was filed at an end, or answered
    REFUSED     an answer or a ruling this question does not take

While the placement is undecided both ends are `to-come`: neither decides a
text or asks a role anything (`Process: #200`), and once the placement is
final each end is evaluated as any place.

A move is identified by its own two addresses (`key_of`), never by a place:
two moves through one place are two moves.
"""

from dataclasses import dataclass, field, replace
from enum import StrEnum, auto

from comment_review.desk.proof.answer import Answer, read_answers
from comment_review.desk.proof.disposition import Disposition, read_disposition
from comment_review.desk.proof.mark import MoveMark, read_member


class Placement(StrEnum):
    """Where one move's placement stands; `OPEN` until the pass decides it."""

    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()

    OPEN = auto()
    AGREED = auto()
    CONTESTED = auto()
    WITHDRAWN = auto()
    REFUSED = auto()


#: The placements a fold carries forward, to a turn or to the chief.
UNDECIDED = frozenset({Placement.OPEN, Placement.CONTESTED})
#: The placements no later answer changes: the record has been rewritten.
FINAL = frozenset({Placement.AGREED, Placement.WITHDRAWN})


def key_of(origin: str, destination: str) -> str:
    """One move's name, from its own two addresses."""
    return f"{origin} -> {destination}"


@dataclass
class Move:
    """One move's placement, the roles that filed it, and what they were asked.

    `filed` and `readers` are derived from the places each fold by
    `moves_in`; `movers` is set from `filed` there and recomputed by each
    `placement_pass`, less the roles that withdrew. None of the three is
    serialized; the answers and what the pass decided are, so a turn knows
    which moves are still open and whom to ask.
    """

    origin: str
    destination: str
    #: Every role that filed this move, as the places show it. `movers` is
    #: the roles still holding the move after withdrawals, recomputed by each
    #: placement pass from `filed`; neither is serialized.
    filed: dict[str, MoveMark] = field(default_factory=dict)
    movers: dict[str, MoveMark] = field(default_factory=dict)
    readers: tuple[str, ...] = ()
    answers: dict[int, dict[str, Answer]] = field(default_factory=dict)
    #: A move is open until the placement pass decides it.
    placement: Placement = Placement.OPEN
    owed: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()
    #: The chief's ruling on this move's placement: `taken_in` a mover's side
    #: agrees the move as that mover filed it, `taken_in` the original keeps
    #: the paragraph where it is.
    disposition: Disposition | None = None

    @property
    def key(self) -> str:
        """This move's name, from its own two addresses."""
        return key_of(self.origin, self.destination)

    def recorded(self) -> "Move":
        """This move as a proof records it, without what a fold derives.

        `filed`, `readers` and `movers` are read off the places by each fold
        and are not serialized, so a proof holds the move without them -- the
        move `deserialize` reads back from what `serialize` wrote.
        """
        return replace(self, filed={}, movers={}, readers=())

    def serialize(self) -> dict:
        """This move's recorded fields, keyed by this class's own field names."""
        return {
            "origin": self.origin,
            "destination": self.destination,
            "answers": {
                str(t): {r: a.serialize() for r, a in by.items()}
                for t, by in self.answers.items()
            },
            "placement": str(self.placement),
            "owed": list(self.owed),
            "reasons": list(self.reasons),
            "disposition": self.disposition.serialize() if self.disposition else None,
        }

    @classmethod
    def deserialize(cls, where: str, entry: object) -> "tuple[Move | None, list[str]]":
        """One recorded entry becomes a `Move`, or becomes named problems.

        Each answer and the chief's ruling is read into its own type.
        """
        if not isinstance(entry, dict):
            return None, [f"{where}: a move must be an object"]
        data: dict = entry
        origin, destination = data.get("origin"), data.get("destination")
        if not isinstance(origin, str) or not origin:
            return None, [f"{where}: a move needs its `origin`"]
        if not isinstance(destination, str) or not destination:
            return None, [f"{where}: a move needs its `destination`"]
        where = f"{where} at {key_of(origin, destination)}"
        problems: list[str] = []
        if data.get("asking"):
            problems.append(
                f"{where}: retired human-held asking lifecycle is not admitted"
            )
        answers, why = read_answers(where, data.get("answers"))
        problems += why
        disposition = None
        if data.get("disposition") is not None:
            disposition, why = read_disposition(where, data["disposition"])
            problems += why
        placement: Placement | None = Placement.OPEN
        if data.get("placement"):
            placement, why = read_member(
                where, "placement", data["placement"], Placement
            )
            problems += why
        if problems or placement is None:
            return None, problems
        return (
            cls(
                origin=origin,
                destination=destination,
                answers=answers,
                placement=placement,
                owed=tuple(data.get("owed") or ()),
                reasons=tuple(data.get("reasons") or ()),
                disposition=disposition,
            ),
            [],
        )


def is_open(move: Move) -> bool:
    """Whether a move's placement is still to be decided.

    An open move is put to the roles owed a say on it, carried forward by
    the fold, waits on the chief's placement ruling at the end of the turns,
    and keeps a proof from closing.
    """
    return move.placement in UNDECIDED
