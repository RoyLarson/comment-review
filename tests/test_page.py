"""`page.py` says what a PAGE is, and `addresser.py` is the LEAF beneath it.

!! THE DIRECTION INVERTED 2026-08-20, and the reason is that a page BUILDS
ITSELF. It has to name the places on it, so it needs the foliator -- while the
addresser had been importing `page` for two constants. That is a cycle, and the
cut is that **the addresser knows nothing about a paragraph**: `code_lines_of`
and `attach` were the only two functions of it that did, and both are page
questions wearing an addressing name.

! The property the original split bought still holds and is what these tests
guard: every module that READS a paragraph can import the definition of one.
`Paragraph` lived in `census.py`, the top of the import graph, so `galley`,
`addresser` and `record` read untyped dicts instead, and the two kind sets ended
up in `galley` because it was the deepest module all three could reach.
"""

import ast  # noqa: I001  -- path shim below must import before page
import unittest
from pathlib import Path

from _paths import SCRIPTS  # noqa: F401
import lexer
import page

SIBLINGS = {p.stem for p in SCRIPTS.glob("*.py")}


def _imports(name: str) -> set[str]:
    """The sibling modules `name` imports."""
    tree = ast.parse((SCRIPTS / f"{name}.py").read_text(encoding="utf-8"))
    got = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            got.add(node.module.split(".")[0])
        elif isinstance(node, ast.Import):
            got.update(a.name.split(".")[0] for a in node.names)
    return got & (SIBLINGS - {name})


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
        self.assertEqual(_imports("addresser") - {"repo"}, set())

    def test_the_lexer_knows_nothing_about_places(self):
        # !! IT DEFINES WHAT IT PRODUCES -- `Paragraph` -- and stops there. Where
        # that paragraph SITS is the page's, which is why the lexer needs no
        # address and no foliation.
        self.assertEqual(_imports("lexer"), set())

    def test_the_page_imports_BOTH_and_nothing_else(self):
        # !! THE PAGE BUILDS ITSELF: it asks the lexer where the prose is and the
        # addresser what to call each place. That is the whole inversion.
        self.assertEqual(_imports("page"), {"addresser", "lexer"})

    def test_every_module_that_reads_a_paragraph_can_import_one(self):
        # ! `galley` is not here. It reads paragraph DICTS and needs none of the
        # kinds -- its staleness check keys on whether text was stored, not on
        # what kind the paragraph is. It joins this list when it takes the type.
        for name in ("record", "census"):
            with self.subTest(module=name):
                text = (SCRIPTS / f"{name}.py").read_text(encoding="utf-8")
                self.assertIn("from page import", text)


class TestAPageCarriesWhatItWasBuiltFrom(unittest.TestCase):
    """!! THE REASON IT IS A TYPE and not a list.

    `page_for` returned a bare list and dropped the text, the foliation, the
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

    def test_it_knows_which_questions_its_reader_could_answer(self):
        self.assertEqual(self.page.tier, "tokenized")

    def test_a_page_IS_its_paragraphs_in_order(self):
        # ! A reviewer reads a page top to bottom, so it iterates and indexes as
        # one. A consumer that wants the list is asking for the page.
        self.assertEqual(list(self.page), self.page.paragraphs)
        self.assertEqual(len(self.page), len(self.page.paragraphs))
        self.assertIs(self.page[0], self.page.paragraphs[0])

    def test_it_carries_EVERY_place_filled_or_not(self):
        # !! What makes an `add` citable. The walk emitted these before any
        # prose was looked at, so a place exists whether or not anything sits
        # in it -- including `b0`, which no paragraph occupies here.
        folios = set(self.page.foliation.places)
        self.assertIn("b0", folios)
        self.assertIn("a0", folios)
        occupied = {b.address.split("@")[-1] for b in self.page if "@" in b.address}
        self.assertTrue(folios - occupied, "every place is occupied -- no empty ones?")

    def test_prose_is_what_a_reviewer_owes_a_record_on(self):
        # ! The empty places are ADDRESSABLE and not accountable.
        kinds = {b.kind for b in self.page.prose}
        self.assertNotIn("interval", kinds)
        self.assertNotIn("margin", kinds)
        self.assertNotIn("undocumented", kinds)
        self.assertLess(len(self.page.prose), len(self.page))

    def test_an_unparsed_file_carries_an_EMPTY_foliation(self):
        # !! HONEST RATHER THAN INVENTED. The walk never ran, because the code
        # lines were never established -- so a consumer that asks gets nothing
        # instead of a table built over lines nobody found.
        path = Path("bad.py")
        broken = page.page_for(path, "x = = 1\n", lexer.language_for(path))
        self.assertEqual(broken.foliation.places, {})
        self.assertTrue(any(b.kind == "unparsed" for b in broken))


class TestTheTwoKindSetsAreNotInterchangeable(unittest.TestCase):
    """A trailing comment occupies no lines of its own AND is prose."""

    def test_a_trailing_comment_occupies_nothing_but_holds_prose(self):
        self.assertIn("trailing-comment", page.OCCUPIES_NOTHING)
        self.assertNotIn("trailing-comment", page.HOLDS_NO_PROSE)

    def test_the_empty_kinds_are_in_both(self):
        for kind in ("interval", "undocumented"):
            with self.subTest(kind=kind):
                self.assertIn(kind, page.OCCUPIES_NOTHING)
                self.assertIn(kind, page.HOLDS_NO_PROSE)
