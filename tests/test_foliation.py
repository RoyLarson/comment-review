"""A place keeps its name when the prose around it changes.

!! THE PROPERTY, in Roy's words 2026-08-18: the census is a HASHED STATIC TABLE
-- exact, constant, fully enumerated -- and without that this scheme falls apart
rather than fails. Every foliator steps past every line of code, so a code line
missed anywhere above a place RENAMES that place, silently and consistently.
These tests hold the naming to the enumeration.
"""

import collections  # noqa: I001  -- path shim below must import before foliation
import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from _paths import SCRIPTS  # noqa: F401
import foliator
from foliator import FRONT
import lexer
import page

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
    {"path": "a.py", "start": 1, "end": 2, "kind": "interval", "original_start": 1},
    {
        "path": "a.py",
        "start": 2,
        "end": 2,
        "kind": "trailing-comment",
        "original_start": 2,
        "original_column": 8,
    },
    {"path": "a.py", "start": 3, "end": 5, "kind": "comment", "original_start": 3},
    {
        "path": "a.py",
        "start": 6,
        "end": 6,
        "kind": "trailing-comment",
        "original_start": 6,
        "original_column": 8,
    },
    {"path": "a.py", "start": 6, "end": 6, "kind": "interval", "original_start": 7},
]
B = [
    {"path": "b.py", "start": 1, "end": 2, "kind": "interval", "original_start": 1},
    {"path": "b.py", "start": 2, "end": 3, "kind": "interval", "original_start": 3},
    {"path": "b.py", "start": 3, "end": 3, "kind": "interval", "original_start": 4},
]


def named(text, paragraphs):
    """The folio each paragraph takes, through the page's own walk.

    ! `attach` returns the folio alone; the path is the page's and is added
    where the address is composed.
    """
    foliation = page.places_on(text, paragraphs)
    return [page.attach(b, foliation) for b in paragraphs]


def addressed(text, paragraphs):
    """`path@folio` for each, composed the way `page_for` composes it."""
    foliation = page.places_on(text, paragraphs)
    return [
        f"{foliator.flatten(b['path'])}@{page.attach(b, foliation)}" for b in paragraphs
    ]


class TestTwoFilesDifferingOnlyInComments(unittest.TestCase):
    def test_the_code_lines_are_the_same_two_in_both(self):
        self.assertEqual(list(page.code_lines(WITH_PROSE, A)), [2, 6])
        self.assertEqual(list(page.code_lines(BARE, B)), [2, 3])

    def test_the_same_gap_gets_the_same_name_prose_or_not(self):
        # !! THE WHOLE POINT. In one file the gap between the two statements
        # holds three comment lines; in the other it is empty. Both are `b2`.
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
        # ! Read from `original_start`, which the census states for the splice --
        # the addressing range cannot say it, because an interval spans the two
        # code lines around the gap rather than the gap itself.
        self.assertEqual(named(BARE, B)[1], "b1")

    def test_a_block_with_no_range_is_reported_not_guessed(self):
        self.assertEqual(
            page.attach({"path": "a.py"}, page.places_on(WITH_PROSE, A)), ""
        )


class TestCodeOnTheFirstLine(unittest.TestCase):
    """The leading gap is `b1` even when it touches the first code line.

    !! FOUND ON REAL RUST, not on a fixture. `StarTraders/src/company.rs` opens
    `use std::fmt;` on line 1, so its leading interval spans `1-1` -- start AND
    end on the first code line -- where an earlier rule counted from the range
    and read that as the gap AFTER code line 1. Every Python file this was first
    written against began with a blank line or a module docstring, so its
    leading gap was `1-2` and the case could not arise.

    ! The range is not what answers it now: `original_start` is 1 for the leading
    gap and 2 for the next, so the two are separated by what the census STATES
    rather than by what a consumer infers from the bounds.
    """

    SRC = "use std::fmt;\n\n#[derive(Debug)]\npub enum X {}\n"
    PARAGRAPHS = [
        {"path": "c.rs", "start": 1, "end": 1, "kind": "interval", "original_start": 1},
        {"path": "c.rs", "start": 1, "end": 3, "kind": "interval", "original_start": 2},
        {"path": "c.rs", "start": 3, "end": 4, "kind": "interval", "original_start": 4},
    ]

    def setUp(self):
        self.code = list(page.code_lines(self.SRC, self.PARAGRAPHS))

    def test_code_starts_on_line_one(self):
        self.assertEqual(self.code[0], 1)

    def test_the_gap_before_it_is_b0_not_b1(self):
        self.assertEqual(addressed(self.SRC, self.PARAGRAPHS)[0], "c.rs@b0")

    def test_the_gap_after_it_is_b1(self):
        self.assertEqual(addressed(self.SRC, self.PARAGRAPHS)[1], "c.rs@b1")

    def test_every_gap_gets_its_own_name(self):
        named = addressed(self.SRC, self.PARAGRAPHS)
        self.assertEqual(len(set(named)), len(named))


class TestTwoFilesOfTheSameName(unittest.TestCase):
    """A path is repo-relative, so same-named files in different packages differ.

    ! Checked because Python lets `pkg/a.py` and `pkg/sub/a.py` coexist and the
    address carries only the path. Verified 2026-08-18 over three such files:
    every address distinct.
    """

    def test_the_package_path_is_part_of_the_address(self):
        one = {
            "path": "pkg/a.py",
            "start": 1,
            "end": 1,
            "kind": "interval",
            "original_start": 1,
        }
        two = {
            "path": "pkg/sub/a.py",
            "start": 1,
            "end": 1,
            "kind": "interval",
            "original_start": 1,
        }
        self.assertNotEqual(
            foliator.flatten(one["path"]), foliator.flatten(two["path"])
        )

    def test_a_windows_separator_is_normalised(self):
        # ! So a census written on Windows and read anywhere names one place.
        paragraph = {
            "path": r"pkg\sub\a.py",
            "start": 1,
            "end": 1,
            "kind": "interval",
            "original_start": 1,
        }
        self.assertEqual(foliator.flatten(paragraph["path"]), "pkg:sub:a.py")

    def test_a_census_without_original_start_is_REFUSED_not_guessed(self):
        # !! The range alone cannot separate the two gaps of a one-line file,
        # which is the whole reason this reads `original_start`. Falling back to it
        # would answer confidently and wrongly.
        old = {"path": "a.py", "start": 1, "end": 1, "kind": "interval"}
        self.assertEqual(page.attach(old, page.places_on("x = 1\n", [old])), "")


class TestAOneLineInitFile(unittest.TestCase):
    """Every package has one, and both its gaps used to be `b1`.

    !! Roy, 2026-08-18: "here it is everywhere -- package/__init__.py,
    package/sub-package/__init__.py". A one-line `__init__.py` emits two
    intervals both spanning `1-1` -- the gap before the import and the gap after
    it -- and `census.address` names them identically. `original_start` is 1 and 2,
    which is what separates them.
    """

    SRC = "from .core import Engine\n"
    PARAGRAPHS = [
        {
            "path": "package/__init__.py",
            "start": 1,
            "end": 1,
            "kind": "interval",
            "original_start": 1,
        },
        {
            "path": "package/__init__.py",
            "start": 1,
            "end": 1,
            "kind": "interval",
            "original_start": 2,
        },
    ]

    def test_the_line_addresses_are_identical(self):
        self.assertEqual({(b["start"], b["end"]) for b in self.PARAGRAPHS}, {(1, 1)})

    def test_the_stable_addresses_are_not(self):
        list(page.code_lines(self.SRC, self.PARAGRAPHS))
        named = addressed(self.SRC, self.PARAGRAPHS)
        self.assertEqual(named, ["package:__init__.py@b0", "package:__init__.py@b1"])

    def test_a_subpackage_of_the_same_name_is_a_different_place(self):
        sub = dict(self.PARAGRAPHS[0], path="package/subpackage/__init__.py")
        self.assertNotEqual(
            foliator.flatten(sub["path"]),
            foliator.flatten(self.PARAGRAPHS[0]["path"]),
        )


class TestTheInverse(unittest.TestCase):
    """An address goes back to the file and the entries that carry it.

    ! The forward direction alone is half a tool: an agent that is handed
    `pkg.mod.py@b4` in a record has to get back to a line to read the code.
    """

    def test_a_flattened_path_resolves_against_the_census(self):
        self.assertEqual(
            foliator.unflatten("pkg:sub:a.py", ["pkg/sub/a.py", "other/a.py"]),
            "pkg/sub/a.py",
        )

    def test_two_paths_that_FLATTEN_alike_are_REFUSED(self):
        # !! THE DOTTED FORM IS NOT SELF-INVERTIBLE. `a/b.py` and `a.b.py` both
        # read `a.b.py`, and a dot in a FILE name is ordinary in most of the
        # eleven languages this census reads -- `app.test.js`, `types.d.ts`.
        # Picking one would answer a question nobody asked.
        self.assertEqual(foliator.unflatten("a:b.py", ["a/b.py", "a:b.py"]), "")

    def test_a_path_the_census_never_carried_resolves_to_nothing(self):
        self.assertEqual(foliator.unflatten("nope.py", ["a/b.py"]), "")

    def test_an_address_splits_into_path_and_folio(self):
        self.assertEqual(foliator.folio_of("pkg:mod.py@b4"), ("pkg:mod.py", "b4"))

    def test_a_string_with_no_folio_is_not_an_address(self):
        self.assertEqual(foliator.folio_of("pkg:mod.py"), ("", ""))

    def test_every_address_finds_its_own_entry_again(self):
        # ! STAMPED FIRST, because `resolve` READS the census's `place` rather
        # than recomputing one -- which is the whole point of the producer
        # stating it. A fixture built without the stamp resolves to nothing.
        stamped = [
            {**b, "address": a}
            for b, a in zip(A, addressed(WITH_PROSE, A), strict=True)
        ]
        for i, paragraph in enumerate(stamped, 1):
            with self.subTest(entry=i):
                self.assertEqual(foliator.resolve(paragraph["address"], stamped), [i])

    def test_an_address_nothing_carries_comes_back_empty(self):

        self.assertEqual(foliator.resolve("b.py@b100", B), [])


class TestAStaleCensusIsRefused(unittest.TestCase):
    """A census older than the file names places the code has left.

    !! THIS IS A MECHANISM, NOT A REMINDER. In one session the same mistake was
    made four times -- an oracle diff, a git reachability call, a coverage
    figure of 51%, and a `SHARED` row that listed one paragraph -- each time by
    reading an artifact built three edits earlier and treating the result as a
    defect in the code. Naming the habit did not stop the fourth. `--check`
    exits 2 instead.
    """

    SRC = "X = 1\n# a note\nY = 2\n"
    PARAGRAPHS = [
        {
            "path": "m.py",
            "start": 2,
            "end": 2,
            "kind": "comment",
            "original_start": 2,
            "original_end": 2,
            "raw_lines": ["# a note"],
            "original_column": 0,
        }
    ]

    def test_the_census_matches_the_file_it_came_from(self):
        from _transcription import transcribes

        self.assertTrue(transcribes(self.PARAGRAPHS[0], self.SRC.splitlines()))

    def test_it_does_not_match_a_file_that_has_moved(self):
        # ! One line added ABOVE the paragraph, which is what a prose edit does.
        moved = "import os\n" + self.SRC
        from _transcription import transcribes

        self.assertFalse(transcribes(self.PARAGRAPHS[0], moved.splitlines()))

    def test_the_addresses_differ_silently_and_neither_errors(self):
        # !! THE POINT. Both answer, both look right, and they disagree. A blank
        # line prepended -- which is what a prose edit does -- moves the code
        # down, so the paragraph's stated `original_start` now has NO code line before
        # it: `b2` becomes `b1`, naming a different place with no complaint.
        list(page.code_lines(self.SRC, self.PARAGRAPHS))
        list(page.code_lines("\n" + self.SRC, self.PARAGRAPHS))
        self.assertEqual(addressed(self.SRC, self.PARAGRAPHS)[0], "m.py@b1")
        self.assertEqual(addressed("\n" + self.SRC, self.PARAGRAPHS)[0], "m.py@b0")


class TestTheDeclarationSeries(unittest.TestCase):
    """`a0..aN` names a DECLARATION, so a docstring leaves the gap series.

    !! IT IS WHAT MAKES AN ADDRESS A SINGLE FACT. Measured 2026-08-18 over
    9,975 paragraphs in this repo, 28 places were answered by two paragraphs and 28 of
    28 were a docstring sharing a gap with the comment run beneath it. Naming a
    docstring for the gap it sits in put two different subjects at one address.
    """

    def _census(self, text):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "m.py"
            path.write_text(text, encoding="utf-8")
            got = page.page_for(path, text, lexer.language_for(path))
            list(page.code_lines(text, [vars(b) for b in got]))
            for b in got:
                # ! The SUFFIX only. `page_for` names a paragraph by the path it
                # was handed, and these are absolute temp paths -- the dotted
                # prefix is `main`'s to make repo-relative.
                b.address = b.address.split("@")[-1]
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

    def test_an_empty_declaration_HOLDS_NO_LINE(self):
        # !! None on both ends. The docstring is not written yet, so no line
        # of the file carries this foliation -- which is different from a
        # range that happens to be empty. `(2, 1)` said it as arithmetic.
        got = self._census("def bare():\n    return 1\n")
        bare = next(b for b in got if b.anchor == "def bare():")
        self.assertIsNone(bare.original_start)
        self.assertIsNone(bare.original_end)

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
        self.assertEqual(list(page.code_lines(text, [vars(b) for b in got])), [1, 2])

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
        # ! LEADING holds no prose either -- it is the space between two
        # paragraphs and answers to nothing.
        prose = [
            b
            for b in got
            if b.kind not in page.HOLDS_NO_PROSE and b.kind != lexer.LEADING
        ]
        self.assertEqual(
            [b.anchor for b in prose],
            [
                "<module>",
                "def widen(width: Annotated[int, Doc('How wide.')]) -> str:",
            ],
        )
        self.assertNotIn("How wide.", " ".join(b.text for b in prose))


class TestAnAnchorsPlacesAreASKED_FOR(unittest.TestCase):
    """`for_anchor` -- which address is this anchor's `a`, `b` or `c`.

    !! ASKING BY POSITION BREAKS ON THE NEXT LANGUAGE. Python's docstring sits
    AFTER its `def` and Rust's `///` BEFORE its `fn`, so "the paragraph above the
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
            got = page.page_for(path, self.SRC, lexer.language_for(path))
            list(page.code_lines(self.SRC, [vars(b) for b in got]))
            self.paragraphs = [vars(b) for b in got]

    def _at(self, anchor, series):
        # ! The FOLIO only -- the temp path is noise here.
        return [
            b["address"].split("@")[-1]
            for b in foliator.for_anchor(anchor, series, self.paragraphs)
        ]

    def test_a_declaration_has_a_place_in_every_series(self):
        # !! ONE ANCHOR, THREE ADDRESSES. The declaration's line is the anchor
        # of its own `a`, of the `b` above it and of the `c` beside it.
        self.assertEqual(self._at("def go(n):", "a"), ["a1"])
        self.assertEqual(self._at("def go(n):", "c"), ["c1"])
        self.assertEqual(self._at("def go(n):", "b"), ["b1"])

    def test_the_MODULE_has_an_a_and_NEVER_a_c(self):
        # !! It has no line to open on, so nothing can sit beside it. That is
        # the one trigger the `c` foliator steps past without emitting.
        self.assertEqual(self._at("<module>", "a"), ["a0"])
        self.assertEqual(self._at("<module>", "c"), [])

    def test_the_MODULE_ALWAYS_HAS_ITS_OWN_PLACE(self):
        """!! `b0` IS THE FILE'S OWN PROSE, not the gap above the first line of
        code -- those were one address until 2026-08-19, so a licence header and
        the comment introducing the first declaration answered to the same name.

        !! AND IT EXISTS WHETHER OR NOT ANYTHING SITS IN IT. This test asserted
        the opposite until 2026-08-20 -- that the module had a `b` ONLY where the
        file had front matter -- which was the defect stated as a rule: `b0` was
        emitted by a branch that fired when `mark_matter` had already
        stamped prose, so `b0` and `b1` were mutually exclusive and Roy's `b1`
        mark was unresolvable on a file that gained a licence.

        ! A place exists because the walk reached its trigger. Roy, 2026-08-19:
        *"all of the addresses exist by definition"*, and *"b1 isn't able to be
        swallowed by b0."*

        ! An edit proposed at `b0` is still promoted to a `query` -- Roy: *"it is
        supposed to promote any verdict that modifies that section to a query
        with an ask-the-human. Never resolved by the agents."* That is what the
        place is FOR; it is not a reason for it to be absent.
        """
        # This fixture opens with a docstring and has no front matter at all --
        # and BOTH of the file's own places answer to the module, since 2026-08-21:
        # `f0` at the head and `f1` at the foot. Neither depends on prose being
        # there, which is the whole assertion.
        self.assertEqual(self._at("<module>", FRONT), ["f0", "f1"])

        with_header = '# Copyright 2026 Roy.\n"""Module."""\n\nBUDGET = 3\n'
        path = Path("m.py")
        got = page.page_for(path, with_header, lexer.language_for(path))
        list(page.code_lines(with_header, [vars(b) for b in got]))
        found = foliator.for_anchor("<module>", FRONT, [vars(b) for b in got])
        self.assertEqual(
            sorted(foliator.folio_of(b["address"])[1] for b in found), ["f0", "f1"]
        )

    def test_the_FILE_HAS_A_PLACE_AT_ITS_FOOT_TOO(self):
        # !! `f1`, RULED 2026-08-21. Roy, asked whether the foot of a file needed
        # a rule of its own: *"same answer for the back matter because of the
        # same reason."* Before it, `f` emitted once at the MODULE trigger and a
        # licence at the bottom of a file landed in the CLOSING GAP -- measured
        # the same day as `b2` on a five-line file.
        path = Path("m.py")
        got = page.page_for(path, "import os\n\nx = 1\n", lexer.language_for(path))
        self.assertEqual(got.foliation.matter(), "f0")
        self.assertEqual(got.foliation.back_matter(), "f1")

    def test_the_foot_place_is_bounded_by_NOTHING_as_the_head_one_is(self):
        # ! It is the FILE's, not the last gap's. A `b` is bounded by the code
        # around it; an `f` is bounded by the edge of the file on both sides, so
        # a sweep that shares a gap out never reaches it.
        path = Path("m.py")
        got = page.page_for(path, "import os\n\nx = 1\n", lexer.language_for(path))
        self.assertEqual(got.foliation.bounds["f1"], (0, 0))
        self.assertEqual(got.foliation.bounds["f0"], (0, 0))

    def test_the_foot_place_exists_on_a_file_with_NO_CODE_AT_ALL(self):
        # ! The EOF trigger fires whether or not the walk stepped a line, so a
        # file that is one comment still has both of its own places.
        path = Path("m.py")
        got = page.page_for(path, "# just a note\n", lexer.language_for(path))
        self.assertEqual(
            sorted(f for f in got.foliation.places if f.startswith(FRONT)),
            ["f0", "f1"],
        )

    def test_an_anchor_the_census_never_stamped_answers_nothing(self):
        # ! Empty, not a guess. A lexical-tier language resolves no anchors at
        # all, and the caller reports that rather than being handed a neighbour.
        self.assertEqual(self._at("nosuchname", "a"), [])
        self.assertEqual(self._at("nosuchname", "b"), [])

    def test_the_c_it_names_is_the_DECLARATIONS_own_line(self):
        found = foliator.for_anchor("def go(n):", "c", self.paragraphs)
        self.assertEqual([b["start"] for b in found], [6])
        # ! The one fact that decides it -- not a list of kinds. `SHARES_ITS_LINE`
        # was a second way to ask, and it disagreed with this one.
        self.assertTrue(found[0]["original_column"])


class TestTheAddresserReadsTheCensusNeverTheTree(unittest.TestCase):
    """It takes no `--repo`, and every question it answers is census-internal.

    !! CHECKING THE FILE WOULD ASSERT THAT LINE NUMBERS STILL MATTER, which is
    what an address exists to stop. Roy, 2026-08-19: *"not necessary for
    foliation to do the staleness sweep as long as the original census is still
    an available document ... In a small way it is the foliation stating the
    line numbers matter still."*

    ! A sweep was here and it refused a census built SECONDS earlier on every
    non-Python file carrying a trailing comment -- and masked a real collision
    `--check` exists to report. Staleness belongs where a file is WRITTEN;
    `_transcription.transcribes` refuses a census the file no longer reads as.
    """

    def _run(self, *args):
        import subprocess
        import sys as _sys

        return subprocess.run(
            [_sys.executable, str(SCRIPTS / "foliator.py"), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

    def test_it_reads_no_file_but_the_census(self):
        text = (SCRIPTS / "foliator.py").read_text(encoding="utf-8")
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
            got = page.page_for(
                src, src.read_text(encoding="utf-8"), lexer.language_for(src)
            )
            list(
                page.code_lines(src.read_text(encoding="utf-8"), [vars(b) for b in got])
            )
            census_json = Path(tmp) / "c.json"
            census_json.write_text(
                __import__("json").dumps([vars(b) for b in got], default=str),
                encoding="utf-8",
            )
            src.write_text("import os\n\n\n# a note\nx = 1\n", encoding="utf-8")
            out = self._run("--census", str(census_json), "--check")
            self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
            self.assertIn("paragraphs addressed", out.stdout)


class TestAMidLineCommentTakesTheLineItSitsOn(unittest.TestCase):
    """One fact decides "shares its line", and the producer states it.

    !! IT WAS DECIDED TWICE AND THE TWO DISAGREED. `address()` read a list of
    KINDS; `code_lines_of` read the paragraph. A `comment` opened after a
    statement is in neither list and has a non-zero `original_column`, so it took a `b`
    folio for a line it sits ON -- and that folio then named the comment AND the
    gap. Measured 2026-08-19 on `let b = 2; /* opens` / `and closes */`: `@b2`
    resolved to an empty interval, so every text check on the comment read "".

    !! AND THE KIND WAS THE HALF STILL WRONG until 2026-08-20. Roy: *"`c`s are
    trailing comments by definition of how they are placed."* This paragraph
    took its `c` correctly and was still reported as a plain `comment`, because
    the lexical tier asks `trailing`, which is false by the time a run spans
    more than one line. Kind and series disagreed on the one paragraph this
    class exists to pin.
    """

    SRC = "let a = 1;\nlet b = 2; /* opens\nand closes */\nlet c = 3;\n"

    def _census(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "s.js"
            path.write_text(self.SRC, encoding="utf-8")
            return page.page_for(path, self.SRC, lexer.language_for(path))

    def test_the_comment_takes_a_c_because_code_precedes_it(self):
        got = self._census()
        # ! Selected by its PROSE, so the assertion below is about neither the
        # kind nor the series the paragraph was picked by.
        mid = next(b for b in got if "opens" in b.text)
        # ! A `c` IS a trailing comment. The kind says so now; it said `comment`
        # until 2026-08-20 while sitting at a `c` place.
        self.assertEqual(mid.kind, "trailing-comment")
        self.assertTrue(mid.original_column)
        # ! The FOLIO, not the address -- the census composes `path@folio` now,
        # and the path is a temp directory here.
        self.assertTrue(mid.address.split("@")[-1].startswith("c"), mid.address)

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
        # ! `paragraphs_in` asks whether a paragraph OVERLAPS the gap, not whether it
        # STARTS in one. The comment begins on the bounding code line and runs
        # into the gap below, so a start test read the gap as empty and emitted
        # an interval over the comment's own second line.
        got = self._census()
        self.assertEqual([b for b in got if b.kind == "interval" and b.start == 3], [])


class TestTheSeparatorIsAPathCannotHoldIt(unittest.TestCase):
    """`:` separates path segments, so a flattened path is INVERTIBLE.

    !! IT WAS `.` UNTIL 2026-08-19, AND A DOT IS ORDINARY IN A FILENAME.
    `a/b.py` and `a.b.py` both flattened to `a.b.py`, so every one of their
    addresses collided -- `@a0`, `@b1`, `@b2`, `@c1`, all of them -- and
    `--check` reported "8 of 8 paragraphs addressed" because it compares only within
    one path. Roy: *"lets use an illegal symbol for the separator then."*

    ! `:` is the one character Windows forbids that is NOT shell-special, so an
    address stays safe as a bare command-line argument where `<`, `>`, `|`, `?`
    and `*` would not. Measured over 2,472 source paths in seven corpora: zero
    hold any of the seven.
    """

    def test_a_directory_and_a_dotted_filename_no_longer_collide(self):
        self.assertNotEqual(foliator.flatten("a/b.py"), foliator.flatten("a.b.py"))
        self.assertEqual(foliator.flatten("a/b.py"), "a:b.py")
        self.assertEqual(foliator.flatten("a.b.py"), "a.b.py")

    def test_it_is_invertible_where_the_dotted_form_was_not(self):
        paths = ["a/b.py", "a.b.py"]
        self.assertEqual(foliator.unflatten("a:b.py", paths), "a/b.py")
        self.assertEqual(foliator.unflatten("a.b.py", paths), "a.b.py")

    def test_a_windows_separator_flattens_the_same_way(self):
        self.assertEqual(foliator.flatten(r"pkg\sub\a.py"), "pkg:sub:a.py")

    def test_the_extension_keeps_its_dot(self):
        # ! Dropping it reintroduces the collision `b.py` / `b.rs` in a repo
        # this census supports by design -- eleven languages in one run.
        self.assertTrue(foliator.flatten("pkg/mod.py").endswith(".py"))

    def test_no_separator_is_shell_special(self):
        # ! An address is passed as a bare CLI argument -- `--resolve <ADDRESS>`
        # in `review.md` and `reviewer-brief.md`. Every OTHER character Windows
        # forbids is a redirect, a pipe or a glob.
        self.assertNotIn(foliator.flatten("a/b.py")[1], '<>|?*"')


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
        paragraphs = page.page_for(path, self.SRC, lexer.language_for(path))
        list(page.code_lines(self.SRC, [vars(b) for b in paragraphs]))
        self.paragraphs = [vars(b) for b in paragraphs]

    def _folios(self, anchor, series):
        found = foliator.for_anchor(anchor, series, self.paragraphs)
        return sorted(foliator.folio_of(b["address"])[1] for b in found)

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
        paragraphs = page.page_for(path, self.SRC, lexer.language_for(path))
        list(page.code_lines(self.SRC, [vars(b) for b in paragraphs]))
        self.paragraphs = [vars(b) for b in paragraphs]

    def test_every_ADDRESS_is_still_unique(self):
        # !! The direction that stays exact. This is what a record cites.
        named = [b["address"] for b in self.paragraphs]
        self.assertEqual(len(named), len(set(named)))

    def test_the_anchor_answers_with_BOTH_trailing_comments(self):
        found = foliator.for_anchor("X=2", "c", self.paragraphs)
        folios = sorted(foliator.folio_of(b["address"])[1] for b in found)
        self.assertEqual(folios, ["c0", "c1"])

    def test_they_are_two_DIFFERENT_statements(self):
        found = foliator.for_anchor("X=2", "c", self.paragraphs)
        self.assertEqual(sorted(b["start"] for b in found), [1, 5])
        self.assertEqual(sorted(b["text"] for b in found), ["initial", "reseting X"])

    def test_the_anchor_is_the_code_WITHOUT_either_comment(self):
        for b in self.paragraphs:
            if b["original_column"]:
                with self.subTest(line=b["start"]):
                    self.assertEqual(b["anchor"], "X=2")

    def test_the_b_series_answers_with_ALL_THREE_gaps(self):
        # !! The `b` half is WORSE, and this file is why: three gaps answer to
        # one spelling -- the gap above the opening statement, the gap holding
        # `# stuff happens`, and the gap at the end of the file. ! The folios
        # below are what THIS walk emits, not a rule anything may count out.
        found = foliator.for_anchor("X=2", "b", self.paragraphs)
        folios = sorted(foliator.folio_of(b["address"])[1] for b in found)
        self.assertEqual(folios, ["b0", "b1", "b2"])

    def test_the_three_gaps_are_drawn_from_TWO_statements(self):
        """!! And the anchor STRING cannot tell you which.

        The first gap sits above the opening statement, so its anchor is that
        line's code. The second holds a comment and is anchored to the code
        BELOW it, which is line 5. The third is the gap at the end of the file
        and takes the line ABOVE, which is line 5 again. Two statements, three
        gaps, one spelling.
        """
        by_folio = {
            foliator.folio_of(b["address"])[1]: b
            for b in foliator.for_anchor("X=2", "b", self.paragraphs)
        }
        # ! Read from the ORIGINAL range, which is the gap's OWN LINES: the
        # first covers nothing above line 1, the second covers line 3 alone, and
        # the third covers nothing after 5.
        #
        # !! IT WAS 2-4 BETWEEN 2026-08-20 AND 2026-08-21, and the reason it was
        # is SUPERSEDED rather than wrong. Roy then: *"`b` owns it, else a
        # literal two paragraph comment is held by nothing and cannot have its
        # internal paragraphs merged or dropped appropriately in the edit
        # process."* The blanks had to belong to SOMETHING, and `b` was the only
        # candidate.
        #
        # !! THE `d` SERIES IS THE BETTER CANDIDATE, and it is what a `b` owning
        # both sides of an `a` could not do: a folio is ONE entry in the reading
        # order, so a `b` holding lines 2 and 4 around prose at 3 emitted both
        # blanks together and the file came back blank-blank-comment. Every
        # paragraph is CONTIGUOUS now, and `# stuff happens` is line 3 alone.
        #
        # ! The blanks are still held -- by `d`, and still merged or dropped in
        # the edit process. What changed is which series holds them.
        # ! `b0` is the gap ABOVE line 1 on a file whose line 1 is code, so it
        # holds no line and says None.
        self.assertIsNone(by_folio["b0"]["original_start"])
        self.assertEqual(
            (by_folio["b1"]["original_start"], by_folio["b1"]["original_end"]), (3, 3)
        )
        self.assertIsNone(by_folio["b2"]["original_start"])
        for folio, paragraph in by_folio.items():
            with self.subTest(folio=folio):
                self.assertEqual(paragraph["anchor"], "X=2")

    def test_the_comment_between_them_is_anchored_to_the_code_BELOW(self):
        # ! `# stuff happens` sits between the two statements and introduces the
        # second, so its anchor is line 5's code -- not line 1's, which it
        # follows. The gap's prose is about what comes next.
        held = next(b for b in self.paragraphs if b["text"] == "stuff happens")
        self.assertEqual(foliator.folio_of(held["address"])[1], "b1")
        self.assertEqual(held["anchor"], "X=2")

    def test_X_2_is_no_declaration_so_the_a_series_is_EMPTY(self):
        # ! An assignment is not a declaration the census names, so nothing
        # answers in `a`. ! The module's `a0` does not answer either: it keeps
        # `<module>`. Anchoring it to the FIRST LINE OF CODE was tried and made
        # a module's documentation answer to `X=2`.
        self.assertEqual(foliator.for_anchor("X=2", "a", self.paragraphs), [])

    def test_the_CLI_says_the_answer_is_AMBIGUOUS_in_both_series(self):
        # !! What an agent actually sees. Without it a caller reads the first
        # line of output as "the" answer and rules on the wrong statement.
        for series, count in (("b", 3), ("c", 2)):
            with self.subTest(series=series):
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    rc = foliator._for_anchor("X=2", series, self.paragraphs)
                self.assertEqual(rc, 0)
                said = out.getvalue()
                self.assertIn(f"{count} places answer", said)
                self.assertIn("Choose by ADDRESS", said)


class TestEachFoliatorCountsItsOwnSteps(unittest.TestCase):
    """Three foliators, three counters, and NO arithmetic between them.

    !! NOTHING MAY COMPUTE ONE FOLIO FROM ANOTHER, OR FROM A LINE ORDINAL.
    Roy, 2026-08-19: *"remove any references that indicate anyone can expect
    that the next line of code is guaranteed to have the next foliation index --
    not in the examples, not in `CLAUDE.md`, not in the docs. It is a
    happenstance and may change at any point if it is determined that another
    system will work better."*

    ! **THIS CLASS REPLACES TWO THAT PROMISED THE OPPOSITE.**
    `TestTheTwoSeriesNameTheSameCodeLine` asserted `bN` and `cN` name one line,
    and `TestTheSHIPPEDPROSETeachesTheNumberingTheCodeUSES` held the shipped
    prose to that claim. Both were written 2026-08-19, both were true of that
    day's trigger list, and both would have FROZEN it: a test that asserts a
    coincidence turns it into a contract.

    !! WHAT IS ACTUALLY GUARANTEED is that each foliator walks the triggers and
    takes a number at every one, emitting or not. Roy: *"each gets its own
    counter and each gets passed the lines of code and the module, and the `c`
    knows it is supposed to skip it."*
    """

    SRC = "".join(f"x{i} = {i}\n" for i in range(4))

    def setUp(self):
        path = Path("m.py")
        paragraphs = page.page_for(path, self.SRC, lexer.language_for(path))
        self.code = list(page.code_lines(self.SRC, [vars(b) for b in paragraphs]))
        self.at = {
            b.address.split("@")[1]: b for b in paragraphs if "@" in (b.address or "")
        }

    def test_the_MODULE_is_a_trigger_that_c_does_not_emit_for(self):
        # !! ASKED OF THE ANCHOR, NOT OF THE NUMBER. `a` and `f` emit at the
        # module; `b` and `c` skip it, because a module has no gap above it and
        # no line to sit beside. ! Skipping takes NO number since 2026-08-20, so
        # `c0` exists and is the first line of code -- what this holds is that
        # no `c` is anchored to the module, which is what it always meant.
        self.assertNotIn(
            foliator.MODULE,
            [b.anchor for f, b in self.at.items() if f.startswith("c")],
        )
        folios = sorted(self.at)
        self.assertTrue(any(f.startswith("a") for f in folios), folios)

    def test_every_place_still_gets_exactly_one_folio(self):
        # ! What the foliators are FOR. The numbering may change; that each
        # place has exactly one name may not.
        named = [b.address for b in self.at.values()]
        self.assertEqual(len(named), len(set(named)))

    def test_a_folio_is_never_DERIVED_from_another(self):
        """!! The property the arithmetic destroyed and the walk restores.

        `b` used to be `sum(1 for n in code if n < at)`, `c` was
        `code.index(start)` and `a` was the AST's ordinal -- three mechanisms
        for one question, so aligning two of them took edits in both plus prose
        in four places, and `b0` still ended up naming the module's front matter
        AND the gap above the first line of code.
        """
        # ! The CODE, not the prose: the docstrings quote the three retired
        # expressions on purpose, to keep the error legible.
        text = Path(foliator.__file__).read_text(encoding="utf-8")
        code = [
            ln
            for ln in text.splitlines()
            if ln.strip() and not ln.lstrip().startswith(("#", '"', "'"))
        ]
        body = "\n".join(code)
        self.assertNotIn('f"{path}@c{code.index(start)}"', body)
        self.assertNotIn('sum(1 for n in code if n < at)}"', body)
        self.assertIn("def folio(", body)

    def test_the_walk_is_one_list_and_foliate_READS_it(self):
        """!! IT DID NOT, AND THIS TEST SAID IT DID. Measured 2026-08-21.

        `triggers` claimed *"ONE LIST, SO THE THREE SERIES CANNOT DRIFT APART"*
        and this test said *"both read it, so neither can drift from the other
        by being edited alone"* -- while `foliate` wrote the walk out by hand and
        `triggers` had exactly ONE caller: this test. The guarantee was
        documented, asserted for SHAPE, and not implemented. Roy: *"WHAT!!!"*

        ! So the shape assertion is not enough and never was. This reads the
        SOURCE for the call, which is the only thing that makes the claim true.
        """
        walk = foliator.triggers(self.code)
        self.assertEqual(walk[0], foliator.MODULE)
        self.assertEqual(walk[-1], foliator.EOF)
        self.assertEqual(walk[1:-1], self.code)
        source = (SCRIPTS / "foliator.py").read_text(encoding="utf-8")
        body = source[source.index("def foliate(") :]
        self.assertIn("triggers(", body[: body.index("\ndef ")])

    def test_EOF_is_a_trigger_and_not_an_arithmetic(self):
        """!! RULED 2026-08-21, against the cheaper N+1 rule.

        Roy: *"I know the N+1 is easiest but I am hesitant because `f` will
        almost certainly get it, and so we might as well pick up both now -- that
        makes two conditions where you would have to understand to keep the code
        consistent, and why 1 gets a +1 and the other gets some other treatment,
        which is the reason each foliator owns its own rules."*

        ! So the closing gap comes from a trigger every series meets, exactly as
        the MODULE does. `b` emits for it and the others skip; `f` taking a tail
        place later is a row at this step, not a second arithmetic.
        """
        self.assertIn(foliator.EOF, foliator.triggers(self.code))
        # ! N lines of code, N+1 gaps -- the last of them from EOF.
        gaps = [f for f in self.at if f.startswith("b")]
        self.assertEqual(len(gaps), len(self.code) + 1)
