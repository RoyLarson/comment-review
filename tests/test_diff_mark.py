"""`desk.diff_mark` -- a PROTOTYPE. See the module's own docstring.

Mirrors `test_mark.py`'s shape tests for `Mark`, over the smaller `DiffMark`.
"""

import pytest

from comment_review.desk.diff_mark import DiffInstruction, DiffMark


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
