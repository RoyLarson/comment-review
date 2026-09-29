"""The passes that find a move on the places and decide its placement.

    moves_in         every move filed on the places, with its movers and readers
    placement_pass   one move's placement, from what was filed and answered
    settle_ends      a final placement, written onto the two place records
    hold_ends        an undecided placement, held on its two ends

The move itself -- its fields, its placements and its name -- is
`desk.proof.move`.
"""

from comment_review.desk.answers.table import ANSWERS, Effect
from comment_review.desk.marks.table import INSTRUCTIONS, Stance
from comment_review.desk.proof.answer import Question
from comment_review.desk.proof.disposition import CHIEF, ORIGINAL, Disposition
from comment_review.desk.proof.mark import Mark, MoveMark, Touch
from comment_review.desk.proof.move import FINAL, UNDECIDED, Move, Placement, key_of
from comment_review.desk.proof.place import Filed, Place
from comment_review.desk.proof.state import State


def moves_in(
    places: dict[str, Place], recorded: dict[str, "Move"] | None = None
) -> dict[str, Move]:
    """Every move filed on these places, carrying what the record holds of each.

    A move is a `MoveMark` found at its origin, where it is filed with
    `Touch.ORIGIN`, and named by its two addresses. A move the record holds
    and no place files any longer -- agreed and split, or withdrawn -- keeps
    its record with no movers, so its final placement is still reported.

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
    if move.disposition is not None:
        _ruled(move, move.disposition)
    return move


def _ruled(move: Move, ruling: Disposition) -> None:
    """The chief's placement ruling, applied to the move the roles left.

    Only an undecided move takes one. The original keeps the paragraph where
    it is; a mover's side agrees the move as that mover filed it, and any
    other mover's filing comes off with the split.
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
    """Write a final placement onto the two place records.

    AGREED: each remaining mover's filing becomes its `drop` at the origin
    and `add` at the destination (`Row.splits`), and a mover that withdrew
    comes off. WITHDRAWN: every filing of this move comes off. A split the
    row declines -- the snippet is not in the origin exactly once -- makes
    the placement REFUSED and writes nothing, so `hold_ends` refuses both
    ends. It adds no reason: the move's own read at the origin tests the same
    snippet against the same paragraph, and names the defect there.
    """
    if move.placement not in FINAL:
        return
    origin, destination = places.get(move.origin), places.get(move.destination)
    if origin is None or destination is None:
        return
    halves: dict[str, tuple[Mark, Mark]] = {}
    if move.placement is Placement.AGREED:
        for role, mark in sorted(move.movers.items()):
            row = INSTRUCTIONS[mark.instruction]
            split = (
                row.splits(mark, origin.base, destination.anchor)
                if row.splits
                else None
            )
            if split is None:
                move.placement = Placement.REFUSED
                return
            halves[role] = split
    for end, index in ((origin, 0), (destination, 1)):
        kept = [one for one in end.filed if not _is_this_move(one, move)]
        added = [
            Filed(role, split[index], Touch.OWN, move.origin)
            for role, split in sorted(halves.items())
        ]
        end.filed = kept + added


def hold_ends(move: Move, places: dict[str, Place]) -> None:
    """Hold a move's two ends to its placement while it is not final.

    HELD: both ends ride to the author and decide no text. REFUSED, or either
    end refused on its own: both are refused, each keeping only its own
    reasons -- the move's are reported once, from the move. OPEN or
    CONTESTED: both ends are `to-come` -- each decides no text and asks no
    role anything until the placement is decided (`Process: #200`). A
    ruling at one of them is refused: its words are ruled against the
    move's outcome, once there is one.

    Args:
        move: the move whose ends are held.
        places: the fold's places, where its two ends are read. Mutated.
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
        for end in ends:
            end.state, end.text = State.REFUSED, None
        return
    for end in ends:
        end.state, end.text, end.question, end.owed = State.TO_COME, None, None, ()
