"""The dispatch packet is validated before four agents fire in parallel."""

import subprocess  # noqa: I001  -- path shim below must import before run_context
import sys
import tempfile
import unittest
from pathlib import Path

from _paths import FIXTURES, SCRIPTS  # noqa: F401  -- path shim must import first
import run_context


FULL = """
## LEVEL
full

## CAP
none published

## WIDTH
88

## DOC CONVENTION
google

## STYLE SHEET
docs/style-sheet.md

## LSP LANGUAGES
python answered; go had no server

## MOVE DESTINATION
UNAVAILABLE — no destination tree

## CENSUS
/tmp/run-abc/census.txt

## ANGLE FILES
/abs/agents/comment-review-locality.md

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
        self.assertTrue(run_context._answered("UNAVAILABLE — no destination tree"))

    def test_a_hint_followed_by_a_real_answer_is_accepted(self):
        self.assertTrue(
            run_context._answered("<!-- path to it, or `new` --> docs/style.md")
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


if __name__ == "__main__":
    unittest.main()
