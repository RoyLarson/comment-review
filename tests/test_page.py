"""`page.py` says what a pCST node is, and it must stay a LEAF.

!! THAT IS THE WHOLE REASON IT EXISTS. `Paragraph` lived in `census.py`, the top of
the import graph, so `galley`, `addresser` and `record` -- which all read paragraphs
-- could not import the definition of one. They read untyped dicts instead, and
the two kind sets ended up in `galley` because it was the deepest module all
three could reach. A sibling import here puts that back.
"""

import ast  # noqa: I001  -- path shim below must import before page
import unittest

from _paths import SCRIPTS  # noqa: F401
import page

SIBLINGS = {p.stem for p in SCRIPTS.glob("*.py")} - {"page"}


class TestItIsALeaf(unittest.TestCase):
    def test_page_imports_no_sibling(self):
        tree = ast.parse((SCRIPTS / "page.py").read_text(encoding="utf-8"))
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
            elif isinstance(node, ast.Import):
                imported.update(a.name.split(".")[0] for a in node.names)
        self.assertEqual(imported & SIBLINGS, set(), "page must import no sibling")

    def test_every_module_that_reads_a_block_can_import_one(self):
        # ! The property the split bought. Each of these operates on paragraphs.
        # ! `galley` is not here. It reads paragraph DICTS and needs none of the
        # kinds -- its staleness check keys on whether text was stored, not on
        # what kind the paragraph is. It joins this list when it takes the type.
        for name in ("addresser", "record", "census"):
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


if __name__ == "__main__":
    unittest.main()
