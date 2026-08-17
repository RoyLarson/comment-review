"""The census join, the evidence check, and the clean arithmetic — mechanically."""

import json  # noqa: I001  -- path shim below must import before verdicts
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from _paths import FIXTURES, SCRIPTS  # noqa: F401
import verdicts

BRIEF = (
    Path(verdicts.__file__).resolve().parent.parent / "references" / "reviewer-brief.md"
)

REPORT = """
Some preamble the tool ignores.

--- RECORD
BLOCK       1
VERDICT     correct
LOCATION    a.py:1-2
EVIDENCE    a.py:5
QUOTE       the settling line
SUMMARY     "only one caller" || three callers here
FINDING     the count is wrong
CHANGE      false: "only one caller" / true: "three callers"
---

--- RECORD
BLOCK       2
VERDICT     clean
LOCATION    a.py:10-11
FINDING     nothing to report from this role
---
"""


def _clean_records(*blocks: int) -> str:
    """One `clean` RECORD per block. There is no range list to write instead."""
    return "".join(
        "--- RECORD\n"
        f"BLOCK       {n}\n"
        "VERDICT     clean\n"
        "LOCATION    a.py:1\n"
        "FINDING     nothing to report from this role\n"
        "---\n"
        for n in blocks
    )


_CLEAN_RECORDS = _clean_records(1, 2, 3)
_CLEAN_RECORDS_23 = _clean_records(2, 3)


def _finding(**kw):
    """A Finding whose required fields are filled, overridden per test.

    Constructing these POSITIONALLY is what made adding one field to the
    record a twenty-site edit; the record grew a `QUOTE` field and its own
    checker never ran against it. A field added to the record should cost one
    line here.
    """
    fields = {
        "reviewer": "block-context",
        "block": 1,
        "verdict": "correct",
        "location": "a.py:1",
        "evidence": "a.py:5",
        "quote": "the settling line",
        "summary": '"x" || three callers, all under tests/',
        "finding": "f",
        "change": 'false: "a" / true: "b"',
    }
    fields.update(kw)
    return verdicts.Finding(**fields)


class TestParsing(unittest.TestCase):
    def test_a_record_is_parsed(self):
        found, _ = verdicts.parse_report(REPORT, "block-context")
        self.assertEqual(len(found), 2)
        self.assertEqual(found[0].block, 1)
        self.assertEqual(found[0].verdict, "correct")
        self.assertEqual(found[0].evidence, "a.py:5")
        self.assertEqual(found[0].quote, "the settling line")

    def test_a_clean_record_parses_like_any_other(self):
        found, _ = verdicts.parse_report(REPORT, "block-context")
        self.assertEqual(found[1].verdict, "clean")
        self.assertEqual(found[1].block, 2)

    def test_the_reviewer_is_attached(self):
        found, _ = verdicts.parse_report(REPORT, "block-context")
        self.assertEqual(found[0].reviewer, "block-context")

    def test_a_bare_range_line_accounts_for_nothing(self):
        # A range list used to cover N blocks in one line and cite nothing. It is
        # not a record, so it parses to no findings and every block it named is a
        # coverage gap.
        found, malformed = verdicts.parse_report("CLEAN 1-9\n", "module-context")
        self.assertEqual(found, [])
        self.assertEqual(malformed, [])

    def test_an_unterminated_record_is_flagged_not_silently_merged(self):
        # I4: two records, the first missing its closing "---", must not merge
        # into one record carrying only the second's fields.
        text = """
--- RECORD
BLOCK       1
VERDICT     correct
LOCATION    a.py:1
EVIDENCE    a.py:1
SUMMARY     "x" || y
FINDING     first record, never closed

--- RECORD
BLOCK       2
VERDICT     correct
LOCATION    a.py:1
EVIDENCE    a.py:1
SUMMARY     "x" || y
FINDING     second record, closed
CHANGE      false: "x" / true: "y"
---
"""
        found, malformed = verdicts.parse_report(text, "block-context")
        self.assertTrue(
            malformed, "an opener/closer mismatch must be reported as malformed"
        )
        self.assertTrue(
            all(f.block > 0 for f in found),
            "a malformed record must not enter the findings at all",
        )


class TestCoverage(unittest.TestCase):
    def test_an_unaccounted_block_is_a_gap(self):
        gaps = verdicts.coverage_gaps(
            {1, 2, 3, 4},
            {"block-context"},
            [_finding(block=n) for n in (1, 2, 3)],
        )
        self.assertEqual(gaps, {"block-context": [4]})

    def test_full_coverage_reports_no_gap(self):
        gaps = verdicts.coverage_gaps(
            {1, 2},
            {"block-context"},
            [_finding(block=1), _finding(block=2, verdict="clean")],
        )
        self.assertEqual(gaps, {})

    def test_a_report_that_parsed_to_nothing_is_every_block_missing(self):
        """A reviewer that handed in a file and recorded nothing must not vanish
        by having no findings for the population to be taken from."""
        gaps = verdicts.coverage_gaps({1, 2}, {"module-context"}, [])
        self.assertEqual(gaps, {"module-context": [1, 2]})


class TestPayload(unittest.TestCase):
    def test_correct_without_a_pair_is_rejected(self):
        f = _finding(change="fix it")
        self.assertIn("true/false pair", verdicts.payload_problem(f))

    def test_correct_with_a_pair_passes(self):
        self.assertIsNone(verdicts.payload_problem(_finding()))

    def test_add_without_an_anchor_is_rejected(self):
        f = _finding(reviewer="ownership-context", verdict="add", change="some text")
        self.assertIn("side", verdicts.payload_problem(f))

    def test_a_verdict_that_states_no_finding_is_rejected(self):
        # FINDING went unchecked while it doubled as the diagnostic slot for a
        # malformed record. It holds one thing now, so it can be required.
        self.assertIn("FINDING", verdicts.payload_problem(_finding(finding="  ")))

    def test_clean_owes_no_finding(self):
        f = _finding(verdict="clean", finding="", change="")
        self.assertIsNone(verdicts.payload_problem(f))


class TestAddAnchor(unittest.TestCase):
    """The brief asks for "the text AND its anchor — which code, above or below".

    That is a NAMED site and a side. The check accepted the bare WORD "anchor"
    instead, so a finding that never named a declaration passed and one that
    named a declaration without using the word failed.
    """

    def _add(self, change):
        return verdicts.payload_problem(
            _finding(reviewer="ownership-context", verdict="add", change=change)
        )

    def test_the_bare_word_anchor_no_longer_passes(self):
        self.assertIsNotNone(self._add("add an anchor comment here"))

    def test_a_side_with_no_named_anchor_is_rejected(self):
        self.assertIn("backticks", self._add("put it above the loop"))

    def test_a_named_anchor_with_no_side_is_rejected(self):
        self.assertIn("side", self._add("goes with `retry_budget`"))

    def test_a_named_anchor_and_a_side_passes(self):
        self.assertIsNone(self._add("above `retry_budget`: the ceiling is 100"))

    def test_before_and_after_count_as_sides(self):
        for side in ("before", "after"):
            self.assertIsNone(self._add(f"{side} `send()`: retries are capped"), side)


class TestQueryPayload(unittest.TestCase):
    """C3: `query` has no EVIDENCE to check, so its PAYLOAD is the gate.

    A query that names no attempted check is the one that hands the judgement
    back, and it is the one this refuses.
    """

    QUERY = (
        "outside the checkout. claim: the archive holds the original"
        " / checked: git ls-files, git log -- archive/"
        " / would settle: a copy of the archive inside the checkout"
    )

    def test_a_documented_query_passes(self):
        f = _finding(verdict="query", change=self.QUERY)
        self.assertIsNone(verdicts.payload_problem(f))

    def test_a_query_naming_no_attempted_check_is_rejected(self):
        f = _finding(
            verdict="query",
            change="outside the code. claim: unclear. someone should settle this",
        )
        self.assertIn("ATTEMPTED", verdicts.payload_problem(f))

    def test_the_attempted_vocabulary_covers_the_verbs_reviewers_are_given(self):
        # A run refused 65 of 65 module-context queries reading "resolved the
        # enclosing definition at ..." -- `resolve` was in QUERY_SETTLES and
        # missing from ATTEMPTED. The list is derived from the brief and the
        # agent files, so a reviewer using the word it was taught passes.
        for verb in ("resolved", "enumerated", "verified", "traced", "compared"):
            f = _finding(
                verdict="query",
                change=(
                    f"outside the code. claim: x / {verb} the enclosing definition"
                    " / would settle: another role"
                ),
            )
            self.assertIsNone(verdicts.payload_problem(f), verb)

    def test_a_query_that_does_not_say_what_would_settle_it_is_rejected(self):
        f = _finding(
            verdict="query",
            change=(
                "outside the code. claim: the archive holds it / checked: git ls-files"
            ),
        )
        self.assertIn("WOULD settle", verdicts.payload_problem(f))


class TestQueryWordBoundary(unittest.TestCase):
    """The fix-round regression: `QUERY_ATTEMPTED`/`QUERY_SETTLES` matched as
    plain substrings, so "ran" hit *b**ran**ch*, *****ran***ge*, *t**ran**sfer*
    and "settle" hit *un**settle**d* -- ordinary English that names no check at
    all was ADMITTED, while an honest query worded with "requires" instead of
    "would ..." was wrongly REJECTED. Word-boundary matching must invert both.
    """

    def test_an_unsettled_branch_name_names_no_check_and_is_rejected(self):
        f = _finding(
            verdict="query",
            change="outside the code. the branch name is unsettled",
        )
        self.assertIn("ATTEMPTED", verdicts.payload_problem(f))

    def test_a_range_of_values_names_no_check_and_is_rejected(self):
        f = _finding(
            verdict="query",
            change="outside the code. a range of values, unsettled",
        )
        self.assertIn("ATTEMPTED", verdicts.payload_problem(f))

    def test_transfer_semantics_names_no_check_and_is_rejected(self):
        f = _finding(
            verdict="query",
            change="outside the code. transfer semantics unsettled",
        )
        self.assertIn("ATTEMPTED", verdicts.payload_problem(f))

    def test_an_honest_query_worded_with_requires_is_admitted(self):
        f = _finding(
            verdict="query",
            change=(
                "outside the code. claim: the cap is 6."
                " attempted: ripgrep over src/ for CAP."
                " resolving it requires the deploy config"
            ),
        )
        self.assertIsNone(verdicts.payload_problem(f))

    def test_ripgrep_counts_as_an_attempted_check_though_grep_is_not_at_a_word_start(
        self,
    ):
        f = _finding(
            verdict="query",
            change=(
                "outside the code. claim: x / attempted: ripgrep -n TODO src/"
                " / would confirm nothing found"
            ),
        )
        self.assertIsNone(verdicts.payload_problem(f))

    def test_looked_at_the_file_counts_as_an_attempted_check(self):
        # A one-character typo (\block\w* for \blook\w*) shipped in the same
        # commit that fixed the substring bug, and made this exact wording
        # reject: 'look'/'looked'/'looking' never matched, and 'locked' -- a
        # word that names no check at all -- matched by accident instead.
        f = _finding(
            verdict="query",
            change=(
                "outside the code. claim: the timeout is 30s."
                " I looked at config.py and found"
                " nothing definitive, would need the deploy config to be sure"
            ),
        )
        self.assertIsNone(verdicts.payload_problem(f))

    def test_looking_up_the_constant_counts_as_an_attempted_check(self):
        f = _finding(
            verdict="query",
            change=(
                "outside the code. claim: x / looking up the constant"
                " in config.py turned up"
                " nothing / would need the deploy config to settle it"
            ),
        )
        self.assertIsNone(verdicts.payload_problem(f))

    def test_locked_names_no_check_and_is_rejected(self):
        # The typo's failure mode in the OTHER direction: \block\w* matched
        # "locked", a word that names no attempted check at all -- the exact
        # shape this whole check exists to refuse.
        f = _finding(
            verdict="query",
            change=(
                "outside the code. claim: x / locked the file"
                " / would need a second opinion"
            ),
        )
        self.assertIn("ATTEMPTED", verdicts.payload_problem(f))


class TestScopeDeclaration(unittest.TestCase):
    """`query — outside my role` is a boundary report, not work.

    Measured: a run reported 1159 blocks needing a ruling when 76 carried a
    substantive verdict. The other 1083 were out-of-role queries, which
    module-context is instructed to return on every block it does not own.
    """

    def _q(self, change):
        return _finding(verdict="query", evidence="", quote="", change=change)

    def test_an_out_of_role_query_declares_scope(self):
        f = self._q("claim: x / outside my role, resolved the enclosing def")
        self.assertTrue(verdicts.declares_scope(f))

    def test_the_other_two_query_shapes_are_still_work(self):
        # The brief names three shapes. Only the first is a non-ruling; these
        # two reach the AUTHOR and must stay in the work list.
        for change in (
            "claim: x / checked the checkout / outside the checkout, it is gitignored",
            "claim: x / read the module / outside the code, needs someone who ran it",
        ):
            self.assertFalse(verdicts.declares_scope(self._q(change)), change)

    def test_a_substantive_verdict_never_declares_scope(self):
        self.assertFalse(verdicts.declares_scope(_finding(verdict="correct")))


class TestCodeConcerns(unittest.TestCase):
    """Carried, never gated. A reviewer WILL find code defects while opening the
    code to settle a comment, and the brief gives them a place -- but nothing read
    that place, so a reviewer following the rule was less visible than one
    breaking it."""

    REPORT = """--- RECORD
BLOCK       1
VERDICT     clean
LOCATION    a.py:1
FINDING     nothing to report from this role
---

## CODE CONCERNS

- `complete --outcome "a | b"` writes a malformed row
- `_ROW_FULL` accepts a row with no trailing pipe
"""

    def test_the_lines_are_carried(self):
        self.assertEqual(len(verdicts.code_concerns(self.REPORT)), 2)
        self.assertIn("malformed row", verdicts.code_concerns(self.REPORT)[0])

    def test_a_report_without_the_section_carries_none(self):
        self.assertEqual(verdicts.code_concerns(_clean_records(1)), [])

    def test_they_are_not_findings(self):
        # They carry no verdict, so they must never reach the record parser --
        # a code concern counted as a finding would enter coverage arithmetic.
        found, _ = verdicts.parse_report(self.REPORT, "block-context")
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].verdict, "clean")


class TestWorkList(unittest.TestCase):
    """The grouping stage 5 works from, and when it is withheld."""

    def test_it_groups_every_finding_by_block(self):
        found = [
            _finding(reviewer="block-context", block=7, verdict="correct"),
            _finding(reviewer="ownership-context", block=7, verdict="move"),
            _finding(reviewer="module-context", block=9, verdict="drop"),
        ]
        grouped = verdicts.by_block(found)
        self.assertEqual(sorted(grouped), [7, 9])
        self.assertEqual(len(grouped[7]), 2)

    def test_a_record_with_no_block_index_never_becomes_a_finding(self):
        # It used to arrive as `block=-1` and every consumer filtered on the
        # sentinel first. `parse_report` returns it on the side instead, so
        # there is nothing for the work list to leave out.
        text = "--- RECORD\nVERDICT     drop\nLOCATION    a.py:1\n---\n"
        found, malformed = verdicts.parse_report(text, "block-context")
        self.assertEqual(found, [])
        self.assertEqual(malformed, ["a record with no BLOCK index"])


class TestVerdicts(unittest.TestCase):
    """Every verdict is admissible on every run."""

    def test_the_seven_verdicts_are_the_whole_set(self):
        self.assertEqual(
            set(verdicts.VERDICTS),
            {"clean", "query", "drop", "correct", "patch", "add", "move"},
        )

    def test_reanchor_collapsed_into_move(self):
        self.assertNotIn("reanchor", verdicts.VERDICTS)


class TestContradiction(unittest.TestCase):
    def test_drop_against_correct_is_flagged(self):
        found = [
            _finding(reviewer="ownership-context", block=7, verdict="drop"),
            _finding(reviewer="block-context", block=7, verdict="correct"),
        ]
        self.assertEqual(verdicts.contradictions(verdicts.by_block(found)), [7])

    def test_drop_alone_is_not_a_contradiction(self):
        found = [_finding(reviewer="ownership-context", block=7, verdict="drop")]
        self.assertEqual(verdicts.contradictions(verdicts.by_block(found)), [])

    def test_move_against_correct_is_flagged(self):
        # The claim was measured against the code the block sat with. One role
        # says that anchor is wrong, so the `correct` was derived at the wrong
        # place -- the same collision as drop/correct, one step earlier.
        found = [
            _finding(reviewer="ownership-context", block=7, verdict="move"),
            _finding(reviewer="block-context", block=7, verdict="correct"),
        ]
        self.assertEqual(verdicts.contradictions(verdicts.by_block(found)), [7])

    def test_move_against_patch_is_flagged(self):
        found = [
            _finding(reviewer="ownership-context", block=7, verdict="move"),
            _finding(reviewer="block-context", block=7, verdict="patch"),
        ]
        self.assertEqual(verdicts.contradictions(verdicts.by_block(found)), [7])

    def test_move_with_clean_is_not_a_contradiction(self):
        # `clean` rules on nothing, so it collides with nothing.
        found = [
            _finding(reviewer="ownership-context", block=7, verdict="move"),
            _finding(reviewer="block-context", block=7, verdict="clean"),
        ]
        self.assertEqual(verdicts.contradictions(verdicts.by_block(found)), [])

    def test_move_and_drop_together_are_not_a_contradiction(self):
        # Both relocate; neither rules on what the sentence says.
        found = [
            _finding(reviewer="ownership-context", block=7, verdict="move"),
            _finding(reviewer="module-context", block=7, verdict="drop"),
        ]
        self.assertEqual(verdicts.contradictions(verdicts.by_block(found)), [])

    def test_a_record_that_names_no_block_cannot_reach_a_contradiction(self):
        # It used to reach here as `block=-1` and surface as "RE-REVIEW [-1]".
        # Now it never becomes a Finding, so there is no index to collide on.
        text = (
            "--- RECORD\nVERDICT     drop\nLOCATION    a.py:1\n---\n"
            "--- RECORD\nVERDICT     correct\nLOCATION    a.py:1\n---\n"
        )
        found, malformed = verdicts.parse_report(text, "ownership-context")
        self.assertEqual(len(malformed), 2)
        self.assertEqual(verdicts.contradictions(verdicts.by_block(found)), [])


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
        self.assertIsNone(verdicts.evidence_problem(_finding(), self.repo))

    def test_a_missing_file_is_caught(self):
        f = _finding(evidence="gone.py:5")
        self.assertIn("does not resolve", verdicts.evidence_problem(f, self.repo))

    def test_a_line_past_the_end_is_caught(self):
        f = _finding(evidence="a.py:900")
        self.assertIn("900", verdicts.evidence_problem(f, self.repo))

    def test_a_quote_that_is_not_there_is_caught(self):
        f = _finding(quote="a line that appears nowhere at all")
        self.assertIn("not found near", verdicts.evidence_problem(f, self.repo))

    def test_a_short_quote_that_is_THERE_is_accepted(self):
        # The 12-character floor refused `x = 1`, `pass` and `return` -- real
        # short lines. Roy dropped it from the brief and the gate follows. What
        # binds is PRESENCE, which the next test holds.
        self.assertIsNone(verdicts.evidence_problem(_finding(quote="line"), self.repo))

    def test_a_short_quote_that_is_ABSENT_is_still_rejected(self):
        # The risk of dropping the floor: a short needle matches by accident.
        # It does not -- absence is what the check is for.
        problem = verdicts.evidence_problem(_finding(quote="zzz"), self.repo)
        self.assertIn("not found near", problem)

    def test_a_missing_quote_is_rejected(self):
        # C2: QUOTE carries the verbatim text and is what the window is
        # checked against. A record without one read nothing off the line.
        f = _finding(quote="")
        problem = verdicts.evidence_problem(f, self.repo)
        self.assertIsNotNone(problem)
        self.assertIn("no QUOTE", problem)

    def test_a_derived_summary_right_half_is_not_checked_verbatim(self):
        # C2: the whole point. A count is not a line any file contains, so
        # requiring SUMMARY's right half verbatim made every counted claim --
        # the block-context reviewer's own category -- structurally inadmissible.
        f = _finding(summary='"twenty call sites" || 31 callers, all under tests/')
        self.assertIsNone(verdicts.evidence_problem(f, self.repo))

    def test_a_summary_with_no_right_half_is_still_rejected(self):
        f = _finding(summary='"twenty call sites"')
        self.assertIn("right half", verdicts.evidence_problem(f, self.repo))

    def test_a_query_MUST_carry_evidence(self):
        # Roy ruled 2026-08-16: "It must contain everything to say it was looked
        # at and this is why it is query." The brief always said so -- "a `query`
        # requires EVIDENCE and QUOTE(s), by construction" -- and the gate
        # waived both. Where you LOOKED is a real line on all three shapes.
        f = _finding(verdict="query", evidence="", quote="")
        self.assertIsNotNone(verdicts.evidence_problem(f, self.repo))

    def test_a_query_with_evidence_that_resolves_passes(self):
        f = _finding(verdict="query")
        self.assertIsNone(verdicts.evidence_problem(f, self.repo))

    def test_evidence_line_zero_is_rejected(self):
        f = _finding(evidence="a.py:0")
        self.assertIsNotNone(verdicts.evidence_problem(f, self.repo))

    def test_a_fabricated_location_is_caught(self):
        # A prose LOCATION must be checked with the same machinery as
        # EVIDENCE -- a fabricated location was admissible before this fix.
        f = _finding(location="gone.py:1")
        problem = verdicts.location_problem(f, self.repo)
        self.assertIsNotNone(problem)
        self.assertIn("does not resolve", problem)

    def test_a_resolvable_location_passes(self):
        f = _finding(location="a.py:1-2")
        self.assertIsNone(verdicts.location_problem(f, self.repo))

    def test_evidence_rejects_a_range(self):
        # Minor: the shared CITE regex widened to serve LOCATION's
        # file:start-end, but the record format reserves that for LOCATION --
        # EVIDENCE must stay file:line.
        f = _finding(evidence="a.py:1-2")
        problem = verdicts.evidence_problem(f, self.repo)
        self.assertIsNotNone(problem)
        self.assertIn("file:line", problem)


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

    def _run(self, *reports, reviewers=None, census=None):
        cmd = [
            sys.executable,
            str(SCRIPTS / "verdicts.py"),
            "--census",
            str(census if census is not None else self.census),
            "--repo",
            str(self.repo),
        ]
        if reviewers is not None:
            cmd += ["--reviewers", reviewers]
        cmd += [str(r) for r in reports]
        return subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8", check=False
        )

    def _clean_report(self, name, blocks=(1, 2, 3)):
        """One `clean` RECORD per block — there is no range list."""
        return self._write(
            name,
            "".join(
                "--- RECORD\n"
                f"BLOCK       {n}\n"
                "VERDICT     clean\n"
                "LOCATION    a.py:1\n"
                "FINDING     nothing to report from this role\n"
                "---\n"
                for n in blocks
            ),
        )

    def test_full_coverage_exits_zero(self):
        report = self._clean_report("block-context.txt")
        result = self._run(report)
        self.assertEqual(result.returncode, 0)
        self.assertIn("STANDS UNCHANGED: 3 blocks", result.stdout)
        self.assertIn("NEEDS A RULING:   0 blocks", result.stdout)

    def test_a_misspelt_report_stem_is_fatal(self):
        # The stem WAS taken as a role name on sight, so `ownershp-context.md`
        # became a reviewer called `ownershp-context` and every line below
        # named a role that does not exist.
        report = self._clean_report("ownershp-context.md")
        result = self._run(report)
        self.assertIn("UNKNOWN reviewer 'ownershp-context'", result.stdout)
        self.assertNotEqual(result.returncode, 0)

    def test_a_misspelt_expected_reviewer_is_fatal(self):
        report = self._clean_report("block-context.md")
        result = self._run(report, reviewers="block-context,blck-context")
        self.assertIn("UNKNOWN reviewer 'blck-context'", result.stdout)
        self.assertNotEqual(result.returncode, 0)

    def test_every_published_role_name_is_accepted(self):
        for role in ("ownership-context", "block-context", "function-context"):
            report = self._clean_report(f"{role}.md")
            result = self._run(report, reviewers=role)
            self.assertEqual(result.returncode, 0, f"{role}: {result.stdout}")

    def test_a_missing_payload_is_fatal(self):
        # C2: a payload problem must not print and then exit 0.
        report = self._write(
            "block-context.txt",
            "--- RECORD\n"
            "BLOCK       1\n"
            "VERDICT     drop\n"
            "LOCATION    a.py:1\n"
            "EVIDENCE    a.py:5\n"
            "QUOTE       five callers, all in tests\n"
            'SUMMARY     "x" || five callers, all in tests\n'
            "FINDING     f\n"
            "CHANGE      \n"
            "---\n"
            "--- RECORD\n"
            "BLOCK       2\n"
            "VERDICT     clean\n"
            "LOCATION    a.py:1\n"
            "FINDING     nothing to report from this role\n"
            "---\n"
            "--- RECORD\n"
            "BLOCK       3\n"
            "VERDICT     clean\n"
            "LOCATION    a.py:1\n"
            "FINDING     nothing to report from this role\n"
            "---\n",
        )
        result = self._run(report)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no payload", result.stdout)
        self.assertNotIn("Every finding is admissible", result.stdout)

    def test_an_out_of_range_block_is_fatal(self):
        report = self._write(
            "block-context.txt",
            "--- RECORD\n"
            "BLOCK       999\n"
            "VERDICT     query\n"
            "LOCATION    a.py:1\n"
            'SUMMARY     "x" || could not be settled from the checkout\n'
            "FINDING     f\n"
            "CHANGE      claim: x / checked: git grep / would settle: a caller\n"
            "---\n"
            "--- RECORD\n"
            "BLOCK       1\n"
            "VERDICT     clean\n"
            "LOCATION    a.py:1\n"
            "FINDING     nothing to report from this role\n"
            "---\n"
            "--- RECORD\n"
            "BLOCK       2\n"
            "VERDICT     clean\n"
            "LOCATION    a.py:1\n"
            "FINDING     nothing to report from this role\n"
            "---\n"
            "--- RECORD\n"
            "BLOCK       3\n"
            "VERDICT     clean\n"
            "LOCATION    a.py:1\n"
            "FINDING     nothing to report from this role\n"
            "---\n",
        )
        result = self._run(report)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("out of range", result.stdout)

    def test_a_bare_range_line_is_a_gap_not_a_pass(self):
        # A range list is not a record, so it accounts for nothing: every block
        # it names is a loud coverage gap, never a silent "everything is clean".
        report = self._write("block-context.txt", "CLEAN 1-3\n")
        result = self._run(report)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("COVERAGE GAPS", result.stdout)
        self.assertIn("block-context: 3 blocks unaccounted", result.stdout)

    def test_a_missing_reviewer_is_fatal_when_declared(self):
        report = self._clean_report("block-context.txt")
        result = self._run(report, reviewers="block-context,ownership-context")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ownership-context", result.stdout)

    def test_reviewer_absence_is_declared_not_inferred_when_undeclared(self):
        report = self._clean_report("block-context.txt")
        result = self._run(report)
        self.assertEqual(result.returncode, 0)
        self.assertIn("NOT checked", result.stdout)

    def test_duplicate_report_stems_are_refused(self):
        sub = Path(self.tmp.name) / "dup"
        sub.mkdir()
        one = sub / "block-context.txt"
        one.write_text(_CLEAN_RECORDS, encoding="utf-8")
        two = self._write("block-context.txt", _CLEAN_RECORDS)
        result = self._run(one, two)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("DUPLICATE", result.stdout)

    def test_a_missing_report_file_prints_one_line_not_a_traceback(self):
        result = self._run(Path(self.tmp.name) / "nope.txt")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Traceback", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_pluralisation_of_a_single_reviewer_and_block(self):
        report = self._write(
            "block-context.txt",
            "--- RECORD\n"
            "BLOCK       1\n"
            "VERDICT     query\n"
            "LOCATION    a.py:1\n"
            'SUMMARY     "x" || could not be settled from the checkout\n'
            "FINDING     f\n"
            "CHANGE      claim: x / checked: git grep / would settle: a caller\n"
            "---\n"
            "--- RECORD\n"
            "BLOCK       2\n"
            "VERDICT     clean\n"
            "LOCATION    a.py:1\n"
            "FINDING     nothing to report from this role\n"
            "---\n"
            "--- RECORD\n"
            "BLOCK       3\n"
            "VERDICT     clean\n"
            "LOCATION    a.py:1\n"
            "FINDING     nothing to report from this role\n"
            "---\n",
        )
        result = self._run(report)
        self.assertNotIn("1 reviewers", result.stdout)
        self.assertNotIn("1 blocks", result.stdout)

    def test_an_unterminated_record_is_fatal(self):
        # I8: a parser-level test only proves the mismatch is DETECTED. Only a
        # CLI-level test proves it reaches `fatal` and changes the exit code
        # -- the exact distinction that let all three Criticals ship.
        report = self._write(
            "block-context.txt",
            "--- RECORD\n"
            "BLOCK       1\n"
            "VERDICT     correct\n"
            "LOCATION    a.py:1\n"
            "EVIDENCE    a.py:5\n"
            "QUOTE       five callers, all in tests\n"
            'SUMMARY     "x" || the count is stale\n'
            "FINDING     first record, never closed\n"
            "\n"
            "--- RECORD\n"
            "BLOCK       2\n"
            "VERDICT     correct\n"
            "LOCATION    a.py:1\n"
            "EVIDENCE    a.py:5\n"
            "QUOTE       five callers, all in tests\n"
            'SUMMARY     "x" || the count is stale\n'
            "FINDING     second record, closed\n"
            'CHANGE      false: "x" / true: "y"\n'
            "---\n"
            "--- RECORD\n"
            "BLOCK       3\n"
            "VERDICT     clean\n"
            "LOCATION    a.py:1\n"
            "FINDING     nothing to report from this role\n"
            "---\n",
        )
        result = self._run(report)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("MALFORMED", result.stdout)
        self.assertIn("swallows the next one", result.stdout)

    def test_a_contradiction_is_named_in_the_closing_line_not_contradicted(self):
        # I3: `contradictions()` never increments `fatal` -- correctly, a
        # re-review is not an inadmissible finding -- but the run printed
        # "send the block back" and four lines later "Stage 5 may rule" at
        # exit 0. The two outputs contradicted each other.
        finding = (
            "--- RECORD\n"
            "BLOCK       1\n"
            "VERDICT     {verdict}\n"
            "LOCATION    a.py:1\n"
            "EVIDENCE    a.py:5\n"
            "QUOTE       five callers, all in tests\n"
            'SUMMARY     "x" || the count is stale\n'
            "FINDING     f\n"
            "CHANGE      {change}\n"
            "---\n" + _CLEAN_RECORDS_23
        )
        drop = self._write(
            "ownership-context.txt",
            finding.format(verdict="drop", change="the sentence, verbatim"),
        )
        correct = self._write(
            "block-context.txt",
            finding.format(verdict="correct", change='false: "x" / true: "y"'),
        )
        result = self._run(drop, correct)
        self.assertEqual(result.returncode, 0)
        self.assertIn("RE-REVIEW", result.stdout)
        self.assertIn("1 block still OUT for re-review", result.stdout)
        self.assertNotIn(
            "Every finding is admissible. Stage 5 may rule.", result.stdout
        )

    def test_a_missing_census_prints_one_line_not_a_traceback(self):
        report = self._clean_report("block-context.txt")
        missing = Path(self.tmp.name) / "nope-census.json"
        result = self._run(report, census=missing)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Traceback", result.stdout)
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn("CANNOT READ", result.stdout)

    def test_a_malformed_census_json_prints_one_line_not_a_traceback(self):
        report = self._clean_report("block-context.txt")
        bad = Path(self.tmp.name) / "bad-census.json"
        bad.write_text("{not valid json", encoding="utf-8")
        result = self._run(report, census=bad)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Traceback", result.stdout)
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn("CANNOT PARSE", result.stdout)


class TestTheBriefsOwnRecordPasses(unittest.TestCase):
    """C2: the record `reviewer-brief.md` teaches, through the gate that ships.

    The format and its checker were designed in one task and never run against
    each other, so the brief's worked example failed `verdicts.py` on the same
    commit that shipped both — and the field it failed on, a counted claim,
    is the block-context reviewer's own category.

    The cited file is SYNTHESISED from the record's own citations: the example
    is invented on purpose (`docs/limitations.md`), so there is no real
    `redacted_pkg/` to read. What this pins is the record's SHAPE — every field the
    parser needs, a QUOTE long enough to have been read off a line, EVIDENCE
    as `file:line` and LOCATION as `file:start-end`, and the payload the
    verdict table demands.
    """

    # The fence may carry a language hint (```text). Matching it loosely keeps
    # this pinned to the RECORD's shape rather than to how the block is fenced.
    RECORD = re.compile(r"```\w*\n(--- RECORD\n.*?\n---)\n```", re.S)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        text = BRIEF.read_text(encoding="utf-8")
        match = self.RECORD.search(text)
        self.assertIsNotNone(match, "no canonical FINDING record in reviewer-brief.md")
        self.record = match.group(1)
        found, _ = verdicts.parse_report(self.record + "\n", "block-context")
        self.assertEqual(len(found), 1, self.record)
        self.finding = found[0]
        self._plant()

    def tearDown(self):
        self.tmp.cleanup()

    def _plant(self):
        """Write the file the record cites, with its QUOTE on the cited line."""
        rel, _, lineno = self.finding.evidence.rpartition(":")
        target = self.repo / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        lines = [f"filler {i}\n" for i in range(1, int(lineno) + 40)]
        lines[int(lineno) - 1] = self.finding.quote + "\n"
        target.write_text("".join(lines), encoding="utf-8")

    def test_the_record_parses_into_a_real_block_index(self):
        self.assertGreaterEqual(self.finding.block, 1)
        self.assertIn(self.finding.verdict, verdicts.VERDICTS)

    def test_the_record_passes_the_evidence_check(self):
        self.assertIsNone(verdicts.evidence_problem(self.finding, self.repo))

    def test_the_record_passes_the_location_check(self):
        self.assertIsNone(verdicts.location_problem(self.finding, self.repo))

    def test_the_record_passes_the_payload_check(self):
        self.assertIsNone(verdicts.payload_problem(self.finding))


if __name__ == "__main__":
    unittest.main()
