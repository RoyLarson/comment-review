"""Human questions: found before a fold, and the human's answers read back.

`decision-log.md Process: #197` and `#198`.
"""

import pytest
from helpers import (
    a_binder_over,
    a_clean,
    a_move,
    a_query,
    a_real_binder_over,
    a_typed_answer,
    copies_over,
    returned,
)

from comment_review.desk.proof.answer import Question
from comment_review.desk.proof.mark import Shape
from comment_review.flows.human import (
    HumanAnswer,
    HumanQuery,
    answered,
    corrections_to_matter,
    queries_in_answers,
    queries_in_copies,
    read_answers,
)

BASE = "# one\n# two\n# three"


def _copies(tmp_path, by_role):
    binder = a_real_binder_over(tmp_path / "repo", {"m.py@b1": BASE, "m.py@b2": BASE})
    return [returned(wire) for wire in copies_over(binder, by_role)]


def _answer(name, shape="", question=Question.COMPOSITION, at="m.py@b1"):
    claim = (
        {"shape": shape, "attempted": "read it", "settles": "the author"}
        if shape
        else {}
    )
    return a_typed_answer(
        address=at,
        anchor="v0 = 0",
        question=question,
        name=name,
        reason="why",
        claim=claim,
    )


def test_a_human_review_query_in_a_copy_is_found_with_its_role_and_place(tmp_path):
    copies = _copies(
        tmp_path,
        {
            "block-context": {
                "m.py@b1": a_query("m.py@b1", Shape.HUMAN_REVIEW_NECESSARY),
                "m.py@b2": a_clean("m.py@b2"),
            },
            "module-context": {
                "m.py@b1": a_clean("m.py@b1"),
                "m.py@b2": a_clean("m.py@b2"),
            },
        },
    )
    got = queries_in_copies(copies)
    assert [(q.role, q.at) for q in got] == [("block-context", "m.py@b1")]
    assert got[0].question  # the query's own reason


def test_a_deferring_query_is_not_a_human_question(tmp_path):
    """Review Focus 5."""
    copies = _copies(
        tmp_path,
        {
            "block-context": {
                "m.py@b1": a_query("m.py@b1", Shape.OUTSIDE_MY_ROLE),
                "m.py@b2": a_query("m.py@b2", Shape.UNABLE_TO_DETERMINE),
            }
        },
    )
    assert queries_in_copies(copies) == []


def test_a_human_review_answer_is_found_under_its_slot_key():
    given = {
        "module-context": {
            "m.py@b1": _answer("clean"),
            "m.py@b1 -> m.py@b5": _answer(
                "query", "human-review-necessary", Question.PLACEMENT
            ),
        },
        "block-context": {"m.py@b2": _answer("query", "outside-my-role", at="m.py@b2")},
    }
    got = queries_in_answers(given)
    assert got == [HumanQuery("module-context", "m.py@b1 -> m.py@b5", "why")]


def test_an_answers_file_reads_one_section_per_query():
    text = (
        '[[answer]]\nrole = "block-context"\nat = "m.py@b1"\n'
        'question = "Is this still true?"\nanswer = "Yes, keep it."\n'
    )
    got, problems = read_answers(text, "human.toml")
    assert problems == []
    assert got == [
        HumanAnswer("block-context", "m.py@b1", "Is this still true?", "Yes, keep it.")
    ]


def test_a_malformed_answers_file_is_named():
    """Review Focus 3."""
    _got, why = read_answers("[[answer\n", "human.toml")
    assert why and why[0].startswith("human.toml: not TOML")
    _got, why = read_answers('answer = "x"\n', "human.toml")
    assert why == ["human.toml: `answer` must be an array of tables, [[answer]]"]
    _got, why = read_answers(
        '[[answer]]\nrole = "block-context"\nat = "m.py@b1"\nquestion = "q"\n',
        "human.toml",
    )
    assert why == ["human.toml: answer 1 needs answer"]


@pytest.mark.parametrize("text", ["", '[[answers]]\nrole = "block-context"\n'])
def test_a_file_with_no_answer_table_is_refused(text):
    got, why = read_answers(text, "human.toml")
    assert got == []
    assert why == ["human.toml: holds no [[answer]] table"]


def test_each_query_is_paired_with_its_own_roles_answer():
    """Review Focus 2: a section for a role that did not ask is not an error."""
    queries = [
        HumanQuery("block-context", "m.py@b1", "q1"),
        HumanQuery("chief", "m.py@b2", "q2"),
    ]
    answers = [
        HumanAnswer("block-context", "m.py@b1", "q1", "a1"),
        HumanAnswer("module-context", "m.py@b1", "q1", "not this role's"),
    ]
    got = answered(queries, answers)
    assert [(q.at, a.answer if a else None) for q, a in got] == [
        ("m.py@b1", "a1"),
        ("m.py@b2", None),
    ]


def test_an_answer_to_another_question_at_the_place_leaves_the_query_open():
    """An answer settles the query whose role, place and question it names; one
    recorded for an earlier question there answers nothing new."""
    queries = [HumanQuery("block-context", "m.py@b1", "the new question")]
    answers = [HumanAnswer("block-context", "m.py@b1", "the old question", "old")]
    assert answered(queries, answers) == [(queries[0], None)]


def test_answers_to_distinct_questions_at_one_place_each_find_their_query():
    queries = [
        HumanQuery("block-context", "m.py@b1", "q1"),
        HumanQuery("block-context", "m.py@b1", "q2"),
    ]
    answers = [
        HumanAnswer("block-context", "m.py@b1", "q2", "a2"),
        HumanAnswer("block-context", "m.py@b1", "q1", "a1"),
    ]
    got = answered(queries, answers)
    assert [(q.question, a.answer if a else None) for q, a in got] == [
        ("q1", "a1"),
        ("q2", "a2"),
    ]


def _section(question, answer):
    return (
        f'[[answer]]\nrole = "block-context"\nat = "m.py@b1"\n'
        f'question = "{question}"\nanswer = "{answer}"\n'
    )


def test_two_answers_to_one_question_are_refused_by_name():
    text = _section("q", "yes") + _section("q", "no") + _section("other", "x")
    got, why = read_answers(text, "human.toml")
    assert why == [
        "human.toml: answer 2 answers block-context at m.py@b1 'q',"
        " which answer 1 already answers"
    ]
    assert got == [
        HumanAnswer("block-context", "m.py@b1", "q", "yes"),
        HumanAnswer("block-context", "m.py@b1", "other", "x"),
    ]


def test_a_move_into_the_matter_is_put_to_the_human_until_answered():
    """`decision-log.md Process: #274`, `#289`."""
    binder = a_binder_over({"m.py@b1": "# one", "m.py@b2": "# two"})
    wire = copies_over(
        binder,
        {
            "ownership-context": {
                "m.py@b1": a_move("m.py@b1", "m.py@f0"),
                "m.py@b2": a_clean("m.py@b2"),
            }
        },
    )[0]
    copies = [returned(wire)]
    assert [q.at for q in corrections_to_matter(copies, ())] == ["m.py@b1"]
    (asked,) = corrections_to_matter(copies, ())
    assert "-> m.py@f0" in asked.question
    other = HumanAnswer("ownership-context", "m.py@b1", "another question", "yes")
    assert corrections_to_matter(copies, (other,)) == [asked]
    yes = HumanAnswer("ownership-context", "m.py@b1", asked.question, "yes")
    assert corrections_to_matter(copies, (yes,)) == []
