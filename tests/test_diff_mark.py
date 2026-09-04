"""`desk.diff_mark` -- a PROTOTYPE. See the module's own docstring.

Mirrors `test_mark.py`'s shape tests for `Mark`, over the smaller `DiffMark`.
"""

import pytest

from comment_review.desk.collator import Placed
from comment_review.desk.diff_mark import (
    DiffInstruction,
    DiffMark,
    batch_of,
    parse_batch,
)
from comment_review.desk.mark import Instruction, Mark


def _placed(role: str, address: str, anchor: str = "def f(x):") -> Placed:
    """One role's owing `correct`, at one place -- the shape `Reconciled`'s
    `marks` lists hold. Only what `batch_of` reads is filled in."""
    return Placed(
        Mark(
            address=address,
            anchor=anchor,
            raw_text="# as it stands\n",
            instruction=Instruction.CORRECT,
            claim={"false": "as it stands", "true": "as it should read"},
            reason="the paragraph is stale",
            sources=(),
            change="# as it should read\n",
        ),
        role,
    )


def test_seed_builds_the_slot_from_the_diff_marks_own_names():
    row = DiffMark.seed("m.py@b1", "def f(x):")
    assert row == {
        "address": "m.py@b1",
        "anchor": "def f(x):",
        "instruction": None,
    }


def test_seed_refuses_a_name_the_diff_mark_does_not_declare(monkeypatch):
    monkeypatch.setattr(DiffMark, "SEEDED", ("address", "anchr"))
    with pytest.raises(AttributeError) as caught:
        DiffMark.seed("m.py@b1", "def f(x):")
    assert "anchr" in str(caught.value)


def test_serialize_round_trips_through_deserialize():
    entry = {
        "address": "m.py@b1",
        "anchor": "def f(x):",
        "instruction": "correct",
        "reason": "the other role's finding still stands, worded better",
        "change": "# as it should read\n",
    }
    diff_mark, why = DiffMark.deserialize("m.py@b1", entry)
    assert why == []
    assert diff_mark is not None
    again, why_again = DiffMark.deserialize("m.py@b1", diff_mark.serialize())
    assert why_again == []
    assert again == diff_mark


def test_hold_and_withdraw_need_no_change():
    for instruction in ("hold", "withdraw"):
        entry = {
            "address": "m.py@b1",
            "anchor": "def f(x):",
            "instruction": instruction,
            "reason": "the finding still stands as originally written",
            "change": "",
        }
        diff_mark, why = DiffMark.deserialize("m.py@b1", entry)
        assert why == [], (instruction, why)
        assert diff_mark is not None


def test_correct_without_a_change_is_refused_by_name():
    entry = {
        "address": "m.py@b1",
        "anchor": "def f(x):",
        "instruction": "correct",
        "reason": "the wording needs to change",
        "change": "",
    }
    diff_mark, why = DiffMark.deserialize("m.py@b1", entry)
    assert diff_mark is None
    assert any("needs a `change`" in w for w in why)


@pytest.mark.parametrize("mark_only", ["clean", "query", "drop", "add", "move"])
def test_a_mark_is_refused_where_a_diff_mark_is_owed(mark_only):
    """P20's own verify. A role answering with one of `Mark`'s seven that is
    not also one of the four is refused BY NAME, not silently read as a diff
    mark that happens to share a spelling."""
    entry = {
        "address": "m.py@b1",
        "anchor": "def f(x):",
        "instruction": mark_only,
        "reason": "a fresh finding, not an answer to a disagreement",
    }
    diff_mark, why = DiffMark.deserialize("m.py@b1", entry)
    assert diff_mark is None
    assert any("not one of" in w and "hold" in w for w in why)


def test_an_unrecognised_instruction_is_refused():
    entry = {"address": "m.py@b1", "anchor": "def f(x):", "instruction": "invent"}
    diff_mark, why = DiffMark.deserialize("m.py@b1", entry)
    assert diff_mark is None
    assert any("must be one of" in w for w in why)


def test_no_instruction_at_all_is_refused():
    diff_mark, why = DiffMark.deserialize("m.py@b1", {"address": "m.py@b1"})
    assert diff_mark is None
    assert any("carries no `instruction`" in w for w in why)


def test_a_non_object_entry_is_refused():
    diff_mark, why = DiffMark.deserialize("m.py@b1", "not a dict")
    assert diff_mark is None
    assert why == ["m.py@b1: a diff mark must be an object"]


def test_the_closed_set_is_exactly_four():
    assert {m.value for m in DiffInstruction} == {
        "hold",
        "withdraw",
        "correct",
        "patch",
    }


# === batch_of -- P21


def test_one_send_per_role_whatever_the_place_count():
    """P21's own verify. A role owing two places gets ONE list, not two
    separate sends -- the batch is keyed by role, not by place."""
    escalations = [
        {
            "address": "m.py@b1",
            "roles": ["block-context", "function-context"],
            "marks": [
                _placed("block-context", "m.py@b1"),
                _placed("function-context", "m.py@b1"),
            ],
        },
    ]
    rereads = [
        {
            "address": "m.py@b3",
            "roles": ["block-context"],
            "marks": [
                _placed("block-context", "m.py@b3"),
            ],
        },
    ]
    batch = batch_of(escalations, rereads)
    assert set(batch) == {"block-context", "function-context"}
    assert len(batch["block-context"]) == 2
    assert len(batch["function-context"]) == 1


def test_each_slot_is_a_seeded_diff_mark_naming_its_place():
    escalations = [
        {
            "address": "m.py@b1",
            "roles": ["block-context", "function-context"],
            "marks": [
                _placed("block-context", "m.py@b1"),
                _placed("function-context", "m.py@b1"),
            ],
        },
    ]
    batch = batch_of(escalations, [])
    slot = batch["block-context"][0]
    assert slot["address"] == "m.py@b1"
    assert slot["anchor"] == "def f(x):"
    assert slot["instruction"] is None


def test_the_diff_carries_every_mark_at_the_place_including_the_readers_own():
    """`Mark` has no `role` field, so the diff must ride it beside each
    entry -- the same pairing `Placed` carries -- or a reader cannot tell
    whose finding is whose."""
    escalations = [
        {
            "address": "m.py@b1",
            "roles": ["block-context", "function-context"],
            "marks": [
                _placed("block-context", "m.py@b1"),
                _placed("function-context", "m.py@b1"),
            ],
        },
    ]
    batch = batch_of(escalations, [])
    roles_seen = {mark["role"] for mark in batch["block-context"][0]["marks"]}
    assert roles_seen == {"block-context", "function-context"}
    assert len(batch["block-context"][0]["marks"]) == 2
    assert len(batch["function-context"][0]["marks"]) == 2


def test_no_disagreements_gives_an_empty_batch():
    assert batch_of([], []) == {}


# === parse_batch -- P16


def test_an_unanswered_place_is_refused_never_read_as_a_withdraw():
    """P16's own verify. Left exactly as `batch_of` handed it out."""
    slot = DiffMark.seed("m.py@b1", "def f(x):")
    marks, problems = parse_batch("block-context", [slot])
    assert marks == []
    assert any("unanswered" in p for p in problems)
    assert not any("withdraw" in p and "unanswered" not in p for p in problems)


def test_an_answered_place_parses():
    slot = DiffMark.seed("m.py@b1", "def f(x):")
    slot["instruction"] = "hold"
    slot["reason"] = "the finding still stands"
    marks, problems = parse_batch("block-context", [slot])
    assert problems == []
    assert len(marks) == 1
    assert marks[0].instruction is DiffInstruction.HOLD


def test_a_malformed_answer_is_refused_by_name_not_dropped():
    slot = DiffMark.seed("m.py@b1", "def f(x):")
    slot["instruction"] = "clean"
    marks, problems = parse_batch("block-context", [slot])
    assert marks == []
    assert any("not one of" in p for p in problems)


def test_a_mixed_batch_reports_both_the_parsed_and_the_refused():
    answered = DiffMark.seed("m.py@b1", "def f(x):")
    answered["instruction"] = "withdraw"
    answered["reason"] = "the other role's reading is right"
    unanswered = DiffMark.seed("m.py@b5", "def g():")
    marks, problems = parse_batch("block-context", [answered, unanswered])
    assert len(marks) == 1
    assert len(problems) == 1
    assert "m.py@b5" in problems[0]
