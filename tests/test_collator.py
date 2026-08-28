"""`desk/collator.py`: source-verification -- T3.1, T3.2, T3.3, and T3.4.

! INPUTS FROM REALITY, `decision-log.md Vocabulary: #23`. Every mark below is
built from a real binder over this repo's own `src/comment_review/desk`, and
every `source` cites a real line of a real file in this checkout -- never a
fixture written to agree with the module under test.

!! T3.4 -- EVERY CHECK IS PROVEN ABLE TO FIRE, not only to pass.
`docs/gates.md`: not "does it pass", but "could it fail". Each
`TestEachCheckCanFire` case starts from a mark the module accepts and mutates
exactly one thing, then asserts the check refuses it and names what broke.
"""

from conftest import ROOT
from helpers import binder_of

from comment_review.binder.binder import rows_of
from comment_review.desk.collator import (
    address_problems,
    claim_verbatim_problems,
    known_addresses,
    source_problems,
    source_verification,
    verify_report,
)
from comment_review.flows.marks import seed

DESK = ROOT / "src" / "comment_review" / "desk"

#: A real binder over `desk/` -- the same fixture-free input
#: `tests/test_marks_flow.py` already builds this way.
BINDER = binder_of(DESK, 0)
ROWS = rows_of(BINDER)
#: `mark.py`'s own `@a0` -- narrowed by suffix, since `desk/` holds several
#: files that each carry their own `@a0`.
ROW = next(r for r in ROWS if r["address"].endswith("mark.py@a0"))
KNOWN = known_addresses(BINDER)

#: A real line of a real file this checkout carries.
CITED_FILE = "src/comment_review/machine/exceptions.py"
CITED_LINE = 57
CITED_TEXT = (
    (ROOT / CITED_FILE).read_text(encoding="utf-8").splitlines()[CITED_LINE - 1]
)


def _well_formed() -> dict:
    """A `correct` mark, as a role would hand back the row `seed()` gave it."""
    false = ROW["raw_text"].splitlines()[0]
    return {
        "address": ROW["address"],
        "anchor": ROW["anchor"],
        "raw_text": ROW["raw_text"],
        "mark": "correct",
        "claim": {"false": false, "true": "the corrected sentence"},
        "reason": "written for the collator test suite",
        "sources": [
            {"cite": f"{CITED_FILE}:{CITED_LINE}", "verbatim": CITED_TEXT}
        ],
        "change": ["# corrected"],
    }


def test_known_addresses_carries_the_real_row():
    assert ROW["address"] in KNOWN


class TestAddressProblems:
    """T3.1 -- the address resolves to a place the binder carries."""

    def test_a_real_address_resolves(self):
        assert address_problems("here", _well_formed(), KNOWN) == []

    def test_clean_needs_no_address(self):
        """A role returns `clean` over most of the binder -- no address at
        all, which is `desk.mark.problems`'s question, not this one's."""
        assert address_problems("here", {"mark": "clean"}, KNOWN) == []


class TestClaimVerbatimProblems:
    """T3.3 -- the sentence the claim rules on is really in the paragraph."""

    def test_the_false_clause_is_really_in_the_paragraph(self):
        assert claim_verbatim_problems("here", _well_formed()) == []

    def test_add_and_query_quote_nothing(self):
        """`add`'s `missing` and `query`'s `shape` are not checked this way --
        `Instruction.quotes_original` is empty for both."""
        add = {"mark": "add", "claim": {"missing": "x", "anchor": "`f`"}}
        query = {"mark": "query", "claim": {"shape": "outside-my-role"}}
        assert claim_verbatim_problems("here", add) == []
        assert claim_verbatim_problems("here", query) == []

    def test_a_missing_claim_key_is_not_this_checks_question(self):
        """`desk.mark.problems` already refuses a `correct` with no `false`;
        source-verification has nothing to compare and says nothing."""
        bad = _well_formed()
        del bad["claim"]["false"]
        assert claim_verbatim_problems("here", bad) == []


class TestSourceProblems:
    """T3.2 -- every `source` resolves, `verbatim` within reach of the cite."""

    def test_a_real_citation_resolves(self):
        cache = {}
        assert source_problems("here", _well_formed(), ROOT, cache) == []

    def test_a_bare_string_source_is_refused_not_dropped(self):
        """`record-and-verdicts-disagree` T3: the retired reader filtered
        `sources` to dicts before its check ran, so a bare string vanished.
        This loop walks `sources` as handed."""
        bad = _well_formed()
        bad["sources"] = ["src/mod.py:12 | def thing()"]
        problems = source_problems("here", bad, ROOT, {})
        assert problems
        assert "not an object" in problems[0]

    def test_a_cite_into_an_unreadable_file_is_refused(self):
        bad = _well_formed()
        bad["sources"] = [
            {"cite": "src/comment_review/no_such_file.py:1", "verbatim": "x"}
        ]
        problems = source_problems("here", bad, ROOT, {})
        assert problems
        assert "cannot be read" in problems[0]

    def test_a_verbatim_outside_the_window_is_refused(self):
        bad = _well_formed()
        bad["sources"] = [
            {"cite": f"{CITED_FILE}:{CITED_LINE}", "verbatim": "not in this file"}
        ]
        problems = source_problems("here", bad, ROOT, {})
        assert problems
        assert f"within {3} lines" in problems[0]

    def test_the_cache_reads_one_file_once(self):
        """Two marks citing the same file share one cache entry."""
        cache: dict = {}
        first = _well_formed()
        second = _well_formed()
        second["sources"] = [
            {"cite": f"{CITED_FILE}:{CITED_LINE + 1}", "verbatim": ""}
        ]
        source_problems("here", first, ROOT, cache)
        source_problems("here", second, ROOT, cache)
        assert list(cache) == [CITED_FILE]


class TestSourceVerification:
    def test_a_well_formed_mark_is_clean(self):
        problems = source_verification(
            "here", _well_formed(), known=KNOWN, root=ROOT, cache={}
        )
        assert problems == []


class TestVerifyReport:
    def test_a_freshly_seeded_sheet_has_nothing_to_refuse(self):
        """Every entry is still `mark: None` -- a coverage gap, not a
        problem this step reports."""
        sheet = seed(BINDER, "block-context")
        assert verify_report(sheet, BINDER, ROOT) == []

    def test_one_filled_entry_is_checked_against_the_page(self):
        sheet = seed(BINDER, "block-context")
        for entry in sheet["marks"]:
            if entry["address"] == ROW["address"]:
                entry.update(_well_formed())
                break
        assert verify_report(sheet, BINDER, ROOT) == []

    def test_a_broken_entry_is_reported_by_its_address(self):
        sheet = seed(BINDER, "block-context")
        for entry in sheet["marks"]:
            if entry["address"] == ROW["address"]:
                bad = _well_formed()
                bad["claim"]["false"] = "a paraphrase nowhere in the paragraph"
                entry.update(bad)
                break
        problems = verify_report(sheet, BINDER, ROOT)
        assert problems
        assert all(p.startswith(ROW["address"]) for p in problems)


class TestEachCheckCanFire:
    """T3.4: each check starts from a passing mark and is mutated to fail."""

    def test_t3_1_an_address_the_binder_does_not_carry_is_refused(self):
        bad = _well_formed()
        bad["address"] = "src/comment_review/desk/mark.py@z9"
        problems = address_problems("here", bad, KNOWN)
        assert problems
        assert "z9" in problems[0]

    def test_t3_2_a_verbatim_never_written_by_the_file_is_refused(self):
        bad = _well_formed()
        bad["sources"][0]["verbatim"] = "this text is not in exceptions.py"
        problems = source_problems("here", bad, ROOT, {})
        assert problems

    def test_t3_3_a_paraphrase_of_the_false_clause_is_refused(self):
        bad = _well_formed()
        bad["claim"]["false"] = "a paraphrase, not the paragraph's own words"
        problems = claim_verbatim_problems("here", bad)
        assert problems
        assert "claim.false" in problems[0]
