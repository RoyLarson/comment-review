"""`page.py` says what a pCST node is, and `addresser.py` is the LEAF beneath it.

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

from _paths import SCRIPTS  # noqa: F401
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


class TestTheAddresserIsTheLeaf(unittest.TestCase):
    """It names places. It does not know what a paragraph is."""

    def test_the_addresser_imports_no_sibling_that_knows_a_paragraph(self):
        # ! `repo` is the exception and is not one: it answers what the CHECKOUT
        # says -- git, the filesystem, the exception tuples -- and carries no
        # notion of prose at all.
        self.assertEqual(_imports("addresser") - {"repo"}, set())

    def test_the_page_imports_the_addresser_and_nothing_else(self):
        # !! THE PAGE BUILDS ITSELF, so it needs the foliator to name the places
        # on it. That is the whole inversion.
        self.assertEqual(_imports("page"), {"addresser"})

    def test_every_module_that_reads_a_paragraph_can_import_one(self):
        # ! `galley` is not here. It reads paragraph DICTS and needs none of the
        # kinds -- its staleness check keys on whether text was stored, not on
        # what kind the paragraph is. It joins this list when it takes the type.
        for name in ("record", "census"):
            with self.subTest(module=name):
                text = (SCRIPTS / f"{name}.py").read_text(encoding="utf-8")
                self.assertIn("from page import", text)


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
