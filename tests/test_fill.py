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
from conftest import SAMPLE
from helpers import a_binder_over, a_small_real_tree, binder_of

from comment_review.desk.marks.mark import Mark, untouched
from comment_review.flows.distribute import seed
from comment_review.flows.fill import fill, withdraw

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
        """The two rule on the paragraph's first and last lines, which compose
        -- a role's marks at one place have to (`decision-log.md Process:
        #179`), and `compose` reads edits on adjacent lines as meeting."""
        _, why = fill(copy, _a_correct(claim={"false": "one", "true": "1"}), root)
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


class TestASecondRulingComposesWithTheFirstOrIsRefused:
    """`decision-log.md Process: #179`: a role's marks at one place compose,
    so `mark` asks of the ruling being placed what the fold would ask of the
    pair -- and refuses in the fold's own words rather than leaving the role
    to find out at the fold."""

    def test_a_second_ruling_on_another_sentence_is_placed(self, copy, root):
        """The paragraph's first line and its last: two sentences with one
        between them, which `compose` reads as not meeting."""
        _, why = fill(copy, _a_correct(claim={"false": "one", "true": "1"}), root)
        assert why == []
        second = _a_correct(claim={"false": "three", "true": "3"})
        placed, why = fill(copy, second, root)
        assert why == [] and placed is not None

    def test_a_second_ruling_on_the_same_sentence_is_refused(self, copy, root):
        _, why = fill(copy, _a_correct(), root)
        assert why == []
        before = json.dumps(copy)
        second = _a_correct(claim={"false": "two", "true": "TWO"})
        placed, why = fill(copy, second, root)
        assert placed is None
        assert len(why) == 1, why
        assert "m.py@b1" in why[0] and "do not compose" in why[0]
        assert "withdraw one" in why[0]
        assert json.dumps(copy) == before

    def test_a_pair_elsewhere_on_the_copy_does_not_refuse_this_ruling(self, copy, root):
        """Only the places this ruling touches are asked about. A pair the
        copy already held somewhere else is not this ruling's doing, and
        refusing it here would leave the role no call that lands."""
        for claim in ({"false": "two", "true": "2"}, {"false": "two", "true": "TWO"}):
            fill(copy, {**_a_correct(address="m.py@b5"), "claim": claim}, root)
        placed, why = fill(copy, _a_correct(), root)
        assert why == [] and placed is not None


class TestAWithdrawnMarkLeavesTheSlotAsSeeded:
    """`mark-defects` T24. A second ruling at an address lands beside the
    first, so a role had no way to take back a mark it placed -- and SKILL.md
    sends a refused mark back to the role that wrote it. On the 2026-09-14
    self-run one role edited its copy's JSON by hand to repair eight."""

    def test_a_seeded_slot_is_handed_back_untouched(self, copy, root):
        seeded = dict(_marks(copy)[0])
        fill(copy, _a_correct(), root)
        fill(copy, _a_correct(claim={"false": "one", "true": "1"}), root)
        left, why = withdraw(copy, "m.py@b1")
        assert why == []
        assert [m for m in _marks(copy) if m["address"] == "m.py@b1"] == [seeded]
        assert left is not None and untouched(left)

    def test_a_ruling_placed_again_is_the_only_one(self, copy, root):
        fill(copy, _a_correct(), root)
        withdraw(copy, "m.py@b1")
        placed, why = fill(copy, _a_correct(claim={"false": "one", "true": "1"}), root)
        assert why == []
        assert [m for m in _marks(copy) if m["address"] == "m.py@b1"] == [placed]

    def test_a_slot_the_role_created_is_removed(self, copy, root):
        entry = {
            "address": "m.py@b3",
            "instruction": "add",
            "claim": {"missing": "why y is 2", "anchor": "`y`"},
            "reason": "the constant is explained nowhere",
            "sources": [{"cite": "m.py:5"}],
            "change": "# y is 2 because the fixture says so\n",
        }
        placed, why = fill(copy, entry, root)
        assert why == [] and placed is not None
        left, why = withdraw(copy, "m.py@b3", root)
        assert why == [] and left == {}
        assert all(m["address"] != "m.py@b3" for m in _marks(copy))

    def test_an_add_over_prose_is_handed_back_the_pages_paragraph(self, root):
        """A row that carries its own `raw_text` wrote the paragraph as it
        would read, so the slot's seed is read back off the page rather than
        off the mark that replaced it."""
        copy = seed(binder_of(root, 0), "block-context")
        slot = dict(_marks(copy)[0])
        added = "# y is 2 because the fixture says so\n"
        entry = {
            "address": slot["address"],
            "instruction": "add",
            "claim": {"missing": "why y is 2", "anchor": "`y`"},
            "reason": "the constant is explained nowhere",
            "sources": [{"cite": "m.py:5"}],
            "change": added,
            "raw_text": "# one, two and three.\n" + added,
        }
        placed, why = fill(copy, entry, root)
        assert why == [] and placed is not None
        left, why = withdraw(copy, slot["address"], root)
        assert why == [] and left is not None
        assert left["raw_text"] == slot["raw_text"]
        assert untouched(left)

    def test_a_move_is_handed_back_its_origins_own_paragraph(self, root):
        """A move's `raw_text` is the destination's text, so the origin's slot
        is reseeded off the page too -- handing the mark's back would leave
        the origin holding a paragraph that belongs at the other end."""
        copy = seed(binder_of(root, 0), "block-context")
        slot = dict(_marks(copy)[0])
        entry = {
            "address": slot["address"],
            "instruction": "move",
            "claim": {"from": slot["address"], "to": "m.py@b3"},
            "reason": "the sentence belongs beside the code it describes",
            "sources": [{"cite": "m.py:5"}],
            "change": "# two\n",
            "raw_text": "# four\n# two\n# five\n",
        }
        placed, why = fill(copy, entry, root)
        assert why == [] and placed is not None
        left, why = withdraw(copy, slot["address"], root)
        assert why == [] and left is not None
        assert left["raw_text"] == slot["raw_text"] == "# one\n# two\n# three"
        assert left["anchor"] == slot["anchor"]
        assert untouched(left)

    def test_nothing_placed_is_refused_and_the_copy_is_untouched(self, copy):
        before = json.dumps(copy)
        left, why = withdraw(copy, "m.py@b1")
        assert left is None and "nothing is placed" in why[0], why
        assert json.dumps(copy) == before


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
        assert placed["raw_text"] == entry["change"]
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
        assert placed["raw_text"] == entry["change"]

    def test_a_page_this_copy_has_no_sheet_for_is_refused(self, copy, root):
        before = json.dumps(copy)
        placed, why = fill(copy, _a_correct(address="other.py@b1"), root)
        assert placed is None
        assert len(why) == 1 and "other.py@b1" in why[0] and "no sheet" in why[0]
        assert json.dumps(copy) == before


class TestAMoveCarriesItsSnippetAndTheDestinationsText:
    """`decision-log.md Process: #172` and `#175`. A move's `change` is the
    snippet, subtracted exactly once from the origin's paragraph, and its
    `raw_text` is the destination paragraph as it will read with the snippet
    in. Both are checked against the pages before the mark is placed."""

    def _a_move(self, origin: str, **overrides) -> dict:
        entry = {
            "address": origin,
            "instruction": "move",
            "claim": {"from": origin, "to": "m.py@b3"},
            "reason": "the sentence belongs beside the code it describes",
            "sources": [{"cite": "m.py:5"}],
            "change": "# two\n",
            "raw_text": "# four\n# two\n# five\n",
        }
        entry.update(overrides)
        return entry

    def _origin(self, root) -> tuple[dict, str]:
        copy = seed(binder_of(root, 0), "block-context")
        return copy, _marks(copy)[0]["address"]

    def test_both_texts_land_on_the_mark(self, root):
        copy, origin = self._origin(root)
        placed, why = fill(copy, self._a_move(origin), root)
        assert why == [] and placed is not None
        assert placed["change"] == "# two\n"
        assert placed["raw_text"] == "# four\n# two\n# five\n"

    def test_a_snippet_the_origin_does_not_hold_once_is_refused(self, root):
        copy, origin = self._origin(root)
        before = json.dumps(copy)
        placed, why = fill(copy, self._a_move(origin, change="# nine\n"), root)
        assert placed is None
        assert any("the snippet is not in the origin" in one for one in why), why
        assert json.dumps(copy) == before

    def test_a_destination_text_that_drops_the_snippet_is_refused(self, root):
        copy, origin = self._origin(root)
        entry = self._a_move(origin, raw_text="# four\n# five\n")
        placed, why = fill(copy, entry, root)
        assert placed is None
        assert len(why) == 1 and "does not keep" in why[0]

    def test_a_move_with_no_raw_text_is_refused(self, root):
        copy, origin = self._origin(root)
        entry = self._a_move(origin)
        del entry["raw_text"]
        placed, why = fill(copy, entry, root)
        assert placed is None
        assert len(why) == 1 and "`raw_text`" in why[0]


class TestARowThatDoesNotCarryItsOwnRawTextIsRefusedOne:
    """Every row but `add` and `move` takes its `raw_text` from the page, so a
    role supplying one has misread what the field is for and is told so."""

    def test_a_correct_carrying_a_raw_text_is_refused(self, copy, root):
        before = json.dumps(copy)
        entry = _a_correct(raw_text="# one\n# 2\n# three\n")
        placed, why = fill(copy, entry, root)
        assert placed is None
        assert len(why) == 1 and "`raw_text`" in why[0]
        assert json.dumps(copy) == before

    def test_a_raw_text_equal_to_the_seeded_one_is_not_a_refusal(self, copy, root):
        placed, why = fill(copy, _a_correct(raw_text=BASE), root)
        assert why == [] and placed is not None
        assert placed["raw_text"] == BASE


class TestAnAddAtAPlaceHoldingProseKeepsItsWords:
    """`decision-log.md Process: #132` and `#176`, `mark-defects` T20. An `add`
    where the page already holds prose adds to that paragraph, so the paragraph
    as it will read keeps every word of the prose, in order; punctuation and
    whitespace are free to move. That paragraph is the mark's `raw_text` and
    the role writes it. The copy is seeded from a binder over the real page
    `root` holds, whose `b1` holds `# one`, `# two` and `# three`."""

    def _add_at(self, address: str, change: str, **overrides) -> dict:
        entry = {
            "address": address,
            "instruction": "add",
            "claim": {"missing": "why y is 2", "anchor": "`y`"},
            "reason": "the constant is explained nowhere",
            "sources": [{"cite": "m.py:5"}],
            "change": change,
        }
        entry.update(overrides)
        return entry

    def test_an_add_whose_raw_text_drops_a_word_is_refused(self, root):
        copy = seed(binder_of(root, 0), "block-context")
        slot = _marks(copy)[0]
        assert slot["raw_text"] == "# one\n# two\n# three"
        before = json.dumps(copy)
        added = "# y is 2 because the fixture says so\n"
        reads = "# one\n# three\n" + added
        entry = self._add_at(slot["address"], added, raw_text=reads)
        placed, why = fill(copy, entry, root)
        assert placed is None
        assert len(why) == 1, why
        assert slot["address"] in why[0] and "'two'" in why[0]
        assert json.dumps(copy) == before

    def test_an_add_whose_raw_text_reorders_the_words_is_refused(self, root):
        copy = seed(binder_of(root, 0), "block-context")
        slot = _marks(copy)[0]
        before = json.dumps(copy)
        added = "# y is 2 because the fixture says so\n"
        reads = "# three, two, one\n" + added
        entry = self._add_at(slot["address"], added, raw_text=reads)
        placed, why = fill(copy, entry, root)
        assert placed is None
        assert len(why) == 1 and slot["address"] in why[0], why
        assert json.dumps(copy) == before

    def test_an_add_whose_raw_text_keeps_every_word_in_order_is_placed(self, root):
        copy = seed(binder_of(root, 0), "block-context")
        slot = _marks(copy)[0]
        added = "# y is 2 because the fixture says so\n"
        reads = "# one, two and three.\n" + added
        entry = self._add_at(slot["address"], added, raw_text=reads)
        placed, why = fill(copy, entry, root)
        assert why == [] and placed is not None
        assert placed is slot
        assert placed["raw_text"] == reads
        assert placed["change"] == added

    def test_an_add_over_prose_with_no_raw_text_is_refused(self, root):
        """The paragraph as it will read is the role's, and at a place holding
        prose nothing can derive it -- so its absence is named rather than
        guessed at."""
        copy = seed(binder_of(root, 0), "block-context")
        slot = _marks(copy)[0]
        before = json.dumps(copy)
        added = "# y is 2 because the fixture says so\n"
        placed, why = fill(copy, self._add_at(slot["address"], added), root)
        assert placed is None
        assert len(why) == 1 and "`raw_text`" in why[0], why
        assert json.dumps(copy) == before

    def test_an_add_at_an_empty_place_takes_its_change_as_its_raw_text(self, root):
        """`decision-log.md Process: #176`: at an empty place the snippet and
        the paragraph as it will read are the same text, so nothing is owed."""
        binder = binder_of(root, 0)
        assert "m.py@b3" not in {p.address for p in binder.paragraphs}
        copy = seed(binder, "block-context")
        change = "# y is 2 because the fixture says so\n"
        placed, why = fill(copy, self._add_at("m.py@b3", change), root)
        assert why == [] and placed is not None
        assert placed["raw_text"] == change
        assert _marks(copy)[-1] is placed


class TestAnAddAtAnFPlaceKeepsThePagesProse:
    """`mark-defects` T21. A role is handed no slot at an `f` place, so a
    ruling there is seeded from the page -- its anchor and its `raw_text` --
    and `decision-log.md Process: #132`'s check applies to the prose the page
    holds. The page is `SAMPLE`, whose front matter `f0` is its interpreter
    line."""

    @pytest.fixture
    def front(self, tmp_path) -> Path:
        (tmp_path / "m.py").write_text(SAMPLE, encoding="utf-8", newline="")
        return tmp_path

    def _add_at_f0(self, change: str, **overrides) -> dict:
        entry = {
            "address": "m.py@f0",
            "instruction": "add",
            "claim": {"missing": "what runs the module", "anchor": "`python`"},
            "reason": "the interpreter line is all the front matter says",
            "sources": [{"cite": "m.py:1"}],
            "change": change,
        }
        entry.update(overrides)
        return entry

    def test_an_add_whose_raw_text_drops_the_prose_is_refused(self, front):
        copy = seed(binder_of(front, 0), "block-context")
        assert "m.py@f0" not in {m["address"] for m in _marks(copy)}
        before = json.dumps(copy)
        added = "# runs as a script\n"
        placed, why = fill(copy, self._add_at_f0(added, raw_text=added), front)
        assert placed is None
        assert len(why) == 1 and "m.py@f0" in why[0] and "'usr'" in why[0], why
        assert json.dumps(copy) == before

    def test_an_add_whose_raw_text_keeps_the_pages_prose_is_placed(self, front):
        copy = seed(binder_of(front, 0), "block-context")
        reads = "#!/usr/bin/env python\n# runs as a script\n"
        entry = self._add_at_f0("# runs as a script\n", raw_text=reads)
        placed, why = fill(copy, entry, front)
        assert why == [] and placed is not None
        assert placed["raw_text"] == reads
        assert placed["anchor"] == "<module>"
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
