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

from comment_review.desk.marks.rules import (
    ANCHOR_EXAMPLE,
    allowed,
    derived_change,
    validate,
)
from comment_review.desk.marks.table import INSTRUCTIONS
from comment_review.desk.proof.mark import (
    QUERY_SHAPES,
    Instruction,
    Mark,
    read_mark,
    untouched,
    without_location,
)
from comment_review.desk.proof.sheet import Sheet


def problems(where: str, entry: object) -> list[str]:
    """Just the refusals `parse` reports -- the half these cases assert on.

    ! `parse` returns `(Mark | None, problems)` and there is no third outcome,
    so an empty list here is also the statement that a `Mark` was built. The
    two are checked together in `TestTheParseHasNoThirdOutcome` below rather
    than at every call site.
    """
    return read_mark(where, entry, validate)[1]


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
        mark, why = read_mark("here", well_formed(instruction), validate)
        assert why == []
        assert mark is not None
        assert mark.instruction == instruction

    @pytest.mark.parametrize("instruction", sorted(BRIEF))
    def test_a_refused_entry_yields_problems_and_NO_mark(self, instruction):
        broken = well_formed(instruction)
        del broken["instruction"]
        mark, why = read_mark("here", broken, validate)
        assert mark is None
        assert why != []

    def test_the_mark_carries_the_claim_the_entry_wrote(self):
        mark, _ = read_mark("here", well_formed("correct"), validate)
        assert mark is not None
        assert mark.claim == CLAIM["correct"]
        assert mark.change == CHANGE["correct"]

    def test_the_claim_is_COPIED_so_the_frozen_mark_cannot_be_mutated_through_it(
        self,
    ):
        entry = well_formed("correct")
        mark, _ = read_mark("here", entry, validate)
        assert mark is not None
        entry["claim"]["false"] = "changed after the parse"
        assert mark.claim["false"] == CLAIM["correct"]["false"]

    def test_an_instruction_typed_as_a_string_resolves_a_row_with_no_cast(self):
        """!! WHAT TASK 3 BUYS. `INSTRUCTIONS` is keyed on `Instruction`, and
        every consumer handed it a `str` -- ten `str`-into-`dict[Instruction,
        Row]` errors in `desk/collator.py` alone. A parsed mark's
        `instruction` IS the member."""
        mark, _ = read_mark("here", well_formed("correct"), validate)
        assert mark is not None
        assert INSTRUCTIONS[mark.instruction].quotes_original == "false"


def test_the_structural_read_admits_what_only_the_rules_refuse():
    """`decision-log.md Process: #203`. `Mark.deserialize` reads the structure
    and asks nothing of the row; a `correct` with no `reason` is a mark of a
    named instruction, and it is `validate` that refuses it -- and a sheet
    handed `validate` refuses it with the validator's own wording."""
    entry = well_formed("correct")
    del entry["reason"]
    mark, why = Mark.deserialize("here", entry)
    assert why == [] and mark is not None
    assert validate("here", mark) == ["here: correct needs a `reason`"]
    sheet, why = Sheet.deserialize(
        "s", {"path": "m.py", "sha": "a", "marks": [entry]}, validate
    )
    assert why == [] and sheet is not None and sheet.marks == ()
    assert sheet.refused[0].reasons == ("correct needs a `reason`",)


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
        mark, why = read_mark("here", entry, validate)
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
        a release: the message names RAW TEXT as what is owed."""
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

    def test_a_WHITESPACE_ONLY_change_is_not_an_answer(self):
        """!! THE SAME GAP `filled` CLOSES FOR A `claim` KEY -- see
        `test_an_empty_claim_key_is_not_an_answer`, above. `may_empty` decides
        whether NO content is acceptable; it says nothing about whether
        whitespace counts as content, and a bare `not change` let it through
        for a row that does not allow an empty change at all."""
        bad = well_formed("correct")
        bad["change"] = "   "
        assert any("change" in p for p in problems("here", bad))

    def test_a_change_carrying_the_anchors_own_code_line_is_refused(self):
        """`collator-defects` T35: a change is the paragraph alone, so one
        holding the line of code its place sits on is refused, and the same
        mark without that line is not."""
        anchor = "    UNABLE_TO_DETERMINE = auto()"
        bad = well_formed("correct")
        bad["anchor"] = anchor
        bad["change"] = f"    #: the corrected comment\n{anchor}"
        assert any("anchor's own line" in p for p in problems("here", bad))

        good = well_formed("correct")
        good["anchor"] = anchor
        good["change"] = "    #: the corrected comment"
        assert problems("here", good) == []

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
    mark, why = read_mark("m.py@b1", entry, validate)
    assert why == []
    assert mark is not None
    assert mark.raw_text == "# the paragraph as it stands\n"


def test_a_mark_that_lost_its_raw_text_still_parses():
    """An absent `raw_text` is not a shape problem. It is seeded, and the base
    a mark is measured against is never this field, so the boundary has
    nothing to refuse (`decision-log.md Process: #185`)."""
    mark, why = read_mark(
        "m.py@b1", {"address": "m.py@b1", "instruction": "clean"}, validate
    )
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


def test_serialize_round_trips_through_deserialize():
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
    mark, why = read_mark("m.py@b1", entry, validate)
    assert why == []
    assert mark is not None
    again, why_again = read_mark("m.py@b1", mark.serialize(), validate)
    assert why_again == []
    assert again == mark


def test_a_move_onto_its_own_address_is_refused_by_name():
    """MEASURED 2026-08-30: this parsed with no problems reported, `_touches`
    deduped its two ends to one address, the fold settled it, and the
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
    mark, why = read_mark("m.py@b1", entry, validate)
    assert mark is None
    assert len(why) == 1
    assert "`claim.to` is this mark's own `address`" in why[0]


@pytest.mark.parametrize("spelled", ["M.py@b1", "m.py@b1 ", " m.py@B1"])
def test_a_move_onto_its_own_address_spelled_otherwise_is_refused(spelled):
    """A case slip names the same page on a file system that ignores case, and
    such a move reached the docket as two schedules for one file: the delete
    at the origin landed and the restoring write was lost."""
    mark, why = read_mark("m.py@b1", _a_move_to(spelled), validate)
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
    mark, why = read_mark("m.py@b1", entry, validate)
    assert why == []
    assert mark is not None


def _a_move_to(destination: str) -> dict:
    """A well-formed `move` from `m.py@b1` to `destination`."""
    return {
        "address": "m.py@b1",
        "anchor": "def f(x):",
        "raw_text": "# a paragraph\n",
        "instruction": "move",
        "claim": {"from": "a paragraph", "to": destination},
        "reason": "it reads better beside the function it describes",
        "sources": [{"cite": "m.py:1", "verbatim": "def f(x):"}],
        "change": "# a paragraph\n",
    }


def test_a_move_out_of_the_code_is_refused_and_routed_to_a_query():
    """`move-is-a-composite-mark` T22, provisional by `decision-log.md Process:
    #173`. The fold and the write end carry no destination that is not a
    `path@cue` place, and the 2026-09-14 self-run filed 19 that `mark` and
    `check` accepted and `collate` refused. Refused here, the role is told to
    file a human-review query naming where the paragraph belongs."""
    for destination in ("docs/history.md", "src/pkg/mod.py:1"):
        mark, why = read_mark("m.py@b1", _a_move_to(destination), validate)
        assert mark is None, destination
        assert len(why) == 1, why
        assert repr(destination) in why[0]
        assert "human-review-necessary" in why[0]
        assert "#173" in why[0]


def test_a_move_to_a_bare_cue_is_refused():
    """A cue with no path names a place on no page -- the self-run's four
    same-file destinations. The full address is what the addresser prints."""
    mark, why = read_mark("m.py@b1", _a_move_to("b8"), validate)
    assert mark is None
    assert "`path@cue`" in why[0], why


def test_a_substantive_mark_whose_address_names_no_page_is_refused():
    """`mark-defects` T1. `filled()` asked only for a non-blank string, so a
    bare cue -- the form measured at 62 of 78 marks on 2026-08-27 -- parsed,
    and `cue_of("b1")` answers `Address('', '')`."""
    mark, why = read_mark("b1", {**_a_move_to("m.py@b8"), "address": "b1"}, validate)
    assert mark is None
    assert any("full `path@cue` address" in one for one in why), why


class TestAStoredReasonDoesNotRepeatItsLocator:
    """A container that carries the place must not carry it twice.

    !! MEASURED 2026-09-01 ON EVERY LINE OF THE REPORT: `block-context
    m.py@b1: m.py@b1: correct needs a reason`. Fifteen message sites in
    `desk/marks/rules.py` open `f"{where}: "` -- right for a caller holding nothing
    else to say which mark it is -- and the two callers that record the place as
    a FIELD printed both. `collate-command-defects` T3.

    !! THIS IS THE GATE ON `without_location`, AND IT ASKS THE QUESTION THAT
    MATTERS RATHER THAN THE FIX. Either half can rot in silence: a sixteenth
    message site spelling the prefix by hand, or the un-prefixer drifting from
    the format it undoes. Neither shows up as a broken build -- both show up as
    a doubled address in a report nothing asserts on.
    """

    def test_a_refused_entrys_reasons_do_not_open_with_its_own_where(self):
        """Over a REAL sheet parse, so it is the stored value being asked."""
        sheet, why = Sheet.deserialize(
            "s",
            {
                "path": "m.py",
                "sha": "a",
                "marks": [
                    {"address": "m.py@b1", "instruction": "correct", "claim": {}},
                    "not an object",
                ],
            },
            validate,
        )
        assert why == []
        assert sheet is not None
        assert sheet.refused, "the fixture must actually be refused"
        for one in sheet.refused:
            for reason in one.reasons:
                assert not reason.startswith(f"{one.where}:"), reason
                assert not reason.startswith(f"{one.address}:"), reason

    def test_it_leaves_a_message_that_does_not_carry_the_prefix(self):
        """! IT REMOVES WHAT WAS ADDED, so anything else is returned whole --
        which is what keeps it from eating a message that happens to begin with
        a colon-bearing word."""
        assert without_location("m.py@b1", "m.py@b1: needs a reason") == (
            "needs a reason"
        )
        assert without_location("m.py@b1", "needs a reason") == "needs a reason"
        assert without_location("", "m.py@b1: needs a reason") == (
            "m.py@b1: needs a reason"
        )


class TestTheChangeDerivedFromAClaim:
    """`change` built from the paragraph and the claim, so a role never types it.

    ! EXPECTATIONS ARE HAND-WRITTEN paragraphs. The rows are read only to
    name which instruction is under test.

    !! THE QUOTED CLAUSE IS ONE STATEMENT. Roy, 2026-09-07: *"a false clause is
    one statement not multiple paragraphs."* A clause the paragraph holds
    twice names two statements, and one it holds nowhere names none; both
    are refused rather than guessed at.
    """

    BASE = "# one\n# two\n# three\n"

    def test_a_correct_substitutes_the_false_clause_with_the_true_one(self):
        change, why = derived_change(
            Instruction.CORRECT, {"false": "two", "true": "2"}, self.BASE
        )
        assert why == []
        assert change == "# one\n# 2\n# three\n"

    def test_a_patch_substitutes_from_with_to(self):
        change, why = derived_change(
            Instruction.PATCH, {"from": "# three", "to": "# 3"}, self.BASE
        )
        assert why == []
        assert change == "# one\n# two\n# 3\n"

    def test_a_clause_may_span_two_lines(self):
        change, why = derived_change(
            Instruction.CORRECT,
            {"false": "two\n# three", "true": "two and three"},
            self.BASE,
        )
        assert why == []
        assert change == "# one\n# two and three\n"

    def test_a_drop_removes_the_sentence(self):
        change, why = derived_change(
            Instruction.DROP, {"drop": " Narrow it later."}, "# Kept. Narrow it later."
        )
        assert why == []
        assert change == "# Kept."

    def test_a_drop_of_the_whole_paragraph_is_the_empty_string(self):
        change, why = derived_change(Instruction.DROP, {"drop": self.BASE}, self.BASE)
        assert why == []
        assert change == ""

    def test_a_drop_across_a_line_break_is_rewrapped_to_the_paragraphs_width(self):
        """`mark-defects` T25. Dropping a clause that spans a line break joins
        the text either side onto one line, and on the 2026-09-14 self-run
        eleven changes ran past 88 columns that way, up to 126. The joined line
        is rewrapped to the paragraph's own widest -- here 67 -- under its own
        indent and marker."""
        base = (
            "    # The first sentence stays where it is. The second one goes\n"
            "    # away entirely. The third sentence is long enough to overflow.\n"
        )
        change, why = derived_change(
            Instruction.DROP,
            {"drop": " The second one goes\n    # away entirely."},
            base,
        )
        assert why == []
        assert change == (
            "    # The first sentence stays where it is. The third sentence is\n"
            "    # long enough to overflow.\n"
        )

    @pytest.mark.parametrize(
        "instruction",
        [Instruction.CLEAN, Instruction.QUERY, Instruction.ADD, Instruction.MOVE],
    )
    def test_a_row_that_quotes_nothing_derives_nothing_and_reports_nothing(
        self, instruction
    ):
        assert derived_change(instruction, {"to": "m.py@b8"}, self.BASE) == (None, [])

    def test_a_clause_not_in_the_paragraph_is_refused(self):
        change, why = derived_change(
            Instruction.CORRECT, {"false": "four", "true": "4"}, self.BASE
        )
        assert change is None
        assert len(why) == 1 and "`claim.false`" in why[0] and "not in" in why[0]

    def test_a_clause_the_paragraph_holds_twice_is_refused(self):
        change, why = derived_change(
            Instruction.CORRECT, {"false": "# t", "true": "# T"}, self.BASE
        )
        assert change is None
        assert len(why) == 1 and "`claim.false`" in why[0] and "2 times" in why[0]

    def test_a_missing_counterpart_is_refused(self):
        change, why = derived_change(Instruction.CORRECT, {"false": "two"}, self.BASE)
        assert change is None
        assert len(why) == 1 and "`claim.true`" in why[0]
