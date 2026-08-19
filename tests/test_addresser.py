"""A place keeps its name when the prose around it changes.

!! THE PROPERTY, in Roy's words 2026-08-18: the census is a HASHED STATIC TABLE
-- exact, constant, fully enumerated -- and without that this scheme falls apart
rather than fails. `b7` means "after the seventh code line", so a code line
missed anywhere above a place RENAMES that place, silently and consistently.
These tests hold the naming to the enumeration.
"""

import collections  # noqa: I001  -- path shim below must import before addresser
import contextlib
import io
import tempfile
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
    {
        "path": "a.py",
        "start": 2,
        "end": 2,
        "kind": "trailing-comment",
        "edit_start": 2,
        "edit_column": 8,
    },
    {"path": "a.py", "start": 3, "end": 5, "kind": "comment", "edit_start": 3},
    {
        "path": "a.py",
        "start": 6,
        "end": 6,
        "kind": "trailing-comment",
        "edit_start": 6,
        "edit_column": 8,
    },
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
        self.assertEqual(addresser.address(block, [1]), "pkg:sub:a.py@b0")

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
        self.assertEqual(named, ["package:__init__.py@b0", "package:__init__.py@b1"])

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

    def test_a_flattened_path_resolves_against_the_census(self):
        self.assertEqual(
            addresser.unflatten("pkg:sub:a.py", ["pkg/sub/a.py", "other/a.py"]),
            "pkg/sub/a.py",
        )

    def test_two_paths_that_FLATTEN_alike_are_REFUSED(self):
        # !! THE DOTTED FORM IS NOT SELF-INVERTIBLE. `a/b.py` and `a.b.py` both
        # read `a.b.py`, and a dot in a FILE name is ordinary in most of the
        # eleven languages this census reads -- `app.test.js`, `types.d.ts`.
        # Picking one would answer a question nobody asked.
        self.assertEqual(addresser.unflatten("a:b.py", ["a/b.py", "a:b.py"]), "")

    def test_a_path_the_census_never_carried_resolves_to_nothing(self):
        self.assertEqual(addresser.unflatten("nope.py", ["a/b.py"]), "")

    def test_an_address_splits_into_path_and_folio(self):
        self.assertEqual(addresser.folio_of("pkg:mod.py@b3"), ("pkg:mod.py", "b3"))

    def test_a_string_with_no_folio_is_not_an_address(self):
        self.assertEqual(addresser.folio_of("pkg:mod.py"), ("", ""))

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
            "edit_column": 0,
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
            b.address: b.anchor for b in self._census(self.NESTED) if b.declares >= 0
        }
        # !! KEYED BY ADDRESS NOW, because an anchor is a LINE OF CODE and two
        # declarations can be spelled alike. The address is the unique half.
        # ! The module keeps `<module>`: it is the one address with no line of
        # code, and that is the name the LANGUAGE gives module-level code.
        self.assertEqual(
            got,
            {
                "a0": "<module>",
                "a1": "def outer():",
                "a2": "    class Inner:",
                "a3": "        def method(self):",
                "a4": "def after():",
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
            [("<module>", "a0"), ("def bare():", "a1")],
        )

    def test_an_empty_declaration_is_a_pure_INSERTION(self):
        # Its edit range is empty, so writing it inserts above the first
        # statement instead of overwriting it -- the interval convention.
        got = self._census("def bare():\n    return 1\n")
        bare = next(b for b in got if b.anchor == "def bare():")
        self.assertEqual((bare.edit_start, bare.edit_end), (2, 1))

    def test_filling_a_docstring_does_not_RENUMBER_the_series(self):
        # !! ONLY A CODE CHANGE SHIFTS IT, and stage 7b proves this tool makes
        # none. Adding a docstring does not add a declaration.
        # ! Only the `a` series -- the `b` above the `def` and the `c` beside
        # it carry the SAME anchor, because one anchor has many addresses, so a
        # dict keyed on the anchor alone would keep whichever came last.
        without = {
            b.anchor: b.address
            for b in self._census("def f():\n    return 1\n")
            if b.declares >= 0
        }
        with_doc = {
            b.anchor: b.address
            for b in self._census('def f():\n    """Doc."""\n    return 1\n')
            if b.declares >= 0
        }
        self.assertEqual(without["def f():"], "a1")
        self.assertEqual(with_doc["def f():"], "a1")

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
        # !! AND THE ANCHOR IS NOW THE LINE, which is spelled alike too --
        # `    def run(self):` twice. The address is still what separates them,
        # which is the same rule read one level down.
        runs = [
            b.address
            for b in got
            if b.anchor == "    def run(self):" and b.declares >= 0
        ]
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
        self.assertEqual(
            [b.anchor for b in prose],
            [
                "<module>",
                "def widen(width: Annotated[int, Doc('How wide.')]) -> str:",
            ],
        )
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
            "edit_column": 8,
        },
    ]

    def setUp(self):
        self.code = addresser.code_lines_of(self.SRC, self.BLOCKS)

    def test_the_code_lines_are_1_3_and_4(self):
        self.assertEqual(self.code, [1, 3, 4])

    def test_the_first_code_line_is_c0(self):
        # ! 0-indexed, so the first code line is `c0` and not `c1`.
        on_first = {
            "path": "m.py",
            "start": 1,
            "end": 1,
            "kind": "trailing-comment",
            "edit_column": 8,
        }
        self.assertEqual(addresser.address(on_first, self.code), "m.py@c0")

    def test_a_comment_above_the_SECOND_code_line_is_b1(self):
        self.assertEqual(addresser.address(self.BLOCKS[1], self.code), "m.py@b1")

    def test_a_trailing_comment_on_the_THIRD_code_line_is_c2(self):
        self.assertEqual(addresser.address(self.BLOCKS[2], self.code), "m.py@c2")

    def test_bN_and_cN_name_THE_SAME_code_line(self):
        # !! THE POINT, and the reverse of what this class once held. `b1` is
        # the gap above the 2nd code line; `c1` is on the 2nd code line.
        above = self.BLOCKS[1]  # the comment run, in the gap above code line 3
        beside = {
            "path": "m.py",
            "start": 3,
            "end": 3,
            "kind": "trailing-comment",
            "edit_column": 8,
        }
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
        # !! ONE ANCHOR, THREE ADDRESSES. The declaration's line is the anchor
        # of its own `a`, of the `b` above it and of the `c` beside it.
        self.assertEqual(self._at("def go(n):", "a"), ["a1"])
        self.assertEqual(self._at("def go(n):", "c"), ["c1"])
        self.assertEqual(self._at("def go(n):", "b"), ["b1"])

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
        found = addresser.for_anchor("def go(n):", "c", self.blocks)
        self.assertEqual([b["start"] for b in found], [6])
        # ! The one fact that decides it -- not a list of kinds. `SHARES_ITS_LINE`
        # was a second way to ask, and it disagreed with this one.
        self.assertTrue(found[0]["edit_column"])


class TestTheAddresserReadsTheCensusNeverTheTree(unittest.TestCase):
    """It takes no `--repo`, and every question it answers is census-internal.

    !! CHECKING THE FILE WOULD ASSERT THAT LINE NUMBERS STILL MATTER, which is
    what an address exists to stop. Roy, 2026-08-19: *"not necessary for
    addresser to do the staleness sweep as long as the original census is still
    an available document ... In a small way it is the addresser stating the
    line numbers matter still."*

    ! A sweep was here and it refused a census built SECONDS earlier on every
    non-Python file carrying a trailing comment -- and masked a real collision
    `--check` exists to report. Staleness belongs where a file is WRITTEN;
    `galley.block_matches` refuses a stale range before it splices.
    """

    def _run(self, *args):
        import subprocess
        import sys as _sys

        return subprocess.run(
            [_sys.executable, str(SCRIPTS / "addresser.py"), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

    def test_it_reads_no_file_but_the_census(self):
        text = (SCRIPTS / "addresser.py").read_text(encoding="utf-8")
        body = text.split('"""', 2)[-1]
        self.assertEqual(body.count("read_text"), 1, "only the census is read")
        self.assertNotIn("from galley import", body)

    def test_it_takes_no_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            census = Path(tmp) / "c.json"
            census.write_text("[]", encoding="utf-8")
            out = self._run("--census", str(census), "--repo", tmp, "--check")
            self.assertNotEqual(out.returncode, 0)
            self.assertIn("unrecognized arguments: --repo", out.stderr)

    def test_check_answers_on_a_census_of_a_file_that_has_since_CHANGED(self):
        # !! THE POINT. The census is the document; the tree may have moved on.
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "m.py"
            src.write_text("# a note\nx = 1\n", encoding="utf-8")
            got = census.census_for(
                src, src.read_text(encoding="utf-8"), census.language_for(src)
            )
            lines = sorted(census.code_lines(src.read_text(encoding="utf-8"), got))
            for b in got:
                b.address = addresser.address(vars(b), lines)
            census_json = Path(tmp) / "c.json"
            census_json.write_text(
                __import__("json").dumps([vars(b) for b in got], default=str),
                encoding="utf-8",
            )
            src.write_text("import os\n\n\n# a note\nx = 1\n", encoding="utf-8")
            out = self._run("--census", str(census_json), "--check")
            self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
            self.assertIn("blocks addressed", out.stdout)


class TestAMidLineCommentTakesTheLineItSitsOn(unittest.TestCase):
    """One fact decides "shares its line", and the producer states it.

    !! IT WAS DECIDED TWICE AND THE TWO DISAGREED. `address()` read a list of
    KINDS; `code_lines_of` read the block. A `comment` opened after a
    statement is in neither list and has a non-zero `edit_column`, so it took a `b`
    folio for a line it sits ON -- and that folio then named the comment AND the
    gap. Measured 2026-08-19 on `let b = 2; /* opens` / `and closes */`: `@b1`
    resolved to an empty interval, so every text check on the comment read "".
    """

    SRC = "let a = 1;\nlet b = 2; /* opens\nand closes */\nlet c = 3;\n"

    def _census(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "s.js"
            path.write_text(self.SRC, encoding="utf-8")
            got = census.census_for(path, self.SRC, census.language_for(path))
            lines = sorted(census.code_lines(self.SRC, got))
            for b in got:
                b.address = addresser.address(vars(b), lines).split("@")[-1]
            return got

    def test_the_comment_takes_a_c_because_code_precedes_it(self):
        got = self._census()
        mid = next(b for b in got if b.kind == "comment")
        self.assertTrue(mid.edit_column)
        self.assertTrue(mid.address.startswith("c"), mid.address)

    def test_no_address_names_two_blocks(self):
        seen = collections.Counter(b.address for b in self._census())
        self.assertEqual([a for a, n in seen.items() if n > 1], [])

    def test_every_line_has_exactly_one_address(self):
        hits = collections.Counter()
        for b in self._census():
            if b.start >= 1:
                for n in range(b.start, b.end + 1):
                    hits[n] += 1
        self.assertEqual(
            {n: hits.get(n, 0) for n in range(1, len(self.SRC.splitlines()) + 1)},
            {1: 1, 2: 1, 3: 1, 4: 1},
        )

    def test_the_gap_is_not_reported_EMPTY_over_lines_the_comment_holds(self):
        # ! `blocks_in` asks whether a block OVERLAPS the gap, not whether it
        # STARTS in one. The comment begins on the bounding code line and runs
        # into the gap below, so a start test read the gap as empty and emitted
        # an interval over the comment's own second line.
        got = self._census()
        self.assertEqual([b for b in got if b.kind == "interval" and b.start == 3], [])


class TestTheSeparatorIsAPathCannotHoldIt(unittest.TestCase):
    """`:` separates path segments, so a flattened path is INVERTIBLE.

    !! IT WAS `.` UNTIL 2026-08-19, AND A DOT IS ORDINARY IN A FILENAME.
    `a/b.py` and `a.b.py` both flattened to `a.b.py`, so every one of their
    addresses collided -- `@a0`, `@b0`, `@b1`, `@c0`, all of them -- and
    `--check` reported "8 of 8 blocks addressed" because it compares only within
    one path. Roy: *"lets use an illegal symbol for the separator then."*

    ! `:` is the one character Windows forbids that is NOT shell-special, so an
    address stays safe as a bare command-line argument where `<`, `>`, `|`, `?`
    and `*` would not. Measured over 2,472 source paths in seven corpora: zero
    hold any of the seven.
    """

    def test_a_directory_and_a_dotted_filename_no_longer_collide(self):
        self.assertNotEqual(addresser.flatten("a/b.py"), addresser.flatten("a.b.py"))
        self.assertEqual(addresser.flatten("a/b.py"), "a:b.py")
        self.assertEqual(addresser.flatten("a.b.py"), "a.b.py")

    def test_it_is_invertible_where_the_dotted_form_was_not(self):
        paths = ["a/b.py", "a.b.py"]
        self.assertEqual(addresser.unflatten("a:b.py", paths), "a/b.py")
        self.assertEqual(addresser.unflatten("a.b.py", paths), "a.b.py")

    def test_a_windows_separator_flattens_the_same_way(self):
        self.assertEqual(addresser.flatten(r"pkg\sub\a.py"), "pkg:sub:a.py")

    def test_the_extension_keeps_its_dot(self):
        # ! Dropping it reintroduces the collision `b.py` / `b.rs` in a repo
        # this census supports by design -- eleven languages in one run.
        self.assertTrue(addresser.flatten("pkg/mod.py").endswith(".py"))

    def test_no_separator_is_shell_special(self):
        # ! An address is passed as a bare CLI argument -- `--resolve <ADDRESS>`
        # in `review.md` and `reviewer-brief.md`. Every OTHER character Windows
        # forbids is a redirect, a pipe or a glob.
        self.assertNotIn(addresser.flatten("a/b.py")[1], '<>|?*"')


class TestOneAnchorReachesEveryOneOfItsAddresses(unittest.TestCase):
    """One anchor, three addresses -- and the lookup reaches all of them.

    !! ASKING BY THE LINE FOUND NOTHING. `for_anchor` matched the string and
    then routed `b`/`c` through `declared_at`, which only an `a` carries, so
    every lookup by the code line fell through to the module branch and
    returned []. Measured 2026-08-19: `--anchor 'def f():' --series c` answered
    *"no `c` place"* on a census holding exactly that one.

    ! It could not arise before the same day, because until then a comment
    carried no anchor at all -- see `TestACPlaceCarriesItsAnchor`.
    """

    SRC = '# what f is for\ndef f():\n    """Doc."""\n    return 1  # why\n'

    def setUp(self):
        path = Path("g.py")
        blocks = census.census_for(path, self.SRC, census.language_for(path))
        lines = sorted(census.code_lines(self.SRC, blocks))
        self.blocks = [vars(b) for b in blocks]
        for b in self.blocks:
            b["address"] = addresser.address(b, lines)

    def _folios(self, anchor, series):
        found = addresser.for_anchor(anchor, series, self.blocks)
        return sorted(addresser.folio_of(b["address"])[1] for b in found)

    def test_the_LINE_reaches_all_three_series(self):
        # !! ONE ANCHOR, THREE ADDRESSES -- the declaration's own `a`, the `b`
        # above it and the `c` beside it. This is the one-to-many relationship
        # measured on one line of code.
        self.assertEqual(self._folios("def f():", "a"), ["a1"])
        self.assertEqual(self._folios("def f():", "b"), ["b0"])
        self.assertEqual(self._folios("def f():", "c"), ["c0"])

    def test_the_NAME_no_longer_answers(self):
        # !! Roy ruled it 2026-08-19: *"drop it -- the line is the anchor."*
        # The census stopped carrying declaration names, so `f` names nothing.
        for series in "abc":
            with self.subTest(series=series):
                self.assertEqual(self._folios("f", series), [])


class TestTwoIdenticalStatementsAreTwoAnchorsSpelledAlike(unittest.TestCase):
    """Roy's case, 2026-08-19, verbatim.

    ```python
    X=2   # initial

    # stuff happens

    X=2  # reseting X
    ```

    !! *"For the addresses this is still exact -- for looking up the anchors to
    get the addresses, not so exact."* An address has ONE anchor, so every
    address here is exact. An anchor has MANY addresses, and `X=2` is TWO
    anchors that happen to be spelled the same -- so the reverse lookup answers
    with several places and the caller chooses by address.

    ! Returning the first would silently rule on the wrong statement, which is
    the whole failure the address system replaced line numbers to end.
    """

    SRC = "X=2   # initial\n\n# stuff happens\n\nX=2  # reseting X\n"

    def setUp(self):
        path = Path("x.py")
        blocks = census.census_for(path, self.SRC, census.language_for(path))
        lines = sorted(census.code_lines(self.SRC, blocks))
        self.blocks = [vars(b) for b in blocks]
        for b in self.blocks:
            b["address"] = addresser.address(b, lines)

    def test_every_ADDRESS_is_still_unique(self):
        # !! The direction that stays exact. This is what a record cites.
        named = [b["address"] for b in self.blocks]
        self.assertEqual(len(named), len(set(named)))

    def test_the_anchor_answers_with_BOTH_trailing_comments(self):
        found = addresser.for_anchor("X=2", "c", self.blocks)
        folios = sorted(addresser.folio_of(b["address"])[1] for b in found)
        self.assertEqual(folios, ["c0", "c1"])

    def test_they_are_two_DIFFERENT_statements(self):
        found = addresser.for_anchor("X=2", "c", self.blocks)
        self.assertEqual(sorted(b["start"] for b in found), [1, 5])
        self.assertEqual(sorted(b["text"] for b in found), ["initial", "reseting X"])

    def test_the_anchor_is_the_code_WITHOUT_either_comment(self):
        for b in self.blocks:
            if b["edit_column"]:
                with self.subTest(line=b["start"]):
                    self.assertEqual(b["anchor"], "X=2")

    def test_the_b_series_answers_with_ALL_THREE_gaps(self):
        # !! The `b` half is WORSE, and this file is why: three gaps answer to
        # one spelling. `b0` is the gap above line 1, `b1` holds `# stuff
        # happens`, and `b2` is the gap at the end of the file.
        found = addresser.for_anchor("X=2", "b", self.blocks)
        folios = sorted(addresser.folio_of(b["address"])[1] for b in found)
        self.assertEqual(folios, ["b0", "b1", "b2"])

    def test_the_three_gaps_are_drawn_from_TWO_statements(self):
        """!! And the anchor STRING cannot tell you which.

        `b0` sits above line 1, so its anchor is line 1's code. `b1` holds a
        comment and is anchored to the code BELOW it, which is line 5. `b2` is
        the gap at the end of the file and takes the line ABOVE, which is line 5
        again. Two statements, three gaps, one spelling.
        """
        by_folio = {
            addresser.folio_of(b["address"])[1]: b
            for b in addresser.for_anchor("X=2", "b", self.blocks)
        }
        # ! Read from the EDIT range, which is the gap itself: `b0` is a pure
        # insertion above line 1, `b1` replaces line 3, `b2` appends after 5.
        self.assertEqual(by_folio["b0"]["edit_start"], 1)
        self.assertEqual(by_folio["b1"]["edit_start"], 3)
        self.assertEqual(by_folio["b2"]["edit_start"], 6)
        for folio, block in by_folio.items():
            with self.subTest(folio=folio):
                self.assertEqual(block["anchor"], "X=2")

    def test_the_comment_between_them_is_anchored_to_the_code_BELOW(self):
        # ! `# stuff happens` sits between the two statements and introduces the
        # second, so its anchor is line 5's code -- not line 1's, which it
        # follows. The gap's prose is about what comes next.
        held = next(b for b in self.blocks if b["text"] == "stuff happens")
        self.assertEqual(addresser.folio_of(held["address"])[1], "b1")
        self.assertEqual(held["anchor"], "X=2")

    def test_X_2_is_no_declaration_so_the_a_series_is_EMPTY(self):
        # ! An assignment is not a declaration the census names, so nothing
        # answers in `a`. ! The module's `a0` does not answer either: it keeps
        # `<module>`. Anchoring it to the FIRST LINE OF CODE was tried and made
        # a module's documentation answer to `X=2`.
        self.assertEqual(addresser.for_anchor("X=2", "a", self.blocks), [])

    def test_the_CLI_says_the_answer_is_AMBIGUOUS_in_both_series(self):
        # !! What an agent actually sees. Without it a caller reads the first
        # line of output as "the" answer and rules on the wrong statement.
        for series, count in (("b", 3), ("c", 2)):
            with self.subTest(series=series):
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    rc = addresser._for_anchor("X=2", series, self.blocks)
                self.assertEqual(rc, 0)
                said = out.getvalue()
                self.assertIn(f"{count} places answer", said)
                self.assertIn("Choose by ADDRESS", said)


class TestTheSHIPPEDPROSETeachesTheNumberingTheCodeUSES(unittest.TestCase):
    """The brief and the addresser's own docstrings, against the addresser.

    !! IT COST 5x TO GET WRONG AND WAS WRONG FOR A DAY. `reviewer-brief.md` is
    read by four agents every run, and it taught *"the number means a different
    statement in `b` than in `c`"* -- true while `c` counted from 1, and an
    off-by-one from the moment the 0-indexing ruling aligned them. A reviewer
    following it cited `c(N+1)` for the line it meant: the error the paragraph
    itself warned about, inverted.

    ! **The ambiguity that hid it is the phrase "code line 3"**, which reads as
    the 3rd to one reader and as index 3 to another. One half of the pair stayed
    wrong while the other was right, in one paragraph, for that reason -- so the
    prose now says "the code line at index N" and this holds it there.
    """

    SRC = "".join(f"x{i} = {i}\n" for i in range(6))
    BRIEF = (
        Path(__file__).resolve().parent.parent
        / "plugins/comment-review/skills/comment-review/references/reviewer-brief.md"
    )

    def setUp(self):
        path = Path("m.py")
        blocks = census.census_for(path, self.SRC, census.language_for(path))
        self.code = sorted(census.code_lines(self.SRC, blocks))
        for b in blocks:
            b.address = addresser.address(vars(b), self.code)
        self.at = {
            b.address.split("@")[1]: b for b in blocks if "@" in (b.address or "")
        }

    def test_bN_and_cN_name_THE_SAME_code_line(self):
        # !! The property the shipped prose denied. Measured over every line.
        for n in range(len(self.code)):
            with self.subTest(n=n):
                self.assertEqual(
                    self.at[f"b{n}"].edit_start, self.at[f"c{n}"].start, f"b{n}/c{n}"
                )

    def test_both_series_count_from_ZERO(self):
        # ! `c0` is beside the FIRST code line, not the second.
        self.assertEqual(self.at["c0"].start, self.code[0])
        self.assertEqual(self.at["b0"].edit_start, self.code[0])

    def test_cN_is_beside_the_code_line_at_INDEX_N(self):
        for n in range(len(self.code)):
            with self.subTest(n=n):
                self.assertEqual(self.at[f"c{n}"].start, self.code[n])

    def test_a_file_with_N_code_lines_has_N_plus_1_gaps(self):
        # ! `b0` before the first and `bN` after the last, which is the one `b`
        # with no `c` to pair with.
        gaps = [k for k in self.at if k.startswith("b")]
        self.assertEqual(len(gaps), len(self.code) + 1)
        self.assertNotIn(f"c{len(self.code)}", self.at)

    def test_the_BRIEF_does_not_teach_the_superseded_rule(self):
        # !! The file four agents read every run. A regression here is silent:
        # the prose is not executed, so nothing else would notice.
        said = self.BRIEF.read_text(encoding="utf-8")
        self.assertIn("`bN` AND `cN` NAME THE SAME CODE LINE", said)
        self.assertNotIn("The number means a different statement", said)
        self.assertNotIn("b(N-1)", said)

    def test_the_ADDRESSER_docstrings_agree_with_the_brief(self):
        # ! Two files stating one rule, which is why they drifted apart.
        src = (SCRIPTS / "addresser.py").read_text(encoding="utf-8")
        self.assertIn("THE SAME NUMBER NAMES THE SAME CODE LINE", src)
        self.assertNotIn("NAMES DIFFERENT STATEMENTS", src)
        self.assertNotIn("`b(N-1)` above it", src)
