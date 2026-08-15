"""The dispatch packet is validated before four agents fire in parallel."""

import unittest  # noqa: I001  -- path shim below must import before run_context

from _paths import FIXTURES  # noqa: F401  -- path shim must import first
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


if __name__ == "__main__":
    unittest.main()
