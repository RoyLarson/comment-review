"""`concordance/annotate.py`: which numbers in prose are VALUES.

`repeated-literal` fires on a number written twice, because a hand-copied
threshold drifts. That makes every false value a false finding handed to a
reviewer, so the two edges of `prose_numbers` are pinned here: a sentence-final
number IS a value, and a list ordinal is NOT.

Both edges were measured on 2026-08-17 and each was regressed by the fix for
the other, which is why they sit in one file.
"""

from comment_review.concordance.annotate import prose_numbers


class TestASentenceFinalNumberIsAValue:
    """The trailing `.` the lookahead used to refuse.

    `(?![\\w.%])` rejected any match followed by a period and had no shorter
    alternative to backtrack to, so `the cap is 3.` returned nothing -- and
    prose is written in sentences, so this was the commonest form of the case
    the annotation exists for.
    """

    def test_a_number_ending_a_sentence_is_found(self):
        assert prose_numbers("the cap is 3.") == {"3"}

    def test_both_numbers_survive_a_comma_and_a_period(self):
        assert prose_numbers("budget 3, not 5.") == {"3", "5"}

    def test_a_version_is_not_a_value(self):
        assert prose_numbers("see v1.2.3 here") == set()

    def test_a_date_is_not_a_value(self):
        assert prose_numbers("measured 2026-08-17") == set()


class TestAListOrdinalIsNotAValue:
    """Two files that number their steps share `1`, `2`, `3` and mean nothing by it.

    !! THE JOINED RUN CANNOT TELL THE TWO APART. `1.` opening a list and `3.`
    ending a sentence are the same characters once the paragraph is joined, and
    only the LINE START separates them -- so the raw lines are what settle it,
    and `census` passes them at both call sites.
    """

    def test_the_ordinal_is_dropped_when_the_raw_lines_are_given(self):
        raw = ["# 1. collate", "# 2. mark"]
        assert prose_numbers(" ".join(raw), raw) == set()

    def test_a_close_paren_ordinal_is_dropped_too(self):
        raw = ["# 1) collate", "# 2) mark"]
        assert prose_numbers(" ".join(raw), raw) == set()

    def test_a_value_on_a_numbered_line_survives_its_ordinal(self):
        # Only the ordinal goes; the line's own prose is still read.
        raw = ["# 1. retry 5 times"]
        assert prose_numbers(" ".join(raw), raw) == {"5"}

    def test_a_sentence_final_number_survives_the_raw_line_path(self):
        # The fix for the ordinal must not undo the fix above it.
        raw = ["# the cap is 3."]
        assert prose_numbers(" ".join(raw), raw) == {"3"}

    def test_without_the_raw_lines_the_ordinal_still_reads_as_a_value(self):
        # Stated so the dependency is visible: a caller that drops `raw_lines`
        # gets the false positive back, and there is no way to recover it from
        # the joined text alone.
        assert prose_numbers("# 1. collate") == {"1"}
