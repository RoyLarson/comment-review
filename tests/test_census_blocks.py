"""The census finds every paragraph, at the tier its language reaches."""

import subprocess  # noqa: I001  -- path shim below must import before census
import sys
import tempfile
import unittest
from pathlib import Path

from _paths import FIXTURES, SCRIPTS
import annotate
import census
import galley
import lexer
import page
import prove_unchanged as pu


def blocks_for(name):
    """Census one fixture file by name."""
    path = FIXTURES / name
    text = path.read_text(encoding="utf-8")
    lang = lexer.language_for(path)
    return page.page_for(path, text, lang)


class TestPythonTier(unittest.TestCase):
    def test_reaches_the_tokenized_tier(self):
        lang = lexer.language_for(FIXTURES / "sample.py")
        self.assertEqual(lexer.tier_for(lang), "tokenized")

    def test_a_blank_line_does_not_end_a_run(self):
        runs = [b for b in blocks_for("sample.py") if b.kind == "comment"]
        self.assertEqual(len(runs), 1, [b.text for b in runs])

    def test_a_marker_line_is_free(self):
        # !! Two counts, and they measure different things. `raw_lines` is
        # every line the paragraph SPANS -- four here, the interior blank
        # included, because the paragraph runs from its first `#` to its last and
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
        # ! The LINE that declares it, not the name -- ruled 2026-08-19. The
        # module is the one address with no line of code and keeps `<module>`.
        docs = {b.anchor for b in blocks_for("sample.py") if b.kind == "docstring"}
        self.assertEqual(docs, {"<module>", "def add(a, b):"})


class TestLexicalTier(unittest.TestCase):
    def test_go_reaches_the_lexical_tier(self):
        lang = lexer.language_for(FIXTURES / "sample.go")
        self.assertEqual(lexer.tier_for(lang), "lexical")

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
        paragraphs = blocks_for("sample.rb")
        begins = [b for b in paragraphs if "=begin" in "".join(b.raw_lines)]
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
        return lexer.paragraphs_lexical(path, self.RUNAWAY, lexer.language_for(path))

    def test_the_runaway_run_is_marked(self):
        found = set().union(*(b.annotations for b in self._blocks()))
        self.assertIn("unterminated-paragraph-comment", found)

    def test_the_mark_carries_a_note_naming_the_delimiter(self):
        marked = [
            b
            for b in self._blocks()
            if "unterminated-paragraph-comment" in b.annotations
        ]
        self.assertEqual(len(marked), 1)
        self.assertIn("UNTERMINATED", " ".join(marked[0].notes))

    def test_a_closed_block_comment_is_not_marked(self):
        path = Path("x.go")
        closed = "func A() {}\n/* note */\nfunc B() {}\n"
        paragraphs = lexer.paragraphs_lexical(path, closed, lexer.language_for(path))
        found = set().union(*(b.annotations for b in paragraphs))
        self.assertNotIn("unterminated-paragraph-comment", found)


class TestEveryFileIsCensusedOrItErrors(unittest.TestCase):
    """A file handed in and not censused is paragraphs nobody will review.

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
        # "0 paragraphs" from a typo reads exactly like "0 paragraphs" from a clean
        # file.
        result = self._run("ok.py", "no-such-directory")
        self.assertEqual(result.returncode, 1)
        self.assertIn("matched no files", result.stdout)


class TestEveryIntervalIsABlock(unittest.TestCase):
    """A paragraph is the interval between two lines of code, empty ones included.

    The census enumerated from PROSE, so an interval with nothing in it had no
    index -- and an `add` says a constraint exists in code and NOWHERE in
    prose, which is a finding ABOUT an empty interval. It had to borrow a
    neighbour's index to be filed at all.
    """

    def _census(self, text):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "a.py"
            path.write_text(text, encoding="utf-8")
            lang = lexer.language_for(path)
            return page.page_for(path, text, lang)

    def test_three_adjacent_code_lines_are_no_longer_zero_blocks(self):
        # The measurement that raised this: three code lines with nothing
        # between them censused as 0 paragraphs and could not be cited.
        got = self._census("a = 1\nb = 2\nc = 3\n")
        self.assertTrue(got, "three code lines must enumerate as intervals")
        # ! The module's own `a0` is here too -- a file with no module docstring
        # still has the PLACE for one. Neither kind holds prose.
        self.assertTrue(all(b.kind in page.HOLDS_NO_PROSE for b in got), got)
        # ! FIVE: `b0` the file's own place, one gap above each of the three
        # code lines, and the gap after the last. It was four until `b0` stopped
        # depending on front matter already being there.
        self.assertEqual(sum(1 for b in got if b.kind == "interval"), 5, got)

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
            # the prose is not written yet. Every paragraph that DOES occupy lines
            # must name real ones.
            # ! A place with NO LINES OF ITS OWN is at line 0 -- an absent
            # docstring, and a gap between two adjacent code lines. Its EDIT
            # range still says where prose would go. Every paragraph that does
            # occupy lines must name real ones.
            if (b.start, b.end) == (0, 0):
                self.assertIn(b.kind, ("undocumented", "interval"), b)
                continue
            self.assertLessEqual(b.start, b.end, b)
            self.assertGreaterEqual(b.start, 1, b)
            self.assertLessEqual(b.end, last, b)

    def test_a_trailing_comments_line_is_still_a_line_of_code(self):
        got = self._census("a = 1  # note\nb = 2\n")
        self.assertEqual(page.code_lines("a = 1  # note\nb = 2\n", got), {1, 2})

    def test_a_file_the_parser_refused_is_not_enumerated(self):
        # An interval drawn over a file whose code lines were never established
        # would be invented, so the `unparsed` paragraph stands alone.
        got = self._census("a = = 1\n")
        self.assertEqual([b.kind for b in got], ["unparsed"])

    def test_a_wrapped_trailing_comment_stamps_its_continuation(self):
        # One sentence, two paragraphs: a trailing comment closes its run, so the
        # line beneath opens a new one and re-anchors to the NEXT declaration.
        # Correct by the paragraph definition and wrong about the prose, so the
        # census says so rather than re-cutting -- merging would renumber every
        # census and invalidate every measurement taken against one.
        got = self._census("x = 1  # a claim that\n       # wraps onto it\ny = 2\n")
        prose = [b for b in got if b.kind not in page.HOLDS_NO_PROSE]
        self.assertEqual([b.kind for b in prose], ["trailing-comment", "comment"])
        self.assertIn("continues-a-trailing-comment", prose[1].annotations)
        self.assertIn("trailing comment", " ".join(prose[1].notes))

    def test_an_ordinary_comment_after_CODE_is_not_stamped(self):
        got = self._census("x = 1\n# a fresh note\ny = 2\n")
        prose = [b for b in got if b.kind not in page.HOLDS_NO_PROSE]
        self.assertEqual([b.kind for b in prose], ["comment"])
        self.assertNotIn("continues-a-trailing-comment", prose[0].annotations)

    def test_a_blank_line_breaks_the_continuation(self):
        # A gap means the author started something new, not wrapped a sentence.
        got = self._census("x = 1  # a claim\n\n# unrelated\ny = 2\n")
        prose = [b for b in got if b.kind == "comment"]
        self.assertNotIn("continues-a-trailing-comment", prose[0].annotations)

    def test_a_file_of_only_prose_is_one_interval(self):
        got = self._census("# just a note\n")
        # ! `b0` is the file's own place and exists whether or not front
        # matter sits in it, so a file of one comment carries that too.
        self.assertEqual(sorted(b.kind for b in got), ["comment", "interval"])


class TestTheLexicalTierStampsToo(unittest.TestCase):
    """The wrapped trailing comment splits identically at BOTH tiers.

    ! Measured before it was fixed: `paragraphs_lexical` flushes on a trailing
    comment exactly as `paragraphs_stdlib` does, so the continuation became its own
    paragraph with no stamp. The stamp is what tells a reviewer that a mid-clause
    ending is the census's doing.
    """

    def _census(self, name, text):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / name
            path.write_text(text, encoding="utf-8")
            return page.page_for(path, text, lexer.language_for(path))

    def test_go_stamps_a_wrapped_trailing_comment(self):
        got = self._census(
            "a.go", "x := 1  // a claim that\n        // wraps onto it\ny := 2\n"
        )
        prose = [b for b in got if b.kind not in page.HOLDS_NO_PROSE]
        self.assertEqual([b.kind for b in prose], ["trailing-comment", "comment"])
        self.assertIn("continues-a-trailing-comment", prose[1].annotations)

    def test_go_does_not_stamp_an_ordinary_comment(self):
        got = self._census("a.go", "x := 1\n// a fresh note\ny := 2\n")
        prose = [b for b in got if b.kind not in page.HOLDS_NO_PROSE]
        self.assertNotIn("continues-a-trailing-comment", prose[0].annotations)


class TestACPlaceCarriesItsAnchor(unittest.TestCase):
    """The line of code a trailing comment sits beside, VERBATIM.

    !! AN ANCHOR IS THE LINE OF CODE, NOT A SYMBOL. Roy, 2026-08-19: *"the
    anchor isn't the technical symbols and their precise semantic meaning and
    code use. It is 'the line of code' -- the exact characters in that line of
    code."*

    !! SO IT NEEDS NO PARSER, NO LANGUAGE SERVER AND NO BUILD TOOL. Every tier
    finds where the comment opens in order to cut there, which means it already
    holds the characters before it. Roy: *"the lexer either knows what is before
    the trailing comment and can snag the whole string or it is broken."*

    ! It was EMPTY in both tiers until 2026-08-19, measured on the files below.
    `paragraphs_stdlib` kept the whole physical line in `raw_lines` and so checked
    both halves of a staleness comparison by accident; `paragraphs_lexical` cut at
    the opener and checked only the prose, so a fresh census read as stale.
    """

    C = "int a = 1;\nint b = 2; // note\nvoid f(void) { } // on a decl\n"
    PY = "a = 1\nb = 2  # note\ndef f():  # on a decl\n    pass\n"

    def _lexical(self):
        path = Path("x.c")
        return lexer.paragraphs_lexical(path, self.C, lexer.language_for(path))

    def _tokenized(self):
        return lexer.paragraphs_stdlib(Path("x.py"), self.PY)

    def test_the_lexical_tier_carries_it(self):
        got = [b.anchor for b in self._lexical() if b.kind == "trailing-comment"]
        self.assertEqual(got, ["int b = 2;", "void f(void) { }"])

    def test_the_tokenized_tier_carries_it(self):
        got = [b.anchor for b in self._tokenized() if b.kind == "trailing-comment"]
        self.assertEqual(got, ["b = 2", "def f():"])

    def test_it_is_EXACTLY_the_column_split(self):
        # !! The anchor and the column say the same thing about one line, and
        # they must not be able to disagree: the anchor IS `line[:column - 1]`.
        for paragraph in self._lexical() + self._tokenized():
            if not paragraph.edit_column:
                continue
            text = self.C if paragraph.path == "x.c" else self.PY
            line = text.splitlines()[paragraph.start - 1]
            with self.subTest(block=paragraph.text):
                self.assertEqual(line[: paragraph.edit_column - 1], paragraph.anchor)

    def test_a_block_owning_its_lines_has_no_code_anchor(self):
        # ! Its anchor is a DECLARATION, which naming needs structure the
        # lexical tier does not have. Nothing here invents one.
        text = "int a = 1;\n// a note\nint b = 2;\n"
        path = Path("x.c")
        paragraphs = lexer.paragraphs_lexical(path, text, lexer.language_for(path))
        note = next(b for b in paragraphs if b.kind == "comment")
        self.assertEqual(note.edit_column, 0)
        self.assertEqual(note.anchor, "")

    def test_a_margin_carries_the_WHOLE_line(self):
        # ! Because the whole line is code. A `margin` and the trailing comment
        # that would replace it are one place, so they agree on both facts.
        path = Path("x.py")
        paragraphs = page.page_for(path, self.PY, lexer.language_for(path))
        margins = {b.start: b.anchor for b in paragraphs if b.kind == "margin"}
        self.assertEqual(margins[1], "a = 1")
        self.assertEqual(margins[4], "    pass")

    def test_no_c_place_in_this_repos_own_scripts_lacks_one(self):
        # !! The measurement that showed the hole, run as a gate. Every paragraph
        # with a column has the characters that precede it.
        root = Path(__file__).resolve().parent.parent
        scripts = root / "plugins/comment-review/skills/comment-review/scripts"
        holes = 0
        seen = 0
        for src in sorted(scripts.glob("*.py")):
            body = src.read_text(encoding="utf-8")
            for b in lexer.paragraphs_stdlib(src, body):
                if not b.edit_column:
                    continue
                seen += 1
                if b.anchor != body.splitlines()[b.start - 1][: b.edit_column - 1]:
                    holes += 1
        self.assertGreater(seen, 0, "no c place in the shipped scripts to check")
        self.assertEqual(holes, 0)


class TestEveryAddressCarriesAnAnchor(unittest.TestCase):
    """`a`, `b` and `c` alike -- and one anchor serves several addresses.

    !! ROY, 2026-08-19: *"a, b, c are the address -- each has an anchor. An
    anchor can be tied to multiple addresses ... anchors have many, an address
    has one."* So `import os` is the anchor of the `b` above it AND of the `c`
    beside it, and the relationship is never symmetric.

    ! A `b` sits ABOVE code, so its anchor is the code line BELOW it. The gap at
    the END of a file has no line below and takes the one above, because a gap
    is bounded by code and that is the bound it has.
    """

    SRC = (
        "# a header note\n"
        "import os\n"
        "\n"
        "\n"
        "# what f is for\n"
        "def f():\n"
        '    """Doc."""\n'
        "    return os  # why\n"
    )

    def setUp(self):
        path = Path("x.py")
        self.paragraphs = page.page_for(path, self.SRC, lexer.language_for(path))

    def _one(self, kind, start=None):
        got = [
            b
            for b in self.paragraphs
            if b.kind == kind and (start is None or b.start == start)
        ]
        self.assertEqual(len(got), 1, f"{kind} at {start}: {len(got)} paragraphs")
        return got[0]

    def test_a_comment_run_is_anchored_to_the_code_BELOW_it(self):
        self.assertEqual(self._one("comment", 1).anchor, "import os")
        self.assertEqual(self._one("comment", 3).anchor, "def f():")

    def test_a_trailing_comment_is_anchored_to_its_OWN_line(self):
        self.assertEqual(self._one("trailing-comment").anchor, "    return os")

    def test_one_anchor_serves_the_b_AND_the_c_of_one_line(self):
        # !! The one-to-many relationship, measured on one line of code.
        b = self._one("comment", 1)
        c = self._one("margin", 2)
        self.assertEqual(b.anchor, c.anchor)
        # ! `page_for` does not stamp the address -- the run loop does, once
        # the path is repo-relative -- so the two places are told apart here by
        # the fact the addresser reads: a `c` has a column and a `b` has none.
        self.assertTrue(c.edit_column)
        self.assertFalse(b.edit_column)

    def test_the_b_and_the_c_of_a_line_AGREE_on_the_code(self):
        # !! They are two computations of one fact unless the `b` copies the
        # `c`. Re-cutting the line here answered `'    return os  # why'` where
        # the `c` for the same line answered `'    return os'`.
        margins = {b.start: b.anchor for b in self.paragraphs if b.edit_column}
        for paragraph in self.paragraphs:
            if paragraph.edit_column or paragraph.declares >= 0 or not paragraph.anchor:
                continue
            with self.subTest(address=paragraph.address):
                # ! `b0` is the FILE'S place. Its anchor is the module,
                # which has no line to sit beside and so no `c` to copy.
                if paragraph.address.endswith("@b0"):
                    continue
                self.assertIn(paragraph.anchor, margins.values())

    def test_NO_block_in_this_file_lacks_an_anchor(self):
        # ! Roy, 2026-08-19: "an anchor missing in a Record is a broken Record."
        self.assertEqual([b.kind for b in self.paragraphs if not b.anchor], [])

    def test_the_gap_at_the_END_takes_the_line_ABOVE_it(self):
        # ! It has no line below. Left empty this was 14 paragraphs of this repo,
        # one per file, every one a broken record.
        gaps = [b for b in self.paragraphs if b.kind == "interval"]
        last = max(gaps, key=lambda b: b.edit_start)
        self.assertEqual(last.anchor, "    return os")

    def test_no_block_in_this_repos_own_scripts_lacks_one(self):
        # !! The hole, run as a gate: 6,376 of 6,531 paragraphs carried an empty
        # anchor before 2026-08-19 -- 98% of this repo's own census.
        root = Path(__file__).resolve().parent.parent
        scripts = root / "plugins/comment-review/skills/comment-review/scripts"
        holes = []
        for src in sorted(scripts.glob("*.py")):
            body = src.read_text(encoding="utf-8")
            for b in page.page_for(src, body, lexer.language_for(src)):
                if not b.anchor:
                    holes.append(f"{src.name} {b.address or b.start} {b.kind}")
        self.assertEqual(holes, [])


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
            return page.page_for(path, text, lexer.language_for(path))

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


class TestBothTiersStoreRawLinesTheSameWay(unittest.TestCase):
    """`raw_lines` is the paragraph's OWN characters, and `anchor` is the code.

    !! THE TWO TIERS STORED DIFFERENT THINGS AND FOUR OF SIX SHAPES COULD NOT BE
    WRITTEN. `paragraphs_lexical` cut at the comment OPENER; `paragraphs_stdlib` kept
    the whole physical line. Measured 2026-08-19, on a FRESH census checked
    against the file it was built from:

    | shape                       | matched |
    | --------------------------- | ------- |
    | trailing `// note`          | NO -- the code was cut away |
    | trailing `/* note */`       | NO |
    | indented `    /* why */`    | NO -- the INDENTATION was cut away |
    | multiline indented `/* one` | NO |
    | indented `    // why`       | yes |
    | column-0 `/* why */`        | yes |

    ! So every paragraph comment not at column 0, and every trailing comment in the
    ten lexical languages, was refused by `galley.paragraph_matches` on a census
    seconds old -- which is what made the `c` series writable in Python only.
    """

    C = Path("x.c")
    SHAPES = {
        "trailing line": "int a = 1;\nint b = 2; // note\n",
        "trailing paragraph": "int a = 1;\nint b = 2; /* note */\n",
        "indented paragraph": "int a = 1;\nvoid f(void) {\n    /* why */\n}\n",
        "indented line": "int a = 1;\nvoid f(void) {\n    // why\n}\n",
        "column 0 paragraph": "/* why */\nint a = 1;\n",
        "multiline indented": "void f(void) {\n    /* one\n       two */\n}\n",
    }

    def _prose(self, text):
        lang = lexer.language_for(self.C)
        return [
            b
            for b in page.page_for(self.C, text, lang)
            if b.kind in ("comment", "trailing-comment")
        ]

    def test_a_FRESH_census_matches_every_shape(self):
        for label, text in self.SHAPES.items():
            lines = text.splitlines()
            for b in self._prose(text):
                with self.subTest(shape=label):
                    self.assertTrue(
                        galley.paragraph_matches(lines, vars(b)),
                        f"{b.raw_lines!r} against {lines[b.start - 1]!r}",
                    )

    def test_a_c_BLOCK_rebuilds_its_line_from_the_anchor_and_the_first_raw_line(
        self,
    ):
        # !! THE INVARIANT THE TWO FIELDS EXIST TO KEEP. Storing the whole line
        # in `raw_lines` would satisfy the staleness check and put the code in
        # two fields; cutting at the opener loses it from both.
        #
        # ! Only a `c` paragraph. A `b`'s anchor is a DIFFERENT line -- the code
        # BELOW the gap -- so it has nothing to rebuild its own line from, and
        # its `raw_lines` is that line whole.
        seen = 0
        for label, text in self.SHAPES.items():
            lines = text.splitlines()
            for b in self._prose(text):
                with self.subTest(shape=label):
                    if b.edit_column:
                        seen += 1
                        self.assertEqual(b.anchor + b.raw_lines[0], lines[b.start - 1])
                    else:
                        self.assertEqual(b.raw_lines[0], lines[b.start - 1])
        self.assertGreater(seen, 0, "no `c` paragraph among the shapes")

    def test_the_TOKENIZED_tier_keeps_the_same_invariant(self):
        text = "TIMEOUT = 30  # a note\n# on its own\nx = 1\n"
        path = Path("x.py")
        lines = text.splitlines()
        for b in page.page_for(path, text, lexer.language_for(path)):
            if b.kind not in ("comment", "trailing-comment"):
                continue
            with self.subTest(kind=b.kind, start=b.start):
                head = b.anchor if b.edit_column else ""
                self.assertEqual(head + b.raw_lines[0], lines[b.start - 1])
                self.assertTrue(galley.paragraph_matches(lines, vars(b)))

    def test_a_trailing_comments_CODE_no_longer_reaches_the_annotators(self):
        """!! `prose_numbers` reads `raw_lines`, so the whole physical line put
        a statement's own literals into the prose.

        Measured 2026-08-19: `TIMEOUT = 30  # the note says nothing` reported
        the number 30 as a claim the prose makes. It is the CODE. The lexical
        tier's own comment says this defect was fixed -- it was fixed on one
        tier, and `repeated-literal` counts across the whole census.
        """
        for path, text in (
            (Path("x.py"), "TIMEOUT = 30  # the note says nothing\n"),
            (Path("x.c"), "int timeout = 30; // the note says nothing\n"),
        ):
            lang = lexer.language_for(path)
            for b in page.page_for(path, text, lang):
                if b.kind != "trailing-comment":
                    continue
                with self.subTest(path=path.name):
                    self.assertNotIn("30", b.raw_lines[0])
                    self.assertEqual(annotate.prose_numbers(b.text, b.raw_lines), set())

    def test_a_margin_stores_the_ROOM_and_not_the_code(self):
        # ! The code is the ANCHOR. Storing it here too would put one fact in
        # two fields, which is what the anchor was added to end.
        text = "a = 1\n"
        path = Path("x.py")
        margin = next(
            b
            for b in page.page_for(path, text, lexer.language_for(path))
            if b.kind == "margin"
        )
        self.assertEqual(margin.anchor, "a = 1")
        self.assertEqual(margin.raw_lines, [""])
        self.assertTrue(galley.paragraph_matches(text.splitlines(), vars(margin)))

    def test_no_prose_block_in_the_fixtures_is_refused_by_a_FRESH_census(self):
        # !! The measurement, as a gate. It was 4 of 6 shapes and 1 of 8 fixture
        # paragraphs before 2026-08-19.
        refused = []
        for src in sorted(FIXTURES.rglob("*")):
            lang = lexer.language_for(src) if src.is_file() else None
            if lang is None:
                continue
            body = src.read_text(encoding="utf-8")
            try:
                paragraphs = page.page_for(src, body, lang)
            except Exception:
                continue
            lines = body.splitlines()
            refused += [
                f"{src.name}:{b.start} {b.kind}"
                for b in paragraphs
                if b.kind not in page.HOLDS_NO_PROSE
                and not galley.paragraph_matches(lines, vars(b))
            ]
        self.assertEqual(refused, [])


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
            paragraphs = lexer.paragraphs_lexical(p, body, lexer.language_for(p))
            prose = [b for b in paragraphs if b.text.strip()]
            return prose, sorted(page.code_lines(body, paragraphs))

    def test_a_comment_to_END_OF_LINE_leaves_its_statement_as_code(self):
        prose, code = self._read("int a = 1;\nint b = 2; /* note */\nint c = 3;\n")
        self.assertEqual(code, [1, 2, 3])
        self.assertEqual(prose[0].kind, "trailing-comment")
        self.assertNotIn("int b", prose[0].text)

    def test_a_MULTILINE_comment_after_code_leaves_its_statement_as_code(self):
        # ! The residual case. The paragraph spans from the line holding the
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

        ! It WAS censused, and the paragraph's text was the whole statement --
        measured 2026-08-19, `f.c@c2 comment text='int x = /* why */ 5;'`,
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
    """An `interval` is a gap that holds NO prose. It may not overlap a paragraph.

    !! `code_lines` discards a paragraph's first line when code precedes the
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
        # Only a paragraph that OCCUPIES its lines may not overlap a gap.
        text = path.read_text(encoding="utf-8")
        paragraphs = page.page_for(path, text, lexer.language_for(path))
        occupying = [
            b for b in paragraphs if b.text.strip() and b.kind != "trailing-comment"
        ]
        gaps = [b for b in paragraphs if b.kind == "interval"]
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
        self.assertEqual(bad, [], "an interval overlaps a paragraph that holds prose")

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
            paragraphs = lexer.paragraphs_lexical(p, body, lexer.language_for(p))
            self.assertIn(2, page.code_lines(body, paragraphs))
