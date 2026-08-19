"""The census finds every block, at the tier its language reaches."""

import subprocess  # noqa: I001  -- path shim below must import before census
import sys
import tempfile
import unittest
from pathlib import Path

from _paths import FIXTURES, SCRIPTS
import census
import pcst
import prove_unchanged as pu


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
        # !! Two counts, and they measure different things. `raw_lines` is
        # every line the block SPANS -- four here, the interior blank
        # included, because the block runs from its first `#` to its last and
        # only CODE ends a run. `lines` is what the CAP charges: three comment
        # lines, of which the TODO is free.
        #
        # ! `raw_lines` used to come from the comment TOKENS, so the blank was
        # missing and the list was shorter than the span. Anything comparing
        # the two disagreed on a file nobody had touched.
        run = [b for b in blocks_for("sample.py") if b.kind == "comment"][0]
        self.assertEqual(len(run.raw_lines), 4)
        self.assertEqual(len(run.raw_lines), run.end - run.start + 1)
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
        # ! The module's own `a0` is here too -- a file with no module docstring
        # still has the PLACE for one. Neither kind holds prose.
        self.assertTrue(all(b.kind in pcst.HOLDS_NO_PROSE for b in got), got)
        self.assertEqual(sum(1 for b in got if b.kind == "interval"), 4, got)

    def test_the_file_boundary_bounds_the_first_and_last_interval(self):
        # !! THE EDIT RANGE CARRIES THE BOUNDARY, not the addressing one. These
        # gaps sit between adjacent code lines, so none holds a line of its own
        # and all are addressed at 0 -- the bounding lines belong to the `c`
        # series. `1-0` is the gap ABOVE line 1 and `4-3` the gap below line 3,
        # each an empty slice, so each is a pure insertion on its own side.
        got = [b for b in self._census("a = 1\nb = 2\nc = 3\n") if b.kind == "interval"]
        self.assertEqual((got[0].edit_start, got[0].edit_end), (1, 0))
        self.assertEqual((got[-1].edit_start, got[-1].edit_end), (4, 3))

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
            # ! An ABSENT docstring is at line 0 -- it occupies no line, because
            # the prose is not written yet. Every block that DOES occupy lines
            # must name real ones.
            # ! A place with NO LINES OF ITS OWN is at line 0 -- an absent
            # docstring, and a gap between two adjacent code lines. Its EDIT
            # range still says where prose would go. Every block that does
            # occupy lines must name real ones.
            if (b.start, b.end) == (0, 0):
                self.assertIn(b.kind, ("undocumented", "interval"), b)
                continue
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
        prose = [b for b in got if b.kind not in pcst.HOLDS_NO_PROSE]
        self.assertEqual([b.kind for b in prose], ["trailing-comment", "comment"])
        self.assertIn("continues-a-trailing-comment", prose[1].annotations)
        self.assertIn("trailing comment", " ".join(prose[1].notes))

    def test_an_ordinary_comment_after_CODE_is_not_stamped(self):
        got = self._census("x = 1\n# a fresh note\ny = 2\n")
        prose = [b for b in got if b.kind not in pcst.HOLDS_NO_PROSE]
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

    ! Measured before it was fixed: `blocks_lexical` flushes on a trailing
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
        prose = [b for b in got if b.kind not in pcst.HOLDS_NO_PROSE]
        self.assertEqual([b.kind for b in prose], ["trailing-comment", "comment"])
        self.assertIn("continues-a-trailing-comment", prose[1].annotations)

    def test_go_does_not_stamp_an_ordinary_comment(self):
        got = self._census("a.go", "x := 1\n// a fresh note\ny := 2\n")
        prose = [b for b in got if b.kind not in pcst.HOLDS_NO_PROSE]
        self.assertNotIn("continues-a-trailing-comment", prose[0].annotations)


# !! LAST LINE, ALWAYS. A runner placed above a class runs before that
# class exists, so `python tests/<file>.py` reported a green bar over a
# SHORTER suite than `unittest discover` -- and the tests it skipped were
# the ones someone running a single file was iterating on. Measured
# 2026-08-17: 26 direct against 28 discovered here, 9 against 11 in
# test_vocabulary.py.
class TestABlockCommentBesideCode(unittest.TestCase):
    """Four shapes, and each one was wrong in a different way.

    !! The rule: everything from the opener onward is comment, EXCEPT when the
    comment closes on the same line with code after it. That one line cannot be
    split into code and prose without losing half of it, so the census keeps it
    whole and `prove_unchanged` refuses the file -- the safe answer for a proof.
    """

    def _read(self, body):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "x.c"
            p.write_text(body, encoding="utf-8")
            blocks = census.blocks_lexical(p, body, census.language_for(p))
            prose = [b for b in blocks if b.text.strip()]
            return prose, sorted(census.code_lines(body, blocks))

    def test_a_comment_to_END_OF_LINE_leaves_its_statement_as_code(self):
        prose, code = self._read("int a = 1;\nint b = 2; /* note */\nint c = 3;\n")
        self.assertEqual(code, [1, 2, 3])
        self.assertEqual(prose[0].kind, "trailing-comment")
        self.assertNotIn("int b", prose[0].text)

    def test_a_MULTILINE_comment_after_code_leaves_its_statement_as_code(self):
        # ! The residual case. The block spans from the line holding the
        # statement, and taking that whole span dropped the statement from the
        # code set -- moving every interval boundary below it -- while its text
        # read `int b = 2; /* opens ...`, the statement handed over as prose.
        prose, code = self._read(
            "int a = 1;\nint b = 2; /* opens\n   and closes */\nint c = 3;\n"
        )
        self.assertEqual(code, [1, 2, 4])
        self.assertEqual((prose[0].start, prose[0].end), (2, 3))
        self.assertNotIn("int b", prose[0].text)

    def test_a_comment_on_its_own_lines_occupies_them(self):
        prose, code = self._read("int a = 1;\n/* opens\n   closes */\nint b = 2;\n")
        self.assertEqual(code, [1, 4])
        self.assertNotIn("int", prose[0].text)

    def test_an_intermediate_comment_is_NOT_CENSUSED(self):
        """!! `int x = /* why */ 5;` is ignored, and the line stays code.

        Roy ruled it 2026-08-19, on the same grounds as a Python type
        annotation: *"they are not comments that can be systemically and
        completely verified across code bases or written consistently on the
        same file because of line length rules ... all intermediate comments
        are ignored. They can be brought up by the agents as code change
        suggestions."*

        ! It WAS censused, and the block's text was the whole statement --
        measured 2026-08-19, `f.c@c1 comment text='int x = /* why */ 5;'`,
        executable code handed to four reviewers as prose. Cutting at the
        opener was the alternative and loses the trailing `5;`, so `5` and `7`
        would compare EQUAL and the proof report PROVEN on changed code.
        """
        prose, code = self._read("int x = /* why */ 5;\nint y = 6;\n")
        self.assertEqual(prose, [])
        # ! The line is code, so it keeps its `b` and its `c` like any other.
        self.assertEqual(code, [1, 2])


class TestTheProofFollowsTheBlocks(unittest.TestCase):
    """`prove_unchanged` must agree with the census about what is code."""

    C = "int a = 1;\nint b = 2; /* opens\n   and closes */\nint c = 3;\n"

    def test_the_statement_survives_into_the_fingerprint(self):
        _, code = pu.code_fingerprint(self.C, Path("x.c"))
        self.assertIn("int b = 2;", code)

    def test_a_code_change_on_that_line_is_caught(self):
        changed = self.C.replace("int b = 2;", "int b = 9;")
        self.assertNotEqual(
            pu.code_fingerprint(self.C, Path("x.c")),
            pu.code_fingerprint(changed, Path("x.c")),
        )

    def test_a_prose_only_edit_on_that_line_proves_identical(self):
        reworded = self.C.replace("opens", "OPENS").replace("closes", "CLOSES")
        self.assertEqual(
            pu.code_fingerprint(self.C, Path("x.c")),
            pu.code_fingerprint(reworded, Path("x.c")),
        )


class TestNoIntervalOverlapsProse(unittest.TestCase):
    """An `interval` is a gap that holds NO prose. It may not overlap a block.

    !! `code_lines` discards a block's first line when code precedes the
    opener, and a structural docstring's `raw_lines` are the AST VALUE, not the
    file's lines -- so one opening on its quote line looked exactly like a
    suffix and its first line was classified as CODE. Measured on `repo.py`:
    eight spurious intervals overlapping real docstrings, in the artefact four
    reviewers are bound by and the one an `add` cites to place missing prose.
    """

    def _overlaps(self, path):
        # ! `trailing-comment` is excluded, and that is not a loophole: it sits
        # ON a code line by definition, so an interval bounded by that line
        # touches it every time. `code_lines` documents the same pass-through.
        # Only a block that OCCUPIES its lines may not overlap a gap.
        text = path.read_text(encoding="utf-8")
        blocks = census.census_for(path, text, census.language_for(path))
        occupying = [
            b for b in blocks if b.text.strip() and b.kind != "trailing-comment"
        ]
        gaps = [b for b in blocks if b.kind == "interval"]
        return [
            (g.start, g.end, b.kind, b.start, b.end)
            for g in gaps
            for b in occupying
            if not (g.end < b.start or g.start > b.end)
        ]

    def test_no_interval_overlaps_prose_anywhere_in_the_shipped_tree(self):
        files = subprocess.run(
            ["git", "ls-files", "plugins/**/*.py"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.split()
        self.assertGreater(len(files), 5, "the sample must be real")
        bad = [(f, o) for f in files if (o := self._overlaps(Path(f)))]
        self.assertEqual(bad, [], "an interval overlaps a block that holds prose")

    def test_a_RAW_docstring_is_not_read_as_code(self):
        # ! `r"""` survives quote-stripping as a bare `r`, which reads as code.
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "r.py"
            src = "\n".join(
                [
                    "def f():",
                    '    r"""Doc opens here.',
                    "",
                    "    More.",
                    '    """',
                    "",
                ]
            )
            p.write_text(src, encoding="utf-8")
            self.assertEqual(self._overlaps(p), [])

    def test_code_before_a_block_opener_IS_still_discarded(self):
        # ! The case the discard exists for must keep working.
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "x.c"
            body = "\n".join(
                [
                    "int a = 1;",
                    "int b = 2; /* opens",
                    "   and closes */",
                    "int c = 3;",
                    "",
                ]
            )
            p.write_text(body, encoding="utf-8")
            blocks = census.blocks_lexical(p, body, census.language_for(p))
            self.assertIn(2, census.code_lines(body, blocks))


if __name__ == "__main__":
    unittest.main()


class TestFrontMatterIsMarked(unittest.TestCase):
    """Prose above a module's own docstring -- a licence, a shebang, a coding line.

    !! IT IS FILTERED OUT OF WHAT A REVIEWER READS, and a verdict on it becomes
    a `query`. No role can settle it: a copyright line states no constraint the
    code could contradict, it documents no function, it is not the module
    announcing its subject, and where it sits is fixed by law or convention
    rather than by editorial judgement. Measured 2026-08-19 over 1,500 files in
    five corpora: 12 carried prose there, 10 of them the same Apache header in
    every file of the project.
    """

    def _census(self, text):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "a.py"
            path.write_text(text, encoding="utf-8")
            return census.census_for(path, text, census.language_for(path))

    def _marked(self, text):
        return [
            b.start for b in self._census(text) if census.FRONT_MATTER in b.annotations
        ]

    LICENCE = '# Copyright 2024\n# Apache 2.0\n\n"""What this is."""\n\nimport os\n'
    SHEBANG = '#!/usr/bin/env python3\n\n"""What this is."""\n\nimport os\n'
    ORDINARY = '"""What this is."""\n\n# about the import\nimport os\n'
    NO_DOCSTRING = "# about the import\nimport os\n"

    def test_a_licence_above_the_module_docstring_is_front_matter(self):
        self.assertEqual(self._marked(self.LICENCE), [1])

    def test_a_shebang_is_front_matter(self):
        self.assertEqual(self._marked(self.SHEBANG), [1])

    def test_a_comment_BELOW_the_module_docstring_is_not(self):
        # ! It sits with the code and is reviewed like any other comment.
        self.assertEqual(self._marked(self.ORDINARY), [])

    def test_a_leading_comment_with_NO_module_docstring_is_not(self):
        # !! DELIBERATELY NARROW. With no docstring above it, a leading comment
        # is about whatever follows -- claiming it as front matter would silence
        # a real comment on the first declaration.
        self.assertEqual(self._marked(self.NO_DOCSTRING), [])

    def test_it_is_dropped_from_the_FILTERED_listing(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "a.py"
            path.write_text(self.LICENCE, encoding="utf-8")
            out = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "census.py"),
                    "--repo",
                    tmp,
                    "--filtered",
                    str(path),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(out.returncode, 0, out.stderr[-300:])
            self.assertNotIn("Copyright", out.stdout)
            self.assertNotIn("front-matter", out.stdout)


class TestAPathThatCannotBeAddressedIsAGap(unittest.TestCase):
    """`:` joins an address's path segments, so a path may not hold one.

    !! IT IS NOT UNIVERSALLY ILLEGAL. Windows forbids it in a filename and so
    did classic Mac OS, which used it as the separator; POSIX forbids only `/`
    and NUL. So a Linux checkout CAN hold `a:b.py`, whose address would be the
    address of `a/b.py` -- the exact collision the separator was chosen to end.
    The census refuses such a file rather than addressing it.

    ! It is refused on the REPO-RELATIVE path. Every absolute Windows path holds
    a colon in its drive letter, so reading the absolute one refuses the tree.
    """

    def test_a_colon_in_the_path_is_reported_and_fatal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            try:
                (root / "a:b.py").write_text("x = 1\n", encoding="utf-8")
            except OSError:
                self.skipTest("this filesystem will not create the path")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "census.py"),
                    "--repo",
                    str(root),
                    str(root / "a:b.py"),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("may not hold", result.stdout)

    def test_a_windows_drive_letter_does_NOT_refuse_the_tree(self):
        # ! The regression this check nearly shipped with: `path.as_posix()` is
        # absolute, so on Windows EVERY file was refused for its `C:`.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "ok.py").write_text("# a note\nx = 1\n", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "census.py"),
                    "--repo",
                    str(root),
                    str(root / "ok.py"),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout)
