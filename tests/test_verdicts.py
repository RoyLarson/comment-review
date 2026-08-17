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
SOURCES     a.py:5 | the settling line
CLAIM       false: "only one caller" / true: "three callers"
REASON      three callers here, so the count is wrong
CHANGE      # three callers, all under tests/
---

--- RECORD
BLOCK       2
VERDICT     clean
REASON      nothing to report from this role
---
"""


def _clean_records(*blocks: int) -> str:
    """One `clean` RECORD per block. There is no range list to write instead."""
    return "".join(
        "--- RECORD\n"
        f"BLOCK       {n}\n"
        "VERDICT     clean\n"
        "REASON      nothing to report from this role\n"
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
        "sources": ["a.py:5 | the settling line"],
        "claim": 'false: "a" / true: "b"',
        "reason": "three callers, all under tests/, so the count is stale",
        "change": "# b, written out with its surrounding block",
    }
    fields.update(kw)
    return verdicts.Finding(**fields)


class TestParsing(unittest.TestCase):
    def test_a_record_is_parsed(self):
        found, _ = verdicts.parse_report(REPORT, "block-context")
        self.assertEqual(len(found), 2)
        self.assertEqual(found[0].block, 1)
        self.assertEqual(found[0].verdict, "correct")
        self.assertEqual(found[0].sources, ["a.py:5 | the settling line"])

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
SOURCES     a.py:1 | one
CLAIM       false: "x" / true: "y"
REASON      first record, never closed

--- RECORD
BLOCK       2
VERDICT     correct
SOURCES     a.py:1 | one
CLAIM       false: "x" / true: "y"
REASON      second record, closed
CHANGE      # y, in its block
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
        f = _finding(claim="fix it")
        self.assertIn("false/true pair", verdicts.payload_problem(f))

    def test_correct_with_a_pair_passes(self):
        self.assertIsNone(verdicts.payload_problem(_finding()))

    def test_add_without_an_anchor_is_rejected(self):
        f = _finding(
            reviewer="ownership-context", verdict="add", claim='missing: "some text"'
        )
        self.assertIn("side", verdicts.payload_problem(f))

    def test_a_verdict_that_states_no_reason_is_rejected(self):
        # The field went unchecked while it doubled as the diagnostic slot
        # for a malformed record. It holds one thing now, so it is required.
        self.assertIn("REASON", verdicts.payload_problem(_finding(reason="  ")))

    def test_clean_owes_no_reason(self):
        f = _finding(verdict="clean", claim="", reason="", change="")
        self.assertIsNone(verdicts.payload_problem(f))


class TestReasonSaysSomething(unittest.TestCase):
    """REASON is the field the `move` ruling rests on -- *"this comment belongs
    to that line there"* -- and nothing checked it. A reviewer that echoes the
    claim back has filed a verdict with no reason.
    """

    SPEC = 'false: "only one caller" / true: "31 callers, all in tests/"'

    def test_a_reason_that_restates_the_claim_is_refused(self):
        f = _finding(claim=self.SPEC, reason=self.SPEC)
        self.assertIn("restates", verdicts.payload_problem(f))

    def test_a_reason_that_adds_the_derivation_passes(self):
        f = _finding(claim=self.SPEC, reason="31 callers and every one is in tests/")
        self.assertIsNone(verdicts.payload_problem(f))

    def test_case_and_quoting_do_not_disguise_a_restatement(self):
        f = _finding(claim=self.SPEC.upper(), reason=f"  {self.SPEC}  ")
        self.assertIn("restates", verdicts.payload_problem(f))

    def test_a_reason_that_QUOTES_the_claim_and_explains_it_passes(self):
        # ⚠ Equality only, never containment. A REASON that quotes the claim
        # and then says what is wrong with it is doing its job, and a
        # containment test would refuse it.
        f = _finding(
            claim=self.SPEC,
            reason=f"{self.SPEC} — the count came from a grep over tests/",
        )
        self.assertIsNone(verdicts.payload_problem(f))


class TestAddAnchor(unittest.TestCase):
    """The brief asks for "the text AND its anchor — which code, above or below".

    That is a NAMED site and a side. The check accepted the bare WORD "anchor"
    instead, so a finding that never named a declaration passed and one that
    named a declaration without using the word failed.
    """

    def _add(self, spec):
        return verdicts.payload_problem(
            _finding(reviewer="ownership-context", verdict="add", claim=spec)
        )

    def test_the_bare_word_anchor_no_longer_passes(self):
        self.assertIsNotNone(self._add('missing: "an anchor comment here"'))

    def test_a_side_with_no_named_anchor_is_rejected(self):
        self.assertIn("backticks", self._add('missing: "x" / put it above the loop'))

    def test_a_named_anchor_with_no_side_is_rejected(self):
        self.assertIn("side", self._add('missing: "x" / goes with `retry_budget`'))

    def test_a_named_anchor_and_a_side_passes(self):
        self.assertIsNone(
            self._add('missing: "the ceiling is 100" above `retry_budget`')
        )

    def test_before_and_after_count_as_sides(self):
        for side in ("before", "after"):
            self.assertIsNone(
                self._add(f'missing: "retries are capped" {side} `send()`'), side
            )

    def test_an_add_that_does_not_carry_its_text_is_rejected(self):
        # ⚠ The anchor alone says WHERE and not WHAT. CLAIM is the spec, so the
        # text belongs in it -- CHANGE shows it already placed in the block, and
        # no checker can pick the new sentence back out of a block.
        self.assertIn("missing:", self._add("above `send()`: retries are capped"))


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
        f = _finding(verdict="query", claim=self.QUERY)
        self.assertIsNone(verdicts.payload_problem(f))

    def test_a_query_naming_no_attempted_check_is_rejected(self):
        f = _finding(
            verdict="query",
            claim="outside the code. claim: unclear. someone should settle this",
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
                claim=(
                    f"outside the code. claim: x / {verb} the enclosing definition"
                    " / would settle: another role"
                ),
            )
            self.assertIsNone(verdicts.payload_problem(f), verb)

    def test_a_query_that_does_not_say_what_would_settle_it_is_rejected(self):
        f = _finding(
            verdict="query",
            claim=(
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
            claim="outside the code. the branch name is unsettled",
        )
        self.assertIn("ATTEMPTED", verdicts.payload_problem(f))

    def test_a_range_of_values_names_no_check_and_is_rejected(self):
        f = _finding(
            verdict="query",
            claim="outside the code. a range of values, unsettled",
        )
        self.assertIn("ATTEMPTED", verdicts.payload_problem(f))

    def test_transfer_semantics_names_no_check_and_is_rejected(self):
        f = _finding(
            verdict="query",
            claim="outside the code. transfer semantics unsettled",
        )
        self.assertIn("ATTEMPTED", verdicts.payload_problem(f))

    def test_an_honest_query_worded_with_requires_is_admitted(self):
        f = _finding(
            verdict="query",
            claim=(
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
            claim=(
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
            claim=(
                "outside the code. claim: the timeout is 30s."
                " I looked at config.py and found"
                " nothing definitive, would need the deploy config to be sure"
            ),
        )
        self.assertIsNone(verdicts.payload_problem(f))

    def test_looking_up_the_constant_counts_as_an_attempted_check(self):
        f = _finding(
            verdict="query",
            claim=(
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
            claim=(
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
        return _finding(verdict="query", sources=[], claim=change)

    def test_an_out_of_role_query_declares_scope(self):
        f = self._q("claim: x / outside my role, resolved the enclosing def")
        self.assertTrue(verdicts.declares_scope(f))

    def test_the_other_two_query_shapes_are_still_work(self):
        # The brief names three shapes. Only the first is a non-ruling; these
        # two reach the AUTHOR and must stay in the work list.
        for spec in (
            "claim: x / checked the checkout / outside the checkout, it is gitignored",
            "claim: x / read the module / outside the code, needs someone who ran it",
        ):
            self.assertFalse(verdicts.declares_scope(self._q(spec)), spec)

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
REASON      nothing to report from this role
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
            _finding(
                reviewer="ownership-context",
                block=7,
                verdict="move",
                claim="from: `a.py` line 3 / to: `b.py` line 9",
            ),
            _finding(
                reviewer="module-context",
                block=9,
                verdict="drop",
                claim='drop: "the sentence"',
            ),
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
    """A contradiction is two verdicts on ONE SENTENCE.

    ⚠ The check keyed on the census BLOCK index while a verdict rules on a
    sentence, so any `drop` in a block collided with any `correct` in it.
    Measured on a live run: 8 blocks flagged, 2 genuine, and a re-review round
    was spent on each of the other six.

    ⚠⚠ `move` is not in the set at all. A relocation and a truth fix COMPOSE --
    move the prose, then correct it at the destination, which is the synthesis
    order at steps 2 and 3. Ruled 2026-08-17.
    """

    # ⚠⚠ These fixtures carry a real ORIGINAL and a real CHANGE, because the
    # collision is keyed on the DIFF between them and not on `CLAIM`. Ruled
    # 2026-08-17. A fixture that named sentences without editing any text would
    # exercise nothing.
    ORIGINAL = "the budget is 3. callers round separately."
    # ⚠ The collision is keyed on the DIFF, and a diff is read through the
    # census -- the block's KIND selects how, its PATH selects the markers. So
    # these tests need a census, and one entry per index they cite.
    BLOCKS = [
        {
            "path": "a.py",
            "start": n,
            "end": n,
            "kind": "comment",
            "text": "the budget is 3. callers round separately.",
        }
        for n in range(1, 8)
    ]

    def _pair(self, drop_text, correct_text, verdict="correct"):
        """A `drop` of one sentence against a `correct`/`patch` of another.

        Each `change` is `ORIGINAL` with only that finding's own edit made --
        which is the contract a reviewer works to, and what makes each diff
        name one sentence.
        """
        dropped = self.ORIGINAL.replace(drop_text, "").strip()
        corrected = self.ORIGINAL.replace(correct_text, "something else")
        return verdicts.by_block(
            [
                _finding(
                    reviewer="ownership-context",
                    verdict="drop",
                    claim=f'drop: "{drop_text}"',
                    original=self.ORIGINAL,
                    change=dropped,
                ),
                _finding(
                    reviewer="block-context",
                    verdict=verdict,
                    claim=f'false: "{correct_text}" / true: "something else"',
                    original=self.ORIGINAL,
                    change=corrected,
                ),
            ]
        )

    def test_drop_and_correct_on_the_SAME_sentence_collide(self):
        # Measured block 728: ownership dropped the sentence function-context
        # was correcting. Delete it, or fix its count -- nothing composes those.
        got = self._pair("the budget is 3.", "the budget is 3")
        self.assertEqual(verdicts.contradictions(got, self.BLOCKS), [1])

    def test_drop_and_correct_on_DIFFERENT_sentences_do_not_collide(self):
        # Measured block 981: ownership dropped one clause, two roles corrected
        # another in the same docstring. The join called it a contradiction and
        # a re-review round established that it was not.
        got = self._pair("callers round separately.", "the budget is 3")
        self.assertEqual(verdicts.contradictions(got, self.BLOCKS), [])

    def test_a_containing_sentence_still_collides(self):
        # One role drops the whole block; another corrects a clause inside it.
        got = self._pair(self.ORIGINAL, "the budget is 3")
        self.assertEqual(verdicts.contradictions(got, self.BLOCKS), [1])

    def test_drop_against_patch_on_one_sentence_collides(self):
        got = self._pair("the budget is 3.", "the budget is 3", "patch")
        self.assertEqual(verdicts.contradictions(got, self.BLOCKS), [1])

    def test_move_against_correct_COMPOSES_and_is_not_flagged(self):
        # Ruled 2026-08-17: placement and truth are a sequence, not a rivalry.
        found = [
            _finding(
                reviewer="ownership-context",
                verdict="move",
                claim="from: `census.py` line 12 / to: `SYMBOLISH`",
            ),
            _finding(
                reviewer="block-context",
                verdict="correct",
                claim=(
                    'false: "the ordering is significant" / true: "the sort decides"'
                ),
            ),
        ]
        self.assertEqual(
            verdicts.contradictions(verdicts.by_block(found), self.BLOCKS), []
        )

    def test_move_against_patch_is_not_flagged(self):
        found = [
            _finding(
                reviewer="ownership-context",
                verdict="move",
                claim="from: `a.py` line 3 / to: `b.py` line 9",
            ),
            _finding(
                reviewer="block-context",
                verdict="patch",
                claim='from: "the old wording" / to: "the new wording"',
            ),
        ]
        self.assertEqual(
            verdicts.contradictions(verdicts.by_block(found), self.BLOCKS), []
        )

    def test_drop_alone_is_not_a_contradiction(self):
        found = [
            _finding(
                reviewer="ownership-context",
                block=7,
                verdict="drop",
                claim='drop: "the sentence"',
            )
        ]
        self.assertEqual(
            verdicts.contradictions(verdicts.by_block(found), self.BLOCKS), []
        )

    def test_drop_with_clean_is_not_a_contradiction(self):
        # `clean` rules on nothing, so it collides with nothing.
        found = [
            _finding(
                reviewer="ownership-context",
                block=7,
                verdict="drop",
                claim='drop: "the sentence"',
            ),
            _finding(reviewer="block-context", block=7, verdict="clean"),
        ]
        self.assertEqual(
            verdicts.contradictions(verdicts.by_block(found), self.BLOCKS), []
        )

    def test_an_unreadable_payload_is_flagged_rather_than_passed(self):
        # ⚠ Silence here would hide a real collision behind a malformed payload.
        found = [
            _finding(reviewer="ownership-context", verdict="drop", claim="drop: "),
            _finding(
                reviewer="block-context", verdict="correct", claim="fix the count"
            ),
        ]
        self.assertEqual(
            verdicts.contradictions(verdicts.by_block(found), self.BLOCKS), [1]
        )

    def test_a_record_that_names_no_block_cannot_reach_a_contradiction(self):
        # It used to reach here as `block=-1` and surface as "RE-REVIEW [-1]".
        # Now it never becomes a Finding, so there is no index to collide on.
        text = (
            "--- RECORD\nVERDICT     drop\nLOCATION    a.py:1\n---\n"
            "--- RECORD\nVERDICT     correct\nLOCATION    a.py:1\n---\n"
        )
        found, malformed = verdicts.parse_report(text, "ownership-context")
        self.assertEqual(len(malformed), 2)
        self.assertEqual(
            verdicts.contradictions(verdicts.by_block(found), self.BLOCKS), []
        )


class TestSource(unittest.TestCase):
    """`EVIDENCE` and `QUOTE` merged into `SOURCES` as `file:line | verbatim`.

    They were ONE field until a split, because the old `SUMMARY` mixed verbatim
    with derived text and a checker cannot verify both in one field. SOURCES's
    two halves are both VERBATIM, so the merge does not recreate that.

    ⚠ A SOURCES line may REPEAT, one per place examined -- which is what "plural
    for a query" means, and it avoids a delimiter that verbatim text could
    contain.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        (self.repo / "a.py").write_text(
            "one\ntwo\nthree\nfour\nthe settling line\nsix\n", encoding="utf-8"
        )
        (self.repo / "b.py").write_text("alpha\nbeta\ngamma\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_a_resolvable_source_passes(self):
        self.assertIsNone(verdicts.source_problem(_finding(), self.repo))

    def test_a_missing_file_is_caught(self):
        f = _finding(sources=["gone.py:5 | x"])
        self.assertIn("does not resolve", verdicts.source_problem(f, self.repo))

    def test_a_line_past_the_end_is_caught(self):
        f = _finding(sources=["a.py:900 | x"])
        self.assertIn("900", verdicts.source_problem(f, self.repo))

    def test_line_zero_is_rejected(self):
        f = _finding(sources=["a.py:0 | one"])
        self.assertIsNotNone(verdicts.source_problem(f, self.repo))

    def test_a_verbatim_half_that_is_not_there_is_caught(self):
        f = _finding(sources=["a.py:5 | a line that appears nowhere at all"])
        self.assertIn("not found", verdicts.source_problem(f, self.repo))

    def test_a_SHORT_verbatim_half_that_is_there_is_accepted(self):
        # The 12-character floor refused `x = 1`, `pass` and `return` -- real
        # short lines. What binds is PRESENCE, not length.
        f = _finding(sources=["a.py:5 | line"])
        self.assertIsNone(verdicts.source_problem(f, self.repo))

    def test_a_range_is_accepted(self):
        # `allow_range` held EVIDENCE to `file:line` on a rule that stated no
        # reason. A range is where the reviewer looked, the same as a line.
        f = _finding(sources=["a.py:4-6 | the settling line"])
        self.assertIsNone(verdicts.source_problem(f, self.repo))

    def test_a_source_with_no_pipe_is_refused(self):
        f = _finding(sources=["a.py:5"])
        self.assertIn("|", verdicts.source_problem(f, self.repo))

    def test_a_source_with_no_verbatim_half_is_refused(self):
        f = _finding(sources=["a.py:5 | "])
        self.assertIn("verbatim", verdicts.source_problem(f, self.repo))

    def test_no_source_at_all_is_refused(self):
        self.assertIn(
            "SOURCES", verdicts.source_problem(_finding(sources=[]), self.repo)
        )

    def test_clean_owes_no_source(self):
        f = _finding(verdict="clean", sources=[], reason="", change="")
        self.assertIsNone(verdicts.source_problem(f, self.repo))

    def test_a_query_carries_a_source_like_any_other_verdict(self):
        # Ruled 2026-08-16: "It must contain everything to say it was looked at
        # and this is why it is query." Where you LOOKED is a real line on all
        # three shapes.
        self.assertIsNone(verdicts.source_problem(_finding(verdict="query"), self.repo))

    def test_a_query_with_no_source_is_refused(self):
        f = _finding(verdict="query", sources=[])
        self.assertIsNotNone(verdicts.source_problem(f, self.repo))

    def test_a_derived_REASON_is_not_checked_verbatim(self):
        # A count is not a line any file contains, so checking the DERIVED
        # statement against the tree made every counted claim -- block-context's
        # own category -- structurally inadmissible. Only SOURCES is verbatim.
        f = _finding(
            claim='"twenty call sites"',
            reason="31 callers and every one is under tests/",
        )
        self.assertIsNone(verdicts.source_problem(f, self.repo))

    # ⚠ The `SUMMARY` right-half check retired with the field. Its job -- a
    # finding must state something derived -- is REASON being required, which
    # `payload_problem` enforces and `TestPayload` covers. The coverage moved.

    # ⚠ The two LOCATION tests retired with the field. LOCATION was checked for
    # RESOLVABILITY and never against the block it claimed to describe, so a
    # finding attached to the wrong block resolved cleanly. `TestClaimAgainstTheCensus`
    # is what replaces it, and it is a stronger check than the one removed.


class TestSeveralSources(unittest.TestCase):
    """A claim often needs TWO sites to settle -- the definition and its callers.

    ⚠ Stricter than the single-citation rule it replaces: EVERY source must
    resolve AND carry its verbatim half. The old rule wanted the quote near one
    citation; both halves of a SOURCES are one statement about one place.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        (self.repo / "a.py").write_text(
            "one\ntwo\nthree\nfour\nthe settling line\nsix\n", encoding="utf-8"
        )
        (self.repo / "b.py").write_text("alpha\nbeta\ngamma\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_two_sources_that_both_resolve_pass(self):
        f = _finding(sources=["a.py:5 | the settling line", "b.py:2 | beta"])
        self.assertIsNone(verdicts.source_problem(f, self.repo))

    def test_a_second_source_that_does_not_resolve_is_refused(self):
        f = _finding(sources=["a.py:5 | the settling line", "gone.py:2 | x"])
        self.assertIn("gone.py", verdicts.source_problem(f, self.repo))

    def test_a_second_verbatim_half_that_is_absent_is_refused(self):
        # ⚠ This is the strictness the merge buys. Under the old rule the quote
        # had to sit near ONE citation, so a second citation carried nothing.
        f = _finding(sources=["a.py:5 | the settling line", "b.py:2 | not there"])
        self.assertIn("not found", verdicts.source_problem(f, self.repo))

    def test_a_pipe_inside_the_verbatim_half_survives(self):
        (self.repo / "c.py").write_text('x = "a | b"\n', encoding="utf-8")
        f = _finding(sources=['c.py:1 | x = "a | b"'])
        self.assertIsNone(verdicts.source_problem(f, self.repo))

    def test_repeated_SOURCE_lines_are_all_kept(self):
        text = (
            "--- RECORD\nBLOCK       1\nVERDICT     correct\nLOCATION    a.py:1\n"
            "SOURCES     a.py:5 | the settling line\n"
            "SOURCES     b.py:2 | beta\n"
            'CLAIM       false: "x" / true: "y"\nREASON      y\n'
            "CHANGE      # b, in its block\n---\n"
        )
        found, _ = verdicts.parse_report(text, "block-context")
        self.assertEqual(len(found[0].sources), 2)


class TestBlockProblem(unittest.TestCase):
    """Is the sentence this finding rules on actually IN the block it cites?

    ⚠⚠ Keyed on the ORIGINAL, which `CLAIM` carries in its `drop:`, `false:` or
    `from:` half -- never on `CHANGE`, which holds the REPLACEMENT. Matching the
    replacement against the original block would refuse every correct finding
    and pass the ones that changed nothing.

    ⚠ This is what `LOCATION` could never do. It was AMBIGUOUS -- four
    possible subjects, set out in `address_problem` -- so it could only be
    checked for resolvability, never against the thing it described.
    """

    BLOCKS = [
        {
            "path": "a.py",
            "start": 1,
            "end": 2,
            "kind": "comment",
            "text": "the retry budget is 3 and callers round separately",
        },
        {"path": "a.py", "start": 9, "end": 9, "kind": "interval", "text": ""},
    ]

    def _at(self, verdict, claim):
        return verdicts.block_problem(
            _finding(block=1, verdict=verdict, claim=claim), self.BLOCKS
        )

    def test_a_correct_whose_false_half_is_in_the_block_passes(self):
        self.assertIsNone(
            self._at("correct", 'false: "the retry budget is 3" / true: "it is 5"')
        )

    def test_a_correct_whose_false_half_is_absent_is_refused(self):
        problem = self._at("correct", 'false: "the timeout is 30s" / true: "60s"')
        self.assertIn("not in block 1", problem)

    def test_a_drop_whose_sentence_is_in_the_block_passes(self):
        self.assertIsNone(self._at("drop", 'drop: "callers round separately"'))

    def test_a_drop_whose_sentence_is_absent_is_refused(self):
        problem = self._at("drop", 'drop: "a line from somewhere else"')
        self.assertIn("not in block 1", problem)

    def test_a_patch_is_checked_on_its_FROM_half(self):
        # ⚠ The `from:` half is what makes a patch checkable at all. With only
        # the rewrite, nothing said WHICH sentence it replaces.
        self.assertIsNone(
            self._at("patch", 'from: "the retry budget is 3" / to: "the budget is 3"')
        )

    def test_a_patch_whose_from_half_is_absent_is_refused(self):
        problem = self._at("patch", 'from: "a line from elsewhere" / to: "x"')
        self.assertIn("not in block 1", problem)

    def test_quoting_and_whitespace_do_not_defeat_the_match(self):
        self.assertIsNone(
            self._at("correct", 'false: "  The  Retry   Budget Is 3 " / true: "x"')
        )

    def test_a_move_names_PLACES_and_so_is_exempt(self):
        # ⚠ A `move`'s from/to are locations, not text, so there is no sentence
        # to look for. The BLOCK it cites is what identifies the prose.
        self.assertIsNone(self._at("move", "from: `a.py` line 1 / to: `send()`"))

    def test_an_add_owes_nothing_here(self):
        # `add` is about prose that is MISSING, so there is no sentence in the
        # block to find.
        f = _finding(block=2, verdict="add", claim='missing: "capped" above `send()`')
        self.assertIsNone(verdicts.block_problem(f, self.BLOCKS))

    def test_clean_owes_nothing_here(self):
        f = _finding(block=1, verdict="clean", claim="", reason="", change="")
        self.assertIsNone(verdicts.block_problem(f, self.BLOCKS))

    def test_a_spec_carrying_no_original_sentence_is_left_alone(self):
        # ⚠ `payload_problem` refuses a malformed CLAIM. Reporting it here too
        # would print two defects for one mistake.
        self.assertIsNone(self._at("correct", "fix the count"))

    def test_an_out_of_range_block_is_left_to_the_range_check(self):
        f = _finding(block=99, claim='false: "x" / true: "y"')
        self.assertIsNone(verdicts.block_problem(f, self.BLOCKS))


class TestChangeIsRequired(unittest.TestCase):
    """CHANGE is the RESULT -- the edit already made, with its surrounding block.

    Roy, 2026-08-17: *"The change is what allows the apply section to apply the
    claim appropriately."* CLAIM says what must change; CHANGE is the finished
    prose stage 5 substitutes, so no checker can judge it beyond its presence.
    """

    def test_an_edit_verdict_with_no_change_is_refused(self):
        self.assertIn(
            "carries no CHANGE", verdicts.payload_problem(_finding(change=""))
        )

    def test_clean_owes_no_change(self):
        f = _finding(verdict="clean", claim="", reason="", change="")
        self.assertIsNone(verdicts.payload_problem(f))

    def test_a_query_owes_no_change(self):
        # ⚠ A query says the claim is UNSETTLED, so it proposes no text and
        # there is nothing for stage 5 to apply.
        f = _finding(
            verdict="query",
            claim=(
                "outside the checkout. checked: git ls-files"
                " / would settle: a copy in the tree"
            ),
            change="",
        )
        self.assertIsNone(verdicts.payload_problem(f))

    def test_a_drop_needs_its_sentence_in_the_claim(self):
        self.assertIn("drop needs", verdicts.payload_problem(_finding(verdict="drop")))

    def test_a_move_needs_a_from_to_pair(self):
        f = _finding(verdict="move", claim="put it in the docs")
        self.assertIn("from/to", verdicts.payload_problem(f))

    def test_correct_keeps_false_true_rather_than_from_to(self):
        # ⚠ The pair differs on purpose: `correct` asserts the sentence is
        # FALSE, and that assertion is what separates it from a `patch`. A
        # neutral from/to would erase the distinction the synthesis order
        # depends on.
        f = _finding(verdict="correct", claim='from: "a" / to: "b"')
        self.assertIn("false/true pair", verdicts.payload_problem(f))


class TestAFieldMayRunOverSeveralLines(unittest.TestCase):
    """`CHANGE` is a whole block, so it is several lines by construction.

    ⚠ Lines naming no field were SKIPPED, so a multi-line CHANGE arrived holding
    only its first line and nothing said so. The task agent then applied one
    line of a block it was told was the whole block.
    """

    def _one(self, body):
        found, malformed = verdicts.parse_report(
            f"--- RECORD\n{body}---\n", "block-context"
        )
        self.assertEqual(malformed, [])
        self.assertEqual(len(found), 1)
        return found[0]

    def test_a_change_keeps_every_line(self):
        f = self._one(
            "BLOCK       1\n"
            "VERDICT     correct\n"
            'CLAIM       false: "three" / true: "31"\n'
            "REASON      counted with git grep\n"
            "CHANGE      # 31 callers want this, all under tests/.\n"
            "            # Narrowing it re-derives the clamp bounds.\n"
        )
        self.assertIn("Narrowing it", f.change)
        self.assertEqual(len(f.change.splitlines()), 2)

    def test_a_blank_line_INSIDE_a_field_is_content(self):
        # ⚠⚠ The worst defect 0.2.0 shipped was the opposite of this. A blank
        # line ended the continuation, so every docstring -- which has one
        # between its summary and its `Args:` -- was truncated to its first
        # paragraph. Measured: 33% of one census, ~450 blocks of another, and
        # every refused transcription was correct.
        f = self._one(
            "BLOCK       1\n"
            "VERDICT     correct\n"
            'CLAIM       false: "a" / true: "b"\n'
            "REASON      why\n"
            "CHANGE      # b, first paragraph.\n"
            "\n"
            "            # and the second, after a gap.\n"
        )
        self.assertIn("second", f.change)
        self.assertIn("\n\n", f.change)

    def test_trailing_blank_lines_come_off_a_field(self):
        # ⚠ Blank lines INSIDE a field are content; the ones before the next
        # label are the spacing between records.
        f = self._one(
            "BLOCK       1\n"
            "VERDICT     correct\n"
            'CLAIM       false: "a" / true: "b"\n'
            "REASON      why\n"
            "CHANGE      # b\n"
            "\n"
            "\n"
        )
        self.assertEqual(f.change, "# b")

    def test_a_later_field_ends_the_continuation(self):
        f = self._one(
            "BLOCK       1\n"
            "VERDICT     correct\n"
            "CHANGE      # b\n"
            "            # and a second line\n"
            'CLAIM       false: "a" / true: "b"\n'
            "REASON      why\n"
        )
        self.assertEqual(f.change, "# b\n            # and a second line")
        self.assertEqual(f.reason, "why")

    def test_a_continued_SOURCE_stays_with_its_own_citation(self):
        # ⚠ SOURCES accumulates where the others overwrite, so a continuation
        # must join the LAST citation rather than starting a new one.
        f = self._one(
            "BLOCK       1\n"
            "VERDICT     correct\n"
            "SOURCES     a.py:5 | def f(\n"
            "                x, y\n"
            "SOURCES     b.py:2 | beta\n"
            'CLAIM       false: "a" / true: "b"\n'
            "REASON      why\n"
            "CHANGE      # b\n"
        )
        self.assertEqual(len(f.sources), 2)
        self.assertIn("x, y", f.sources[0])
        self.assertEqual(f.sources[1], "b.py:2 | beta")


class TestMoveShowsBothBlocks(unittest.TestCase):
    """A `move` changes TWO blocks, so its CHANGE shows both.

    Roy, 2026-08-17: *"Move kind of needs both sides to be correct. What the
    block where it comes from looks like and what the block the sentence looks
    like after. The upstream side can be omitted if the full block moves not
    just a sentence."*
    """

    def _move(self, change):
        return verdicts.payload_problem(
            _finding(
                verdict="move",
                claim="from: `a.py` line 3 / to: `docs/a.md`",
                change=change,
            )
        )

    def test_both_sides_pass(self):
        self.assertIsNone(
            self._move("to: # the destination, with it\nfrom: # the origin, without it")
        )

    def test_the_destination_alone_passes_as_a_WHOLE_block_move(self):
        # ⚠ Omitting `from:` ASSERTS the whole block moved -- nothing is left at
        # the origin to show. No checker can tell that from a partial move, so
        # the reviewer says which by what it supplies.
        self.assertIsNone(self._move("to: # the destination, with it"))

    def test_the_origin_alone_is_refused(self):
        self.assertIn("DESTINATION", self._move("from: # the origin, without it"))

    def test_a_move_with_no_change_at_all_is_refused(self):
        self.assertIn("carries no CHANGE", self._move("   "))


class TestBlockCarriesItsAddressAndOriginal(unittest.TestCase):
    """`BLOCK` is `<index> | <path>:<start>-<end>` plus the block's text.

    Roy, 2026-08-17: *"BLOCK gets the address and the original text verbatim.
    This allows the reviewer to have most the context and most of the time all
    of the context it needs to understand."*

    ⚠⚠ All three are CHECKED, and this is NOT `LOCATION` coming back. That
    field was dropped for AMBIGUITY: it could have named where the prose sits,
    where the reviewer looked, where the prose should GO, or which sentence
    exactly. Three of those are fields now and the fourth is DERIVED from the
    difference between `BLOCK`'s original and `CHANGE` -- `address_problem`
    sets out which is which -- and each is checked against a different thing.
    """

    BLOCKS = [
        {
            "path": "redacted_pkg/rates.py",
            "start": 352,
            "end": 354,
            "kind": "comment",
            "text": "the retry budget is 3 and callers round separately",
        },
        {
            "path": "redacted_pkg/rates.py",
            "start": 9,
            "end": 9,
            "kind": "interval",
            "text": "",
        },
        {
            "path": "redacted_pkg/rates.py",
            "start": 20,
            "end": 20,
            "kind": "comment",
            "text": "one line only",
        },
    ]

    ORIGINAL = "# the retry budget is 3 and callers\n# round separately"

    def _at(self, **kw):
        fields = {
            "block": 1,
            "address": "redacted_pkg/rates.py:352-354",
            "original": self.ORIGINAL,
        }
        fields.update(kw)
        return verdicts.address_problem(_finding(**fields), self.BLOCKS)

    def test_a_matching_address_and_original_passes(self):
        self.assertIsNone(self._at())

    def test_a_missing_address_is_refused_and_the_message_shows_the_right_one(self):
        problem = self._at(address="")
        self.assertIn("carries no ADDRESS", problem)
        self.assertIn("1 | redacted_pkg/rates.py:352-354", problem)

    def test_an_address_naming_the_wrong_lines_is_refused(self):
        self.assertIn("census says", self._at(address="redacted_pkg/rates.py:352-353"))

    def test_an_address_naming_the_wrong_file_is_refused(self):
        self.assertIn("census says", self._at(address="redacted_pkg/other.py:352-354"))

    def test_a_windows_separator_still_matches(self):
        # ⚠ The census writes `/`; a reviewer on Windows may copy `\`. That is
        # the same address and refusing it would be a platform bug, not a check.
        self.assertIsNone(self._at(address="redacted_pkg\\rates.py:352-354"))

    def test_a_one_line_block_is_addressed_without_a_range(self):
        self.assertIsNone(
            self._at(block=3, address="redacted_pkg/rates.py:20", original="# one line only")
        )

    def test_a_missing_original_is_refused(self):
        self.assertIn("carries no ORIGINAL", self._at(original="  "))

    def test_an_original_that_is_not_the_block_is_refused(self):
        self.assertIn("does not match", self._at(original="# something else"))

    def test_comment_markers_and_wrapping_are_forgiven(self):
        # ⚠ Case, whitespace and leading markers only. The census stores the
        # prose with its markers stripped; a reviewer transcribes what the FILE
        # shows. Comparing those raw would refuse every honest transcription --
        # a check that fires only on people who did the work.
        self.assertIsNone(
            self._at(
                original="  #   The Retry Budget is 3 and\n"
                "  # callers ROUND separately  "
            )
        )

    def test_an_empty_INTERVAL_owes_no_original(self):
        # ⚠ This is what an `add` cites: prose that is MISSING has no original.
        self.assertIsNone(
            self._at(
                block=2,
                verdict="add",
                claim='missing: "capped" above `send()`',
                address="redacted_pkg/rates.py:9",
                original="",
            )
        )

    def test_clean_owes_neither(self):
        f = _finding(verdict="clean", claim="", reason="", change="", address="")
        self.assertIsNone(verdicts.address_problem(f, self.BLOCKS))

    def test_an_out_of_range_block_is_left_to_the_range_check(self):
        self.assertIsNone(self._at(block=99))


class TestTheBlockLineParses(unittest.TestCase):
    """`BLOCK <index> | <address>` with the original on the lines below."""

    def _one(self, body):
        found, malformed = verdicts.parse_report(
            f"--- RECORD\n{body}---\n", "block-context"
        )
        self.assertEqual(malformed, [])
        return found[0]

    def test_the_three_parts_come_apart(self):
        f = self._one(
            "BLOCK       17 | redacted_pkg/rates.py:352-354\n"
            "            # Kept because twenty call sites want this.\n"
            "            # Narrowing it re-derives the clamp bounds.\n"
            "VERDICT     clean\n"
            "REASON      nothing to report from this role\n"
        )
        self.assertEqual(f.block, 17)
        self.assertEqual(f.address, "redacted_pkg/rates.py:352-354")
        self.assertIn("twenty call sites", f.original)
        self.assertIn("clamp bounds", f.original)

    def test_a_bare_index_still_parses_for_clean(self):
        f = self._one(
            "BLOCK       17\n"
            "VERDICT     clean\n"
            "REASON      nothing to report from this role\n"
        )
        self.assertEqual(f.block, 17)
        self.assertEqual(f.address, "")
        self.assertEqual(f.original, "")


class TestSourcesTakeContinuationLines(unittest.TestCase):
    """SOURCES is plural because it repeats -- by label or by continuation."""

    def _sources(self, body):
        found, _ = verdicts.parse_report(f"--- RECORD\n{body}---\n", "block-context")
        return found[0].sources

    def test_a_second_citation_below_the_label_is_its_own_entry(self):
        got = self._sources(
            "BLOCK       1\n"
            "VERDICT     clean\n"
            "SOURCES     a.py:5 | def f():\n"
            "            b.py:9 | f()\n"
            "REASON      why\n"
        )
        self.assertEqual(got, ["a.py:5 | def f():", "b.py:9 | f()"])

    def test_a_wrapped_verbatim_half_stays_with_its_own_citation(self):
        # ⚠ The ambiguity this resolves: a continuation is either the NEXT
        # citation or the wrapped tail of the one above. Only a line opening
        # with `path:line` is the former.
        got = self._sources(
            "BLOCK       1\n"
            "VERDICT     clean\n"
            "SOURCES     a.py:5 | def compute(plan,\n"
            "            week, *, clamp=True):\n"
            "REASON      why\n"
        )
        self.assertEqual(len(got), 1)
        self.assertIn("clamp=True", got[0])


class TestTheClaimAndTheEditMustAgree(unittest.TestCase):
    """A BACKSTOP: does CHANGE edit the sentence CLAIM says it edits?

    ⚠⚠ Nothing else reads the two accounts of one edit against each other.
    `block_problem` confirms the claimed sentence is IN the block;
    `payload_problem` confirms CHANGE exists. Neither notices a reviewer that
    reasoned about one sentence and rewrote another. Roy authorised this
    2026-08-17 "as a backstop to the Apply agent not doing its due diligence".
    """

    ORIGINAL = "# the budget is 3.\n# callers round separately."

    # ⚠ The diff is read through the CENSUS: `kind` selects how the block is
    # read, `path` selects the comment markers. A hand-rolled normaliser here
    # would be the third definition of a block's text, which is the defect
    # this whole class exists to pin.
    ENTRY = {
        "path": "a.py",
        "start": 1,
        "end": 2,
        "kind": "comment",
        "text": "the budget is 3. callers round separately.",
    }

    def _at(self, **kw):
        return verdicts.edit_problem(_finding(original=self.ORIGINAL, **kw), self.ENTRY)

    def test_an_edit_confined_to_the_claimed_sentence_passes(self):
        self.assertIsNone(
            self._at(
                claim='false: "the budget is 3" / true: "the budget is 5"',
                change="# the budget is 5.\n# callers round separately.",
            )
        )

    def test_an_edit_to_a_sentence_the_claim_does_not_name_is_refused(self):
        # ⚠ THE CASE THIS EXISTS FOR. The claim is about the budget; the text
        # rewrites the rounding. Both halves look fine on their own.
        problem = self._at(
            claim='false: "the budget is 3" / true: "the budget is 5"',
            change="# the budget is 3.\n# callers round together.",
        )
        self.assertIn("CLAIM does not name", problem)

    def test_a_change_identical_to_the_original_is_refused(self):
        # ⚠ Otherwise the backstop passes vacuously: no removed span means
        # nothing to disagree with, and a verdict that edits nothing sails
        # through the check built to catch it.
        problem = self._at(
            claim='false: "the budget is 3" / true: "the budget is 5"',
            change=self.ORIGINAL,
        )
        self.assertIn("UNCHANGED", problem)

    def test_rewrapping_alone_is_not_an_edit(self):
        # ⚠ Compared on WORDS, so a reviewer that reflows the block while
        # correcting one sentence is not accused of editing the rest.
        self.assertIsNone(
            self._at(
                claim='false: "the budget is 3" / true: "the budget is 5"',
                change="# the budget is 5. callers\n# round separately.",
            )
        )

    def test_a_purely_additive_edit_passes(self):
        # ⚠ Words that only APPEAR are not a claim about existing prose, so
        # there is nothing for the claim to disagree with.
        self.assertIsNone(
            self._at(
                claim='from: "the budget is 3" / to: "the retry budget is 3"',
                verdict="patch",
                change="# the retry budget is 3.\n# callers round separately.",
            )
        )

    def test_a_drop_whose_CHANGE_is_the_same_block_is_refused(self):
        problem = self._at(
            verdict="drop",
            claim='drop: "callers round separately"',
            change="# the budget is 3. callers round separately.",
        )
        self.assertIn("UNCHANGED", problem)

    def test_a_drop_that_only_ADDS_is_refused(self):
        # ⚠ Not word-identical, so the unchanged check does not fire -- and yet
        # the sentence the drop names is still there. This is the case the
        # drop-specific message exists for.
        problem = self._at(
            verdict="drop",
            claim='drop: "callers round separately"',
            change=self.ORIGINAL + "\n# and a note nobody asked for.",
        )
        self.assertIn("nothing was removed", problem)

    def test_a_drop_that_removes_its_own_sentence_passes(self):
        self.assertIsNone(
            self._at(
                verdict="drop",
                claim='drop: "callers round separately"',
                change="# the budget is 3.",
            )
        )

    def test_a_drop_that_removes_MORE_than_it_claims_is_refused(self):
        problem = self._at(
            verdict="drop",
            claim='drop: "callers round separately"',
            change="",
        )
        # ⚠ An empty CHANGE is `payload_problem`'s to refuse, not this one --
        # reporting it twice would print two defects for one mistake.
        self.assertIsNone(problem)
        self.assertIn(
            "carries no CHANGE",
            verdicts.payload_problem(
                _finding(verdict="drop", claim='drop: "x"', change="")
            ),
        )

    def test_two_findings_folded_into_one_CHANGE_are_refused(self):
        # ⚠⚠ The brief rules that ONE finding's CHANGE makes ONE finding's
        # edit. A reviewer handing in the block fully fixed on both records is
        # claiming one edit and showing two, and stage 5 cannot compose records
        # that have already been merged.
        problem = self._at(
            claim='false: "the budget is 3" / true: "the budget is 5"',
            change="# the budget is 5.\n# callers round together.",
        )
        self.assertIn("CLAIM does not name", problem)

    def test_move_is_exempt_because_its_CHANGE_is_two_blocks(self):
        self.assertIsNone(
            self._at(
                verdict="move",
                claim="from: `a.py` line 1 / to: `docs/a.md`",
                change="to: # the destination\nfrom: # the origin",
            )
        )

    def test_add_is_exempt_because_it_has_no_original(self):
        self.assertIsNone(
            verdicts.edit_problem(
                _finding(
                    verdict="add",
                    claim='missing: "capped" above `send()`',
                    original="",
                    change="# capped\ndef send():",
                ),
                self.ENTRY,
            )
        )

    def test_clean_and_query_are_exempt(self):
        for verdict in ("clean", "query"):
            self.assertIsNone(
                verdicts.edit_problem(
                    _finding(verdict=verdict, claim="", reason="", change=""),
                    self.ENTRY,
                ),
                verdict,
            )

    def test_a_record_with_no_original_is_left_to_the_address_check(self):
        f = _finding(original="", change="# anything")
        self.assertIsNone(verdicts.edit_problem(f, self.ENTRY))


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
                # ⚠ `text` is not optional. `block_problem` matches the sentence
                # a finding rules on against the block it cites, so a fixture without
                # it refuses every finding -- which is the check working, and
                # the real census has carried `text` since it was written.
                [
                    {"path": "a.py", "start": 1, "end": 2, "text": "x"},
                    {"path": "a.py", "start": 3, "end": 4, "text": "x"},
                    {"path": "a.py", "start": 5, "end": 6, "text": "x"},
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
                "REASON      nothing to report from this role\n"
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
            "BLOCK       1 | a.py:1-2\n"
            "            x\n"
            "VERDICT     move\n"
            "SOURCES     a.py:5 | five callers, all in tests\n"
            "CLAIM       from: `a.py` line 1 / to: `docs/a.md`\n"
            "REASON      five callers, all in tests\n"
            "CHANGE      \n"
            "---\n"
            "--- RECORD\n"
            "BLOCK       2\n"
            "VERDICT     clean\n"
            "REASON      nothing to report from this role\n"
            "---\n"
            "--- RECORD\n"
            "BLOCK       3\n"
            "VERDICT     clean\n"
            "REASON      nothing to report from this role\n"
            "---\n",
        )
        result = self._run(report)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("carries no CHANGE", result.stdout)
        self.assertNotIn("Every finding is admissible", result.stdout)

    def test_an_out_of_range_block_is_fatal(self):
        report = self._write(
            "block-context.txt",
            "--- RECORD\n"
            "BLOCK       999\n"
            "VERDICT     query\n"
            'CLAIM       false: "x" / true: "y"\n'
            "REASON      could not be settled from the checkout\n"
            "CHANGE      # the settled line, in its block\n"
            "---\n"
            "--- RECORD\n"
            "BLOCK       1\n"
            "VERDICT     clean\n"
            "REASON      nothing to report from this role\n"
            "---\n"
            "--- RECORD\n"
            "BLOCK       2\n"
            "VERDICT     clean\n"
            "REASON      nothing to report from this role\n"
            "---\n"
            "--- RECORD\n"
            "BLOCK       3\n"
            "VERDICT     clean\n"
            "REASON      nothing to report from this role\n"
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
            'CLAIM       false: "x" / true: "y"\n'
            "REASON      could not be settled from the checkout\n"
            "CHANGE      # the settled line, in its block\n"
            "---\n"
            "--- RECORD\n"
            "BLOCK       2\n"
            "VERDICT     clean\n"
            "REASON      nothing to report from this role\n"
            "---\n"
            "--- RECORD\n"
            "BLOCK       3\n"
            "VERDICT     clean\n"
            "REASON      nothing to report from this role\n"
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
            "SOURCES     a.py:5 | five callers, all in tests\n"
            'CLAIM       false: "x" / true: "y"\n'
            "REASON      the count is stale, and this record never closed\n"
            "\n"
            "--- RECORD\n"
            "BLOCK       2\n"
            "VERDICT     correct\n"
            "SOURCES     a.py:5 | five callers, all in tests\n"
            'CLAIM       false: "x" / true: "y"\n'
            "REASON      the count is stale, and this record closed\n"
            "CHANGE      # y, in its block\n"
            "---\n"
            "--- RECORD\n"
            "BLOCK       3\n"
            "VERDICT     clean\n"
            "REASON      nothing to report from this role\n"
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
            "BLOCK       1 | a.py:1-2\n"
            "            x\n"
            "VERDICT     {verdict}\n"
            "SOURCES     a.py:5 | five callers, all in tests\n"
            "CLAIM       {claim}\n"
            "REASON      the count is stale\n"
            "CHANGE      # the block, as it reads after this edit\n"
            "---\n" + _CLEAN_RECORDS_23
        )
        drop = self._write(
            "ownership-context.txt",
            # ⚠ The two must name the SAME sentence, or there is no collision:
            # a contradiction is keyed on the text, not on the block index.
            finding.format(verdict="drop", claim='drop: "x"'),
        )
        correct = self._write(
            "block-context.txt",
            finding.format(verdict="correct", claim='false: "x" / true: "y"'),
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
    as `file:line` and BLOCK as `<index> | file:start-end`, and the payload the
    verdict table demands.
    """

    # ⚠⚠ The field ORDER is a contract, not a layout. Roy, 2026-08-17:
    # *"Verdict -> Claim -> REASON -> SOURCES -> CHANGE ... that is a clear
    # chain of custody on the reasoning and the required actions."* The parser
    # is label-keyed and would accept any order, so nothing but this test stops
    # the brief drifting out of the sequence it teaches.
    CHAIN = ["BLOCK", "VERDICT", "CLAIM", "REASON", "SOURCES", "CHANGE"]

    # The fence may carry a language hint (```text). Matching it loosely keeps
    # this pinned to the RECORD's shape rather than to how the block is fenced.
    RECORD = re.compile(r"```\w*\n(--- RECORD\n.*?\n---)\n```", re.S)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        text = BRIEF.read_text(encoding="utf-8")
        match = self.RECORD.search(text)
        self.assertIsNotNone(match, "no canonical RECORD in reviewer-brief.md")
        self.record = match.group(1)
        found, _ = verdicts.parse_report(self.record + "\n", "block-context")
        self.assertEqual(len(found), 1, self.record)
        self.finding = found[0]
        self._plant()

    def tearDown(self):
        self.tmp.cleanup()

    def _plant(self):
        """Write each file a SOURCES cites, with its verbatim half on that line.

        ⚠ Every source is planted, not just the first: `source_problem` resolves
        all of them, so a record citing two places needs both to exist.
        """
        for source in self.finding.sources:
            cite, _, verbatim = source.partition("|")
            rel, _, lineno = cite.strip().rpartition(":")
            target = self.repo / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            lines = [f"filler {i}\n" for i in range(1, int(lineno) + 40)]
            lines[int(lineno) - 1] = verbatim.strip() + "\n"
            target.write_text("".join(lines), encoding="utf-8")

    def test_the_record_parses_into_a_real_block_index(self):
        self.assertGreaterEqual(self.finding.block, 1)
        self.assertIn(self.finding.verdict, verdicts.VERDICTS)

    def test_the_record_is_written_in_the_chain_of_custody_order(self):
        labels = [
            m.group(1)
            for line in self.record.splitlines()
            if (m := verdicts.FIELD.match(line))
        ]
        self.assertEqual(
            labels,
            self.CHAIN,
            "the brief's record has drifted out of the chain-of-custody order",
        )

    def test_the_dataclass_is_written_in_the_same_order(self):
        # ⚠ The Finding docstring says field order follows the brief's record.
        # A dataclass reordered without the brief, or the reverse, makes that
        # sentence false with nothing to catch it.
        fields = [f for f in verdicts.Finding.__dataclass_fields__ if f != "reviewer"]
        chain = [c.lower() for c in self.CHAIN]
        self.assertEqual([f for f in fields if f in chain], chain)

    def test_the_record_passes_the_source_check(self):
        self.assertIsNone(verdicts.source_problem(self.finding, self.repo))

    def test_the_records_CLAIM_carries_a_quoted_original(self):
        # ⚠ Not run against a census: the brief's record cites block 17 of a
        # tree that does not exist here. What IS checkable is that its CLAIM is
        # a SPEC -- `false:` naming the existing sentence, quoted, and `true:`
        # the replacement -- because the quoted half is what `block_problem`
        # matches against the census text.
        claim = self.finding.claim
        self.assertIn("false:", claim)
        self.assertIn("true:", claim)
        self.assertTrue(
            verdicts.ruled_text(self.finding),
            f"no original sentence readable from the brief's CLAIM: {claim!r}",
        )

    def test_the_records_CHANGE_is_the_finished_block(self):
        # ⚠ CHANGE is what stage 5 substitutes, so the brief must SHOW prose
        # rather than another from/to pair. A record whose CHANGE repeated the
        # spec would teach every reviewer to hand back a diff.
        change = self.finding.change
        self.assertTrue(change.strip(), "the brief's record carries no CHANGE")
        for marker in ("false:", "true:", "from:", "to:"):
            self.assertNotIn(
                marker, change, f"the brief's CHANGE restates the spec: {change!r}"
            )

    def test_the_record_passes_the_payload_check(self):
        self.assertIsNone(verdicts.payload_problem(self.finding))


class TestSkillAndBriefAgreeOnTheUnit(unittest.TestCase):
    """The brief says a block can carry six verdicts; SKILL.md said one per role.

    Six summaries have been found disagreeing with the detailed site they
    summarise, every one drifting in the summary while the detail stayed
    correct. This is the pair that was still doing it.
    """

    SKILL = BRIEF.parent.parent / "SKILL.md"

    def _skill(self):
        """SKILL.md with newlines flattened, so a wrapped phrase still matches.

        ⚠ Read through a helper and asserted with `assertTrue` rather than
        `assertIn`: the file is 40 KB and `assertIn` prints the whole haystack,
        which buries the one line that failed.
        """
        return " ".join(self.SKILL.read_text(encoding="utf-8").split())

    def test_the_brief_permits_several_verdicts_on_one_block(self):
        brief = " ".join(BRIEF.read_text(encoding="utf-8").split())
        self.assertTrue(
            "A block of six sentences can carry six" in brief,
            "the brief no longer says a block can carry several verdicts",
        )

    def test_the_skill_does_not_say_one_per_role_per_block(self):
        self.assertFalse(
            "one per role per block" in self._skill(),
            "SKILL.md still says ONE verdict per role per block",
        )

    def test_the_skill_says_one_or_more(self):
        self.assertTrue(
            "one or more per role per block" in self._skill(),
            "SKILL.md does not say a role may file several",
        )

    def test_the_skill_requires_reading_the_surrounding_code(self):
        # Roy, 2026-08-17: the synthesiser is expected to read the context
        # around where the replacement lands. Both worse-than-before findings
        # from the rolled-back run die there.
        self.assertTrue(
            "read the code around where that replacement lands" in self._skill(),
            "SKILL.md does not oblige the synthesiser to read the context",
        )


if __name__ == "__main__":
    unittest.main()
