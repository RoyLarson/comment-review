"""The mark's shape, checked against real marks, the brief, and the table.

! INPUTS for the acceptance/refusal cases are the 706 real marks the
2026-08-27 run recorded at `evidence/the-loop-measured-2026-08-27/marks.jsonl`
-- their addresses and their verdicts, actually written by a role -- paired
with claims hand-written from `reviewer-brief.md:280-288` (also
`tests/test_mark_brief.py::BRIEF`). Those EXPECTATIONS are never derived from
`INSTRUCTIONS`.

!! `TestTheTableIsTheContract` AND `TestTheQueryShapes` DO READ `INSTRUCTIONS`
AND `QUERY_SHAPES` -- AS INPUT. `decision-log.md Vocabulary: #23` forbids an
EXPECTATION taken from the module under test; it expressly permits an INPUT
read from it. Every expectation in those two classes is a hand-checked
literal (`["clean"]`, `"needs no source"`, `False`, a retired shape string, a
non-empty check) -- none is derived from the row it is checking.
"""

import json
from pathlib import Path

import pytest
from test_mark_brief import BRIEF

from comment_review.desk.mark import (
    ANCHOR_EXAMPLE,
    INSTRUCTIONS,
    QUERY_SHAPES,
    allowed,
    problems,
)

MARKS_PATH = (
    Path(__file__).resolve().parents[1]
    / "evidence"
    / "the-loop-measured-2026-08-27"
    / "marks.jsonl"
)


def _load_marks() -> list[dict]:
    with MARKS_PATH.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh]


#: The 706 marks a real 2026-08-27 run actually wrote.
REAL_MARKS = _load_marks()

#: One real address per verdict -- the first the 2026-08-27 run recorded for
#: it, in file order. All seven verdicts appear at least once in the 706.
REAL_ADDRESS: dict[str, str] = {}
for _mark in REAL_MARKS:
    REAL_ADDRESS.setdefault(_mark["verdict"], _mark["address"])


#: A source in the shape the brief asks for.
SOURCE = {"cite": "src/mod.py:12", "verbatim": "def thing() -> int:"}

#: A literal, well-formed `claim` for each of the seven, carrying exactly the
#: keys `BRIEF` publishes for that verdict. Hand-copied from
#: `reviewer-brief.md`, not derived from `INSTRUCTIONS`.
CLAIM: dict[str, dict] = {
    "clean": {},
    "query": {
        "shape": "unable-to-determine",
        "attempted": "grepped the module and its callers for a unit",
        "settles": "the caller that supplies the value",
    },
    "drop": {"drop": "the sentence being removed, verbatim"},
    "correct": {"false": "the old, wrong sentence", "true": "the corrected one"},
    "patch": {"from": "the sentence as it stands", "to": "the rewrite"},
    "add": {"missing": "the text that is missing", "anchor": ANCHOR_EXAMPLE},
    "move": {"from": "src/old.py@b1", "to": "src/new.py@b1"},
}

#: A literal, well-formed `change` for each verdict that owes one. `clean`
#: and `query` propose no text, so neither has an entry.
#:
#: !! `move`'s ROW describes `change` as a dict keyed `to` (`change_help`,
#: `desk/mark.py`'s `Row.change_all`), but `problems()` demands an
#: ARRAY of lines from every instruction that owes a `change` before it ever
#: looks at `change_all` -- so a dict is refused before the `to`/`from` check
#: is reached, and a plain array of lines is what actually passes. MEASURED
#: against the shipped gate, 2026-08-28; out of this task's scope (files
#: touched: `claim_keys`, `allowed`, `_claim_problems`). Flagged in
#: `task-1-report.md`, not fixed here.
CHANGE: dict[str, object] = {
    "drop": [],
    "correct": ["# the corrected line"],
    "patch": ["# the reworded line"],
    "add": ["# the new line"],
    "move": ["# the paragraph as it reads at its destination"],
}

#: Verdicts whose payload cites no source: `clean` rules on nothing, `patch`
#: rules on wording alone -- reviewer-brief.md:286.
NO_SOURCE = ("clean", "patch")


def well_formed(verdict: str) -> dict:
    """A literal mark that satisfies `verdict`'s row in the brief.

    The address is a REAL one the 2026-08-27 run recorded for this verdict;
    the reason, claim, change and sources are hand-written from the brief.
    """
    mark: dict = {
        "mark": verdict,
        "address": REAL_ADDRESS[verdict],
        "reason": "written from the brief for the mark-gate suite",
    }
    if CLAIM[verdict]:
        mark["claim"] = dict(CLAIM[verdict])
    if verdict in CHANGE:
        mark["change"] = CHANGE[verdict]
    if verdict not in NO_SOURCE:
        mark["sources"] = [dict(SOURCE)]
    return mark


class TestRealMarksStayInsideTheClosedSet:
    """What the 706 recorded marks actually say, checked against the brief."""

    def test_every_recorded_verdict_is_one_the_brief_publishes(self):
        recorded = {m["verdict"] for m in REAL_MARKS}
        assert recorded <= set(BRIEF)

    def test_all_seven_were_recorded_at_least_once(self):
        """! Confirms `REAL_ADDRESS` covers every verdict `well_formed` needs."""
        recorded = {m["verdict"] for m in REAL_MARKS}
        assert recorded == set(BRIEF)


class TestTheTableIsTheContract:
    """`INSTRUCTIONS` read as INPUT; every expectation below is a hand-checked
    literal, never derived from the row it is checking -- see the module
    docstring.

    !! FOUR TESTS THAT LIVED HERE WERE DELETED 2026-08-28, not adjusted: they
    asserted properties of `payload`, `claim_help`, `claim_any` and `removes`
    -- fields `docs/the-mark.md` deleted by ruling (`decision-log.md Process:
    #37`). The structure they checked no longer exists, so the assertions had
    nothing left to test. The one that guarded a real, twice-shipped defect
    (`patch`'s `payload` prose disagreeing with its `owes_sources` flag) is
    rebuilt in `tests/gates/test_mark_shape.py`, checking the spec's own
    per-instruction table against `INSTRUCTIONS` directly -- stronger than
    this file's row-against-itself check, because the expectation now sits
    where the code cannot move it.
    """

    def test_only_clean_is_not_substantive(self):
        """`clean` is the null mark; every other instruction asks something
        of the apply step."""
        not_substantive = [n for n, s in INSTRUCTIONS.items() if not s.substantive]
        assert not_substantive == ["clean"]


class TestTheQueryShapes:
    """`QUERY_SHAPES` read as INPUT; expectations are literal strings."""

    def test_the_retired_shapes_are_gone(self):
        """`Process: #33` re-keyed the set on WHO RESOLVES a query, retiring
        the WHERE-keyed set these three replaced."""
        for old in ("outside the checkout", "outside the code", "outside my role"):
            assert old not in QUERY_SHAPES

    def test_the_scope_shape_is_outside_my_role(self):
        """The literal is written here, not read from `OUT_OF_ROLE` --
        `allowed()["scope_shape"]` is what a flow reads, and this pins what
        it must equal without going through the same constant twice."""
        assert allowed()["scope_shape"] == "outside-my-role"


class TestWellFormedMarksAtRealAddresses:
    @pytest.mark.parametrize("verdict", sorted(BRIEF))
    def test_a_mark_written_from_the_brief_at_a_real_address_is_accepted(
        self, verdict
    ):
        assert problems("here", well_formed(verdict)) == []


class TestWhatAllowedPublishes:
    def test_the_seven_instructions_match_the_brief(self):
        assert allowed()["instruction"] == sorted(BRIEF)

    def test_the_published_anchor_example_is_itself_backtick_delimited(self):
        """A literal check on the published string, not on `ANCHOR_NAME` --
        the pattern the gate enforces is checked separately, below, against
        the brief's own wording rather than against this constant."""
        assert ANCHOR_EXAMPLE.startswith("`")
        assert ANCHOR_EXAMPLE.endswith("`")
        assert ANCHOR_EXAMPLE.count("`") == 2

    def test_it_names_the_source_keys_including_ran(self):
        keys = allowed()["source_keys"]
        assert keys["required"] == ["cite", "verbatim"]
        assert "ran" in keys["optional"]


class TestTheRulesBite:
    """Each case starts from a mark `well_formed` accepts and breaks one rule."""

    def test_an_unknown_instruction_is_refused(self):
        assert problems("here", {"mark": "stet"})

    def test_a_missing_address_is_refused(self):
        bad = well_formed("correct")
        del bad["address"]
        assert any("address" in p for p in problems("here", bad))

    def test_clean_needs_no_address(self):
        """A role returns `clean` over most of the binder."""
        assert problems("here", {"mark": "clean"}) == []

    def test_an_empty_claim_key_is_not_an_answer(self):
        bad = well_formed("correct")
        bad["claim"]["false"] = "   "
        assert problems("here", bad)

    def test_change_as_a_string_is_refused(self):
        """Measured: a hand-transcribed paragraph lost its comment markers."""
        bad = well_formed("correct")
        bad["change"] = "# one line, as a string"
        assert any("ARRAY" in p for p in problems("here", bad))

    def test_a_drop_may_empty_the_paragraph(self):
        good = well_formed("drop")
        good["change"] = []
        assert problems("here", good) == []

    def test_a_correct_may_not_empty_the_paragraph(self):
        bad = well_formed("correct")
        bad["change"] = []
        assert problems("here", bad)

    def test_a_mark_owing_sources_that_cites_nothing_is_refused(self):
        """! ADDED after a mutation survived: both source cases below pass a
        NON-EMPTY list, so the loop caught them and the guard above it was
        never exercised. A mark with no `sources` at all went through.
        """
        bad = well_formed("correct")
        del bad["sources"]
        assert any("source" in p for p in problems("here", bad))

    def test_an_empty_source_list_is_refused(self):
        bad = well_formed("correct")
        bad["sources"] = []
        assert any("source" in p for p in problems("here", bad))

    def test_a_source_string_is_refused_where_a_pair_is_owed(self):
        bad = well_formed("correct")
        bad["sources"] = ["src/mod.py:12 | def thing()"]
        assert problems("here", bad)

    def test_a_source_missing_its_verbatim_is_refused(self):
        bad = well_formed("correct")
        bad["sources"] = [{"cite": "src/mod.py:12"}]
        assert any("verbatim" in p for p in problems("here", bad))

    def test_a_source_may_carry_ran(self):
        good = well_formed("correct")
        good["sources"] = [dict(SOURCE, ran="uv run pytest -q")]
        assert problems("here", good) == []

    def test_patch_needs_no_source(self):
        """reviewer-brief.md:286 -- the claim is already true; only the
        wording is at issue."""
        good = well_formed("patch")
        assert "sources" not in good
        assert problems("here", good) == []

    def test_an_add_whose_anchor_is_not_named_is_refused(self):
        bad = well_formed("add")
        bad["claim"]["anchor"] = "compute_rates"
        assert any("backticks" in p for p in problems("here", bad))

    def test_add_needs_the_backtick_delimiter_the_brief_publishes(self):
        """reviewer-brief.md:287 -- "the anchor NAMED IN BACKTICKS." Pinned
        against LITERAL backtick and square-bracket forms written here, not
        against `ANCHOR_NAME` -- a mutation moving BOTH the gate's pattern
        and `ANCHOR_EXAMPLE` to another delimiter leaves this red, because
        neither literal in this test moved with them.
        """
        bracketed = well_formed("add")
        bracketed["claim"]["anchor"] = "[compute_rates]"
        assert any("backticks" in p for p in problems("here", bracketed))

        backticked = well_formed("add")
        backticked["claim"]["anchor"] = "`compute_rates`"
        assert problems("here", backticked) == []

    def test_a_query_missing_what_would_settle_it_is_refused(self):
        bad = well_formed("query")
        del bad["claim"]["settles"]
        assert any("settles" in p for p in problems("here", bad))

    def test_a_query_naming_a_shape_outside_the_three_is_refused(self):
        bad = well_formed("query")
        bad["claim"]["shape"] = "i-give-up"
        assert problems("here", bad) != []
