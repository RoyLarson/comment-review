"""The census join, the evidence check, and the clean arithmetic — mechanically."""

import json  # noqa: I001  -- path shim below must import before verdicts
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from _paths import FIXTURES, SCRIPTS  # noqa: F401
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

    def test_a_wrapped_clean_line_does_not_merge_across_lines(self):
        # C1: `\s` inside CLEAN_LINE's class let a stray continuation line glue
        # onto the range, turning "CLEAN 1-9" + a stray "50" into "1-950".
        text = "CLEAN 1-9\n50\n"
        _, clean = verdicts.parse_report(text, "module-coherence")
        self.assertEqual(clean, {1, 2, 3, 4, 5, 6, 7, 8, 9})

    def test_a_bad_clean_range_becomes_a_malformed_finding_not_a_silent_drop(self):
        # C1: an unparseable CLEAN part must be REPORTED, not dropped -- a range
        # list that doesn't parse is a malformed record, not an empty one.
        text = "CLEAN 9-2\n"
        found, clean = verdicts.parse_report(text, "currency")
        self.assertEqual(clean, set())
        self.assertEqual(len(found), 1)
        self.assertLess(found[0].block, 0)
        self.assertIn("9-2", found[0].finding)

    def test_a_zero_index_in_clean_is_rejected_not_admitted(self):
        text = "CLEAN 0-3\n"
        _, clean = verdicts.parse_report(text, "currency")
        self.assertNotIn(0, clean)

    def test_an_unterminated_record_is_flagged_not_silently_merged(self):
        # I4: two records, the first missing its closing "---", must not merge
        # into one record carrying only the second's fields.
        text = """
--- FINDING
BLOCK       1
VERDICT     correct
LOCATION    a.py:1
EVIDENCE    a.py:1
SUMMARY     "x" || y
FINDING     first record, never closed

--- FINDING
BLOCK       2
VERDICT     correct
LOCATION    a.py:1
EVIDENCE    a.py:1
SUMMARY     "x" || y
FINDING     second record, closed
CHANGE      false: "x" / true: "y"
---
"""
        found, _ = verdicts.parse_report(text, "currency")
        malformed = [f for f in found if f.block < 0]
        self.assertTrue(
            malformed, "an opener/closer mismatch must produce a malformed finding"
        )


class TestExpand(unittest.TestCase):
    """`_expand` must REPORT what it cannot parse, never drop it silently."""

    def test_a_reversed_range_is_reported_bad(self):
        expanded, bad = verdicts._expand("9-2")
        self.assertEqual(expanded, set())
        self.assertIn("9-2", bad)

    def test_a_wildly_reversed_range_is_reported_bad(self):
        expanded, bad = verdicts._expand("1820-45")
        self.assertEqual(expanded, set())
        self.assertIn("1820-45", bad)

    def test_a_zero_start_is_reported_bad(self):
        expanded, bad = verdicts._expand("0-3")
        self.assertNotIn(0, expanded)
        self.assertIn("0-3", bad)

    def test_a_valid_range_is_not_reported_bad(self):
        expanded, bad = verdicts._expand("1-3,7")
        self.assertEqual(expanded, {1, 2, 3, 7})
        self.assertEqual(bad, [])


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

    def test_a_malformed_block_is_never_reported_as_a_contradiction(self):
        # Minor: a -1 sentinel (a malformed record) must not surface as
        # "RE-REVIEW [-1]" -- it names no real block.
        found = [
            verdicts.Finding("locality", -1, "drop", "", "", "", "", ""),
            verdicts.Finding("currency", -1, "correct", "", "", "", "", ""),
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

    def test_a_one_character_needle_is_rejected(self):
        # C3: `head = needle[:40]` had no minimum, so SUMMARY "... || e" passed
        # against nearly any file -- defeating the one mechanical defence
        # against a fabricated report.
        f = verdicts.Finding(
            "currency", 1, "correct", "a.py:1", "a.py:5", "x || e", "f", "c"
        )
        problem = verdicts.evidence_problem(f, self.repo)
        self.assertIsNotNone(problem)
        self.assertIn("too short", problem)

    def test_evidence_line_zero_is_rejected(self):
        f = verdicts.Finding(
            "currency", 1, "correct", "a.py:1", "a.py:0", "x || y" * 5, "f", "c"
        )
        self.assertIsNotNone(verdicts.evidence_problem(f, self.repo))

    def test_a_fabricated_location_is_caught(self):
        # A prose LOCATION must be checked with the same machinery as
        # EVIDENCE -- a fabricated location was admissible before this fix.
        f = verdicts.Finding(
            "currency",
            1,
            "correct",
            "gone.py:1",
            "a.py:5",
            "x || the settling line",
            "f",
            "c",
        )
        problem = verdicts.location_problem(f, self.repo)
        self.assertIsNotNone(problem)
        self.assertIn("does not resolve", problem)

    def test_a_resolvable_location_passes(self):
        f = verdicts.Finding(
            "currency",
            1,
            "correct",
            "a.py:1-2",
            "a.py:5",
            "x || the settling line",
            "f",
            "c",
        )
        self.assertIsNone(verdicts.location_problem(f, self.repo))


class TestCLI(unittest.TestCase):
    """`main()` end to end -- the gate must actually gate on exit code."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        (self.repo / "a.py").write_text(
            "one\ntwo\nthree\nfour\nfive callers, all in tests\nsix\n",
            encoding="utf-8",
        )
        self.census = Path(self.tmp.name) / "census.json"
        self.census.write_text(
            json.dumps(
                [
                    {"path": "a.py", "start": 1, "end": 2},
                    {"path": "a.py", "start": 3, "end": 4},
                    {"path": "a.py", "start": 5, "end": 6},
                ]
            ),
            encoding="utf-8",
        )

    def tearDown(self):
        self.tmp.cleanup()

    def _write(self, name, text):
        path = Path(self.tmp.name) / name
        path.write_text(text, encoding="utf-8")
        return path

    def _run(self, *reports, level="full", angles=None):
        cmd = [
            sys.executable,
            str(SCRIPTS / "verdicts.py"),
            "--census",
            str(self.census),
            "--level",
            level,
            "--repo",
            str(self.repo),
        ]
        if angles is not None:
            cmd += ["--angles", angles]
        cmd += [str(r) for r in reports]
        return subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8", check=False
        )

    def _clean_report(self, name):
        return self._write(name, "CLEAN 1-3\n")

    def test_full_coverage_exits_zero(self):
        report = self._clean_report("currency.txt")
        result = self._run(report)
        self.assertEqual(result.returncode, 0)
        self.assertIn("STANDS UNCHANGED: 3 blocks", result.stdout)
        self.assertIn("NEEDS A RULING:   0 blocks", result.stdout)

    def test_a_missing_payload_is_fatal(self):
        # C2: a payload problem must not print and then exit 0.
        report = self._write(
            "currency.txt",
            "--- FINDING\n"
            "BLOCK       1\n"
            "VERDICT     drop\n"
            "LOCATION    a.py:1\n"
            "EVIDENCE    a.py:5\n"
            'SUMMARY     "x" || five callers, all in tests\n'
            "FINDING     f\n"
            "CHANGE      \n"
            "---\n"
            "CLEAN 2-3\n",
        )
        result = self._run(report)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no payload", result.stdout)
        self.assertNotIn("Every finding is admissible", result.stdout)

    def test_an_out_of_range_block_is_fatal(self):
        report = self._write(
            "currency.txt",
            "--- FINDING\n"
            "BLOCK       999\n"
            "VERDICT     query\n"
            "LOCATION    a.py:1\n"
            "EVIDENCE    a.py:5\n"
            'SUMMARY     "x" || five callers, all in tests\n'
            "FINDING     f\n"
            "CHANGE      what would settle it\n"
            "---\n"
            "CLEAN 1-3\n",
        )
        result = self._run(report)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("out of range", result.stdout)

    def test_a_wrapped_clean_line_is_a_gap_not_a_pass(self):
        # C1, end to end: a stray continuation line after CLEAN must produce a
        # loud coverage gap on block 3, never a silent "everything is clean".
        report = self._write("currency.txt", "CLEAN 1-2\n900\n")
        result = self._run(report)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("COVERAGE GAPS", result.stdout)
        self.assertIn("currency: 1 block unaccounted", result.stdout)

    def test_a_missing_angle_is_fatal_when_declared(self):
        report = self._clean_report("currency.txt")
        result = self._run(report, angles="currency,locality")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("locality", result.stdout)

    def test_angle_absence_is_declared_not_inferred_when_undeclared(self):
        report = self._clean_report("currency.txt")
        result = self._run(report)
        self.assertEqual(result.returncode, 0)
        self.assertIn("NOT checked", result.stdout)

    def test_duplicate_report_stems_are_refused(self):
        sub = Path(self.tmp.name) / "dup"
        sub.mkdir()
        one = sub / "currency.txt"
        one.write_text("CLEAN 1-3\n", encoding="utf-8")
        two = self._write("currency.txt", "CLEAN 1-3\n")
        result = self._run(one, two)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("DUPLICATE", result.stdout)

    def test_a_missing_report_file_prints_one_line_not_a_traceback(self):
        result = self._run(Path(self.tmp.name) / "nope.txt")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Traceback", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_pluralisation_of_a_single_angle_and_block(self):
        report = self._write(
            "currency.txt",
            "--- FINDING\n"
            "BLOCK       1\n"
            "VERDICT     query\n"
            "LOCATION    a.py:1\n"
            "EVIDENCE    a.py:5\n"
            'SUMMARY     "x" || five callers, all in tests\n'
            "FINDING     f\n"
            "CHANGE      what would settle it\n"
            "---\n"
            "CLEAN 2-3\n",
        )
        result = self._run(report)
        self.assertNotIn("1 angles", result.stdout)
        self.assertNotIn("1 blocks", result.stdout)


if __name__ == "__main__":
    unittest.main()
