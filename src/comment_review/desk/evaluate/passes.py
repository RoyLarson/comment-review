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
    partner: Place | None = None,
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

    **A role that withdrew at the other end of its own move answered under the
    third of those**, and the answer is filed at the end it was written at, so
    this place cannot see it in its own record: `_withdrew_at_the_partner`
    names those roles and they count as having answered here
    (`Process: #129`, `#190`). Derived from the place, its partner and the
    turn, which this already takes, rather than handed in -- the answers pass
    reads the same function for the sides it takes off, so the rule is reached
    one way.

    Args:
        place: the place being settled, carrying its readers, what was filed
            and every turn's answers.
        text: the one text the sides have come to.
        sides: role -> the text that role proposes, as the pass holds them.
        partner: the other end, where this place is one end of a move. A move
            is one mark at two places, so a role that defers at either end
            defers on the move (`Process: #137` and `#138`) -- otherwise a
            role that queried the origin would be waited on at a destination
            it never marked.
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
    } | _withdrew_at_the_partner(place, partner, turn)
    deferring = _deferring(place) | _deferring(partner)
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


def marks_pass(place: Place, partner: Place | None = None) -> Place:
    """The place's state from the marks filed there, and what to advise on them.

    The notes are collected first and kept whatever the state turns out to
    be: a note is something the chief is told, never a reason a place came
    to one state rather than another (`decision-log.md Process: #177`).
    Collected here rather than once per fold so that re-evaluating a place
    from its own record derives them again with everything else.

    Args:
        place: the place to evaluate.
        partner: the other end, where this place is one end of a move --
            see `owed_a_say`, which is what reads it.
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
    return _from_sides(place, sides, partner)


def pair_moves(places: dict[str, Place]) -> None:
    """A move's two places take one state: the worse of the two.

    An end that takes the other's state takes what that state is read with:
    the question a turn asks about it and the roles it is asked of, where it
    has none of its own. Without them an end carried forward by its partner
    would go out asking nobody.

    An end that has a question of its own keeps it, so a paired place's state
    and its question are read separately: the state says how the move stands,
    the question says what this end's roles are asked, and an answer is read
    against the question alone. A destination can be carried forward contested,
    its partner's state, while it still asks a composition of the roles that
    have not seen its text.

    And an end held for the human decides no text, as `marks_pass` decides
    none where the query was filed. A text left on the end that took the
    state is read downstream as a place the fold decided
    (`flows.places.chief_copy_of` takes every place carrying one), so the move
    the human was asked to rule would be written to the page while the
    question was still open -- measured 2026-09-18 on the smoke's held move,
    which landed at both ends.
    """
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
                taken = other if end is place else place
                end.state = worst
                end.reasons = end.reasons + tuple(
                    r for r in (place.reasons + other.reasons) if r not in end.reasons
                )
                if worst in CARRIED:
                    end.question = end.question or taken.question
                    end.owed = end.owed or taken.owed
                if worst is State.UNSETTLABLE:
                    end.asking = end.asking or taken.asking
                    end.text = None


def _one_mark_at_both(role: str, place: Place, partner: Place) -> bool:
    """Whether one mark of this role's is filed at both of these places.

    A move is one mark at two places, so the entry at the origin and the entry
    at the destination carry the same mark. Compared by value, not by
    identity: a place read back off a proof deserializes its own marks, so the
    one mark is two equal objects once the stage has crossed the wire.
    """
    mine = [one.mark for one in place.filed if one.role == role]
    return any(one.mark in mine for one in partner.filed if one.role == role)


def _withdrew_at_the_partner(
    place: Place, partner: Place | None, turn: int
) -> set[str]:
    """The roles whose answer at the other end of their own move reaches here.

    `decision-log.md Process: #129`, `#152` and `#153`: a move is one mark at
    two places and an answer its filer gives at either end reaches the move
    whole. Which answers cross is the answers row's `reaches_partner`, not a
    name read here; a withdrawal is the one that does, and it takes the
    filer's side off the place it was not written at as well.

    Every turn up to `turn` is read, not `turn` alone: the answer stays on the
    partner's record, and a role that withdrew its move in an earlier turn has
    still withdrawn it in this one. Taking a side off twice does nothing, and
    the roles are what `owed_a_say` needs for as long as the place is open
    (`Process: #190`).

    So a withdrawal is never undone by a later turn, where an acceptance is --
    `_accepting` lets a later `REPLACES` or `REMOVES` take the acceptance back,
    and nothing here takes a withdrawal back. It cannot arise in the fold's own
    flow: a role that answered and holds no side is not asked at that place
    again (`owed_a_say`), and `flows.bus._on_answers` refuses an answer at a
    place the role was not put to, so there is no later answer of its to read.
    MEASURED, on a proof that carries one anyway: where the place it was
    written at has settled it is not read at all (`Process: #91`), and where
    that place is still carried forward the side comes back at that end alone
    and `refuse_half_moves` refuses the pair -- *"its answers leave the move
    half done"* -- rather than letting one half commit.

    Args:
        place: the end being decided.
        partner: the other end, where there is one.
        turn: the last turn whose answers are applied.

    Returns:
        The roles that withdrew at the other end of a mark they filed at both
        places. Empty where the place has no partner, or nothing crossed.
    """
    if partner is None:
        return set()
    out: set[str] = set()
    for at in sorted(one for one in partner.answers if one <= turn):
        for role, answer in partner.answers[at].items():
            row = ANSWERS.get((answer.question, answer.name))
            if row is None or not row.reaches_partner:
                continue
            if _one_mark_at_both(role, place, partner):
                out.add(role)
    return out


def _accepting(place: Place, turn: int) -> set[str]:
    """The roles whose side here was accepted from another rather than proposed.

    A `clean` takes the text that was put to the role (`Effect.ACCEPTS`), so
    that side is a stance toward somebody else's proposal. A later answer that
    replaces or removes it makes the side the role's own again, or none; a
    `hold` leaves it as it stands, acceptance and all.

    `decision-log.md Process: #188` is what reads this: an acceptance of a
    withdrawn move's text goes with the move, and a proposal of the same text
    does not.

    Args:
        place: the place, carrying every turn's answers.
        turn: the turn being decided -- answers after it are not read, as
            `owed_a_say` does not read them.

    Returns:
        The roles, for the caller to ask about a side it is taking off.
    """
    out: set[str] = set()
    for at in sorted(one for one in place.answers if one <= turn):
        for role, answer in place.answers[at].items():
            row = ANSWERS.get((answer.question, answer.name))
            if row is None:
                continue
            effect = row.effect(answer)
            if effect is Effect.ACCEPTS:
                out.add(role)
            elif effect in (Effect.REPLACES, Effect.REMOVES):
                out.discard(role)
    return out


def answers_pass(place: Place, turn: int, partner: Place | None = None) -> Place:
    """Narrow a carried-forward place by the roles' answers at `turn`.

    A place held for the human or refused is left as it is, whatever was
    answered: the first rides to the author (`decision-log.md Process: #90`)
    and the second is rolling the round back.

    !! A WITHDRAWAL AT THE OTHER END OF A MOVE IS READ HERE TOO, and at a
    place this fold is not otherwise narrowing. A move is one mark at two
    places and an answer at either end reaches it whole (`Process: #129`), so
    the reach is a fact about the mark rather than about the state this end
    came to on its own: one end of a move settles with the move and not before
    it, which is `Process: #190` and one step past `#91`.

    Args:
        place: the place, carrying what the marks pass left and the answers.
        turn: which turn's answers to apply.
        partner: the other end of a move, as `marks_pass` takes it.
    """
    if place.state in (State.UNSETTLABLE, State.REFUSED):
        return place
    withdrew = _withdrew_at_the_partner(place, partner, turn)
    if place.state not in CARRIED and not withdrew:
        return place
    sides = dict(place.sides)
    gone = {place.sides[role] for role in withdrew if role in place.sides}
    for role in withdrew:
        sides.pop(role, None)
    # A place the fold has already settled is narrowed by nothing else
    # (`Process: #91`); what reached it above came from the move's other end.
    answers = place.answers.get(turn, {}) if place.state in CARRIED else {}
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
            return _set(place, State.UNSETTLABLE, asking=(f"{role}: {answer.reason}",))
        if effect is Effect.REMOVES:
            sides.pop(role, None)
        elif effect is Effect.REPLACES:
            sides[role] = answer.change
        elif effect is Effect.ACCEPTS and place.text is not None:
            sides[role] = place.text
    # An acceptance of a withdrawn move's text goes with the move
    # (`decision-log.md Process: #188`): a `clean` is a stance toward a
    # proposal, so with the move off the place there is nothing left to
    # accept, and a side left standing on it is what carries a withdrawn move
    # onto the page under another role's name. Unless another role proposes
    # that text itself -- a second move, or a `correct` that came to the same
    # words -- which is the ruling's last clause and is read off the sides
    # that survive: a role withdrawn above holds none, and a role whose side
    # is an acceptance proposes nothing.
    #
    # !! READ AFTER THIS TURN'S OWN ANSWERS, AND THE ORDER IS THE RULE.
    # MEASURED by moving these four lines above the loop: the proposal that
    # protects an acceptance may be written in the same turn as the
    # withdrawal, and read before the loop the only texts here are the ones
    # that turn is about to replace -- three cases of
    # `tests/test_passes.py::TestAnAnswerReachesBothEndsOfTheMove` fail, the
    # acceptance dropped where a `correct` restores its text and kept where
    # nothing does.
    accepting = _accepting(place, turn)
    proposed = {text for role, text in sides.items() if role not in accepting}
    for role in accepting:
        if sides.get(role) in gone - proposed:
            sides.pop(role)
    return _from_sides(place, sides, partner, turn)


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


def refuse_half_moves(places: dict[str, Place]) -> None:
    """Refuse a move whose filer holds a side at one of its ends and none at the other.

    A move is one mark at two places, so the role that filed it holds a side
    at both of them or at neither: the origin's paragraph with the snippet
    gone is only right where the destination's paragraph with the snippet in
    is right too. A commit takes no move half done, and this is where the fold
    finds one.

    It is reachable through one shape: a role answering its own move two ways
    in one turn. The withdrawal reaches the other end (`answers_pass`) and a
    `correct` or `patch` at that end puts the role's side back there, so the
    move is neither withdrawn nor made and the round goes back to the role --
    `decision-log.md Process: #189`, which reads that pair as `#154` reads an
    ambiguous move rather than letting the withdrawal win.

    An end held for the human or already refused is left alone. The first
    decides no text at either end and rides to the author as one move
    (`decision-log.md Process: #155`), and an answer that holds a place keeps
    no sides there, which is the same shape as a side that went.

    So is a pair the chief has ruled at either end: `dispositions_pass` closes
    the end it names and keeps no sides there, so the ruled end and the
    unruled one would read as a move half done. A carried-forward place the
    chief left unruled is refused by name in `flows.bus._on_dispositions`,
    which is the check that case belongs to.
    """
    for address in sorted(places):
        place = places[address]
        other = places.get(place.partner or "")
        if other is None or other.partner != address:
            continue
        if _OUTSIDE_THE_GUARD & {place.state, other.state}:
            continue
        if place.disposition is not None or other.disposition is not None:
            continue
        for role in sorted({one.role for one in place.filed}):
            if not _one_mark_at_both(role, place, other):
                continue
            if (role in place.sides) == (role in other.sides):
                continue
            held, lost = (address, other.address)
            if role not in place.sides:
                held, lost = lost, held
            reason = (
                f"{role}: its answers leave the move half done -- its side"
                f" stands at {held} and is gone at {lost}; an answer at either"
                " end reaches the move whole, so withdraw it at both or keep"
                " it at both"
            )
            _set(place, State.REFUSED, reasons=(reason,))
            _set(other, State.REFUSED, reasons=(reason,))
            break


#: The states `refuse_half_moves` asks nothing of -- see its own docstring.
_OUTSIDE_THE_GUARD = frozenset({State.UNSETTLABLE, State.REFUSED})


def decide(places: dict[str, Place], turn: int = 0) -> dict[str, Place]:
    """Every place decided, in the one order the passes may run in.

    The marks and then each turn's answers, per place; `pair_moves`, which
    gives a move's two ends their one state; the chief's dispositions;
    `pair_moves` again, so an end the chief's ruling refused takes its partner
    with it; and `refuse_half_moves`, which is what the commit asks about a
    move -- last, so it reads the sides every other pass has left.

    !! THE DISPOSITIONS PASS READS THE PAIRED STATE, AND DID NOT UNTIL
    2026-09-18. It ran inside a per-place `evaluate` with the pairing after
    all of them, so the chief's ruling was measured against the state an end
    reaches ALONE. MEASURED through the commands: a move whose origin nobody
    else marked is `agreed` by itself and `contested` once paired, so a run
    that reported both ends contested, put them to both roles and wrote
    `contested` on the proof then refused every ruling the chief made with
    *"taken_in cannot close a place that is agreed"* -- at a place its own
    report had just called contested. The chief could not close a contested
    move at all.

    !! AND IT IS A FUNCTION OF THE PLACES, NOT OF ONE PLACE, for that reason.
    `evaluate(place, turn, partner)` was the entry point and its order was the
    defect; a caller holding one place cannot pair anything, so there is no
    single-place entry left to call in the wrong order. The passes stay public
    and a test drives them one at a time; what is gone is the function that
    looked like the whole sequence and was not.

    Args:
        places: address -> the place, each from its own record. Mutated in
            place and returned, as the passes themselves do.
        turn: the turn to decide at -- every answer up to it is applied.

    Returns:
        `places`, decided.
    """
    for place in places.values():
        partner = places.get(place.partner or "")
        marks_pass(place, partner)
        for t in range(1, turn + 1):
            answers_pass(place, t, partner)
    pair_moves(places)
    for place in places.values():
        dispositions_pass(place)
    # ! THE SECOND PAIRING IS THE CHIEF'S OWN REFUSAL TRAVELLING. Two ends the
    # chief closed are both `stands`, so it changes nothing there -- the guard
    # only touches an end whose state is not the worse of the two, and each
    # keeps the text its own ruling set. What it carries is a ruling the pass
    # refused: a move refused at one end rolls back both, as it does when the
    # refusal comes from the marks.
    pair_moves(places)
    refuse_half_moves(places)
    return places


def _from_sides(
    place: Place,
    sides: dict[str, str],
    partner: Place | None = None,
    turn: int = 0,
) -> Place:
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
        owed = owed_a_say(place, text, sides, partner, turn)
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
        # alone is carried forward by its partner, where the chief's
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
        owed=owed_a_say(place, composed, sides, partner, turn),
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
