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


# !! LAST LINE, ALWAYS. A runner placed above a class runs before that class
# exists, so `python tests/<file>.py` reports a green bar over a shorter suite
# than `unittest discover`.
if __name__ == "__main__":
    unittest.main()
