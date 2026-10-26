"""What the generic lexical reader hands the page: its paragraphs and code lines."""

from pathlib import Path

import pytest
from conftest import kinds

from comment_review.reading.language import Language, language_for
from comment_review.reading.lexer import LexicalRead, declarations, leading_between
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


def test_a_closing_comment_with_a_blank_line_inside_is_one_matter_run():
    text = "import a.b;\n/* a\n\n b */\n"
    assert kinds("m.java", text) == [(2, 4, Kind.MATTER)]


def test_a_closing_doc_run_documenting_nothing_is_the_modules_at_eof():
    found = read("m.java", "import a.b;\n/** x */\n").paragraphs(Path("m.java"))
    assert [(p.start, p.end, p.kind, p.anchor) for p in found] == [
        (2, 2, Kind.DOCSTRING, "<eof>")
    ]


@pytest.mark.parametrize(
    ("text", "doc_line"),
    [
        ("fun f() {}\n\n// note\n/** foot doc */\n", 4),
        ("fun f() {}\n\n// note\n\n/** foot doc */\n", 5),
    ],
    ids=["flush", "blank-between"],
)
def test_a_closing_doc_run_starts_at_its_first_doc_marked_line(text, doc_line):
    # The foot mirrors the head: the comment above the closing docstring stays
    # an ordinary comment, and the docstring is the module's at `<eof>`.
    found = read("m.kt", text).paragraphs(Path("m.kt"))
    assert [(p.start, p.end, p.kind, p.anchor) for p in found] == [
        (3, 3, Kind.COMMENT, ""),
        (doc_line, doc_line, Kind.DOCSTRING, "<eof>"),
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


@pytest.mark.parametrize("name", ["m.js", "m.ts"])
@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (
            "#!/usr/bin/env node\nfunction f() {}\n",
            [(1, 1, Kind.MATTER, ["#!/usr/bin/env node"])],
        ),
        (
            "#!/usr/bin/env node\n// Licence MIT\n\nlet x = 1;\n",
            [(1, 2, Kind.MATTER, ["#!/usr/bin/env node", "// Licence MIT"])],
        ),
        (
            "#!/usr/bin/env node\n\n// note\nlet x = 1;\n",
            [
                (1, 1, Kind.MATTER, ["#!/usr/bin/env node"]),
                (3, 3, Kind.COMMENT, ["// note"]),
            ],
        ),
    ],
    ids=["alone", "with-front-matter", "blank-after"],
)
def test_a_shebang_is_the_files_matter_and_the_matter_rule_opens_below_it(
    name, text, expected
):
    lexical = read(name, text)
    found = lexical.paragraphs(Path(name))
    assert [(p.start, p.end, p.kind, p.raw_lines) for p in found] == expected
    assert 1 not in [c.line for c in lexical.code_lines()]


def test_a_shebang_does_not_document_the_declaration_below_it():
    found = read("m.js", "#!/usr/bin/env node\nfunction f() {}\n").paragraphs(
        Path("m.js")
    )
    assert [(p.kind, p.anchor_line) for p in found] == [(Kind.MATTER, None)]


def test_a_row_without_a_shebang_reads_hash_bang_as_its_language_does():
    # Go names no shebang, so `#!` on line 1 is code.
    lexical = read("m.go", "#!/x\npackage p\n")
    assert lexical.paragraphs(Path("m.go")) == []
    assert [c.line for c in lexical.code_lines()] == [1, 2]


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


@pytest.mark.parametrize(
    ("name", "closing"),
    [
        ("m.java", True),
        ("m.swift", True),
        ("m.go", False),
        ("m.rb", False),
        ("m.sh", False),
        ("m.lua", False),
        ("m.sql", False),
    ],
    ids=["doc-block", "doc-line-and-block", "go", "ruby", "shell", "lua", "neither"],
)
def test_a_lexical_read_holds_a_closing_docstring_when_its_row_has_a_doc_marker(
    name, closing
):
    assert read(name, "x\n").closing_docstring is closing


@pytest.mark.parametrize(
    ("doc_line", "doc_block", "declares", "closing"),
    [
        (("///",), (), (), True),
        ((), ("/**",), (), True),
        ((), (), ("def",), False),
        ((), (), (), False),
    ],
    ids=["doc-line", "doc-block", "keywords-alone", "neither"],
)
def test_a_row_holds_a_closing_docstring_when_it_has_a_doc_marker(
    doc_line, doc_block, declares, closing
):
    row = Language(
        "x",
        (".x",),
        ("//",),
        doc_line=doc_line,
        doc_block=doc_block,
        declares=declares,
    )
    assert row.closing_docstring is closing


def test_a_blank_looking_line_the_reader_gave_as_code_is_not_leading():
    text = "a\n\u00a0\nb\n"
    assert leading_between([], text, [1, 2, 3]) == []
    assert [(p.start, p.end) for p in leading_between([], text, [1, 3])] == [(2, 2)]


def test_a_byte_order_mark_before_a_line_comment_is_not_code():
    found = read("m.js", "\ufeff// Licence MIT\nconst x = 1;\n").paragraphs(
        Path("m.js")
    )
    assert [(p.start, p.kind, p.anchor, p.raw_lines) for p in found] == [
        (1, Kind.MATTER, "<module>", ["\ufeff// Licence MIT"])
    ]
    assert found[0].text == "Licence MIT"


def test_a_byte_order_mark_before_code_stays_in_the_anchor_of_a_trailing_comment():
    found = read("m.js", "\ufeffconst x = 1; // why\n").paragraphs(Path("m.js"))
    assert [(p.kind, p.anchor, p.raw_lines) for p in found] == [
        (Kind.TRAILING, "\ufeffconst x = 1;", [" // why"])
    ]


def test_a_byte_order_mark_before_a_shebang_keeps_the_shebang_as_matter():
    found = read("m.js", "\ufeff#!/usr/bin/env node\nconst x = 1;\n").paragraphs(
        Path("m.js")
    )
    assert [(p.kind, p.raw_lines) for p in found] == [
        (Kind.MATTER, ["\ufeff#!/usr/bin/env node"])
    ]


def test_declarations_hold_only_the_declaring_lines():
    go = language_for(Path("m.go"))
    assert go is not None
    assert declarations(go, {1: "package m", 3: "func f() {}"}) == {
        3: DocPlace(3, True)
    }
