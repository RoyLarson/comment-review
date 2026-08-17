"""The census finds every block, at the tier its language reaches."""

import subprocess  # noqa: I001  -- path shim below must import before census
import sys
import tempfile
import unittest
from pathlib import Path

from _paths import FIXTURES, SCRIPTS
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

    def test_docstrings_carry_an_anchor(self):
        docs = {b.anchor for b in blocks_for("sample.py") if b.kind == "docstring"}
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


class TestEveryFileIsCensusedOrItErrors(unittest.TestCase):
    """A file handed in and not censused is blocks nobody will review.

    The reviewers are handed the CENSUS, not the file list, so a gap here is
    invisible downstream -- it reads as a smaller repo. The run stops instead.
    """

    def _run(self, *names):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "ok.py").write_text("# a note\nx = 1\n", encoding="utf-8")
            (root / "weird.zzz").write_text("x\n", encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(SCRIPTS / "census.py"), "--repo", str(root)]
                + [str(root / n) for n in names],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )

    def test_a_file_with_no_language_record_is_fatal(self):
        result = self._run("ok.py", "weird.zzz")
        self.assertEqual(result.returncode, 1)
        self.assertIn("were not", result.stdout)
        self.assertIn("weird.zzz", result.stdout)

    def test_a_censusable_file_alone_exits_zero(self):
        result = self._run("ok.py")
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_an_argument_matching_nothing_is_fatal(self):
        # "0 blocks" from a typo reads exactly like "0 blocks" from a clean file.
        result = self._run("ok.py", "no-such-directory")
        self.assertEqual(result.returncode, 1)
        self.assertIn("matched no files", result.stdout)


class TestEveryIntervalIsABlock(unittest.TestCase):
    """A block is the interval between two lines of code, empty ones included.

    The census enumerated from PROSE, so an interval with nothing in it had no
    index -- and an `add` says a constraint exists in code and NOWHERE in
    prose, which is a finding ABOUT an empty interval. It had to borrow a
    neighbour's index to be filed at all.
    """

    def _census(self, text):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "a.py"
            path.write_text(text, encoding="utf-8")
            lang = census.language_for(path)
            return census.census_for(path, text, lang)

    def test_three_adjacent_code_lines_are_no_longer_zero_blocks(self):
        # The measurement that raised this: three code lines with nothing
        # between them censused as 0 blocks and could not be cited.
        got = self._census("a = 1\nb = 2\nc = 3\n")
        self.assertTrue(got, "three code lines must enumerate as intervals")
        self.assertTrue(all(b.kind == "interval" for b in got), got)

    def test_the_file_boundary_bounds_the_first_and_last_interval(self):
        got = self._census("a = 1\nb = 2\nc = 3\n")
        self.assertEqual((got[0].start, got[0].end), (1, 1))
        self.assertEqual((got[-1].start, got[-1].end), (3, 3))

    def test_an_interval_holding_prose_is_not_enumerated_twice(self):
        got = self._census("a = 1\n# a note\nb = 2\n")
        kinds = [b.kind for b in got]
        self.assertEqual(kinds.count("comment"), 1, got)
        # Two code lines, one gap between them, and the gap holds the comment.
        self.assertNotIn(
            (2, 2), [(b.start, b.end) for b in got if b.kind == "interval"]
        )

    def test_every_interval_citation_resolves_to_a_real_line(self):
        text = "a = 1\n\n\nb = 2\nc = 3\n"
        last = len(text.splitlines())
        for b in self._census(text):
            self.assertLessEqual(b.start, b.end, b)
            self.assertGreaterEqual(b.start, 1, b)
            self.assertLessEqual(b.end, last, b)

    def test_a_trailing_comments_line_is_still_a_line_of_code(self):
        got = self._census("a = 1  # note\nb = 2\n")
        self.assertEqual(census.code_lines("a = 1  # note\nb = 2\n", got), {1, 2})

    def test_a_file_the_parser_refused_is_not_enumerated(self):
        # An interval drawn over a file whose code lines were never established
        # would be invented, so the `unparsed` block stands alone.
        got = self._census("a = = 1\n")
        self.assertEqual([b.kind for b in got], ["unparsed"])

    def test_a_wrapped_trailing_comment_stamps_its_continuation(self):
        # One sentence, two blocks: a trailing comment closes its run, so the
        # line beneath opens a new one and re-anchors to the NEXT declaration.
        # Correct by the block definition and wrong about the prose, so the
        # census says so rather than re-cutting -- merging would renumber every
        # census and invalidate every measurement taken against one.
        got = self._census("x = 1  # a claim that\n       # wraps onto it\ny = 2\n")
        prose = [b for b in got if b.kind != "interval"]
        self.assertEqual([b.kind for b in prose], ["trailing-comment", "comment"])
        self.assertIn("continues-a-trailing-comment", prose[1].annotations)
        self.assertIn("trailing comment", " ".join(prose[1].notes))

    def test_an_ordinary_comment_after_CODE_is_not_stamped(self):
        got = self._census("x = 1\n# a fresh note\ny = 2\n")
        prose = [b for b in got if b.kind != "interval"]
        self.assertEqual([b.kind for b in prose], ["comment"])
        self.assertNotIn("continues-a-trailing-comment", prose[0].annotations)

    def test_a_blank_line_breaks_the_continuation(self):
        # A gap means the author started something new, not wrapped a sentence.
        got = self._census("x = 1  # a claim\n\n# unrelated\ny = 2\n")
        prose = [b for b in got if b.kind == "comment"]
        self.assertNotIn("continues-a-trailing-comment", prose[0].annotations)

    def test_a_file_of_only_prose_is_one_interval(self):
        got = self._census("# just a note\n")
        self.assertEqual([b.kind for b in got], ["comment"])


class TestTheLexicalTierStampsToo(unittest.TestCase):
    """The wrapped trailing comment splits identically at BOTH tiers.

    ⚠ Measured before it was fixed: `blocks_lexical` flushes on a trailing
    comment exactly as `blocks_stdlib` does, so the continuation became its own
    block with no stamp. The stamp is what tells a reviewer that a mid-clause
    ending is the census's doing.
    """

    def _census(self, name, text):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / name
            path.write_text(text, encoding="utf-8")
            return census.census_for(path, text, census.language_for(path))

    def test_go_stamps_a_wrapped_trailing_comment(self):
        got = self._census(
            "a.go", "x := 1  // a claim that\n        // wraps onto it\ny := 2\n"
        )
        prose = [b for b in got if b.kind != "interval"]
        self.assertEqual([b.kind for b in prose], ["trailing-comment", "comment"])
        self.assertIn("continues-a-trailing-comment", prose[1].annotations)

    def test_go_does_not_stamp_an_ordinary_comment(self):
        got = self._census("a.go", "x := 1\n// a fresh note\ny := 2\n")
        prose = [b for b in got if b.kind != "interval"]
        self.assertNotIn("continues-a-trailing-comment", prose[0].annotations)


# ⚠⚠ LAST LINE, ALWAYS. A runner placed above a class runs before that
# class exists, so `python tests/<file>.py` reported a green bar over a
# SHORTER suite than `unittest discover` — and the tests it skipped were
# the ones someone running a single file was iterating on. Measured
# 2026-08-17: 26 direct against 28 discovered here, 9 against 11 in
# test_vocabulary.py.
if __name__ == "__main__":
    unittest.main()
