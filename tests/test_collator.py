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

import re
from dataclasses import replace
from pathlib import Path

import pytest
from conftest import ROOT
from helpers import a_clean, a_correct, a_small_real_tree, binder_of

from comment_review.binder.binder import rows_of
from comment_review.desk.collator import (
    address_problems,
    base_texts,
    claim_verbatim_problems,
    drift_in,
    known_addresses,
    problems_in,
    source_problems,
    source_verification,
    tally,
    verify_report,
)
from comment_review.desk.mark import Instruction, Mark, parse
from comment_review.flows.distribute import seed

DESK = ROOT / "src" / "comment_review" / "desk"

#: A real binder over `desk/` -- the same fixture-free input
#: `tests/test_distribute_flow.py` already builds this way.
BINDER = binder_of(DESK, 0)
ROWS = rows_of(BINDER)
#: `mark.py`'s own `@a0` -- narrowed by suffix, since `desk/` holds several
#: files that each carry their own `@a0`.
ROW = next(r for r in ROWS if r["address"].endswith("mark.py@a0"))
KNOWN = known_addresses(BINDER)


def line_of(path: Path, number: int) -> str:
    """Line `number` of `path`, numbered from the file's own line endings.

    !! DERIVED HERE, FROM WHAT A LINE ENDING IS -- never from the splitter the
    module under test calls. This read the file with `Path.read_text(...)` and
    `str.splitlines()` until 2026-08-29, which is the SAME defect the collator
    carried, so the suite could not disagree with it: a form feed made both
    sides count a page break as a line and both agreed on the wrong number.

    ! The three endings are CR, LF and CRLF, and nothing else. `newline=""`
    turns off universal-newline translation so a CRLF file is read as it sits.
    """
    with open(path, encoding="utf-8", newline="") as f:
        text = f.read()
    return re.split(r"\r\n|\r|\n", text)[number - 1]


#: A real line of a real file this checkout carries.
CITED_FILE = "src/comment_review/machine/exceptions.py"
CITED_LINE = 57
CITED_TEXT = line_of(ROOT / CITED_FILE, CITED_LINE)


#: The paragraph the row seeded -- what T3.3 checks a quoted sentence against.
#: ! IT IS THE ROW'S, NOT THE MARK'S: `docs/the-mark.md` puts `raw_text` on the
#: seeded row and `change` on the mark, so the two can be diffed, and
#: `claim_verbatim_problems` takes it as its own argument for that reason.
RAW_TEXT = ROW["raw_text"]


def _entry() -> dict:
    """A `correct` entry, as a role would hand back the row `seed()` gave it.

    ! KEYED `instruction`, which is what `reviewer-brief.md` publishes. The
    code read it as `mark` until 2026-08-29.
    """
    false = RAW_TEXT.splitlines()[0]
    return {
        "address": ROW["address"],
        "anchor": ROW["anchor"],
        "raw_text": RAW_TEXT,
        "instruction": "correct",
        "claim": {"false": false, "true": "the corrected sentence"},
        "reason": "written for the collator test suite",
        "sources": [{"cite": f"{CITED_FILE}:{CITED_LINE}", "verbatim": CITED_TEXT}],
        "change": "# corrected",
    }


def _well_formed() -> Mark:
    """`_entry()` through the real parse -- what every check below now takes.

    !! THE COLLATOR TAKES A `Mark`, NOT A DICT, SINCE 2026-08-29. Each check
    read the entry by key until then, which is what let `INSTRUCTIONS.get(...)`
    be handed a `str` at ten sites.
    """
    mark, why = parse("the collator fixture", _entry())
    assert why == [], why
    assert mark is not None
    return mark


def a_mark(**overrides) -> Mark:
    """`_well_formed()` with one field replaced -- how each check is made to fire.

    ! BUILT WITH `dataclasses.replace`, not by re-parsing a broken entry. Some
    of the shapes below (a bare-string `source`) are ones `parse` refuses
    outright, and the question here is what SOURCE-VERIFICATION does when it
    meets one -- the two steps ask different questions and this file must be
    able to ask its own.
    """
    return replace(_well_formed(), **overrides)


def test_known_addresses_carries_the_real_row():
    assert ROW["address"] in KNOWN


class TestAddressProblems:
    """T3.1 -- the address resolves to a place the binder carries."""

    def test_a_real_address_resolves(self):
        assert address_problems("here", _well_formed(), KNOWN) == []

    def test_clean_needs_no_address(self):
        """A role returns `clean` over most of the binder -- no address at
        all, which is `desk.mark.parse`'s question, not this one's."""
        clean, why = parse("here", {"instruction": "clean"})
        assert why == [] and clean is not None
        assert address_problems("here", clean, KNOWN) == []


class TestClaimVerbatimProblems:
    """T3.3 -- the sentence the claim rules on is really in the paragraph."""

    def test_the_false_clause_is_really_in_the_paragraph(self):
        assert claim_verbatim_problems("here", _well_formed(), RAW_TEXT) == []

    def test_add_and_query_quote_nothing(self):
        """`add`'s `missing` and `query`'s `shape` are not checked this way --
        `Row.quotes_original` is empty for both, so neither is measured
        against the paragraph even when it names nothing in it."""
        add = a_mark(instruction="add", claim={"missing": "x", "anchor": "`f`"})
        query = a_mark(instruction="query", claim={"shape": "outside-my-role"})
        assert claim_verbatim_problems("here", add, RAW_TEXT) == []
        assert claim_verbatim_problems("here", query, RAW_TEXT) == []

    def test_a_missing_claim_key_is_not_this_checks_question(self):
        """`desk.mark.parse` already refuses a `correct` with no `false`;
        source-verification has nothing to compare and says nothing."""
        assert claim_verbatim_problems("here", a_mark(claim={}), RAW_TEXT) == []


class TestSourceProblems:
    """T3.2 -- every `source` resolves, `verbatim` within reach of the cite."""

    def test_a_real_citation_resolves(self):
        cache = {}
        assert source_problems("here", _well_formed(), ROOT, cache) == []

    def test_a_bare_string_source_is_refused_not_dropped(self):
        """`record-and-verdicts-disagree` T3: the retired reader filtered
        `sources` to dicts before its check ran, so a bare string vanished.
        This loop walks `sources` as handed.

        ! AND `Mark.sources` IS TYPED `object` FOR THIS REASON -- a parse that
        narrowed it to dicts would drop the entry before this check saw it,
        which is the same defect one step earlier."""
        bad = a_mark(sources=("src/mod.py:12 | def thing()",))
        problems = source_problems("here", bad, ROOT, {})
        assert problems
        assert "not an object" in problems[0]

    def test_a_cite_into_an_unreadable_file_is_refused(self):
        bad = a_mark(
            sources=({"cite": "src/comment_review/no_such_file.py:1", "verbatim": "x"},)
        )
        problems = source_problems("here", bad, ROOT, {})
        assert problems
        assert "cannot be read" in problems[0]

    def test_a_verbatim_outside_the_window_is_refused(self):
        bad = a_mark(
            sources=(
                {"cite": f"{CITED_FILE}:{CITED_LINE}", "verbatim": "not in this file"},
            )
        )
        problems = source_problems("here", bad, ROOT, {})
        assert problems
        assert f"within {3} lines" in problems[0]

    def test_an_ABSOLUTE_cite_cannot_reach_outside_the_checkout(self, tmp_path):
        """`root / path` DISCARDS `root` when `path` is absolute, so a role's
        own `cite` could name any file on the machine and have its `verbatim`
        confirmed against it.

        ! The root here is a real, empty directory the secret does not sit
        under, and the `verbatim` is the secret file's own line -- so the only
        way this passes is by refusing before the join.
        """
        root = tmp_path / "repo"
        root.mkdir()
        outside = tmp_path / "outside"
        outside.mkdir()
        secret = outside / "secrets.txt"
        secret.write_text("TOKEN=the-line-outside\n", encoding="utf-8")

        mark = a_mark(
            sources=({"cite": f"{secret}:1", "verbatim": "TOKEN=the-line-outside"},)
        )
        cache: dict = {}
        problems = source_problems("here", mark, root, cache)
        assert problems
        assert "outside the checkout" in problems[0]
        assert cache == {}  # nothing outside the root was ever opened

    def test_a_cite_that_WALKS_UP_cannot_reach_outside_the_checkout(self, tmp_path):
        """The other shape of the same escape -- `..`, which resolves out of
        the root without ever being absolute."""
        root = tmp_path / "repo"
        root.mkdir()
        outside = tmp_path / "outside"
        outside.mkdir()
        (outside / "secrets.txt").write_text(
            "TOKEN=the-line-outside\n", encoding="utf-8"
        )

        mark = a_mark(
            sources=(
                {
                    "cite": "../outside/secrets.txt:1",
                    "verbatim": "TOKEN=the-line-outside",
                },
            )
        )
        cache: dict = {}
        problems = source_problems("here", mark, root, cache)
        assert problems
        assert "outside the checkout" in problems[0]
        assert cache == {}

    def test_the_cache_reads_one_file_once(self):
        """Two marks citing the same file share one cache entry."""
        cache: dict = {}
        first = _well_formed()
        second = a_mark(
            sources=({"cite": f"{CITED_FILE}:{CITED_LINE + 1}", "verbatim": ""},)
        )
        source_problems("here", first, ROOT, cache)
        source_problems("here", second, ROOT, cache)
        assert list(cache) == [CITED_FILE]


#: A page-break character `str.splitlines()` treats as a line ending and a file
#: does not. It is the shape the collator's own splitter disagreed on; the other
#: seven are the vertical tab, the three ASCII separators, NEL, and Unicode's
#: line and paragraph separators.
PAGE_BREAK = "\x0c"
#: Four page breaks above the cited comment, so the skew is 4 -- one past
#: `WITHIN`, which is what turns a truthful citation into a refusal.
PAGED = (
    "import os\n"
    f"{PAGE_BREAK}\n"
    "def a():\n"
    "    return 1\n"
    f"{PAGE_BREAK}\n"
    "def b():\n"
    "    return 2\n"
    f"{PAGE_BREAK}\n"
    "def c():\n"
    "    return 3\n"
    f"{PAGE_BREAK}\n"
    "# the cited comment\n"
    "def d():\n"
    "    return 4\n"
)


class TestACitedFileIsNumberedTheWAYTHEBINDERNUMBERSIT:
    """A role cites the line number it was HANDED, so this must agree with it.

    !! `str.splitlines()` BREAKS ON ELEVEN CHARACTERS AND EIGHT ARE NOT LINE
    ENDINGS, which is why `machine/constants.text_lines` exists and why its
    docstring states that *"nothing in the reading or setting path calls
    `splitlines`"*. `collator._lines` was the one site in `src/` that did.

    ! THE EXPECTATIONS BELOW ARE DERIVED FROM WHAT A LINE ENDING IS, by this
    file's own `line_of`/`re.split` -- not from `constants.text_lines`, and not
    from the collator. A test that split the file the same way the module does
    is how this survived: both sides counted a page break as a line and agreed.
    """

    def _write(self, tmp_path: Path) -> Path:
        p = tmp_path / "pages.py"
        with open(p, "w", encoding="utf-8", newline="") as f:
            f.write(PAGED)
        return p

    def test_a_truthful_citation_at_the_real_line_resolves(self, tmp_path):
        """The failure that costs the most: a role quotes a real sentence,
        numbers it as the page numbered it, and is told the evidence is not
        within reach -- so a true finding is discarded as fabricated."""
        self._write(tmp_path)
        lines = re.split(r"\r\n|\r|\n", PAGED)
        at = lines.index("# the cited comment") + 1
        mark = a_mark(
            sources=({"cite": f"pages.py:{at}", "verbatim": "# the cited comment"},)
        )
        assert source_problems("here", mark, tmp_path, {}) == []

    def test_the_page_breaks_really_do_move_the_number(self, tmp_path):
        """The case has to be able to fail, or the test above proves nothing:
        the two splitters must actually disagree on this file."""
        lines = re.split(r"\r\n|\r|\n", PAGED)
        at = lines.index("# the cited comment") + 1
        assert PAGED.splitlines().index("# the cited comment") + 1 - at == 4

    def test_a_cite_past_the_real_end_of_the_file_is_refused(self, tmp_path):
        """The inflated count let a cite past EOF through the bound check and
        into a window of lines the file does not have."""
        self._write(tmp_path)
        # ! The file ends with a newline, so its last line is the one before
        # the trailing break -- `re.split` leaves an empty final element.
        real = len([ln for ln in re.split(r"\r\n|\r|\n", PAGED)[:-1]])
        mark = a_mark(sources=({"cite": f"pages.py:{real + 2}", "verbatim": "x"},))
        problems = source_problems("here", mark, tmp_path, {})
        assert problems
        assert "past the end of the file" in problems[0]

    def test_a_CRLF_file_is_numbered_the_same_as_an_LF_one(self, tmp_path):
        """A Windows checkout must resolve the same citations as a POSIX one.

        ! This passes under BOTH readers, and is kept as the statement of that
        agreement rather than as a gate: `LINE_BREAK` splits on the same three
        sequences universal-newline translation collapses. `collator._lines`
        says so at the change.
        """
        for name, text in (
            ("lf.py", "a = 1\nb = 2\nc = 3\n"),
            ("crlf.py", "a = 1\r\nb = 2\r\nc = 3\r\n"),
        ):
            p = tmp_path / name
            with open(p, "w", encoding="utf-8", newline="") as f:
                f.write(text)
            mark = a_mark(sources=({"cite": f"{name}:2", "verbatim": "b = 2"},))
            assert source_problems("here", mark, tmp_path, {}) == [], name


class TestSourceVerification:
    def test_a_well_formed_mark_is_clean(self):
        problems = source_verification(
            "here",
            _well_formed(),
            base=RAW_TEXT,
            known=KNOWN,
            root=ROOT,
            cache={},
        )
        assert problems == []


def _filled(overrides: dict) -> dict:
    """A seeded edit_copy with `ROW`'s own slot filled in by `_entry()`.

    Args:
        overrides: applied to the entry after `_entry()`, before it is written
            into the slot.
    """
    copy = seed(BINDER, "block-context")
    for page in copy["sheets"]:
        for entry in page["marks"]:
            if entry["address"] == ROW["address"]:
                entry.update({**_entry(), **overrides})
                return copy
    raise AssertionError(f"no seeded slot for {ROW['address']}")


class TestVerifyReport:
    def test_a_freshly_seeded_sheet_has_nothing_to_refuse(self):
        """Every entry is still `instruction: None` and nothing else written
        -- `desk.mark.untouched`, a coverage gap rather than a problem this
        step reports."""
        sheet = seed(BINDER, "block-context")
        assert verify_report(sheet, BINDER, ROOT) == []

    def test_one_filled_entry_is_checked_against_the_page(self):
        assert verify_report(_filled({}), BINDER, ROOT) == []

    def test_a_broken_entry_is_reported_by_its_address(self):
        copy = _filled(
            {
                "claim": {
                    "false": "a paraphrase nowhere in the paragraph",
                    "true": "the corrected sentence",
                }
            }
        )
        problems = verify_report(copy, BINDER, ROOT)
        assert problems
        # !! THE ADDRESS IS A FIELD SINCE 2026-08-31, not a prefix on a
        # sentence -- `P25` gave this a production caller, and `Problem` exists
        # so a finding can be ROUTED. This asserts the same claim more strictly
        # than the `startswith` it replaces: the address is the whole value now,
        # not the opening of one.
        assert all(p.address == ROW["address"] for p in problems)
        assert all(p.role == copy["role"] for p in problems)

    def test_an_entry_THAT_DOES_NOT_PARSE_is_left_to_problems_in(self):
        """!! SUPERSEDED 2026-08-31, AND THE DISTINCTION IT NAMED STILL HOLDS.

        It read `test_..._is_reported_not_skipped` and asserted `verify_report`
        contributed `desk.mark.parse`'s messages -- right while this function
        had no production caller. `P25` put it in the flow beside
        `problems_in`, which parses every entry already, so a malformed mark
        came back TWICE with a byte-identical message.

        ! WHAT 2026-08-29 FIXED IS NOT UNDONE. That defect was reading
        `mark.get("mark") is None`, which said the same thing about a slot
        nobody wrote in and a mark whose ruling key the code did not
        recognise -- and the second is still not silently folded into the
        first. It is reported once, by `problems_in`, which
        `tests/test_collator.py::TestProblemsIn` covers.
        """
        copy = _filled({"instruction": None})
        assert verify_report(copy, BINDER, ROOT) == []
        found, _ruled = problems_in(copy)
        assert any("instruction" in p.message for p in found)


class TestTheBaseIsTheBinders:
    """D10 -- a compose or a verbatim check reads its base off the binder,
    never off a mark's own returned `raw_text`."""

    def test_base_texts_keys_every_address_the_binder_carries(self, tmp_path):
        binder = binder_of(a_small_real_tree(tmp_path), 0)
        base = base_texts(binder)
        carried = {r["address"] for r in rows_of(binder) if r.get("address")}
        assert set(base) == carried

    def test_a_returned_raw_text_that_changed_is_REPORTED(self, tmp_path):
        """!! THE 699/699 SHAPE, REFUSED. A check that reads its base off the
        entry it is checking cannot disagree with it -- `docs/gates.md`."""
        repo = a_small_real_tree(tmp_path)
        binder = binder_of(repo, 0)
        copy = seed(binder, "block-context")
        entry = copy["sheets"][0]["marks"][0]
        entry.update(a_clean(entry["address"]))
        entry["raw_text"] = "# not what was seeded\n"
        drift = drift_in(copy, base_texts(binder))
        assert [p.address for p in drift] == [entry["address"]]
        assert drift[0].role == "block-context"

    def test_an_untouched_slot_is_not_drift(self, tmp_path):
        """Nobody wrote here, so there is nothing to have drifted."""
        repo = a_small_real_tree(tmp_path)
        binder = binder_of(repo, 0)
        copy = seed(binder, "block-context")
        assert drift_in(copy, base_texts(binder)) == []

    def test_a_faithful_copy_reports_no_drift(self, tmp_path):
        repo = a_small_real_tree(tmp_path)
        binder = binder_of(repo, 0)
        copy = seed(binder, "block-context")
        entry = copy["sheets"][0]["marks"][0]
        entry.update(a_clean(entry["address"]))
        assert drift_in(copy, base_texts(binder)) == []

    def test_verify_report_measures_the_claim_against_the_BINDER(self, tmp_path):
        """A mark whose `claim.false` is absent from the seeded paragraph is
        reported even when the mark's own `raw_text` was rewritten to contain
        it -- which is the whole point of taking the base from the binder."""
        repo = a_small_real_tree(tmp_path)
        binder = binder_of(repo, 0)
        copy = seed(binder, "block-context")
        entry = copy["sheets"][0]["marks"][0]
        entry.update(a_correct(entry["address"], "a sentence nobody wrote"))
        entry["raw_text"] = "a sentence nobody wrote"
        problems = verify_report(copy, binder, repo)
        assert any("is not in the paragraph" in p.message for p in problems)


class TestEachCheckCanFire:
    """T3.4: each check starts from a passing mark and is mutated to fail."""

    def test_t3_1_an_address_the_binder_does_not_carry_is_refused(self):
        bad = a_mark(address="src/comment_review/desk/mark.py@z9")
        problems = address_problems("here", bad, KNOWN)
        assert problems
        assert "z9" in problems[0]

    def test_t3_2_a_verbatim_never_written_by_the_file_is_refused(self):
        bad = a_mark(
            sources=(
                {
                    "cite": f"{CITED_FILE}:{CITED_LINE}",
                    "verbatim": "this text is not in exceptions.py",
                },
            )
        )
        problems = source_problems("here", bad, ROOT, {})
        assert problems

    def test_t3_3_a_paraphrase_of_the_false_clause_is_refused(self):
        bad = a_mark(
            claim={
                "false": "a paraphrase, not the paragraph's own words",
                "true": "the corrected sentence",
            }
        )
        problems = claim_verbatim_problems("here", bad, RAW_TEXT)
        assert problems
        assert "claim.false" in problems[0]


class TestProblemsAreRoutable:
    def test_a_problem_names_the_role_and_the_address(self, tmp_path):
        """Roy, 2026-08-30: "the errors should be stacked and capable of being
        read off correctly so that each can be fixed or sent back to the role."
        A sentence cannot be routed; a role and an address can."""
        copy = seed(binder_of(a_small_real_tree(tmp_path), 0), "block-context")
        entry = copy["sheets"][0]["marks"][0]
        entry.update({"instruction": "correct", "claim": {}})
        problems, ruled = problems_in(copy)
        assert ruled == 1
        assert problems
        assert all(p.role == "block-context" for p in problems)
        assert all(p.address == entry["address"] for p in problems)
        assert all(isinstance(p.message, str) and p.message for p in problems)

    def test_every_broken_mark_is_reported_not_only_the_first(self, tmp_path):
        # ! NOT NECESSARILY `sheets[0]` -- `a_small_real_tree` copies
        # `__init__.py` alongside the other three, and its page (sorted first,
        # alphabetically ahead of the rest) holds exactly one row: a bare
        # module docstring with no code below it. So the sheet checked here is
        # whichever one actually carries two places, not the first in order.
        copy = seed(binder_of(a_small_real_tree(tmp_path), 0), "block-context")
        marks = next(s["marks"] for s in copy["sheets"] if len(s["marks"]) >= 2)
        for entry in marks[:2]:
            entry.update({"instruction": "correct", "claim": {}})
        problems, ruled = problems_in(copy)
        assert ruled == 2
        assert len({p.address for p in problems}) == 2

    def test_a_copy_level_problem_carries_an_empty_address(self, tmp_path):
        copy = seed(binder_of(a_small_real_tree(tmp_path), 0), "block-context")
        del copy["role"]
        problems, _ = problems_in(copy)
        assert any(p.address == "" and "`role`" in p.message for p in problems)


# ! MOVED FROM `tests/test_distribute_flow.py`, `decision-log.md Process: #54` --
# `problems_in`, `unruled` and `tally` moved to this module with the rest of
# P24; these tests came with them, changing only the import and (for the one
# case that read a message as a string) the `Problem` field it now reads.
def test_problems_in_reads_every_sheet_not_just_the_first():
    copy = seed(binder_of(DESK, 0), "block-context")
    # A malformed mark on the LAST sheet -- a walker that stops at the first
    # sheet passes this file and misses it.
    copy["sheets"][-1]["marks"][0]["instruction"] = "correct"
    messages, ruled = problems_in(copy)
    assert ruled == 1
    assert messages, "a correct with no claim must be refused wherever it sits"


@pytest.mark.parametrize(
    "bad", [{"junk": 1}, {"root": 7, "revise": "x"}, {}, "oops", None, []]
)
def test_a_sheet_whose_read_from_is_the_wrong_SHAPE_is_refused(bad):
    # !! `problems_in` HAND-ROLLED `isinstance(..., dict) and truthy` FOR ONE
    # COMMIT, so `{"junk": 1}` and `{"root": 7, "revise": "x"}` passed
    # the per-copy check at exit 0 while `bind` REFUSED the identical value -- two
    # spellings of one rule, disagreeing. It reuses `binder`'s checker now.
    sheet = {"role": "block-context", "read_from": bad, "sheets": []}
    messages, _ = problems_in(sheet)
    # ! FORCED BY THE MOVE: `messages` holds `Problem`s now, not strings, so
    # the membership test reads `.message` instead of the `Problem` itself.
    assert any("read_from" in m.message for m in messages), bad


def test_a_sheet_carrying_a_code_concern_validates():
    """An EXPECTATION test, not an INPUT one -- the sheet is a literal a
    human checked, per `decision-log.md Vocabulary: #23`. It carries no real
    mark to check, so nothing here needs a real binder."""
    sheet = {
        "role": "block-context",
        # ! `read_from` IS PART OF A WELL-FORMED SHEET since 2026-08-28 --
        # `seed` puts it there and `problems_in` now rules on it, so a literal
        # that omits it is testing a sheet no role can return.
        "read_from": {"root": "src/comment_review/desk", "revise": 0},
        "sheets": [],
        "code_concerns": [
            {"where": "src/m.py:12", "concern": "the guard admits a negative"}
        ],
    }
    assert problems_in(sheet) == ([], 0)


def test_tally_counts_a_ruled_mark_wherever_its_sheet_sits():
    # INPUT FROM REALITY: a real binder through the real seed(), then filled
    # exactly as a role legitimately would -- `instruction` holds the
    # INSTRUCTION NAME as a plain string, matching `desk.mark.parse`'s own
    # `isinstance(named, str)` check and this file's own `_well_formed()`
    # fixture. `tally` walked `report["marks"]`, a top-level key `seed()` has
    # not written since 2026-08-29 -- so on today's nested shape it silently
    # returned `{}` for every sheet, ruled or not, rather than raising or
    # reporting.
    copy = seed(binder_of(DESK, 0), "block-context")
    copy["sheets"][-1]["marks"][0].update(
        {
            "instruction": "correct",
            "claim": {"false": "x", "true": "y"},
            "reason": "test",
            "sources": [],
            "change": "# x",
        }
    )
    assert tally(copy) == {Instruction.CORRECT: 1}


def test_tally_of_a_freshly_seeded_sheet_is_empty():
    # ! An unruled sheet's `{}` is the CORRECT answer -- every mark is still
    # `None`, so nothing has an instruction to count. This is what
    # distinguishes it from the silent `{}` the bug above produced for a
    # RULED sheet: the same return value, for opposite reasons.
    copy = seed(binder_of(DESK, 0), "block-context")
    assert tally(copy) == {}
