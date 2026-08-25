"""The census finds every paragraph, at the tier its language reaches."""

import json
import subprocess  # noqa: I001  -- path shim below must import before census
import tempfile
import unittest
from pathlib import Path

# ! `_paths` FIRST: importing it is what puts `src/` on the path.
from _paths import FIXTURES, PKG, ROOT, cli
from _transcription import transcribes

from comment_review.binder import annotate, page
from comment_review.reading import lexer
from comment_review.reading.addresser import COVERS, EOF
from comment_review.results import prove_unchanged as pu


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


class TestADelimiterIsNotAParagraphBoundary(unittest.TestCase):
    """Only CODE ends a paragraph -- opening or closing `/* */` does not.

    !! THE WHOLE OF `two-paragraphs-one-address` OUTSIDE PYTHON, fixed
    2026-08-21. The lexer flushed the run in progress whenever a delimited
    comment OPENED, and again whenever one CLOSED. A line comment raises neither
    event, so its run stayed open and a blank line bridged it -- and the same
    prose in the same gap became one paragraph or several depending only on
    which comment syntax the author reached for.

    ! MEASURED over 699 files in ten languages: 157 shared addresses before, 0
    after. `cpython/Include/abstract.h` held SEVENTEEN runs between `#endif` and
    the next `#if` -- 178 lines with no code in them, so one gap, so one address
    for all seventeen.
    """

    def _runs(self, name, text):
        path = Path(name)
        got = lexer.paragraphs_lexical(path, text, lexer.language_for(path))
        return [(b.start, b.end, b.kind, b.original_column) for b in got]

    def test_two_delimited_comments_across_a_blank_are_ONE_paragraph(self):
        got = self._runs("x.c", "int a;\n\n/* one */\n\n/* two */\n\nint b;\n")
        self.assertEqual(got, [(3, 5, "comment", 0)])

    def test_which_is_what_LINE_comments_already_did(self):
        # ! The point is that these two agree. Neither answer is new; they
        # disagreed, and a gap cannot hold two paragraphs at one address.
        got = self._runs("x.c", "int a;\n\n// one\n\n// two\n\nint b;\n")
        self.assertEqual(got, [(3, 5, "comment", 0)])

    def test_the_two_SYNTAXES_MIX_in_one_paragraph(self):
        got = self._runs("x.c", "int a;\n\n/* one */\n\n// two\n\nint b;\n")
        self.assertEqual(got, [(3, 5, "comment", 0)])

    def test_a_multi_line_delimited_comment_joins_the_next_one_too(self):
        got = self._runs("x.c", "int a;\n\n/* one\n   more */\n\n/* two */\n\nint b;\n")
        self.assertEqual(got, [(3, 6, "comment", 0)])

    def test_a_TRAILING_delimited_comment_still_ends_its_run(self):
        # ! Code BEFORE the opener makes it a `c` -- the room beside one line --
        # and it must not absorb the prose beneath it.
        got = self._runs("x.c", "int a; /* beside */\n\n/* below */\n\nint b;\n")
        self.assertEqual(got, [(1, 1, "trailing-comment", 7), (3, 3, "comment", 0)])

    def test_CODE_still_ends_a_run(self):
        got = self._runs("x.c", "/* one */\nint a;\n/* two */\nint b;\n")
        # ! A run on LINE 1 is the file's own MATTER since 2026-08-21 -- Roy:
        # *"if the opening/closing line is a comment then the matter continues
        # down/up."* The lexer types it, so the kind says so here.
        self.assertEqual(got, [(1, 1, "matter", 0), (3, 3, "comment", 0)])

    def test_only_the_FIRST_run_splits_at_the_head_of_a_file(self):
        # !! THREE runs before any code, measured on
        # `meta-package-manager/tests/cli-test-plan.toml`. The head rule split at
        # every blank, so the second and third both took `b0`. Only the first is
        # the file's own matter; the rest are ordinary prose in the gap above the
        # first statement and merge there.
        got = self._runs("x.c", "/* head */\n\n/* one */\n\n/* two */\nint a;\n")
        # ! A run on LINE 1 is the file's own MATTER since 2026-08-21 -- Roy:
        # *"if the opening/closing line is a comment then the matter continues
        # down/up."* The lexer types it, so the kind says so here.
        self.assertEqual(got, [(1, 1, "matter", 0), (3, 5, "comment", 0)])


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
                [*cli("census"), "--repo", str(root)]
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
        self.assertTrue(all(lexer.Kind.holds_no_prose(b.kind) for b in got), got)
        # ! FOUR INTERVALS: one gap above each of the three code lines, and the
        # gap after the last. ! The file's own places are NOT among them since
        # 2026-08-20 -- they are `dark-matter`, in their own series.
        self.assertEqual(sum(1 for b in got if b.kind == "interval"), 4, got)
        # ! TWO of them since 2026-08-21: `f0` at the head of the file and `f1`
        # at its foot. A file with no matter at either end still has both
        # places, exactly as it has an `a0` with no module docstring in it.
        self.assertEqual(sum(1 for b in got if b.kind == "dark-matter"), 2, got)

    def test_a_gap_between_adjacent_code_lines_holds_NO_line(self):
        # !! None, NOT AN EMPTY RANGE. Roy, 2026-08-20: the original lines are
        # a closed list `[1..7]`, *"or it is None, meaning there are currently
        # no lines that have that cues."* These gaps sit between adjacent
        # code lines, so none holds a line of its own -- the bounding lines
        # belong to the `c` series. `(1, 0)` and `(4, 3)` said the same thing
        # in a form that reads as a range and invites arithmetic on it.
        got = [b for b in self._census("a = 1\nb = 2\nc = 3\n") if b.kind == "interval"]
        self.assertTrue(got)
        for b in got:
            with self.subTest(address=b.address):
                self.assertIsNone(b.original_start)
                self.assertIsNone(b.original_end)

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
                self.assertIn(b.kind, ("undocumented", "interval", "dark-matter"), b)
                continue
            self.assertLessEqual(b.start, b.end, b)
            self.assertGreaterEqual(b.start, 1, b)
            self.assertLessEqual(b.end, last, b)

    def test_a_trailing_comments_line_is_still_a_line_of_code(self):
        got = self._census("a = 1  # note\nb = 2\n")
        self.assertEqual(
            page.code_lines("a = 1  # note\nb = 2\n", [vars(b) for b in got]),
            {1: "a = 1", 2: "b = 2"},
        )

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
        prose = [b for b in got if not lexer.Kind.holds_no_prose(b.kind)]
        self.assertEqual([b.kind for b in prose], ["trailing-comment", "comment"])
        self.assertIn("continues-a-trailing-comment", prose[1].annotations)
        self.assertIn("trailing comment", " ".join(prose[1].notes))

    def test_an_ordinary_comment_after_CODE_is_not_stamped(self):
        got = self._census("x = 1\n# a fresh note\ny = 2\n")
        prose = [b for b in got if not lexer.Kind.holds_no_prose(b.kind)]
        self.assertEqual([b.kind for b in prose], ["comment"])
        self.assertNotIn("continues-a-trailing-comment", prose[0].annotations)

    def test_a_blank_line_breaks_the_continuation(self):
        # A gap means the author started something new, not wrapped a sentence.
        got = self._census("x = 1  # a claim\n\n# unrelated\ny = 2\n")
        prose = [b for b in got if b.kind == "comment"]
        self.assertNotIn("continues-a-trailing-comment", prose[0].annotations)

    def test_a_file_of_only_prose_carries_every_empty_place(self):
        got = self._census("# just a note\n")
        # ! `f0` and `f1` are the file's OWN places -- its matter at the head and
        # at the foot -- and both exist whether or not anything sits in them, so
        # a file of one comment carries both. So is `a0`, where a module
        # docstring would go. None of the three depends on prose already being
        # there. ! `f1` since 2026-08-21; a licence at the foot of a file used to
        # land in the closing gap.
        #
        # !! THE `undocumented` WAS ABSENT UNTIL 2026-08-20, because the old
        # generator skipped a node with an empty body: an empty `__init__.py`
        # had nowhere to cite a missing module docstring. Filed as task 4 of
        # `census-degrades-silently`, and closed by moving the emission to the
        # page, which asks the walk rather than the AST.
        # !! WHICH PLACE THE COMMENT OCCUPIES MOVED ON 2026-08-21 and the COUNT
        # did not. It used to fill `b0` -- the gap above the first code line --
        # leaving `f0` empty; under the positional matter rule it fills `f0` and
        # `b0` is the empty one. Four places either way.
        self.assertEqual(
            sorted(b.kind for b in got),
            ["dark-matter", "interval", "matter", "undocumented"],
        )


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
        prose = [b for b in got if not lexer.Kind.holds_no_prose(b.kind)]
        self.assertEqual([b.kind for b in prose], ["trailing-comment", "comment"])
        self.assertIn("continues-a-trailing-comment", prose[1].annotations)

    def test_go_does_not_stamp_an_ordinary_comment(self):
        got = self._census("a.go", "x := 1\n// a fresh note\ny := 2\n")
        prose = [b for b in got if not lexer.Kind.holds_no_prose(b.kind)]
        self.assertNotIn("continues-a-trailing-comment", prose[0].annotations)


class TestAQuoteThatHoldsONECHARACTER(unittest.TestCase):
    """`'` is a CHAR literal in some languages and a STRING in others.

    !! A RUST LIFETIME BLANKED THE REST OF ITS LINE. `_strip_strings` blanks a
    literal so a comment marker inside one stays out of the census, and it read
    `'` as a paired quote in every language. In Rust `&'static str` opens a
    quote that never closes, so everything after it -- the whole comment -- was
    blanked and the paragraph vanished. VERIFIED 2026-08-20: the line censused
    ZERO prose paragraphs, while the identical line with `&str` yielded one.

    !! IT IS A DATA ROW, PER LANGUAGE, and that is why it cannot be one rule.
    `'x'` is one character in Rust, C, Go, Java, C# and Kotlin; `'a string'` is
    prose in Python, JS, Ruby, Lua, shell and SQL. Reading either as the other
    loses a comment.
    """

    def _prose(self, name, text):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / name
            path.write_text(text, encoding="utf-8")
            got = page.page_for(path, text, lexer.language_for(path))
        return [b for b in got if not lexer.Kind.holds_no_prose(b.kind)]

    def test_a_rust_lifetime_does_not_eat_the_comment(self):
        prose = self._prose(
            "a.rs", "pub fn name(&self) -> &'static str { 1 } // the display name\n"
        )
        self.assertEqual([b.kind for b in prose], ["trailing-comment"])
        self.assertEqual(prose[0].text, "the display name")

    def test_the_SAME_line_without_the_lifetime_is_unchanged(self):
        # ! The control the finding was measured against.
        prose = self._prose(
            "a.rs", "pub fn name(&self) -> &str { 1 } // the display name\n"
        )
        self.assertEqual([b.text for b in prose], ["the display name"])

    def test_a_rust_char_literal_is_STILL_blanked(self):
        # !! THE HALF THAT MUST NOT REGRESS. A marker inside a one-character
        # literal is not a comment, and blanking is what keeps it out.
        prose = self._prose("a.rs", "let slash = '/'; // not a comment above\n")
        self.assertEqual([b.text for b in prose], ["not a comment above"])

    def test_an_ESCAPED_char_literal_is_blanked_too(self):
        prose = self._prose("a.rs", "let nl = '\\n'; // still one comment\n")
        self.assertEqual([b.text for b in prose], ["still one comment"])

    def test_a_lifetime_INSIDE_a_string_is_not_reached(self):
        # ! The `"` opens first, so the `'` never gets its own reading.
        prose = self._prose("a.rs", 'let s = "it\'s //here"; // the real one\n')
        self.assertEqual([b.text for b in prose], ["the real one"])

    def test_TWO_LIFETIMES_are_not_one_literal(self):
        """!! THE FIRST FIX WAS TOO LOOSE AND BLANKED REAL CODE.

        It scanned a WINDOW for any closer within a character's width, so the
        `'` of `<'a>` found the `'` of `&'a` and everything between them was
        read as a literal. Measured 2026-08-21: `fn f<'a>(x: &'a T) { } // note`
        came back `fn f<         a T) { } // note` -- 9 characters of code gone,
        and a comment opener falling in that span would go with them.

        ! A character is ONE character, so its closer is at a fixed offset. The
        window was never the right question.
        """
        prose = self._prose("a.rs", "fn f<'a>(x: &'a T) { return 1; } // the note\n")
        self.assertEqual([b.text for b in prose], ["the note"])

    def test_a_comment_BETWEEN_two_lifetimes_survives(self):
        # ! The consequence that made it worth fixing rather than filing: an
        # opener inside the blanked span disappears, so the comment is dropped
        # from the census with exit 0.
        prose = self._prose("a.rs", "fn f<'a, 'b>(x: u8) { } // the note\n")
        self.assertEqual([b.text for b in prose], ["the note"])

    def test_the_WIDEST_escape_is_recognised(self):
        r"""!! `'\u{10FFFF}'` IS THE LITERAL THE BOUND EXISTS FOR, and the first
        bound never reached it -- the closer sits at +11 and the window stopped
        at +10, so the one case the constant was sized for was the one it did
        not recognise. Measured 2026-08-21.
        """
        prose = self._prose("a.rs", "let c = '\\u{10FFFF}'; // the note\n")
        self.assertEqual([b.text for b in prose], ["the note"])

    def test_a_SINGLE_QUOTED_STRING_language_is_untouched(self):
        # !! THE REASON IT IS PER LANGUAGE. In JS `'...'` is a string, so the
        # `//` inside it must still be blanked -- the opposite of Rust.
        prose = self._prose("a.js", "const u = 'http://x'; // the only comment\n")
        self.assertEqual([b.text for b in prose], ["the only comment"])


class TestALineWhosePrefixIsAStringIsSTILLCode(unittest.TestCase):
    """Blanking a literal must not erase the evidence that code came first.

    !! A JS ARRAY ELEMENT WAS CENSUSED AS A WHOLE-LINE COMMENT. The whole-line
    test ran `code.strip().startswith(openers)` on the string-BLANKED line, so
    `  "b" // the last one` blanked to `      // the last one`, whose strip
    starts with the opener. The element left `code_lines` entirely.

    !! WHAT THAT COSTS IS NOT THE MISREADING. Every `b` and `c` below the line
    shifts, so a galley splice over one of those addresses lands on the wrong
    place -- and the paragraph's TEXT holds `"b"`, which is executable code
    handed to four reviewers as prose. Silent: no refusal, exit 0. Measured
    2026-08-20.
    """

    def _prose(self, name, text):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / name
            path.write_text(text, encoding="utf-8")
            got = page.page_for(path, text, lexer.language_for(path))
        return [b for b in got if not lexer.Kind.holds_no_prose(b.kind)]

    def _code(self, name, text):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / name
            path.write_text(text, encoding="utf-8")
            got = page.page_for(path, text, lexer.language_for(path))
        return sorted(page.code_lines(text, [vars(b) for b in got]))

    JS = 'const a = [\n  "a",\n  "b" // the last one\n];\n'

    def test_the_element_is_a_TRAILING_comment_not_a_whole_line_one(self):
        prose = self._prose("a.js", self.JS)
        self.assertEqual([b.kind for b in prose], ["trailing-comment"])
        self.assertEqual(prose[0].text, "the last one")

    def test_the_code_it_sits_beside_is_its_ANCHOR(self):
        prose = self._prose("a.js", self.JS)
        self.assertEqual(prose[0].anchor, '  "b"')

    def test_the_anchor_and_the_paragraph_RECONSTRUCT_the_line(self):
        # !! THE INVARIANT `Paragraph` STATES, and the one that says the split
        # landed in the right place: the separating space belongs to the
        # paragraph, not to the anchor.
        prose = self._prose("a.js", self.JS)
        self.assertEqual(
            prose[0].anchor + prose[0].raw_lines[0], self.JS.splitlines()[2]
        )

    def test_the_line_STAYS_in_the_code_set(self):
        # !! THE HALF THAT SHIFTS ADDRESSES. Line 3 dropped out entirely, so
        # every `b` and `c` below it named a different place.
        self.assertEqual(self._code("a.js", self.JS), [1, 2, 3, 4])

    def test_the_same_shape_in_C(self):
        # ! The prefix must blank to WHITESPACE for the defect to fire, so it is
        # an array element and not `char *s = "b"; // note` -- that one has
        # `char *s =` in front and was always read correctly.
        prose = self._prose("a.c", 'char *a[] = {\n  "a",\n  "b" // the last one\n};\n')
        self.assertEqual([b.kind for b in prose], ["trailing-comment"])
        self.assertEqual(prose[0].text, "the last one")

    def test_a_REAL_whole_line_comment_is_still_one(self):
        # ! NOT on line 1: a run there is the file's own MATTER since 2026-08-21,
        # and this test is about the OPENER being read rather than about which
        # series the run lands in.
        prose = self._prose("a.js", "const a = 1;\n// a fresh note\nconst b = 2;\n")
        self.assertEqual([b.kind for b in prose], ["comment"])

    def test_an_INDENTED_whole_line_comment_is_still_one(self):
        # ! Whitespace before the opener is not code, and this is the case the
        # blanked-line test got right and must keep getting right.
        prose = self._prose("a.js", "function f() {\n    // a fresh note\n}\n")
        self.assertEqual([b.kind for b in prose], ["comment"])


class TestARunsCLOSINGLineIsCutAtTheCloser(unittest.TestCase):
    """Code after `*/` is not the comment's, and it was being censused as prose.

    !! THE FILE RECORDED THIS AS FIXED FOR THE OPENING LINE. `int b = 2; /* note`
    cuts at the opener, and has since 2026-08-17 -- the closing line was never
    covered, so a run that opened earlier appended its last line WHOLE.
    Measured 2026-08-20 on C: `/* note\\n   more */ int x = 5;` yielded one
    paragraph whose text was `/* note more */ int x = 5;`, so the statement was
    handed to four reviewers as prose and run through the annotation regexes.
    """

    SRC = "int a = 1;\n/* note\n   more */ int x = 5;\nint b = 2;\n"

    def _page(self, text):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "a.c"
            path.write_text(text, encoding="utf-8")
            return text, page.page_for(path, text, lexer.language_for(path))

    def test_the_statement_is_not_in_the_prose(self):
        _, got = self._page(self.SRC)
        prose = [b for b in got if not lexer.Kind.holds_no_prose(b.kind)]
        self.assertEqual([b.text for b in prose], ["/* note more */"])
        self.assertNotIn("int x = 5;", prose[0].text)

    def test_the_ONE_LINE_twin_is_already_right(self):
        """!! `/* note */ int x = 5;` IS WHOLLY A CODE LINE, and censuses as one.

        Roy's 2026-08-19 ruling covers it: a comment that closes mid-line with
        code after it is not censused, and the line stays code. Measured over
        the fetched corpora, this form is ordinary -- 1,551 hits in 180,821
        lines of C and JS/TS.
        """
        text, got = self._page("int a = 1;\n/* note */ int x = 5;\nint b = 2;\n")
        self.assertEqual([b for b in got if not lexer.Kind.holds_no_prose(b.kind)], [])
        self.assertEqual(
            sorted(page.code_lines(text, [vars(b) for b in got])), [1, 2, 3]
        )

    def test_the_SPANNING_form_loses_its_code_line_and_that_is_ACCEPTED(self):
        """!! THE RESIDUE, PINNED. Ruled 2026-08-20 after measuring it.

        The run is censused and `int x = 5;` leaves `code_lines`, so every
        interval boundary below it moves. Both fixes cost more than the shape is
        worth: dropping the run leaves the opening line -- nothing but comment --
        belonging to nothing, and keeping both needs a field for where the text
        ENDS or a kind for comment-then-code.

        !! IT OCCURS 0 TIMES in 180,821 lines of C and JS/TS across the fetched
        corpora, and the style guides discourage it. Roy: *"it is stupid to break
        context like that."* ! This test exists so the residue is CHECKED rather
        than merely accepted -- if the behaviour changes, it changed on purpose.
        """
        text, got = self._page(self.SRC)
        self.assertEqual(sorted(page.code_lines(text, [vars(b) for b in got])), [1, 4])

    def test_a_run_that_does_NOT_close_on_the_line_is_unchanged(self):
        text, got = self._page("/* one\n   two\n   three */\nint a = 1;\n")
        prose = [b for b in got if not lexer.Kind.holds_no_prose(b.kind)]
        self.assertEqual([b.text for b in prose], ["/* one two three */"])
        self.assertEqual((prose[0].start, prose[0].end), (1, 3))


class TestANESTEDBlockCommentClosesWhenEVERYLayerDoes(unittest.TestCase):
    """`/* a /* b */ c */` is ONE comment where the language nests.

    !! IT COST THE WHOLE COMMENT. Measured 2026-08-20 on Rust: `let a = 1; /*
    outer /* inner */ still comment */` censused ZERO prose paragraphs. The scan
    closed at the FIRST `*/`, saw ` still comment */` after it, and applied the
    intermediate-comment rule -- which says a comment closing mid-line with code
    after it is not censused. There was no code after it; there was more comment.

    !! NESTING IS A DATA ROW, PER LANGUAGE. Rust, Swift and Kotlin nest their
    block comments; C, C++, Java, C#, JS, TS, Go and SQL do not, and there the
    first closer still wins. Lua nests only through its `--[==[` long-bracket
    form, which is a different opener, so it does not.

    ! WHERE IT MATTERS IS THE TRAILING COMMENT. Roy, 2026-08-20: *"the only
    place we need to care is if it is a trailing comment."* A `b` needs no depth
    -- a gap cannot hold a line of code, so its bounds are the code either side
    -- and no language here marks documentation with a bare `/*`, so depth
    cannot change what counts as a doc either.
    """

    def _prose(self, name, text):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / name
            path.write_text(text, encoding="utf-8")
            got = page.page_for(path, text, lexer.language_for(path))
        return [b for b in got if not lexer.Kind.holds_no_prose(b.kind)]

    NESTED = "let a = 1; /* outer /* inner */ still comment */\nlet b = 2;\n"

    def test_the_whole_nested_run_is_ONE_trailing_comment(self):
        prose = self._prose("a.rs", self.NESTED)
        self.assertEqual([b.kind for b in prose], ["trailing-comment"])
        self.assertEqual(prose[0].text, "/* outer /* inner */ still comment */")

    def test_it_spans_lines_the_same_way(self):
        prose = self._prose(
            "a.rs", "let a = 1; /* outer\n   /* inner */\n   still */\nlet b = 2;\n"
        )
        self.assertEqual([b.kind for b in prose], ["trailing-comment"])
        self.assertEqual((prose[0].start, prose[0].end), (1, 3))

    def test_a_language_that_does_NOT_nest_still_closes_at_the_first(self):
        # !! THE GUARD. In C the first `*/` closes it and ` still comment */` is
        # code after a mid-line close -- which the intermediate-comment ruling
        # says is not censused. Unchanged by this.
        self.assertEqual(self._prose("a.c", self.NESTED.replace("let", "int a")), [])

    def test_an_ORDINARY_block_comment_is_unaffected_where_it_nests(self):
        prose = self._prose("a.rs", "let a = 1; /* just the one */\n")
        self.assertEqual([b.text for b in prose], ["/* just the one */"])

    def test_LUA_long_brackets_do_not_nest(self):
        # ! `--[[ ]]` nests only via `--[==[`, a different opener, so the first
        # `]]` closes this. ! The leading `--` is off because Lua's LINE comment
        # marker is `--` and `_join` strips it -- nothing to do with nesting.
        prose = self._prose("a.lua", "local a = 1 --[[ outer --[[ inner ]]\n")
        self.assertEqual([b.text for b in prose], ["[[ outer --[[ inner ]]"])


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
            if not paragraph.original_column:
                continue
            text = self.C if paragraph.path == "x.c" else self.PY
            line = text.splitlines()[paragraph.start - 1]
            with self.subTest(block=paragraph.text):
                self.assertEqual(
                    line[: paragraph.original_column - 1], paragraph.anchor
                )

    def test_a_block_owning_its_lines_has_no_code_anchor(self):
        # ! Its anchor is a DECLARATION, which naming needs structure the
        # lexical tier does not have. Nothing here invents one.
        text = "int a = 1;\n// a note\nint b = 2;\n"
        path = Path("x.c")
        paragraphs = lexer.paragraphs_lexical(path, text, lexer.language_for(path))
        note = next(b for b in paragraphs if b.kind == "comment")
        self.assertEqual(note.original_column, 0)
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
        root = ROOT
        scripts = root / "src/comment_review"
        holes = 0
        seen = 0
        # ! RGLOB: the modules sit in seven sub-packages since 2026-08-24, and
        # a flat glob of the package root finds only `__init__.py`.
        for src in sorted(scripts.rglob("*.py")):
            body = src.read_text(encoding="utf-8")
            for b in lexer.paragraphs_stdlib(src, body):
                if not b.original_column:
                    continue
                seen += 1
                if b.anchor != body.splitlines()[b.start - 1][: b.original_column - 1]:
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
        # ! `# a header note` on line 1 is NOT one of these since 2026-08-21: a
        # run opening the file is its own MATTER, so the lexer types it `matter`
        # and anchors it to the MODULE. Roy: *"It is a matter designator, the
        # anchor is the module."*
        self.assertEqual(self._one("matter", 1).anchor, "<module>")
        # ! Line 5, not 3. A run stopped OWNING the blanks above it on
        # 2026-08-21 -- those are LEADING now -- so it starts where its
        # prose starts.
        self.assertEqual(self._one("comment", 5).anchor, "def f():")

    def test_a_trailing_comment_is_anchored_to_its_OWN_line(self):
        self.assertEqual(self._one("trailing-comment").anchor, "    return os")

    def test_one_anchor_serves_the_b_AND_the_c_of_one_line(self):
        # !! The one-to-many relationship, measured on one line of code.
        # ! Measured on `def f():` rather than on `import os`, because the run
        # above `import os` is the file's own matter and answers to the module
        # rather than to a line -- which is the one anchor that serves no `c`.
        b = self._one("comment", 5)
        c = self._one("margin", 6)
        self.assertEqual(b.anchor, c.anchor)
        # ! `page_for` does not stamp the address -- the run loop does, once
        # the path is repo-relative -- so the two places are told apart here by
        # the fact the cues reads: a `c` has a column and a `b` has none.
        self.assertTrue(c.original_column)
        self.assertFalse(b.original_column)

    def test_the_b_and_the_c_of_a_line_AGREE_on_the_code(self):
        # !! They are two computations of one fact unless the `b` copies the
        # `c`. Re-cutting the line here answered `'    return os  # why'` where
        # the `c` for the same line answered `'    return os'`.
        margins = {b.start: b.anchor for b in self.paragraphs if b.original_column}
        for paragraph in self.paragraphs:
            if (
                paragraph.original_column
                or paragraph.declares >= 0
                or not paragraph.anchor
            ):
                continue
            with self.subTest(address=paragraph.address):
                # ! AN `f` IS THE FILE'S OWN place -- `f0` at the head, `f1` at
                # the foot -- and neither is anchored to a line, so neither has
                # a `c` to copy. ! Written as the SERIES rather than as `@f0`,
                # so the day a third is emitted it needs no edit.
                if paragraph.address.split("@")[-1].startswith(COVERS):
                    continue
                # !! NOR IS THE CLOSING GAP, since 2026-08-22. It is emitted at
                # the EOF trigger and anchored to it, so there is no line of
                # code for a `c` to agree with -- which is the point: it used to
                # borrow the last line's, and then two places answered one line.
                if paragraph.anchor == EOF:
                    continue
                self.assertIn(paragraph.anchor, margins.values())

    def test_NO_block_in_this_file_lacks_an_anchor(self):
        # ! Roy, 2026-08-19: "an anchor missing in a Record is a broken Record."
        # ! LEADING is excluded: it answers to nothing, which is ruled rather than
        # missing -- Roy, 2026-08-21, taking the trade: *"the anchors are
        # empty."*
        self.assertEqual(
            [
                b.kind
                for b in self.paragraphs
                if not b.anchor and b.kind != lexer.Kind.LEADING
            ],
            [],
        )

    def test_the_gap_at_the_END_is_anchored_to_EOF(self):
        # !! IT TOOK THE LINE ABOVE IT UNTIL 2026-08-22, which broke Roy's own
        # 2026-08-21 ruling in the sentence that made EOF a trigger: a place
        # emitted at a trigger is a ROW at that trigger, never *"some other
        # treatment"*. Reaching back to the previous trigger for an anchor put
        # the special case back one level down.
        #
        # ! Roy, 2026-08-22: *"the last `b` triggers on EOF and records either
        # `<eof>` or `<module>`, and its anchor and where it is placed becomes a
        # determined fact by the compositor."*
        gaps = [b for b in self.paragraphs if b.kind == "interval"]
        # ! By ADDRESS, not by line: a gap holding no line has None for both
        # ends, and the `b` series counts down the page in order anyway.
        last = max(gaps, key=lambda b: int(b.address.split("@")[-1][1:]))
        self.assertEqual(last.anchor, EOF)

    def test_no_block_in_this_repos_own_scripts_lacks_one(self):
        # !! The hole, run as a gate: 6,376 of 6,531 paragraphs carried an empty
        # anchor before 2026-08-19 -- 98% of this repo's own census.
        root = ROOT
        scripts = root / "src/comment_review"
        holes = []
        # ! RGLOB: the modules sit in seven sub-packages since 2026-08-24, and
        # a flat glob of the package root finds only `__init__.py`.
        for src in sorted(scripts.rglob("*.py")):
            body = src.read_text(encoding="utf-8")
            for b in page.page_for(src, body, lexer.language_for(src)):
                # ! LEADING answers to nothing, ruled 2026-08-21.
                if b.kind == lexer.Kind.LEADING:
                    continue
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
        # ! THE KIND, NOT AN ANNOTATION, since 2026-08-21. The lexer types a run
        # `matter`; the page used to stamp it afterwards, which put a positioning
        # rule in a module that may hold none.
        return [b.start for b in self._census(text) if b.kind == lexer.Kind.MATTER]

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

    def test_a_leading_comment_with_NO_module_docstring_IS_front_matter(self):
        # !! SUPERSEDED 2026-08-21, and the reverse of what it asserted. The old
        # rule needed a module docstring to exist above which a comment could
        # sit, and `declares` is stated only where a parser runs -- so a `.c` or
        # `.rs` licence header matched nothing and was reviewed as ordinary work.
        #
        # ! Roy ruled the replacement positional: *"Any normal comment section at
        # the top of the file becomes f0 until there is either a docstring or a
        # blank line."* `# about the import` IS about the import, and it becomes
        # `f0` anyway -- knowingly: *"The agents can always ask for the record for
        # the f0 to move it ... it is a little cluggy but it will be consistent."*
        self.assertEqual(self._marked(self.NO_DOCSTRING), [1])

    def _cue(self, name, text, line):
        """The cue of the paragraph HOLDING this line.

        ! Containment, not `original_start == line`: a gap paragraph owns the
        blank lines around its prose, so a comment on line 3 with a blank above
        it starts at 2. Matching the start asked a question about
        `fill_the_gaps` rather than about the cue.
        """
        path = Path(name)
        for b in page.page_for(path, text, lexer.language_for(path)):
            first, last = b.original_start, b.original_end
            if first and last and first <= line <= last and not b.original_column:
                return b.address.split("@")[-1]
        return ""

    def test_a_licence_at_the_FOOT_of_a_file_is_back_matter(self):
        # !! `f1`, ruled 2026-08-21. It landed in the CLOSING GAP before -- the
        # gap after the last statement, which belongs to that statement.
        text = "import os\n\nx = 1\n\n# Copyright 2001.\n"
        self.assertEqual(self._cue("m.py", text, 5), "f1")

    def test_a_file_whose_ONLY_prose_is_at_the_foot_is_not_the_HEAD_matter(self):
        # !! The head run and the foot run are the SAME paragraph here, and it is
        # the foot's. Guarding on `foot is not head` left it marked as neither.
        text = "int add(int a) { return a; }\n\n/* Copyright 2001. */\n"
        self.assertEqual(self._cue("m.c", text, 3), "f1")

    def test_a_comment_BETWEEN_two_code_lines_is_neither(self):
        # ! It is above the code below it, which is what a `b` is for. Matter is
        # only what sits outside the code entirely.
        text = "import os\n\n# about the next line\nx = 1\n"
        self.assertEqual(self._cue("m.py", text, 3), "b1")

    def test_the_foot_run_needs_no_blank_line_above_it(self):
        # ! What ends it reading upward is CODE, exactly as a blank line does.
        text = "import os\nx = 1\n# no blank above me\n"
        self.assertEqual(self._cue("m.py", text, 3), "f1")

    def test_a_comment_that_DOCUMENTS_something_is_not_front_matter(self):
        # !! WHAT ENDS THE MATTER IS DOCUMENTATION, not the comment's syntax. Go
        # documents with plain `//`, so a kind test would have called every Go
        # file's first doc comment a licence. `declares` is what tells them apart.
        path = Path("g.go")
        got = page.page_for(
            path, "// One does it.\nfunc One() {}\n", lexer.language_for(path)
        )
        marked = [b.start for b in got if "matter" in b.annotations]
        self.assertEqual(marked, [])

    def test_it_is_dropped_from_the_FILTERED_listing(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "a.py"
            path.write_text(self.LICENCE, encoding="utf-8")
            out = subprocess.run(
                [*cli("census"),
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
            self.assertNotIn("matter", out.stdout)


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
                [*cli("census"),
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
                [*cli("census"),
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
    ten lexical languages, was refused by the retired `paragraph_matches` on a census
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
                        transcribes(vars(b), lines),
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
                    if b.original_column:
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
                head = b.anchor if b.original_column else ""
                self.assertEqual(head + b.raw_lines[0], lines[b.start - 1])
                self.assertTrue(transcribes(vars(b), lines))

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
        self.assertTrue(transcribes(vars(margin), text.splitlines()))

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
                if not lexer.Kind.holds_no_prose(b.kind)
                and not transcribes(vars(b), lines)
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
            return prose, list(page.code_lines(body, [vars(b) for b in paragraphs]))

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
            ["git", "ls-files", "src/**/*.py"],
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
            self.assertIn(2, page.code_lines(body, [vars(b) for b in paragraphs]))


class TestTheCensusCarriesNoFence(unittest.TestCase):
    """A `d` never reaches an agent, and nothing checked that until 2026-08-24.

    !! LEADING IS THE FENCE BETWEEN TWO PLACES AND IS NOT ONE. Roy, 2026-08-24:
    *"The leading is not something that will be passed to the agents ... It gets
    dropped because there is nothing to rule on. It is for white space."* And:
    *"You don't put an address on a fence because it is what divides
    properties."*

    ! IT WAS CARRIED ANYWAY, as a row whose `address` was `""` -- so every
    consumer downstream had to test for that blank to learn the row was never a
    place. MEASURED before the fix: 3 such rows from a ten-line file, and 422 of
    9,459 over this repo's own `src/`.

    !! AND THE WHOLE SUITE PASSED EITHER WAY. Dropping them broke NOTHING, which
    is the argument for this class existing: nothing asserted the emit's
    population in either direction.
    """

    def _rows(self, text):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "m.py"
            src.write_text(text, encoding="utf-8")
            out = subprocess.run(
                [*cli("census"), "--json", "--repo", tmp, str(src)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(out.returncode, 0, out.stderr)
            return json.loads(out.stdout)

    # A file whose blank runs are unmistakable: three of them, two lines each.
    SPACED = '"""Doc."""\n\n\n# a note\n\n\nx = 1\n'

    def test_every_row_the_census_emits_names_a_place(self):
        rows = self._rows(self.SPACED)
        self.assertTrue(rows, "the sample must be real")
        blank = [r for r in rows if not r.get("address")]
        self.assertEqual(blank, [], "a row with no address is not a place")

    def test_no_row_is_leading(self):
        # ! ASKED BY KIND TOO. The address test above would also pass if a fence
        # were given an address, which is the other way to get this wrong.
        kinds = {r.get("kind") for r in self._rows(self.SPACED)}
        self.assertNotIn("leading", kinds)

    def test_the_page_still_HOLDS_the_fences_it_does_not_emit(self):
        # !! THE CUT IS THE EMIT, NOT THE PAGE. A fence still has to be set back
        # or the file cannot round trip, so `page_for` keeps it and only the
        # census drops it. A change that removed it from the page would pass the
        # two tests above and destroy the compositor.
        built = page.page_for(
            Path("m.py"), self.SPACED, lexer.language_for(Path("m.py"))
        )
        held = [b for b in built.paragraphs if b.kind == "leading"]
        self.assertTrue(held, "the page must still carry its fences")
        self.assertTrue(all(not b.address for b in held))
        self.assertTrue(all(b.symbol for b in held), "each is found by SYMBOL")


class TestAnUnaddressedCensusIsREFUSEDAtBothEnds(unittest.TestCase):
    """The census refuses on EMIT and the stage-5 gate on READ.

    !! BOTH, AND FOR DIFFERENT REASONS. The emit check catches the census where
    it is BUILT; the read check catches a FILE -- one from an older version, one
    edited by hand, one from a run that crashed midway. `verdicts.py` takes a
    PATH and trusts what it parses, so nothing else stands between a stale
    census and a certified review.
    """

    def _run(self, script, *args):
        return subprocess.run(
            [*cli(script), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

    def test_the_gate_REFUSES_a_census_it_cannot_cite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "m.py").write_text("# x\nN = 0\n", encoding="utf-8")
            good = self._run(
                "census.py", "--repo", str(root), "--json", str(root / "m.py")
            )
            self.assertEqual(good.returncode, 0, good.stderr)
            stripped = [b | {"address": ""} for b in json.loads(good.stdout)]
            census = root / "c.json"
            census.write_text(json.dumps(stripped), encoding="utf-8")
            report = root / "block-context.json"
            report.write_text(
                json.dumps(
                    {"reviewer": "block-context", "pages": [], "code_concerns": []}
                ),
                encoding="utf-8",
            )
            got = self._run(
                "verdicts.py",
                "--census",
                str(census),
                "--repo",
                str(root),
                "--reviewers",
                "block-context",
                str(report),
            )
            self.assertEqual(got.returncode, 1)
            self.assertIn("NO ADDRESS", got.stdout)
            # !! THE SENTENCE IT USED TO PRINT INSTEAD.
            self.assertNotIn("Stage 5 may rule", got.stdout)

    def test_a_census_of_a_REAL_file_still_passes_both_paths(self):
        # ! Guards the guard the other way: a check that refuses everything is
        # not a check. Both output paths run over a file with prose in it.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "m.py").write_text(
                '"""Doc."""\n\n# a note\nN = 0\n', encoding="utf-8"
            )
            for extra in ([], ["--json"]):
                with self.subTest(json=bool(extra)):
                    got = self._run(
                        "census.py", "--repo", str(root), *extra, str(root / "m.py")
                    )
                    self.assertEqual(got.returncode, 0, got.stderr or got.stdout)

    def test_the_census_REFUSES_a_run_with_NO_PATHS(self):
        """!! The same failure as above with one input fewer, and it is reachable.

        Stage 1 takes its paths from a merge-base diff, so a diff touching no
        reviewable file hands the census nothing. Measured 2026-08-24: it
        printed `[]` and returned 0.
        """
        got = self._run("census.py", "--repo", str(PKG), "--json")
        self.assertEqual(got.returncode, 2)
        self.assertIn("no paths", got.stdout)
        # !! WHAT IT USED TO PRINT. An empty list is the shape the join reads as
        # a complete census, so this is the sentence that has to stop appearing.
        self.assertNotEqual(got.stdout.strip(), "[]")

    def test_LANGUAGES_still_runs_with_no_paths(self):
        # ! The one caller that legitimately passes none. A refusal that also
        # refused this would be the check written to the test rather than to
        # the defect.
        got = self._run("census.py", "--languages")
        self.assertEqual(got.returncode, 0, got.stderr or got.stdout)
        self.assertIn("tokenized", got.stdout)

    def test_the_gate_REFUSES_an_EMPTY_census(self):
        """!! `unaddressed([])` is empty for the wrong reason, so the check
        above it passes vacuously and the run reaches the certification.

        Measured 2026-08-24 over `[]` and a report ruling on nothing: `0
        findings from 1 reviewer over 0 prose paragraphs`, then **"Every
        finding is admissible. Stage 5 may rule."** at exit 0.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            census = root / "c.json"
            census.write_text("[]", encoding="utf-8")
            report = root / "block-context.json"
            report.write_text(
                json.dumps(
                    {"reviewer": "block-context", "pages": [], "code_concerns": []}
                ),
                encoding="utf-8",
            )
            got = self._run(
                "verdicts.py",
                "--census",
                str(census),
                "--repo",
                str(root),
                "--reviewers",
                "block-context",
                str(report),
            )
            self.assertEqual(got.returncode, 1)
            self.assertIn("NO PARAGRAPHS", got.stdout)
            self.assertNotIn("Stage 5 may rule", got.stdout)
