"""What the generic lexical reader hands the page: its paragraphs and code lines."""

from pathlib import Path

import pytest

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


@pytest.mark.parametrize(
    ("name", "text", "a_series"),
    [("m.go", GO, True), ("m.c", "int x; // n\n", False)],
)
def test_a_language_with_no_declaring_keyword_has_no_a_series(name, text, a_series):
    assert read(name, text).a_series is a_series


def test_declarations_hold_only_the_declaring_lines():
    go = language_for(Path("m.go"))
    assert go is not None
    assert declarations(go, {1: "package m", 3: "func f() {}"}) == {
        3: DocPlace(3, True)
    }
