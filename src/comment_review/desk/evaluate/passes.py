"""The three passes, and the pairing of a move's two places."""

from comment_review.desk.answers.answer import Question
from comment_review.desk.answers.table import ANSWERS, Effect
from comment_review.desk.dispositions.disposition import CHIEF, ORIGINAL
from comment_review.desk.dispositions.table import DISPOSITIONS
from comment_review.desk.evaluate.place import Place
from comment_review.desk.evaluate.state import CARRIED, State
from comment_review.desk.marks.table import INSTRUCTIONS, Stance
from comment_review.machine.differences import CannotCompose, compose


def _doubled(place: Place) -> list[str]:
    """One reason per role that filed more than one mark touching this place.

    A place holds one text and a role holds one position on it, so two of a
    role's own marks reaching here cannot both be honoured -- and nothing
    downstream could say which was meant: `Place.proposals` is keyed by role,
    so the second would stand and the first would vanish without a word. The
    reason names each mark by its instruction and its own address, since a
    mark reaching a place is not always addressed to it: a move is filed at
    its destination under the origin's address.

    Args:
        place: a place with its marks filed.

    Returns:
        `"<role>: <why>"` for each such role, in the order the marks were
        filed. Empty where every role filed at most one.
    """
    by_role: dict[str, list[str]] = {}
    for one in place.filed:
        by_role.setdefault(one.role, []).append(
            f"{one.mark.instruction} at {one.mark.address}"
        )
    return [
        f"{role}: {len(named)} of its marks touch this place -- "
        + ", ".join(named)
        + "; a place takes one mark from a role"
        for role, named in by_role.items()
        if len(named) > 1
    ]


def marks_pass(place: Place) -> Place:
    """The place's state from the marks filed there, and what to advise on them.

    The notes are collected first and kept whatever the state turns out to
    be: a note is something the chief is told, never a reason a place came
    to one state rather than another (`decision-log.md Process: #177`).
    Collected here rather than once per fold so that re-evaluating a place
    from its own record derives them again with everything else.
    """
    place.notes = tuple(
        f"{one.role}: {note}"
        for one in place.filed
        for note in INSTRUCTIONS[one.mark.instruction].notes(
            one.mark, one.touch, place.base
        )
    )
    reasons = _doubled(place)
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
    sides = {
        role: text if text is not None else place.base
        for role, text in proposals.items()
    }
    return _from_sides(place, sides)


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


def answers_pass(place: Place, turn: int) -> Place:
    """Narrow a carried-forward place by the roles' answers at `turn`."""
    if place.state not in CARRIED:
        return place
    answers = place.answers.get(turn, {})
    sides = dict(place.sides)
    for role, answer in answers.items():
        row = ANSWERS.get((answer.question, answer.name))
        if row is None:
            return _set(
                place,
                State.REFUSED,
                reasons=(
                    f"{role}: {answer.name} is not an answer to {answer.question}",
                ),
            )
        effect = row.effect(answer)
        if effect is Effect.UNSETTLABLE:
            return _set(place, State.UNSETTLABLE)
        if effect is Effect.REMOVES:
            sides.pop(role, None)
        elif effect is Effect.REPLACES:
            sides[role] = answer.change
        elif effect is Effect.ACCEPTS and place.text is not None:
            sides[role] = place.text
    return _from_sides(place, sides)


def dispositions_pass(place: Place) -> Place:
    """Close a carried-forward place on the chief's ruling."""
    if place.disposition is None:
        return place
    row = DISPOSITIONS[place.disposition.name]
    if place.state not in row.closes:
        return _set(
            place,
            State.REFUSED,
            reasons=(
                f"copy-chief: {place.disposition.name} cannot close a place "
                f"that is {place.state}",
            ),
        )
    if place.disposition.side not in place.sides and place.disposition.side not in (
        ORIGINAL,
        CHIEF,
    ):
        return _set(
            place,
            State.REFUSED,
            reasons=(f"copy-chief: {place.disposition.side!r} proposed nothing here",),
        )
    text = row.sets(place.disposition, place.base, place.sides)
    return _set(place, State.STANDS, text=text)


def evaluate(place: Place, turn: int = 0) -> Place:
    """Run the marks pass, every turn's answers pass, then the dispositions pass."""
    marks_pass(place)
    for t in range(1, turn + 1):
        answers_pass(place, t)
    return dispositions_pass(place)


def _from_sides(place: Place, sides: dict[str, str]) -> Place:
    distinct = set(sides.values())
    if not sides:
        return _set(place, State.STANDS)
    if len(distinct) == 1:
        text = next(iter(distinct))
        state = State.STANDS if len(sides) == 1 else State.AGREED
        return _set(place, state, text=text)
    try:
        composed = compose(place.base, sides)
    except CannotCompose:
        return _set(place, State.CONTESTED, sides=sides, question=Question.ESCALATION)
    return _set(
        place, State.COMPOSED, text=composed, sides=sides, question=Question.COMPOSITION
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
