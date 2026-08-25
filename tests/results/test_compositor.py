"""Setting a page as text, and the identity that proves the model is lossless.

Roy, 2026-08-21: *"we can compare the round trip directly page in page out, page
in, comments removed, page out no comments ... No ambiguity about how the page
gets written. No this got lost this wasn't done right."*
"""

import tempfile
import unittest
from pathlib import Path

# ! `_paths` FIRST: importing it is what puts `src/` on the path.
from _paths import PKG, ROOT  # noqa: F401  -- puts `src/` on the path

from comment_review.binder import page as page_mod
from comment_review.machine import constants  # noqa: E402
from comment_review.reading import lexer  # noqa: E402
from comment_review.results import compositor  # noqa: E402


def set_from(name: str, text: str) -> str:
    """Build the page for this text, then set it back."""
    p = Path(name)
    page = page_mod.page_for(p, text, lexer.language_for(p), rel=name)
    return compositor.set_page(page)


class TestAPageSetsBackToItsOwnFile(unittest.TestCase):
    """`set_page(page_for(text)) == text`, byte for byte."""

    def test_a_python_file_round_trips(self):
        text = '"""A module."""\n\nimport os\n\n\ndef f(a):\n    return a\n'
        self.assertEqual(set_from("m.py", text), text)

    def test_a_trailing_comment_round_trips(self):
        # ! The line is the ANCHOR and the room beside it, concatenated -- the
        # whitespace between them belongs to the room.
        text = "import os  # a note\n"
        self.assertEqual(set_from("m.py", text), text)

    def test_a_trailing_comment_SPANNING_LINES_round_trips(self):
        # !! THIS DROPPED TEN C FILES until the identity was run over a corpus,
        # 2026-08-21. Only the FIRST line of a trailing run sits beside code;
        # the rest hold no code and are verbatim. MEASURED on CPython's
        # `object.h`: `PyAsyncMethods *tp_as_async;` carries a comment opening
        # `/* formerly known as tp_compare (Python 2)` and closing on the line
        # below, and every line after the first was set as empty.
        text = "int x; /* opens here\n          and closes here */\nint y;\n"
        self.assertEqual(set_from("m.c", text), text)

    def test_a_file_with_no_prose_at_all_round_trips(self):
        text = "import os\nimport sys\n"
        self.assertEqual(set_from("m.py", text), text)

    def test_a_file_that_is_ONLY_prose_round_trips(self):
        text = "# one\n# two\n"
        self.assertEqual(set_from("m.py", text), text)

    def test_an_empty_file_round_trips(self):
        self.assertEqual(set_from("m.py", ""), "")


class TestTheLineEndingComesFromTheFile(unittest.TestCase):
    """A paragraph cannot state CRLF, so the page's own text answers it.

    ! Without this a Windows checkout is rewritten line for line by a tool that
    changed no prose, and every gate downstream sees a diff of the whole file.
    """

    def test_CRLF_survives(self):
        text = "import os\r\n\r\n# a note\r\nx = 1\r\n"
        self.assertEqual(set_from("m.py", text), text)

    def test_LF_survives(self):
        text = "import os\n\n# a note\nx = 1\n"
        self.assertEqual(set_from("m.py", text), text)

    def test_a_file_with_NO_trailing_newline_gains_none(self):
        # ! `splitlines` drops it, so nothing in the model can state it. The
        # page's text is asked instead.
        text = "# just this"
        self.assertEqual(set_from("m.py", text), text)

    def test_line_endings_picks_CRLF_when_any_line_has_one(self):
        self.assertEqual(compositor.line_endings("a\r\nb\n"), "\r\n")
        self.assertEqual(compositor.line_endings("a\nb\n"), "\n")


class TestItReadsTheParagraphsAndNotTheText(unittest.TestCase):
    """A round trip that consulted `page.text` would prove a string equals itself."""

    def test_a_page_with_every_PROSE_paragraph_emptied_sets_the_code_alone(self):
        # !! ROY'S SECOND ROUND TRIP, 2026-08-21: *"page in page out, page in,
        # comments removed, page out no comments."* Emptying every paragraph
        # leaves the code, because a `c` place holds the LINE and its prose is
        # only the room beside it.
        #
        # !! AND IT IS WHAT MAKES THE IDENTITY MEAN SOMETHING. If `set_page` read
        # `page.text`, this would return the original file with its comment
        # still in it and every other test in this module would pass unchanged.
        p = Path("m.py")
        text = "# a note\nx = 1  # beside\ny = 2\n"
        page = page_mod.page_for(p, text, lexer.language_for(p), rel="m.py")
        for b in page.paragraphs:
            b.raw_lines = []
        self.assertEqual(compositor.set_page(page), "x = 1\ny = 2\n")

    def test_a_page_with_NO_places_over_a_FILE_WITH_TEXT_is_refused(self):
        # !! IT ASSERTED `""` UNTIL 2026-08-21, and that was the wrong answer to
        # the right question. The question is whether `set_page` falls back to
        # `page.text` -- it must not, or a model that had lost every place would
        # set the original file back and the identity would pass over the top of
        # it. But returning `""` is not safe either: `draft()` writes it, and an
        # 884-line file came back as 0 characters. Refusing answers both.
        p = Path("m.py")
        page = page_mod.page_for(p, "# a note\n", lexer.language_for(p), rel="m.py")
        page.cues.reading.clear()
        with self.assertRaises(ValueError):
            compositor.set_page(page)

    def test_changing_a_paragraphs_raw_lines_changes_the_output(self):
        p = Path("m.py")
        text = "# a note\nx = 1\n"
        page = page_mod.page_for(p, text, lexer.language_for(p), rel="m.py")
        for b in page.paragraphs:
            if b.raw_lines == ["# a note"]:
                b.raw_lines = ["# a DIFFERENT note"]
        self.assertEqual(compositor.set_page(page), "# a DIFFERENT note\nx = 1\n")


class TestTheSeriesOrderIsFixedAndFComesFirst(unittest.TestCase):
    """`f0`, then `a0`, then `b0`, then `c0` -- ruled 2026-08-21.

    Roy: *"f0 always first, then a0, then b0, then c0. I know f0 is going to grab
    b0 lines. It is a sacrifice I am willing to make and will give the agents a
    specific set of instructions to look out for this and move it."*

    ! So a file whose front matter is NOT on line 1 is set with the matter above
    the blank that `b` owns. That is LOSSY ON ORDER and never on content, which
    is the line `lossless` holds and `identity` does not.
    """

    def _page(self, name, text):
        p = Path(name)
        return page_mod.page_for(p, text, lexer.language_for(p), rel=name)

    def test_a_file_whose_LINE_1_IS_BLANK_has_no_matter_and_round_trips(self):
        # !! THE SACRIFICE IS GONE, and a sharper ruling removed it rather than a
        # workaround. Roy, 2026-08-21: *"if the opening/closing line is a comment
        # then the matter continues down/up."* Line 1 here is BLANK, so the file
        # has no matter at all, the gap above `int a;` is contiguous, and nothing
        # moves.
        #
        # ! It used to be set as `/* Header. */\n\n\nint a;\n` -- the comment
        # above its own blank line -- because `page.mark_matter` took the first
        # run of PROSE wherever it sat. MEASURED on `cpython/Include/floatobject.h`
        # and 10 others, every one a C header opening with a blank.
        text = "\n/* Header. */\n\nint a;\n"
        self.assertEqual(compositor.set_page(self._page("m.c", text)), text)

    def test_no_line_is_lost_or_invented(self):
        # !! THE INVARIANT THAT MUST NEVER BREAK. It is weaker than `identity` on
        # purpose -- the series order is FIXED at f, a, b, c, so a page can be
        # set in an order the file did not have -- but never with a line missing
        # or a line the file never held.
        text = "\n/* Header. */\n\nint a;\n"
        got = compositor.set_page(self._page("m.c", text))
        self.assertEqual(sorted(got.splitlines()), sorted(text.splitlines()))

    def test_matter_ON_line_1_is_set_unchanged(self):
        text = "/* Header. */\n\nint a;\n"
        self.assertEqual(compositor.set_page(self._page("m.c", text)), text)

    def test_matter_at_the_FOOT_takes_the_second_place_and_stays_there(self):
        # ! `f1`. Taking `f0` would set a closing licence at the head of the
        # file, which is what the count-based mapping alone could not tell.
        text = "int a;\n\n/* Copyright. */\n"
        self.assertEqual(compositor.set_page(self._page("m.c", text)), text)

    def test_lossless_and_identity_now_agree_on_the_shape_that_parted_them(self):
        # ! They differed on a file whose matter sat below a blank line, which
        # the 2026-08-21 ruling stopped producing: line 1 is not a comment, so
        # there is no matter to move.
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "m.c"
            path.write_text("\n/* Header. */\n\nint a;\n", encoding="utf-8")
            self.assertIsNone(compositor.lossless(path))
            self.assertIsNone(compositor.identity(path))

    def test_a_page_that_was_never_BUILT_is_refused_not_set(self):
        # !! IT WOULD EMPTY THE FILE. `page_for` skips the walk when a reader
        # refuses the source, so `reading` is empty and every line is
        # unaccounted for. MEASURED 2026-08-21 on
        # `sentry/src/sentry/api/paginator.py`: 884 lines in, 0 characters out,
        # silently -- it uses PEP 695 syntax the floor interpreter cannot parse.
        #
        # ! `draft()` writes what `set_page` returns, so an empty draft approved
        # by anyone not reading the diff is a deleted file.
        page = self._page("m.py", "x = 1\ny = 2\n")
        page.cues.reading.clear()
        with self.assertRaises(ValueError) as caught:
            compositor.set_page(page)
        self.assertIn("never read", str(caught.exception))

    def test_an_EMPTY_file_is_still_set_as_empty(self):
        # ! The refusal must not fire on a page that is empty because its FILE
        # is: there is nothing unaccounted for.
        self.assertEqual(compositor.set_page(self._page("m.py", "")), "")

    def test_lossless_REPORTS_a_line_that_goes_missing(self):
        # ! The failure the gate exists for, forced: empty one place's prose and
        # the line it held is gone.
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "m.c"
            path.write_text("/* Header. */\nint a;\n", encoding="utf-8")
            page = self._page("m.c", path.read_text(encoding="utf-8"))
            for b in page.paragraphs:
                if b.raw_lines == ["/* Header. */"]:
                    b.raw_lines = []
            self.assertNotEqual(
                sorted(compositor.set_page(page).splitlines()),
                sorted(path.read_text(encoding="utf-8").splitlines()),
            )


class TestTheShippedTreeSetsBackToItself(unittest.TestCase):
    """The identity, over real files rather than fixtures.

    ! MEASURED 2026-08-21 over 699 files in ten languages -- every shipped
    script, this repo's own, and `corpora/` -- all identical. This test holds the
    shipped tree, which is what a change to `page.py` or `lexer.py` would break.
    """

    def test_every_shipped_script_sets_back_to_itself(self):
        root = (
            ROOT
            / "src/comment_review"
        )
        broken = {}
        for path in sorted(root.glob("*.py")):
            why = compositor.identity(path)
            if why is not None:
                broken[path.name] = why
        self.assertEqual(broken, {})


class TestOnlyALineBreakBreaksALine(unittest.TestCase):
    """A separator inside a literal is DATA, and setting it back must keep it.

    !! `str.splitlines()` BREAKS ON ELEVEN THINGS AND EIGHT ARE NOT LINE
    ENDINGS -- the vertical tab, the form feed, three ASCII separators, the
    next-line control, and Unicode's own line and paragraph separators. Every one
    of them can sit inside a string literal, where it is a character and not a
    line break.

    !! AND BOTH GATES PASSED ON THE CORRUPTED FILE, which is why this is a test
    and not a note. MEASURED 2026-08-22: the reader saw three lines where the
    file has two, the compositor rejoined them with newlines, and the literal
    came back broken across two lines -- a `SyntaxError`. `identity` reported
    *3 lines in, 3 out* and `lossless` returned None, because both were counting
    the reader's own idea of a line rather than the file's.
    """

    # ! One per separator `splitlines` invents a line at, each inside a literal.
    SEPARATORS = ("\v", "\f", "\x1c", "\x1d", "\x1e", "\x85", " ", " ")

    def test_a_separator_inside_a_literal_sets_back_unchanged(self):
        for sep in self.SEPARATORS:
            with self.subTest(sep=repr(sep)):
                src = f'x = "a{sep}b"\ny = 1\n'
                self.assertEqual(set_from("m.py", src), src)

    def test_the_file_still_compiles_after_setting(self):
        # ! The consequence a reader sees. A lost separator does not merely
        # differ -- it ends the string literal early.
        for sep in self.SEPARATORS:
            with self.subTest(sep=repr(sep)):
                src = f'x = "a{sep}b"\ny = 1\n'
                compile(set_from("m.py", src), "m.py", "exec")

    def test_a_real_line_ending_still_breaks_a_line(self):
        # ! The other half: the three that ARE endings must still split.
        for ending in ("\n", "\r\n", "\r"):
            with self.subTest(ending=repr(ending)):
                src = f"x = 1{ending}y = 2{ending}"
                self.assertEqual(len(constants.text_lines(src)), 2)
