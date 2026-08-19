"""The dispatch packet is validated before four agents fire in parallel."""

import subprocess  # noqa: I001  -- path shim below must import before run_context
import sys
import tempfile
import unittest
from pathlib import Path

from _paths import FIXTURES, SCRIPTS  # noqa: F401  -- path shim must import first
import run_context


FULL = """
## REPO ROOT
/abs/repo

## DOC CONVENTION
google

## STYLE SHEET
docs/style-sheet.md

## LSP LANGUAGES
python answered; go had no server

## MOVE DESTINATION
UNAVAILABLE -- no destination tree

## CENSUS
/tmp/run-abc/dispatch.txt

## LOOKUP CENSUS
/tmp/run-abc/census.json

## REVIEWER FILES
/abs/agents/comment-review-ownership-context.md

## FILES UNDER REVIEW
a.py

## REFERENCE ONLY
docs/decisions.md
"""


class TestValidation(unittest.TestCase):
    def test_a_complete_packet_passes(self):
        self.assertEqual(run_context.missing_sections(FULL), [])

    def test_an_absent_section_is_named(self):
        without = FULL.replace("## STYLE SHEET\ndocs/style-sheet.md", "")
        self.assertIn("STYLE SHEET", run_context.missing_sections(without))

    def test_an_empty_section_is_named(self):
        empty = FULL.replace("docs/decisions.md", "")
        self.assertIn("REFERENCE ONLY", run_context.missing_sections(empty))

    def test_the_template_validates_as_incomplete(self):
        self.assertTrue(run_context.missing_sections(run_context.template()))

    def test_every_required_section_is_in_the_template(self):
        tmpl = run_context.template()
        for name in run_context.REQUIRED:
            self.assertIn(f"## {name}", tmpl)

    def test_a_wrapped_hint_comment_is_not_an_answer(self):
        # A reflowed (word-wrapped) HTML comment splits the hint across two
        # lines. Neither line, read on its own, looks like the rest of the
        # hint -- this must still be rejected as a non-answer.
        wrapped = FULL.replace(
            "## STYLE SHEET\ndocs/style-sheet.md",
            "## STYLE SHEET\n<!-- path to it, or `new --\nstarted this run` -->",
        )
        self.assertIn("STYLE SHEET", run_context.missing_sections(wrapped))

    def test_an_unterminated_comment_swallows_the_rest_of_the_body(self):
        # No closing "-->": everything from the opener to the end of the
        # body is treated as comment, even real-looking content after it.
        # Over-rejection is the safe direction here.
        unterminated = FULL.replace(
            "## STYLE SHEET\ndocs/style-sheet.md",
            "## STYLE SHEET\n<!-- forgot to close this hint\ndocs/style-sheet.md",
        )
        self.assertIn("STYLE SHEET", run_context.missing_sections(unterminated))

    def test_a_repeated_heading_with_one_empty_copy_is_named(self):
        # Regression test: first-occurrence-wins would let the answered copy
        # mask the empty one and pass STYLE SHEET clean.
        duped = FULL + "\n## STYLE SHEET\n"
        self.assertIn("STYLE SHEET", run_context.missing_sections(duped))

    def test_the_docstrings_count_claim_matches_required(self):
        # Regression test: the module docstring once said "seven things"
        # while REQUIRED held eleven entries -- a counted claim that had
        # drifted from the list it was counting. The docstring must name
        # the true count of REQUIRED, whatever that count currently is, so
        # a twelfth section added later fails this test instead of quietly
        # re-creating the same false claim.
        self.assertIn(str(len(run_context.REQUIRED)), run_context.__doc__)


class TestAnswered(unittest.TestCase):
    """`_answered` probed against the whole class of malformed comments.

    HTML comments do not nest, so a second "<!--" before the first span
    closes leaves a dangling "-->" behind -- that must not read as content
    either.
    """

    def test_a_nested_comment_is_rejected(self):
        self.assertFalse(run_context._answered("<!-- outer <!-- inner --> -->"))

    def test_a_triple_nested_comment_is_rejected(self):
        self.assertFalse(run_context._answered("<!-- <!-- <!-- --> --> -->"))

    def test_adjacent_comments_are_rejected(self):
        self.assertFalse(run_context._answered("<!-- a --><!-- b -->"))

    def test_a_bare_closing_token_in_real_prose_does_not_erase_the_answer(self):
        self.assertTrue(run_context._answered("see --> docs/style.md"))

    def test_a_triple_dash_closer_alone_is_rejected(self):
        # An off-by-one dash count on the delimiter -- no letter or digit
        # survives, so this is exactly as empty as "-->" or "<!--" alone.
        self.assertFalse(run_context._answered("--->"))

    def test_a_hint_followed_by_a_dash_artifact_is_rejected(self):
        self.assertFalse(run_context._answered("<!-- hint --> --->"))

    def test_content_genuinely_outside_a_closed_span_is_accepted(self):
        # HTML comments do not nest: "<!--" opens and the FIRST "-->" closes
        # it, so the "c" here is genuinely outside the span, by the same
        # rule that makes the two rejections above correct. Not a hole.
        self.assertTrue(run_context._answered("<!--- a <!-- b --> c --->"))

    def test_none_published_is_accepted(self):
        self.assertTrue(run_context._answered("none published"))

    def test_a_bare_number_is_accepted(self):
        self.assertTrue(run_context._answered("88"))

    def test_a_bare_word_is_accepted(self):
        self.assertTrue(run_context._answered("google"))

    def test_a_path_is_accepted(self):
        self.assertTrue(run_context._answered("docs/style-sheet.md"))

    def test_unavailable_with_an_em_dash_is_accepted(self):
        self.assertTrue(run_context._answered("UNAVAILABLE -- no destination tree"))

    def test_a_hint_followed_by_a_real_answer_is_accepted(self):
        self.assertTrue(
            run_context._answered("<!-- path to it, or `new` --> docs/style.md")
        )


class TestCheckableAnswers(unittest.TestCase):
    """I4: presence was the whole check, so `x` in every section passed.

    Replacing every hint with `x` reported every section complete and
    dispatched four reviewers against a census path that does not resolve.
    The two answers a machine can settle are now settled.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve()
        self.census = self.root / "census.json"
        self.census.write_text("[]", encoding="utf-8")
        self.reviewer = self.root / "ownership-context.md"
        self.reviewer.write_text("reviewer\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def _packet(self, census=None, reviewers=None, root=None):
        census = self.census.as_posix() if census is None else census
        reviewers = [self.reviewer.as_posix()] if reviewers is None else reviewers
        root = self.root.as_posix() if root is None else root
        return (
            FULL.replace("## REPO ROOT\n/abs/repo", f"## REPO ROOT\n{root}")
            .replace("## CENSUS\n/tmp/run-abc/dispatch.txt", f"## CENSUS\n{census}")
            # ! BOTH census paths must point at a real file, or every packet in
            # this suite fails the existence check on the second one alone.
            .replace(
                "## LOOKUP CENSUS\n/tmp/run-abc/census.json",
                f"## LOOKUP CENSUS\n{census}",
            )
            .replace(
                "## REVIEWER FILES\n/abs/agents/comment-review-ownership-context.md",
                "## REVIEWER FILES\n" + "\n".join(reviewers),
            )
        )

    def test_a_valid_packet_has_no_invalid_answers(self):
        packet = self._packet()
        self.assertEqual(run_context.missing_sections(packet), [])
        self.assertEqual(run_context.invalid_answers(packet), [])

    def test_a_relative_repo_root_is_named(self):
        # Roy, 2026-08-17: the reviewers "could get the full path to the root
        # directory they are supposed to work in". A relative one is the same
        # guess at a working directory the packet exists to remove.
        problems = run_context.invalid_answers(self._packet(root="."))
        self.assertTrue(any(p.startswith("REPO ROOT:") for p in problems), problems)

    def test_a_repo_root_that_is_not_there_is_named(self):
        gone = (self.root / "no-such-repo").as_posix()
        problems = run_context.invalid_answers(self._packet(root=gone))
        self.assertTrue(any(p.startswith("REPO ROOT:") for p in problems), problems)

    def test_a_relative_census_path_is_named(self):
        problems = run_context.invalid_answers(self._packet(census="census.json"))
        self.assertTrue(any(p.startswith("CENSUS:") for p in problems), problems)

    def test_an_absolute_census_path_that_is_not_there_is_named(self):
        gone = (self.root / "gone.json").as_posix()
        problems = run_context.invalid_answers(self._packet(census=gone))
        self.assertTrue(any(p.startswith("CENSUS:") for p in problems), problems)

    def test_each_reviewer_file_entry_is_checked_not_just_the_first(self):
        entries = [self.reviewer.as_posix(), (self.root / "missing.md").as_posix()]
        problems = run_context.invalid_answers(self._packet(reviewers=entries))
        self.assertEqual(len(problems), 1, problems)
        self.assertIn("missing.md", problems[0])

    def test_a_bulleted_and_a_labelled_entry_both_resolve(self):
        entries = [
            f"- {self.reviewer.as_posix()}",
            f"ownership-context: {self.reviewer.as_posix()}",
        ]
        self.assertEqual(
            run_context.invalid_answers(self._packet(reviewers=entries)), []
        )

    def test_every_x_packet_is_refused(self):
        # The exact reproduction: a hint replaced by `x` everywhere.
        packet = "\n".join(f"## {name}\nx\n" for name in run_context.REQUIRED)
        self.assertEqual(run_context.missing_sections(packet), [])
        problems = run_context.invalid_answers(packet)
        # ! Asserted by NAME, never by count. This held a hardcoded 3 and broke
        # the moment a fourth checkable section was added -- a number carried
        # beside the thing it counts, which is the defect this repo keeps
        # finding. The names also say WHICH sections a machine can settle.
        self.assertEqual(
            {p.split(":")[0] for p in problems},
            {"REPO ROOT", "CENSUS", "LOOKUP CENSUS", "REVIEWER FILES"},
            problems,
        )


class TestCLI(unittest.TestCase):
    """`main()` end to end -- the unreadable-packet branch must actually gate."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, *args):
        cmd = [sys.executable, str(SCRIPTS / "run_context.py"), *args]
        return subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8", check=False
        )

    def test_a_missing_packet_exits_nonzero_without_a_traceback(self):
        missing = Path(self.tmp.name) / "does-not-exist.md"
        result = self._run("--check", str(missing))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("CANNOT READ", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_a_directory_given_as_the_packet_exits_nonzero_without_a_traceback(self):
        # A directory is not a file: read_text() raises, and that must be
        # caught the same way a missing file is, not left to a traceback.
        result = self._run("--check", self.tmp.name)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("CANNOT READ", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_a_present_but_unusable_answer_gates_at_the_exit_code(self):
        # I4, end to end: every section answered with `x` reported itself
        # complete at exit 0 and dispatched four reviewers.
        packet = Path(self.tmp.name) / "context.md"
        packet.write_text(
            "\n".join(f"## {name}\nx\n" for name in run_context.REQUIRED),
            encoding="utf-8",
        )
        result = self._run("--check", str(packet))
        self.assertEqual(result.returncode, 1)
        self.assertIn("UNUSABLE", result.stdout)
        self.assertIn("CENSUS:", result.stdout)
        self.assertIn("REVIEWER FILES:", result.stdout)
        self.assertNotIn("Complete:", result.stdout)


# !! LAST LINE, ALWAYS. A runner placed above a class runs before that
# class exists, so `python tests/<file>.py` reported a green bar over a
# SHORTER suite than `unittest discover` -- and the tests it skipped were
# the ones someone running a single file was iterating on. Measured
# 2026-08-17: 26 direct against 28 discovered here, 9 against 11 in
# test_vocabulary.py.
if __name__ == "__main__":
    unittest.main()
