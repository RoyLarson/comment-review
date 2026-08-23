"""A language that attaches docs by POSITION declares the gap, never guesses."""

import unittest  # noqa: I001  -- path shim must import first
from pathlib import Path

from _paths import FIXTURES
import lexer
import page


def blocks_for(name):
    path = FIXTURES / name
    text = path.read_text(encoding="utf-8")
    return page.page_for(path, text, lexer.language_for(path))


class TestStructuralDocGap(unittest.TestCase):
    def test_a_run_above_code_in_go_is_marked_unresolved(self):
        above_func = [b for b in blocks_for("sample.go") if "Add returns" in b.text]
        self.assertEqual(len(above_func), 1)
        self.assertIn("doc-kind-unresolved", above_func[0].annotations)

    def test_the_mark_carries_a_note_naming_the_consequence(self):
        paragraph = [b for b in blocks_for("sample.go") if "Add returns" in b.text][0]
        self.assertTrue(
            any("cap" in n.lower() for n in paragraph.notes), paragraph.notes
        )

    def test_an_orphan_run_followed_by_blank_lines_is_not_marked(self):
        orphan = [b for b in blocks_for("sample.go") if "orphan run" in b.text]
        self.assertEqual(len(orphan), 1)
        self.assertNotIn("doc-kind-unresolved", orphan[0].annotations)

    def test_a_lexical_trailing_comment_is_stamped(self):
        trailing = [b for b in blocks_for("sample.go") if "trailing comment" in b.text]
        self.assertEqual(len(trailing), 1)
        self.assertEqual(trailing[0].kind, "trailing-comment")

    def test_a_trailing_comment_is_never_a_structural_doc(self):
        trailing = [b for b in blocks_for("sample.go") if "trailing comment" in b.text]
        self.assertEqual(len(trailing), 1)
        self.assertNotIn("doc-kind-unresolved", trailing[0].annotations)

    def test_rust_is_untouched_because_it_marks_docs_lexically(self):
        for paragraph in blocks_for("sample.rs"):
            self.assertNotIn("doc-kind-unresolved", paragraph.annotations)

    def test_python_never_reaches_this_pass(self):
        for paragraph in blocks_for("sample.py"):
            self.assertNotIn("doc-kind-unresolved", paragraph.annotations)


def built(name: str, text: str):
    """A page for text that has no fixture of its own."""
    p = Path(name)
    return page.page_for(p, text, lexer.language_for(p))


def prose(pg):
    """`(address, kind)` for every paragraph holding prose."""
    return [(b.address.split("@")[-1], str(b.kind)) for b in pg if b.text.strip()]


class TestARuleIsNotADocComment(unittest.TestCase):
    """A banner made of the marker's own character opens nothing.

    !! IT WAS TYPED `docstring` AND COULD THEN DOCUMENT A DECLARATION.
    `/*******************/` starts with `/**`, and the test was `startswith` --
    so a RULE was routed by FORMAT where the question is what the run says.
    MEASURED 2026-08-22; the corpora hold 135 runs of that shape.

    ! The test is the character AFTER the marker, which is the rule Javadoc and
    Doxygen use themselves, and it holds for `doc_line` unchanged.
    """

    def test_a_rule_of_stars_is_not_a_docstring(self):
        got = prose(built("a.c", "/*******************/\nint x = 1;\n"))
        self.assertNotIn("docstring", [kind for _, kind in got])

    def test_a_real_doc_block_still_is_one(self):
        got = prose(built("b.c", "/** Adds one. */\nint x = 1;\n"))
        self.assertIn("docstring", [kind for _, kind in got])

    def test_a_rule_of_slashes_is_not_a_rust_doc_line(self):
        got = prose(built("c.rs", "////////////////\npub fn f() {}\n"))
        self.assertNotIn("docstring", [kind for _, kind in got])

    def test_a_real_rust_doc_line_still_is_one(self):
        got = prose(built("d.rs", "/// Adds one.\npub fn f() {}\n"))
        self.assertIn("docstring", [kind for _, kind in got])


class TestATrailingCommentSurvivesAnIntermediateOne(unittest.TestCase):
    """`int x = /* why */ 5; // note` keeps the `// note`.

    !! IT LOST IT ENTIRELY. The intermediate-comment branch returned as soon as
    it saw code after the closer, so the `c` place survived as an empty `margin`
    and a real comment reached no reviewer. MEASURED 2026-08-22 against the same
    line without the intermediate comment, where `c1` reads `note`.

    ! The ruling ignores the INTERMEDIATE comment -- Roy, 2026-08-19: *"all
    intermediate comments are ignored"* -- and says the line is then simply
    code. A code line carrying a trailing comment is the ordinary case.
    """

    def _c1(self, text: str):
        held = [b for b in built("m.c", text) if b.address.endswith("c1")]
        self.assertEqual(len(held), 1, text)
        return held[0]

    def test_the_trailing_comment_survives(self):
        got = self._c1("int y = 0;\nint x = /* why */ 5; // note\nint z = 1;\n")
        self.assertEqual(str(got.kind), "trailing-comment")
        self.assertEqual(got.text, "note")

    def test_the_same_line_without_the_intermediate_one_is_unchanged(self):
        got = self._c1("int y = 0;\nint x = 5; // note\nint z = 1;\n")
        self.assertEqual(str(got.kind), "trailing-comment")
        self.assertEqual(got.text, "note")

    def test_an_intermediate_comment_ALONE_still_yields_no_prose(self):
        # ! The ruling itself: nothing is censused for the intermediate comment.
        got = self._c1("int y = 0;\nint x = /* why */ 5;\nint z = 1;\n")
        self.assertEqual(str(got.kind), "margin")
        self.assertEqual(got.text, "")
