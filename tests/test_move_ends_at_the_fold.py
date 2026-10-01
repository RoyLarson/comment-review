"""A move's two ends at the fold, read as the fold reports them.

An agreed move stays filed at both ends (`decision-log.md Process: #205`),
and each end is decided as an ordinary place against the move itself: its
row sets the remainder at the origin and the arrival at the destination. A
refusal anywhere rolls the whole round back and saves nothing, so what a
case asserts is what the fold reports -- committed or rolled back, the
refusals at the place or move that raised them, and, for a committed fold,
each end's state, text and owed roles.

The agreed cases' expected outcomes are the ones the retired split -- the
mover's `drop` at the origin and `add` at the destination -- came to on the
same places, measured against it before it was removed.
"""

import pytest
from helpers import a_typed_answer, a_typed_mark, a_typed_ruling

from comment_review.desk.evaluate.move import moves_in
from comment_review.desk.proof.answer import Question
from comment_review.desk.proof.mark import Instruction, Shape, Touch
from comment_review.desk.proof.place import Filed, Place
from comment_review.desk.proof.state import State
from comment_review.desk.work import events
from comment_review.desk.work.fold import Fold

ORIGIN, DESTINATION = "m.py@b1", "m.py@b5"
KEY = f"{ORIGIN} -> {DESTINATION}"
LANDING = "# four\n# five\n"
BASE = "# one\n# two\n# three\n"
LANDED = "# four\n# two\n# five\n"
NOT_IN_THE_ORIGIN = "the snippet is not in the origin's paragraph: '# nine\\n'"
HUMAN = {"shape": str(Shape.HUMAN_REVIEW_NECESSARY), "attempted": "a", "settles": "s"}


def _move(snippet, arrival):
    return a_typed_mark(
        Instruction.MOVE,
        address=ORIGIN,
        raw_text=arrival,
        claim={"from": ORIGIN, "to": DESTINATION},
        change=snippet,
    )


def _placement(name, claim=None):
    return a_typed_answer(
        address=ORIGIN,
        anchor="x = 1",
        question=Question.PLACEMENT,
        name=name,
        reason="r",
        claim=claim,
    )


def _at_destination(instruction, claim, change, raw_text=LANDING):
    return Filed(
        "b",
        a_typed_mark(
            instruction,
            address=DESTINATION,
            anchor="y = 5",
            raw_text=raw_text,
            claim=claim,
            change=change,
        ),
        Touch.OWN,
    )


def _places(origin_base, landing, movers, readers, at_destination=()):
    """The two ends, every mover's move filed at both."""
    origin = Place(
        address=ORIGIN, anchor="x = 1", base=origin_base, readers=readers, filed=[]
    )
    destination = Place(
        address=DESTINATION,
        anchor="y = 5",
        base=landing,
        readers=readers,
        filed=list(at_destination),
    )
    for role, move in movers.items():
        origin.filed.append(Filed(role, move, Touch.ORIGIN))
        destination.filed.append(Filed(role, move, Touch.DESTINATION))
    return {ORIGIN: origin, DESTINATION: destination}


def _fold(places, answers=None, ruling=None, turn=0):
    """What the fold reports: `(committed, the refusals, each end)`.

    The refusals are `(role, address, reasons)`; each end is `(state, text,
    owed)` and is asked of a committed fold alone -- a rolled-back one saves
    nothing.
    """
    recorded = moves_in(places)
    for move in recorded.values():
        if answers:
            move.answers[1] = answers
        move.disposition = ruling
    fold = Fold(places, recorded, turn=turn).run()
    refusals = [
        (one.role, one.address, one.reasons)
        for one in fold.events
        if isinstance(one, events.Refused)
    ]
    ends = {
        address: (place.state, place.text, place.owed)
        for address, place in fold.decided.items()
    }
    return fold.committed, refusals, ends


AGREED = {
    "whole-paragraph": (
        lambda: _fold(
            _places("# two\n", LANDING, {"a": _move("# two\n", LANDED)}, ("a",))
        ),
        {ORIGIN: (State.STANDS, "", ()), DESTINATION: (State.STANDS, LANDED, ())},
    ),
    "partial-snippet": (
        lambda: _fold(_places(BASE, LANDING, {"a": _move("# two\n", LANDED)}, ("a",))),
        {
            ORIGIN: (State.STANDS, "# one\n# three\n", ()),
            DESTINATION: (State.STANDS, LANDED, ()),
        },
    ),
    "into-an-empty-place": (
        lambda: _fold(_places(BASE, "", {"a": _move("# two\n", "# two\n")}, ("a",))),
        {
            ORIGIN: (State.STANDS, "# one\n# three\n", ()),
            DESTINATION: (State.STANDS, "# two\n", ()),
        },
    ),
    "beside-another-roles-correct": (
        lambda: _fold(
            _places(
                BASE,
                LANDING,
                {"a": _move("# two\n", LANDED)},
                ("a", "b"),
                (
                    _at_destination(
                        Instruction.CORRECT,
                        {"false": "five", "true": "5"},
                        "# four\n# 5\n",
                    ),
                ),
            ),
            answers={"b": _placement("agree")},
            turn=1,
        ),
        {
            ORIGIN: (State.COMPOSED, "# one\n# three\n", ("b",)),
            DESTINATION: (State.COMPOSED, "# four\n# two\n# 5\n", ("a", "b")),
        },
    ),
    "beside-another-roles-patch": (
        lambda: _fold(
            _places(
                BASE,
                LANDING,
                {"a": _move("# two\n", LANDED)},
                ("a", "b"),
                (
                    _at_destination(
                        Instruction.PATCH,
                        {"from": "# four", "to": "# Four"},
                        "# Four\n# five\n",
                    ),
                ),
            ),
            answers={"b": _placement("agree")},
            turn=1,
        ),
        {
            ORIGIN: (State.COMPOSED, "# one\n# three\n", ("b",)),
            DESTINATION: (State.COMPOSED, "# Four\n# two\n# five\n", ("a", "b")),
        },
    ),
    "two-movers-the-chief-takes-one-in": (
        lambda: _fold(
            _places(
                BASE,
                LANDING,
                {
                    "a": _move("# two\n", LANDED),
                    "c": _move("# two\n", "# two\n# four\n# five\n"),
                },
                ("a", "b", "c"),
            ),
            answers={"b": _placement("stet")},
            ruling=a_typed_ruling(
                address=ORIGIN, name="taken_in", side="a", reason="r", to=DESTINATION
            ),
            turn=1,
        ),
        {
            ORIGIN: (State.COMPOSED, "# one\n# three\n", ("b", "c")),
            DESTINATION: (State.COMPOSED, LANDED, ("b", "c")),
        },
    ),
}


@pytest.mark.parametrize("case", sorted(AGREED))
def test_each_end_of_an_agreed_move_comes_to_what_the_split_did(case):
    fold, expected = AGREED[case]
    assert fold() == (True, [], expected)


def test_the_chief_leaves_the_move_it_did_not_take_in_filed_nowhere():
    places = _places(
        BASE,
        LANDING,
        {
            "a": _move("# two\n", LANDED),
            "c": _move("# two\n", "# two\n# four\n# five\n"),
        },
        ("a", "b", "c"),
    )
    _fold(
        places,
        answers={"b": _placement("stet")},
        ruling=a_typed_ruling(
            address=ORIGIN, name="taken_in", side="a", reason="r", to=DESTINATION
        ),
        turn=1,
    )
    for end in places.values():
        assert [one.role for one in end.filed] == ["a"]


#: A move whose snippet the origin does not hold.
MISPLACED = _move("# nine\n", "# four\n# nine\n# five\n")


ROLLED_BACK = {
    # Agreed at once: only the move's own reads at each end speak.
    "agreed-a-snippet-not-in-the-origin": (
        lambda: _fold(_places(BASE, LANDING, {"a": MISPLACED}, ("a",))),
        [("a", ORIGIN, (NOT_IN_THE_ORIGIN,))],
    ),
    "agreed-an-arrival-that-drops-a-word": (
        lambda: _fold(
            _places(BASE, LANDING, {"a": _move("# two\n", "# four\n# two\n")}, ("a",))
        ),
        [("a", DESTINATION, ("the destination text does not keep 'five'",))],
    ),
    # Undecided: each end's refusal at that end, the move's at the move.
    "open-a-snippet-not-in-the-origin": (
        lambda: _fold(_places(BASE, LANDING, {"a": MISPLACED}, ("a", "b"))),
        [("a", ORIGIN, (NOT_IN_THE_ORIGIN,))],
    ),
    "open-another-roles-mark-refused": (
        lambda: _fold(
            _places(
                BASE,
                LANDING,
                {"a": _move("# two\n", LANDED)},
                ("a", "b"),
                (
                    _at_destination(
                        Instruction.ADD,
                        {"missing": "more", "anchor": "`y = 5`"},
                        "# more\n",
                        raw_text="# four\n# more\n",
                    ),
                ),
            )
        ),
        [("b", DESTINATION, ("the text does not keep 'five'",))],
    ),
    "contested-a-snippet-not-in-the-origin": (
        lambda: _fold(
            _places(BASE, LANDING, {"a": MISPLACED}, ("a", "b")),
            answers={"b": _placement("stet")},
            turn=1,
        ),
        [("a", ORIGIN, (NOT_IN_THE_ORIGIN,))],
    ),
    "refused-placement-and-an-end": (
        lambda: _fold(
            _places(BASE, LANDING, {"a": MISPLACED}, ("a", "b")),
            answers={"b": _placement("withdraw")},
            turn=1,
        ),
        [
            ("a", ORIGIN, (NOT_IN_THE_ORIGIN,)),
            (
                "b",
                KEY,
                (
                    "only the role that filed a move withdraws it -- stet it to"
                    " keep the paragraph where it is",
                ),
            ),
        ],
    ),
    "human-query-and-a-snippet-not-in-the-origin": (
        lambda: _fold(
            _places(BASE, LANDING, {"a": MISPLACED}, ("a", "b")),
            answers={"b": _placement("query", HUMAN)},
            turn=1,
        ),
        [
            ("a", ORIGIN, (NOT_IN_THE_ORIGIN,)),
            ("b", KEY, ("human query must be replaced before folding: r",)),
        ],
    ),
}


def test_a_human_placement_answer_rolls_back_naming_the_move():
    places = _places(BASE, LANDING, {"a": _move("# two\n", LANDED)}, ("a", "b"))
    recorded = moves_in(places)
    recorded[KEY].answers[1] = {"b": _placement("query", HUMAN)}
    fold = Fold(places, recorded, turn=1).run()
    assert not fold.committed
    assert [
        (one.address, one.role, one.reasons)
        for one in fold.events
        if isinstance(one, events.Refused)
    ] == [(KEY, "b", ("human query must be replaced before folding: r",))]
    assert fold.decided == {} and fold.decided_moves == {}


@pytest.mark.parametrize("case", sorted(ROLLED_BACK))
def test_a_refusal_rolls_the_round_back_reported_where_it_was_raised(case):
    fold, refusals = ROLLED_BACK[case]
    assert fold() == (False, refusals, {})
