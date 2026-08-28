"""The mark's shape, and the rules `desk/mark.py` settles without the binder.

! Every case here is built from `INSTRUCTIONS` rather than from a literal, so a
row change moves the test with it. A literal appears only where MALFORMED is the
input -- which is the one thing the table cannot supply.
"""

import pytest

from comment_review.desk.mark import (
    ANCHOR_EXAMPLE,
    ANCHOR_NAME,
    INSTRUCTIONS,
    OUT_OF_ROLE,
    QUERY_SHAPES,
    allowed,
    claim_keys,
    problems,
)

#: A source in the shape the brief asks for. `ran` is optional.
SOURCE = {"cite": "src/mod.py:12", "verbatim": "def thing() -> int:"}


def a_mark(instruction: str, **over) -> dict:
    """The smallest mark that SATISFIES its row -- built from the row itself."""
    spec = INSTRUCTIONS[instruction]
    mark: dict = {"mark": instruction}
    if spec.owes_address:
        mark["address"] = "pkg:mod.py@b3"
    if spec.owes_reason:
        mark["reason"] = "the enclosing function was renamed in 4a1c2e0"
    if spec.owes_sources:
        mark["sources"] = [dict(SOURCE)]
    if spec.owes_change:
        mark["change"] = ["# the replacement line"]
    claim: dict = {}
    for key in spec.claim_all:
        claim[key] = ANCHOR_EXAMPLE if key == "missing" else "a sentence"
    if spec.claim_any:
        claim[spec.claim_any[0]] = "yes"
    if spec.needs_attempted:
        claim["attempted"] = "grepped the tree for the symbol"
    if spec.needs_settles:
        claim["settles"] = "the author saying which behaviour was intended"
    if claim:
        mark["claim"] = claim
    return mark | over


class TestTheTableIsTheContract:
    def test_the_seven_are_closed(self):
        assert sorted(INSTRUCTIONS) == [
            "add", "clean", "correct", "drop", "move", "patch", "query"
        ]

    @pytest.mark.parametrize("name", sorted(INSTRUCTIONS))
    def test_every_instruction_says_what_its_claim_carries(self, name):
        """A row with no `payload` publishes nothing for a role to copy."""
        assert INSTRUCTIONS[name].payload.strip()

    @pytest.mark.parametrize("name", sorted(INSTRUCTIONS))
    def test_a_row_demanding_keys_says_how_to_meet_them(self, name):
        spec = INSTRUCTIONS[name]
        if spec.claim_all or spec.claim_any:
            assert spec.claim_help.strip(), f"{name} demands keys and explains none"

    def test_only_clean_is_not_substantive(self):
        not_sub = [n for n, s in INSTRUCTIONS.items() if not s.substantive]
        assert not_sub == ["clean"]

    def test_only_query_may_declare_scope(self):
        scoped = [n for n, s in INSTRUCTIONS.items() if s.can_declare_scope]
        assert scoped == ["query"]

    def test_removes_and_rules_on_text_never_coincide(self):
        """The one contradiction the set expresses is BETWEEN marks, not within.

        ! `move` is deliberately neither: relocation and a truth fix compose.
        """
        for name, spec in INSTRUCTIONS.items():
            assert not (spec.removes and spec.rules_on_text), name
        assert not INSTRUCTIONS["move"].removes
        assert not INSTRUCTIONS["move"].rules_on_text

    def test_patch_owes_no_sources_because_its_payload_says_so(self):
        """The gate and the published sentence read off ONE row.

        Measured 2026-08-22 and twice after: the payload shipped saying a patch
        needs no source while the flag said it did, so the join refused every
        `patch` a compliant reviewer filed.
        """
        spec = INSTRUCTIONS["patch"]
        assert "needs no source" in spec.payload
        assert not spec.owes_sources


class TestTheQueryShapes:
    def test_the_three_are_closed_and_query_demands_one(self):
        assert INSTRUCTIONS["query"].claim_any == QUERY_SHAPES
        assert len(QUERY_SHAPES) == 3

    def test_the_scope_shape_is_named_so_a_flow_need_not_read_prose(self):
        assert allowed()["scope_shape"] == OUT_OF_ROLE
        assert OUT_OF_ROLE in QUERY_SHAPES

    def test_the_retired_set_is_gone(self):
        """`Process: #33` re-keyed these on WHO RESOLVES IT."""
        for old in ("outside the checkout", "outside the code", "outside my role"):
            assert old not in QUERY_SHAPES

    def test_a_query_naming_no_shape_is_refused(self):
        bad = a_mark("query")
        bad["claim"] = {"attempted": "looked", "settles": "the author"}
        assert any("shape" in p for p in problems("here", bad))


class TestWhatAllowedPublishes:
    def test_it_is_generated_from_the_rows(self):
        got = allowed()
        assert got["instruction"] == sorted(INSTRUCTIONS)
        for name, spec in INSTRUCTIONS.items():
            every, any_of = claim_keys(spec)
            assert got["claim"][name] == {"all": every, "any": any_of}

    def test_the_anchor_example_satisfies_the_anchor_pattern(self):
        """Published form and enforced pattern are ONE string, not two that agree."""
        assert ANCHOR_NAME.search(ANCHOR_EXAMPLE)
        assert not ANCHOR_NAME.search("compute_rates")

    def test_it_names_the_source_keys_including_ran(self):
        keys = allowed()["source_keys"]
        assert keys["required"] == ["cite", "verbatim"]
        assert "ran" in keys["optional"]


class TestAWellFormedMarkPasses:
    @pytest.mark.parametrize("name", sorted(INSTRUCTIONS))
    def test_the_row_can_build_a_mark_its_own_rules_accept(self, name):
        assert problems("here", a_mark(name)) == []


class TestTheRulesBite:
    """Each case is the SAME mark with one rule broken."""

    def test_an_unknown_instruction_is_refused(self):
        assert problems("here", {"mark": "stet"})

    def test_a_missing_address_is_refused(self):
        bad = a_mark("correct")
        del bad["address"]
        assert any("address" in p for p in problems("here", bad))

    def test_clean_needs_no_address(self):
        """A role returns `clean` over most of the binder."""
        assert problems("here", {"mark": "clean"}) == []

    def test_an_empty_claim_key_is_not_an_answer(self):
        bad = a_mark("correct")
        bad["claim"]["false"] = "   "
        assert problems("here", bad)

    def test_change_as_a_string_is_refused(self):
        """Measured: a hand-transcribed paragraph lost its comment markers."""
        bad = a_mark("correct", change="# one line, as a string")
        assert any("ARRAY" in p for p in problems("here", bad))

    def test_a_drop_may_empty_the_paragraph(self):
        assert problems("here", a_mark("drop", change=[])) == []

    def test_a_correct_may_not(self):
        assert problems("here", a_mark("correct", change=[]))

    def test_a_mark_owing_sources_that_cites_nothing_is_refused(self):
        """! ADDED after a mutation survived: both source cases below pass a
        NON-EMPTY list, so the loop caught them and the guard above it was never
        exercised. A mark with no `sources` at all went through.
        """
        bare = a_mark("correct")
        del bare["sources"]
        assert any("source" in p for p in problems("here", bare))

    def test_an_empty_source_list_is_refused(self):
        empty = a_mark("correct", sources=[])
        assert any("source" in p for p in problems("here", empty))

    def test_a_source_string_is_refused_where_a_pair_is_owed(self):
        bad = a_mark("correct", sources=["src/mod.py:12 | def thing()"])
        assert problems("here", bad)

    def test_a_source_missing_its_verbatim_is_refused(self):
        bad = a_mark("correct", sources=[{"cite": "src/mod.py:12"}])
        assert any("verbatim" in p for p in problems("here", bad))

    def test_a_source_may_carry_ran(self):
        good = a_mark("correct", sources=[SOURCE | {"ran": "uv run pytest -q"}])
        assert problems("here", good) == []

    def test_an_add_whose_anchor_is_not_named_is_refused(self):
        bad = a_mark("add")
        bad["claim"]["missing"] = "the anchor should be documented"
        assert any("backticks" in p for p in problems("here", bad))

    def test_a_query_missing_what_would_settle_it_is_refused(self):
        bad = a_mark("query")
        del bad["claim"]["settles"]
        assert any("settles" in p for p in problems("here", bad))
