"""A place keeps its name when the prose around it changes.

!! THE PROPERTY, in Roy's words 2026-08-18: the census is a HASHED STATIC TABLE
-- exact, constant, fully enumerated -- and without that this scheme falls apart
rather than fails. `b7` means "after the seventh code line", so a code line
missed anywhere above a place RENAMES that place, silently and consistently.
These tests hold the naming to the enumeration.
"""

import unittest  # noqa: I001  -- path shim below must import before addresser

from _paths import SCRIPTS  # noqa: F401
import addresser

# Roy's two files: the same two statements, one with comments and one without.
WITH_PROSE = (
    "\n"
    'my_code_is_awesome ="awesomeness" # I know\n'
    "# I like typing but\n"
    "# I like things getting done\n"
    "# more\n"
    'my_goals_are_even_better = "Yeah for me!" # Still working\n'
)
BARE = (
    '\nmy_code_is_awesome = "awesomeness"\nmy_goals_are_even_better = "Yeah for me!"\n'
)

A = [
    {"path": "a.py", "start": 1, "end": 2, "kind": "interval"},
    {"path": "a.py", "start": 2, "end": 2, "kind": "trailing-comment"},
    {"path": "a.py", "start": 3, "end": 5, "kind": "comment"},
    {"path": "a.py", "start": 6, "end": 6, "kind": "trailing-comment"},
    {"path": "a.py", "start": 6, "end": 6, "kind": "interval"},
]
B = [
    {"path": "b.py", "start": 1, "end": 2, "kind": "interval"},
    {"path": "b.py", "start": 2, "end": 3, "kind": "interval"},
    {"path": "b.py", "start": 3, "end": 3, "kind": "interval"},
]


def named(text, blocks):
    code = addresser.code_lines_of(text, blocks)
    return [addresser.stable(b, code).split("@")[1] for b in blocks]


class TestTwoFilesDifferingOnlyInComments(unittest.TestCase):
    def test_the_code_lines_are_the_same_two_in_both(self):
        self.assertEqual(addresser.code_lines_of(WITH_PROSE, A), [2, 6])
        self.assertEqual(addresser.code_lines_of(BARE, B), [2, 3])

    def test_the_same_gap_gets_the_same_name_prose_or_not(self):
        # !! THE WHOLE POINT. In one file the gap between the two statements
        # holds three comment lines; in the other it is empty. Both are `b1`.
        self.assertEqual(named(WITH_PROSE, A)[2], "b1")
        self.assertEqual(named(BARE, B)[1], "b1")

    def test_the_gap_after_the_last_statement_agrees(self):
        self.assertEqual(named(WITH_PROSE, A)[4], "b2")
        self.assertEqual(named(BARE, B)[2], "b2")

    def test_the_gap_before_the_first_statement_agrees(self):
        self.assertEqual(named(WITH_PROSE, A)[0], "b0")
        self.assertEqual(named(BARE, B)[0], "b0")

    def test_line_addresses_do_NOT_agree_which_is_why_this_exists(self):
        self.assertNotEqual(
            [(b["start"], b["end"]) for b in A],
            [(b["start"], b["end"]) for b in B],
        )


class TestOnAndBetween(unittest.TestCase):
    def test_a_trailing_comment_sits_ON_its_code_line(self):
        self.assertEqual(named(WITH_PROSE, A)[1], "c1")
        self.assertEqual(named(WITH_PROSE, A)[3], "c2")

    def test_an_interval_names_the_gap_AFTER_its_first_bounding_line(self):
        # ! `<=` and not `<`. An interval's `start` IS a code line, so that
        # line is counted -- `<` named the gap before it instead.
        self.assertEqual(named(BARE, B)[1], "b1")

    def test_a_block_with_no_range_is_reported_not_guessed(self):
        self.assertEqual(addresser.stable({"path": "a.py"}, [2, 6]), "")


if __name__ == "__main__":
    unittest.main()


class TestCodeOnTheFirstLine(unittest.TestCase):
    """The leading gap is `b0` even when it touches the first code line.

    !! FOUND ON REAL RUST, not on a fixture. `StarTraders/src/company.rs` opens
    `use std::fmt;` on line 1, so its leading interval is `1-1` -- start AND end
    on the first code line -- and counting `code <= start` read that as the gap
    AFTER code line 1. Every Python file this was first written against began
    with a blank line or a module docstring, so its leading gap was `1-2` and
    the case could not arise.
    """

    SRC = "use std::fmt;\n\n#[derive(Debug)]\npub enum X {}\n"
    BLOCKS = [
        {"path": "c.rs", "start": 1, "end": 1, "kind": "interval"},
        {"path": "c.rs", "start": 1, "end": 3, "kind": "interval"},
        {"path": "c.rs", "start": 3, "end": 4, "kind": "interval"},
    ]

    def setUp(self):
        self.code = addresser.code_lines_of(self.SRC, self.BLOCKS)

    def test_code_starts_on_line_one(self):
        self.assertEqual(self.code[0], 1)

    def test_the_gap_before_it_is_b0_not_b1(self):
        self.assertEqual(addresser.stable(self.BLOCKS[0], self.code), "c.rs@b0")

    def test_the_gap_after_it_is_b1(self):
        self.assertEqual(addresser.stable(self.BLOCKS[1], self.code), "c.rs@b1")

    def test_every_gap_gets_its_own_name(self):
        named = [addresser.stable(b, self.code) for b in self.BLOCKS]
        self.assertEqual(len(set(named)), len(named))


class TestTwoFilesOfTheSameName(unittest.TestCase):
    """A path is repo-relative, so same-named files in different packages differ.

    ! Checked because Python lets `pkg/a.py` and `pkg/sub/a.py` coexist and the
    address carries only the path. Verified 2026-08-18 over three such files:
    every address distinct.
    """

    def test_the_package_path_is_part_of_the_address(self):
        code = [1]
        one = {"path": "pkg/a.py", "start": 1, "end": 1, "kind": "interval"}
        two = {"path": "pkg/sub/a.py", "start": 1, "end": 1, "kind": "interval"}
        self.assertNotEqual(addresser.stable(one, code), addresser.stable(two, code))

    def test_a_windows_separator_is_normalised(self):
        # ! So a census written on Windows and read anywhere names one place.
        block = {"path": r"pkg\sub\a.py", "start": 1, "end": 1, "kind": "interval"}
        self.assertEqual(addresser.stable(block, [1]), "pkg/sub/a.py@b0")
