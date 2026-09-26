"""The answers table: what a role's answer in a turn does to its own proposal,
and the contract that publishes the table's own sets."""

from comment_review.desk.answers.answer import Answer, Question
from comment_review.desk.answers.table import ANSWERS, Effect
from comment_review.flows.answers import contracts


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


def test_the_placement_answers():
    """`decision-log.md Process: #195` item 6: a move's placement is a question
    of its own, and its four answers act on the move, not on a side."""
    p = Question.PLACEMENT
    assert ANSWERS[(p, "agree")].effect(_answer(p, "agree")) is Effect.ACCEPTS
    assert ANSWERS[(p, "stet")].effect(_answer(p, "stet")) is Effect.CONTESTS
    assert ANSWERS[(p, "withdraw")].effect(_answer(p, "withdraw")) is Effect.REMOVES
    deferring = _answer(p, "query", claim={"shape": "outside-my-role"})
    human = _answer(p, "query", claim={"shape": "human-review-necessary"})
    assert ANSWERS[(p, "query")].effect(deferring) is Effect.ABSTAINS
    assert ANSWERS[(p, "query")].effect(human) is Effect.UNSETTLABLE
    # A placement answer is about where the paragraph goes; none rewrites it.
    assert not any(row.owes_change for (asked, _), row in ANSWERS.items() if asked is p)
    assert {name for asked, name in ANSWERS if asked is p} == {
        "agree",
        "stet",
        "withdraw",
        "query",
    }


def test_a_placement_answer_is_read_against_its_question():
    got, why = Answer.deserialize(
        "m.py@b1",
        {
            "address": "m.py@b1",
            "question": "placement",
            "instruction": "stet",
            "reason": "r",
        },
    )
    assert why == [] and got is not None and got.name == "stet"
    for name in ("hold", "correct", "patch", "clean"):
        got, why = Answer.deserialize(
            "m.py@b1",
            {
                "address": "m.py@b1",
                "question": "placement",
                "instruction": name,
                "reason": "r",
            },
        )
        assert got is None and "not an answer to a placement" in why[0], name
    for question in ("escalation", "composition"):
        got, why = Answer.deserialize(
            "m.py@b1",
            {
                "address": "m.py@b1",
                "question": question,
                "instruction": "stet",
                "reason": "r",
            },
        )
        assert got is None and "not an answer to" in why[0], question


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


def test_a_query_answer_with_no_shape_is_refused_rather_than_read_as_deferring():
    """`_query_effect` reads `claim.shape` to tell a place held for a person
    from a role standing aside, and a missing key fell to the second -- the
    difference between a review that stops for someone and one that does not.

    ! ASKED OF BOTH QUESTIONS, since the row is what carries the keys: a
    `query` answers a composition alone, so the escalation half is that it is
    not an answer there at all.
    """
    c = Question.COMPOSITION
    for claim in ({}, {"shape": ""}, {"attempted": "read it", "settles": "the chief"}):
        got, why = Answer.deserialize(
            "m.py@b1",
            {
                "address": "m.py@b1",
                "question": str(c),
                "instruction": "query",
                "reason": "r",
                "claim": claim,
            },
        )
        assert got is None, claim
        assert any("needs `claim.shape`" in one for one in why), why
    got, why = Answer.deserialize(
        "m.py@b1",
        {
            "address": "m.py@b1",
            "question": str(c),
            "instruction": "query",
            "reason": "r",
            "claim": {
                "shape": "outside-my-role",
                "attempted": "read it",
                "settles": "the chief",
            },
        },
    )
    assert why == [] and got is not None
    assert ANSWERS[(c, "query")].effect(got) is Effect.ABSTAINS
    got, why = Answer.deserialize(
        "m.py@b1",
        {
            "address": "m.py@b1",
            "question": "escalation",
            "instruction": "query",
            "reason": "r",
            "claim": {"shape": "outside-my-role"},
        },
    )
    assert got is None and "not an answer to an escalation" in why[0]


def test_an_answer_whose_row_owes_no_claim_keys_takes_any_claim():
    for claim in ({}, {"anything": "at all"}, "not an object"):
        got, why = Answer.deserialize(
            "m.py@b1",
            {
                "address": "m.py@b1",
                "question": "escalation",
                "instruction": "hold",
                "reason": "r",
                "claim": claim,
            },
        )
        assert why == [], (claim, why)
        assert got is not None


def test_the_contracts_are_the_tables_own_sets():
    """Ported from `tests/test_turn.py`, which read the same three shapes off
    the old escalation type's own names. They come off the answers table now,
    so a row added to it reaches `check --contract` with no edit here or
    there."""
    got = contracts()
    assert set(got) == {"stage_4c_mark", "escalation", "composition", "placement"}
    assert got["escalation"]["instruction"] == ["correct", "hold", "patch", "withdraw"]
    assert got["escalation"]["owes_change"] == ["correct", "patch"]
    assert got["composition"]["instruction"] == ["clean", "correct", "patch", "query"]
    assert got["composition"]["owes_change"] == ["correct", "patch"]
    assert got["placement"]["instruction"] == ["agree", "query", "stet", "withdraw"]
    assert got["placement"]["owes_change"] == []
    assert got["placement"]["claim"]["query"] == ["shape", "attempted", "settles"]
    assert got["stage_4c_mark"]["instruction"] == sorted(
        ["add", "clean", "correct", "drop", "move", "patch", "query"]
    )


def test_the_contract_names_every_claim_key_the_parse_reads():
    """The keys, and the closed set `shape` takes, published where the role
    that must write them reads. The old contract carried both, off the mark's
    own `allowed()`; this derives them from the answers table."""
    got = contracts()
    assert got["composition"]["claim"] == {
        "clean": [],
        "correct": [],
        "patch": [],
        "query": ["shape", "attempted", "settles"],
    }
    assert got["composition"]["values"] == {
        "shape": ["outside-my-role", "unable-to-determine", "human-review-necessary"]
    }
    # No escalation answer owes a claim, so that question publishes no value
    # set -- an empty map rather than a key a reader would go looking for.
    assert set(got["escalation"]["claim"]) == {"hold", "withdraw", "correct", "patch"}
    assert got["escalation"]["claim"]["correct"] == []
    assert got["escalation"]["values"] == {}
    for question in ("escalation", "composition", "placement"):
        assert "claim" in got[question]["fields"], question


def test_every_claim_key_the_contract_names_is_one_the_parse_demands():
    """The contract is the table's own, so a key it names is a key an answer
    without it is refused for. Read off the contract rather than typed here,
    so a row that gains a key is covered with no edit."""
    given = {"address": "m.py@b1", "question": "composition", "reason": "r"}
    for name, keys in contracts()["composition"]["claim"].items():
        row = ANSWERS[(Question.COMPOSITION, name)]
        entry = {**given, "instruction": name, "claim": dict.fromkeys(keys, "x")}
        if row.owes_change:
            entry["change"] = "# x"
        got, why = Answer.deserialize("m.py@b1", entry)
        assert why == [], (name, why)
        assert got is not None
        for key in keys:
            claim = {k: v for k, v in entry["claim"].items() if k != key}
            got, why = Answer.deserialize("m.py@b1", {**entry, "claim": claim})
            assert got is None, (name, key)
            assert any(f"needs `claim.{key}`" in one for one in why), (name, key, why)


def test_a_placement_and_a_composition_at_one_origin_are_two_answers(tmp_path):
    """Review Focus 1: both are asked of one role at one address in one turn."""
    from comment_review.flows.answers import answers_of, slot_key

    sent = {
        "m.py@b1": {"question": "composition", "anchor": "x = 1"},
        slot_key({"address": "m.py@b1", "to": "m.py@b5"}): {
            "question": "placement",
            "anchor": "x = 1",
        },
    }
    returned = [
        {"address": "m.py@b1", "instruction": "clean", "reason": "r"},
        {"address": "m.py@b1", "to": "m.py@b5", "instruction": "agree", "reason": "r"},
    ]
    got, problems = answers_of("b", sent, returned, lambda a: "not sent", tmp_path, {})
    assert problems == []
    assert got["m.py@b1"].name == "clean"
    assert got["m.py@b1 -> m.py@b5"].name == "agree"
