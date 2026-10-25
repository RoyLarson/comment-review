"""What a `Paragraph` derives from the raw lines a reader hands it."""

import pytest

from comment_review.reading.paragraph import MARKERS, Paragraph


def paragraph(*raw_lines: str) -> Paragraph:
    return Paragraph("m.py", 1, len(raw_lines), "comment", "", raw_lines=[*raw_lines])


def test_every_prose_line_counts():
    assert paragraph("# one", "# two", "# three").lines == 3


def test_a_blank_line_inside_the_run_is_free():
    assert paragraph("# one", "", "# two").lines == 2


@pytest.mark.parametrize("marker", MARKERS)
def test_a_work_marker_line_is_free(marker):
    assert paragraph("# one", f"# {marker}: filed", "# two").lines == 2


def test_a_marker_continuation_line_counts():
    assert paragraph("# TODO: filed", "#   and its reason").lines == 1


def test_a_word_that_only_starts_like_a_marker_counts():
    assert paragraph("# TODOS are filed", "# BUGGY input").lines == 2


def test_an_empty_place_counts_nothing():
    assert paragraph().lines == 0
    assert paragraph("").lines == 0
