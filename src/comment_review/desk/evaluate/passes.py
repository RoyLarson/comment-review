"""The three passes, and the pairing of a move's two places."""

from comment_review.desk.answers.answer import Question
from comment_review.desk.evaluate.place import Place
from comment_review.desk.evaluate.state import State
from comment_review.desk.marks.table import INSTRUCTIONS, Stance
from comment_review.machine.differences import CannotCompose, compose


def marks_pass(place: Place) -> Place:
    """The place's state from the marks filed there."""
    reasons = []
    for one in place.filed:
        row = INSTRUCTIONS[one.mark.instruction]
        reasons += [
            f"{one.role}: {why}" for why in row.reads(one.mark, one.touch, place.base)
        ]
    if reasons:
        return _set(place, State.REFUSED, reasons=tuple(reasons))
    stances = {
        one.role: INSTRUCTIONS[one.mark.instruction].pairs(one.mark)
        for one in place.filed
    }
    if Stance.UNSETTLABLE in stances.values():
        return _set(place, State.UNSETTLABLE)
    proposals = place.proposals()
    # Ruling R4, `decision-log.md Process: #116` and `#121`: an `add` is
    # carried forward for every role that read the page, so it composes on
    # its own text even where it is the only proposal at this place --
    # never falling through to the "one proposal stands" branch below.
    reread = next(
        (one for one in place.filed if INSTRUCTIONS[one.mark.instruction].rereads),
        None,
    )
    if reread is not None:
        row = INSTRUCTIONS[reread.mark.instruction]
        text = row.sets(reread.mark, reread.touch, place.base)
        return _set(
            place,
            State.COMPOSED,
            text=text,
            sides=dict(proposals),
            question=Question.COMPOSITION,
        )
    texts = {role: text for role, text in proposals.items()}
    distinct = set(texts.values())
    if not texts:
        return _set(place, State.STANDS)
    if len(distinct) == 1:
        text = next(iter(distinct))
        state = State.STANDS if len(texts) == 1 else State.AGREED
        return _set(place, state, text=text)
    sides = {
        role: text if text is not None else place.base for role, text in texts.items()
    }
    try:
        composed = compose(place.base, sides)
    except CannotCompose:
        return _set(place, State.CONTESTED, sides=sides, question=Question.ESCALATION)
    return _set(
        place, State.COMPOSED, text=composed, sides=sides, question=Question.COMPOSITION
    )


def pair_moves(places: dict[str, Place]) -> None:
    """A move's two places take one state: the worse of the two."""
    order = [
        State.REFUSED,
        State.UNSETTLABLE,
        State.CONTESTED,
        State.COMPOSED,
        State.AGREED,
        State.STANDS,
    ]
    for address, place in places.items():
        other = places.get(place.partner or "")
        if other is None or other.partner != address:
            continue
        worst = min(
            (place.state, other.state),
            key=lambda s: order.index(s) if s else len(order),
        )
        for end in (place, other):
            if end.state is not worst:
                end.state = worst
                end.reasons = end.reasons + tuple(
                    r for r in (place.reasons + other.reasons) if r not in end.reasons
                )


def _set(
    place: Place, state: State, text=None, sides=None, reasons=(), question=None
) -> Place:
    place.state = state
    place.text = text
    place.sides = sides or {}
    place.reasons = reasons
    place.question = question
    return place
