"""The move: one placement claim over two places, and the pass that decides it.

`decision-log.md Process: #195`. A move claims where a paragraph belongs and
nothing else, so its placement is decided once for the pair, by every role
that read either page, before either end's words are.
"""

from comment_review.desk.answers.answer import Answer, Question
from comment_review.desk.evaluate.move import (
    Move,
    Placement,
    moves_in,
    placement_pass,
)
from comment_review.desk.evaluate.place import Filed, Place
from comment_review.desk.marks.mark import Instruction, Mark, Shape
from comment_review.desk.marks.table import Touch

ORIGIN, DESTINATION = "m.py@b1", "m.py@b5"
BASE = "# one\n# two\n# three\n"
LANDING = "# four\n# five\n"
LANDED = "# four\n# two\n# five\n"
HUMAN = {
    "shape": str(Shape.HUMAN_REVIEW_NECESSARY),
    "attempted": "read both ends",
    "settles": "the author",
}
DEFERRING = {
    "shape": str(Shape.OUTSIDE_MY_ROLE),
    "attempted": "read both ends",
    "settles": "ownership-context",
}


def _mark(instruction, address=ORIGIN, change="", raw_text=BASE, claim=None) -> Mark:
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


def _move(origin=ORIGIN, destination=DESTINATION) -> Mark:
    return _mark(
        Instruction.MOVE,
        address=origin,
        change="# two\n",
        raw_text=LANDED,
        claim={"from": origin, "to": destination},
    )


def _ends(*, readers=("a", "b"), at_origin=(), at_destination=()) -> dict[str, Place]:
    move = _move()
    origin = Place(
        address=ORIGIN,
        anchor="x = 1",
        base=BASE,
        readers=readers,
        filed=[Filed("a", move, Touch.ORIGIN), *at_origin],
    )
    destination = Place(
        address=DESTINATION,
        anchor="y = 5",
        base=LANDING,
        readers=readers,
        filed=[Filed("a", move, Touch.DESTINATION), *at_destination],
    )
    return {ORIGIN: origin, DESTINATION: destination}


def _answer(name: str, claim=None) -> Answer:
    return Answer(
        address=ORIGIN,
        anchor="x = 1",
        question=Question.PLACEMENT,
        name=name,
        reason="r",
        claim=claim or {},
    )


def _decided(places, answers=None, turn=1) -> Move:
    (move,) = moves_in(places).values()
    if answers:
        move.answers[turn] = answers
    return placement_pass(move, places, turn)


def test_a_move_is_found_by_its_own_two_addresses():
    moves = moves_in(_ends())
    assert list(moves) == ["m.py@b1 -> m.py@b5"]
    move = moves["m.py@b1 -> m.py@b5"]
    assert set(move.movers) == {"a"} and move.readers == ("a", "b")


def test_a_move_no_other_role_read_is_agreed_at_once():
    """D2: ownership-context alone at 4a -- its moves land before 4c."""
    move = _decided(_ends(readers=("a",)), turn=0)
    assert move.placement is Placement.AGREED and move.owed == ()


def test_a_move_another_reader_has_not_answered_is_open_to_it():
    move = _decided(_ends(), turn=0)
    assert move.placement is Placement.OPEN and move.owed == ("b",)


def test_every_readers_agree_agrees_it():
    move = _decided(_ends(), {"b": _answer("agree")})
    assert move.placement is Placement.AGREED


def test_a_stet_contests_it_and_puts_it_to_the_mover_and_the_stetter():
    move = _decided(
        _ends(readers=("a", "b", "c")), {"b": _answer("stet"), "c": _answer("agree")}
    )
    assert move.placement is Placement.CONTESTED
    assert move.owed == ("a", "b")


def test_a_stetter_who_later_agrees_closes_it():
    places = _ends()
    (move,) = moves_in(places).values()
    move.answers[1] = {"b": _answer("stet"), "a": _answer("agree")}
    move.answers[2] = {"b": _answer("agree"), "a": _answer("agree")}
    assert placement_pass(move, places, 2).placement is Placement.AGREED


def test_the_movers_withdraw_withdraws_it():
    move = _decided(_ends(), {"a": _answer("withdraw"), "b": _answer("agree")})
    assert move.placement is Placement.WITHDRAWN and move.movers == {}


def test_another_roles_withdraw_is_refused_by_name():
    move = _decided(_ends(), {"b": _answer("withdraw")})
    assert move.placement is Placement.REFUSED
    assert move.reasons and move.reasons[0].startswith("b: ")
    assert "only the role that filed a move withdraws it" in move.reasons[0]


def test_a_human_review_query_answer_holds_it():
    move = _decided(_ends(), {"b": _answer("query", HUMAN)})
    assert move.placement is Placement.HELD and move.asking == ("b: r",)


def test_a_human_review_query_filed_at_either_end_holds_it():
    query = _mark(Instruction.QUERY, address=DESTINATION, claim=HUMAN)
    move = _decided(_ends(at_destination=(Filed("b", query, Touch.OWN),)), turn=0)
    assert move.placement is Placement.HELD


def test_a_role_deferring_at_either_end_is_not_owed_the_placement():
    query = _mark(Instruction.QUERY, claim=DEFERRING)
    move = _decided(_ends(at_origin=(Filed("b", query, Touch.OWN),)), turn=0)
    assert move.placement is Placement.AGREED


def test_an_answer_to_another_question_is_refused():
    wrong = Answer(
        address=ORIGIN,
        anchor="x = 1",
        question=Question.COMPOSITION,
        name="clean",
        reason="r",
    )
    move = _decided(_ends(), {"b": wrong})
    assert move.placement is Placement.REFUSED


def test_an_agreed_move_stays_agreed():
    """D4: agreement is final -- the split has already been written."""
    places = _ends()
    (move,) = moves_in(places).values()
    move.placement = Placement.AGREED
    move.answers[2] = {"b": _answer("stet")}
    assert placement_pass(move, places, 2).placement is Placement.AGREED


def test_a_move_round_trips():
    move = _decided(_ends(), {"b": _answer("stet")})
    back, why = Move.deserialize("m", move.serialize())
    assert why == [] and back is not None
    assert (back.origin, back.destination, back.placement) == (
        ORIGIN,
        DESTINATION,
        Placement.CONTESTED,
    )
    assert back.answers == move.answers and back.owed == move.owed


def _two_into_one_place(second_mover: str) -> dict[str, Place]:
    places = _ends(readers=("a",) if second_mover == "a" else ("a", "b"))
    second = _move(origin="m.py@b3")
    places["m.py@b3"] = Place(
        address="m.py@b3",
        anchor="z = 3",
        base=BASE,
        readers=places[ORIGIN].readers,
        filed=[Filed(second_mover, second, Touch.ORIGIN)],
    )
    places[DESTINATION].filed.append(Filed(second_mover, second, Touch.DESTINATION))
    return places


def test_two_roles_moves_into_one_place_are_two_placements():
    """#196: a move is its own two addresses, whoever filed the other."""
    places = _two_into_one_place("b")
    moves = moves_in(places)
    assert set(moves) == {"m.py@b1 -> m.py@b5", "m.py@b3 -> m.py@b5"}
    assert moves["m.py@b1 -> m.py@b5"].movers.keys() == {"a"}
    assert moves["m.py@b3 -> m.py@b5"].movers.keys() == {"b"}


def test_one_roles_two_moves_into_one_place_are_each_agreed_on_their_own():
    """#196 supersedes #154: two pieces of one passage, or two addresses,
    may belong at one place, and neither placement is refused for the other."""
    places = _two_into_one_place("a")
    moves = moves_in(places)
    decided = [placement_pass(move, places, 0) for move in moves.values()]
    assert [move.placement for move in decided] == [Placement.AGREED, Placement.AGREED]


def test_a_recorded_moves_answers_survive_being_found_again():
    places = _ends()
    (move,) = moves_in(places).values()
    move.answers[1] = {"b": _answer("stet")}
    again = moves_in(places, {move.key: move})
    assert again[move.key].answers == {1: {"b": _answer("stet")}}
    assert set(again[move.key].movers) == {"a"}


def test_a_pass_run_twice_on_one_move_comes_to_the_same_placement():
    """A fold re-runs the pass each turn from the record; replaying an
    applied withdrawal must not read it as another role's."""
    places = _ends()
    second = _move()
    places[ORIGIN].filed.append(Filed("b", second, Touch.ORIGIN))
    places[DESTINATION].filed.append(Filed("b", second, Touch.DESTINATION))
    (move,) = moves_in(places).values()
    move.answers[1] = {"a": _answer("withdraw")}
    assert placement_pass(move, places, 1).placement is Placement.OPEN
    assert set(move.movers) == {"b"}
    move.answers[2] = {"b": _answer("withdraw")}
    again = placement_pass(move, places, 2)
    assert again.placement is Placement.WITHDRAWN and again.movers == {}
