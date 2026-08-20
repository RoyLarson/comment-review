"""The galley is the proposal set as files, and it refuses what it cannot splice."""

import json  # noqa: I001  -- path shim below must import before galley
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from _paths import SCRIPTS  # noqa: F401
import galley
import lexer
import page

ORIGINAL = "def f():\n    # old note\n    # second line\n    return 1\n"


class TestSplice(unittest.TestCase):
    def test_a_replacement_lands_on_the_named_range(self):
        out = galley.splice(ORIGINAL, [(2, 3, 0, "    # new note")])
        self.assertEqual(out, "def f():\n    # new note\n    return 1\n")

    def test_a_longer_replacement_does_not_eat_the_line_below(self):
        out = galley.splice(ORIGINAL, [(2, 3, 0, "    # a\n    # b\n    # c")])
        self.assertIn("    return 1", out)
        self.assertNotIn("old note", out)

    def test_two_edits_apply_bottom_up_so_neither_shifts_the_other(self):
        # !! The case that makes descending order load-bearing: the first edit
        # changes the line count, so a top-down splice would put the second one
        # in the wrong place.
        text = "a\n# one\nb\n# two\nc\n"
        out = galley.splice(text, [(2, 2, 0, "# ONE\n# ONE MORE"), (4, 4, 0, "# TWO")])
        self.assertEqual(out, "a\n# ONE\n# ONE MORE\nb\n# TWO\nc\n")

    def test_crlf_survives(self):
        out = galley.splice("a\r\n# old\r\nb\r\n", [(2, 2, 0, "# new")])
        self.assertEqual(out, "a\r\n# new\r\nb\r\n")

    def test_a_file_with_no_trailing_newline_keeps_none(self):
        self.assertEqual(galley.splice("a\n# old", [(2, 2, 0, "# new")]), "a\n# new")


class TestOverlapsAreRefused(unittest.TestCase):
    def test_two_edits_sharing_a_line_are_found(self):
        self.assertEqual(galley.overlaps([(1, 3, 0, "x"), (3, 5, 0, "y")]), (1, 3))

    def test_adjacent_edits_do_not_overlap(self):
        self.assertIsNone(galley.overlaps([(1, 2, 0, "x"), (3, 4, 0, "y")]))

    def test_order_of_the_list_does_not_matter(self):
        self.assertEqual(galley.overlaps([(3, 5, 0, "y"), (1, 3, 0, "x")]), (1, 3))


class TestBlockMatches(unittest.TestCase):
    """!! This check must be able to FAIL, and the first version could not.

    It compared the file against a slice of itself, which is equal by
    construction. A stale census range would then have been spliced over
    whatever now sits at those line numbers -- the one failure a galley must
    never produce quietly.
    """

    LINES = ORIGINAL.splitlines()

    def test_a_matching_block_passes(self):
        paragraph = {
            "start": 2,
            "end": 3,
            "edit_start": 2,
            "edit_end": 3,
            "raw_lines": ["    # old note", "    # second line"],
        }
        self.assertTrue(galley.paragraph_matches(self.LINES, paragraph))

    def test_a_block_whose_text_moved_is_caught(self):
        paragraph = {
            "start": 2,
            "end": 3,
            "edit_start": 2,
            "edit_end": 3,
            "raw_lines": ["    # SOMETHING ELSE", "    # x"],
        }
        self.assertFalse(galley.paragraph_matches(self.LINES, paragraph))

    def test_a_range_past_the_end_of_the_file_is_caught(self):
        paragraph = {
            "start": 9,
            "end": 12,
            "edit_start": 9,
            "edit_end": 12,
            "raw_lines": ["    # x"],
        }
        self.assertFalse(galley.paragraph_matches(self.LINES, paragraph))

    def test_a_block_carrying_no_raw_lines_is_refused(self):
        # An interval paragraph stores none, and nothing can be verified against it.
        self.assertFalse(
            galley.paragraph_matches(
                self.LINES, {"start": 2, "end": 3, "edit_start": 2, "edit_end": 3}
            )
        )


class TestCLI(unittest.TestCase):
    """End to end: the exit code and the tree it writes."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.repo = self.root / "repo"
        (self.repo / "pkg").mkdir(parents=True)
        (self.repo / "pkg" / "m.py").write_text(ORIGINAL, encoding="utf-8")
        # !! FROM `census.py`, not by hand. A hand-built census omits the
        # fields the galley asks of it, and `galley.py` refuses such a census
        # whole -- rightly, since the one per-field default that was tried put
        # back a deleted statement. A fixture that hand-writes the shape also
        # drifts from what the tool actually emits, which is how a trailing
        # comment passed here while the shipped path deleted code.
        self.census = self.root / "census.json"
        # ! STAMPED, as `census.py`'s own run loop does once the path is
        # repo-relative. `page_for` alone leaves every address empty, and a
        # census like that can key nothing -- `unanswerable` refuses it now
        # rather than letting each edit fail separately.
        built = page.page_for(
            Path("pkg/m.py"), ORIGINAL, lexer.language_for(Path("m.py"))
        )
        sorted(page.code_lines(ORIGINAL, built))
        self.census.write_text(
            json.dumps([vars(b) for b in built], default=list), encoding="utf-8"
        )
        self.paragraphs = json.loads(self.census.read_text(encoding="utf-8"))
        self.note = next(
            b["address"] for b in self.paragraphs if b["kind"] == "comment"
        )
        self.out = self.root / "galley"

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, edits):
        path = self.root / "edits.json"
        path.write_text(json.dumps(edits), encoding="utf-8")
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "galley.py"),
                "--repo",
                str(self.repo),
                "--census",
                str(self.census),
                "--edits",
                str(path),
                "--out",
                str(self.out),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

    def test_it_writes_a_mirror_and_leaves_the_source_alone(self):
        result = self._run({str(self.note): "    # new note"})
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(
            (self.out / "pkg" / "m.py").read_text(encoding="utf-8"),
            "def f():\n    # new note\n    return 1\n",
        )
        self.assertEqual(
            (self.repo / "pkg" / "m.py").read_text(encoding="utf-8"), ORIGINAL
        )

    def test_an_ADDRESS_the_census_does_not_carry_is_refused(self):
        # ! `--edits` keys by ADDRESS now, so a key nothing carries is refused
        # by name rather than by range. An index would be the wrong key even if
        # something still emitted one: it is a position in ONE census, and the
        # galley is censused again for round 2.
        result = self._run({"pkg:m.py@b99": "    # x"})
        self.assertEqual(result.returncode, 1)
        self.assertIn("no paragraph in this census carries that address", result.stdout)

    def test_a_stale_range_refuses_the_file_and_writes_nothing(self):
        (self.repo / "pkg" / "m.py").write_text(
            "def f():\n    return 1\n", encoding="utf-8"
        )
        result = self._run({str(self.note): "    # new note"})
        self.assertEqual(result.returncode, 1)
        self.assertIn("no longer match the census", result.stdout)
        self.assertFalse((self.out / "pkg" / "m.py").exists())


class TestAnIntervalIsInsertedInto(unittest.TestCase):
    """An `add` cites the empty INTERVAL its prose is missing from.

    !! An interval's `start` and `end` are the two lines of CODE that bound it,
    so replacing `start..end` writes over both of them. Measured 2026-08-17 on
    the first cycle run: `paragraph_matches` answered False for all 99 intervals in
    one census, so every `add` was refused before the range was ever used --
    and the refusal hid the fact that the range would have deleted code.

    !! THE PARAGRAPHS HERE COME FROM A REAL CENSUS. Built by hand they carried no
    `edit_start`/`edit_end`, took the legacy fallback, and went on passing
    against a shape `census.py` no longer emits -- which is the whole failure
    being tested, one level up.
    """

    FILE = "a = 1\nb = 2\nc = 3\n"

    def _census(self, text):
        prose = lexer.paragraphs_stdlib(Path("m.py"), text)
        return [b.__dict__ for b in page.intervals(Path("m.py"), text, prose)]

    def _gap(self, text, edit_start, edit_end):
        """The interval whose EDIT range is this, as the census emits it.

        ! Found by the edit range, not the addressing one. A gap between two
        adjacent code lines has no lines of its own, so it is addressed at line
        0 -- every line has ONE address and those two belong to the `c` series.
        """
        for b in self._census(text):
            if (b["edit_start"], b["edit_end"]) == (edit_start, edit_end):
                return b
        raise AssertionError(f"no gap editing {edit_start}-{edit_end}")

    def test_adjacent_code_lines_give_an_EMPTY_range(self):
        # ! `n+1 .. n` -- `splice` assigns into an empty slice, which inserts.
        self.assertEqual(galley.splice_range(self._gap(self.FILE, 2, 1)), (2, 1))

    def test_a_prose_block_keeps_its_own_range(self):
        # ! A prose paragraph is REPLACED, so its edit range is its own lines.
        text = "a = 1\n# a note\nb = 2\n"
        paragraph = next(
            b.__dict__
            for b in lexer.paragraphs_stdlib(Path("m.py"), text)
            if b.kind == "comment"
        )
        self.assertEqual(galley.splice_range(paragraph), (2, 2))

    def test_the_insertion_lands_BETWEEN_the_two_code_lines(self):
        start, end = galley.splice_range(self._gap(self.FILE, 2, 1))
        out = galley.splice(self.FILE, [(start, end, 0, "# note")])
        self.assertEqual(out, "a = 1\n# note\nb = 2\nc = 3\n")

    def test_it_deletes_no_code(self):
        # !! The failure this range exists to avoid: `(1, 2)` would have
        # replaced BOTH bounding lines with the new prose.
        start, end = galley.splice_range(self._gap(self.FILE, 2, 1))
        out = galley.splice(self.FILE, [(start, end, 0, "# note")])
        for line in ("a = 1", "b = 2", "c = 3"):
            self.assertIn(line, out)

    def test_the_gap_ABOVE_the_first_code_line_inserts_above_it(self):
        # !! The file boundary. `start` and `end` are both clamped to 1 here,
        # so the address cannot say which side of line 1 the gap is on --
        # measured 2026-08-17, an `add` on it landed BELOW the anchor.
        out = galley.splice(
            self.FILE,
            [(*galley.splice_range(self._gap(self.FILE, 1, 0)), 0, "# header")],
        )
        self.assertEqual(out, "# header\na = 1\nb = 2\nc = 3\n")

    def test_the_gap_BELOW_the_last_code_line_appends(self):
        out = galley.splice(
            self.FILE,
            [(*galley.splice_range(self._gap(self.FILE, 4, 3)), 0, "# footer")],
        )
        self.assertEqual(out, "a = 1\nb = 2\nc = 3\n# footer\n")

    def test_the_two_boundary_gaps_of_a_ONE_LINE_file_differ(self):
        # !! Both address the same place -- neither holds a line of its own --
        # so only the edit range tells them apart.
        gaps = [b for b in self._census("a = 1\n") if b["kind"] == "interval"]
        self.assertEqual(len(gaps), 2)
        self.assertNotEqual(galley.splice_range(gaps[0]), galley.splice_range(gaps[1]))

    def test_an_empty_interval_MATCHES(self):
        lines = self.FILE.splitlines()
        self.assertTrue(galley.paragraph_matches(lines, self._gap(self.FILE, 2, 1)))

    def test_an_interval_spanning_a_blank_line_matches(self):
        text = "a = 1\n\nb = 2\n"
        self.assertTrue(
            galley.paragraph_matches(text.splitlines(), self._gap(text, 2, 2))
        )

    def test_an_interval_that_GAINED_prose_is_stale(self):
        # !! The staleness that matters for an `add`: the gap it says holds no
        # prose now holds some.
        text = "a = 1\n\nb = 2\n"
        gap = self._gap(text, 2, 2)
        grown = "a = 1\n# someone wrote this\nb = 2\n".splitlines()
        self.assertFalse(galley.paragraph_matches(grown, gap))

    def test_an_interval_past_the_end_of_the_file_is_stale(self):
        gap = dict(self._gap(self.FILE, 2, 1), start=3, end=9, edit_start=4, edit_end=8)
        self.assertFalse(galley.paragraph_matches(self.FILE.splitlines(), gap))


class TestADocstringBlockMatchesItsFile(unittest.TestCase):
    """`raw_lines` is the file's slice, so a docstring compares to itself.

    !! Measured 2026-08-17 before the census fix: on `galley.py`'s own census,
    all six docstring paragraphs answered False against an UNMODIFIED file and all
    five comment paragraphs answered True. A docstring edit could not be spliced at
    all, which blocked every re-review whose paragraph was a docstring.
    """

    SOURCE = '''def f():
    """One line.

    More prose.
    """
    return 1
'''

    def _census(self):
        return [b.__dict__ for b in lexer.paragraphs_stdlib(Path("m.py"), self.SOURCE)]

    def test_the_docstring_block_matches_the_source_it_came_from(self):
        paragraphs = [b for b in self._census() if b["kind"] == "docstring"]
        self.assertEqual(len(paragraphs), 1)
        self.assertTrue(
            galley.paragraph_matches(self.SOURCE.splitlines(), paragraphs[0])
        )

    def test_raw_lines_carries_the_delimiters(self):
        # ! The AST value has neither the opening `"""` nor its indent.
        paragraph = next(b for b in self._census() if b["kind"] == "docstring")
        self.assertTrue(paragraph["raw_lines"][0].lstrip().startswith('"""'))
        self.assertTrue(paragraph["raw_lines"][-1].strip().endswith('"""'))

    def test_lines_agrees_with_raw_lines(self):
        # ! They disagreed by one on every multi-line docstring: the AST value
        # has no closing-delimiter line.
        paragraph = next(b for b in self._census() if b["kind"] == "docstring")
        self.assertEqual(paragraph["lines"], len(paragraph["raw_lines"]))

    def test_an_EDITED_docstring_is_stale(self):
        paragraph = next(b for b in self._census() if b["kind"] == "docstring")
        edited = self.SOURCE.replace("More prose.", "Different prose.")
        self.assertFalse(galley.paragraph_matches(edited.splitlines(), paragraph))


class TestALineNobodyEditedKeepsItsEnding(unittest.TestCase):
    """`splice` joined split lines with ONE ending and rewrote the whole file.

    !! Measured 2026-08-18 on a mixed file: editing line 1 converted the
    untouched LF line 2 to CRLF, so the `git diff --no-index` stage 7a exists
    for showed both as changed. That is the diff noise `line_endings` says it
    prevents, arriving by the other route.
    """

    MIXED = "a\r\nb\nc\r\n"

    def test_editing_one_line_leaves_the_others_alone(self):
        self.assertEqual(galley.splice(self.MIXED, [(1, 1, 0, "A")]), "A\r\nb\nc\r\n")

    def test_the_edited_line_gets_the_files_ending(self):
        # ! A NEW line has no ending of its own, so `line_endings` decides it --
        # and deciding that is now the only thing it does.
        self.assertEqual(galley.splice(self.MIXED, [(2, 2, 0, "B")]), "a\r\nB\r\nc\r\n")

    def test_a_file_with_no_final_newline_still_has_none(self):
        self.assertEqual(galley.splice("a\nb", [(1, 1, 0, "A")]), "A\nb")

    def test_an_insertion_at_the_top_keeps_every_ending(self):
        self.assertEqual(galley.splice("a\r\nb\n", [(1, 0, 0, "T")]), "T\r\na\r\nb\n")


class TestTheColumnSaysWhereTheProseStarts(unittest.TestCase):
    """The `c` series is WRITABLE, and the column is what makes it so.

    !! ROY RULED IT, 2026-08-19: *"c needs to be writeable. It is the reason c
    is not an extension of b."* Until then a `c` paragraph was admitted by the join
    and refused by the galley, which discarded every other edit in that file
    with it.

    !! THE PARAGRAPHS COME FROM A REAL CENSUS. Hand-written ones passed while the
    shipped path failed: the fixture put the comment token alone in
    `raw_lines`, and `census.py` stores the whole physical line for a trailing
    comment -- so the suffix test that preceded this answered False on every
    real one, the galley spliced over the code, and the test said it would not.
    Measured 2026-08-18: a galley read `# reworded trailing` where
    `z = 3  # trailing` had been.
    """

    SOURCE = "def f():\n    z = 3  # trailing\n    return z\n"

    def _blocks(self, text=None):
        # ! ADDRESSED, because `unanswerable` refuses a census that carries no
        # address at all -- `--edits` keys by one, so such a census can key
        # nothing. `paragraphs_stdlib` alone leaves them empty, so the page's
        # own walk names them here.
        src = text or self.SOURCE
        built = lexer.paragraphs_stdlib(Path("m.py"), src)
        prose = [b.__dict__ for b in built]
        foliation = page.places_on(src, prose)
        for b in prose:
            b["address"] = f"m.py@{page.attach(b, foliation)}"
        return prose

    def _kind(self, kind, text=None):
        found = [b for b in self._blocks(text) if b["kind"] == kind]
        self.assertTrue(found, f"no {kind} in the census")
        return found[0]

    def test_the_column_is_the_END_OF_THE_CODE_not_the_hash(self):
        """!! Roy ruled it 2026-08-19: *"c addresses start at the end of the
        code on the line."*

        `    z = 3  # trailing` -- the statement ends at the 9th character, so
        the `c` place starts at the 10th. The `#` is at the 12th, and the two
        spaces between them belong to the `c` place, not to the code.

        ! It is a little opinionated, and it is the SAME opinion every
        formatter already holds: black and ruff normalise the gap before an
        inline comment to two spaces, `gofmt` aligns it, `cargo fmt` the same.
        Roy, 2026-08-19: *"it happens to be the same opinionatedness that also
        sits in all of the code formatters."*
        """
        paragraph = self._kind("trailing-comment")
        line = self.SOURCE.splitlines()[1]
        self.assertEqual(line[:9], "    z = 3")
        self.assertEqual(paragraph["edit_column"], 10)
        self.assertEqual(line[11], "#")

    def test_a_margin_and_a_trailing_comment_name_the_SAME_column(self):
        # !! Which is the point of measuring from the code. The room beside a
        # code line is one place whether or not prose is in it, so `add`ing a
        # trailing comment and `patch`ing one write to the same column.
        path = Path("m.py")
        bare = "def f():\n    z = 3\n    return z\n"
        margin = next(
            b.__dict__
            for b in page.page_for(path, bare, lexer.language_for(path))
            if b.kind == "margin" and b.start == 2
        )
        self.assertEqual(
            margin["edit_column"], self._kind("trailing-comment")["edit_column"]
        )

    def test_the_splice_keeps_the_code_and_replaces_the_prose(self):
        paragraph = self._kind("trailing-comment")
        out = galley.splice(
            self.SOURCE,
            [
                (
                    *galley.splice_range(paragraph),
                    paragraph["edit_column"],
                    "  # reworded",
                )
            ],
        )
        self.assertEqual(out, "def f():\n    z = 3  # reworded\n    return z\n")

    def test_the_REPLACEMENT_CARRIES_ITS_OWN_SEPARATOR(self):
        # !! The contract a writer works to, and it is the same one an `add` on
        # an `interval` already follows: the text carries its own leading
        # whitespace. Everything left of the `c` place -- the statement -- is
        # kept, and nothing else.
        paragraph = self._kind("trailing-comment")
        out = galley.splice(
            self.SOURCE,
            [(*galley.splice_range(paragraph), paragraph["edit_column"], "# no gap")],
        )
        self.assertIn("z = 3# no gap", out)

    def test_dropping_it_needs_no_special_case(self):
        # ! Because the kept head ends at the code, the separating whitespace
        # is already on the far side of it. Pointing the column at the `#`
        # instead left `    z = 3  ` behind and needed an rstrip to fix.
        paragraph = self._kind("trailing-comment")
        out = galley.splice(
            self.SOURCE,
            [(*galley.splice_range(paragraph), paragraph["edit_column"], "")],
        )
        self.assertEqual(out, "def f():\n    z = 3\n    return z\n")

    def test_a_margin_appends_because_its_column_is_past_the_line(self):
        # !! An `add` at a `c` place. The line is code to its end, so the
        # column is one past it and the prose supplies its own separator --
        # exactly as an `add` on an `interval` supplies its own indentation.
        text = "a = 1\n"
        path = Path("m.py")
        margin = next(
            b.__dict__
            for b in page.page_for(path, text, lexer.language_for(path))
            if b.kind == "margin"
        )
        self.assertEqual(margin["edit_column"], len("a = 1") + 1)
        out = galley.splice(
            text, [(*galley.splice_range(margin), margin["edit_column"], "  # why")]
        )
        self.assertEqual(out, "a = 1  # why\n")

    def test_a_block_owning_its_lines_still_loses_them_on_a_drop(self):
        # ! An empty head means the whole-line case, which is unchanged.
        text = "a = 1\n# a note\nb = 2\n"
        paragraph = next(
            b.__dict__
            for b in lexer.paragraphs_stdlib(Path("m.py"), text)
            if b.kind == "comment"
        )
        self.assertEqual(paragraph["edit_column"], 0)
        out = galley.splice(text, [(*galley.splice_range(paragraph), 0, "")])
        self.assertEqual(out, "a = 1\nb = 2\n")

    def test_a_trailing_comment_matches_its_file_ANYWAY(self):
        # !! Which is why the kind has to be asked. `paragraph_matches` passes --
        # the census stores the whole line -- so nothing downstream would have
        # stopped the splice.
        paragraph = self._kind("trailing-comment")
        self.assertTrue(galley.paragraph_matches(self.SOURCE.splitlines(), paragraph))

    def test_a_comment_on_its_own_line_owns_its_lines_whole(self):
        text = "def f():\n    # a note\n    return 1\n"
        paragraph = self._kind("comment", text)
        self.assertEqual(paragraph["edit_column"], 0)

    def test_a_docstring_owns_its_lines_whole(self):
        text = 'def f():\n    """A note."""\n    return 1\n'
        paragraph = self._kind("docstring", text)
        self.assertEqual(paragraph["edit_column"], 0)

    def test_a_census_without_the_field_is_REFUSED_not_defaulted(self):
        """!! Defaulting it put the deleted statement back.

        A trailing comment's stored text IS the file's whole line, so the
        staleness check passes it and nothing else would have stopped the
        write. The census is refused whole instead, before any paragraph is read.
        """
        paragraphs = self._blocks()
        self.assertIsNone(galley.unanswerable(paragraphs))
        for field in ("edit_column", "edit_start", "edit_end"):
            with self.subTest(field=field):
                stripped = [
                    {k: v for k, v in b.items() if k != field} for b in paragraphs
                ]
                problem = galley.unanswerable(stripped)
                self.assertIsNotNone(problem)
                self.assertIn(field, problem)


class TestTheGalleyWritesATrailingCommentEndToEnd(unittest.TestCase):
    """The CLI, because the unit answered correctly while the CLI deleted code."""

    SOURCE = "def f():\n    z = 3  # trailing\n    return z\n"

    def test_the_statement_survives_and_the_prose_is_replaced(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "m.py").write_text(self.SOURCE, encoding="utf-8")
            # ! ADDRESSED, as `census.py`'s own run loop does. A census from
            # `paragraphs_stdlib` alone carries no address and can key nothing.
            built = lexer.paragraphs_stdlib(Path("m.py"), self.SOURCE)
            paragraphs = [b.__dict__ for b in built]
            foliation = page.places_on(self.SOURCE, paragraphs)
            for b in paragraphs:
                b["address"] = f"m.py@{page.attach(b, foliation)}"
            at = next(
                b["address"] for b in paragraphs if b["kind"] == "trailing-comment"
            )
            # ! `default=list` -- a Paragraph holds a set field, and the shipped
            # writer converts it. The test only needs it readable back.
            (root / "c.json").write_text(
                json.dumps(paragraphs, default=list), encoding="utf-8"
            )
            (root / "e.json").write_text(
                json.dumps({at: "  # reworded trailing"}), encoding="utf-8"
            )
            code = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "galley.py"),
                    "--repo",
                    str(root),
                    "--census",
                    str(root / "c.json"),
                    "--edits",
                    str(root / "e.json"),
                    "--out",
                    str(root / "out"),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(code.returncode, 0, code.stdout)
            self.assertEqual(
                (root / "out" / "m.py").read_text(encoding="utf-8"),
                "def f():\n    z = 3  # reworded trailing\n    return z\n",
            )
            # ! Nothing under `--repo` is touched, whatever was written.
            self.assertEqual((root / "m.py").read_text(encoding="utf-8"), self.SOURCE)


class TestTheCSeriesIsWritableInALexicalLanguage(unittest.TestCase):
    """B3's point: Go, not just Python.

    !! IT WAS PYTHON ONLY. `paragraphs_lexical` cut `raw_lines` at the comment
    opener, so `paragraph_matches` refused every lexical trailing comment on a
    census seconds old -- one of eleven languages could have a `c` edit written.
    """

    SRC = "package math\n\nfunc Add(a, b int) int {\n\treturn a + b // adds them\n}\n"

    def _blocks(self):
        path = Path("m.go")
        got = page.page_for(path, self.SRC, lexer.language_for(path))
        sorted(page.code_lines(self.SRC, got))
        return [vars(b) for b in got]

    def _splice(self, kind, change):
        paragraph = next(b for b in self._blocks() if b["kind"] == kind)
        self.assertTrue(galley.paragraph_matches(self.SRC.splitlines(), paragraph))
        return galley.splice(
            self.SRC,
            [(*galley.splice_range(paragraph), paragraph["edit_column"], change)],
        )

    def test_a_patch_keeps_the_statement_AND_its_tab(self):
        out = self._splice("trailing-comment", " // sums them")
        self.assertIn("\treturn a + b // sums them", out)
        self.assertNotIn("adds them", out)

    def test_an_add_at_a_margin_lands_beside_the_code(self):
        out = self._splice("margin", " // the package clause")
        self.assertIn("package math // the package clause", out)

    def test_a_drop_leaves_the_statement_alone(self):
        out = self._splice("trailing-comment", "")
        self.assertIn("\treturn a + b\n", out)
        self.assertNotIn("adds them", out)
