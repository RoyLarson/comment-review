"""A place keeps its name when the prose around it changes.

!! THE PROPERTY, in Roy's words 2026-08-18: the census is a HASHED STATIC TABLE
-- exact, constant, fully enumerated -- and without that this scheme falls apart
rather than fails. Every foliator steps past every line of code, so a code line
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


def named(text, paragraphs):
    """The folio each paragraph takes, through the page's own walk.

    ! `attach` returns the folio alone; the path is the page's and is added
    where the address is composed.
    """
    foliation = page.places_on(text, paragraphs)
    return [page.attach(b, foliation) for b in paragraphs]


def addressed(text, paragraphs):
    """`path@folio` for each, composed the way `census_for` composes it."""
    foliation = page.places_on(text, paragraphs)
    return [
        f"{addresser.flatten(b['path'])}@{page.attach(b, foliation)}"
        for b in paragraphs
    ]


class TestTwoFilesDifferingOnlyInComments(unittest.TestCase):
    def test_the_code_lines_are_the_same_two_in_both(self):
        self.assertEqual(page.code_lines_of(WITH_PROSE, A), [2, 6])
        self.assertEqual(page.code_lines_of(BARE, B), [2, 3])

    def test_the_same_gap_gets_the_same_name_prose_or_not(self):
        # !! THE WHOLE POINT. In one file the gap between the two statements
        # holds three comment lines; in the other it is empty. Both are `b2`.
        self.assertEqual(named(WITH_PROSE, A)[2], "b2")
        self.assertEqual(named(BARE, B)[1], "b2")

    def test_the_gap_after_the_last_statement_agrees(self):
        self.assertEqual(named(WITH_PROSE, A)[4], "b3")
        self.assertEqual(named(BARE, B)[2], "b3")

    def test_the_gap_before_the_first_statement_agrees(self):
        self.assertEqual(named(WITH_PROSE, A)[0], "b1")
        self.assertEqual(named(BARE, B)[0], "b1")

    def test_line_addresses_do_NOT_agree_which_is_why_this_exists(self):
        self.assertNotEqual(
            [(b["start"], b["end"]) for b in A],
            [(b["start"], b["end"]) for b in B],
        )


class TestOnAndBetween(unittest.TestCase):
    def test_a_trailing_comment_sits_ON_its_code_line(self):
        self.assertEqual(named(WITH_PROSE, A)[1], "c1")
        self.assertEqual(named(WITH_PROSE, A)[3], "c2")

    def test_an_interval_names_the_gap_AFTER_its_bounding_line(self):
        # ! Read from `edit_start`, which the census states for the splice --
        # the addressing range cannot say it, because an interval spans the two
        # code lines around the gap rather than the gap itself.
        self.assertEqual(named(BARE, B)[1], "b2")

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

    ! The range is not what answers it now: `edit_start` is 1 for the leading
    gap and 2 for the next, so the two are separated by what the census STATES
    rather than by what a consumer infers from the bounds.
    """

    SRC = "use std::fmt;\n\n#[derive(Debug)]\npub enum X {}\n"
    PARAGRAPHS = [
        {"path": "c.rs", "start": 1, "end": 1, "kind": "interval", "edit_start": 1},
        {"path": "c.rs", "start": 1, "end": 3, "kind": "interval", "edit_start": 2},
        {"path": "c.rs", "start": 3, "end": 4, "kind": "interval", "edit_start": 4},
    ]

    def setUp(self):
        self.code = page.code_lines_of(self.SRC, self.PARAGRAPHS)

    def test_code_starts_on_line_one(self):
        self.assertEqual(self.code[0], 1)

    def test_the_gap_before_it_is_b0_not_b1(self):
        self.assertEqual(addressed(self.SRC, self.PARAGRAPHS)[0], "c.rs@b1")

    def test_the_gap_after_it_is_b1(self):
        self.assertEqual(addressed(self.SRC, self.PARAGRAPHS)[1], "c.rs@b2")

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
            "edit_start": 1,
        }
        two = {
            "path": "pkg/sub/a.py",
            "start": 1,
            "end": 1,
            "kind": "interval",
            "edit_start": 1,
        }
        self.assertNotEqual(
            addresser.flatten(one["path"]), addresser.flatten(two["path"])
        )

    def test_a_windows_separator_is_normalised(self):
        # ! So a census written on Windows and read anywhere names one place.
        paragraph = {
            "path": r"pkg\sub\a.py",
            "start": 1,
            "end": 1,
            "kind": "interval",
            "edit_start": 1,
        }
        self.assertEqual(addresser.flatten(paragraph["path"]), "pkg:sub:a.py")

    def test_a_census_without_edit_start_is_REFUSED_not_guessed(self):
        # !! The range alone cannot separate the two gaps of a one-line file,
        # which is the whole reason this reads `edit_start`. Falling back to it
        # would answer confidently and wrongly.
        old = {"path": "a.py", "start": 1, "end": 1, "kind": "interval"}
        self.assertEqual(page.attach(old, page.places_on("x = 1\n", [old])), "")


class TestAOneLineInitFile(unittest.TestCase):
    """Every package has one, and both its gaps used to be `b1`.

    !! Roy, 2026-08-18: "here it is everywhere -- package/__init__.py,
    package/sub-package/__init__.py". A one-line `__init__.py` emits two
    intervals both spanning `1-1` -- the gap before the import and the gap after
    it -- and `census.address` names them identically. `edit_start` is 1 and 2,
    which is what separates them.
    """

    SRC = "from .core import Engine\n"
    PARAGRAPHS = [
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
        self.assertEqual({(b["start"], b["end"]) for b in self.PARAGRAPHS}, {(1, 1)})

    def test_the_stable_addresses_are_not(self):
        page.code_lines_of(self.SRC, self.PARAGRAPHS)
        named = addressed(self.SRC, self.PARAGRAPHS)
        self.assertEqual(named, ["package:__init__.py@b1", "package:__init__.py@b2"])

    def test_a_subpackage_of_the_same_name_is_a_different_place(self):
        sub = dict(self.PARAGRAPHS[0], path="package/subpackage/__init__.py")
        self.assertNotEqual(
            addresser.flatten(sub["path"]),
            addresser.flatten(self.PARAGRAPHS[0]["path"]),
        )


class TestTheInverse(unittest.TestCase):
    """An address goes back to the file and the entries that carry it.

    ! The forward direction alone is half a tool: an agent that is handed
    `pkg.mod.py@b4` in a record has to get back to a line to read the code.
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
        self.assertEqual(addresser.folio_of("pkg:mod.py@b4"), ("pkg:mod.py", "b4"))

    def test_a_string_with_no_folio_is_not_an_address(self):
        self.assertEqual(addresser.folio_of("pkg:mod.py"), ("", ""))

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
                self.assertEqual(addresser.resolve(paragraph["address"], stamped), [i])

    def test_an_address_nothing_carries_comes_back_empty(self):

        self.assertEqual(addresser.resolve("b.py@b100", B), [])


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
            "edit_start": 2,
            "edit_end": 2,
            "raw_lines": ["# a note"],
            "edit_column": 0,
        }
    ]

    def test_the_census_matches_the_file_it_came_from(self):
        from galley import paragraph_matches

        self.assertTrue(paragraph_matches(self.SRC.splitlines(), self.PARAGRAPHS[0]))

    def test_it_does_not_match_a_file_that_has_moved(self):
        # ! One line added ABOVE the paragraph, which is what a prose edit does.
        moved = "import os\n" + self.SRC
        from galley import paragraph_matches

        self.assertFalse(paragraph_matches(moved.splitlines(), self.PARAGRAPHS[0]))

    def test_the_addresses_differ_silently_and_neither_errors(self):
        # !! THE POINT. Both answer, both look right, and they disagree. A blank
        # line prepended -- which is what a prose edit does -- moves the code
        # down, so the paragraph's stated `edit_start` now has NO code line before
        # it: `b2` becomes `b1`, naming a different place with no complaint.
        page.code_lines_of(self.SRC, self.PARAGRAPHS)
        page.code_lines_of("\n" + self.SRC, self.PARAGRAPHS)
        self.assertEqual(addressed(self.SRC, self.PARAGRAPHS)[0], "m.py@b2")
        self.assertEqual(addressed("\n" + self.SRC, self.PARAGRAPHS)[0], "m.py@b1")


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
            got = census.census_for(path, text, census.language_for(path))
            sorted(census.code_lines(text, got))
            for b in got:
                # ! The SUFFIX only. `census_for` names a paragraph by the path it
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
        prose = [b for b in got if b.kind not in page.HOLDS_NO_PROSE]
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
            got = census.census_for(path, self.SRC, census.language_for(path))
            sorted(census.code_lines(self.SRC, got))
            self.paragraphs = [vars(b) for b in got]

    def _at(self, anchor, series):
        # ! The FOLIO only -- the temp path is noise here.
        return [
            b["address"].split("@")[-1]
            for b in addresser.for_anchor(anchor, series, self.paragraphs)
        ]

    def test_a_declaration_has_a_place_in_every_series(self):
        # !! ONE ANCHOR, THREE ADDRESSES. The declaration's line is the anchor
        # of its own `a`, of the `b` above it and of the `c` beside it.
        self.assertEqual(self._at("def go(n):", "a"), ["a1"])
        self.assertEqual(self._at("def go(n):", "c"), ["c2"])
        self.assertEqual(self._at("def go(n):", "b"), ["b2"])

    def test_the_MODULE_has_an_a_and_NEVER_a_c(self):
        # !! It has no line to open on, so nothing can sit beside it. That is
        # the one trigger the `c` foliator steps past without emitting.
        self.assertEqual(self._at("<module>", "a"), ["a0"])
        self.assertEqual(self._at("<module>", "c"), [])

    def test_the_MODULE_has_a_b_ONLY_WHERE_IT_HAS_FRONT_MATTER(self):
        """!! `b0` IS THE FILE'S OWN PROSE, not the gap above the first line of
        code -- those were one address until 2026-08-19, so a licence header and
        the comment introducing the first declaration answered to the same name.

        ! Nothing is lost by its absence here. `b0` is where a licence header,
        a shebang or a coding line sits, and any verdict proposing an edit there
        is promoted to a `query` -- Roy, 2026-08-19: *"it is supposed to promote
        any verdict that modifies that section to a query with an ask-the-human.
        Never resolved by the agents."* So there is nothing an `add` could put
        in an empty one.
        """
        # This fixture opens with a docstring and has no front matter at all.
        self.assertEqual(self._at("<module>", "b"), [])

        with_header = '# Copyright 2026 Roy.\n"""Module."""\n\nBUDGET = 3\n'
        path = Path("m.py")
        got = census.census_for(path, with_header, census.language_for(path))
        sorted(census.code_lines(with_header, got))
        found = addresser.for_anchor("<module>", "b", [vars(b) for b in got])
        self.assertEqual(
            sorted(addresser.folio_of(b["address"])[1] for b in found), ["b0"]
        )

    def test_an_anchor_the_census_never_stamped_answers_nothing(self):
        # ! Empty, not a guess. A lexical-tier language resolves no anchors at
        # all, and the caller reports that rather than being handed a neighbour.
        self.assertEqual(self._at("nosuchname", "a"), [])
        self.assertEqual(self._at("nosuchname", "b"), [])

    def test_the_c_it_names_is_the_DECLARATIONS_own_line(self):
        found = addresser.for_anchor("def go(n):", "c", self.paragraphs)
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
    `galley.paragraph_matches` refuses a stale range before it splices.
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
            sorted(census.code_lines(src.read_text(encoding="utf-8"), got))
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
    statement is in neither list and has a non-zero `edit_column`, so it took a `b`
    folio for a line it sits ON -- and that folio then named the comment AND the
    gap. Measured 2026-08-19 on `let b = 2; /* opens` / `and closes */`: `@b2`
    resolved to an empty interval, so every text check on the comment read "".
    """

    SRC = "let a = 1;\nlet b = 2; /* opens\nand closes */\nlet c = 3;\n"

    def _census(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "s.js"
            path.write_text(self.SRC, encoding="utf-8")
            return census.census_for(path, self.SRC, census.language_for(path))

    def test_the_comment_takes_a_c_because_code_precedes_it(self):
        got = self._census()
        mid = next(b for b in got if b.kind == "comment")
        self.assertTrue(mid.edit_column)
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
        paragraphs = census.census_for(path, self.SRC, census.language_for(path))
        sorted(census.code_lines(self.SRC, paragraphs))
        self.paragraphs = [vars(b) for b in paragraphs]

    def _folios(self, anchor, series):
        found = addresser.for_anchor(anchor, series, self.paragraphs)
        return sorted(addresser.folio_of(b["address"])[1] for b in found)

    def test_the_LINE_reaches_all_three_series(self):
        # !! ONE ANCHOR, THREE ADDRESSES -- the declaration's own `a`, the `b`
        # above it and the `c` beside it. This is the one-to-many relationship
        # measured on one line of code.
        self.assertEqual(self._folios("def f():", "a"), ["a1"])
        self.assertEqual(self._folios("def f():", "b"), ["b1"])
        self.assertEqual(self._folios("def f():", "c"), ["c1"])

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
        paragraphs = census.census_for(path, self.SRC, census.language_for(path))
        sorted(census.code_lines(self.SRC, paragraphs))
        self.paragraphs = [vars(b) for b in paragraphs]

    def test_every_ADDRESS_is_still_unique(self):
        # !! The direction that stays exact. This is what a record cites.
        named = [b["address"] for b in self.paragraphs]
        self.assertEqual(len(named), len(set(named)))

    def test_the_anchor_answers_with_BOTH_trailing_comments(self):
        found = addresser.for_anchor("X=2", "c", self.paragraphs)
        folios = sorted(addresser.folio_of(b["address"])[1] for b in found)
        self.assertEqual(folios, ["c1", "c2"])

    def test_they_are_two_DIFFERENT_statements(self):
        found = addresser.for_anchor("X=2", "c", self.paragraphs)
        self.assertEqual(sorted(b["start"] for b in found), [1, 5])
        self.assertEqual(sorted(b["text"] for b in found), ["initial", "reseting X"])

    def test_the_anchor_is_the_code_WITHOUT_either_comment(self):
        for b in self.paragraphs:
            if b["edit_column"]:
                with self.subTest(line=b["start"]):
                    self.assertEqual(b["anchor"], "X=2")

    def test_the_b_series_answers_with_ALL_THREE_gaps(self):
        # !! The `b` half is WORSE, and this file is why: three gaps answer to
        # one spelling -- the gap above the opening statement, the gap holding
        # `# stuff happens`, and the gap at the end of the file. ! The folios
        # below are what THIS walk emits, not a rule anything may count out.
        found = addresser.for_anchor("X=2", "b", self.paragraphs)
        folios = sorted(addresser.folio_of(b["address"])[1] for b in found)
        self.assertEqual(folios, ["b1", "b2", "b3"])

    def test_the_three_gaps_are_drawn_from_TWO_statements(self):
        """!! And the anchor STRING cannot tell you which.

        The first gap sits above the opening statement, so its anchor is that
        line's code. The second holds a comment and is anchored to the code
        BELOW it, which is line 5. The third is the gap at the end of the file
        and takes the line ABOVE, which is line 5 again. Two statements, three
        gaps, one spelling.
        """
        by_folio = {
            addresser.folio_of(b["address"])[1]: b
            for b in addresser.for_anchor("X=2", "b", self.paragraphs)
        }
        # ! Read from the EDIT range, which is the gap itself: the first is a
        # pure insertion above line 1, the second replaces line 3, the third
        # appends after 5.
        self.assertEqual(by_folio["b1"]["edit_start"], 1)
        self.assertEqual(by_folio["b2"]["edit_start"], 3)
        self.assertEqual(by_folio["b3"]["edit_start"], 6)
        for folio, paragraph in by_folio.items():
            with self.subTest(folio=folio):
                self.assertEqual(paragraph["anchor"], "X=2")

    def test_the_comment_between_them_is_anchored_to_the_code_BELOW(self):
        # ! `# stuff happens` sits between the two statements and introduces the
        # second, so its anchor is line 5's code -- not line 1's, which it
        # follows. The gap's prose is about what comes next.
        held = next(b for b in self.paragraphs if b["text"] == "stuff happens")
        self.assertEqual(addresser.folio_of(held["address"])[1], "b2")
        self.assertEqual(held["anchor"], "X=2")

    def test_X_2_is_no_declaration_so_the_a_series_is_EMPTY(self):
        # ! An assignment is not a declaration the census names, so nothing
        # answers in `a`. ! The module's `a0` does not answer either: it keeps
        # `<module>`. Anchoring it to the FIRST LINE OF CODE was tried and made
        # a module's documentation answer to `X=2`.
        self.assertEqual(addresser.for_anchor("X=2", "a", self.paragraphs), [])

    def test_the_CLI_says_the_answer_is_AMBIGUOUS_in_both_series(self):
        # !! What an agent actually sees. Without it a caller reads the first
        # line of output as "the" answer and rules on the wrong statement.
        for series, count in (("b", 3), ("c", 2)):
            with self.subTest(series=series):
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    rc = addresser._for_anchor("X=2", series, self.paragraphs)
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
        paragraphs = census.census_for(path, self.SRC, census.language_for(path))
        self.code = sorted(census.code_lines(self.SRC, paragraphs))
        self.at = {
            b.address.split("@")[1]: b for b in paragraphs if "@" in (b.address or "")
        }

    def test_the_MODULE_is_a_trigger_that_c_does_not_emit_for(self):
        # !! The one rule the three share. `a` and `b` emit at the module; `c`
        # steps past it, because a module has front matter and a docstring and
        # no line to sit beside.
        self.assertNotIn("c0", self.at)
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
        text = Path(addresser.__file__).read_text(encoding="utf-8")
        code = [
            ln
            for ln in text.splitlines()
            if ln.strip() and not ln.lstrip().startswith(("#", '"', "'"))
        ]
        body = "\n".join(code)
        self.assertNotIn('f"{path}@c{code.index(start)}"', body)
        self.assertNotIn('sum(1 for n in code if n < at)}"', body)
        self.assertIn("def folio(", body)

    def test_the_walk_is_one_list_for_b_and_c(self):
        # ! `triggers` is the module then every line of code. Both read it, so
        # neither can drift from the other by being edited alone.
        walk = addresser.triggers(self.code)
        self.assertEqual(walk[0], addresser.MODULE)
        self.assertEqual(walk[1:], self.code)
