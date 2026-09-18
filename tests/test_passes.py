"""The marks pass: from the marks filed at a place to its state and text."""

from comment_review.desk.answers.answer import Answer, Question
from comment_review.desk.dispositions.disposition import ORIGINAL, Disposition
from comment_review.desk.evaluate.passes import (
    answers_pass,
    dispositions_pass,
    evaluate,
    marks_pass,
    pair_moves,
)
from comment_review.desk.evaluate.place import Filed, Place
from comment_review.desk.evaluate.state import State
from comment_review.desk.marks.mark import Instruction, Mark, Shape
from comment_review.desk.marks.table import Touch

BASE = "# one\n# two\n# three\n"


def _mark(instruction, change="", raw_text=BASE, claim=None, address="m.py@b1"):
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


def _place(*filed: Filed, base=BASE, address="m.py@b1") -> Place:
    return Place(address=address, anchor="x = 1", base=base, filed=list(filed))


def test_an_all_clean_place_stands_on_its_base():
    place = _place(
        Filed("a", _mark(Instruction.CLEAN), Touch.OWN),
        Filed("b", _mark(Instruction.CLEAN), Touch.OWN),
    )
    got = marks_pass(place)
    assert got.state is State.STANDS and got.text is None


class TestTwoOfOneRolesMarksAtOnePlace:
    """A place holds one text and a role holds one position on it, so two of
    one role's marks reaching it is refused. Before that the second
    overwrote the first in `Place.proposals`, which is keyed by role, and a
    role's own correction vanished under its own move at exit 0."""

    def _a_correct_and_a_move_into_it(self, role: str, other: str) -> Place:
        correct = _mark(
            Instruction.CORRECT,
            change="# one\n# 2\n# three\n",
            claim={"false": "two", "true": "2"},
        )
        moved = _mark(
            Instruction.MOVE,
            address="m.py@b5",
            change="# five\n",
            raw_text=BASE + "# five\n",
            claim={"from": "m.py@b5", "to": "m.py@b1"},
        )
        return _place(
            Filed(role, correct, Touch.OWN),
            Filed(other, moved, Touch.DESTINATION),
        )

    def test_one_role_filing_both_is_refused_naming_each_mark(self):
        got = marks_pass(self._a_correct_and_a_move_into_it("a", "a"))
        assert got.state is State.REFUSED
        assert len(got.reasons) == 1, got.reasons
        (why,) = got.reasons
        assert why.startswith("a: ")
        assert "correct at m.py@b1" in why and "move at m.py@b5" in why

    def test_two_roles_filing_one_mark_each_is_not(self):
        got = marks_pass(self._a_correct_and_a_move_into_it("a", "b"))
        assert got.state is not State.REFUSED
        assert got.reasons == ()

    def test_the_other_role_is_not_named(self):
        place = self._a_correct_and_a_move_into_it("a", "a")
        place.filed.append(Filed("b", _mark(Instruction.CLEAN), Touch.OWN))
        got = marks_pass(place)
        assert [why.split(":")[0] for why in got.reasons] == ["a"]


def test_a_lone_proposal_stands():
    place = _place(
        Filed(
            "a",
            _mark(
                Instruction.CORRECT,
                change="# one\n# 2\n# three\n",
                claim={"false": "two", "true": "2"},
            ),
            Touch.OWN,
        ),
        Filed("b", _mark(Instruction.CLEAN), Touch.OWN),
    )
    got = marks_pass(place)
    assert got.state is State.STANDS and got.text == "# one\n# 2\n# three\n"


def test_two_proposals_of_one_text_agree():
    corr = _mark(
        Instruction.CORRECT,
        change="# one\n# 2\n# three\n",
        claim={"false": "two", "true": "2"},
    )
    patch = _mark(
        Instruction.PATCH,
        change="# one\n# 2\n# three\n",
        claim={"from": "two", "to": "2"},
    )
    got = marks_pass(_place(Filed("a", corr, Touch.OWN), Filed("b", patch, Touch.OWN)))
    assert got.state is State.AGREED and got.text == "# one\n# 2\n# three\n"


def test_two_proposals_on_one_sentence_contest():
    a = _mark(
        Instruction.CORRECT,
        change="# one\n# 2\n# three\n",
        claim={"false": "two", "true": "2"},
    )
    b = _mark(
        Instruction.CORRECT,
        change="# one\n# II\n# three\n",
        claim={"false": "two", "true": "II"},
    )
    got = marks_pass(_place(Filed("a", a, Touch.OWN), Filed("b", b, Touch.OWN)))
    assert got.state is State.CONTESTED and got.text is None
    assert got.sides == {"a": "# one\n# 2\n# three\n", "b": "# one\n# II\n# three\n"}


def test_two_proposals_on_different_sentences_compose():
    a = _mark(
        Instruction.CORRECT,
        change="# 1\n# two\n# three\n",
        claim={"false": "one", "true": "1"},
    )
    b = _mark(
        Instruction.CORRECT,
        change="# one\n# two\n# 3\n",
        claim={"false": "three", "true": "3"},
    )
    got = marks_pass(_place(Filed("a", a, Touch.OWN), Filed("b", b, Touch.OWN)))
    assert got.state is State.COMPOSED and got.text == "# 1\n# two\n# 3\n"


def test_a_human_review_query_makes_the_place_unsettlable_whatever_else_is_there():
    q = _mark(Instruction.QUERY, claim={"shape": str(Shape.HUMAN_REVIEW_NECESSARY)})
    c = _mark(
        Instruction.CORRECT,
        change="# one\n# 2\n# three\n",
        claim={"false": "two", "true": "2"},
    )
    got = marks_pass(_place(Filed("a", q, Touch.OWN), Filed("b", c, Touch.OWN)))
    assert got.state is State.UNSETTLABLE


def test_a_mark_its_row_cannot_read_refuses_the_place_and_names_the_role():
    move = _mark(
        Instruction.MOVE, change="# six\n", claim={"from": "m.py@b1", "to": "m.py@b5"}
    )
    got = marks_pass(_place(Filed("a", move, Touch.ORIGIN)))
    assert got.state is State.REFUSED
    assert got.reasons == (
        "a: the snippet is not in the origin's paragraph: '# six\\n'",
    )


def test_a_moves_two_places_take_one_state():
    move = _mark(
        Instruction.MOVE,
        change="# two\n",
        raw_text="# four\n# two\n# five\n",
        claim={"from": "m.py@b1", "to": "m.py@b5"},
    )
    origin = marks_pass(_place(Filed("a", move, Touch.ORIGIN)))
    other = _mark(
        Instruction.CORRECT,
        change="# four\n# 5\n",
        claim={"false": "five", "true": "5"},
        address="m.py@b5",
    )
    destination = marks_pass(
        _place(
            Filed("a", move, Touch.DESTINATION),
            Filed("b", other, Touch.OWN),
            base="# four\n# five\n",
            address="m.py@b5",
        )
    )
    origin.partner, destination.partner = "m.py@b5", "m.py@b1"
    places = {"m.py@b1": origin, "m.py@b5": destination}
    pair_moves(places)
    assert places["m.py@b1"].state is State.CONTESTED
    assert places["m.py@b5"].state is State.CONTESTED


def test_a_lone_add_composes_even_alone():
    """Ruling R4: an `add` is carried forward and composes on its own text,
    even where it is the place's only proposal -- it does not stand.
    """
    add = _mark(
        Instruction.ADD,
        raw_text="# new paragraph\n",
        claim={"missing": "a paragraph", "anchor": "`x`"},
    )
    got = marks_pass(_place(Filed("a", add, Touch.OWN), base=""))
    assert got.state is State.COMPOSED and got.text == "# new paragraph\n"
    assert got.question is Question.COMPOSITION


def _contested() -> Place:
    a = _mark(
        Instruction.CORRECT,
        change="# one\n# 2\n# three\n",
        claim={"false": "two", "true": "2"},
    )
    b = _mark(
        Instruction.CORRECT,
        change="# one\n# II\n# three\n",
        claim={"false": "two", "true": "II"},
    )
    return marks_pass(_place(Filed("a", a, Touch.OWN), Filed("b", b, Touch.OWN)))


def _answer(name, change="", claim=None):
    return Answer(
        address="m.py@b1",
        anchor="x = 1",
        question=Question.ESCALATION,
        name=name,
        reason="r",
        change=change,
        claim=claim or {},
    )


def test_a_withdrawal_leaves_the_other_side_standing():
    place = _contested()
    place.answers[1] = {"a": _answer("hold"), "b": _answer("withdraw")}
    got = answers_pass(place, 1)
    assert got.state is State.STANDS and got.text == "# one\n# 2\n# three\n"


def test_two_holds_keep_the_place_contested():
    place = _contested()
    place.answers[1] = {"a": _answer("hold"), "b": _answer("hold")}
    assert answers_pass(place, 1).state is State.CONTESTED


def test_both_replacing_with_one_text_agree():
    place = _contested()
    place.answers[1] = {
        "a": _answer("correct", "# one\n# 2\n# three\n"),
        "b": _answer("patch", "# one\n# 2\n# three\n"),
    }
    got = answers_pass(place, 1)
    assert got.state is State.AGREED and got.text == "# one\n# 2\n# three\n"


def test_an_unanswered_role_leaves_its_side_and_the_place_open():
    place = _contested()
    place.answers[1] = {"a": _answer("hold")}
    got = answers_pass(place, 1)
    assert got.state is State.CONTESTED
    assert "b" in got.sides


def test_answers_pass_leaves_a_place_that_is_not_carried_forward_alone():
    stands = marks_pass(
        _place(
            Filed("a", _mark(Instruction.CLEAN), Touch.OWN),
            Filed("b", _mark(Instruction.CLEAN), Touch.OWN),
        )
    )
    state, text, reasons = stands.state, stands.text, stands.reasons
    got = answers_pass(stands, 1)
    assert (got.state, got.text, got.reasons) == (state, text, reasons)

    move = _mark(
        Instruction.MOVE, change="# six\n", claim={"from": "m.py@b1", "to": "m.py@b5"}
    )
    refused = marks_pass(_place(Filed("a", move, Touch.ORIGIN)))
    state, text, reasons = refused.state, refused.text, refused.reasons
    got = answers_pass(refused, 1)
    assert (got.state, got.text, got.reasons) == (state, text, reasons)


def test_answers_pass_refuses_an_unknown_answer_name():
    place = _contested()
    place.answers[1] = {"a": _answer("not-a-real-answer")}
    got = answers_pass(place, 1)
    assert got.state is State.REFUSED
    assert got.reasons == ("a: not-a-real-answer is not an answer to escalation",)


def test_a_taken_in_on_the_original_side_stands_on_the_base():
    place = _contested()
    place.disposition = Disposition(
        address="m.py@b1", name="taken_in", side=ORIGINAL, prose="", reason="r"
    )
    got = dispositions_pass(place)
    assert got.state is State.STANDS and got.text is None
    assert got.base == BASE


def test_a_taken_in_closes_a_contested_place_on_one_side():
    place = _contested()
    place.disposition = Disposition(
        address="m.py@b1", name="taken_in", side="b", prose="", reason="r"
    )
    got = dispositions_pass(place)
    assert got.state is State.STANDS and got.text == "# one\n# II\n# three\n"


def test_a_recast_closes_it_on_the_chiefs_prose():
    place = _contested()
    place.disposition = Disposition(
        address="m.py@b1",
        name="recast",
        side="copy-chief",
        prose="# mine\n",
        reason="r",
    )
    got = dispositions_pass(place)
    assert got.state is State.STANDS and got.text == "# mine\n"


def test_a_disposition_on_an_unsettlable_place_is_refused():
    q = _mark(Instruction.QUERY, claim={"shape": str(Shape.HUMAN_REVIEW_NECESSARY)})
    place = marks_pass(_place(Filed("a", q, Touch.OWN)))
    place.disposition = Disposition(
        address="m.py@b1",
        name="recast",
        side="copy-chief",
        prose="# mine\n",
        reason="r",
    )
    got = dispositions_pass(place)
    assert got.state is State.REFUSED and "unsettlable" in got.reasons[0]


def test_evaluate_runs_the_three_in_order():
    place = _contested()
    place.answers[1] = {"a": _answer("hold"), "b": _answer("hold")}
    place.disposition = Disposition(
        address="m.py@b1", name="taken_in", side="a", prose="", reason="r"
    )
    got = evaluate(place, turn=1)
    assert got.state is State.STANDS and got.text == "# one\n# 2\n# three\n"


def test_a_correct_that_drops_an_unnamed_word_is_noted_and_still_settles():
    """`decision-log.md Process: #163` and `#177`: the words a change drops
    that its claim never named are advisory, so the place settles on the
    change and the note rides beside it."""
    correct = _mark(
        Instruction.CORRECT,
        change="# one\n# TWO\n",
        claim={"false": "two", "true": "TWO"},
    )
    got = marks_pass(_place(Filed("a", correct, Touch.OWN)))
    assert got.state is State.STANDS
    assert got.text == "# one\n# TWO\n"
    assert got.notes == ("a: its change drops 'three', which its claim never names",)


def test_a_correct_that_keeps_every_unnamed_word_is_not_noted():
    correct = _mark(
        Instruction.CORRECT,
        change="# one\n# TWO\n# three\n",
        claim={"false": "two", "true": "TWO"},
    )
    got = marks_pass(_place(Filed("a", correct, Touch.OWN)))
    assert got.state is State.STANDS
    assert got.notes == ()


def test_a_note_survives_the_state_the_place_comes_to():
    """A refusal is decided after the notes are collected, and keeps them."""
    correct = _mark(
        Instruction.CORRECT,
        change="# one\n# TWO\n",
        claim={"false": "two", "true": "TWO"},
    )
    move = _mark(
        Instruction.MOVE,
        change="# nowhere\n",
        claim={"from": "m.py@b1", "to": "m.py@b5"},
    )
    got = marks_pass(
        _place(Filed("a", correct, Touch.OWN), Filed("b", move, Touch.ORIGIN))
    )
    assert got.state is State.REFUSED
    assert got.notes == ("a: its change drops 'three', which its claim never names",)
