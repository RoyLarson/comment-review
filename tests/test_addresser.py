"""A place keeps its name when the prose around it changes.

!! THE PROPERTY, in Roy's words 2026-08-18: the census is a HASHED STATIC TABLE
-- exact, constant, fully enumerated -- and without that this scheme falls apart
rather than fails. `b7` means "after the seventh code line", so a code line
missed anywhere above a place RENAMES that place, silently and consistently.
These tests hold the naming to the enumeration.
"""

import tempfile  # noqa: I001  -- path shim below must import before addresser
import unittest
from pathlib import Path

from _paths import SCRIPTS  # noqa: F401
import addresser
import census
import pcst

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
    {"path": "a.py", "start": 1, "end": 2, "kind": "interval", "edit_start": 1},
    {"path": "a.py", "start": 2, "end": 2, "kind": "trailing-comment", "edit_start": 2},
    {"path": "a.py", "start": 3, "end": 5, "kind": "comment", "edit_start": 3},
    {"path": "a.py", "start": 6, "end": 6, "kind": "trailing-comment", "edit_start": 6},
    {"path": "a.py", "start": 6, "end": 6, "kind": "interval", "edit_start": 7},
]
B = [
    {"path": "b.py", "start": 1, "end": 2, "kind": "interval", "edit_start": 1},
    {"path": "b.py", "start": 2, "end": 3, "kind": "interval", "edit_start": 3},
    {"path": "b.py", "start": 3, "end": 3, "kind": "interval", "edit_start": 4},
]


def named(text, blocks):
    code = addresser.code_lines_of(text, blocks)
    return [addresser.address(b, code).split("@")[1] for b in blocks]


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
        self.assertEqual(named(WITH_PROSE, A)[1], "c0")
        self.assertEqual(named(WITH_PROSE, A)[3], "c1")

    def test_an_interval_names_the_gap_AFTER_its_bounding_line(self):
        # ! Read from `edit_start`, which the census states for the splice --
        # the addressing range cannot say it, because an interval spans the two
        # code lines around the gap rather than the gap itself.
        self.assertEqual(named(BARE, B)[1], "b1")

    def test_a_block_with_no_range_is_reported_not_guessed(self):
        self.assertEqual(addresser.address({"path": "a.py"}, [2, 6]), "")


class TestCodeOnTheFirstLine(unittest.TestCase):
    """The leading gap is `b0` even when it touches the first code line.

    !! FOUND ON REAL RUST, not on a fixture. `StarTraders/src/company.rs` opens
    `use std::fmt;` on line 1, so its leading interval spans `1-1` -- start AND
    end on the first code line -- where an earlier rule counted from the range
    and read that as the gap AFTER code line 1. Every Python file this was first
    written against began with a blank line or a module docstring, so its
    leading gap was `1-2` and the case could not arise.

    ! The range is not what answers it now: `edit_start` is 1 for the leading
    gap and 2 for the next, so the two are separated by what the census STATES
    rather than by what a consumer infers from the bounds.
    """

    SRC = "use std::fmt;\n\n#[derive(Debug)]\npub enum X {}\n"
    BLOCKS = [
        {"path": "c.rs", "start": 1, "end": 1, "kind": "interval", "edit_start": 1},
        {"path": "c.rs", "start": 1, "end": 3, "kind": "interval", "edit_start": 2},
        {"path": "c.rs", "start": 3, "end": 4, "kind": "interval", "edit_start": 4},
    ]

    def setUp(self):
        self.code = addresser.code_lines_of(self.SRC, self.BLOCKS)

    def test_code_starts_on_line_one(self):
        self.assertEqual(self.code[0], 1)

    def test_the_gap_before_it_is_b0_not_b1(self):
        self.assertEqual(addresser.address(self.BLOCKS[0], self.code), "c.rs@b0")

    def test_the_gap_after_it_is_b1(self):
        self.assertEqual(addresser.address(self.BLOCKS[1], self.code), "c.rs@b1")

    def test_every_gap_gets_its_own_name(self):
        named = [addresser.address(b, self.code) for b in self.BLOCKS]
        self.assertEqual(len(set(named)), len(named))


class TestTwoFilesOfTheSameName(unittest.TestCase):
    """A path is repo-relative, so same-named files in different packages differ.

    ! Checked because Python lets `pkg/a.py` and `pkg/sub/a.py` coexist and the
    address carries only the path. Verified 2026-08-18 over three such files:
    every address distinct.
    """

    def test_the_package_path_is_part_of_the_address(self):
        code = [1]
        one = {
            "path": "pkg/a.py",
            "start": 1,
            "end": 1,
            "kind": "interval",
            "edit_start": 1,
        }
        two = {
            "path": "pkg/sub/a.py",
            "start": 1,
            "end": 1,
            "kind": "interval",
            "edit_start": 1,
        }
        self.assertNotEqual(addresser.address(one, code), addresser.address(two, code))

    def test_a_windows_separator_is_normalised(self):
        # ! So a census written on Windows and read anywhere names one place.
        block = {
            "path": r"pkg\sub\a.py",
            "start": 1,
            "end": 1,
            "kind": "interval",
            "edit_start": 1,
        }
        self.assertEqual(addresser.address(block, [1]), "pkg.sub.a.py@b0")

    def test_a_census_without_edit_start_is_REFUSED_not_guessed(self):
        # !! The range alone cannot separate the two gaps of a one-line file,
        # which is the whole reason this reads `edit_start`. Falling back to it
        # would answer confidently and wrongly.
        old = {"path": "a.py", "start": 1, "end": 1, "kind": "interval"}
        self.assertEqual(addresser.address(old, [1]), "")


class TestAOneLineInitFile(unittest.TestCase):
    """Every package has one, and both its gaps used to be `b0`.

    !! Roy, 2026-08-18: "here it is everywhere -- package/__init__.py,
    package/sub-package/__init__.py". A one-line `__init__.py` emits two
    intervals both spanning `1-1` -- the gap before the import and the gap after
    it -- and `census.address` names them identically. `edit_start` is 1 and 2,
    which is what separates them.
    """

    SRC = "from .core import Engine\n"
    BLOCKS = [
        {
            "path": "package/__init__.py",
            "start": 1,
            "end": 1,
            "kind": "interval",
            "edit_start": 1,
        },
        {
            "path": "package/__init__.py",
            "start": 1,
            "end": 1,
            "kind": "interval",
            "edit_start": 2,
        },
    ]

    def test_the_line_addresses_are_identical(self):
        self.assertEqual({(b["start"], b["end"]) for b in self.BLOCKS}, {(1, 1)})

    def test_the_stable_addresses_are_not(self):
        code = addresser.code_lines_of(self.SRC, self.BLOCKS)
        named = [addresser.address(b, code) for b in self.BLOCKS]
        self.assertEqual(named, ["package.__init__.py@b0", "package.__init__.py@b1"])

    def test_a_subpackage_of_the_same_name_is_a_different_place(self):
        code = [1]
        sub = dict(self.BLOCKS[0], path="package/subpackage/__init__.py")
        self.assertNotEqual(
            addresser.address(sub, code), addresser.address(self.BLOCKS[0], code)
        )


if __name__ == "__main__":
    unittest.main()


class TestTheInverse(unittest.TestCase):
    """An address goes back to the file and the entries that carry it.

    ! The forward direction alone is half a tool: an agent that is handed
    `pkg.mod.py@b3` in a record has to get back to a line to read the code.
    """

    def test_a_dotted_path_resolves_against_the_census(self):
        self.assertEqual(
            addresser.undot("pkg.sub.a.py", ["pkg/sub/a.py", "other/a.py"]),
            "pkg/sub/a.py",
        )

    def test_two_paths_that_dot_alike_are_REFUSED(self):
        # !! THE DOTTED FORM IS NOT SELF-INVERTIBLE. `a/b.py` and `a.b.py` both
        # read `a.b.py`, and a dot in a FILE name is ordinary in most of the
        # eleven languages this census reads -- `app.test.js`, `types.d.ts`.
        # Picking one would answer a question nobody asked.
        self.assertEqual(addresser.undot("a.b.py", ["a/b.py", "a.b.py"]), "")

    def test_a_path_the_census_never_carried_resolves_to_nothing(self):
        self.assertEqual(addresser.undot("nope.py", ["a/b.py"]), "")

    def test_an_address_splits_into_path_and_folio(self):
        self.assertEqual(addresser.folio_of("pkg.mod.py@b3"), ("pkg.mod.py", "b3"))

    def test_a_string_with_no_folio_is_not_an_address(self):
        self.assertEqual(addresser.folio_of("pkg.mod.py"), ("", ""))

    def test_every_address_finds_its_own_entry_again(self):
        # ! STAMPED FIRST, because `resolve` READS the census's `place` rather
        # than recomputing one -- which is the whole point of the producer
        # stating it. A fixture built without the stamp resolves to nothing.
        code = addresser.code_lines_of(WITH_PROSE, A)
        stamped = [{**b, "address": addresser.address(b, code)} for b in A]
        for i, block in enumerate(stamped, 1):
            with self.subTest(entry=i):
                self.assertEqual(addresser.resolve(block["address"], stamped), [i])

    def test_an_address_nothing_carries_comes_back_empty(self):

        self.assertEqual(addresser.resolve("b.py@b99", B), [])


class TestAStaleCensusIsRefused(unittest.TestCase):
    """A census older than the file names places the code has left.

    !! THIS IS A MECHANISM, NOT A REMINDER. In one session the same mistake was
    made four times -- an oracle diff, a git reachability call, a coverage
    figure of 51%, and a `SHARED` row that listed one block -- each time by
    reading an artifact built three edits earlier and treating the result as a
    defect in the code. Naming the habit did not stop the fourth. `--check`
    exits 2 instead.
    """

    SRC = "X = 1\n# a note\nY = 2\n"
    BLOCKS = [
        {
            "path": "m.py",
            "start": 2,
            "end": 2,
            "kind": "comment",
            "edit_start": 2,
            "edit_end": 2,
            "raw_lines": ["# a note"],
            "whole_lines": True,
        }
    ]

    def test_the_census_matches_the_file_it_came_from(self):
        from galley import block_matches

        self.assertTrue(block_matches(self.SRC.splitlines(), self.BLOCKS[0]))

    def test_it_does_not_match_a_file_that_has_moved(self):
        # ! One line added ABOVE the block, which is what a prose edit does.
        moved = "import os\n" + self.SRC
        from galley import block_matches

        self.assertFalse(block_matches(moved.splitlines(), self.BLOCKS[0]))

    def test_the_addresses_differ_silently_and_neither_errors(self):
        # !! THE POINT. Both answer, both look right, and they disagree. A blank
        # line prepended -- which is what a prose edit does -- moves the code
        # down, so the block's stated `edit_start` now has NO code line before
        # it: `b1` becomes `b0`, naming a different place with no complaint.
        here = addresser.code_lines_of(self.SRC, self.BLOCKS)
        there = addresser.code_lines_of("\n" + self.SRC, self.BLOCKS)
        self.assertEqual(addresser.address(self.BLOCKS[0], here), "m.py@b1")
        self.assertEqual(addresser.address(self.BLOCKS[0], there), "m.py@b0")


class TestTheDeclarationSeries(unittest.TestCase):
    """`a0..aN` names a DECLARATION, so a docstring leaves the gap series.

    !! IT IS WHAT MAKES AN ADDRESS A SINGLE FACT. Measured 2026-08-18 over
    9,975 blocks in this repo, 28 places were answered by two blocks and 28 of
    28 were a docstring sharing a gap with the comment run beneath it. Naming a
    docstring for the gap it sits in put two different subjects at one address.
    """

    def _census(self, text):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "m.py"
            path.write_text(text, encoding="utf-8")
            got = census.census_for(path, text, census.language_for(path))
            lines = sorted(census.code_lines(text, got))
            for b in got:
                # ! The SUFFIX only. `census_for` names a block by the path it
                # was handed, and these are absolute temp paths -- the dotted
                # prefix is `main`'s to make repo-relative.
                b.address = addresser.address(vars(b), lines).split("@")[-1]
            return got

    NESTED = (
        '"""Module."""\n'
        "\n\n"
        "def outer():\n"
        '    """Outer."""\n'
        "\n"
        "    class Inner:\n"
        '        """Inner."""\n'
        "\n"
        "        def method(self):\n"
        '            """Method."""\n'
        "\n\n"
        "def after():\n"
        '    """After."""\n'
    )

    def test_the_series_is_SOURCE_order_not_walk_order(self):
        # !! `ast.walk` IS BREADTH FIRST, so `after` -- a top-level `def` --
        # comes back before the nested `Inner` and `method` that a reader meets
        # first. Ordering by `lineno` is the order down the page, and it is the
        # only one a human can check against the file.
        got = {
            b.anchor: b.address for b in self._census(self.NESTED) if b.declares >= 0
        }
        self.assertEqual(
            got,
            {
                "<module>": "a0",
                "outer": "a1",
                "Inner": "a2",
                "method": "a3",
                "after": "a4",
            },
        )

    def test_a_declaration_with_NO_docstring_still_has_a_place(self):
        # !! THE EMPTY ONES ARE THE POINT. An `add` says a constraint holds in
        # code and appears in no prose, so it must cite the place the prose is
        # missing from -- and a function with no docstring had none.
        got = self._census("def bare():\n    return 1\n")
        empty = [b for b in got if b.kind == "undocumented"]
        self.assertEqual(
            [(b.anchor, b.address) for b in empty],
            [("<module>", "a0"), ("bare", "a1")],
        )

    def test_an_empty_declaration_is_a_pure_INSERTION(self):
        # Its edit range is empty, so writing it inserts above the first
        # statement instead of overwriting it -- the interval convention.
        got = self._census("def bare():\n    return 1\n")
        bare = next(b for b in got if b.anchor == "bare")
        self.assertEqual((bare.edit_start, bare.edit_end), (2, 1))

    def test_filling_a_docstring_does_not_RENUMBER_the_series(self):
        # !! ONLY A CODE CHANGE SHIFTS IT, and stage 7b proves this tool makes
        # none. Adding a docstring does not add a declaration.
        without = {
            b.anchor: b.address for b in self._census("def f():\n    return 1\n")
        }
        with_doc = {
            b.anchor: b.address
            for b in self._census('def f():\n    """Doc."""\n    return 1\n')
        }
        self.assertEqual(without["f"], "a1")
        self.assertEqual(with_doc["f"], "a1")

    def test_an_empty_declaration_occupies_NO_code_lines(self):
        # ! Counting it as occupied would drop a real code line and renumber
        # every `b` below it.
        text = "def f():\n    return 1\n"
        got = self._census(text)
        self.assertEqual(census.code_lines(text, got), {1, 2})

    def test_two_declarations_of_the_SAME_NAME_get_different_addresses(self):
        # !! THE ANCHOR NAME WAS NEVER UNIQUE AND NEVER PROMISED TO BE. Roy,
        # 2026-08-18: "the anchor is the address. full stop." Three `run`s in
        # one file are three declarations, and the address is what tells them
        # apart.
        got = self._census(
            "class A:\n"
            "    def run(self):\n"
            '        """A."""\n'
            "class B:\n"
            "    def run(self):\n"
            '        """B."""\n'
        )
        runs = [b.address for b in got if b.anchor == "run"]
        self.assertEqual(len(runs), 2)
        self.assertEqual(len(set(runs)), 2, runs)

    def test_a_type_annotation_is_NOT_a_docstring(self):
        # !! A PEP 727 `Doc()` IS A TYPE ANNOTATION. Roy, 2026-08-18: "Type
        # annotations are not comments or docstrings ... we are not building a
        # type checker". The real docstrings beside it are untouched.
        got = self._census(
            '"""Module."""\n'
            "\n"
            "def widen(width: Annotated[int, Doc('How wide.')]) -> str:\n"
            '    """Widen."""\n'
            "    return str(width)\n"
        )
        prose = [b for b in got if b.kind not in pcst.HOLDS_NO_PROSE]
        self.assertEqual([b.anchor for b in prose], ["<module>", "widen"])
        self.assertNotIn("How wide.", " ".join(b.text for b in prose))


class TestTheTwoSeriesNameTheSameCodeLine(unittest.TestCase):
    """`cN` is ON code line N; `bN` is the gap ABOVE it. Same N, same line.

    !! SUPERSEDED, AND THE OLD READING IS WHY THIS EXISTS. While `c` counted
    from 1 and `b` from 0, `b3` and `c3` named DIFFERENT statements, and a
    reader pairing them attached a comment one line too high. Roy ruled `c`
    0-indexed 2026-08-19 -- "empty c0" on the first code line -- and the two
    series line up: code line N carries `bN` above it and `cN` on it.
    """

    SRC = "a = 1\n# about b\nb = 2\nc = 3  # beside c\n"
    BLOCKS = [
        {"path": "m.py", "start": 1, "end": 2, "kind": "interval", "edit_start": 1},
        {"path": "m.py", "start": 2, "end": 2, "kind": "comment", "edit_start": 2},
        {
            "path": "m.py",
            "start": 4,
            "end": 4,
            "kind": "trailing-comment",
            "edit_start": 4,
        },
    ]

    def setUp(self):
        self.code = addresser.code_lines_of(self.SRC, self.BLOCKS)

    def test_the_code_lines_are_1_3_and_4(self):
        self.assertEqual(self.code, [1, 3, 4])

    def test_the_first_code_line_is_c0(self):
        # ! 0-indexed, so the first code line is `c0` and not `c1`.
        on_first = {"path": "m.py", "start": 1, "end": 1, "kind": "trailing-comment"}
        self.assertEqual(addresser.address(on_first, self.code), "m.py@c0")

    def test_a_comment_above_the_SECOND_code_line_is_b1(self):
        self.assertEqual(addresser.address(self.BLOCKS[1], self.code), "m.py@b1")

    def test_a_trailing_comment_on_the_THIRD_code_line_is_c2(self):
        self.assertEqual(addresser.address(self.BLOCKS[2], self.code), "m.py@c2")

    def test_bN_and_cN_name_THE_SAME_code_line(self):
        # !! THE POINT, and the reverse of what this class once held. `b1` is
        # the gap above the 2nd code line; `c1` is on the 2nd code line.
        above = self.BLOCKS[1]  # the comment run, in the gap above code line 3
        beside = {"path": "m.py", "start": 3, "end": 3, "kind": "trailing-comment"}
        self.assertEqual(addresser.address(above, self.code), "m.py@b1")
        self.assertEqual(addresser.address(beside, self.code), "m.py@c1")


class TestAnAnchorsPlacesAreASKED_FOR(unittest.TestCase):
    """`for_anchor` -- which address is this anchor's `a`, `b` or `c`.

    !! ASKING BY POSITION BREAKS ON THE NEXT LANGUAGE. Python's docstring sits
    AFTER its `def` and Rust's `///` BEFORE its `fn`, so "the block above the
    declaration" names the doc in one and the comment above it in the other. An
    agent that counted would be right until the census reached a language that
    lays its prose out the other way. This asks the census, which parsed it.
    """

    SRC = (
        '"""Module."""\n\nBUDGET = 3\n\n\ndef go(n):\n    """Do it."""\n    return n\n'
    )

    def setUp(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "m.py"
            path.write_text(self.SRC, encoding="utf-8")
            got = census.census_for(path, self.SRC, census.language_for(path))
            lines = sorted(census.code_lines(self.SRC, got))
            for b in got:
                b.address = addresser.address(vars(b), lines)
            self.blocks = [vars(b) for b in got]

    def _at(self, anchor, series):
        # ! The FOLIO only -- the temp path is noise here.
        return [
            b["address"].split("@")[-1]
            for b in addresser.for_anchor(anchor, series, self.blocks)
        ]

    def test_a_declaration_has_a_place_in_every_series(self):
        self.assertEqual(self._at("go", "a"), ["a1"])
        self.assertEqual(self._at("go", "c"), ["c1"])
        self.assertEqual(self._at("go", "b"), ["b1"])

    def test_the_MODULE_has_an_a_and_a_b_but_no_c(self):
        # !! It has no line to open on, so nothing can sit beside it. Its `b` is
        # `b0` by definition -- where a licence header or a shebang goes.
        self.assertEqual(self._at("<module>", "a"), ["a0"])
        self.assertEqual(self._at("<module>", "b"), ["b0"])
        self.assertEqual(self._at("<module>", "c"), [])

    def test_an_anchor_the_census_never_stamped_answers_nothing(self):
        # ! Empty, not a guess. A lexical-tier language resolves no anchors at
        # all, and the caller reports that rather than being handed a neighbour.
        self.assertEqual(self._at("nosuchname", "a"), [])
        self.assertEqual(self._at("nosuchname", "b"), [])

    def test_the_c_it_names_is_the_DECLARATIONS_own_line(self):
        found = addresser.for_anchor("go", "c", self.blocks)
        self.assertEqual([b["start"] for b in found], [6])
        self.assertIn(found[0]["kind"], addresser.SHARES_ITS_LINE)
