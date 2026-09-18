"""The marks pass: from the marks filed at a place to its state and text."""

from comment_review.desk.answers.answer import Answer, Question
from comment_review.desk.dispositions.disposition import ORIGINAL, Disposition
from comment_review.desk.evaluate.passes import (
    answers_pass,
    dispositions_pass,
    evaluate,
    marks_pass,
    pair_moves,
    sides_of,
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


def test_sides_holds_only_the_roles_that_propose():
    """A `clean` proposes no text, so its role has no side -- which is what
    keeps it from reading as a proposal of the base."""
    corr = _mark(
        Instruction.CORRECT,
        change="# one\n# 2\n# three\n",
        claim={"false": "two", "true": "2"},
    )
    place = _place(
        Filed("a", corr, Touch.OWN),
        Filed("b", _mark(Instruction.CLEAN), Touch.OWN),
    )
    assert sides_of(place) == ({"a": "# one\n# 2\n# three\n"}, ())


def test_a_move_sets_its_origins_remainder_and_its_destinations_text():
    move = _mark(
        Instruction.MOVE,
        change="# two\n",
        raw_text="# four\n# two\n# five\n",
        claim={"from": "m.py@b1", "to": "m.py@b5"},
    )
    origin = _place(Filed("a", move, Touch.ORIGIN))
    assert sides_of(origin) == ({"a": "# one\n# three\n"}, ())
    landing = _place(Filed("a", move, Touch.DESTINATION), base="# four\n# five\n")
    assert sides_of(landing) == ({"a": "# four\n# two\n# five\n"}, ())


class TestSeveralOfOneRolesMarksAtOnePlace:
    """`decision-log.md Process: #179`: a role's own marks at one place
    compose the way two roles' do. Before it the second overwrote the first in
    a sides map keyed by role, and a role's own correction vanished under its
    own move at exit 0."""

    def _a_correct(self) -> Mark:
        return _mark(
            Instruction.CORRECT,
            change="# one\n# 2\n# three\n",
            claim={"false": "two", "true": "2"},
        )

    def _a_move_landing(self, reads: str) -> Mark:
        return _mark(
            Instruction.MOVE,
            address="m.py@b5",
            change="# five\n",
            raw_text=reads,
            claim={"from": "m.py@b5", "to": "m.py@b1"},
        )

    def _place_with(self, role: str, other: str, reads: str) -> Place:
        return _place(
            Filed(role, self._a_correct(), Touch.OWN),
            Filed(other, self._a_move_landing(reads), Touch.DESTINATION),
        )

    #: The move lands its text above the paragraph, so it edits no line the
    #: correct edits -- the correct replaces the second.
    ABOVE = "# five\n" + BASE
    #: And here it lands on the second line, keeping every word already there
    #: as its row demands -- which is the line the correct rewrites. One
    #: sentence, two marks.
    ON_THE_SENTENCE = "# one\n# two five\n# three\n"

    def test_marks_on_different_sentences_compose_into_one_side(self):
        got = sides_of(self._place_with("a", "a", self.ABOVE))
        assert got == ({"a": "# five\n# one\n# 2\n# three\n"}, ())

    def test_the_composed_side_settles_the_place_as_one_side_would(self):
        got = marks_pass(self._place_with("a", "a", self.ABOVE))
        assert got.state is State.STANDS
        assert got.text == "# five\n# one\n# 2\n# three\n"

    def test_marks_on_the_same_sentence_are_refused_naming_both(self):
        got = marks_pass(self._place_with("a", "a", self.ON_THE_SENTENCE))
        assert got.state is State.REFUSED
        (why,) = got.reasons
        assert why.startswith("a: ")
        assert "its correct at m.py@b1" in why and "its move at m.py@b5" in why
        assert "withdraw one" in why

    def test_two_roles_filing_one_mark_each_still_compose(self):
        got = marks_pass(self._place_with("a", "b", self.ABOVE))
        assert got.state is State.COMPOSED
        assert got.text == "# five\n# one\n# 2\n# three\n"
        assert sorted(got.sides) == ["a", "b"]

    def test_a_composed_side_contests_another_roles(self):
        """The composed text is one role's side and meets the others as any
        side does -- here on the sentence the other role also rewrote."""
        place = self._place_with("a", "a", self.ABOVE)
        place.filed.append(
            Filed(
                "b",
                _mark(
                    Instruction.CORRECT,
                    change="# one\n# TWO\n# three\n",
                    claim={"false": "two", "true": "TWO"},
                ),
                Touch.OWN,
            )
        )
        got = marks_pass(place)
        assert got.state is State.CONTESTED
        assert got.sides["a"] == "# five\n# one\n# 2\n# three\n"
        assert got.sides["b"] == "# one\n# TWO\n# three\n"

    def test_a_query_beside_a_proposal_holds_the_place_and_keeps_the_side(self):
        """A mark that proposes no text stands beside the ones that do, and
        behaves as it would from any role: the human's query holds the place,
        and what the role proposed is still recorded."""
        place = self._place_with("a", "a", self.ABOVE)
        place.filed.append(
            Filed(
                "a",
                _mark(
                    Instruction.QUERY,
                    claim={
                        "shape": str(Shape.HUMAN_REVIEW_NECESSARY),
                        "attempted": "read it",
                        "settles": "human",
                    },
                ),
                Touch.OWN,
            )
        )
        got = marks_pass(place)
        assert got.state is State.UNSETTLABLE
        assert got.sides == {"a": "# five\n# one\n# 2\n# three\n"}
        assert got.reasons == ()


def _a_correct(change="# one\n# 2\n# three\n", false="two", true="2"):
    return _mark(
        Instruction.CORRECT, change=change, claim={"false": false, "true": true}
    )


def test_a_lone_proposal_no_one_else_read_stands():
    """`decision-log.md Process: #180`: the rule waits on the roles that read
    the place, and here there are none."""
    place = _place(Filed("a", _a_correct(), Touch.OWN))
    place.readers = ("a",)
    got = marks_pass(place)
    assert got.state is State.STANDS and got.text == "# one\n# 2\n# three\n"
    assert got.owed == ()


class TestATextEveryReaderMustHaveSeen:
    """`decision-log.md Process: #180`, the one invariant: a place settles on a
    text only when every role that read it, a role that filed only a query
    excluded, has proposed that text or accepted it."""

    def _three_cleans(self) -> Place:
        place = _place(
            Filed("a", _a_correct(), Touch.OWN),
            Filed("b", _mark(Instruction.CLEAN), Touch.OWN),
            Filed("c", _mark(Instruction.CLEAN), Touch.OWN),
            Filed("d", _mark(Instruction.CLEAN), Touch.OWN),
        )
        place.readers = ("a", "b", "c", "d")
        return place

    def test_a_lone_correct_against_three_cleans_is_composed_and_asked_of_them(self):
        got = marks_pass(self._three_cleans())
        assert got.state is State.COMPOSED and got.text == "# one\n# 2\n# three\n"
        assert got.question is Question.COMPOSITION
        assert got.owed == ("b", "c", "d")

    def test_their_cleans_settle_it(self):
        place = marks_pass(self._three_cleans())
        place.answers[1] = {
            role: _answer("clean", question=Question.COMPOSITION) for role in "bcd"
        }
        got = answers_pass(place, 1)
        assert got.state is State.AGREED and got.text == "# one\n# 2\n# three\n"
        assert got.owed == ()

    def test_a_role_that_filed_only_a_query_is_not_waited_on(self):
        place = _place(
            Filed("a", _a_correct(), Touch.OWN),
            Filed(
                "b",
                _mark(Instruction.QUERY, claim={"shape": str(Shape.OUTSIDE_MY_ROLE)}),
                Touch.OWN,
            ),
        )
        place.readers = ("a", "b")
        got = marks_pass(place)
        assert got.state is State.STANDS and got.owed == ()

    def test_one_hold_and_a_withdrawal_go_to_the_roles_that_were_never_asked(self):
        """The role that withdrew has had its say and holds no position; the
        roles that were clean at the first fold have seen no text yet."""
        place = _place(
            Filed("a", _a_correct(), Touch.OWN),
            Filed("b", _a_correct("# one\n# II\n# three\n", true="II"), Touch.OWN),
            Filed("c", _mark(Instruction.CLEAN), Touch.OWN),
            Filed("d", _mark(Instruction.CLEAN), Touch.OWN),
        )
        place.readers = ("a", "b", "c", "d")
        contested = marks_pass(place)
        assert contested.state is State.CONTESTED and contested.owed == ("a", "b")
        place.answers[1] = {"a": _answer("hold"), "b": _answer("withdraw")}
        got = answers_pass(place, 1)
        assert got.state is State.COMPOSED and got.text == "# one\n# 2\n# three\n"
        assert got.owed == ("c", "d")

    def test_an_add_is_carried_to_the_roles_that_read_its_page(self):
        """What `Row.rereads` carried until `#180` -- the same case, decided by
        the one invariant: the roles that read the page have not seen the
        text, so the add is put to them."""
        add = _mark(
            Instruction.ADD,
            raw_text="# new paragraph\n",
            claim={"missing": "a paragraph", "anchor": "`x`"},
        )
        place = _place(Filed("a", add, Touch.OWN), base="")
        place.readers = ("a", "b")
        got = marks_pass(place)
        assert got.state is State.COMPOSED and got.text == "# new paragraph\n"
        assert got.question is Question.COMPOSITION and got.owed == ("b",)

    def test_a_deferring_query_beside_an_add_settles_it(self):
        """`decision-log.md Process: #121`, which the invariant keeps: the one
        role that could have opposed the add abstains, so nothing is owed."""
        add = _mark(
            Instruction.ADD,
            raw_text="# new paragraph\n",
            claim={"missing": "a paragraph", "anchor": "`x`"},
        )
        place = _place(
            Filed("a", add, Touch.OWN),
            Filed(
                "b",
                _mark(Instruction.QUERY, claim={"shape": str(Shape.OUTSIDE_MY_ROLE)}),
                Touch.OWN,
            ),
            base="",
        )
        place.readers = ("a", "b")
        got = marks_pass(place)
        assert got.state is State.STANDS and got.text == "# new paragraph\n"


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


def _answer(name, change="", claim=None, question=Question.ESCALATION):
    return Answer(
        address="m.py@b1",
        anchor="x = 1",
        question=question,
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
