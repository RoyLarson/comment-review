"""A move: one placement claim over two places, and the pass that decides it.

`decision-log.md Process: #195`. A move claims that a paragraph is located
wrongly and belongs at its destination, and nothing about the wording of
either end. So its placement is one question for the pair, put to every role
that read either page, and decided here before either end's words are:

    OPEN        a reader owed a say has not answered it
    AGREED      every reader owed a say agreed -- final; the move is split
    CONTESTED   a reader answered `stet`; carried forward for the chief
    WITHDRAWN   every mover withdrew it -- final; the filing comes off
    HELD        a human-review query was filed at an end, or answered
    REFUSED     an answer this question does not take

A move is identified by its own two addresses (`key_of`), never by a place:
two moves through one place are two moves.
"""

from dataclasses import dataclass, field
from enum import StrEnum, auto

from comment_review.desk.answers.answer import Answer, Question
from comment_review.desk.answers.table import ANSWERS, Effect
from comment_review.desk.evaluate.place import Filed, Place
from comment_review.desk.evaluate.state import SETTLED, State
from comment_review.desk.marks.mark import Mark
from comment_review.desk.marks.table import INSTRUCTIONS, Stance, Touch


class Placement(StrEnum):
    """Where one move's placement stands, once the pass has read it."""

    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()

    OPEN = auto()
    AGREED = auto()
    CONTESTED = auto()
    WITHDRAWN = auto()
    HELD = auto()
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
    filed: dict[str, Mark] = field(default_factory=dict)
    movers: dict[str, Mark] = field(default_factory=dict)
    readers: tuple[str, ...] = ()
    answers: dict[int, dict[str, Answer]] = field(default_factory=dict)
    placement: Placement | None = None
    owed: tuple[str, ...] = ()
    asking: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()

    @property
    def key(self) -> str:
        """This move's name, from its own two addresses."""
        return key_of(self.origin, self.destination)

    def serialize(self) -> dict:
        """This move's recorded fields, keyed by this class's own field names."""
        return {
            "origin": self.origin,
            "destination": self.destination,
            "answers": {
                str(t): {r: a.serialize() for r, a in by.items()}
                for t, by in self.answers.items()
            },
            "placement": str(self.placement) if self.placement else None,
            "owed": list(self.owed),
            "asking": list(self.asking),
            "reasons": list(self.reasons),
        }

    @classmethod
    def deserialize(cls, where: str, entry: object) -> "tuple[Move | None, list[str]]":
        """One recorded entry becomes a `Move`, or becomes named problems."""
        if not isinstance(entry, dict):
            return None, [f"{where}: a move must be an object"]
        data: dict = entry
        origin, destination = data.get("origin"), data.get("destination")
        if not isinstance(origin, str) or not origin:
            return None, [f"{where}: a move needs its `origin`"]
        if not isinstance(destination, str) or not destination:
            return None, [f"{where}: a move needs its `destination`"]
        problems: list[str] = []
        answers: dict[int, dict[str, Answer]] = {}
        for turn, by in (data.get("answers") or {}).items():
            for role, raw in by.items():
                answer, why = Answer.deserialize(f"{where} turn {turn} {role}", raw)
                if answer is None:
                    problems += why
                else:
                    answers.setdefault(int(turn), {})[role] = answer
        if problems:
            return None, problems
        placement = data.get("placement")
        return (
            cls(
                origin=origin,
                destination=destination,
                answers=answers,
                placement=Placement(placement) if placement else None,
                owed=tuple(data.get("owed") or ()),
                asking=tuple(data.get("asking") or ()),
                reasons=tuple(data.get("reasons") or ()),
            ),
            [],
        )


def moves_in(
    places: dict[str, Place], recorded: dict[str, "Move"] | None = None
) -> dict[str, Move]:
    """Every move filed on these places, carrying what the record holds of each.

    A move is found at its origin, where it is filed with `Touch.ORIGIN`, and
    named by its two addresses. A move the record holds and no place files
    any longer -- agreed and split, or withdrawn -- keeps its record with no
    movers, so its final placement is still reported.

    Args:
        places: address -> place, as the fold holds them.
        recorded: key -> move, as the proof last recorded them; None at the
            first fold.

    Returns:
        key -> move, movers and readers derived from these places.
    """
    out: dict[str, Move] = dict(recorded or {})
    for move in out.values():
        move.filed = {}
    for place in places.values():
        for one in place.filed:
            if one.touch is not Touch.ORIGIN:
                continue
            written = INSTRUCTIONS[one.mark.instruction].places(one.mark)
            destination = next(
                (where for where, touch in written if touch is Touch.DESTINATION), ""
            )
            if not destination:
                continue
            key = key_of(place.address, destination)
            move = out.setdefault(key, Move(place.address, destination))
            move.filed[one.role] = one.mark
    for move in out.values():
        ends = (places.get(move.origin), places.get(move.destination))
        move.readers = tuple(
            sorted({role for end in ends if end for role in end.readers})
        )
        move.movers = dict(move.filed)
    return out


def placement_pass(move: Move, places: dict[str, Place], turn: int) -> Move:
    """Decide one move's placement from what was filed at its ends and answered.

    A mover's filing is its agreement. The roles owed a say are the readers
    of either page, less the movers, less a role whose every mark at both
    ends defers; an answer up to `turn` narrows them. A final placement is
    left as it is.

    Args:
        move: the move, its movers and readers from `moves_in`.
        places: the fold's places, where its two ends are read.
        turn: the last turn whose placement answers are applied.

    Returns:
        `move`, decided.
    """
    if move.placement in FINAL:
        return move
    ends = [
        end for end in (places.get(move.origin), places.get(move.destination)) if end
    ]
    stances: dict[str, set[Stance]] = {}
    asking: list[str] = []
    for end in ends:
        for one in end.filed:
            stance = INSTRUCTIONS[one.mark.instruction].pairs(one.mark)
            stances.setdefault(one.role, set()).add(stance)
            if stance is Stance.UNSETTLABLE:
                asking.append(f"{one.role}: {one.mark.reason}")
    deferring = {role for role, held in stances.items() if held == {Stance.DEFERS}}
    movers = dict(move.filed)
    accepted: set[str] = set()
    stetted: set[str] = set()
    reasons: list[str] = []
    for at in sorted(t for t in move.answers if t <= turn):
        for role, answer in move.answers[at].items():
            row = ANSWERS.get((answer.question, answer.name))
            if row is None or answer.question is not Question.PLACEMENT:
                reasons.append(f"{role}: {answer.name} is not an answer to a placement")
                continue
            effect = row.effect(answer)
            if effect is Effect.ACCEPTS:
                accepted.add(role)
                stetted.discard(role)
            elif effect is Effect.CONTESTS:
                stetted.add(role)
                accepted.discard(role)
            elif effect is Effect.REMOVES and role in movers:
                movers.pop(role)
            elif effect is Effect.REMOVES:
                reasons.append(
                    f"{role}: only the role that filed a move withdraws it -- stet"
                    " it to keep the paragraph where it is"
                )
            elif effect is Effect.UNSETTLABLE:
                asking.append(f"{role}: {answer.reason}")
            elif effect is Effect.ABSTAINS:
                deferring.add(role)
    move.movers = movers
    move.reasons, move.asking, move.owed = tuple(reasons), (), ()
    if reasons:
        move.placement = Placement.REFUSED
    elif not movers:
        move.placement = Placement.WITHDRAWN
    elif asking:
        move.placement, move.asking = Placement.HELD, tuple(asking)
    elif stetted:
        move.placement = Placement.CONTESTED
        move.owed = tuple(sorted(set(movers) | stetted))
    else:
        owed = set(move.readers) - set(movers) - deferring - accepted
        move.owed = tuple(sorted(owed))
        move.placement = Placement.OPEN if owed else Placement.AGREED
    return move


def _is_this_move(one: Filed, move: Move) -> bool:
    """Whether this filing writes this move's origin and destination, in that order.

    Ordered, not as a set of two addresses: a move the other way between the
    same two places is another move, and settling this one leaves it filed.
    """
    written = INSTRUCTIONS[one.mark.instruction].places(one.mark)
    return (move.origin, Touch.ORIGIN) in written and (
        move.destination,
        Touch.DESTINATION,
    ) in written


def settle_ends(move: Move, places: dict[str, Place]) -> None:
    """Write a final placement onto the two place records.

    AGREED: each remaining mover's filing becomes its `drop` at the origin
    and `add` at the destination (`Row.splits`), and a mover that withdrew
    comes off. WITHDRAWN: every filing of this move comes off. A split the
    row declines -- the snippet is not in the origin exactly once -- makes
    the placement REFUSED, with one reason per declined mover, and writes
    nothing, so `hold_ends` refuses both ends.
    """
    if move.placement not in FINAL:
        return
    origin, destination = places.get(move.origin), places.get(move.destination)
    if origin is None or destination is None:
        return
    halves: dict[str, tuple[Mark, Mark]] = {}
    declined: list[str] = []
    if move.placement is Placement.AGREED:
        for role, mark in sorted(move.movers.items()):
            row = INSTRUCTIONS[mark.instruction]
            split = (
                row.splits(mark, origin.base, destination.anchor)
                if row.splits
                else None
            )
            if split is None:
                declined.append(
                    f"{role}: its move cannot be split -- the snippet is not in"
                    f" {move.origin}'s paragraph exactly once"
                )
            else:
                halves[role] = split
    if declined:
        move.placement, move.reasons = Placement.REFUSED, tuple(declined)
        return
    for end, index in ((origin, 0), (destination, 1)):
        kept = [one for one in end.filed if not _is_this_move(one, move)]
        added = [
            Filed(role, split[index], Touch.OWN, move.origin)
            for role, split in sorted(halves.items())
        ]
        end.filed = kept + added


def hold_ends(move: Move, places: dict[str, Place], ruled: bool = False) -> None:
    """Hold a move's two ends to its placement while it is not final.

    HELD: both ends ride to the author and decide no text. REFUSED, or either
    end refused on its own: both are refused, with every reason. OPEN or
    CONTESTED: an end that would settle is carried with nobody asked about
    its words, since the paragraph may not be moving; an end already carried
    keeps its own question.

    `ruled` says whether the chief's dispositions pass has run. Before it,
    every end of an undecided move is carried, whether or not a ruling is on
    its record, so the chief's ruling has a carried place to close -- a
    ruling finds a settled end and is refused otherwise. After it, an end
    carrying a ruling is left as ruled.

    Args:
        move: the move whose ends are held.
        places: the fold's places, where its two ends are read. Mutated.
        ruled: True once `dispositions_pass` has run over the places.
    """
    if move.placement in FINAL:
        return
    ends = [
        end for end in (places.get(move.origin), places.get(move.destination)) if end
    ]
    if move.placement is Placement.HELD:
        for end in ends:
            end.state, end.text, end.question, end.owed = (
                State.UNSETTLABLE,
                None,
                None,
                (),
            )
            end.asking = end.asking or move.asking
        return
    refused = move.placement is Placement.REFUSED or any(
        end.state is State.REFUSED for end in ends
    )
    if refused:
        reasons = move.reasons + tuple(r for end in ends for r in end.reasons)
        for end in ends:
            end.state, end.text = State.REFUSED, None
            end.reasons = tuple(dict.fromkeys(reasons))
        return
    for end in ends:
        if ruled and end.disposition is not None:
            continue
        if end.state in SETTLED:
            end.state, end.owed, end.question = State.COMPOSED, (), None


def ruled_at_both_ends(move: Move, places: dict[str, Place]) -> bool:
    """Whether the chief has ruled both of a move's ends.

    Until the chief's placement ruling exists, the chief rules a move's ends
    one by one (`decision-log.md Process: #195` item 4). A move with both ends
    ruled is closed, and nothing asks its placement again.

    Args:
        move: the move.
        places: the fold's places, where its two ends are read.

    Returns:
        True where both ends are among `places` and each carries a
        disposition; False otherwise.
    """
    ends = (places.get(move.origin), places.get(move.destination))
    return all(end is not None and end.disposition is not None for end in ends)
