"""The galley is the proposal set as files, and it refuses what it cannot splice."""

import json  # noqa: I001  -- path shim below must import before galley
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from _paths import SCRIPTS  # noqa: F401
import galley

ORIGINAL = "def f():\n    # old note\n    # second line\n    return 1\n"


class TestSplice(unittest.TestCase):
    def test_a_replacement_lands_on_the_named_range(self):
        out = galley.splice(ORIGINAL, [(2, 3, "    # new note")])
        self.assertEqual(out, "def f():\n    # new note\n    return 1\n")

    def test_a_longer_replacement_does_not_eat_the_line_below(self):
        out = galley.splice(ORIGINAL, [(2, 3, "    # a\n    # b\n    # c")])
        self.assertIn("    return 1", out)
        self.assertNotIn("old note", out)

    def test_two_edits_apply_bottom_up_so_neither_shifts_the_other(self):
        # !! The case that makes descending order load-bearing: the first edit
        # changes the line count, so a top-down splice would put the second one
        # in the wrong place.
        text = "a\n# one\nb\n# two\nc\n"
        out = galley.splice(text, [(2, 2, "# ONE\n# ONE MORE"), (4, 4, "# TWO")])
        self.assertEqual(out, "a\n# ONE\n# ONE MORE\nb\n# TWO\nc\n")

    def test_crlf_survives(self):
        out = galley.splice("a\r\n# old\r\nb\r\n", [(2, 2, "# new")])
        self.assertEqual(out, "a\r\n# new\r\nb\r\n")

    def test_a_file_with_no_trailing_newline_keeps_none(self):
        self.assertEqual(galley.splice("a\n# old", [(2, 2, "# new")]), "a\n# new")


class TestOverlapsAreRefused(unittest.TestCase):
    def test_two_edits_sharing_a_line_are_found(self):
        self.assertEqual(galley.overlaps([(1, 3, "x"), (3, 5, "y")]), (1, 3))

    def test_adjacent_edits_do_not_overlap(self):
        self.assertIsNone(galley.overlaps([(1, 2, "x"), (3, 4, "y")]))

    def test_order_of_the_list_does_not_matter(self):
        self.assertEqual(galley.overlaps([(3, 5, "y"), (1, 3, "x")]), (1, 3))


class TestBlockMatches(unittest.TestCase):
    """!! This check must be able to FAIL, and the first version could not.

    It compared the file against a slice of itself, which is equal by
    construction. A stale census range would then have been spliced over
    whatever now sits at those line numbers -- the one failure a galley must
    never produce quietly.
    """

    LINES = ORIGINAL.splitlines()

    def test_a_matching_block_passes(self):
        block = {
            "start": 2,
            "end": 3,
            "raw_lines": ["    # old note", "    # second line"],
        }
        self.assertTrue(galley.block_matches(self.LINES, block))

    def test_a_block_whose_text_moved_is_caught(self):
        block = {"start": 2, "end": 3, "raw_lines": ["    # SOMETHING ELSE", "    # x"]}
        self.assertFalse(galley.block_matches(self.LINES, block))

    def test_a_range_past_the_end_of_the_file_is_caught(self):
        block = {"start": 9, "end": 12, "raw_lines": ["    # x"]}
        self.assertFalse(galley.block_matches(self.LINES, block))

    def test_a_block_carrying_no_raw_lines_is_refused(self):
        # An interval block stores none, and nothing can be verified against it.
        self.assertFalse(galley.block_matches(self.LINES, {"start": 2, "end": 3}))


class TestCLI(unittest.TestCase):
    """End to end: the exit code and the tree it writes."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.repo = self.root / "repo"
        (self.repo / "pkg").mkdir(parents=True)
        (self.repo / "pkg" / "m.py").write_text(ORIGINAL, encoding="utf-8")
        self.census = self.root / "census.json"
        self.census.write_text(
            json.dumps(
                [
                    {
                        "path": "pkg/m.py",
                        "start": 2,
                        "end": 3,
                        "kind": "comment",
                        "raw_lines": ["    # old note", "    # second line"],
                    }
                ]
            ),
            encoding="utf-8",
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
        result = self._run({"1": "    # new note"})
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(
            (self.out / "pkg" / "m.py").read_text(encoding="utf-8"),
            "def f():\n    # new note\n    return 1\n",
        )
        self.assertEqual(
            (self.repo / "pkg" / "m.py").read_text(encoding="utf-8"), ORIGINAL
        )

    def test_an_index_outside_the_census_is_refused(self):
        result = self._run({"99": "    # x"})
        self.assertEqual(result.returncode, 1)
        self.assertIn("outside the census", result.stdout)

    def test_a_stale_range_refuses_the_file_and_writes_nothing(self):
        (self.repo / "pkg" / "m.py").write_text(
            "def f():\n    return 1\n", encoding="utf-8"
        )
        result = self._run({"1": "    # new note"})
        self.assertEqual(result.returncode, 1)
        self.assertIn("no longer match the census", result.stdout)
        self.assertFalse((self.out / "pkg" / "m.py").exists())


class TestAnIntervalIsInsertedInto(unittest.TestCase):
    """An `add` cites the empty INTERVAL its prose is missing from.

    !! An interval's `start` and `end` are the two lines of CODE that bound it,
    so replacing `start..end` writes over both of them. Measured 2026-08-17 on
    the first cycle run: `block_matches` answered False for all 99 intervals in
    one census, so every `add` was refused before the range was ever used --
    and the refusal hid the fact that the range would have deleted code.

    !! THE BLOCKS HERE COME FROM A REAL CENSUS. Built by hand they carried no
    `edit_start`/`edit_end`, took the legacy fallback, and went on passing
    against a shape `census.py` no longer emits -- which is the whole failure
    being tested, one level up.
    """

    FILE = "a = 1\nb = 2\nc = 3\n"

    def _census(self, text):
        import census

        prose = census.blocks_stdlib(Path("m.py"), text)
        return [b.__dict__ for b in census.intervals(Path("m.py"), text, prose)]

    def _gap(self, text, start, end):
        """The interval bounded by these two lines, as the census emits it."""
        for b in self._census(text):
            if (b["start"], b["end"]) == (start, end):
                return b
        raise AssertionError(f"no interval {start}-{end} in {self._census(text)}")

    def test_adjacent_code_lines_give_an_EMPTY_range(self):
        # ! `n+1 .. n` -- `splice` assigns into an empty slice, which inserts.
        self.assertEqual(galley.splice_range(self._gap(self.FILE, 1, 2)), (2, 1))

    def test_a_prose_block_keeps_its_own_range(self):
        block = {"start": 4, "end": 6, "kind": "comment", "raw_lines": ["# x"]}
        self.assertEqual(galley.splice_range(block), (4, 6))

    def test_the_insertion_lands_BETWEEN_the_two_code_lines(self):
        start, end = galley.splice_range(self._gap(self.FILE, 1, 2))
        out = galley.splice(self.FILE, [(start, end, "# note")])
        self.assertEqual(out, "a = 1\n# note\nb = 2\nc = 3\n")

    def test_it_deletes_no_code(self):
        # !! The failure this range exists to avoid: `(1, 2)` would have
        # replaced BOTH bounding lines with the new prose.
        start, end = galley.splice_range(self._gap(self.FILE, 1, 2))
        out = galley.splice(self.FILE, [(start, end, "# note")])
        for line in ("a = 1", "b = 2", "c = 3"):
            self.assertIn(line, out)

    def test_the_gap_ABOVE_the_first_code_line_inserts_above_it(self):
        # !! The file boundary. `start` and `end` are both clamped to 1 here,
        # so the address cannot say which side of line 1 the gap is on --
        # measured 2026-08-17, an `add` on it landed BELOW the anchor.
        out = galley.splice(
            self.FILE, [(*galley.splice_range(self._gap(self.FILE, 1, 1)), "# header")]
        )
        self.assertEqual(out, "# header\na = 1\nb = 2\nc = 3\n")

    def test_the_gap_BELOW_the_last_code_line_appends(self):
        out = galley.splice(
            self.FILE, [(*galley.splice_range(self._gap(self.FILE, 3, 3)), "# footer")]
        )
        self.assertEqual(out, "a = 1\nb = 2\nc = 3\n# footer\n")

    def test_the_two_boundary_gaps_of_a_ONE_LINE_file_differ(self):
        # !! Both address `m.py:1-1`; only the edit range tells them apart.
        gaps = [b for b in self._census("a = 1\n") if (b["start"], b["end"]) == (1, 1)]
        self.assertEqual(len(gaps), 2)
        self.assertNotEqual(galley.splice_range(gaps[0]), galley.splice_range(gaps[1]))

    def test_an_empty_interval_MATCHES(self):
        lines = self.FILE.splitlines()
        self.assertTrue(galley.block_matches(lines, self._gap(self.FILE, 1, 2)))

    def test_an_interval_spanning_a_blank_line_matches(self):
        text = "a = 1\n\nb = 2\n"
        self.assertTrue(galley.block_matches(text.splitlines(), self._gap(text, 1, 3)))

    def test_an_interval_that_GAINED_prose_is_stale(self):
        # !! The staleness that matters for an `add`: the gap it says holds no
        # prose now holds some.
        text = "a = 1\n\nb = 2\n"
        gap = self._gap(text, 1, 3)
        grown = "a = 1\n# someone wrote this\nb = 2\n".splitlines()
        self.assertFalse(galley.block_matches(grown, gap))

    def test_an_interval_past_the_end_of_the_file_is_stale(self):
        gap = dict(self._gap(self.FILE, 1, 2), start=3, end=9, edit_start=4, edit_end=8)
        self.assertFalse(galley.block_matches(self.FILE.splitlines(), gap))


class TestADocstringBlockMatchesItsFile(unittest.TestCase):
    """`raw_lines` is the file's slice, so a docstring compares to itself.

    !! Measured 2026-08-17 before the census fix: on `galley.py`'s own census,
    all six docstring blocks answered False against an UNMODIFIED file and all
    five comment blocks answered True. A docstring edit could not be spliced at
    all, which blocked every re-review whose block was a docstring.
    """

    SOURCE = '''def f():
    """One line.

    More prose.
    """
    return 1
'''

    def _census(self):
        import census

        return [b.__dict__ for b in census.blocks_stdlib(Path("m.py"), self.SOURCE)]

    def test_the_docstring_block_matches_the_source_it_came_from(self):
        blocks = [b for b in self._census() if b["kind"] == "docstring"]
        self.assertEqual(len(blocks), 1)
        self.assertTrue(galley.block_matches(self.SOURCE.splitlines(), blocks[0]))

    def test_raw_lines_carries_the_delimiters(self):
        # ! The AST value has neither the opening `"""` nor its indent.
        block = next(b for b in self._census() if b["kind"] == "docstring")
        self.assertTrue(block["raw_lines"][0].lstrip().startswith('"""'))
        self.assertTrue(block["raw_lines"][-1].strip().endswith('"""'))

    def test_lines_agrees_with_raw_lines(self):
        # ! They disagreed by one on every multi-line docstring: the AST value
        # has no closing-delimiter line.
        block = next(b for b in self._census() if b["kind"] == "docstring")
        self.assertEqual(block["lines"], len(block["raw_lines"]))

    def test_an_EDITED_docstring_is_stale(self):
        block = next(b for b in self._census() if b["kind"] == "docstring")
        edited = self.SOURCE.replace("More prose.", "Different prose.")
        self.assertFalse(galley.block_matches(edited.splitlines(), block))


# !! LAST LINE, ALWAYS. A runner placed above a class runs before that class
# exists, so `python tests/<file>.py` reports a green bar over a shorter suite
# than `unittest discover`.
if __name__ == "__main__":
    unittest.main()
