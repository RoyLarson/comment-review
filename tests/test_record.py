"""The seeded record: what the tool fills, and what it leaves for the reviewer."""

import json  # noqa: I001  -- path shim below must import before record
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from _paths import SCRIPTS  # noqa: F401
import record
import verdicts

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

    def test_the_record_does_NOT_carry_the_block_text(self):
        """!! The reviewer is told WHERE, not WHAT, and that is deliberate.

        A record carrying the prose lets a reviewer produce a complete,
        admissible ruling without opening the file, and nothing in the gate can
        tell that from real work. Every role's remit requires the read.

        !! The two errors are not symmetric, which is what decided it. Reading
        the wrong lines makes `CLAIM` quote a sentence the census block does not
        contain, and `block_problem` already catches that. Ruling from the
        record instead of the code is invisible. ! Re-check that asymmetry
        before reversing this; it has flipped three times.
        """
        self.assertNotIn("original", self.records[0])

    def test_every_seeded_field_is_present(self):
        for field in record.SEEDED:
            with self.subTest(field=field):
                self.assertIn(field, self.records[0])

    def test_only_the_index_and_the_address_are_seeded(self):
        self.assertEqual(record.SEEDED, ("block", "address"))


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


class TestTheTemplateStatesWhatIsAllowed(unittest.TestCase):
    """A constrained field that does not say its values has only moved the guessing.

    !! Every value here is DERIVED from the `Verdict` table, so adding a verdict
    stays a ROW and this block cannot drift from what the gate enforces. These
    tests pin the correspondence, not the current contents.
    """

    def setUp(self):
        self.allowed = record.allowed()

    def test_every_verdict_the_gate_knows_is_offered(self):
        self.assertEqual(set(self.allowed["verdict"]), set(verdicts.VERDICTS))

    def test_a_claim_key_is_the_gates_marker_without_its_colon(self):
        for name, spec in verdicts.VERDICTS.items():
            for marker in spec.claim_all:
                with self.subTest(verdict=name, marker=marker):
                    self.assertIn(marker.rstrip(":"), self.allowed["claim"][name])

    def test_clean_is_offered_no_claim_keys(self):
        self.assertEqual(self.allowed["claim"]["clean"], [])

    def test_query_is_told_its_three_shapes(self):
        self.assertEqual(self.allowed["values"]["shape"], list(verdicts.QUERY_SHAPES))
        self.assertIn("shape", self.allowed["claim"]["query"])

    def test_query_is_told_it_owes_attempted_and_settles(self):
        # ! Both are `needs_` flags on the table, not markers, so they would be
        # invisible to a reviewer that only saw the claim markers.
        self.assertIn("attempted", self.allowed["claim"]["query"])
        self.assertIn("settles", self.allowed["claim"]["query"])

    def test_add_is_told_it_owes_an_anchor_and_a_side(self):
        self.assertIn("anchor", self.allowed["claim"]["add"])
        self.assertIn("side", self.allowed["claim"]["add"])
        self.assertEqual(self.allowed["values"]["side"], ["above", "below"])

    def test_the_boundary_shape_is_named(self):
        # ! One of the three query shapes is a scope report rather than work,
        # and a reader of the file alone cannot tell which.
        self.assertEqual(self.allowed["scope_shape"], verdicts.OUT_OF_ROLE)
        self.assertIn(self.allowed["scope_shape"], self.allowed["values"]["shape"])

    def test_the_seeded_file_carries_it_before_the_records(self):
        keys = list(record.seed(CENSUS, "x"))
        self.assertLess(keys.index("allowed"), keys.index("records"))


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
