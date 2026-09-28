"""Human questions: found before a fold, and the human's answers read back.

`decision-log.md Process: #197` and `#198`.
"""

from helpers import (
    a_clean,
    a_query,
    a_real_binder_over,
    copies_over,
    returned,
)

from comment_review.desk.answers.answer import Answer, Question
from comment_review.desk.proof.mark import Shape
from comment_review.flows.human import (
    HumanAnswer,
    HumanQuery,
    answered,
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
    return Answer(
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
