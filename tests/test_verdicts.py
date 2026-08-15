"""The census join, the evidence check, and the clean arithmetic — mechanically."""

import tempfile  # noqa: I001  -- path shim below must import before verdicts
import unittest
from pathlib import Path

from _paths import FIXTURES  # noqa: F401
import verdicts

REPORT = """
Some preamble the tool ignores.

--- FINDING
BLOCK       1
VERDICT     correct
LOCATION    a.py:1-2
EVIDENCE    a.py:5
SUMMARY     "only one caller" || three callers here
FINDING     the count is wrong
CHANGE      false: "only one caller" / true: "three callers"
---

CLEAN 2-3
"""


class TestParsing(unittest.TestCase):
    def test_a_record_is_parsed(self):
        found, clean = verdicts.parse_report(REPORT, "currency")
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].block, 1)
        self.assertEqual(found[0].verdict, "correct")
        self.assertEqual(found[0].evidence, "a.py:5")

    def test_clean_ranges_expand(self):
        _, clean = verdicts.parse_report(REPORT, "currency")
        self.assertEqual(clean, {2, 3})

    def test_the_angle_is_attached(self):
        found, _ = verdicts.parse_report(REPORT, "currency")
        self.assertEqual(found[0].angle, "currency")


class TestCoverage(unittest.TestCase):
    def test_an_unaccounted_block_is_a_gap(self):
        gaps = verdicts.coverage_gaps(
            {1, 2, 3, 4},
            {"currency": {2, 3}},
            [
                verdicts.Finding(
                    "currency", 1, "correct", "a.py:1-2", "a.py:5", "x", "y", "z"
                )
            ],
        )
        self.assertEqual(gaps, {"currency": [4]})

    def test_full_coverage_reports_no_gap(self):
        gaps = verdicts.coverage_gaps(
            {1, 2},
            {"currency": {2}},
            [verdicts.Finding("currency", 1, "clean", "", "", "", "", "")],
        )
        self.assertEqual(gaps, {})


class TestPayload(unittest.TestCase):
    def test_correct_without_a_pair_is_rejected(self):
        f = verdicts.Finding(
            "currency", 1, "correct", "a.py:1", "a.py:5", "s", "f", "fix it"
        )
        self.assertIn("true/false pair", verdicts.payload_problem(f))

    def test_correct_with_a_pair_passes(self):
        f = verdicts.Finding(
            "currency",
            1,
            "correct",
            "a.py:1",
            "a.py:5",
            "s",
            "f",
            'false: "a" / true: "b"',
        )
        self.assertIsNone(verdicts.payload_problem(f))

    def test_add_without_an_anchor_is_rejected(self):
        f = verdicts.Finding(
            "locality", 1, "add", "a.py:1", "a.py:5", "s", "f", "some text"
        )
        self.assertIn("anchor", verdicts.payload_problem(f))


class TestLevel(unittest.TestCase):
    def test_patch_is_illegal_at_fact_check(self):
        self.assertFalse(verdicts.allowed("patch", "fact-check"))

    def test_correct_is_legal_at_every_level(self):
        for level in ("fact-check", "line", "full"):
            self.assertTrue(verdicts.allowed("correct", level))

    def test_reanchor_needs_line(self):
        self.assertFalse(verdicts.allowed("reanchor", "fact-check"))
        self.assertTrue(verdicts.allowed("reanchor", "line"))


class TestContradiction(unittest.TestCase):
    def test_drop_against_correct_is_flagged(self):
        found = [
            verdicts.Finding("locality", 7, "drop", "a.py:1", "a.py:5", "s", "f", "c"),
            verdicts.Finding(
                "currency", 7, "correct", "a.py:1", "a.py:5", "s", "f", "c"
            ),
        ]
        self.assertEqual(verdicts.contradictions(found), [7])

    def test_drop_alone_is_not_a_contradiction(self):
        found = [
            verdicts.Finding("locality", 7, "drop", "a.py:1", "a.py:5", "s", "f", "c")
        ]
        self.assertEqual(verdicts.contradictions(found), [])


class TestEvidence(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        (self.repo / "a.py").write_text(
            "one\ntwo\nthree\nfour\nthe settling line\nsix\n"
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_a_resolvable_citation_passes(self):
        f = verdicts.Finding(
            "currency",
            1,
            "correct",
            "a.py:1",
            "a.py:5",
            "x || the settling line",
            "f",
            "c",
        )
        self.assertIsNone(verdicts.evidence_problem(f, self.repo))

    def test_a_missing_file_is_caught(self):
        f = verdicts.Finding(
            "currency", 1, "correct", "a.py:1", "gone.py:5", "x || y", "f", "c"
        )
        self.assertIn("does not resolve", verdicts.evidence_problem(f, self.repo))

    def test_a_line_past_the_end_is_caught(self):
        f = verdicts.Finding(
            "currency", 1, "correct", "a.py:1", "a.py:900", "x || y", "f", "c"
        )
        self.assertIn("900", verdicts.evidence_problem(f, self.repo))

    def test_a_quote_that_is_not_there_is_caught(self):
        f = verdicts.Finding(
            "currency",
            1,
            "correct",
            "a.py:1",
            "a.py:5",
            "x || a line that appears nowhere at all",
            "f",
            "c",
        )
        self.assertIn("not found near", verdicts.evidence_problem(f, self.repo))


if __name__ == "__main__":
    unittest.main()
