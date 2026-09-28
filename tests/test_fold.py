"""The Unit of Work: every place decided, or nothing."""

from dataclasses import replace

from comment_review.desk.answers.answer import Answer, Question
from comment_review.desk.dispositions.disposition import Disposition
from comment_review.desk.evaluate.move import moves_in
from comment_review.desk.proof.mark import Instruction, Mark, Shape, Touch
from comment_review.desk.proof.move import Placement
from comment_review.desk.proof.place import Filed, Place
from comment_review.desk.proof.state import State
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


def _a_move_between(readers):
    move = Mark(
        address="m.py@b1",
        anchor="x = 1",
        raw_text="# four\n# two\n# five\n",
        instruction=Instruction.MOVE,
        claim={"from": "m.py@b1", "to": "m.py@b5"},
        reason="it belongs with five",
        sources=(),
        change="# two\n",
    )
    origin = Place(
        address="m.py@b1",
        anchor="x = 1",
        base="# one\n# two\n# three\n",
        readers=readers,
        filed=[Filed("a", move, Touch.ORIGIN)],
    )
    destination = Place(
        address="m.py@b5",
        anchor="y = 5",
        base="# four\n# five\n",
        readers=readers,
        filed=[Filed("a", move, Touch.DESTINATION)],
    )
    places = {"m.py@b1": origin, "m.py@b5": destination}
    return places, moves_in(places)


def test_a_moves_snippet_missing_from_its_origin_is_one_refusal():
    """One defect, reported once: the origin's own read names it at the
    origin, and neither the declined split nor the other end repeats it."""
    places, _moves = _a_move_between(("a",))
    places["m.py@b1"].base = "# one\n# three\n"
    fold = Fold(places).run()
    assert fold.events == [
        events.Refused(
            "a",
            "m.py@b1",
            ("the snippet is not in the origin's paragraph: '# two\\n'",),
        ),
        events.RolledBack(1),
    ]


def test_a_refused_placement_is_one_refusal_at_the_move():
    """A reason the move itself was refused for is the move's, so it is
    reported once, at the move's own key, and not at each of its ends."""
    places, moves = _a_move_between(("a", "b"))
    moves["m.py@b1 -> m.py@b5"].answers[1] = {
        "b": Answer(
            address="m.py@b1",
            anchor="x = 1",
            question=Question.COMPOSITION,
            name="clean",
            reason="r",
            claim={},
        )
    }
    fold = Fold(places, moves, turn=1).run()
    assert fold.events == [
        events.Refused(
            "b",
            "m.py@b1 -> m.py@b5",
            ("clean is not an answer to a placement",),
        ),
        events.RolledBack(1),
    ]


def test_an_open_move_is_reported_once_with_whom_it_is_put_to():
    places, moves = _a_move_between(("a", "b"))
    fold = Fold(places, moves).run()
    carried = [e for e in fold.events if isinstance(e, events.PlacementCarried)]
    assert carried == [
        events.PlacementCarried("m.py@b1", "m.py@b5", Placement.OPEN, ("b",))
    ]
    assert fold.decided_moves["m.py@b1 -> m.py@b5"].placement is Placement.OPEN


def test_a_held_move_is_one_unsettlable_naming_both_ends():
    places, moves = _a_move_between(("a", "b"))
    human = {
        "shape": str(Shape.HUMAN_REVIEW_NECESSARY),
        "attempted": "a",
        "settles": "b",
    }
    query = Mark(
        address="m.py@b5",
        anchor="y = 5",
        raw_text="# four\n# five\n",
        instruction=Instruction.QUERY,
        claim=human,
        reason="ask",
        sources=(),
        change="",
    )
    places["m.py@b5"].filed.append(Filed("b", query, Touch.OWN))
    fold = Fold(places, moves).run()
    held = [e for e in fold.events if isinstance(e, events.Unsettlable)]
    assert len(held) == 1
    assert (held[0].address, held[0].partner) == ("m.py@b1", "m.py@b5")
    assert held[0].move == events.HeldMove(
        "a", "it belongs with five", "m.py@b1", "m.py@b5"
    )


def test_a_contested_move_the_chief_ruled_asks_no_placement():
    """`b` stets the move in turn 1; the chief takes the move in and rules
    each end's words. The ruling closes the move, so nothing puts its
    placement to the roles again, and both ends settle."""
    places, moves = _a_move_between(("a", "b"))
    move = moves["m.py@b1 -> m.py@b5"]
    move.answers[1] = {
        "b": Answer(
            address="m.py@b1",
            anchor="x = 1",
            question=Question.PLACEMENT,
            name="stet",
            reason="r",
            claim={},
        )
    }
    move.disposition = Disposition(
        address="m.py@b1",
        name="taken_in",
        side="a",
        prose="",
        reason="r",
        to="m.py@b5",
    )
    for address, place in places.items():
        place.disposition = Disposition(
            address=address, name="taken_in", side="a", prose="", reason="r"
        )
    fold = Fold(places, moves, turn=1).run()
    assert fold.decided_moves["m.py@b1 -> m.py@b5"].placement is Placement.AGREED
    assert [type(e).__name__ for e in fold.events] == [
        "Settled",
        "Settled",
        "Committed",
    ], fold.events


def test_a_rolled_back_fold_decides_no_move():
    places, moves = _a_move_between(("a",))
    places["m.py@b1"].filed[0] = Filed(
        "a", replace(places["m.py@b1"].filed[0].mark, change="# nine\n"), Touch.ORIGIN
    )
    fold = Fold(places, moves_in(places)).run()
    assert not fold.committed and fold.decided_moves == {}
