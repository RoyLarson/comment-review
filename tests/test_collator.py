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
from comment_review.desk.mark import Mark, parse
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
        "sources": [
            {"cite": f"{CITED_FILE}:{CITED_LINE}", "verbatim": CITED_TEXT}
        ],
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
            sources=({"cite": "src/comment_review/no_such_file.py:1",
                      "verbatim": "x"},)
        )
        problems = source_problems("here", bad, ROOT, {})
        assert problems
        assert "cannot be read" in problems[0]

    def test_a_verbatim_outside_the_window_is_refused(self):
        bad = a_mark(
            sources=({"cite": f"{CITED_FILE}:{CITED_LINE}",
                      "verbatim": "not in this file"},)
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
            sources=({"cite": f"{secret}:1",
                      "verbatim": "TOKEN=the-line-outside"},)
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
            sources=({"cite": f"pages.py:{at}",
                      "verbatim": "# the cited comment"},)
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
        mark = a_mark(
            sources=({"cite": f"pages.py:{real + 2}", "verbatim": "x"},)
        )
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
        for name, text in (("lf.py", "a = 1\nb = 2\nc = 3\n"),
                           ("crlf.py", "a = 1\r\nb = 2\r\nc = 3\r\n")):
            p = tmp_path / name
            with open(p, "w", encoding="utf-8", newline="") as f:
                f.write(text)
            mark = a_mark(
                sources=({"cite": f"{name}:2", "verbatim": "b = 2"},)
            )
            assert source_problems("here", mark, tmp_path, {}) == [], name


class TestSourceVerification:
    def test_a_well_formed_mark_is_clean(self):
        problems = source_verification(
            "here",
            _well_formed(),
            raw_text=RAW_TEXT,
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
        assert all(p.startswith(ROW["address"]) for p in problems)

    def test_an_entry_THAT_DOES_NOT_PARSE_is_reported_not_skipped(self):
        """!! IT READ `mark.get("mark") is None` AND SKIPPED UNTIL 2026-08-29,
        which said the same thing about a slot nobody wrote in and a mark whose
        ruling key this code did not recognise -- so the second vanished here
        as well as in `flows.marks.problems_in`."""
        copy = _filled({"instruction": None})
        problems = verify_report(copy, BINDER, ROOT)
        assert problems
        assert any("instruction" in p for p in problems)


class TestEachCheckCanFire:
    """T3.4: each check starts from a passing mark and is mutated to fail."""

    def test_t3_1_an_address_the_binder_does_not_carry_is_refused(self):
        bad = a_mark(address="src/comment_review/desk/mark.py@z9")
        problems = address_problems("here", bad, KNOWN)
        assert problems
        assert "z9" in problems[0]

    def test_t3_2_a_verbatim_never_written_by_the_file_is_refused(self):
        bad = a_mark(
            sources=({"cite": f"{CITED_FILE}:{CITED_LINE}",
                      "verbatim": "this text is not in exceptions.py"},)
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
