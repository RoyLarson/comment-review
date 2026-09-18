"""The three passes, and the pairing of a move's two places."""

from comment_review.desk.answers.answer import Question
from comment_review.desk.answers.table import ANSWERS, Effect
from comment_review.desk.dispositions.disposition import CHIEF, ORIGINAL
from comment_review.desk.dispositions.table import DISPOSITIONS
from comment_review.desk.evaluate.place import Filed, Place
from comment_review.desk.evaluate.state import CARRIED, State
from comment_review.desk.marks.table import INSTRUCTIONS, Stance
from comment_review.machine.differences import CannotCompose, compose


def proposing(filed: list[Filed]) -> list[Filed]:
    """Those of these marks whose row proposes text where they are filed.

    A `clean` and a deferring `query` propose none: they stand beside a
    proposal and are read for their stance, never for a text.
    """
    return [
        one
        for one in filed
        if INSTRUCTIONS[one.mark.instruction].pairs(one.mark) is Stance.PROPOSES
    ]


def _named(one: Filed) -> str:
    """One mark as a reason names it -- its instruction and its own address.

    The address is the mark's own, not the place's: a mark reaching a place is
    not always addressed to it, since a move is filed at its destination under
    its origin's address, and a role fixing the pair has to find both.
    """
    return f"its {one.mark.instruction} at {one.mark.address}"


def composed_side(
    role: str, filed: list[Filed], base: str
) -> tuple[str | None, list[str]]:
    """The one text a role proposes at a place, from every mark it filed there.

    `decision-log.md Process: #179`: a role's own marks compose the way two
    roles' do. One proposing mark sets the side by itself. Two or more compose
    against the base, each keyed by the mark it came from, so marks on
    different sentences become one text and marks on the same sentence are
    refused back to the role rather than one of them silently standing.

    Args:
        role: whose marks these are, for the reason.
        filed: that role's proposing marks at one place, as `proposing`
            returns them. An empty list is not a caller's to pass -- a role
            with no proposal has no side.
        base: the paragraph the place was seeded with, which is what every
            side is measured against.

    Returns:
        `(the text, [])`, the text being whatever the row sets where one mark
        was filed and the composition where several were. Or
        `(None, [one "<role>: <why>" reason])` where they will not compose.
    """
    if len(filed) == 1:
        one = filed[0]
        return INSTRUCTIONS[one.mark.instruction].sets(one.mark, one.touch, base), []
    # Keyed by position, not by what `_named` calls the mark: two of a role's
    # corrections at one address are named the same, and one key would drop
    # one of them into the other and compose a pair with itself.
    texts: dict[str, str] = {}
    for i, one in enumerate(filed):
        text = INSTRUCTIONS[one.mark.instruction].sets(one.mark, one.touch, base)
        texts[f"{i} {_named(one)}"] = base if text is None else text
    try:
        return compose(base, texts), []
    except CannotCompose:
        return None, [
            f"{role}: its marks here edit the same sentence and do not compose"
            f" -- {', '.join(_named(one) for one in filed)}; withdraw one"
        ]


def sides_of(place: Place) -> tuple[dict[str, str | None], tuple[str, ...]]:
    """Role -> the one text it proposes here, and what would not compose.

    One entry per role that filed a proposing mark, whatever number of them it
    filed: a role holds one position on a place, and `#179` is how several of
    its marks make one. A role that proposed nothing is absent, which is what
    keeps a `clean` from reading as a proposal of the base.

    Returns:
        `(role -> its text, the reasons)`. A text is None where the row sets
        nothing there; a role whose marks would not compose is left out and
        named in the reasons instead.
    """
    by_role: dict[str, list[Filed]] = {}
    for one in place.filed:
        by_role.setdefault(one.role, []).append(one)
    sides: dict[str, str | None] = {}
    reasons: list[str] = []
    for role, filed in by_role.items():
        here = proposing(filed)
        if not here:
            continue
        text, why = composed_side(role, here, place.base)
        if why:
            reasons += why
        else:
            sides[role] = text
    return sides, tuple(reasons)


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
    reasons = []
    for one in place.filed:
        row = INSTRUCTIONS[one.mark.instruction]
        reasons += [
            f"{one.role}: {why}" for why in row.reads(one.mark, one.touch, place.base)
        ]
    if reasons:
        return _set(place, State.REFUSED, reasons=tuple(reasons))
    proposals, why = sides_of(place)
    if why:
        return _set(place, State.REFUSED, reasons=why)
    sides = {
        role: text if text is not None else place.base
        for role, text in proposals.items()
    }
    # Asked of every mark filed here, not one per role: a role may file a
    # query beside a proposal, and the place goes to the human on the query
    # whatever else it holds. Its side is recorded all the same, so what it
    # proposed is not lost behind the question.
    if any(
        INSTRUCTIONS[one.mark.instruction].pairs(one.mark) is Stance.UNSETTLABLE
        for one in place.filed
    ):
        return _set(place, State.UNSETTLABLE, sides=sides)
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
