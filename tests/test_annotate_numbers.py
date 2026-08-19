"""`repeated-literal` fires on a hand-copied VALUE, and a list ordinal is not one."""

import unittest  # noqa: I001  -- path shim below must import before annotate

from _paths import FIXTURES  # noqa: F401
import annotate


class TestProseNumbersFindsValues(unittest.TestCase):
    """The loosened trailing lookahead, kept: prose is written in sentences."""

    def test_a_sentence_final_number_is_a_value(self):
        self.assertEqual(annotate.prose_numbers("the cap is 3."), {"3"})

    def test_both_numbers_survive_a_comma_and_a_period(self):
        self.assertEqual(annotate.prose_numbers("budget 3, not 5."), {"3", "5"})

    def test_a_version_is_not_a_value(self):
        self.assertEqual(annotate.prose_numbers("see v1.2.3 here"), set())

    def test_a_date_is_not_a_value(self):
        self.assertEqual(annotate.prose_numbers("measured 2026-08-17"), set())


class TestAListOrdinalIsNotAValue(unittest.TestCase):
    """Two files that number their steps share `1`, `2`, `3` and mean nothing by it.

    The joined run cannot tell `1.` opening a list from `3.` ending a sentence
    -- the characters are identical and only the LINE START separates them --
    so the raw lines are what settle it.
    """

    def test_the_ordinal_is_dropped_when_the_raw_lines_are_given(self):
        raw = ["# 1. collate", "# 2. mark"]
        self.assertEqual(annotate.prose_numbers(" ".join(raw), raw), set())

    def test_a_close_paren_ordinal_is_dropped_too(self):
        raw = ["# 1) collate", "# 2) mark"]
        self.assertEqual(annotate.prose_numbers(" ".join(raw), raw), set())

    def test_a_value_on_a_numbered_line_survives_its_ordinal(self):
        raw = ["# 1. retry 5 times"]
        self.assertEqual(annotate.prose_numbers(" ".join(raw), raw), {"5"})

    def test_a_sentence_final_number_survives_the_raw_line_path(self):
        raw = ["# the cap is 3."]
        self.assertEqual(annotate.prose_numbers(" ".join(raw), raw), {"3"})

    def test_without_the_raw_lines_the_ordinal_still_reads_as_a_value(self):
        # The joined text alone cannot separate the two, which is why the raw
        # lines are passed at both call sites in `census.py`.
        self.assertEqual(annotate.prose_numbers("# 1. collate"), {"1"})
