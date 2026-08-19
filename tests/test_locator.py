"""The locator answers one question: what is the ADDRESS of this line.

! It makes no ruling. A line held by two entries returns both, because an
interval's range spans the two CODE LINES bounding the gap -- so a code line
ends one interval and starts the next, and picking between them here would be a
placement decision the reviewer owns.
"""

import unittest

import locator
from _paths import SCRIPTS  # noqa: F401

CENSUS = [
    {"path": "a.py", "start": 1, "end": 10, "kind": "docstring"},
    {"path": "a.py", "start": 12, "end": 14, "kind": "interval"},
    {"path": "a.py", "start": 14, "end": 20, "kind": "interval"},
    {"path": "b.py", "start": 1, "end": 3, "kind": "comment"},
]


class TestParsingTheLine(unittest.TestCase):
    def test_a_windows_path_keeps_its_drive_colon(self):
        # ! Split on the LAST colon, or `C:\x\a.py:5` loses its drive.
        self.assertEqual(locator.parse_at("C:/x/a.py:5"), ("C:/x/a.py", 5))

    def test_a_backslash_path_is_read_as_the_census_writes_it(self):
        self.assertEqual(locator.parse_at(r"x\a.py:5"), ("x/a.py", 5))

    def test_no_line_is_refused(self):
        self.assertIsInstance(locator.parse_at("a.py"), str)

    def test_line_zero_is_refused(self):
        # ! Lines are 1-based everywhere else in this system.
        self.assertIsInstance(locator.parse_at("a.py:0"), str)


class TestFindingTheSpot(unittest.TestCase):
    def test_a_line_inside_one_entry_returns_it(self):
        self.assertEqual([i for i, _ in locator.at(CENSUS, "a.py", 5)], [1])

    def test_a_shared_boundary_returns_BOTH_entries(self):
        # !! Line 14 ends one interval and starts the next. Measured on a real
        # census: 90 lines were held by more than one entry, so this is the
        # common case rather than the corner.
        self.assertEqual([i for i, _ in locator.at(CENSUS, "a.py", 14)], [2, 3])

    def test_the_index_counts_every_entry_including_intervals(self):
        # ! It is the numbering the join and the record file already use, which
        # is what makes a filtered census citable against the full one.
        self.assertEqual([i for i, _ in locator.at(CENSUS, "b.py", 2)], [4])

    def test_a_line_no_entry_holds_returns_nothing(self):
        self.assertEqual(locator.at(CENSUS, "a.py", 11), [])

    def test_another_file_is_not_matched(self):
        self.assertEqual(locator.at(CENSUS, "c.py", 5), [])


class TestTheCensusShape(unittest.TestCase):
    def test_a_bare_list_is_read(self):
        self.assertEqual(len(locator.entries(CENSUS)), 4)

    def test_a_wrapped_census_is_read(self):
        self.assertEqual(len(locator.entries({"blocks": CENSUS})), 4)

    def test_anything_else_reads_as_no_blocks(self):
        self.assertEqual(locator.entries({"nope": 1}), [])


if __name__ == "__main__":
    unittest.main()
