"""A language that attaches docs by POSITION declares the gap, never guesses."""

import unittest  # noqa: I001  -- path shim must import first

from _paths import FIXTURES
import page


def blocks_for(name):
    path = FIXTURES / name
    text = path.read_text(encoding="utf-8")
    return page.page_for(path, text, page.language_for(path))


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
