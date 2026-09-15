"""The Unit of Work: every place decided, or nothing."""

from comment_review.desk.evaluate.place import Filed, Place
from comment_review.desk.evaluate.state import State
from comment_review.desk.marks.mark import Instruction, Mark, Shape
from comment_review.desk.marks.table import Touch
from comment_review.desk.work import events
from comment_review.desk.work.fold import Fold

BASE = "# one\n# two\n# three\n"


def _mark(instruction, change="", claim=None, address="m.py@b1", raw_text=BASE):
    return Mark(
        address=address,
        anchor="x = 1",
        raw_text=raw_text,
        instruction=instruction,
        claim=claim or {},
        reason="r",
        sources=(),
        change=change,
    )


def _place(address, *filed, base=BASE):
    return Place(address=address, anchor="x = 1", base=base, filed=list(filed))


def test_a_fold_of_settled_places_commits_and_says_what_it_settled():
    fold = Fold(
        {
            "m.py@b1": _place(
                "m.py@b1", Filed("a", _mark(Instruction.CLEAN), Touch.OWN)
            ),
            "m.py@b5": _place(
                "m.py@b5",
                Filed(
                    "a",
                    _mark(
                        Instruction.CORRECT,
                        "# one\n# 2\n# three\n",
                        {"false": "two", "true": "2"},
                        "m.py@b5",
                    ),
                    Touch.OWN,
                ),
            ),
        }
    )
    fold.run()
    assert fold.committed
    assert [type(e).__name__ for e in fold.events] == [
        "Settled",
        "Settled",
        "Committed",
    ]
    assert fold.decided["m.py@b5"].text == "# one\n# 2\n# three\n"


def test_one_refused_place_rolls_the_fold_back():
    move = _mark(Instruction.MOVE, "# six\n", {"from": "m.py@b1", "to": "m.py@b5"})
    fold = Fold(
        {
            "m.py@b1": _place("m.py@b1", Filed("a", move, Touch.ORIGIN)),
            "m.py@b5": _place(
                "m.py@b5",
                Filed("a", _mark(Instruction.CLEAN, address="m.py@b5"), Touch.OWN),
            ),
        }
    )
    fold.run()
    assert not fold.committed
    refused = [e for e in fold.events if isinstance(e, events.Refused)]
    assert refused and refused[0].role == "a" and refused[0].address == "m.py@b1"
    assert isinstance(fold.events[-1], events.RolledBack)


def test_a_carried_and_an_unsettlable_place_are_reported_and_the_fold_commits():
    a = _mark(
        Instruction.CORRECT, "# one\n# 2\n# three\n", {"false": "two", "true": "2"}
    )
    b = _mark(
        Instruction.CORRECT, "# one\n# II\n# three\n", {"false": "two", "true": "II"}
    )
    q = _mark(
        Instruction.QUERY,
        claim={"shape": str(Shape.HUMAN_REVIEW_NECESSARY)},
        address="m.py@b5",
    )
    fold = Fold(
        {
            "m.py@b1": _place(
                "m.py@b1", Filed("a", a, Touch.OWN), Filed("b", b, Touch.OWN)
            ),
            "m.py@b5": _place("m.py@b5", Filed("a", q, Touch.OWN)),
        }
    )
    fold.run()
    assert fold.committed
    kinds = [type(e).__name__ for e in fold.events]
    assert kinds == ["CarriedForward", "Unsettlable", "Committed"]
    carried = fold.events[0]
    assert carried.state is State.CONTESTED and carried.roles == ("a", "b")


def test_a_move_refused_at_one_end_rolls_back_both():
    move = _mark(
        Instruction.MOVE,
        "# two\n",
        {"from": "m.py@b1", "to": "m.py@b5"},
        raw_text="# four\n# five\n",
    )
    origin = _place("m.py@b1", Filed("a", move, Touch.ORIGIN))
    destination = _place(
        "m.py@b5", Filed("a", move, Touch.DESTINATION), base="# four\n# five\n"
    )
    origin.partner, destination.partner = "m.py@b5", "m.py@b1"
    fold = Fold({"m.py@b1": origin, "m.py@b5": destination}).run()
    assert not fold.committed
    assert {e.address for e in fold.events if isinstance(e, events.Refused)} == {
        "m.py@b1",
        "m.py@b5",
    }


def test_a_composed_place_carries_forward_every_reader_beyond_its_sides():
    a = _mark(
        Instruction.CORRECT, "# 1\n# two\n# three\n", {"false": "one", "true": "1"}
    )
    b = _mark(
        Instruction.CORRECT, "# one\n# two\n# 3\n", {"false": "three", "true": "3"}
    )
    place = _place("m.py@b1", Filed("a", a, Touch.OWN), Filed("b", b, Touch.OWN))
    place.readers = ("a", "b", "c")
    fold = Fold({"m.py@b1": place})
    fold.run()
    assert fold.committed
    carried = fold.events[0]
    assert isinstance(carried, events.CarriedForward)
    assert carried.state is State.COMPOSED and carried.roles == ("a", "b", "c")
