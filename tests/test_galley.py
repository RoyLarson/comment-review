"""The galley is the proposal SET AS PAGES, and it refuses what it cannot place.

!! IT HELD 686 LINES OF LINE ARITHMETIC UNTIL 2026-08-21 -- a splice over
`(start, end, column)` ranges applied in descending order, and a staleness check
comparing stored text against the file's lines with a case for every kind. Roy:
*"how do I get you to stop thinking in line numbers?"* A page addresses its
paragraphs, so a replacement is an ASSIGNMENT and the arithmetic has nothing
left to be wrong about.

! WHAT THE DELETED TESTS PINNED IS KEPT HERE, measured through the new
mechanism: a replacement landing where it was addressed, a longer one not eating
the line below, a `c` keeping its code, CRLF surviving, a file with no final
newline keeping none. Those are facts about the RESULT and they still hold; the
tests that pinned `splice`, `overlaps` and `splice_range` went with the
functions -- see `docs/history.md`.
"""

import json  # noqa: I001  -- path shim below must import before galley
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from _paths import SCRIPTS  # noqa: F401
import compositor
import galley
import lexer
import page

ORIGINAL = "def f():\n    # old note\n    # second line\n    return 1\n"


def built(text: str, name: str = "m.py"):
    """The page for this text."""
    p = Path(name)
    return page.page_for(p, text, lexer.language_for(p), rel=name)


def place(pg, kind: str) -> str:
    """The address of the first paragraph of this kind."""
    for b in pg:
        if b.kind == kind and b.address:
            return b.address
    raise AssertionError(f"no {kind} on this page")


class TestAReplacementIsPlacedByItsAddress(unittest.TestCase):
    def test_it_lands_where_it_was_addressed(self):
        pg = built(ORIGINAL)
        self.assertEqual(galley.reset(pg, {place(pg, "comment"): "    # new note"}), [])
        self.assertEqual(
            compositor.set_page(pg), "def f():\n    # new note\n    return 1\n"
        )

    def test_a_LONGER_replacement_does_not_eat_the_line_below(self):
        # !! THE CASE THAT MADE DESCENDING ORDER LOAD-BEARING in the splice: a
        # replacement with more lines than it replaces used to shift every range
        # below it. A paragraph just hands back its lines and the next place is
        # set next, so there is no order to get right.
        pg = built(ORIGINAL)
        galley.reset(pg, {place(pg, "comment"): "    # a\n    # b\n    # c"})
        out = compositor.set_page(pg)
        self.assertIn("    return 1", out)
        self.assertNotIn("old note", out)
        self.assertEqual(out.count("# "), 3)

    def test_an_EMPTY_replacement_is_a_drop_and_needs_no_case(self):
        pg = built(ORIGINAL)
        galley.reset(pg, {place(pg, "comment"): ""})
        self.assertEqual(compositor.set_page(pg), "def f():\n    return 1\n")

    def test_an_ADDRESS_THE_PAGE_DOES_NOT_CARRY_is_refused(self):
        pg = built(ORIGINAL)
        problems = galley.reset(pg, {"m.py@b99": "# nowhere"})
        self.assertEqual(len(problems), 1)
        self.assertIn("no such place", problems[0])

    def test_CRLF_survives(self):
        pg = built(ORIGINAL.replace("\n", "\r\n"))
        galley.reset(pg, {place(pg, "comment"): "    # new note"})
        out = compositor.set_page(pg)
        self.assertIn("\r\n", out)
        # ! NO LONE LF SURVIVES: strip every CRLF and nothing ending a line is
        # left. A rewrite that normalised endings would show every line as
        # changed in the `git diff --no-index` a galley exists for.
        self.assertNotIn("\n", out.replace("\r\n", ""))

    def test_a_file_with_no_final_newline_keeps_none(self):
        pg = built(ORIGINAL.rstrip("\n"))
        galley.reset(pg, {place(pg, "comment"): "    # new note"})
        self.assertFalse(compositor.set_page(pg).endswith("\n"))


class TestACIsWritableWithoutAColumn(unittest.TestCase):
    """Roy, 2026-08-19: *"c needs to be writeable. It is the reason c is not an
    extension of b."*"""

    SRC = "z = 3  # trailing\n"

    def test_the_replacement_keeps_the_code_and_takes_ONLY_the_prose(self):
        # !! THE DEFECT THE COLUMN EXISTED FOR. A splice replaced whole lines, so
        # a `patch` on a trailing comment wrote `# reworded` OVER the statement
        # -- measured 2026-08-18, in the galley a human is asked to approve. The
        # compositor sets the code and joins what sits beside it, so the column
        # is not a field any more: there is nothing to get wrong.
        pg = built(self.SRC)
        galley.reset(pg, {place(pg, "trailing-comment"): "  # reworded"})
        self.assertEqual(compositor.set_page(pg), "z = 3  # reworded\n")

    def test_the_REPLACEMENT_CARRIES_ITS_OWN_SEPARATOR(self):
        # ! Two spaces before the hash are the author's, not the tool's.
        pg = built(self.SRC)
        galley.reset(pg, {place(pg, "trailing-comment"): "    # far out"})
        self.assertEqual(compositor.set_page(pg), "z = 3    # far out\n")

    def test_dropping_it_leaves_the_statement(self):
        pg = built(self.SRC)
        galley.reset(pg, {place(pg, "trailing-comment"): ""})
        self.assertEqual(compositor.set_page(pg), "z = 3\n")


class TestTheAnchorIsTheWholeStalenessCheck(unittest.TestCase):
    """Roy, 2026-08-21: *"the reset should only check if the address is tied to
    the anchor line of code - like they claim."*"""

    def test_a_census_whose_anchor_still_reads_the_same_is_not_drifted(self):
        pg = built(ORIGINAL)
        self.assertEqual(galley.drifted(pg, [vars(b) for b in built(ORIGINAL)]), [])

    def test_an_anchor_that_MOVED_is_caught(self):
        # ! The code under the address changed since the reviewers read it, so a
        # replacement written there would land against a statement nobody
        # reviewed.
        census = [vars(b) for b in built(ORIGINAL)]
        moved = galley.drifted(
            built("def g():\n    # old note\n    return 1\n"), census
        )
        self.assertTrue(moved)
        self.assertIn("def f():", moved[0])

    def test_a_series_with_NO_anchor_is_not_checked(self):
        # ! Leading answers to nothing by ruling, so it cannot drift against a
        # line of code. Its absence from the report is a fact, not a gap.
        pg = built('# licence\n\n"""Doc."""\n\nimport os\n')
        census = [vars(b) for b in pg]
        self.assertEqual(
            [b for b in census if b["kind"] == lexer.LEADING and b["anchor"]], []
        )


class TestAnAddIntoAnEmptyGap(unittest.TestCase):
    """!! EIGHT OF THESE WERE `@unittest.expectedFailure` UNTIL 2026-08-21.

    Every one is an `add`, and the splice could not do any of them: an empty gap
    has no lines, so its range was `n+1 .. n` -- an empty slice -- and the
    arithmetic that made an insertion land BETWEEN two code lines instead of
    replacing one of them was never got right. At the file's edges both bounds
    clamped to 1, so the address could not say which side of line 1 a gap was on
    and an `add` landed BELOW its anchor.

    ! A page has a place for the gap, and the compositor sets the places in
    order. There is no range, so there is nothing to clamp.
    """

    FILE = "a = 1\nb = 2\nc = 3\n"

    def _gap(self, pg, folio: str) -> str:
        for b in pg:
            if b.address.split("@")[-1] == folio:
                return b.address
        raise AssertionError(f"no {folio} on this page")

    def test_the_insertion_lands_BETWEEN_the_two_code_lines(self):
        pg = built(self.FILE)
        galley.reset(pg, {self._gap(pg, "b1"): "# note"})
        self.assertEqual(compositor.set_page(pg), "a = 1\n# note\nb = 2\nc = 3\n")

    def test_it_deletes_no_code(self):
        # !! THE FAILURE THE RANGE EXISTED TO AVOID: `(1, 2)` replaced BOTH
        # bounding lines with the new prose.
        pg = built(self.FILE)
        galley.reset(pg, {self._gap(pg, "b1"): "# note"})
        out = compositor.set_page(pg)
        for line in ("a = 1", "b = 2", "c = 3"):
            self.assertIn(line, out)

    def test_the_gap_ABOVE_the_first_code_line_inserts_above_it(self):
        # !! THE FILE BOUNDARY. Measured 2026-08-17: an `add` here landed BELOW
        # its anchor, because `start` and `end` both clamped to 1.
        pg = built(self.FILE)
        galley.reset(pg, {self._gap(pg, "b0"): "# header"})
        self.assertEqual(compositor.set_page(pg), "# header\na = 1\nb = 2\nc = 3\n")

    def test_the_gap_BELOW_the_last_code_line_appends(self):
        pg = built(self.FILE)
        galley.reset(pg, {self._gap(pg, "b3"): "# footer"})
        self.assertEqual(compositor.set_page(pg), "a = 1\nb = 2\nc = 3\n# footer\n")

    def test_the_two_boundary_gaps_of_a_ONE_LINE_file_DIFFER(self):
        # ! Above and below the only line of code are two places, and a range
        # over a one-line file could not tell them apart.
        above = built("a = 1\n")
        galley.reset(above, {self._gap(above, "b0"): "# over"})
        below = built("a = 1\n")
        galley.reset(below, {self._gap(below, "b1"): "# under"})
        self.assertEqual(compositor.set_page(above), "# over\na = 1\n")
        self.assertEqual(compositor.set_page(below), "a = 1\n# under\n")


class TestCLI(unittest.TestCase):
    """End to end: the exit code and the tree it writes."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.repo = self.root / "repo"
        (self.repo / "pkg").mkdir(parents=True)
        (self.repo / "pkg" / "m.py").write_text(ORIGINAL, encoding="utf-8")
        # !! FROM `page_for`, STAMPED as `census.py`'s run loop stamps it. A
        # hand-built census drifts from what the tool emits, which is how a
        # trailing comment once passed here while the shipped path deleted code.
        self.census = self.root / "census.json"
        made = page.page_for(
            Path("pkg/m.py"), ORIGINAL, lexer.language_for(Path("m.py"))
        )
        self.census.write_text(
            json.dumps([vars(b) for b in made], default=list), encoding="utf-8"
        )
        self.paragraphs = json.loads(self.census.read_text(encoding="utf-8"))
        self.note = next(
            b["address"] for b in self.paragraphs if b["kind"] == "comment"
        )
        self.out = self.root / "galley"

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, edits):
        path = self.root / "edits.json"
        path.write_text(json.dumps(edits), encoding="utf-8")
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "galley.py"),
                "--repo",
                str(self.repo),
                "--census",
                str(self.census),
                "--edits",
                str(path),
                "--out",
                str(self.out),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

    def test_it_writes_a_mirror_and_leaves_the_source_alone(self):
        result = self._run({str(self.note): "    # new note"})
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        written = self.out / "pkg" / "m.py"
        self.assertTrue(written.exists(), result.stdout)
        self.assertIn("# new note", written.read_text(encoding="utf-8"))
        # !! NOTHING UNDER `--repo` IS TOUCHED. The galley is a trial impression;
        # the real file is not written until 7b approves the draft.
        self.assertEqual(
            (self.repo / "pkg" / "m.py").read_text(encoding="utf-8"), ORIGINAL
        )

    def test_an_ADDRESS_the_census_does_not_carry_is_refused(self):
        result = self._run({"pkg!m.py@b99": "    # nowhere"})
        self.assertEqual(result.returncode, 1)
        self.assertIn("no paragraph in this census", result.stdout)

    def test_a_MOVED_anchor_refuses_the_file_and_writes_nothing(self):
        (self.repo / "pkg" / "m.py").write_text(
            "def RENAMED():\n    # old note\n    # second line\n    return 1\n",
            encoding="utf-8",
        )
        result = self._run({str(self.note): "    # new note"})
        self.assertEqual(result.returncode, 1)
        self.assertIn("moved since the census", result.stdout)
        self.assertFalse((self.out / "pkg" / "m.py").exists())

    def test_an_UNADDRESSED_census_is_refused_whole(self):
        bare = [dict(b, address="") for b in self.paragraphs]
        self.census.write_text(json.dumps(bare, default=list), encoding="utf-8")
        result = self._run({"m.py@b0": "    # anything"})
        self.assertEqual(result.returncode, 2)
        self.assertIn("carries no addresses", result.stdout)
