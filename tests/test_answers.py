"""The answers table: what a role's answer in a turn does to its own proposal,
and the contract that publishes the table's own sets."""

from typing import Any

import pytest
from helpers import a_typed_answer

from comment_review.desk.answers.table import ANSWERS, Effect
from comment_review.desk.proof.answer import (
    Answer,
    Question,
    Rewrite,
    answer_type,
    read_answer,
)
from comment_review.flows.answers import contracts


def _answer(question: Question, name: str, **fields) -> Answer:
    base: dict[str, Any] = {
        "address": "m.py@b1",
        "anchor": "x = 1",
        "question": question,
        "name": name,
        "reason": "a reason",
    }
    base.update(fields)
    return a_typed_answer(**base)


def _kind(name: str) -> type[Answer]:
    kind = answer_type(name)
    assert kind is not None, name
    return kind


def test_every_row_of_the_table_is_an_answer_type_and_its_question():
    """The table's `(question, name)` keys and the types' `asked` state one
    set from two sides, so the two are held equal."""
    typed = {(question, name) for _, name in ANSWERS for question in _kind(name).asked}
    assert typed == set(ANSWERS)
    assert answer_type("stet-it") is None


@pytest.mark.parametrize(("question", "name"), sorted(ANSWERS))
def test_each_answer_writes_the_wire_entry_it_read(question, name):
    """The wire is unchanged by the types: every key a turn carried is
    written back, and it reads back as the same answer."""
    kind = _kind(name)
    entry = {
        "address": "m.py@b1",
        "anchor": "x = 1",
        "question": str(question),
        "reason": "r",
        "change": "# x" if kind.owes_change else "",
        "claim": {
            key: "outside-my-role" if key == "shape" else "x" for key in kind.claim_all
        },
        "sources": [{"cite": "m.py:1", "verbatim": "x = 1"}],
        "instruction": name,
    }
    got, why = read_answer("m.py@b1", entry)
    assert why == [] and type(got) is kind
    assert got is not None
    assert got.serialize() == entry
    again, why = read_answer("m.py@b1", got.serialize())
    assert why == [] and again == got
    assert isinstance(got, Rewrite) is kind.owes_change


def test_the_escalation_answers():
    e = Question.ESCALATION
    assert ANSWERS[(e, "hold")].effect(_answer(e, "hold")) is Effect.KEEPS
    assert ANSWERS[(e, "withdraw")].effect(_answer(e, "withdraw")) is Effect.REMOVES
    assert (
        ANSWERS[(e, "correct")].effect(_answer(e, "correct", change="# x"))
        is Effect.REPLACES
    )
    assert _kind("patch").owes_change is True
    assert _kind("hold").owes_change is False


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
    assert not any(_kind(name).owes_change for asked, name in ANSWERS if asked is p)
    assert {name for asked, name in ANSWERS if asked is p} == {
        "agree",
        "stet",
        "withdraw",
        "query",
    }


def test_a_placement_answer_is_read_against_its_question():
    got, why = read_answer(
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
        got, why = read_answer(
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
        got, why = read_answer(
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
    got, why = read_answer(
        "m.py@b1",
        {
            "address": "m.py@b1",
            "question": "escalation",
            "instruction": "hold",
            "reason": "r",
        },
    )
    assert why == [] and got is not None and got.name == "hold"
    got, why = read_answer(
        "m.py@b1",
        {
            "address": "m.py@b1",
            "question": "escalation",
            "instruction": "clean",
            "reason": "r",
        },
    )
    assert got is None and "not an answer to an escalation" in why[0]
    got, why = read_answer(
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
        got, why = read_answer(
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
    got, why = read_answer(
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
    got, why = read_answer(
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


@pytest.mark.parametrize("question", ["composition", "placement"])
def test_a_query_answer_whose_shape_is_not_one_of_the_three_is_refused(question):
    """A mistyped `human-review-necessary` would otherwise read as deferring --
    a place nobody waits on -- instead of going to the author. Refused as a
    query mark's shape is, in the same words, so `_query_effect` only ever
    sees one of the three."""
    entry = {
        "address": "m.py@b1",
        "question": question,
        "instruction": "query",
        "reason": "r",
        "claim": {"shape": "human-review", "attempted": "a", "settles": "s"},
    }
    got, why = read_answer("m.py@b1", entry)
    assert got is None
    assert why == [
        "m.py@b1: query needs `claim.shape` to be one of outside-my-role,"
        " unable-to-determine, human-review-necessary"
    ]


def test_an_answer_whose_row_owes_no_claim_keys_takes_any_claim():
    for claim in ({}, {"anything": "at all"}, "not an object"):
        got, why = read_answer(
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


def test_the_mark_contract_names_who_writes_raw_text():
    """A role following the contract writes an add's and a move's raw_text;
    the parse refuses either without it (`decision-log.md Process: #175`,
    `#176`)."""
    got = contracts()["stage_4c_mark"]["raw_text"]
    assert got["owed_by"] == ["add", "move"]
    assert "as it will read" in got["is"]


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
    published = contracts()["composition"]
    for name, keys in published["claim"].items():
        # A key whose value is a closed set takes the first the contract names.
        claim = {key: published["values"].get(key, ["x"])[0] for key in keys}
        entry = {**given, "instruction": name, "claim": claim}
        if _kind(name).owes_change:
            entry["change"] = "# x"
        got, why = read_answer("m.py@b1", entry)
        assert why == [], (name, why)
        assert got is not None
        for key in keys:
            claim = {k: v for k, v in entry["claim"].items() if k != key}
            got, why = read_answer("m.py@b1", {**entry, "claim": claim})
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


def test_a_placement_answer_built_from_the_contract_is_taken_at_its_move(tmp_path):
    """A role copies from the slot the fields the contract says are copied
    from it, and writes the rest. For a placement slot that has to include
    `to`, or its answer keys at the origin and is refused."""
    from comment_review.flows.answers import answers_of, slot_key

    fields = contracts()["placement"]["fields"]
    assert "to" in fields
    slot = {
        "address": "m.py@b1",
        "to": "m.py@b5",
        "anchor": "x = 1",
        "question": "placement",
        "movers": [
            {
                "role": "block-context",
                "snippet": "# two\n",
                "raw_text": "# four\n# two\n",
            }
        ],
        "instruction": None,
    }
    copied = {
        name: slot[name]
        for name, meaning in fields.items()
        if meaning.startswith("copied from the slot") and name in slot
    }
    answer = {**copied, "instruction": "agree", "reason": "it reads there"}
    got, problems = answers_of(
        "module-context",
        {slot_key(slot): {"question": "placement", "anchor": "x = 1"}},
        [answer],
        lambda a: "not sent",
        tmp_path,
        {},
    )
    assert problems == []
    assert got["m.py@b1 -> m.py@b5"].name == "agree"
