"""The locator answers one question: what is the ADDRESS of this line.

! It makes no ruling. A line held by two entries returns both, because an
interval's range spans the two CODE LINES bounding the gap -- so a code line
ends one interval and starts the next, and picking between them here would be a
placement decision the reviewer owns.
"""

import unittest  # noqa: I001  -- path shim below must import before locator
from pathlib import Path

from _paths import SCRIPTS  # noqa: F401
import lexer
import page
import locator

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
        self.assertEqual(len(locator.entries({"paragraphs": CENSUS})), 4)

    def test_anything_else_reads_as_no_blocks(self):
        self.assertEqual(locator.entries({"nope": 1}), [])


class TestTheFilteredCensusIsAProjection(unittest.TestCase):
    """`census.py --filtered` narrows the VIEW and never the numbering.

    !! The index is the whole contract. A reviewer cites a paragraph by its number
    and the join resolves that number against the FULL census, so a filtered
    view that renumbered would make every citation resolve to the wrong paragraph
    with nothing able to tell. Measured 2026-08-18 over two files: 124 prose
    paragraphs, every filtered index naming the same paragraph as the full census, and
    822 intervals collapsed into 105 run lines.
    """

    import re as _re

    # index, place, line range, kind -- the listing's first four columns.
    PARAGRAPH = _re.compile(r"^\s*(\d+)\s+(@\S+)\s+(\S+)\s+(\S+)\s")

    def _indexed(self, text):
        out = {}
        for line in text.split("\n"):
            m = self.PARAGRAPH.match(line)
            # ! The SAME set the census collapses on, read from `page` rather
            # than listed here. A hand-written tuple said ("interval",
            # "no-prose") and went stale the day `margin` and `undocumented`
            # joined the collapse -- 3,282 margin rows appeared in the full
            # listing and in no filtered one, so the two could not be compared.
            if m and m.group(4) not in (*page.HOLDS_NO_PROSE, "no-prose"):
                out[int(m.group(1))] = m.group(2)
        return out

    def test_a_filtered_index_names_the_same_block_as_the_full_one(self):
        import subprocess
        import sys as _sys

        target = SCRIPTS / "locator.py"
        root = SCRIPTS.parent.parent.parent.parent.parent

        def run(*extra):
            out = subprocess.run(
                [
                    _sys.executable,
                    str(SCRIPTS / "census.py"),
                    "--repo",
                    str(root),
                    *extra,
                    str(target),
                ],
                capture_output=True,
                text=True,
                cwd=str(root),
            )
            self.assertEqual(out.returncode, 0, out.stderr[-400:])
            return out.stdout

        full, filtered = self._indexed(run()), self._indexed(run("--filtered"))
        self.assertTrue(full, "the full census listed no prose paragraph")
        self.assertEqual(full, filtered)


class TestAPlaceAtLineZeroIsReachable(unittest.TestCase):
    """The empty places are exactly the ones a range test cannot find.

    !! AN `add` CITES AN EMPTY PLACE, and an empty place occupies NO LINE. An
    `interval` with nothing in it and a declaration with no docstring are both
    at line 0, so `start <= line <= end` can never match one -- and the brief
    tells a reviewer to ask the locator for precisely those. **Measured
    2026-08-19 on a seven-line file: 4 of 9 places unreachable by any line,
    every one an `interval` or an `undocumented`.** An `add` above an ordinary
    statement had no sanctioned route at all.

    ! The fix reads `edit_start` -- where prose WOULD go, and the same field the
    galley splices at -- so the place a lookup names is the place a write lands
    in.
    """

    SRC = '"""Module doc."""\n\nimport os\n\n\ndef f():\n    return os\n'

    def setUp(self):
        path = Path("m.py")
        built = page.page_for(path, self.SRC, lexer.language_for(path))
        for b in built:
            b.path = "m.py"
        self.paragraphs = [vars(b) for b in built]
        self.last = len(self.SRC.splitlines())

    def _reachable(self):
        seen = set()
        # ! `last + 1` because the gap AFTER the last line inserts one past the
        # end, which is where an append goes.
        for n in range(1, self.last + 2):
            for _, b in locator.at(self.paragraphs, "m.py", n):
                seen.add(b["address"])
        return seen

    def test_the_fixture_really_holds_places_at_line_zero(self):
        # ! Guards the guard: a fixture with no empty places would pass every
        # assertion below without exercising anything.
        empty = [b for b in self.paragraphs if b["start"] == 0]
        self.assertTrue(empty, "no place at line 0 in the fixture")

    def test_every_place_is_reachable_by_some_line(self):
        named = {b["address"] for b in self.paragraphs}
        self.assertEqual(sorted(named - self._reachable()), [])

    def test_an_empty_place_is_found_where_it_would_INSERT(self):
        gap = next(
            b for b in self.paragraphs if b["kind"] == "interval" and b["start"] == 0
        )
        got = locator.at(self.paragraphs, "m.py", gap["edit_start"])
        self.assertIn(gap["address"], [b["address"] for _, b in got])

    def test_ONE_line_answers_with_several_places(self):
        # !! Which is correct and is why the caller reads the KIND. A line can
        # carry the gap above it, the room beside it, and a declaration's
        # absent docstring at once.
        got = locator.at(self.paragraphs, "m.py", self.last)
        self.assertGreater(len(got), 1)
        self.assertEqual(len({b["address"] for _, b in got}), len(got))

    def test_a_place_WITH_lines_is_not_returned_twice(self):
        # ! Matching the edit range for every place would return a prose
        # paragraph once for its lines and again for its insertion point.
        for n in range(1, self.last + 2):
            got = locator.at(self.paragraphs, "m.py", n)
            with self.subTest(line=n):
                self.assertEqual(len(got), len({b["address"] for _, b in got}))
