"""The `d` series: the empty space between two paragraphs.

Roy, 2026-08-21, ruling it in: *"I like the leading solution even though it added
another foliation and the anchors are empty."* And the rule: *"it covers all
empty space between two different types of paragraphs. If the new line is
internal to the paragraph then the two paragraphs + the newlines are in fact one
paragraph."*

!! WHY IT EXISTS. A `b` owned the blanks on BOTH sides of an `a`, which is exact
covering and unsettable: a folio is ONE entry in the reading order, so its two
lines emitted together and a file came back blank-blank-comment where it was
blank-comment-blank. Every paragraph is CONTIGUOUS with leading, so the straddle
cannot arise.

! IT IS THE ORDINARY SHAPE OF A PYTHON FILE -- a licence header, a blank, the
module docstring, a blank, the first import -- which is why 16 of 185 files in
`corpora/meta-package-manager` failed to set back before this.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parents[1]
        / "plugins/comment-review/skills/comment-review/scripts"
    ),
)

import compositor  # noqa: E402
import lexer  # noqa: E402
import page as page_mod  # noqa: E402


def built(name: str, text: str):
    """The page for this text."""
    p = Path(name)
    return page_mod.page_for(p, text, lexer.language_for(p), rel=name)


def owner(page, line: int) -> str:
    """The folio of the paragraph holding this line."""
    for b in page:
        first, last = b.original_start, b.original_end
        if first and last and first <= line <= last and not b.original_column:
            return b.address.split("@")[-1]
    return ""


class TestLeadingHoldsTheSpaceBetween(unittest.TestCase):
    def test_the_blank_between_code_and_a_comment_is_a_d(self):
        page = built("x.c", "int a;\n\n/* doc */\n\nint b;\n")
        self.assertEqual(owner(page, 2), "d0")
        self.assertEqual(owner(page, 4), "d1")

    def test_the_comment_between_them_keeps_ONLY_its_own_line(self):
        # ! It held 2-4 before -- its prose and the blanks either side.
        page = built("x.c", "int a;\n\n/* doc */\n\nint b;\n")
        self.assertEqual(owner(page, 3), "b1")

    def test_a_blank_INSIDE_a_run_stays_in_the_run(self):
        # !! THE HALF OF THE RULE THAT IS NOT LEADING. Roy: *"if the new line is
        # internal to the paragraph then the two paragraphs + the newlines are in
        # fact one paragraph."* Only CODE ends a run, so these are one comment.
        page = built("x.c", "int a;\n\n/* one */\n\n/* two */\n\nint b;\n")
        self.assertEqual(owner(page, 3), owner(page, 5))
        self.assertEqual(owner(page, 4), owner(page, 3))

    def test_EVERY_paragraph_is_contiguous(self):
        # !! THE PROPERTY THAT MAKES THE STRADDLE IMPOSSIBLE. A place holding
        # lines 2 and 4 but not 3 cannot be emitted as one block, and a folio is
        # one entry in the reading order.
        text = (
            "# licence\n\n'''Doc.'''\n\nimport os\n"
            "\n\ndef f():\n    '''D.'''\n\n    return 1\n"
        )
        for b in built("m.py", text):
            if not b.original_start:
                continue
            with self.subTest(place=b.address):
                span = b.original_end - b.original_start + 1
                self.assertEqual(len(b.raw_lines), span, b.address)


class TestLeadingIsNotCitable(unittest.TestCase):
    """Roy: *"there is no information to rule on. It is just there for document
    preservation."*"""

    SRC = "# licence\n\n'''Doc.'''\n\nimport os\n"

    def test_it_carries_no_anchor(self):
        # ! Every other series answers to a line of code. This answers to nothing.
        leads = [b for b in built("m.py", self.SRC) if b.kind == lexer.LEADING]
        self.assertTrue(leads)
        self.assertEqual([b.anchor for b in leads], [""] * len(leads))

    def test_it_is_not_prose_a_reviewer_owes_a_record_on(self):
        page = built("m.py", self.SRC)
        self.assertNotIn(lexer.LEADING, {b.kind for b in page.prose})

    def test_NO_EMPTY_d_IS_EMITTED(self):
        # !! THE OTHER FOUR SERIES EXIST WHEREVER PROSE COULD GO, because an
        # `add` cites them. A place no verdict can name has no reason to exist
        # unfilled -- so a `d` exists only where the lexer found a blank run.
        page = built("m.py", "import os\nimport sys\n")
        self.assertEqual([b for b in page if b.kind == lexer.LEADING], [])


class TestTheShapeThatCouldNotBeSetBack(unittest.TestCase):
    """A licence, a blank, a docstring, a blank, the first import."""

    SRC = '# Copyright 2001.\n\n"""What this is."""\n\nimport os\n'

    def test_it_sets_back(self):
        self.assertEqual(compositor.set_page(built("m.py", self.SRC)), self.SRC)

    def test_the_blanks_belong_to_d_and_not_to_the_b(self):
        page = built("m.py", self.SRC)
        self.assertTrue(owner(page, 2).startswith("d"), owner(page, 2))
        self.assertTrue(owner(page, 4).startswith("d"), owner(page, 4))

    def test_the_reading_order_puts_them_where_they_sit(self):
        # ! `f0` the licence, `d0` the blank, `a0` the docstring, `d1` the blank,
        # `c0` the import -- which is the file, top to bottom.
        self.assertEqual(
            built("m.py", self.SRC).foliation.reading,
            ["f0", "d0", "a0", "d1", "c0"],
        )

    def test_a_doc_comment_one_blank_above_its_declaration_is_STILL_tied(self):
        # !! LEADING MUST NOT BREAK THE TIE. The walk up from a declaring line
        # skips blanks, and once those blanks were paragraphs it stopped at the
        # blank and tied THAT -- so the 38% of CPython declarations documented
        # across a blank line lost their `a`.
        text = "package thing\n\n// One does it.\n\nfunc One() {}\n"
        self.assertEqual(owner(built("g.go", text), 3), "a1")
