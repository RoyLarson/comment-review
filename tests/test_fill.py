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
from helpers import a_binder_over, a_small_real_tree, binder_of

from comment_review.desk.mark import Mark, untouched
from comment_review.flows.distribute import seed
from comment_review.flows.fill import fill

BASE = "# one\n# two\n# three\n"
#: Six real code lines so the file carries a real, empty `b3` gap (before
#: `w = 4`) for the "no slot" tests to target -- `m.py:5` still names
#: `y = 2`, which the existing cites rely on.
PAGE = "x = 1\n# one\n# two\n# three\ny = 2\nz = 3\nw = 4\n"


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
        assert why == [] and placed is not None
        marks = _marks(copy)
        assert marks[-1] is placed
        assert placed["address"] == "m.py@b3"
        assert placed["anchor"] == "w = 4"
        assert placed["raw_text"] == ""
        assert placed["sources"] == [{"cite": "m.py:5", "verbatim": "y = 2"}]

    def test_the_anchor_comes_from_the_page_not_the_entry(self, copy, root):
        """The base is the system's, never the party being checked. It is
        the rule `desk/collator.base_texts` states for base texts, one layer
        up: an entry's own `anchor` is what a role invented, not what the
        page carries at that place."""
        entry = {
            "address": "m.py@b3",
            "instruction": "add",
            "anchor": "a line the role invented",
            "claim": {"missing": "why y is 2", "anchor": "`y`"},
            "reason": "the constant is explained nowhere",
            "sources": [{"cite": "m.py:5"}],
            "change": "# y is 2 because the fixture says so\n",
        }
        placed, why = fill(copy, entry, root)
        assert why == [] and placed is not None
        assert placed["anchor"] != "a line the role invented"
        assert placed["anchor"] == "w = 4"
        assert placed["raw_text"] == ""

    def test_a_page_this_copy_has_no_sheet_for_is_refused(self, copy, root):
        before = json.dumps(copy)
        placed, why = fill(copy, _a_correct(address="other.py@b1"), root)
        assert placed is None
        assert len(why) == 1 and "other.py@b1" in why[0] and "no sheet" in why[0]
        assert json.dumps(copy) == before


class TestAnAddAtAPlaceHoldingProseKeepsItsWords:
    """`decision-log.md Process: #132`, `mark-defects` T20. An `add` where the
    page already holds prose adds to that paragraph, so its change keeps every
    word of the prose, in order; punctuation and whitespace are free to move.
    The copy is seeded from a binder over the real page `root` holds, whose
    `b1` holds `# one`, `# two` and `# three`."""

    def _add_at(self, address: str, change: str) -> dict:
        return {
            "address": address,
            "instruction": "add",
            "claim": {"missing": "why y is 2", "anchor": "`y`"},
            "reason": "the constant is explained nowhere",
            "sources": [{"cite": "m.py:5"}],
            "change": change,
        }

    def test_an_add_that_drops_a_word_is_refused(self, root):
        copy = seed(binder_of(root, 0), "block-context")
        slot = _marks(copy)[0]
        assert slot["raw_text"] == "# one\n# two\n# three"
        before = json.dumps(copy)
        change = "# one\n# three\n# y is 2 because the fixture says so\n"
        placed, why = fill(copy, self._add_at(slot["address"], change), root)
        assert placed is None
        assert len(why) == 1, why
        assert slot["address"] in why[0] and "'two'" in why[0]
        assert json.dumps(copy) == before

    def test_an_add_that_keeps_the_words_out_of_order_is_refused(self, root):
        copy = seed(binder_of(root, 0), "block-context")
        slot = _marks(copy)[0]
        before = json.dumps(copy)
        change = "# three, two, one\n# y is 2 because the fixture says so\n"
        placed, why = fill(copy, self._add_at(slot["address"], change), root)
        assert placed is None
        assert len(why) == 1 and slot["address"] in why[0], why
        assert json.dumps(copy) == before

    def test_an_add_that_keeps_every_word_in_order_is_placed(self, root):
        copy = seed(binder_of(root, 0), "block-context")
        slot = _marks(copy)[0]
        change = "# one, two and three.\n# y is 2 because the fixture says so\n"
        placed, why = fill(copy, self._add_at(slot["address"], change), root)
        assert why == [] and placed is not None
        assert placed is slot
        assert placed["raw_text"] == "# one\n# two\n# three"
        assert placed["change"] == change

    def test_an_add_at_an_empty_place_has_no_words_to_keep(self, root):
        binder = binder_of(root, 0)
        assert "m.py@b3" not in {p.address for p in binder.paragraphs}
        copy = seed(binder, "block-context")
        change = "# y is 2 because the fixture says so\n"
        placed, why = fill(copy, self._add_at("m.py@b3", change), root)
        assert why == [] and placed is not None
        assert placed["raw_text"] == ""
        assert _marks(copy)[-1] is placed


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


class TestACueThePageDoesNotHaveIsRefused:
    def test_a_cue_the_page_does_not_have_is_refused(self, tmp_path):
        """The page carries every place, absent and present, so a cue it does
        not have names nothing. `decision-log.md Process: #111`."""
        tree = a_small_real_tree(tmp_path)
        copy = seed(binder_of(tree, 0), "block-context")
        entry = {"address": "mark.py@b9999", "instruction": "clean"}
        placed, why = fill(copy, entry, tree)
        assert placed is None
        assert any("names no place on that page" in reason for reason in why)

    def test_a_no_slot_address_with_no_checkout_is_refused_not_raised(self, tmp_path):
        """The cue can only be checked against a real page, so an address
        with no slot and no checkout to build one from is refused rather
        than crashing on `root / rel`."""
        tree = a_small_real_tree(tmp_path)
        copy = seed(binder_of(tree, 0), "block-context")
        entry = {"address": "mark.py@b9999", "instruction": "clean"}
        placed, why = fill(copy, entry, None)
        assert placed is None
        assert any("no checkout" in reason for reason in why)
