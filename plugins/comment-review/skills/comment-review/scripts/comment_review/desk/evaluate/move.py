"""The passes that find a move on the places and decide its placement.

    moves_in         every move filed on the places, with its movers and readers
    placement_pass   one move's placement, from what was filed and answered
    settle_ends      a final placement, written onto the two place records
    hold_ends        an undecided placement, held on its two ends

The move itself -- its fields, its placements and its name -- is
`desk.proof.move`.
"""

from typing import assert_never

from comment_review.desk.answers.table import (
    ANSWERS,
    PlacementAnswerRow,
    PlacementEffect,
    asks_human,
)
from comment_review.desk.marks.table import INSTRUCTIONS, Stance
from comment_review.desk.proof.answer import QueryAnswer, Question
from comment_review.desk.proof.disposition import CHIEF, ORIGINAL, Disposition
from comment_review.desk.proof.mark import MoveMark, Touch
from comment_review.desk.proof.move import FINAL, UNDECIDED, Move, Placement, key_of
from comment_review.desk.proof.place import Filed, Place
from comment_review.desk.proof.state import State


def moves_in(
    places: dict[str, Place], recorded: dict[str, "Move"] | None = None
) -> dict[str, Move]:
    """Every move filed on these places, carrying what the record holds of each.

    A move is a `MoveMark` found at its origin, where it is filed with
    `Touch.ORIGIN`, and named by its two addresses. A move the record holds
    and no place files any longer -- withdrawn -- keeps its record with no
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
            mark = one.mark
            if one.touch is not Touch.ORIGIN or not isinstance(mark, MoveMark):
                continue
            written = INSTRUCTIONS[mark.instruction].places(mark)
            destination = next(
                (where for where, touch in written if touch is Touch.DESTINATION), ""
            )
            if not destination:
                continue
            key = key_of(place.address, destination)
            move = out.setdefault(key, Move(place.address, destination))
            move.filed[one.role] = mark
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

    Each later vote replaces the role's earlier vote. Deferral removes its
    prior acceptance or contest and leaves other readers owing their say.

    Args:
        move: the move, its movers and readers from `moves_in`.
        places: the fold's places, where its two ends are read.
        turn: the last turn whose placement answers are applied.

    Returns:
        `move`, decided.
    """
    ends = [
        end for end in (places.get(move.origin), places.get(move.destination)) if end
    ]
    stances: dict[str, set[Stance]] = {}
    reasons: list[str] = []
    for end in ends:
        for one in end.filed:
            stance = INSTRUCTIONS[one.mark.instruction].pairs(one.mark)
            stances.setdefault(one.role, set()).add(stance)
            if stance is Stance.UNSETTLABLE:
                reasons.append(
                    f"{one.role}: human query must be replaced before folding: "
                    f"{one.mark.reason}"
                )
    reasons += [
        f"{role}: human query must be replaced before folding: {answer.reason}"
        for at, answers in move.answers.items()
        if at <= turn
        for role, answer in answers.items()
        if isinstance(answer, QueryAnswer) and asks_human(answer)
    ]
    if reasons:
        move.placement, move.reasons, move.owed = Placement.REFUSED, tuple(reasons), ()
        return move
    if move.placement in FINAL:
        return move
    deferring = {role for role, held in stances.items() if held == {Stance.DEFERS}}
    movers = dict(move.filed)
    accepted: set[str] = set()
    stetted: set[str] = set()
    for at in sorted(t for t in move.answers if t <= turn):
        for role, answer in move.answers[at].items():
            row = ANSWERS.get((answer.question, answer.name))
            if row is None or answer.question is not Question.PLACEMENT:
                reasons.append(f"{role}: {answer.name} is not an answer to a placement")
                continue
            if not isinstance(row, PlacementAnswerRow):
                reasons.append(f"{role}: expected a placement row")
                continue
            effect = row.effect(answer)
            if not isinstance(effect, PlacementEffect):
                reasons.append(f"{role}: invalid placement effect")
                continue
            match effect:
                case PlacementEffect.ACCEPTS:
                    accepted.add(role)
                    stetted.discard(role)
                    deferring.discard(role)
                case PlacementEffect.CONTESTS:
                    stetted.add(role)
                    accepted.discard(role)
                    deferring.discard(role)
                case PlacementEffect.REMOVES:
                    if role in movers:
                        movers.pop(role)
                    else:
                        reasons.append(
                            f"{role}: only the role that filed a move withdraws it --"
                            " stet it to keep the paragraph where it is"
                        )
                case PlacementEffect.HUMAN_QUERY:
                    reasons.append(
                        f"{role}: human query must be replaced before folding: "
                        f"{answer.reason}"
                    )
                case PlacementEffect.DEFERS:
                    accepted.discard(role)
                    stetted.discard(role)
                    deferring.add(role)
                case _:
                    assert_never(effect)
    move.movers = movers
    move.reasons, move.owed = tuple(reasons), ()
    if reasons:
        move.placement = Placement.REFUSED
    elif not movers:
        move.placement = Placement.WITHDRAWN
    elif stetted:
        move.placement = Placement.CONTESTED
        move.owed = tuple(sorted((set(movers) | stetted) - deferring))
    else:
        owed = set(move.readers) - set(movers) - deferring - accepted
        move.owed = tuple(sorted(owed))
        move.placement = Placement.OPEN if owed else Placement.AGREED
    if move.disposition is not None:
        _ruled(move, move.disposition)
    return move


def _ruled(move: Move, ruling: Disposition) -> None:
    """The chief's placement ruling, applied to the move the roles left.

    Only an undecided move takes one. The original keeps the paragraph where
    it is; a mover's side agrees the move as that mover filed it, and any
    other mover's filing comes off when the placement is settled.
    """
    if move.placement not in UNDECIDED:
        move.placement, move.reasons = (
            Placement.REFUSED,
            (f"{CHIEF}: a placement that is {move.placement} takes no ruling",),
        )
    elif ruling.taken_side == ORIGINAL:
        move.movers, move.placement = {}, Placement.WITHDRAWN
    elif ruling.taken_side in move.movers:
        move.movers = {ruling.taken_side: move.movers[ruling.taken_side]}
        move.placement = Placement.AGREED
    else:
        move.placement, move.reasons = (
            Placement.REFUSED,
            (
                f"{CHIEF}: a placement is taken in from a mover or the original,"
                f" and {ruling.taken_side!r} filed no move here",
            ),
        )
    move.owed = ()


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
    """Take off the two ends the filings a final placement no longer stands on.

    `decision-log.md Process: #205`: an agreed move stays filed at both ends,
    and each end is decided against the move itself -- its row sets the
    remainder at the origin and the arrival at the destination. AGREED: a
    mover the placement did not keep -- one that withdrew, or one the chief
    did not take in (`Process: #196`) -- comes off. WITHDRAWN: every filing
    of this move comes off. Nothing is added.
    """
    if move.placement not in FINAL:
        return
    for end in (places.get(move.origin), places.get(move.destination)):
        if end is None:
            continue
        end.filed = [
            one
            for one in end.filed
            if not _is_this_move(one, move)
            or (move.placement is Placement.AGREED and one.role in move.movers)
        ]


def hold_ends(move: Move, places: dict[str, Place]) -> None:
    """Hold a move's two ends to its placement while it is not final.

    While placement is unresolved, ends marked `refused` retain that state.
    The remaining ends become `to-come`, with their text and questions cleared.

    Args:
        move: the move whose ends are held.
        places: the fold's places, where its two ends are read. Mutated.
    """
    if move.placement in FINAL:
        return
    ends = [
        end for end in (places.get(move.origin), places.get(move.destination)) if end
    ]
    for end in ends:
        if end.state is not State.REFUSED:
            end.state, end.text, end.question, end.owed = (
                State.TO_COME,
                None,
                None,
                (),
            )
