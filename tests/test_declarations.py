"""Which languages have an `a` series, and which lines declare one.

Roy, 2026-08-20: *"we need to be able to distinguish `a` foliations for as many
languages as there are `a` possible foliations. yaml, toml are not ones. The
easy way to do that is to supply the lexer with the list of keywords that a
language/practice uses to say this can get a docstring."*
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parents[1]
        / "plugins/comment-review/skills/comment-review/scripts"
    ),
)

import lexer  # noqa: E402
import page  # noqa: E402


def places(name: str, text: str) -> list[str]:
    """The folios on this file, in series order."""
    p = Path(name)
    pg = page.page_for(p, text, lexer.language_for(p))
    return sorted(pg.foliation.places, key=lambda f: (f[0], int(f[1:])))


def a_places(name: str, text: str) -> list[tuple[str, str]]:
    """`(folio, anchor)` for every `a` on this file."""
    p = Path(name)
    return [
        (b.address.split("@")[-1], b.anchor)
        for b in page.page_for(p, text, lexer.language_for(p))
        if b.address.split("@")[-1].startswith("a")
    ]


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
