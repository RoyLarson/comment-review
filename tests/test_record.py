"""The seeded record: what the tool fills, and what it leaves for the reviewer."""

import json  # noqa: I001  -- path shim below must import before record
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from _paths import SCRIPTS  # noqa: F401
import record

CENSUS = [
    {
        "path": "pkg/m.py",
        "start": 1,
        "end": 3,
        "kind": "docstring",
        "raw_lines": ["Summary.", "", "Args:"],
    },
    {"path": "pkg/m.py", "start": 4, "end": 4, "kind": "interval", "raw_lines": []},
    {
        "path": "pkg/m.py",
        "start": 5,
        "end": 5,
        "kind": "comment",
        "raw_lines": ["# a note"],
    },
]


class TestOnlyProseGetsASlot(unittest.TestCase):
    def test_intervals_are_skipped(self):
        self.assertEqual([i for i, _ in record.prose_blocks(CENSUS)], [1, 3])

    def test_a_census_of_only_intervals_seeds_nothing(self):
        only = [{"path": "a.py", "start": 1, "end": 1, "kind": "interval"}]
        self.assertEqual(record.seed(only, "block-context")["records"], [])

    def test_the_index_is_the_CENSUS_index_not_the_slot_number(self):
        # !! The second prose block is census index 3, not 2. The index IS the
        # block's identity, and renumbering it would make every citation wrong.
        self.assertEqual(record.seed(CENSUS, "x")["records"][1]["block"], 3)


class TestWhatTheToolFills(unittest.TestCase):
    def setUp(self):
        self.records = record.seed(CENSUS, "block-context")["records"]

    def test_the_address_is_built_from_the_census(self):
        self.assertEqual(self.records[0]["address"], "pkg/m.py:1-3")

    def test_the_original_is_a_LINE_ARRAY(self):
        self.assertEqual(self.records[0]["original"], ["Summary.", "", "Args:"])

    def test_a_blank_line_inside_a_block_survives(self):
        # !! The defect this shape makes impossible. A blank line ending a field
        # was 0.2.0's worst: it truncated BLOCK and CHANGE to their first
        # paragraph and refused 113 of one reviewer's 134 correct findings.
        self.assertIn("", self.records[0]["original"])

    def test_every_seeded_field_is_present(self):
        for field in record.SEEDED:
            with self.subTest(field=field):
                self.assertIn(field, self.records[0])


class TestWhatTheReviewerFills(unittest.TestCase):
    def setUp(self):
        self.records = record.seed(CENSUS, "block-context")["records"]

    def test_the_verdict_is_NULL_not_empty(self):
        # ! An unruled block must be distinguishable from one ruled with an
        # empty verdict. Only the first is a coverage gap.
        self.assertIsNone(self.records[0]["verdict"])

    def test_the_answered_fields_are_present_and_empty(self):
        empty = {"claim": {}, "reason": "", "sources": [], "change": []}
        for field, value in empty.items():
            with self.subTest(field=field):
                self.assertEqual(self.records[0][field], value)

    def test_every_answered_field_is_present(self):
        for field in record.ANSWERED:
            with self.subTest(field=field):
                self.assertIn(field, self.records[0])

    def test_code_concerns_is_a_list_not_a_section(self):
        # ! One more boundary that cannot be guessed wrong: it was a markdown
        # heading found with a regex.
        self.assertEqual(record.seed(CENSUS, "x")["code_concerns"], [])


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.census = self.root / "census.json"
        self.census.write_text(json.dumps(CENSUS), encoding="utf-8")
        self.out = self.root / "nested" / "block-context.json"

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, *extra):
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "record.py"),
                "--census",
                str(self.census),
                "--reviewer",
                "block-context",
                "--out",
                str(self.out),
                *extra,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

    def test_it_writes_a_file_and_makes_its_directory(self):
        result = self._run("--seed")
        self.assertEqual(result.returncode, 0, result.stdout)
        written = json.loads(self.out.read_text(encoding="utf-8"))
        self.assertEqual(len(written["records"]), 2)
        self.assertEqual(written["reviewer"], "block-context")

    def test_it_round_trips_as_json(self):
        self._run("--seed")
        # ! The point of the format: reading it back needs no parser of ours.
        self.assertIsInstance(json.loads(self.out.read_text(encoding="utf-8")), dict)

    def test_without_seed_it_does_nothing(self):
        self.assertEqual(self._run().returncode, 2)
        self.assertFalse(self.out.exists())

    def test_an_unreadable_census_is_refused(self):
        self.census.write_text("not json at all", encoding="utf-8")
        result = self._run("--seed")
        self.assertEqual(result.returncode, 2)
        self.assertIn("CANNOT PARSE", result.stdout)


# !! LAST LINE, ALWAYS. A runner placed above a class runs before that class
# exists, so `python tests/<file>.py` reports a green bar over a shorter suite
# than `unittest discover`.
if __name__ == "__main__":
    unittest.main()
