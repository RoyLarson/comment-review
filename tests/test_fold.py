"""The Unit of Work: every place decided, or nothing."""

from comment_review.desk.dispositions.disposition import Disposition
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


def test_a_rollback_reports_its_refusals_and_nothing_else():
    """A rollback commits nothing, so beside a refused place nothing settles,
    nobody is asked about a carried or a held place, and a note has no chief's
    copy to go with. Each of those would be reported on a commit.

    The rollback counts reasons, as the bus and the collate command count
    theirs: two roles refused at one place are two."""
    committed = Fold(_a_place_of_each_kind()).run()
    assert [type(e).__name__ for e in committed.events] == [
        "Settled",
        "CarriedForward",
        "Unsettlable",
        "Settled",
        "Advised",
        "Committed",
    ]

    places = _a_place_of_each_kind()
    places["m.py@b5"] = _place(
        "m.py@b5",
        *(
            Filed(
                role,
                _mark(
                    Instruction.MOVE,
                    "# six\n",
                    {"from": "m.py@b5", "to": "m.py@b9"},
                    "m.py@b5",
                ),
                Touch.ORIGIN,
            )
            for role in ("a", "b")
        ),
    )
    fold = Fold(places).run()
    assert not fold.committed
    assert [type(e).__name__ for e in fold.events] == [
        "Refused",
        "Refused",
        "RolledBack",
    ], fold.events
    assert fold.events[-1] == events.RolledBack(reasons=2)


def _a_place_of_each_kind() -> dict:
    """Four places, unfolded: one that settles, one carried forward, one held
    for the human, and one that settles with a note for the chief."""
    return {
        "m.py@b1": _place("m.py@b1", Filed("a", _mark(Instruction.CLEAN), Touch.OWN)),
        "m.py@b2": _place(
            "m.py@b2",
            Filed(
                "a",
                _mark(
                    Instruction.CORRECT,
                    "# one\n# 2\n# three\n",
                    {"false": "two", "true": "2"},
                    "m.py@b2",
                ),
                Touch.OWN,
            ),
            Filed(
                "b",
                _mark(
                    Instruction.CORRECT,
                    "# one\n# II\n# three\n",
                    {"false": "two", "true": "II"},
                    "m.py@b2",
                ),
                Touch.OWN,
            ),
        ),
        "m.py@b3": _place(
            "m.py@b3",
            Filed(
                "a",
                _mark(
                    Instruction.QUERY,
                    claim={"shape": str(Shape.HUMAN_REVIEW_NECESSARY)},
                    address="m.py@b3",
                ),
                Touch.OWN,
            ),
        ),
        "m.py@b4": _place(
            "m.py@b4",
            Filed(
                "a",
                _mark(
                    Instruction.CORRECT,
                    "# one\n# TWO\n",
                    {"false": "two", "true": "TWO"},
                    "m.py@b4",
                ),
                Touch.OWN,
            ),
        ),
    }


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


def test_an_advised_place_is_reported_and_the_fold_commits():
    """`decision-log.md Process: #177`: a note is for the chief to read, not a
    reason to give up the round."""
    correct = _mark(
        Instruction.CORRECT,
        "# one\n# TWO\n",
        {"false": "two", "true": "TWO"},
    )
    fold = Fold({"m.py@b1": _place("m.py@b1", Filed("a", correct, Touch.OWN))})
    fold.run()
    assert fold.committed
    assert [type(e).__name__ for e in fold.events] == [
        "Settled",
        "Advised",
        "Committed",
    ]
    advised = fold.events[1]
    assert advised.role == "a"
    assert advised.address == "m.py@b1"
    assert advised.notes == ("its change drops 'three', which its claim never names",)


def _a_contested_move():
    """block-context moves b1's middle line to b5; function-context corrects
    b5, which contests the destination and pairs the origin to it.

    Returns:
        `{address -> Place}`, unfolded, with each end's `partner` set.
    """
    move = _mark(
        Instruction.MOVE,
        "# two\n",
        {"from": "m.py@b1", "to": "m.py@b5"},
        raw_text="# four\n# five\n# two\n",
    )
    other = _mark(
        Instruction.CORRECT,
        "# four\n# 5\n",
        {"false": "five", "true": "5"},
        address="m.py@b5",
    )
    origin = _place("m.py@b1", Filed("block-context", move, Touch.ORIGIN))
    destination = _place(
        "m.py@b5",
        Filed("block-context", move, Touch.DESTINATION),
        Filed("function-context", other, Touch.OWN),
        base="# four\n# five\n",
    )
    origin.partner, destination.partner = "m.py@b5", "m.py@b1"
    return {"m.py@b1": origin, "m.py@b5": destination}


def _ruled(address: str, name: str, **fields) -> Disposition:
    """One of the chief's rulings, through the real parse.

    ! NOT BUILT DIRECTLY. `Disposition.deserialize` is what fills a `recast`'s
    `side` from its own row, so a hand-built one carries `""` and is refused
    for proposing nothing -- a shape the command cannot produce.
    """
    got, why = Disposition.deserialize(
        address, {"address": address, "answer": name, "reason": "the chief's", **fields}
    )
    assert got is not None, why
    return got


def test_the_chief_closes_a_contested_move_with_a_ruling_at_each_end():
    """!! THE ORIGIN IS THE CASE. It reaches `stands` on its own -- nobody
    marked it but the mover -- and is carried forward only because its
    partner is, so a disposition read before the pairing was measured against
    `agreed` and refused. Both ends are ruled here, and each takes the text
    its own ruling decided.
    """
    places = _a_contested_move()
    # The case has to be able to fail: unruled, this pair is carried forward.
    assert Fold(_a_contested_move()).run().events[0].state is State.CONTESTED
    for address, place in places.items():
        place.disposition = _ruled(address, "taken_in", side="block-context")
    fold = Fold(places).run()
    assert fold.committed, fold.events
    assert [type(e).__name__ for e in fold.events] == [
        "Settled",
        "Settled",
        "Committed",
    ]
    assert fold.decided["m.py@b1"].text == "# one\n# three\n"
    assert fold.decided["m.py@b5"].text == "# four\n# five\n# two\n"


def test_the_chief_may_take_one_end_in_and_recast_the_other():
    """The two ends are ruled by their own dispositions, so the texts they
    close on need not come from one side."""
    places = _a_contested_move()
    recast = "# four\n# five\n# two, as the chief words it\n"
    places["m.py@b1"].disposition = _ruled("m.py@b1", "taken_in", side="block-context")
    places["m.py@b5"].disposition = _ruled("m.py@b5", "recast", prose=recast)
    fold = Fold(places).run()
    assert fold.committed, fold.events
    assert fold.decided["m.py@b1"].text == "# one\n# three\n"
    assert fold.decided["m.py@b5"].text == recast


def test_a_move_ruled_at_one_end_only_is_still_carried_at_both():
    """The fold does not invent the missing ruling. The place the chief left
    alone stays carried forward, and so does the end it is paired to -- which
    is what `flows.bus` refuses by name before it ever folds."""
    places = _a_contested_move()
    places["m.py@b1"].disposition = _ruled("m.py@b1", "taken_in", side="block-context")
    fold = Fold(places).run()
    assert fold.committed, fold.events
    carried = {e.address for e in fold.events if isinstance(e, events.CarriedForward)}
    assert carried == {"m.py@b1", "m.py@b5"}


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
