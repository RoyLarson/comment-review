"""The file's own matter: which lines open and close a file as its own prose."""

import pytest

from comment_review.reading.matter import file_matter


def test_front_run_is_the_prose_from_the_opening_line_to_the_first_other_line():
    matter = file_matter(6, 1, {1, 2, 4})
    assert matter.front == range(1, 3)


def test_a_run_with_code_before_it_is_not_front_matter():
    # Line 1 is code: nothing in the prose set opens the file.
    matter = file_matter(4, 1, {2, 3})
    assert matter.front == range(1, 1)


def test_back_run_is_the_prose_below_the_last_other_line():
    matter = file_matter(8, 1, {6, 8})
    assert matter.back == range(8, 9)


def test_a_run_above_the_last_code_line_is_not_back_matter():
    # Line 5 is code and line 5 is the file's last line.
    matter = file_matter(5, 1, {3, 4})
    assert matter.back == range(6, 6)


def test_a_file_that_is_all_prose_is_one_front_run():
    matter = file_matter(3, 1, {1, 2, 3})
    assert (matter.front, matter.back) == (range(1, 4), range(4, 4))


def test_the_matter_opens_on_the_line_the_caller_names():
    # A reader whose shebang is not prose names line 2.
    matter = file_matter(4, 2, {2, 3})
    assert matter.front == range(2, 4)


def test_a_blank_opening_line_leaves_no_front_matter():
    matter = file_matter(4, 2, {3})
    assert matter.front == range(2, 2)


@pytest.mark.parametrize(
    "start,end,parts",
    [
        # A run across the blank that ends the front matter is cut there.
        (1, 3, [(1, 1, True), (3, 3, False)]),
        # A run across the blank that opens the back matter is cut there.
        (5, 8, [(5, 6, False), (8, 8, True)]),
        # A run in neither stays whole.
        (5, 6, [(5, 6, False)]),
    ],
)
def test_parts_cut_a_run_at_the_matter_edges_and_trim_to_its_comments(
    start, end, parts
):
    held = {1, 3, 5, 6, 8}
    matter = file_matter(8, 1, held)
    assert matter.parts(start, end, held) == parts


def test_parts_keep_a_run_whole_across_a_line_that_is_prose():
    # Line 2 is a blank line inside a delimited comment: prose, not an edge.
    matter = file_matter(3, 1, {1, 2, 3})
    assert matter.parts(1, 3, {1, 2, 3}) == [(1, 3, True)]


def test_a_documentation_line_ends_the_matter_and_stays_in_its_part():
    # Line 2 is documentation: not prose, so the front matter ends above it,
    # but the run has a comment on it, so the part below the edge keeps it.
    matter = file_matter(4, 1, {1, 3})
    assert matter.front == range(1, 2)
    assert matter.parts(1, 3, {1, 2, 3}) == [(1, 1, True), (2, 3, False)]


def test_a_documentation_line_at_the_foot_leaves_no_back_matter():
    matter = file_matter(4, 1, {3})
    assert matter.back == range(5, 5)


def test_with_a_module_docstring_every_comment_above_it_is_front_matter():
    # Line 2 is blank, and it ends nothing above the docstring on lines 5-6.
    matter = file_matter(8, 1, {1, 3, 4}, module_doc=range(5, 7))
    assert matter.front == range(1, 5)
    assert matter.parts(1, 4, {1, 3, 4}) == [(1, 4, True)]


def test_with_a_module_docstring_the_front_matter_opens_where_the_caller_names():
    matter = file_matter(5, 2, {3}, module_doc=range(4, 5))
    assert matter.front == range(2, 4)


def test_a_module_docstring_on_the_opening_line_leaves_no_front_matter():
    matter = file_matter(3, 1, {3}, module_doc=range(1, 2))
    assert matter.front == range(1, 1)


def test_with_no_module_docstring_a_blank_line_ends_the_front_matter():
    matter = file_matter(5, 1, {1, 3})
    assert matter.front == range(1, 2)


def test_with_a_closing_docstring_every_comment_below_it_is_back_matter():
    # Line 5 is blank, and it ends nothing below the docstring on line 2.
    matter = file_matter(6, 1, {3, 4, 6}, closing_doc=range(2, 3))
    assert matter.back == range(3, 7)


def test_a_blank_last_line_leaves_no_back_matter_below_a_closing_docstring():
    matter = file_matter(5, 1, {3, 4}, closing_doc=range(2, 3))
    assert matter.back == range(6, 6)


def test_a_closing_docstring_on_the_last_line_leaves_no_back_matter():
    matter = file_matter(4, 1, {3}, closing_doc=range(4, 5))
    assert matter.back == range(5, 5)


def test_with_no_closing_docstring_a_blank_line_ends_the_back_matter():
    matter = file_matter(6, 1, {2, 4, 6})
    assert matter.back == range(6, 7)


def test_with_no_code_everything_past_the_front_matter_is_one_back_matter():
    matter = file_matter(5, 1, {1, 3, 5}, codeless=True)
    assert (matter.front, matter.back) == (range(1, 2), range(2, 6))


def test_with_no_code_everything_past_the_module_docstring_is_one_back_matter():
    # Line 6 is documentation inside it, and it goes with it.
    matter = file_matter(8, 1, {1, 5, 8}, module_doc=range(3, 4), codeless=True)
    assert (matter.front, matter.back) == (range(1, 3), range(4, 9))


def test_with_no_code_a_blank_last_line_leaves_no_back_matter():
    matter = file_matter(4, 1, {1, 3}, codeless=True)
    assert (matter.front, matter.back) == (range(1, 2), range(5, 5))
