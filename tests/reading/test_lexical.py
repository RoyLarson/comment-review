"""What the generic lexical reader hands the page: its paragraphs and code lines."""

from pathlib import Path

import pytest

from comment_review.reading.diagnostics import ReadFailure
from comment_review.reading.language import language_for
from comment_review.reading.lexer import LexicalRead, declarations
from comment_review.reading.readers import read_source
from comment_review.reading.series import Kind
from comment_review.reading.source import CodeLine, DocPlace

GO = (
    "package m\n"
    "\n"
    "// F does a thing.\n"
    "func F() { // why\n"
    "\t/* inside\n"
    "\t   still */\n"
    "}\n"
)


def read(name: str, text: str) -> LexicalRead:
    result = read_source(Path(name), text)
    assert isinstance(result, LexicalRead)
    return result


def test_the_code_lines_carry_code_and_the_documentation_place():
    # Line 4 declares and keeps its code beside the trailing comment; lines 5-6
    # are a block comment and hold no code.
    assert read("m.go", GO).code_lines() == [
        CodeLine(1, "package m", None),
        CodeLine(4, "func F() {", DocPlace(4, True)),
        CodeLine(7, "}", None),
    ]


def test_each_call_hands_back_a_new_list():
    lexical = read("m.go", GO)
    first = lexical.paragraphs(Path("m.go"))
    first.clear()
    assert lexical.paragraphs(Path("m.go"))


def test_the_run_above_a_declaration_documents_its_declaring_line():
    found = read("m.go", GO).paragraphs(Path("m.go"))
    assert [(p.start, p.kind, p.anchor_line) for p in found] == [
        (3, Kind.DOCSTRING, 4),
        (4, Kind.TRAILING, None),
        (5, Kind.COMMENT, None),
    ]


def test_a_doc_run_that_documents_no_declaration_is_a_comment():
    # `/** two */` is held off `function f` by code, so it documents nothing.
    text = "/** one */\nfunction f() {}\nlet x = 1;\n/** two */\nlet y = 2;\n"
    found = read("m.js", text).paragraphs(Path("m.js"))
    assert [(p.start, p.kind, p.anchor_line) for p in found] == [
        (1, Kind.DOCSTRING, 2),
        (4, Kind.COMMENT, None),
    ]


def kinds(name: str, text: str) -> list[tuple[int, int, str]]:
    found = read(name, text).paragraphs(Path(name))
    return [(p.start, p.end, p.kind) for p in found]


def test_a_closing_comment_with_a_blank_line_inside_is_one_matter_run():
    text = "import a.b;\n/* a\n\n b */\n"
    assert kinds("m.java", text) == [(2, 4, Kind.MATTER)]


def test_a_closing_doc_run_documenting_nothing_is_the_modules_at_eof():
    found = read("m.java", "import a.b;\n/** x */\n").paragraphs(Path("m.java"))
    assert [(p.start, p.end, p.kind, p.anchor) for p in found] == [
        (2, 2, Kind.DOCSTRING, "<eof>")
    ]


def test_an_opening_doc_run_ends_at_its_last_doc_marked_line():
    # `val` declares nothing here, so the run documents nothing: the module's
    # docstring is line 1, and the comment after the empty line is ordinary.
    text = "/** x */\n\n// y\nval z = 1\n"
    found = read("m.kt", text).paragraphs(Path("m.kt"))
    assert [(p.start, p.end, p.kind, p.anchor_line) for p in found] == [
        (1, 1, Kind.DOCSTRING, None),
        (3, 3, Kind.COMMENT, None),
    ]


def test_an_opening_doc_run_on_line_one_of_c_is_the_modules():
    found = read("m.c", "/** x */\nint y;\n").paragraphs(Path("m.c"))
    assert [(p.start, p.kind, p.anchor_line) for p in found] == [
        (1, Kind.DOCSTRING, None)
    ]


def test_a_comment_on_line_one_of_sql_is_front_matter():
    assert kinds("m.sql", "-- x\nselect 1;\n") == [(1, 1, Kind.MATTER)]


def test_a_licence_header_is_not_part_of_the_declarations_documentation():
    text = "// licence\n\n// doc\nfun f() {}\n"
    assert kinds("m.kt", text) == [(1, 1, Kind.MATTER), (3, 3, Kind.DOCSTRING)]


def test_kt_and_rs_hand_back_matter_on_the_same_runs_for_a_licence_then_an_import():
    # The code after the licence declares nothing in either language: where a
    # comment documents a declaration is each reader's own rule.
    kotlin = "// licence\n// more\n\nimport a.b\n\n// tail one\n\n// tail two\n"
    rust = "// licence\n// more\n\nuse a::b;\n\n// tail one\n\n// tail two\n"
    expected = [(1, 2, Kind.MATTER), (6, 6, Kind.COMMENT), (8, 8, Kind.MATTER)]
    assert kinds("m.kt", kotlin) == expected
    rust_read = read_source(Path("m.rs"), rust)
    assert not isinstance(rust_read, ReadFailure)
    found = rust_read.paragraphs(Path("m.rs"))
    assert not isinstance(found, ReadFailure)
    assert [(p.start, p.end, p.kind) for p in found] == expected


@pytest.mark.parametrize(
    ("name", "text", "a_series"),
    [
        ("m.go", GO, True),
        ("m.c", "int x; // n\n", True),
        ("m.sql", "select 1; -- n\n", False),
    ],
    ids=["keywords", "doc-markers-alone", "neither"],
)
def test_a_language_has_an_a_series_when_it_documents_at_all(name, text, a_series):
    assert read(name, text).a_series is a_series


def test_a_lexical_read_can_hold_a_closing_docstring():
    assert read("m.java", "import a.b;\n/** x */\n").closing_docstring is True


def test_declarations_hold_only_the_declaring_lines():
    go = language_for(Path("m.go"))
    assert go is not None
    assert declarations(go, {1: "package m", 3: "func f() {}"}) == {
        3: DocPlace(3, True)
    }
