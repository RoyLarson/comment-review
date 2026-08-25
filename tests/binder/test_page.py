"""`page.py` says what a PAGE is, and `addresser.py` is the LEAF beneath it.

!! THE DIRECTION INVERTED 2026-08-20, and the reason is that a page BUILDS
ITSELF. It has to name the places on it, so it needs the addresser -- while the
cues had been importing `page` for two constants. That is a cycle, and the
cut is that **the cues knows nothing about a paragraph**: `code_lines_of`
and `attach` were the only two functions of it that did, and both are page
questions wearing an addressing name.

! The property the original split bought still holds and is what these tests
guard: every module that READS a paragraph can import the definition of one.
`Paragraph` lived in `census.py`, the top of the import graph, so `galley`,
`cues` and `record` read untyped dicts instead, and the two kind sets ended
up in `galley` because it was the deepest module all three could reach.
"""

import ast
import collections
import unittest
from pathlib import Path

# ! `_paths` FIRST: importing it is what puts `src/` on the path.
from _paths import MODULES, command_source, source_of  # noqa: I001

from comment_review.binder import page
from comment_review.reading import addresser, lexer

SIBLINGS = set(MODULES)


# !! A LEAF IS NOT A DEPENDENCY, and every rule below is about dependencies.
# `constants` imports nothing from this package -- it holds the console guard and
# `text_lines`, the one definition of where a line of a FILE ends -- so taking it
# acquires no subject and can carry no notion of anything. See `constants.py`,
# which states that contract itself.
LEAF = {"constants", "exceptions"}


def _imports(name: str) -> set[str]:
    """The sibling modules `name` imports, LEAVES excluded.

    !! A RELATIVE IMPORT NAMES ITS MODULE IN ONE OF TWO PLACES, and which one
    depends on whether the target is a module or a package. `from ..reading.lexer
    import Kind` names `lexer` in the MODULE path; `from ..machine import
    constants` names `constants` in the ALIAS list, because `machine` is the
    package. ! Both are read and the intersection with `SIBLINGS` decides which
    half was the module -- taking `node.module` alone returns the PACKAGE and
    matches no sibling, so every rule below would pass on an empty set.
    """
    tree = ast.parse(source_of(name))
    got = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module:
                got.update(node.module.split("."))
            got.update(a.name for a in node.names)
        elif isinstance(node, ast.Import):
            got.update(a.name.split(".")[0] for a in node.names)
    return got & (SIBLINGS - {name} - LEAF)


class TestTheTwoLeaves(unittest.TestCase):
    """`addresser` names places; `lexer` finds prose. Neither knows the other.

    !! THAT IS THE SHAPE, and it is why the page can be one subject. A place has
    no prose in it, and prose has no place until a page puts the two together --
    so the two halves are independent and the page is the only thing that needs
    both.
    """

    def test_the_addresser_knows_nothing_about_prose(self):
        # ! `repo` is the exception and is not one: it answers what the CHECKOUT
        # says -- git, the filesystem, the exception tuples -- and carries no
        # notion of prose at all.
        #
        self.assertEqual(_imports("addresser") - {"repo"}, set())

    def test_the_lexer_knows_nothing_about_places(self):
        # !! IT DEFINES WHAT IT PRODUCES -- `Paragraph` -- and stops there. Where
        # that paragraph SITS is the page's, which is why the lexer needs no
        # address and no cues.
        # ! ONE SIBLING SINCE 2026-08-21, and it is the rows it reads a file
        # with. Roy: *"The language definition file should be a leaf separate
        # from everything else and imported only by lexer and compositor."*
        self.assertEqual(_imports("lexer"), {"language"})

    def test_the_LANGUAGE_ROWS_are_a_leaf_with_two_importers(self):
        # !! THE RULE, ENFORCED. Roy, 2026-08-21: *"All framing about positioning
        # should come from the language and should be only in either the language
        # definition file, or a reference to the language definition file in
        # lexer and compositor."* The lexer reads a file into paragraphs and the
        # compositor sets a page back into one; they are the only two modules
        # that touch a file, so they are the only two that may ask a language
        # anything.
        #
        # ! While the rows sat inside `lexer.py`, FOUR more modules imported them
        # through it -- `census`, `desk`, `page` and `prove_unchanged` -- and
        # every module holding a `Language` is a place a positioning rule can be
        # written a second time and drift from the first.
        self.assertEqual(_imports("language"), set())
        readers = {name for name in SIBLINGS if "language" in _imports(name)}
        self.assertEqual(readers, {"lexer", "compositor"})

    def test_the_page_imports_BOTH_and_nothing_else(self):
        # !! THE PAGE BUILDS ITSELF: it asks the lexer where the prose is and the
        # cues what to call each place. That is the whole inversion.
        self.assertEqual(_imports("page"), {"addresser", "lexer"})

    def test_every_module_that_reads_a_paragraph_can_import_one(self):
        # ! `galley` and `record` are not here. Both read paragraph DICTS rather
        # than the type: galley's staleness check keys on whether text was
        # stored, and record asks one question about a KIND. Either joins this
        # list when it takes the type itself.
        #
        # !! IT IS THE COMMAND THAT BUILDS PAGES, NOT THE FLOW, AND THAT IS A
        # DEFECT THIS ASSERTION IS RECORDING RATHER THAN BLESSING. Lifting the
        # entry points out on 2026-08-24 showed that `census`'s orchestration
        # lived inside `main`/`_report` all along: `flows/census.py` kept 261
        # lines of helpers and `commands/census.py` took 446 lines that call
        # `page_for`. A command is supposed to EXPOSE a flow, not be one --
        # `decision-log.md Process: #12`.
        #
        # ! WHEN THE FLOW IS PUT BACK, THIS READS `source_of` AGAIN. Tracked in
        # `TODO/the-flow-lives-in-the-command.md`.
        self.assertIn("from ..binder.page import", command_source("census"))

    def test_the_ULTIMATE_LEAF_is_only_ever_imported_WHOLE(self):
        """`import constants`, never `from constants import`.

        !! ROY'S RULE, 2026-08-22: *"constants.py is the ultimate leaf"*, and
        *"you can't do `from constants import` anywhere. All things are
        `import constants`, `constants.ENCODING`."*

        ! IT IS ABOUT THIS MODULE, not about re-export in general. What the form
        buys is that `constants` CANNOT BE RE-EXPORTED: a `from constants import
        text_lines` binds that name into the importing module, and a third module
        can then take it from there -- so a module that owns nothing becomes a
        door to the leaf. A qualified `constants.text_lines` names the owner at
        every call site, and there is no local name for anyone to take.

        ! Every module may import it, because it is the leaf beneath all of them
        and taking it acquires no subject.
        """
        offenders = [
            p.name
            for p in sorted(MODULES.values())
            if "from constants import" in p.read_text(encoding="utf-8")
        ]
        self.assertEqual(offenders, [])

    def test_the_ULTIMATE_LEAF_IMPORTS_NOTHING_FROM_THIS_PACKAGE(self):
        # ! The other half of the contract, and what makes it safe for anything
        # to take: `constants` cannot pull a sibling in behind it.
        tree = ast.parse(source_of("constants"))
        taken = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                taken.add(node.module.split(".")[0])
            elif isinstance(node, ast.Import):
                taken.update(a.name.split(".")[0] for a in node.names)
        self.assertEqual(taken & SIBLINGS, set())

    def test_a_KIND_question_goes_to_the_LEAF_and_not_through_the_page(self):
        # !! `record` IMPORTED NOTHING ELSE FROM `page`, and what it imported was
        # a re-export: `page.HOLDS_NO_PROSE` was `lexer`'s tuple under a second
        # name. So the edge existed to carry a constant that was never the
        # page's, and asking `lexer.Kind` directly removed the edge entirely.
        #
        # ! THE OLD TEST COULD NOT SEE THIS. It asserted the STRING
        # `"from page import"` appeared, which a pass-through satisfies exactly
        # as well as a real dependency does.
        text = source_of("record")
        self.assertIn("from ..reading.lexer import Kind", text)
        self.assertNotIn("from ..binder.page import", text)


class TestAPageCarriesWhatItWasBuiltFrom(unittest.TestCase):
    """!! THE REASON IT IS A TYPE and not a list.

    `page_for` returned a bare list and dropped the text, the cues, the
    tier and the path. Every consumer that needed one of them either re-derived
    it from the file -- a chance to read a file the page no longer describes --
    or made the caller carry it alongside.
    """

    SRC = '"""Doc."""\n\n# introduces N\nN = 0\n\n\ndef f():\n    return N\n'

    def setUp(self):
        path = Path("pkg/m.py")
        self.page = page.page_for(path, self.SRC, lexer.language_for(path), "pkg/m.py")

    def test_it_knows_its_own_path_as_the_repo_sees_it(self):
        self.assertEqual(self.page.path, "pkg/m.py")

    def test_it_carries_the_text_a_splice_is_checked_against(self):
        self.assertEqual(self.page.text, self.SRC)

    def test_it_carries_NO_tier(self):
        """!! DELETED 2026-08-24, and the absence is asserted rather than left.

        Roy: *"their level gets dropped entirely. Not necessary and the parser
        tier isn't long for this world."* The field stamped one of two words
        onto every paragraph of a file, and its only reader was a census
        counter printing one line of preamble about a distinction
        `python-cannot-read-python` is about to erase.

        ! `tier_for(lang)` SURVIVES and answers `--languages`: which tier a
        LANGUAGE reaches is a fact about the language. What went is the stamp
        on a place.
        """
        self.assertFalse(hasattr(self.page, "tier"))
        self.assertFalse(any(hasattr(b, "tier") for b in self.page))

    def test_a_page_IS_its_paragraphs_in_order(self):
        # ! A reviewer reads a page top to bottom, so it iterates and indexes as
        # one. A consumer that wants the list is asking for the page.
        self.assertEqual(list(self.page), self.page.paragraphs)
        self.assertEqual(len(self.page), len(self.page.paragraphs))
        self.assertIs(self.page[0], self.page.paragraphs[0])

    def test_it_carries_EVERY_place_filled_or_not(self):
        # !! What makes an `add` citable. The walk emitted these before any
        # prose was looked at, so a place exists whether or not anything sits
        # in it -- including `f0`, which no paragraph occupies here.
        cues = set(self.page.cues.places)
        self.assertIn("f0", cues)
        self.assertIn("a0", cues)
        # !! EVERY PLACE HAS A PARAGRAPH -- that is what the collapse bought.
        # A place the walk emitted and nothing filled gets an empty paragraph,
        # so the two sets are equal rather than the cues being a superset.
        occupied = {b.address.split("@")[-1] for b in self.page if "@" in b.address}
        self.assertEqual(cues, occupied)

    def test_prose_is_what_a_reviewer_owes_a_record_on(self):
        # ! The empty places are ADDRESSABLE and not accountable.
        kinds = {b.kind for b in self.page.prose}
        self.assertNotIn("interval", kinds)
        self.assertNotIn("margin", kinds)
        self.assertNotIn("undocumented", kinds)
        self.assertLess(len(self.page.prose), len(self.page))

    def test_an_unparsed_file_carries_an_EMPTY_cues(self):
        # !! HONEST RATHER THAN INVENTED. The walk never ran, because the code
        # lines were never established -- so a consumer that asks gets nothing
        # instead of a table built over lines nobody found.
        path = Path("bad.py")
        broken = page.page_for(path, "x = = 1\n", lexer.language_for(path))
        self.assertEqual(broken.cues.places, {})
        self.assertTrue(any(b.kind == "unparsed" for b in broken))


def covers(paragraph, which="original") -> list[int]:
    """The lines this paragraph covers -- a CLOSED list, or empty.

    !! `original_start`/`original_end` are `[lo..hi]` INCLUSIVE, or None when no
    line carries that cues. Roy, 2026-08-20. There is no `(n, n - 1)`
    empty-slice form to decode, which is why this reads as a membership question
    and not as arithmetic.
    """
    if which == "original":
        lo, hi = paragraph.original_start, paragraph.original_end
    else:
        # ! The ADDRESSING range still spells "occupies nothing" as `0/0`.
        lo, hi = paragraph.start, paragraph.end
        lo = lo if lo >= 1 else None
    if lo is None or hi is None or hi < lo:
        return []
    return list(range(lo, hi + 1))


class TestEveryLineBelongsToExactlyOneParagraph(unittest.TestCase):
    """Roy, 2026-08-20: *"on the original every line belongs to 1 paragraph and
    every paragraph belongs to 1 anchor."*

    !! EXACTLY one, so a line in NONE breaks it as surely as a line in two. It
    held on the ADDRESSING range and not on the original: measured over the 16
    shipped scripts, 105 lines in 16 of 16 files were addressed by a paragraph
    and covered by none, every one blank and every one at the edge of a gap.
    """

    SHAPES = {
        "a wholly empty gap": "x = 1\n\n\n\ny = 2\n",
        "one comment in a gap": "x = 1\n\n# a note\n\ny = 2\n",
        "two runs in one gap": "x = 1\n\n# one\n\n# two\n\ny = 2\n",
        "docstring then blank": '"""Doc."""\n\nimport os\n',
        "front matter and docstring": (
            '#!/usr/bin/env python\n\n"""Doc."""\n\nimport os\n'
        ),
        "a trailing comment": "x = 1  # beside\n\ny = 2\n",
        "no trailing newline": "x = 1\n\n# a note",
    }

    def owners(self, text, attr):
        """Line -> how many paragraphs own it, BY PRECEDENCE.

        !! `a` AND `c` ARE EXACT AND `b` TAKES THE REST, so a `b`'s SPAN may
        cross an `a` without owning its lines. Roy, 2026-08-20: *"a's and c's
        own their lines exactly, b's own all the other lines. a's and c's get
        set first because of this, b's get set after."* Counting a raw range
        overlap asks a question the rule does not answer.
        """
        path = Path("m.py")
        pg = page.page_for(path, text, lexer.language_for(path))
        counts = collections.Counter()
        exact = set()

        # ! EVERY SERIES BUT `b` IS EXACT -- `a`, `c`, and `f` since front
        # matter got its own -- and LEADING with them, by its SYMBOL.
        #
        # !! NAMING THE EXACT ONES IS HOW THIS DRIFTS, TWICE NOW. First `f0` was
        # in neither branch and its line came out owned by nobody. Then
        # 2026-08-22, when `d` left `addresser.SERIES` and gave up its address,
        # every run of blank lines fell into the same hole -- read from
        # `address` alone a `d` answers `""`, which this excludes.
        def series(b):
            return (b.address.split("@")[-1] or b.symbol)[:1]

        for b in pg:
            if series(b) not in ("b", ""):
                counts.update(covers(b, attr))
                exact.update(covers(b, attr))
        for b in pg:
            if series(b) == "b":
                counts.update(n for n in covers(b, attr) if n not in exact)
        return {n: counts.get(n, 0) for n in range(1, len(text.splitlines()) + 1)}

    def test_on_both_ranges_every_line_has_exactly_one_owner(self):
        for attr in ("address", "original"):
            for name, text in self.SHAPES.items():
                with self.subTest(range=attr, shape=name):
                    got = self.owners(text, attr)
                    self.assertEqual(
                        {n: c for n, c in got.items() if c != 1},
                        {},
                        f"{name}: line -> owner count",
                    )

    def test_the_blank_at_a_gaps_edge_belongs_to_LEADING(self):
        # !! IT WENT TO THE `b` UNTIL 2026-08-21, and that is what could not be
        # set back: a `b` holding the blanks on BOTH sides of an `a` is ONE entry
        # in the reading order, so its two lines emitted together and the file
        # came back blank-blank-docstring where it was blank-docstring-blank.
        #
        # ! Not to the `a` either, and that reason still holds: an `a` has none
        # of the flexibility that lets a blank be absorbed and given back.
        text = '"""Doc."""\n\nimport os\n'
        path = Path("m.py")
        pg = page.page_for(path, text, lexer.language_for(path))
        owner = next(b for b in pg if 2 in covers(b))
        self.assertEqual(owner.kind, lexer.Kind.LEADING, owner.symbol)
        # ! ITS `d` IS A SYMBOL, NOT AN ADDRESS, since 2026-08-22 -- leading
        # names no place, so it carries a label and cites nothing.
        self.assertTrue(owner.symbol.startswith("d"), owner.symbol)
        self.assertEqual(owner.address, "")

    def test_every_paragraph_names_one_anchor(self):
        # ! EXCEPT LEADING, whose anchor is empty by ruling rather than by
        # omission: every other series answers to a line of code, and the space
        # between two paragraphs answers to nothing. Roy, 2026-08-21, taking the
        # trade: *"I like the leading solution even though it added another
        # cues and the anchors are empty."*
        for name, text in self.SHAPES.items():
            with self.subTest(shape=name):
                path = Path("m.py")
                for b in page.page_for(path, text, lexer.language_for(path)):
                    if b.kind == lexer.Kind.LEADING:
                        continue
                    self.assertTrue(b.anchor, f"{name}: {b.address} has no anchor")

    def test_raw_lines_are_the_lines_this_paragraph_OWNS(self):
        # !! THEY ARE NOT THE WHOLE RANGE, since 2026-08-21. A `b` takes the
        # lines of its gap that no other series owns exactly -- Roy: *"b owns the
        # blank line -- same answer as the blanks around a's and c's for the same
        # reason. it is the flex in the system. it makes the covering precise and
        # full."* So a gap holding an `f0` runs THROUGH it: the range spans it,
        # `raw_lines` does not, and the two together are what makes the covering
        # precise.
        #
        # ! It read `raw_lines == the range's lines` before, because the SPLICING
        # galley compared them that way. That galley is what the compositor
        # replaces, and its successor checks an anchor rather than a range.
        for name, text in self.SHAPES.items():
            with self.subTest(shape=name):
                path = Path("m.py")
                lines = text.splitlines()
                built = page.page_for(path, text, lexer.language_for(path))
                exact = {
                    n
                    for other in built
                    if other.address.split("@")[-1][:1] != "b"
                    for n in covers(other)
                }
                for b in built:
                    held = covers(b)
                    # ! A `c` stores only the half of its first line that is
                    # prose, so `raw_lines` is not that line whole.
                    if b.original_column or not held:
                        continue
                    # ! Every other series owns its range exactly; only a `b`
                    # gives way to what sits inside it.
                    is_gap = b.address.split("@")[-1][:1] == "b"
                    mine = [n for n in held if not (is_gap and n in exact)]
                    want = [lines[n - 1] for n in mine]
                    self.assertEqual(
                        [ln.rstrip() for ln in b.raw_lines],
                        [ln.rstrip() for ln in want],
                        f"{name}: {b.address}",
                    )

    def test_a_place_with_no_lines_says_None_and_not_an_empty_range(self):
        # !! ROY'S RULE, 2026-08-20: a closed list `[1..7]`, *"or it is None,
        # meaning there are currently no lines that have that cues."* The
        # `(n, n - 1)` form it replaced reads as a range and invites arithmetic.
        path = Path("m.py")
        text = "x = 1\ny = 2\n"  # adjacent code: the gap between them holds nothing
        empty = [
            b
            for b in page.page_for(path, text, lexer.language_for(path))
            if b.kind in ("interval", "undocumented")
        ]
        self.assertTrue(empty)
        for b in empty:
            with self.subTest(address=b.address):
                self.assertIsNone(b.original_start)
                self.assertIsNone(b.original_end)


class TestAnEmptyPlaceHoldsNoProse(unittest.TestCase):
    """The kind says a place holds no prose; the lines must agree.

    !! IT IS THE KIND'S WHOLE MEANING. `census.py` tells four reviewers that an
    `interval` is a place where prose could go and does NOT, and an `add` is the
    verdict that cites one. A paragraph that says `interval` while owning a line
    with text on it is a false statement to every reader of the census, before
    any galley runs.

    ! MEASURED 2026-08-20 on a shebang + licence + module docstring: `@b0` was a
    `comment` reported as `2L` and owning NO lines, while `@b1`, an `interval`
    reported as `0L`, owned both lines of the licence header. The row was
    self-contradicting on its face.

    ! The cause was `fill_the_gaps` sharing a gap out to front matter, whose
    `b0` is the FILE'S own place and not that gap's. This states the property
    without naming front matter, so it holds for whatever else reaches the same
    shape.
    """

    SHAPES = {
        "shebang, licence, docstring": (
            '#!/usr/bin/env python\n# Copyright 2024\n"""Doc."""\nX = 1\n'
        ),
        "shebang and licence, NO docstring": (
            "#!/usr/bin/env python\n# Copyright 2024\nX = 1\n"
        ),
        "a licence, a blank, then code": "# Copyright 2024\n\nX = 1\n",
        "an ordinary comment": "# just a note about X\nX = 1\n",
        "a coding line": "# -*- coding: utf-8 -*-\nX = 1\n",
        "front matter and nothing else": "#!/usr/bin/env python\n",
    }

    def test_an_interval_owns_only_blank_lines(self):
        for name, text in self.SHAPES.items():
            with self.subTest(shape=name):
                path = Path("m.py")
                lines = text.splitlines()
                for b in page.page_for(path, text, lexer.language_for(path)):
                    if b.kind != "interval":
                        continue
                    held = covers(b)
                    self.assertEqual(
                        [n for n in held if lines[n - 1].strip()],
                        [],
                        f"{name}: {b.address} is an interval holding text",
                    )

    def test_an_undocumented_declaration_owns_nothing(self):
        for name, text in self.SHAPES.items():
            with self.subTest(shape=name):
                path = Path("m.py")
                for b in page.page_for(path, text, lexer.language_for(path)):
                    if b.kind == "undocumented":
                        self.assertEqual(covers(b), [], f"{name}: {b.address}")

    def test_prose_owns_the_lines_it_was_read_from(self):
        # ! The other half: a paragraph reported as `NL` of prose must hold
        # lines. `@b0` reported 2L and held none.
        for name, text in self.SHAPES.items():
            with self.subTest(shape=name):
                path = Path("m.py")
                for b in page.page_for(path, text, lexer.language_for(path)):
                    if lexer.Kind.holds_no_prose(b.kind) or not b.text.strip():
                        continue
                    self.assertTrue(
                        covers(b),
                        f"{name}: {b.address} is {b.lines}L and holds no line",
                    )


class TestEverySeriesHasAPositiveAndANegative(unittest.TestCase):
    """The pairing is the structure, and the negatives are read off it.

    !! IT WAS TWO HAND-KEPT TUPLES, and this class was named
    `TestTheTwoKindSetsAreNotInterchangeable` while proving the opposite: its
    first test asserted `trailing-comment` was in NEITHER set, which shows
    nothing about two sets that hold identical members. Roy, 2026-08-22: *"each
    cues gets its positive and its negative"*, and *"they are enums not a
    list."*
    """

    def test_each_series_pairs_prose_with_its_absence(self):
        self.assertEqual(
            {s.name: (s.value.present, s.value.absent) for s in lexer.Series},
            {
                "DECLARED": ("docstring", "undocumented"),
                "GAP": ("comment", "interval"),
                "ON": ("trailing-comment", "margin"),
                "COVERS": ("matter", "dark-matter"),
            },
        )

    def test_the_pair_is_NAMED_and_not_positional(self):
        # ! `pair[0]` and `pair[1]` said nothing, so every reader had to know
        # which way round they went. Roy: *"NamedTuples(present, absent)."*
        self.assertEqual(lexer.Series.ON.value.present, "trailing-comment")
        self.assertEqual(lexer.Series.ON.value.absent, "margin")

    def test_the_absences_are_DERIVED_and_not_listed(self):
        # ! The thing a hand-kept tuple could get wrong, and did.
        self.assertEqual(lexer.ABSENT, {s.value.absent for s in lexer.Series})

    def test_every_series_NAME_is_a_addresser_constant(self):
        # !! WHAT TIES THE TWO MODULES, now that the letters are spelled in only
        # ONE of them. `lexer` cannot import `addresser` -- it takes no sibling
        # but `language` -- so a letter it duplicated could drift in silence.
        # The member NAME carries the link instead, and this fails if either
        # side renames a series without the other.
        self.assertEqual(
            sorted(getattr(addresser, s.name) for s in lexer.Series),
            sorted(addresser.SERIES),
        )

    def test_LEADING_IS_A_KIND_WITH_NO_SERIES(self):
        # !! SQUARING THE TABLE WOULD BE THE ERROR. An empty leading run could
        # not be cited -- Roy: *"there is no information to rule on"* -- which
        # is the same reason `d` is not in `addresser.SERIES`. So `Kind` keeps
        # nine members and `Series` covers the eight that pair.
        self.assertIn(lexer.Kind.LEADING, set(lexer.Kind))
        self.assertNotIn(
            lexer.Kind.LEADING,
            {k for s in lexer.Series for k in s.value},
        )

    def test_leading_HOLDS_NO_PROSE_BUT_OCCUPIES_LINES(self):
        # !! THE TWO QUESTIONS PART ON EXACTLY THIS MEMBER, which is why one
        # merged set was wrong. A blank run has nothing to read AND stands on
        # real lines; answering the second with the first takes those lines out
        # of `occupied` in `code_lines`, so they read as CODE and every `b` and
        # `c` below them renumbers.
        self.assertTrue(lexer.Kind.holds_no_prose(lexer.Kind.LEADING))
        self.assertFalse(lexer.Kind.occupies_no_lines(lexer.Kind.LEADING))

    def test_the_two_questions_agree_on_every_OTHER_kind(self):
        # ! Leading is the ONLY member they part on -- so the merge was right
        # about the four negatives and wrong about the ninth kind.
        parted = [
            k
            for k in lexer.Kind
            if k is not lexer.Kind.LEADING
            and lexer.Kind.holds_no_prose(k) != lexer.Kind.occupies_no_lines(k)
        ]
        self.assertEqual(parted, [])

    def test_a_wrapped_trailing_comment_takes_its_continuation_lines(self):
        path = Path("a.c")
        text = "int a = 1;\nint b = 2; /* opens\n   runs on */\nint c = 3;\n"
        got = page.code_lines(
            text, [vars(b) for b in page.page_for(path, text, lexer.language_for(path))]
        )
        # Line 2 still holds `int b = 2;`; line 3 is comment and is NOT code.
        self.assertEqual(list(got), [1, 2, 4])
        self.assertEqual(got[2], "int b = 2;")

    def test_every_absence_belongs_to_exactly_ONE_series(self):
        for kind in lexer.ABSENT:
            with self.subTest(kind=kind):
                owner = [s.name for s in lexer.Series if s.value.absent == kind]
                self.assertEqual(len(owner), 1, f"{kind} belongs to {owner}")
