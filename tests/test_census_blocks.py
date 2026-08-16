"""The census finds every block, at the tier its language reaches."""

import unittest  # noqa: I001  -- path shim below must import before census
from pathlib import Path

from _paths import FIXTURES
import census


def blocks_for(name):
    """Census one fixture file by name."""
    path = FIXTURES / name
    text = path.read_text(encoding="utf-8")
    lang = census.language_for(path)
    return census.census_for(path, text, lang)


class TestPythonTier(unittest.TestCase):
    def test_reaches_the_tokenized_tier(self):
        lang = census.language_for(FIXTURES / "sample.py")
        self.assertEqual(census.tier_for(lang), "tokenized")

    def test_a_blank_line_does_not_end_a_run(self):
        runs = [b for b in blocks_for("sample.py") if b.kind == "comment"]
        self.assertEqual(len(runs), 1, [b.text for b in runs])

    def test_a_marker_line_is_free(self):
        # Three COMMENT tokens (the blank line yields NL, which is skipped and
        # never joins the run), of which the TODO line is not charged.
        run = [b for b in blocks_for("sample.py") if b.kind == "comment"][0]
        self.assertEqual(len(run.raw_lines), 3)
        self.assertEqual(run.lines, 2)

    def test_a_trailing_comment_is_its_own_block(self):
        trailing = [b for b in blocks_for("sample.py") if b.kind == "trailing-comment"]
        self.assertEqual(len(trailing), 1)
        self.assertNotIn("result", trailing[0].text)

    def test_docstrings_carry_an_owner(self):
        docs = {b.owner for b in blocks_for("sample.py") if b.kind == "docstring"}
        self.assertEqual(docs, {"<module>", "add"})


class TestLexicalTier(unittest.TestCase):
    def test_go_reaches_the_lexical_tier(self):
        lang = census.language_for(FIXTURES / "sample.go")
        self.assertEqual(census.tier_for(lang), "lexical")

    def test_a_string_holding_a_marker_is_not_prose(self):
        texts = " ".join(b.text for b in blocks_for("sample.go"))
        self.assertNotIn("example.com", texts)

    def test_rust_doc_comments_are_docstrings(self):
        kinds = {b.kind for b in blocks_for("sample.rs")}
        self.assertIn("docstring", kinds)

    def test_rust_strips_the_longest_opener_first(self):
        docs = [b for b in blocks_for("sample.rs") if b.kind == "docstring"]
        self.assertFalse(
            any(b.text.startswith("/") for b in docs), [b.text for b in docs]
        )

    def test_ruby_block_comment_is_one_block(self):
        blocks = blocks_for("sample.rb")
        begins = [b for b in blocks if "=begin" in "".join(b.raw_lines)]
        self.assertEqual(len(begins), 1)


class TestUnterminatedBlockComment(unittest.TestCase):
    """A runaway opener ate the rest of the file, and the census says so.

    C1: without the annotation, that run is indistinguishable from a long comment,
    and every line of code below the opener is censused as prose with nothing
    reporting the gap.
    """

    RUNAWAY = "func A() {}\n/* note\nfunc B() {}\n"

    def _blocks(self):
        path = Path("x.go")
        return census.blocks_lexical(path, self.RUNAWAY, census.language_for(path))

    def test_the_runaway_run_is_marked(self):
        found = set().union(*(b.annotations for b in self._blocks()))
        self.assertIn("unterminated-block-comment", found)

    def test_the_mark_carries_a_note_naming_the_delimiter(self):
        marked = [
            b for b in self._blocks() if "unterminated-block-comment" in b.annotations
        ]
        self.assertEqual(len(marked), 1)
        self.assertIn("UNTERMINATED", " ".join(marked[0].notes))

    def test_a_closed_block_comment_is_not_marked(self):
        path = Path("x.go")
        closed = "func A() {}\n/* note */\nfunc B() {}\n"
        blocks = census.blocks_lexical(path, closed, census.language_for(path))
        found = set().union(*(b.annotations for b in blocks))
        self.assertNotIn("unterminated-block-comment", found)


if __name__ == "__main__":
    unittest.main()
