"""The answers table: what a role's answer in a turn does to its own proposal."""

from comment_review.desk.answers.answer import Answer, Question
from comment_review.desk.answers.table import ANSWERS, Effect


def _answer(question: Question, name: str, **fields) -> Answer:
    base = {
        "address": "m.py@b1",
        "anchor": "x = 1",
        "question": question,
        "name": name,
        "reason": "a reason",
        "change": "",
        "claim": {},
        "sources": (),
    }
    base.update(fields)
    return Answer(**base)


def test_the_escalation_answers():
    e = Question.ESCALATION
    assert ANSWERS[(e, "hold")].effect(_answer(e, "hold")) is Effect.KEEPS
    assert ANSWERS[(e, "withdraw")].effect(_answer(e, "withdraw")) is Effect.REMOVES
    assert (
        ANSWERS[(e, "correct")].effect(_answer(e, "correct", change="# x"))
        is Effect.REPLACES
    )
    assert ANSWERS[(e, "patch")].owes_change is True
    assert ANSWERS[(e, "hold")].owes_change is False


def test_the_composition_answers():
    c = Question.COMPOSITION
    assert ANSWERS[(c, "clean")].effect(_answer(c, "clean")) is Effect.ACCEPTS
    deferring = _answer(c, "query", claim={"shape": "outside-my-role"})
    human = _answer(c, "query", claim={"shape": "human-review-necessary"})
    assert ANSWERS[(c, "query")].effect(deferring) is Effect.ABSTAINS
    assert ANSWERS[(c, "query")].effect(human) is Effect.UNSETTLABLE
    assert (
        ANSWERS[(c, "correct")].effect(_answer(c, "correct", change="# x"))
        is Effect.REPLACES
    )


def test_an_answer_is_read_against_its_question():
    got, why = Answer.deserialize(
        "m.py@b1",
        {
            "address": "m.py@b1",
            "question": "escalation",
            "instruction": "hold",
            "reason": "r",
        },
    )
    assert why == [] and got is not None and got.name == "hold"
    got, why = Answer.deserialize(
        "m.py@b1",
        {
            "address": "m.py@b1",
            "question": "escalation",
            "instruction": "clean",
            "reason": "r",
        },
    )
    assert got is None and "not an answer to an escalation" in why[0]
    got, why = Answer.deserialize(
        "m.py@b1",
        {
            "address": "m.py@b1",
            "question": "escalation",
            "instruction": "correct",
            "reason": "r",
        },
    )
    assert got is None and "needs a `change`" in why[0]
