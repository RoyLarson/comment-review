"""What the generic lexical reader hands the page: its paragraphs and code lines."""

from pathlib import Path

import pytest
from conftest import kinds
from helpers import GO, LEXICAL_INPUTS

from comment_review.reading.language import Language, language_for
from comment_review.reading.lexer import LexicalRead, declarations, leading_between
from comment_review.reading.readers import read_source
from comment_review.reading.series import Kind
from comment_review.reading.source import CodeLine, DocPlace


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


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("/** one */\n", [(1, 1, Kind.DOCSTRING, "")]),
        ("/** one */\n/** two */\n", [(1, 2, Kind.DOCSTRING, "")]),
        ("/** one */\n\n/** two */\n", [(1, 3, Kind.DOCSTRING, "")]),
        ("\n/** one */\n", [(2, 2, Kind.DOCSTRING, "")]),
        (
            "// licence\n\n/** one */\n",
            [(1, 1, Kind.MATTER, "<module>"), (3, 3, Kind.DOCSTRING, "")],
        ),
        (
            "// licence\n\n/** one */\n// note\n/** two */\n",
            [
                (1, 1, Kind.MATTER, "<module>"),
                (3, 3, Kind.DOCSTRING, ""),
                (4, 4, Kind.COMMENT, ""),
                (5, 5, Kind.DOCSTRING, "<eof>"),
            ],
        ),
        (
            "/** one */\n// note\n\n// more\n/** two */\n",
            [
                (1, 1, Kind.DOCSTRING, ""),
                (2, 4, Kind.COMMENT, ""),
                (5, 5, Kind.DOCSTRING, "<eof>"),
            ],
        ),
    ],
    ids=[
        "one",
        "two-flush",
        "two-apart",
        "blank-above",
        "blank-below-matter",
        "comment-between",
        "comments-between",
    ],
)
def test_with_no_code_the_docs_at_the_top_are_the_modules_until_a_comment(
    text, expected
):
    # The one run is both the head and the foot. The docs at its top are the
    # module's `a0`; a comment in it ends them, and the docs below its last
    # comment are the `<eof>` `a`.
    found = read("m.js", text).paragraphs(Path("m.js"))
    assert [(p.start, p.end, p.kind, p.anchor) for p in found] == expected


DOC = Kind.DOCSTRING
NOTE = Kind.COMMENT


@pytest.mark.parametrize(
    ("name", "text", "expected"),
    [
        (
            *LEXICAL_INPUTS["two-runs/two-runs-above-a-declaration"],
            [(2, 5, NOTE, "", None), (6, 6, DOC, "", 7)],
        ),
        (
            *LEXICAL_INPUTS["two-runs/two-runs-above-plain-code"],
            [(2, 4, NOTE, "", None)],
        ),
        (
            *LEXICAL_INPUTS["two-runs/plain-groups-facing"],
            [(2, 3, NOTE, "", None), (4, 4, DOC, "", 5)],
        ),
        (
            *LEXICAL_INPUTS["two-runs/doc-groups-facing-mid-file"],
            [(2, 3, NOTE, "", None), (4, 4, DOC, "", 5)],
        ),
        (
            *LEXICAL_INPUTS["two-runs/doc-groups-facing-at-the-head"],
            [(1, 2, DOC, "", None), (3, 3, DOC, "", 4)],
        ),
        (
            *LEXICAL_INPUTS["two-runs/lua"],
            [(2, 3, NOTE, "", None), (4, 4, DOC, "", 5)],
        ),
        (
            *LEXICAL_INPUTS["two-runs/blank-between-the-runs"],
            [(2, 3, NOTE, "", None), (5, 5, DOC, "", 6)],
        ),
    ],
    ids=[
        "two-runs-above-a-declaration",
        "two-runs-above-plain-code",
        "plain-groups-facing",
        "doc-groups-facing-mid-file",
        "doc-groups-facing-at-the-head",
        "lua",
        "blank-between-the-runs",
    ],
)
def test_a_gap_holding_two_runs_has_one_b(name, text, expected):
    # A delimited comment closing on a line that holds code leaves that line
    # out of the code, so the run below it is in the same gap and joins its b.
    # A group never crosses from one run into the next, so the lower edge's
    # `a` stays inside the last run and `a0` inside the first.
    found = read(name, text).paragraphs(Path(name))
    got = [(p.start, p.end, p.kind, p.anchor, p.anchor_line) for p in found]
    assert [row for row in got if row[2] != Kind.TRAILING] == expected


ROYS_CASE = "// M1\n/** D1 */\n// C1\n/** D2 */\n// C2\n/** D3 */\n// C3\n"


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (
            ROYS_CASE,
            [
                (1, 1, Kind.MATTER, "<module>"),
                (2, 2, DOC, ""),
                (3, 7, Kind.MATTER, "<module>"),
            ],
        ),
        (
            ROYS_CASE + "\n",
            [(1, 1, Kind.MATTER, "<module>"), (2, 2, DOC, ""), (3, 7, NOTE, "")],
        ),
    ],
    ids=["back-matter", "blank-last-line"],
)
def test_each_place_holds_one_paragraph_and_the_rest_is_one_b_or_the_back_matter(
    text, expected
):
    # Past a0, the gap's comments and docs are one paragraph: the back matter
    # when they reach the last line, the gap's b when a blank line ends it.
    found = read("m.js", text).paragraphs(Path("m.js"))
    assert [(p.start, p.end, p.kind, p.anchor) for p in found] == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (
            "let x = 1;\n/** D1 */\n// C1\n",
            [(2, 2, DOC, "<eof>"), (3, 3, Kind.MATTER, "<module>")],
        ),
        (
            "let x = 1;\n/** D1 */\n// C1\n/** D2 */\n// C2\n",
            [(2, 2, DOC, "<eof>"), (3, 5, Kind.MATTER, "<module>")],
        ),
        ("let x = 1;\n/** D1 */\n// C1\n\n", [(2, 3, NOTE, "")]),
        ("let x = 1;\n/** D1 */\n// C1\n/** D2 */\n// C2\n\n", [(2, 5, NOTE, "")]),
    ],
    ids=["one-comment", "comments-and-docs", "one-comment-blank", "comments-blank"],
)
def test_a_closing_docstring_below_code_keeps_its_a_above_the_back_matter(
    text, expected
):
    # The doc that ends the file's code is the module's `<eof>` `a`, and every
    # comment below it is back matter, one paragraph. With a blank last line
    # there is no back matter, and the gap's prose is its one b.
    found = read("m.js", text).paragraphs(Path("m.js"))
    got = [(p.start, p.end, p.kind, p.anchor) for p in found]
    assert [row for row in got if row[2] != Kind.TRAILING] == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (
            "/** A */\n// n1\n/** B */\n// n2\n/** C */\n",
            [(1, 1, DOC, "", None), (2, 4, NOTE, "", None), (5, 5, DOC, "<eof>", None)],
        ),
        (
            "/** A */\n// note\n/** B */\nfunction f() {}\n",
            [(1, 1, DOC, "", None), (2, 2, NOTE, "", None), (3, 3, DOC, "", 4)],
        ),
        (
            "/** doc */\n// eslint-disable-next-line\nfunction f() {}\n",
            [(1, 1, DOC, "", None), (2, 2, DOC, "", 3)],
        ),
        (
            "let x = 1;\n/** doc */\n// eslint-disable-next-line\nfunction f() {}\n",
            [(2, 2, NOTE, "", None), (3, 3, DOC, "", 4)],
        ),
        (
            "function f() {}\n\n/** A */\n// n1\n/** B */\n// n2\n/** C */\n"
            "function g() {}\n",
            [(3, 6, NOTE, "", None), (7, 7, DOC, "", 8)],
        ),
        (
            "let x = 1;\n/** A */\n// n1\n/** B */\n",
            [(2, 3, NOTE, "", None), (4, 4, DOC, "<eof>", None)],
        ),
        (
            "/** A */\n// n1\n/** B */\nlet x = 1;\n",
            [(1, 1, DOC, "", None), (2, 3, NOTE, "", None)],
        ),
    ],
    ids=[
        "no-code",
        "head-above-a-declaration",
        "comment-documents-below-the-head-doc",
        "comment-documents-below-a-mid-file-doc",
        "between-two-declarations",
        "foot-below-code",
        "head-above-plain-code",
    ],
)
def test_a_gap_is_cut_into_its_a0_its_one_b_and_the_a_at_its_lower_edge(text, expected):
    # The run touching the gap's lower edge is that edge's `a`; at the head the
    # doc run opening the file is `a0`; everything else in the gap is one `b`.
    found = read("m.js", text).paragraphs(Path("m.js"))
    got = [(p.start, p.end, p.kind, p.anchor, p.anchor_line) for p in found]
    assert [row for row in got if row[2] != Kind.TRAILING] == expected


@pytest.mark.parametrize(
    ("name", "text", "expected"),
    [
        (
            "m.js",
            "/** M */\n/** F */\nfunction f() {}\n",
            [(1, 1, DOC, "", None), (2, 2, DOC, "", 3)],
        ),
        (
            "m.js",
            "/** M */\n\n/** F */\nfunction f() {}\n",
            [(1, 1, DOC, "", None), (3, 3, DOC, "", 4)],
        ),
        (
            "m.js",
            "/** A */\n/** B */\n/** C */\nfunction f() {}\n",
            [(1, 1, DOC, "", None), (2, 2, NOTE, "", None), (3, 3, DOC, "", 4)],
        ),
        (
            "m.js",
            "/**\n * M\n */\n/**\n * F\n */\nfunction f() {}\n",
            [(1, 3, DOC, "", None), (4, 6, DOC, "", 7)],
        ),
        (
            "m.swift",
            "/// M\n\n/// F\nfunc f() {}\n",
            [(1, 1, DOC, "", None), (3, 3, DOC, "", 4)],
        ),
        (
            "m.js",
            "/** M */\n/** F */\n// c\nfunction f() {}\n",
            [(1, 1, DOC, "", None), (2, 2, NOTE, "", None), (3, 3, DOC, "", 4)],
        ),
        ("m.js", "/** F */\nfunction f() {}\n", [(1, 1, DOC, "", 2)]),
        ("m.swift", "/// M\n/// F\nfunc f() {}\n", [(1, 2, DOC, "", 3)]),
        (
            "m.js",
            "/** M */ /** F */\nfunction f() {}\n",
            [(1, 1, DOC, "", 2)],
        ),
        ("m.js", "/** M */\n/** F */\nlet x = 1;\n", [(1, 2, DOC, "", None)]),
    ],
    ids=[
        "two-flush",
        "two-apart",
        "three",
        "two-multi-line",
        "two-doc-line-runs",
        "two-over-a-documenting-comment",
        "one",
        "one-doc-line-run",
        "two-on-one-line",
        "above-plain-code",
    ],
)
def test_two_head_doc_comments_over_a_declaration_split_into_a0_and_its_a(
    name, text, expected
):
    # A lone doc comment at the head touching a declaration is the
    # declaration's. Two or more split: the first is `a0`, the one touching the
    # declaration is its `a`, and any between are the gap's `b`. A line is not
    # cut, so two doc comments on one line are one.
    found = read(name, text).paragraphs(Path(name))
    got = [(p.start, p.end, p.kind, p.anchor, p.anchor_line) for p in found]
    assert [row for row in got if row[2] != Kind.TRAILING] == expected


def test_the_modules_docstring_ends_where_its_opening_doc_group_does():
    # `val` declares nothing here, so the run documents nothing: the module's
    # docstring is line 1, and the comment and the doc below it are one `b`.
    text = "/** x */\n// y\n/** w */\n\nval z = 1\n"
    found = read("m.kt", text).paragraphs(Path("m.kt"))
    assert [(p.start, p.end, p.kind, p.anchor_line) for p in found] == [
        (1, 1, Kind.DOCSTRING, None),
        (2, 3, Kind.COMMENT, None),
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
        (
            *LEXICAL_INPUTS["a-series/keywords"],
            True,
        ),
        (
            *LEXICAL_INPUTS["a-series/doc-markers-alone"],
            True,
        ),
        (
            *LEXICAL_INPUTS["a-series/neither"],
            False,
        ),
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


def test_a_line_holding_only_a_byte_order_mark_is_leading_and_keeps_the_mark():
    mark = chr(0xFEFF)
    found = leading_between([], mark + "\nx\n", [2])
    assert [(p.start, p.end, p.raw_lines) for p in found] == [(1, 1, [mark])]


def test_a_line_holding_only_a_byte_order_mark_is_not_a_code_line():
    mark = chr(0xFEFF)
    lines = read("m.js", mark + "\nconst x = 1;\n").code_lines()
    assert [line.line for line in lines] == [2]


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


@pytest.mark.parametrize(
    ("name", "text", "raw"),
    [
        (
            *LEXICAL_INPUTS["doc-trailing/above-a-declaration"],
            [" /** note */"],
        ),
        (
            *LEXICAL_INPUTS["doc-trailing/at-the-head"],
            [" /** note */"],
        ),
        (
            *LEXICAL_INPUTS["doc-trailing/java"],
            [" /** note */"],
        ),
        (
            *LEXICAL_INPUTS["doc-trailing/spanning-lines"],
            [" /** note", "   more */"],
        ),
    ],
    ids=["above-a-declaration", "at-the-head", "java", "spanning-lines"],
)
def test_a_doc_comment_trailing_code_is_a_trailing_comment(name, text, raw):
    lexical = read(name, text)
    found = lexical.paragraphs(Path(name))
    code = text.split(" /**")[0]
    assert [
        (p.start, p.end, p.kind, p.anchor, p.anchor_line, p.raw_lines) for p in found
    ] == [(1, len(raw), Kind.TRAILING, code, None, raw)]
    assert lexical.code_lines()[0].line == 1


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (
            "--[[\n  Licence MIT\n]]--\n-- Module foo\nlocal M = {}\nreturn M\n",
            [(1, 4, Kind.MATTER, ["--[[", "  Licence MIT", "]]--", "-- Module foo"])],
        ),
        (
            "local M = {}\nreturn M\n--[[\n  notes\n]]--\n-- end\n",
            [(3, 6, Kind.MATTER, ["--[[", "  notes", "]]--", "-- end"])],
        ),
    ],
    ids=["head", "foot"],
)
def test_a_line_comment_after_a_long_comments_closer_continues_its_run(text, expected):
    found = read("m.lua", text).paragraphs(Path("m.lua"))
    assert [(p.start, p.end, p.kind, p.raw_lines) for p in found] == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (
            "/* a\n b */ /* c */\n// d\nint y;\n",
            [(1, 3, Kind.MATTER, "<module>", ["/* a", " b */ /* c */", "// d"])],
        ),
        (
            "int y;\n/* a\n b */ /* c */\n// d\n",
            [(2, 4, Kind.MATTER, "<module>", ["/* a", " b */ /* c */", "// d"])],
        ),
    ],
    ids=["front", "back"],
)
def test_the_runs_at_one_end_of_the_file_are_one_matter_paragraph(text, expected):
    found = read("m.c", text).paragraphs(Path("m.c"))
    assert [(p.start, p.end, p.kind, p.anchor, p.raw_lines) for p in found] == (
        expected
    )


@pytest.mark.parametrize(
    ("name", "text", "expected", "code"),
    [
        (
            *LEXICAL_INPUTS["closer/closer-then-block-comment"],
            [(2, 4, Kind.COMMENT)],
            [1, 5],
        ),
        (
            *LEXICAL_INPUTS["closer/closer-then-open-block"],
            [(2, 4, Kind.COMMENT)],
            [1, 5],
        ),
        (
            *LEXICAL_INPUTS["closer/one-line-then-open-block"],
            [(2, 3, Kind.COMMENT)],
            [1, 4],
        ),
        (
            *LEXICAL_INPUTS["closer/one-line-then-line-comment"],
            [(1, 1, Kind.MATTER)],
            [2],
        ),
        (
            *LEXICAL_INPUTS["closer/beside-code"],
            [(1, 1, Kind.TRAILING)],
            [1],
        ),
        (
            *LEXICAL_INPUTS["closer/lua-long-closer"],
            [(1, 4, Kind.MATTER)],
            [5],
        ),
        (
            *LEXICAL_INPUTS["closer/lua-one-line"],
            [(1, 1, Kind.MATTER)],
            [2],
        ),
        (
            *LEXICAL_INPUTS["closer/lua-one-line-with-text"],
            [(1, 2, Kind.MATTER)],
            [3],
        ),
    ],
    ids=[
        "closer-then-block-comment",
        "closer-then-open-block",
        "one-line-then-open-block",
        "one-line-then-line-comment",
        "beside-code",
        "lua-long-closer",
        "lua-one-line",
        "lua-one-line-with-text",
    ],
)
def test_a_comment_after_a_closer_continues_the_run_on_a_line_holding_no_code(
    name, text, expected, code
):
    lexical = read(name, text)
    found = lexical.paragraphs(Path(name))
    assert [(p.start, p.end, p.kind) for p in found] == expected
    assert [c.line for c in lexical.code_lines()] == code


@pytest.mark.parametrize(
    ("name", "text", "line"),
    [
        (
            *LEXICAL_INPUTS["annotated-doc/one"],
            3,
        ),
        (
            *LEXICAL_INPUTS["annotated-doc/two"],
            4,
        ),
        (
            *LEXICAL_INPUTS["annotated-doc/with-arguments"],
            3,
        ),
        (
            *LEXICAL_INPUTS["annotated-doc/typescript-decorator"],
            3,
        ),
    ],
    ids=["one", "two", "with-arguments", "typescript-decorator"],
)
def test_a_doc_run_above_annotation_lines_documents_the_declaration_below(
    name, text, line
):
    # The run documents the declaring line, across the annotations above it.
    found = read(name, text).paragraphs(Path(name))
    assert [(p.start, p.kind, p.anchor_line) for p in found] == [
        (1, Kind.DOCSTRING, line)
    ]


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("/** x */\n@Ann\nint y = 1;\n", [(1, Kind.DOCSTRING, None, "")]),
        (
            "class A {}\n/** x */\n@Ann\nint y = 1;\n",
            [(2, Kind.COMMENT, None, "")],
        ),
    ],
    ids=["at-the-head", "between-code"],
)
def test_a_doc_run_above_an_annotation_on_no_declaration_documents_none(text, expected):
    found = read("m.java", text).paragraphs(Path("m.java"))
    assert [(p.start, p.kind, p.anchor_line, p.anchor) for p in found] == expected


def test_a_csharp_line_opening_with_a_bracket_is_not_an_annotation():
    # C# names no annotation opener: `[` opens an attribute section and a
    # collection-expression line alike.
    found = read("m.cs", "/// App.\n[Serializable]\nclass App {}\n").paragraphs(
        Path("m.cs")
    )
    assert [(p.start, p.kind, p.anchor_line) for p in found] == [
        (1, Kind.DOCSTRING, None)
    ]
    csharp = language_for(Path("m.cs"))
    assert csharp is not None
    code = {
        1: "class A {",
        2: "  int[] xs =",
        3: "  [1, 2];",
        4: "  public void F() {}",
    }
    assert declarations(csharp, code) == {1: DocPlace(1, True), 4: DocPlace(4, True)}


def test_an_annotation_line_belongs_only_to_a_row_that_names_it():
    # Go names no annotation opener, so `@x` is code the walk stops at.
    found = read("m.go", "// doc\n@x\nfunc F() {}\n").paragraphs(Path("m.go"))
    assert [(p.start, p.anchor_line) for p in found] == [(1, None)]


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        ({1: "@Ann", 2: "@Other(x = 1)", 3: "class A {}"}, {3: DocPlace(1, True)}),
        ({1: "int x;", 3: "@Ann", 4: "class A {}"}, {4: DocPlace(3, True)}),
        ({1: "@Ann", 3: "class A {}"}, {3: DocPlace(3, True)}),
        ({1: "@Ann", 2: "int y = 1;"}, {}),
    ],
    ids=["two-annotations", "below-code", "blank-between", "no-declaration"],
)
def test_a_declarations_doc_is_set_above_the_annotation_lines_directly_above_it(
    code, expected
):
    java = language_for(Path("m.java"))
    assert java is not None
    assert declarations(java, code) == expected


def test_the_annotation_lines_and_their_declaring_line_are_handed_over_joined():
    text = "class A {\n  /** F. */\n  @Ann // why\n  @Other\n  public void f() {}\n}\n"
    assert read("m.java", text).code_lines() == [
        CodeLine(1, "class A {", DocPlace(1, True)),
        CodeLine(3, "  @Ann", None),
        CodeLine(4, "  @Other", None, True),
        CodeLine(5, "  public void f() {}", DocPlace(3, True), True),
        CodeLine(6, "}", None),
    ]


@pytest.mark.parametrize(
    ("name", "text", "expected"),
    [
        (
            *LEXICAL_INPUTS["annotation-join/kotlin-annotated-members"],
            [
                CodeLine(1, "class A {", DocPlace(1, True)),
                CodeLine(2, "    @Inject lateinit var a: Foo", None),
                CodeLine(3, "    @Inject lateinit var b: Bar", None),
                CodeLine(4, "    private val c = 1", DocPlace(4, True)),
                CodeLine(5, "}", None),
            ],
        ),
        (
            *LEXICAL_INPUTS["annotation-join/java-annotated-method"],
            [
                CodeLine(1, "class A {", DocPlace(1, True)),
                CodeLine(
                    2,
                    "  @Override public int hashCode() { return 1; }",
                    DocPlace(2, True),
                ),
                CodeLine(
                    3, '  public String toString() { return ""; }', DocPlace(3, True)
                ),
                CodeLine(4, "}", None),
            ],
        ),
        (
            *LEXICAL_INPUTS[
                "annotation-join/annotation-above-an-annotated-declaration"
            ],
            [
                CodeLine(1, "@Ann", None),
                CodeLine(2, "@Override public void f() {}", DocPlace(1, True), True),
            ],
        ),
        (
            *LEXICAL_INPUTS["annotation-join/annotations-with-arguments"],
            [
                CodeLine(1, '@Ann(x = "a)")', None),
                CodeLine(2, "@Other({1, 2})", None, True),
                CodeLine(3, "public void f() {}", DocPlace(1, True), True),
            ],
        ),
    ],
    ids=[
        "kotlin-annotated-members",
        "java-annotated-method",
        "annotation-above-an-annotated-declaration",
        "annotations-with-arguments",
    ],
)
def test_only_a_line_holding_nothing_but_annotations_joins_the_line_below(
    name, text, expected
):
    assert read(name, text).code_lines() == expected


def test_declarations_hold_only_the_declaring_lines():
    go = language_for(Path("m.go"))
    assert go is not None
    assert declarations(go, {1: "package m", 3: "func f() {}"}) == {
        3: DocPlace(3, True)
    }
