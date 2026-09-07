"""`flows.fill` -- one ruling placed on a role's copy, the way the helpers did it.

! INPUTS ARE REAL: a binder from `a_binder_over`, a copy from the real
`seed`, and a checkout under `tmp_path` holding the page the cites name.
Every expectation is a hand-written paragraph or a hand-checked message.

! WHERE THE EXPECTATIONS COME FROM: the 2026-09-06 and 2026-09-07 runs, where
every role wrote a helper that found the slot by address, substituted the
false clause inside `raw_text`, and appended a second entry for a second
ruling -- `TODO/a-role-writes-its-own-mark-tool.md`.
"""

import json
from pathlib import Path

import pytest
from helpers import a_binder_over

from comment_review.desk.mark import Mark, untouched
from comment_review.flows.distribute import seed
from comment_review.flows.fill import fill

BASE = "# one\n# two\n# three\n"
PAGE = "x = 1\n# one\n# two\n# three\ny = 2\n"


@pytest.fixture
def root(tmp_path) -> Path:
    (tmp_path / "m.py").write_text(PAGE, encoding="utf-8")
    return tmp_path


@pytest.fixture
def copy() -> dict:
    binder = a_binder_over({"m.py@b1": BASE, "m.py@b5": BASE})
    return seed(binder, "block-context")


def _marks(copy: dict) -> list[dict]:
    return copy["sheets"][0]["marks"]


def _a_correct(**overrides) -> dict:
    entry = {
        "address": "m.py@b1",
        "instruction": "correct",
        "claim": {"false": "two", "true": "2"},
        "reason": "the count moved",
        "sources": [{"cite": "m.py:5"}],
    }
    entry.update(overrides)
    return entry


class TestAnUntouchedSlotIsFilledInPlace:
    def test_the_fields_land_on_the_seeded_slot(self, copy, root):
        before = json.dumps(copy)
        placed, why = fill(copy, _a_correct(), root)
        assert why == []
        slot = _marks(copy)[0]
        assert slot is placed
        assert slot["address"] == "m.py@b1"
        assert slot["instruction"] == "correct"
        assert slot["reason"] == "the count moved"
        assert not untouched(slot)
        assert json.dumps(copy) != before

    def test_the_change_is_derived_from_the_slots_raw_text(self, copy, root):
        placed, why = fill(copy, _a_correct(), root)
        assert why == [] and placed is not None
        assert placed["change"] == "# one\n# 2\n# three\n"

    def test_a_change_given_is_taken_as_written(self, copy, root):
        placed, why = fill(copy, _a_correct(change="# one\n# 2\n# three\n"), root)
        assert why == [] and placed is not None
        assert placed["change"] == "# one\n# 2\n# three\n"

    def test_the_verbatim_is_read_from_the_cited_line(self, copy, root):
        placed, why = fill(copy, _a_correct(), root)
        assert why == [] and placed is not None
        assert placed["sources"] == [{"cite": "m.py:5", "verbatim": "y = 2"}]

    def test_a_verbatim_given_is_kept(self, copy, root):
        entry = _a_correct(
            sources=[{"cite": "m.py:5", "verbatim": "y = 2", "ran": "rg y"}]
        )
        placed, why = fill(copy, entry, root)
        assert why == [] and placed is not None
        assert placed["sources"] == [
            {"cite": "m.py:5", "verbatim": "y = 2", "ran": "rg y"}
        ]

    def test_what_lands_is_a_mark_the_parse_accepts(self, copy, root):
        placed, why = fill(copy, _a_correct(), root)
        assert why == []
        mark, problems = Mark.deserialize("m.py@b1", placed)
        assert problems == [] and mark is not None


class TestASecondRulingOnARuledSlotIsAppendedBesideIt:
    def test_the_second_entry_follows_the_first_and_carries_its_seed(self, copy, root):
        _, why = fill(copy, _a_correct(), root)
        assert why == []
        second = _a_correct(claim={"false": "three", "true": "3"})
        placed, why = fill(copy, second, root)
        assert why == []
        marks = _marks(copy)
        assert len(marks) == 3
        assert marks[1] is placed
        assert marks[1]["address"] == marks[0]["address"] == "m.py@b1"
        assert marks[1]["anchor"] == marks[0]["anchor"]
        assert marks[1]["raw_text"] == marks[0]["raw_text"] == BASE
        assert marks[1]["change"] == "# one\n# two\n# 3\n"
        assert marks[2]["address"] == "m.py@b5"


class TestAnAddressWithNoSlotIsAppendedToItsSheet:
    def test_an_add_on_an_empty_place(self, copy, root):
        entry = {
            "address": "m.py@b3",
            "instruction": "add",
            "anchor": "y = 2",
            "claim": {"missing": "why y is 2", "anchor": "`y`"},
            "reason": "the constant is explained nowhere",
            "sources": [{"cite": "m.py:5"}],
            "change": "# y is 2 because the fixture says so\n",
        }
        placed, why = fill(copy, entry, root)
        assert why == []
        marks = _marks(copy)
        assert marks[-1] is placed
        assert placed["address"] == "m.py@b3"
        assert placed["anchor"] == "y = 2"
        assert placed["raw_text"] == ""
        assert placed["sources"] == [{"cite": "m.py:5", "verbatim": "y = 2"}]

    def test_a_page_this_copy_has_no_sheet_for_is_refused(self, copy, root):
        before = json.dumps(copy)
        placed, why = fill(copy, _a_correct(address="other.py@b1"), root)
        assert placed is None
        assert len(why) == 1 and "other.py@b1" in why[0] and "no sheet" in why[0]
        assert json.dumps(copy) == before


class TestARefusalWritesNothing:
    def test_a_clause_not_in_the_paragraph(self, copy, root):
        before = json.dumps(copy)
        placed, why = fill(copy, _a_correct(claim={"false": "four", "true": "4"}), root)
        assert placed is None
        assert len(why) == 1 and "`claim.false`" in why[0]
        assert json.dumps(copy) == before

    def test_a_row_that_derives_nothing_and_is_given_no_change(self, copy, root):
        entry = {
            "address": "m.py@b3",
            "instruction": "add",
            "claim": {"missing": "why y is 2", "anchor": "`y`"},
            "reason": "the constant is explained nowhere",
            "sources": [{"cite": "m.py:5"}],
        }
        placed, why = fill(copy, entry, root)
        assert placed is None
        assert len(why) == 1 and "`change`" in why[0]

    def test_a_cite_to_a_file_that_cannot_be_read(self, copy, root):
        placed, why = fill(copy, _a_correct(sources=[{"cite": "gone.py:1"}]), root)
        assert placed is None
        assert len(why) == 1 and "gone.py:1" in why[0]

    def test_a_cite_past_the_end_of_the_file(self, copy, root):
        placed, why = fill(copy, _a_correct(sources=[{"cite": "m.py:9"}]), root)
        assert placed is None
        assert len(why) == 1 and "m.py:9" in why[0] and "past the end" in why[0]

    def test_a_bare_cite_with_no_checkout_to_read(self, copy):
        placed, why = fill(copy, _a_correct(), None)
        assert placed is None
        assert len(why) == 1 and "checkout" in why[0]

    def test_a_mark_the_parse_refuses_is_refused_with_its_reasons(self, copy, root):
        before = json.dumps(copy)
        placed, why = fill(copy, _a_correct(reason=""), root)
        assert placed is None
        assert any("reason" in m for m in why)
        assert json.dumps(copy) == before

    def test_an_instruction_outside_the_seven(self, copy, root):
        placed, why = fill(copy, _a_correct(instruction="fix"), root)
        assert placed is None
        assert len(why) == 1 and "`instruction`" in why[0]
