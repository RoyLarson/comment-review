"""The three passes over a place, run after each move's placement is decided."""

from typing import assert_never

from comment_review.desk.answers.table import ANSWERS, SideAnswerRow, SideEffect
from comment_review.desk.dispositions.table import DISPOSITIONS
from comment_review.desk.evaluate.move import hold_ends, placement_pass, settle_ends
from comment_review.desk.marks.table import INSTRUCTIONS, Stance
from comment_review.desk.proof.answer import Question, Rewrite
from comment_review.desk.proof.disposition import CHIEF, ORIGINAL
from comment_review.desk.proof.mark import Touch
from comment_review.desk.proof.move import Move
from comment_review.desk.proof.place import Filed, Place
from comment_review.desk.proof.state import CARRIED, State
from comment_review.differences import CannotCompose, compose


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
    against the base, each keyed by the mark it came from. Equal edits apply
    once without discarding their filings; competing edits are refused back
    to the role rather than one of them silently standing.

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
        # Marks whose rows set their own `raw_text` -- each a paragraph as it
        # will read (`decision-log.md Process: #196`) -- are all wanted, so
        # the role is asked for one paragraph holding both rather than to
        # give one up. Not at a move's origin, where the text is a remainder
        # rather than an arrival and there is no paragraph holding both.
        whole = all(
            INSTRUCTIONS[one.mark.instruction].carries_raw_text
            and one.touch is not Touch.ORIGIN
            for one in filed
        )
        ask = (
            "restate the paragraph with both texts in each original mark's raw_text;"
            " keep each move's own change, from and to"
            if whole
            else "withdraw one"
        )
        return None, [
            f"{role}: its marks here edit the same sentence and do not compose"
            f" -- {', '.join(_named(one) for one in filed)}; {ask}"
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


def _defers(filed: list[Filed]) -> bool:
    """Whether every one of one role's marks here declines to hold a view.

    The row says so itself: a deferring `query` takes the stance of that
    name, and it is the only mark that does. A `clean` abstains from
    proposing and still holds a view -- it read the paragraph and found
    nothing to report -- so a text it has not been shown owes it a say.

    Args:
        filed: one role's marks at one place, never empty.

    Returns:
        True where the role is not waited on for its say here.
    """
    return all(
        INSTRUCTIONS[one.mark.instruction].pairs(one.mark) is Stance.DEFERS
        for one in filed
    )


def _by_role(place: Place) -> dict[str, list[Filed]]:
    """One role's marks at one place, by role."""
    out: dict[str, list[Filed]] = {}
    for one in place.filed:
        out.setdefault(one.role, []).append(one)
    return out


def _deferring(place: Place | None) -> set[str]:
    """The roles that hold no view at this place, because they filed only queries."""
    if place is None:
        return set()
    return {role for role, filed in _by_role(place).items() if _defers(filed)}


def owed_a_say(
    place: Place,
    text: str,
    sides: dict[str, str],
    turn: int = 0,
) -> tuple[str, ...]:
    """The roles that have not accepted `text`, whose say it still owes.

    `decision-log.md Process: #180`: a place settles on a text only when every
    role that read it has proposed that text or answered `clean` to it. A role
    is owed a say unless one of three things is true of it:

        it filed only a query   it defers, either shape (`Process: #121`)
        its side is this text   it proposed it, or its answer replaced or
                                accepted its way to it
        it answered and holds   it was asked, and withdrew or abstained; it
        no side                 has had its say and holds no position now

    Args:
        place: the place being settled, carrying its readers, what was filed
            and every turn's answers.
        text: the one text the sides have come to.
        sides: role -> the text that role proposes, as the pass holds them.
        turn: the turn being decided. Only answers up to it count: the marks
            pass decides the place as it stood before any turn, and a role
            whose answer has not been applied yet has not had its say.

    Returns:
        The roles owed a say, sorted, so two runs name them in one order.
        Empty where the text may settle.
    """
    filed_by = _by_role(place)
    answered = {
        role for at, by_role in place.answers.items() if at <= turn for role in by_role
    }
    deferring = _deferring(place)
    out = []
    for role in set(place.readers) | set(filed_by):
        if role in deferring:
            continue
        if sides.get(role) == text:
            continue
        if role not in sides and role in answered:
            continue
        out.append(role)
    return tuple(sorted(out))


def marks_pass(place: Place) -> Place:
    """The place's state from the marks filed there, and what to advise on them.

    The notes are collected first and kept whatever the state turns out to
    be: a note is something the chief is told, never a reason a place came
    to one state rather than another (`decision-log.md Process: #177`).
    Collected here rather than once per fold so that re-evaluating a place
    from its own record derives them again with everything else.

    Args:
        place: the place to evaluate.
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
    asking = tuple(
        f"{one.role}: {one.mark.reason}"
        for one in place.filed
        if INSTRUCTIONS[one.mark.instruction].pairs(one.mark) is Stance.UNSETTLABLE
    )
    if asking:
        return _set(place, State.UNSETTLABLE, sides=sides, asking=asking)
    return _from_sides(place, sides)


def answers_pass(place: Place, turn: int) -> Place:
    """Narrow a carried-forward place by the roles' answers at `turn`.

    A place held for the human or refused is left as it is, whatever was
    answered: the first rides to the author (`decision-log.md Process: #90`)
    and the second is rolling the round back.

    Every admitted side effect has a case. A deferral removes the role's
    side while keeping its answer; unrelated readers still owe acceptance.

    Args:
        place: the place, carrying what the marks pass left and the answers.
        turn: which turn's answers to apply.
    """
    if place.state not in CARRIED:
        return place
    sides = dict(place.sides)
    for role, answer in place.answers.get(turn, {}).items():
        row = ANSWERS.get((answer.question, answer.name))
        if row is None:
            return _set(
                place,
                State.REFUSED,
                reasons=(
                    f"{role}: {answer.name} is not an answer to {answer.question}",
                ),
            )
        if not isinstance(row, SideAnswerRow) or answer.question is Question.PLACEMENT:
            return _set(place, State.REFUSED, reasons=(f"{role}: expected a side row",))
        effect = row.effect(answer)
        if not isinstance(effect, SideEffect):
            return _set(place, State.REFUSED, reasons=(f"{role}: invalid side effect",))
        match effect:
            case SideEffect.KEEPS:
                pass
            case SideEffect.REMOVES | SideEffect.DEFERS:
                sides.pop(role, None)
            case SideEffect.REPLACES:
                if not isinstance(answer, Rewrite):
                    return _set(
                        place,
                        State.REFUSED,
                        reasons=(f"{role}: replacement requires Rewrite",),
                    )
                sides[role] = answer.change
            case SideEffect.ACCEPTS:
                if place.text is None:
                    return _set(
                        place,
                        State.REFUSED,
                        reasons=(f"{role}: acceptance requires composed text",),
                    )
                sides[role] = place.text
            case SideEffect.HUMAN_QUERY:
                return _set(
                    place, State.UNSETTLABLE, asking=(f"{role}: {answer.reason}",)
                )
            case _:
                assert_never(effect)
    return _from_sides(place, sides, turn)


def dispositions_pass(place: Place) -> Place:
    """Close a carried-forward place on the chief's ruling.

    A ruling that names the chief's own side (`CHIEF`) where its row does not
    fix that side -- every row but `recast` -- is refused by name, rather than
    reaching `row.sets` and failing to find `copy-chief` among the roles'
    proposed `sides`.
    """
    if place.disposition is None:
        return place
    row = DISPOSITIONS[place.disposition.name]
    side = place.disposition.taken_side
    if place.state not in row.closes:
        return _set(
            place,
            State.REFUSED,
            reasons=(
                f"copy-chief: {place.disposition.name} cannot close a place "
                f"that is {place.state}",
            ),
        )
    if side == CHIEF and place.disposition.default_side != CHIEF:
        return _set(
            place,
            State.REFUSED,
            reasons=(
                f"copy-chief: {place.disposition.name} takes a role's side or the"
                f" original; the chief's own prose is a recast",
            ),
        )
    if side not in place.sides and side not in (ORIGINAL, CHIEF):
        return _set(
            place,
            State.REFUSED,
            reasons=(f"copy-chief: {side!r} proposed nothing here",),
        )
    text = row.sets(place.disposition, place.base, place.sides)
    return _set(place, State.STANDS, text=text)


def decide(
    places: dict[str, Place], moves: "dict[str, Move] | None" = None, turn: int = 0
) -> dict[str, Place]:
    """Every move's placement, then every place, in the one order they run in.

    `decision-log.md Process: #195`: a move is a placement claim decided once
    for the pair before either end's words. So each move's placement pass
    runs first, with the chief's placement ruling where there is one, and a
    final one takes off the filings that no longer stand (`Process: #205`):
    an agreed move stays filed at both ends, and each end is then decided
    against it as an ordinary place. Then each place's marks and answers, as
    for any one-place mark; then every move not yet final holds its two ends
    `to-come` (`Process: #200`); then the chief's dispositions, which a
    `to-come` end does not take.

    Args:
        places: address -> place, each from its own record. Mutated.
        moves: key -> move, from `desk.evaluate.move.moves_in`. Mutated.
            None where the caller has none, which is every place alone.
        turn: the turn to decide at -- every answer up to it is applied.

    Returns:
        `places`, decided.
    """
    moves = {} if moves is None else moves
    for move in moves.values():
        placement_pass(move, places, turn)
        settle_ends(move, places)
    for place in places.values():
        marks_pass(place)
        for t in range(1, turn + 1):
            answers_pass(place, t)
    for move in moves.values():
        hold_ends(move, places)
    for place in places.values():
        dispositions_pass(place)
    return places


def _from_sides(place: Place, sides: dict[str, str], turn: int = 0) -> Place:
    """The place's state from the one text its sides hold, or from their disagreement.

    A text every role owed a say has accepted settles here; a text some have
    not seen is carried forward to exactly those roles, as a composition
    (`decision-log.md Process: #180`). It is the same question at the first
    fold and after a turn, so both reach it here rather than each keeping a
    rule of its own -- which is what made an `add` a special case before.
    """
    distinct = set(sides.values())
    if not sides:
        return _set(place, State.STANDS)
    if len(distinct) == 1:
        text = next(iter(distinct))
        owed = owed_a_say(place, text, sides, turn)
        if owed:
            return _set(
                place,
                State.COMPOSED,
                text=text,
                sides=sides,
                question=Question.COMPOSITION,
                owed=owed,
            )
        state = State.STANDS if len(sides) == 1 else State.AGREED
        # !! THE SIDES ARE KEPT, AND WERE DROPPED HERE UNTIL 2026-09-18. They
        # are what the roles proposed, which is a fact about the marks and not
        # about the state the place came to -- and a move's origin that stands
        # alone is carried forward by `move.hold_ends` while the move's
        # placement is not final, where the chief's
        # `taken_in` names a side and found none to name. MEASURED: the ruling
        # was refused with *"'block-context' proposed nothing here"* at a
        # place that role had moved a paragraph out of.
        return _set(place, state, text=text, sides=sides)
    try:
        composed = compose(place.base, sides)
    except CannotCompose:
        return _set(
            place,
            State.CONTESTED,
            sides=sides,
            question=Question.ESCALATION,
            # The sides are who is asked: a place with no one text yet is put
            # to the roles that hold the texts, and the roles that have seen
            # none of them are owed their say once one text is left.
            owed=tuple(sorted(sides)),
        )
    return _set(
        place,
        State.COMPOSED,
        text=composed,
        sides=sides,
        question=Question.COMPOSITION,
        owed=owed_a_say(place, composed, sides, turn),
    )


def _set(
    place: Place,
    state: State,
    text=None,
    sides=None,
    reasons=(),
    question=None,
    asking=(),
    owed=(),
) -> Place:
    place.state = state
    place.text = text
    place.sides = sides or {}
    place.reasons = reasons
    place.asking = asking
    place.owed = owed
    place.question = question
    return place
