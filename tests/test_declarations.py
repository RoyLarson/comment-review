"""Which languages have an `a` series, and which lines declare one.

Roy, 2026-08-20: *"we need to be able to distinguish `a` foliations for as many
languages as there are `a` possible foliations. yaml, toml are not ones. The
easy way to do that is to supply the lexer with the list of keywords that a
language/practice uses to say this can get a docstring."*
"""

import ast
import sys
import unittest
from pathlib import Path

SCRIPTS = (
    Path(__file__).resolve().parents[1]
    / "plugins/comment-review/skills/comment-review/scripts"
)
sys.path.insert(0, str(SCRIPTS))

import lexer  # noqa: E402
import page  # noqa: E402


def places(name: str, text: str) -> list[str]:
    """The folios on this file, in series order."""
    p = Path(name)
    pg = page.page_for(p, text, lexer.language_for(p))
    return sorted(pg.foliation.places, key=lambda f: (f[0], int(f[1:])))


def a_places(name: str, text: str) -> list[tuple[str, str]]:
    """`(folio, anchor)` for every `a` on this file, in SERIES order.

    ! SORTED ON THE FOLIO'S OWN NUMBER, which is what the walk counted. Iterating
    the page gives the order its PARAGRAPHS are listed in -- `Page.paragraphs` is
    sorted on the lines a paragraph covers -- and an empty place covers none, so
    it sorts ahead of every filled one. That is a fact about the prose list and
    not about the foliation, which never reads a line number to number a place.
    The two orders agreed only while no `a` outside Python was ever filled.
    """
    p = Path(name)
    got = [
        (b.address.split("@")[-1], b.anchor)
        for b in page.page_for(p, text, lexer.language_for(p))
        if b.address.split("@")[-1].startswith("a")
    ]
    return sorted(got, key=lambda f: int(f[0][1:]))


class TestALanguageWithNoDocstringPracticeHasNoASeries(unittest.TestCase):
    """Not an EMPTY `a` series -- none at all.

    ! A place nothing can ever fill is worse than no place: `undocumented` is
    what an `add` cites, so a YAML `a0` invited a verdict proposing a module
    docstring for a language that has no such thing.
    """

    def test_yaml_has_no_a_at_all(self):
        got = places("x.yaml", "# a note\nname: thing\nitems:\n  - one\n")
        self.assertEqual([f for f in got if f.startswith("a")], [])

    def test_toml_has_no_a_at_all(self):
        got = places("y.toml", "# a note\n[table]\nkey = 1\n")
        self.assertEqual([f for f in got if f.startswith("a")], [])

    def test_it_still_has_its_b_and_c_places(self):
        # ! The other two series are unaffected: every line of a YAML file is
        # still code with room beside it, and still has gaps between.
        got = places("x.yaml", "# a note\nname: thing\n")
        self.assertTrue([f for f in got if f.startswith("b")])
        self.assertTrue([f for f in got if f.startswith("c")])

    def test_c_and_cpp_are_left_out_deliberately(self):
        # !! A RULING, not an oversight. Roy, 2026-08-20: *"leave it out because
        # it is ambiguous in every way."* A C function opens with its RETURN
        # TYPE, and completing that list means knowing every type the program
        # defines.
        self.assertEqual(lexer.language_for(Path("m.c")).declares, ())
        self.assertEqual(lexer.language_for(Path("m.cpp")).declares, ())
        got = places("m.c", "int a = 1;\nint f(void) { return a; }\n")
        self.assertEqual([f for f in got if f.startswith("a")], [])


class TestTheKeywordListResolvesDeclarations(unittest.TestCase):
    """The lexer matches the language's own keywords -- no parser, no LSP."""

    def test_rust_declares_by_keyword(self):
        got = a_places(
            "z.rs", "/// doc\nfn one() {}\n\npub struct S {\n    x: i32,\n}\n"
        )
        self.assertEqual(
            got, [("a0", "<module>"), ("a1", "fn one() {}"), ("a2", "pub struct S {")]
        )

    def test_go_declares_by_keyword(self):
        got = a_places("g.go", "package main\n\nfunc One() {}\n\ntype T struct{}\n")
        # ! `package` is NOT a declaration: Go's package comment IS `a0`.
        self.assertEqual(
            got,
            [("a0", "<module>"), ("a1", "func One() {}"), ("a2", "type T struct{}")],
        )

    def test_the_anchor_is_the_declaring_line_verbatim(self):
        got = a_places("z.rs", "pub fn wrapped(\n    x: i32,\n) -> i32 { x }\n")
        self.assertEqual(got[1], ("a1", "pub fn wrapped("))


def folio_of(name: str, text: str, line: int) -> str:
    """The folio the paragraph STARTING on this line was tied to."""
    p = Path(name)
    for b in page.page_for(p, text, lexer.language_for(p)):
        if b.original_start == line:
            return b.address.split("@")[-1]
    return ""


class TestTheAPlaceIsFilledOutsidePython(unittest.TestCase):
    """The lexer-to-paragraph junction: prose above a declaration takes its `a`.

    Wired 2026-08-21. `Paragraph.declares` was stated only by `paragraphs_stdlib`,
    so `attach` fell past its first branch for every language whose `a` comes
    from a keyword and every doc comment took the `b` for the gap it sat in.
    """

    def test_a_doc_comment_flush_against_the_declaration_takes_its_a(self):
        self.assertEqual(folio_of("z.rs", "/// The name.\npub fn f() {}\n", 1), "a1")

    def test_a_BLANK_LINE_between_does_not_break_the_tie(self):
        # !! MEASURED on CPython v3.13.1: 1,124 of 2,987 documented declarations
        # (38%) leave a blank line before the declaring line. An adjacency test
        # would abandon every one of them in `b`.
        # ! `package thing` opens the file so the doc comment is not on LINE 1,
        # where a run is the file's own matter since 2026-08-21.
        text = "package thing\n\n// One does it.\n\nfunc One() {}\n"
        self.assertEqual(folio_of("g.go", text, 3), "a1")

    def test_prose_above_a_line_of_CODE_documents_the_code_not_the_next_one(self):
        # ! The walk back stops at code: this comment sits above `func One`, and
        # `func Two` two lines below has no documentation at all.
        text = "package thing\n\n// One does it.\nfunc One() {}\nfunc Two() {}\n"
        self.assertEqual(folio_of("g.go", text, 3), "a1")

    def test_the_NEAREST_paragraph_above_takes_it_and_the_header_keeps_its_gap(self):
        # !! THE COLLISION THIS CLOSES. Both paragraphs used to answer to `b0`,
        # and `record.entry_for` returns the FIRST -- so a correct edit to the
        # doc comment was checked against the licence header and refused.
        #
        # ! The header takes `f0` rather than `b0` since 2026-08-21: it documents
        # nothing, so it is the file's own matter. `package` is not in Go's
        # `declares`. Either way the two are separate places, which is the point.
        text = (
            "// Copyright 2001.\npackage thing\n\n// Name returns it.\nfunc Name() {}\n"
        )
        self.assertEqual(folio_of("g.go", text, 1), "f0")
        self.assertEqual(folio_of("g.go", text, 4), "a1")

    def test_a_TRAILING_comment_is_beside_its_line_and_never_documents(self):
        # ! It states a column, and its line is a line of code.
        self.assertEqual(folio_of("g.go", "func One() {} // note\n", 1), "c0")

    def test_a_language_with_no_keyword_list_ties_nothing(self):
        # ! C is deliberately empty -- see `test_c_and_cpp_are_left_out...`. The
        # junction cannot invent an `a` for a language that has no `a` series, so
        # `/* Adds. */` documents nothing THE PAGE CAN SEE and becomes the file's
        # own matter. ! That is the C licence-header case working for the first
        # time: it took `b0` and was editable work until 2026-08-21.
        self.assertEqual(
            folio_of("m.c", "/* Adds. */\nint add(int a) { return a; }\n", 1), "f0"
        )

    def test_a_SECOND_run_is_not_matter_even_when_the_first_is(self):
        # ! Only the head run is the file's. A licence, a blank, then a doc
        # comment: the second documents the declaration below it and takes its
        # `a`, which is the collision `two-paragraphs-one-address` measured.
        text = "// Copyright 2001.\n\n/// The name.\npub fn name() {}\n"
        self.assertEqual(folio_of("z.rs", text, 1), "f0")
        self.assertEqual(folio_of("z.rs", text, 3), "a1")


class TestTheMatchIsOnTheFIRSTWORDNeverASubstring(unittest.TestCase):
    """`deffered = 1` is not a `def`, and `x = my_func()` declares nothing."""

    def test_a_word_merely_starting_with_a_keyword_does_not_declare(self):
        self.assertFalse(lexer._declares_here("deffered = 1", ("def",)))
        self.assertFalse(lexer._declares_here("funcs = []", ("func",)))

    def test_a_keyword_inside_the_line_does_not_declare(self):
        self.assertFalse(lexer._declares_here("x = my_func()", ("func",)))
        self.assertFalse(lexer._declares_here("    return fn(a)", ("fn",)))

    def test_indentation_does_not_hide_the_keyword(self):
        self.assertTrue(lexer._declares_here("        fn inner() {}", ("fn",)))

    def test_a_trailing_bang_is_part_of_the_word(self):
        self.assertTrue(lexer._declares_here("macro_rules! thing {", ("macro_rules!",)))

    def test_a_TWO_WORD_keyword_is_matched_as_two_words(self):
        # ! Lua: bare `local` opens a variable, `local function` opens a
        # function. Only the pair declares.
        self.assertTrue(
            lexer._declares_here("local function f()", ("function", "local function"))
        )
        self.assertFalse(
            lexer._declares_here("local x = 1", ("function", "local function"))
        )


class TestEachLanguageCarriesItsOwnList(unittest.TestCase):
    """Roy, 2026-08-20, on why the grouped rows were split.

    *"Don't try to make the list generic -- that is a failure of the single
    responsibility principle. Each language could change on a new version
    invalidating the list for all of them. Better an explicit precise list with
    duplicated words than an implicit word set hoping to catch each."*
    """

    def test_javascript_and_typescript_are_separate_records(self):
        js = lexer.language_for(Path("a.js"))
        ts = lexer.language_for(Path("a.ts"))
        self.assertNotEqual(js.name, ts.name)
        # ! TypeScript's list is a superset TODAY. It is written out rather than
        # derived, so a TypeScript release cannot change JavaScript's answer.
        self.assertIn("interface", ts.declares)
        self.assertNotIn("interface", js.declares)

    def test_the_c_family_row_is_split_per_language(self):
        names = {
            ext: lexer.language_for(Path(f"a{ext}")).name
            for ext in (".c", ".cpp", ".java", ".cs", ".swift", ".kt")
        }
        self.assertEqual(len(set(names.values())), 6, names)

    def test_no_extension_is_claimed_by_two_languages(self):
        seen: dict[str, str] = {}
        for lang in lexer.LANGUAGES:
            for ext in lang.extensions:
                self.assertNotIn(ext, seen, f"{ext}: {seen.get(ext)} and {lang.name}")
                seen[ext] = lang.name

    def test_every_row_STATES_its_own_quotes(self):
        """A row that says nothing takes the dataclass default, which is inheriting.

        !! 15 OF 18 ROWS INHERITED `('"', "'")` AND NOBODY HAD DECIDED IT. Roy,
        2026-08-22, stating the rule explicitly for the second time: *"every
        language gets its own definition requirements in the file. No language
        ever inherits from the `a` family ... every language gets all of the
        definitions necessary to parse it specifically, because anything else is
        failing the SRP rules."*

        ! IT WAS WRONG FOR AT LEAST TWO. INI has no string quoting at all, so
        `name = Roy's config ; a trailing comment` censused with NO prose -- the
        apostrophe opened a literal that swallowed the comment. Swift has no
        character literal, so its `'` had nothing to open either.

        ! THE TEST READS THE SOURCE, not the objects. Every row's `quotes`
        attribute is populated at runtime whether it was stated or defaulted, so
        only the text can tell a decision from an inheritance.
        """
        source = (SCRIPTS / "language.py").read_text(encoding="utf-8")
        rows = [
            node
            for node in ast.walk(ast.parse(source))
            if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "Language"
        ]
        # ! Guards the guard: if the walk stops finding rows, the check below
        # passes by having nothing to look at.
        self.assertEqual(len(rows), len(lexer.LANGUAGES))
        silent = [
            node.args[0].value
            for node in rows
            if isinstance(node.args[0], ast.Constant)
            and not any(kw.arg == "quotes" for kw in node.keywords)
        ]
        self.assertEqual(silent, [])

    def test_every_doc_opener_is_listed_as_a_comment_opener_LONGEST_FIRST(self):
        # !! THE TABLE'S OWN RULE, and nothing checked it until 2026-08-20: a
        # doc opener that is not in `line_comment` is cut by the SHORTER
        # opener, and the remainder lands in the prose. Measured when C# and
        # Swift were split out with `("//",)` alone: `/// <summary>x</summary>`
        # was censused as `/ <summary>x</summary>`, one slash into the text.
        for lang in lexer.LANGUAGES:
            with self.subTest(lang=lang.name):
                for opener in lang.doc_line:
                    self.assertIn(opener, lang.line_comment)
                self.assertEqual(
                    list(lang.line_comment),
                    sorted(lang.line_comment, key=len, reverse=True),
                    f"{lang.name}: openers must be longest-first",
                )

    def test_a_doc_marked_run_keeps_none_of_its_marker(self):
        # ! The text a reviewer reads is the PROSE, not the syntax that marked
        # it. One case per line-comment doc marker in the table.
        for name, text in (
            ("a.rs", "/// The one doc.\nfn one() {}\n"),
            ("a.cs", "/// The one doc.\npublic void One() {}\n"),
            ("a.swift", "/// The one doc.\nfunc one() {}\n"),
        ):
            with self.subTest(name=name):
                p = Path(name)
                doc = next(
                    b
                    for b in page.page_for(p, text, lexer.language_for(p))
                    if b.kind == "docstring"
                )
                self.assertEqual(doc.text.strip(), "The one doc.")

    def test_only_python_puts_its_doc_INSIDE_the_declaration(self):
        inside = [lang.name for lang in lexer.LANGUAGES if lang.doc_inside]
        self.assertEqual(inside, ["python"])

    def test_a_language_with_declares_reaches_the_a_series_and_one_without_does_not(
        self,
    ):
        for lang in lexer.LANGUAGES:
            with self.subTest(lang=lang.name):
                decls = lexer.declarations("", lang, {})
                self.assertEqual(bool(decls), bool(lang.declares))
