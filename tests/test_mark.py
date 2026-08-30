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
    Mark,
    allowed,
    parse,
    untouched,
)


def problems(where: str, entry: object) -> list[str]:
    """Just the refusals `parse` reports -- the half these cases assert on.

    ! `parse` returns `(Mark | None, problems)` and there is no third outcome,
    so an empty list here is also the statement that a `Mark` was built. The
    two are checked together in `TestTheParseHasNoThirdOutcome` below rather
    than at every call site.
    """
    return parse(where, entry)[1]


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

#: A literal, well-formed `change` for each instruction that owes one. `clean`
#: and `query` propose no text, so neither has an entry.
#:
#: !! RAW TEXT, NOT A LINE ARRAY -- `reviewer-brief.md`'s own wording, *"the
#: updated paragraph, as RAW TEXT -- not lines, not sentences"*, which is what
#: `docs/the-mark.md` rules and what the gate demanded the opposite of until
#: 2026-08-29 (`TODO/change-is-raw-text-not-lines.md`).
#:
#: ! `drop`'s empty string IS the edit, on the one row `may_empty` is True for.
CHANGE: dict[str, object] = {
    "drop": "",
    "correct": "# the corrected line",
    "patch": "# the reworded line",
    "add": "# the new line",
    "move": "# the paragraph as it reads at its destination",
}

#: Verdicts whose payload cites no source: `clean` rules on nothing, `patch`
#: rules on wording alone -- reviewer-brief.md:286.
NO_SOURCE = ("clean", "patch")


def well_formed(instruction: str) -> dict:
    """A literal entry that satisfies `instruction`'s row in the brief.

    The address is a REAL one the 2026-08-27 run recorded for this
    instruction; the reason, claim, change and sources are hand-written from
    the brief.

    ! THE RULING KEY IS `instruction`, which is what `reviewer-brief.md`
    publishes. The code read it as `mark` until 2026-08-29 and the brief's own
    example was silently skipped as unruled --
    `tests/test_brief_worked_example.py`.
    """
    entry: dict = {
        "instruction": instruction,
        "address": REAL_ADDRESS[instruction],
        "reason": "written from the brief for the mark-gate suite",
    }
    if CLAIM[instruction]:
        entry["claim"] = dict(CLAIM[instruction])
    if instruction in CHANGE:
        entry["change"] = CHANGE[instruction]
    if instruction not in NO_SOURCE:
        entry["sources"] = [dict(SOURCE)]
    return entry


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
    @pytest.mark.parametrize("instruction", sorted(BRIEF))
    def test_a_mark_written_from_the_brief_at_a_real_address_is_accepted(
        self, instruction
    ):
        assert problems("here", well_formed(instruction)) == []


class TestTheParseHasNoThirdOutcome:
    """!! ONE FUNCTION, TWO ANSWERS, AND NEVER BOTH OR NEITHER. `problems(where,
    mark: dict)` returned messages and left the dict for the caller to use
    anyway, so a half-valid mark reached every consumer -- which is what
    `desk/collator.py` then re-derived by key at ten sites.
    """

    @pytest.mark.parametrize("instruction", sorted(BRIEF))
    def test_an_accepted_entry_yields_a_mark_and_no_problems(self, instruction):
        mark, why = parse("here", well_formed(instruction))
        assert why == []
        assert mark is not None
        assert mark.instruction == instruction

    @pytest.mark.parametrize("instruction", sorted(BRIEF))
    def test_a_refused_entry_yields_problems_and_NO_mark(self, instruction):
        broken = well_formed(instruction)
        del broken["instruction"]
        mark, why = parse("here", broken)
        assert mark is None
        assert why != []

    def test_the_mark_carries_the_claim_the_entry_wrote(self):
        mark, _ = parse("here", well_formed("correct"))
        assert mark is not None
        assert mark.claim == CLAIM["correct"]
        assert mark.change == CHANGE["correct"]

    def test_the_claim_is_COPIED_so_the_frozen_mark_cannot_be_mutated_through_it(
        self,
    ):
        entry = well_formed("correct")
        mark, _ = parse("here", entry)
        assert mark is not None
        entry["claim"]["false"] = "changed after the parse"
        assert mark.claim["false"] == CLAIM["correct"]["false"]

    def test_an_instruction_typed_as_a_string_resolves_a_row_with_no_cast(self):
        """!! WHAT TASK 3 BUYS. `INSTRUCTIONS` is keyed on `Instruction`, and
        every consumer handed it a `str` -- ten `str`-into-`dict[Instruction,
        Row]` errors in `desk/collator.py` alone. A parsed mark's
        `instruction` IS the member."""
        mark, _ = parse("here", well_formed("correct"))
        assert mark is not None
        assert INSTRUCTIONS[mark.instruction].quotes_original == "false"


class TestUntouchedIsNotTheSameAsUnruled:
    """!! THE MEASURED DEFECT. `flows/distribute.py` read `mark.get("mark") is None`
    and skipped, which said the same thing about a slot nobody wrote in and a
    mark a role HAD filled in that named no instruction -- so the second was
    dropped before any check saw it and recounted as a coverage gap."""

    def test_a_freshly_seeded_slot_is_untouched(self):
        assert untouched(
            {"address": "m.py@b1", "anchor": "", "raw_text": "", "instruction": None}
        )

    def test_a_filled_slot_naming_no_instruction_is_NOT_untouched(self):
        entry = well_formed("correct")
        entry["instruction"] = None
        assert not untouched(entry)

    def test_a_slot_with_no_instruction_KEY_AT_ALL_is_NOT_untouched(self):
        """The brief's own example arrived this way -- keyed `instruction`
        while the code read `mark`, so the key it looked for was absent."""
        assert not untouched({"address": "m.py@b1", "anchor": "", "raw_text": ""})

    def test_a_ruled_slot_is_not_untouched(self):
        assert not untouched(well_formed("clean"))

    def test_what_is_not_untouched_is_refused_by_NAME(self):
        entry = well_formed("correct")
        entry["instruction"] = None
        mark, why = parse("here", entry)
        assert mark is None
        assert any("instruction" in message for message in why)


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
        assert problems("here", {"instruction": "stet"})

    def test_a_missing_address_is_refused(self):
        bad = well_formed("correct")
        del bad["address"]
        assert any("address" in p for p in problems("here", bad))

    def test_clean_needs_no_address(self):
        """A role returns `clean` over most of the binder."""
        assert problems("here", {"instruction": "clean"}) == []

    def test_an_empty_claim_key_is_not_an_answer(self):
        bad = well_formed("correct")
        bad["claim"]["false"] = "   "
        assert problems("here", bad)

    def test_change_as_a_LINE_ARRAY_is_refused_BY_NAME(self):
        """!! THE FORM THIS GATE DEMANDED UNTIL 2026-08-29, while the brief
        mandated raw text -- `TODO/change-is-raw-text-not-lines.md`. A role
        written against the retired rule is told so, rather than accepted for
        a release: the message names RAW TEXT and what arrived instead."""
        bad = well_formed("correct")
        bad["change"] = ["# one line, in the retired array form"]
        assert any("RAW TEXT" in p for p in problems("here", bad))

    def test_change_as_raw_text_is_what_is_ACCEPTED(self):
        """reviewer-brief.md: *"the updated paragraph, as RAW TEXT -- not
        lines, not sentences."*"""
        good = well_formed("correct")
        good["change"] = "# the corrected line\n# and its second line"
        assert problems("here", good) == []

    def test_a_drop_may_empty_the_paragraph(self):
        good = well_formed("drop")
        good["change"] = ""
        assert problems("here", good) == []

    def test_a_correct_may_not_empty_the_paragraph(self):
        bad = well_formed("correct")
        bad["change"] = ""
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


def test_the_mark_carries_the_raw_text_the_row_seeded():
    """`raw_text` is seeded onto every slot and must survive the round trip --
    `decision-log.md Process: #54` makes "did this parse back correctly" the
    mark's own question, and a field that never comes back has no round trip."""
    entry = {
        "address": "m.py@b1",
        "anchor": "def f(x):",
        "raw_text": "# the paragraph as it stands\n",
        "instruction": "clean",
    }
    mark, why = parse("m.py@b1", entry)
    assert why == []
    assert mark is not None
    assert mark.raw_text == "# the paragraph as it stands\n"


def test_a_mark_that_lost_its_raw_text_still_parses():
    """!! AN ABSENT `raw_text` IS NOT A SHAPE PROBLEM. It is seeded, so its
    absence is DRIFT -- a copy that did not come back with what it was handed
    -- and `decision-log.md` D10 of the SP-1 spec rules drift REPORTED, by the
    collator, never refused at the boundary. Refusing an absent field here
    while a CHANGED field is only reported would be two treatments of one
    problem."""
    mark, why = parse("m.py@b1", {"address": "m.py@b1", "instruction": "clean"})
    assert why == []
    assert mark is not None
    assert mark.raw_text == ""


def test_seed_builds_the_slot_from_the_marks_own_names():
    row = Mark.seed("m.py@b1", "def f(x):", "# as it stands\n")
    assert row == {
        "address": "m.py@b1",
        "anchor": "def f(x):",
        "raw_text": "# as it stands\n",
        "instruction": None,
    }


def test_seed_refuses_a_name_the_mark_does_not_declare(monkeypatch):
    """!! THE POINT OF THE FUNCTION, AND THE ONLY WAY IT CAN FAIL. `P35` asks
    that a renamed field break AT CONSTRUCTION rather than leave another
    module writing the old key -- so `SEEDED` is checked against the
    dataclass's own fields every call, and this proves that check fires."""
    monkeypatch.setattr(Mark, "SEEDED", ("address", "anchor", "raw_txt"))
    with pytest.raises(AttributeError) as caught:
        Mark.seed("m.py@b1", "def f(x):", "# as it stands\n")
    assert "raw_txt" in str(caught.value)


def test_as_entry_round_trips_through_parse():
    """A mark written back onto a sheet parses as the mark it came from --
    which is what lets the copy chief's `edit_copy` be an ordinary one."""
    entry = {
        "address": "m.py@b1",
        "anchor": "def f(x):",
        "raw_text": "# as it stands\n",
        "instruction": "correct",
        "claim": {"false": "as it stands", "true": "as it should read"},
        "reason": "the paragraph names a parameter the signature dropped",
        "sources": [{"cite": "m.py:1", "verbatim": "def f(x):"}],
        "change": "# as it should read\n",
    }
    mark, why = parse("m.py@b1", entry)
    assert why == []
    assert mark is not None
    again, why_again = parse("m.py@b1", mark.as_entry())
    assert why_again == []
    assert again == mark


def test_a_move_onto_its_own_address_is_refused_by_name():
    """MEASURED 2026-08-30: this parsed with no problems reported, `_touches`
    deduped its two ends to one address, `reconcile` settled it, and the
    docket carried a single alteration deleting the paragraph --
    `('m.py', 'b1', None)` -- with no matching write."""
    entry = {
        "address": "m.py@b1",
        "anchor": "def f(x):",
        "raw_text": "# a paragraph\n",
        "instruction": "move",
        "claim": {"from": "a paragraph", "to": "m.py@b1"},
        "reason": "it reads better beside the function it describes",
        "sources": [{"cite": "m.py:1", "verbatim": "def f(x):"}],
        "change": "# a paragraph\n",
    }
    mark, why = parse("m.py@b1", entry)
    assert mark is None
    assert len(why) == 1
    assert "`claim.to` is this mark's own `address`" in why[0]


def test_a_move_to_a_different_address_still_parses():
    """The guard must not refuse an ordinary move -- the one that names a real
    second place."""
    entry = {
        "address": "m.py@b1",
        "anchor": "def f(x):",
        "raw_text": "# a paragraph\n",
        "instruction": "move",
        "claim": {"from": "a paragraph", "to": "m.py@b8"},
        "reason": "it reads better beside the function it describes",
        "sources": [{"cite": "m.py:1", "verbatim": "def f(x):"}],
        "change": "# a paragraph\n",
    }
    mark, why = parse("m.py@b1", entry)
    assert why == []
    assert mark is not None
