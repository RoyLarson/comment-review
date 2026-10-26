import re
from importlib import import_module
from importlib.resources import files
from pathlib import Path

import pytest

from comment_review.reading.definitions import LanguageDefinition, decode_definition
from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage
from comment_review.reading.paragraph import Paragraph
from comment_review.reading.rust import records
from comment_review.reading.series import Kind
from comment_review.reading.source import (
    CodeLine,
    DocPlace,
    DocumentationOwner,
    RegionKind,
    SourceDeclaration,
    SourceRegion,
    SourceSection,
    SourceSpan,
    SourceStructure,
)

TEXT = "// note\nfn go() {}\n#![allow(x)]\n"
COMMENT = SourceSpan(0, 7)
BREAK = SourceSpan(7, 8)
CODE = SourceSpan(8, 18)
BREAK_2 = SourceSpan(18, 19)
DIRECTIVE = SourceSpan(19, 31)
BREAK_3 = SourceSpan(31, 32)


def regions() -> tuple[SourceRegion, ...]:
    return (
        SourceRegion(COMMENT, RegionKind.COMMENT),
        SourceRegion(BREAK, RegionKind.WHITESPACE),
        SourceRegion(CODE, RegionKind.CODE),
        SourceRegion(BREAK_2, RegionKind.WHITESPACE),
        SourceRegion(DIRECTIVE, RegionKind.DIRECTIVE),
        SourceRegion(BREAK_3, RegionKind.WHITESPACE),
    )


def tokens():
    kind = records.RustTokenKind
    return (
        records.RustToken(kind.LINE, COMMENT),
        records.RustToken(kind.WORD, SourceSpan(8, 10)),
        records.RustToken(kind.INNER_ATTRIBUTE, DIRECTIVE),
    )


def declaration(start: int = 8) -> SourceDeclaration:
    return SourceDeclaration(SourceSpan(start, start + 2), start, "fn")


def source(*, declarations=(), text=TEXT, found=None) -> SourceStructure:
    return SourceStructure(text, found or regions(), (), declarations, ())


def read(protected=(DIRECTIVE,), warnings=(), declarations=()):
    detached = tuple(
        records.DetachedRun(w.span) for w in warnings if w.span is not None
    )
    return records.RustRead(
        source(declarations=declarations),
        protected,
        warnings,
        detached,
    )


def rust_scan(text, found, scanned_tokens):
    return records.RustScan(text, found, scanned_tokens)


def warning(span=COMMENT, code="detached-documentation", stage=ReadStage.PLACE):
    return ReadDiagnostic(stage, code, "documentation cannot be placed", span)


def test_records_token_kinds_spell_the_six_comment_forms():
    values = {kind.value for kind in records.RustTokenKind}
    assert {
        "line",
        "outer_doc_line",
        "inner_doc_line",
        "delimited_comment",
        "outer_doc_delimited",
        "inner_doc_delimited",
    } <= values


def test_records_valid_scan_reconstructs_its_text():
    scan = rust_scan(TEXT, regions(), tokens())
    assert "".join(TEXT[r.span.start : r.span.end] for r in scan.regions) == TEXT


def test_records_empty_text_has_no_regions():
    rust_scan("", (), ())
    with pytest.raises(ValueError):
        rust_scan("", regions(), ())


@pytest.mark.parametrize(
    "bad",
    [
        regions()[:1] + regions()[2:],
        (SourceRegion(SourceSpan(0, 8), RegionKind.COMMENT),) + regions()[1:],
        regions()[1:] + regions()[:1],
        regions() + (SourceRegion(SourceSpan(32, 40), RegionKind.CODE),),
        regions()[:-1],
    ],
    ids=["gap", "overlap", "out-of-order", "out-of-bounds", "short"],
)
def test_records_scan_rejects_bad_region_partition(bad):
    with pytest.raises(ValueError):
        rust_scan(TEXT, bad, ())


def test_records_token_requires_nonempty_span():
    with pytest.raises(ValueError):
        records.RustToken(records.RustTokenKind.WORD, SourceSpan(3, 3))


def test_records_scan_rejects_tokens_out_of_order_or_overlapping():
    first, second, third = tokens()
    with pytest.raises(ValueError):
        rust_scan(TEXT, regions(), (second, first, third))
    overlap = records.RustToken(records.RustTokenKind.WORD, SourceSpan(9, 12))
    with pytest.raises(ValueError):
        rust_scan(TEXT, regions(), (first, second, overlap, third))
    outside = records.RustToken(records.RustTokenKind.WORD, SourceSpan(30, 40))
    with pytest.raises(ValueError):
        rust_scan(TEXT, regions(), (first, second, outside))


def test_records_comment_token_must_equal_a_comment_region():
    kind = records.RustTokenKind
    short = records.RustToken(kind.LINE, SourceSpan(0, 5))
    with pytest.raises(ValueError):
        rust_scan(TEXT, regions(), (short,))
    on_code = records.RustToken(kind.DELIMITED_COMMENT, CODE)
    with pytest.raises(ValueError):
        rust_scan(TEXT, regions(), (on_code,))


def test_records_literal_token_must_lie_in_a_literal_region():
    token = records.RustToken(records.RustTokenKind.STRING, SourceSpan(8, 10))
    with pytest.raises(ValueError):
        rust_scan(TEXT, regions(), (token,))


def test_records_scan_accepts_a_literal_token_inside_a_literal_region():
    kind = records.RustTokenKind
    found = (
        SourceRegion(COMMENT, RegionKind.COMMENT),
        SourceRegion(SourceSpan(7, 12), RegionKind.LITERAL),
        SourceRegion(SourceSpan(12, 32), RegionKind.CODE),
    )
    scan = rust_scan(
        TEXT,
        found,
        (
            records.RustToken(kind.LINE, COMMENT),
            records.RustToken(kind.STRING, SourceSpan(7, 12)),
        ),
    )
    assert len(scan.tokens) == 2


def test_records_scan_accepts_a_token_enclosed_by_an_attribute():
    kind = records.RustTokenKind
    inside = (
        records.RustToken(kind.OUTER_ATTRIBUTE, DIRECTIVE),
        records.RustToken(kind.OPEN, SourceSpan(21, 22)),
        records.RustToken(kind.WORD, SourceSpan(22, 27)),
        records.RustToken(kind.INNER_ATTRIBUTE, SourceSpan(27, 31)),
        records.RustToken(kind.WORD, SourceSpan(31, 32)),
    )
    rust_scan(TEXT, regions(), inside)
    nested = (
        records.RustToken(kind.OUTER_ATTRIBUTE, DIRECTIVE),
        records.RustToken(kind.INNER_ATTRIBUTE, SourceSpan(21, 31)),
        records.RustToken(kind.WORD, SourceSpan(22, 27)),
    )
    rust_scan(TEXT, regions(), nested)


def test_records_scan_rejects_partial_overlap_with_an_attribute():
    kind = records.RustTokenKind
    attribute = records.RustToken(kind.OUTER_ATTRIBUTE, DIRECTIVE)
    runs_past = records.RustToken(kind.WORD, SourceSpan(28, 32))
    with pytest.raises(ValueError):
        rust_scan(TEXT, regions(), (attribute, runs_past))
    starts_before = records.RustToken(kind.WORD, SourceSpan(17, 21))
    with pytest.raises(ValueError):
        rust_scan(TEXT, regions(), (starts_before, attribute))
    nested_past = records.RustToken(kind.INNER_ATTRIBUTE, SourceSpan(25, 32))
    with pytest.raises(ValueError):
        rust_scan(TEXT, regions(), (attribute, nested_past))


def test_records_scan_rejects_a_non_attribute_token_enclosing_another():
    kind = records.RustTokenKind
    outer = records.RustToken(kind.PUNCT, DIRECTIVE)
    inner = records.RustToken(kind.WORD, SourceSpan(22, 27))
    with pytest.raises(ValueError):
        rust_scan(TEXT, regions(), (outer, inner))


def test_records_placement_accepts_detached_runs():
    one = declaration()
    records.RustPlacement((one,), (records.DetachedRun(COMMENT),))
    records.RustPlacement((), ())
    records.RustPlacement((one, declaration(10)), ())


def test_records_read_accepts_a_consistent_read():
    read(warnings=(warning(),))
    read(declarations=(declaration(),))


def test_records_read_refuses_two_declarations_on_one_line():
    with pytest.raises(ValueError, match="own line"):
        read(declarations=(declaration(), declaration(10)))


def test_records_read_rejects_wrong_warning_code_stage_or_span():
    with pytest.raises(ValueError):
        read(warnings=(warning(code="other"),))
    with pytest.raises(ValueError):
        read(warnings=(warning(stage=ReadStage.LEX),))
    with pytest.raises(ValueError):
        read(warnings=(warning(span=None),))
    with pytest.raises(ValueError):
        read(warnings=(warning(span=SourceSpan(30, 99)),))


def test_records_read_protected_span_must_be_a_directive_region():
    with pytest.raises(ValueError):
        read(protected=(CODE,))
    with pytest.raises(ValueError):
        read(protected=(SourceSpan(19, 30),))
    with pytest.raises(ValueError):
        read(protected=(SourceSpan(30, 99),))


@pytest.fixture
def rust_definition():
    text = (
        files("comment_review")
        .joinpath("references/languages/rust.toml")
        .read_text(encoding="utf-8")
    )
    definition = decode_definition(text)
    assert isinstance(definition, LanguageDefinition)
    return definition


def scan(text, definition):
    try:
        scanner = import_module("comment_review.reading.rust.scanner")
    except ModuleNotFoundError:
        pytest.fail("Rust scanner is not implemented", pytrace=False)
    return scanner.scan_rust(text, definition)


def scanned(text, definition):
    result = scan(text, definition)
    assert not isinstance(result, ReadFailure), result
    assert "".join(text[r.span.start : r.span.end] for r in result.regions) == text
    kind = records.RustTokenKind
    code = {kind.WORD, kind.PUNCT, kind.OPEN, kind.CLOSE, kind.LIFETIME}
    for token in result.tokens:
        if token.kind in records.ATTRIBUTE_KINDS:
            first, last = (
                [r for r in result.regions if r.span.start <= at < r.span.end][0]
                for at in (token.span.start, token.span.end - 1)
            )
            assert first.kind is RegionKind.CODE and last.kind is RegionKind.CODE
            continue
        (region,) = [
            r
            for r in result.regions
            if r.span.start <= token.span.start and token.span.end <= r.span.end
        ]
        if token.kind in records.COMMENT_KINDS:
            assert region.kind is RegionKind.COMMENT and region.span == token.span
        elif token.kind in records.LITERAL_KINDS:
            assert region.kind is RegionKind.LITERAL
        elif token.kind in code:
            assert region.kind is RegionKind.CODE
        elif token.kind is kind.SHEBANG:
            assert region.kind is RegionKind.DIRECTIVE and region.span == token.span
        else:
            assert token.kind is kind.WHITESPACE
            assert region.kind is RegionKind.WHITESPACE
    return result


def shape(result):
    return [
        (region.kind, result.text[region.span.start : region.span.end])
        for region in result.regions
    ]


def spelled(result):
    return [
        (token.kind.value, result.text[token.span.start : token.span.end])
        for token in result.tokens
    ]


def test_exact_source_empty_input_has_no_regions_or_tokens(rust_definition):
    result = scanned("", rust_definition)
    assert result.regions == ()
    assert result.tokens == ()


def test_exact_source_keeps_a_leading_byte_order_mark(rust_definition):
    result = scanned("\ufefffn x", rust_definition)
    assert shape(result) == [
        (RegionKind.WHITESPACE, "\ufeff"),
        (RegionKind.CODE, "fn"),
        (RegionKind.WHITESPACE, " "),
        (RegionKind.CODE, "x"),
    ]
    assert spelled(result) == [("word", "fn"), ("whitespace", " "), ("word", "x")]


def test_exact_source_byte_order_mark_joins_following_whitespace(rust_definition):
    result = scanned(chr(0xFEFF) + " \nx", rust_definition)
    assert shape(result) == [
        (RegionKind.WHITESPACE, chr(0xFEFF) + " \n"),
        (RegionKind.CODE, "x"),
    ]
    assert spelled(result) == [("whitespace", " \n"), ("word", "x")]


def test_comments_after_a_byte_order_mark(rust_definition):
    result = scanned(chr(0xFEFF) + "//! a", rust_definition)
    assert shape(result) == [
        (RegionKind.WHITESPACE, chr(0xFEFF)),
        (RegionKind.COMMENT, "//! a"),
    ]
    assert spelled(result) == [("inner_doc_line", "//! a")]


def test_comments_closer_without_an_opener_is_code(rust_definition):
    result = scanned("a */ b", rust_definition)
    assert shape(result) == [
        (RegionKind.CODE, "a"),
        (RegionKind.WHITESPACE, " "),
        (RegionKind.CODE, "*/"),
        (RegionKind.WHITESPACE, " "),
        (RegionKind.CODE, "b"),
    ]
    assert spelled(result) == [
        ("word", "a"),
        ("whitespace", " "),
        ("punct", "*"),
        ("punct", "/"),
        ("whitespace", " "),
        ("word", "b"),
    ]


@pytest.mark.parametrize("newline", ["\n", "\r\n"])
def test_exact_source_reads_lf_and_crlf_as_one_line_break(rust_definition, newline):
    text = f"// a{newline}fn b(){newline}"
    result = scanned(text, rust_definition)
    assert shape(result) == [
        (RegionKind.COMMENT, "// a"),
        (RegionKind.WHITESPACE, newline),
        (RegionKind.CODE, "fn"),
        (RegionKind.WHITESPACE, " "),
        (RegionKind.CODE, "b()"),
        (RegionKind.WHITESPACE, newline),
    ]
    assert spelled(result) == [
        ("line", "// a"),
        ("whitespace", newline),
        ("word", "fn"),
        ("whitespace", " "),
        ("word", "b"),
        ("open", "("),
        ("close", ")"),
        ("whitespace", newline),
    ]


def test_exact_source_without_a_final_newline(rust_definition):
    result = scanned("let x=[y];", rust_definition)
    assert shape(result) == [
        (RegionKind.CODE, "let"),
        (RegionKind.WHITESPACE, " "),
        (RegionKind.CODE, "x=[y];"),
    ]
    assert spelled(result) == [
        ("word", "let"),
        ("whitespace", " "),
        ("word", "x"),
        ("punct", "="),
        ("open", "["),
        ("word", "y"),
        ("close", "]"),
        ("punct", ";"),
    ]


@pytest.mark.parametrize("space", ["\v", "\f", chr(0x85), chr(0x2028)])
def test_exact_source_reads_rust_pattern_whitespace(rust_definition, space):
    result = scanned(f"a{space}b", rust_definition)
    assert spelled(result) == [("word", "a"), ("whitespace", space), ("word", "b")]


@pytest.mark.parametrize(
    ("text", "kind"),
    [
        ("// a", "line"),
        ("/// a", "outer_doc_line"),
        ("//! a", "inner_doc_line"),
        ("//// a", "line"),
        ("/* a */", "delimited_comment"),
        ("/** a */", "outer_doc_delimited"),
        ("/*! a */", "inner_doc_delimited"),
        ("/***/", "delimited_comment"),
        ("/*!*/", "inner_doc_delimited"),
        ("/** a /* b */ c */", "outer_doc_delimited"),
        ("/*** a */", "delimited_comment"),
        ("/**/", "delimited_comment"),
    ],
)
def test_comments_each_form_is_one_comment_region(rust_definition, text, kind):
    result = scanned(text, rust_definition)
    assert shape(result) == [(RegionKind.COMMENT, text)]
    assert spelled(result) == [(kind, text)]


def test_comments_nested_delimited_comment_is_one_region(rust_definition):
    result = scanned("/* a /* b */ c */x", rust_definition)
    assert shape(result) == [
        (RegionKind.COMMENT, "/* a /* b */ c */"),
        (RegionKind.CODE, "x"),
    ]
    assert spelled(result) == [
        ("delimited_comment", "/* a /* b */ c */"),
        ("word", "x"),
    ]


def test_comments_delimited_comment_spans_lines(rust_definition):
    result = scanned("/** a\r\n b */\r\nfn", rust_definition)
    assert shape(result) == [
        (RegionKind.COMMENT, "/** a\r\n b */"),
        (RegionKind.WHITESPACE, "\r\n"),
        (RegionKind.CODE, "fn"),
    ]
    assert spelled(result)[0] == ("outer_doc_delimited", "/** a\r\n b */")


def test_comments_after_a_closing_brace_on_the_same_line(rust_definition):
    result = scanned("}// a\n", rust_definition)
    assert shape(result) == [
        (RegionKind.CODE, "}"),
        (RegionKind.COMMENT, "// a"),
        (RegionKind.WHITESPACE, "\n"),
    ]
    assert spelled(result) == [("close", "}"), ("line", "// a"), ("whitespace", "\n")]


def test_comments_split_code_around_a_delimited_comment(rust_definition):
    result = scanned("a/* x */b", rust_definition)
    assert shape(result) == [
        (RegionKind.CODE, "a"),
        (RegionKind.COMMENT, "/* x */"),
        (RegionKind.CODE, "b"),
    ]
    assert spelled(result) == [
        ("word", "a"),
        ("delimited_comment", "/* x */"),
        ("word", "b"),
    ]


def test_comments_resume_after_a_close_into_another_comment(rust_definition):
    result = scanned("/* a *//// b", rust_definition)
    assert shape(result) == [
        (RegionKind.COMMENT, "/* a */"),
        (RegionKind.COMMENT, "/// b"),
    ]
    assert spelled(result) == [
        ("delimited_comment", "/* a */"),
        ("outer_doc_line", "/// b"),
    ]


def test_comments_final_line_comment_without_newline(rust_definition):
    result = scanned("x\n//! end", rust_definition)
    assert shape(result) == [
        (RegionKind.CODE, "x"),
        (RegionKind.WHITESPACE, "\n"),
        (RegionKind.COMMENT, "//! end"),
    ]


@pytest.mark.parametrize(
    ("text", "opener"),
    [
        ("x /* a\n", 2),
        ("/* a /* b */ c", 0),
        ("y\n/*! a /* b /* c */", 2),
    ],
)
def test_comments_unterminated_delimited_comment_fails_at_outermost_opener(
    rust_definition, text, opener
):
    result = scan(text, rust_definition)
    assert isinstance(result, ReadFailure)
    assert len(result.diagnostics) == 1
    diagnostic = result.diagnostics[0]
    assert diagnostic.stage == ReadStage.LEX
    assert diagnostic.code == "unterminated-comment"
    assert diagnostic.span == SourceSpan(opener, opener + 2)


@pytest.mark.parametrize("text", ["\x00", "// a\x00\n", "/* \x00 */", "x\x00"])
def test_comments_source_nul_refuses(rust_definition, text):
    result = scan(text, rust_definition)
    assert isinstance(result, ReadFailure)
    at = text.index("\x00")
    assert result.diagnostics == (
        ReadDiagnostic(
            ReadStage.LEX, "source-nul", "source nul", SourceSpan(at, at + 1)
        ),
    )


def refused(text, definition, code, start, end):
    result = scan(text, definition)
    assert isinstance(result, ReadFailure)
    assert len(result.diagnostics) == 1
    diagnostic = result.diagnostics[0]
    assert diagnostic.stage == ReadStage.LEX
    assert diagnostic.code == code
    assert diagnostic.span == SourceSpan(start, end)


def test_literals_string_crosses_lines(rust_definition):
    result = scanned('let s = "a\nb";', rust_definition)
    assert shape(result) == [
        (RegionKind.CODE, "let"),
        (RegionKind.WHITESPACE, " "),
        (RegionKind.CODE, "s"),
        (RegionKind.WHITESPACE, " "),
        (RegionKind.CODE, "="),
        (RegionKind.WHITESPACE, " "),
        (RegionKind.LITERAL, '"a\nb"'),
        (RegionKind.CODE, ";"),
    ]
    assert spelled(result)[-2:] == [("string", '"a\nb"'), ("punct", ";")]


@pytest.mark.parametrize(
    "text",
    ['"a\\"b"', '"a\\\nb"', '"a\\\r\nb"', '"\\\\"', 'b"a"', 'c"a"', '""'],
    ids=[
        "escaped-quote",
        "escaped-lf",
        "escaped-crlf",
        "escaped-escape",
        "b",
        "c",
        "empty",
    ],
)
def test_literals_string_forms_are_one_string(rust_definition, text):
    result = scanned(text, rust_definition)
    assert shape(result) == [(RegionKind.LITERAL, text)]
    assert spelled(result) == [("string", text)]


@pytest.mark.parametrize(
    "text",
    [
        'r"a\\"',
        'r#"a"#',
        'r###"a"## "###',
        'r##"a"#b"##',
        'br"a"',
        'br#"a"#',
        'cr"a"',
        'cr##"a"##',
    ],
)
def test_literals_raw_string_closes_at_its_own_guard_count(rust_definition, text):
    result = scanned(text, rust_definition)
    assert shape(result) == [(RegionKind.LITERAL, text)]
    assert spelled(result) == [("raw_string", text)]


def test_literals_raw_string_ends_before_extra_guards(rust_definition):
    result = scanned('r#"a"##', rust_definition)
    assert shape(result) == [
        (RegionKind.LITERAL, 'r#"a"#'),
        (RegionKind.CODE, "#"),
    ]
    assert spelled(result) == [("raw_string", 'r#"a"#'), ("punct", "#")]


@pytest.mark.parametrize(
    ("literal", "kind"),
    [
        ('"// a /* b"', "string"),
        ('b"// a /* b"', "string"),
        ('c"// a /* b"', "string"),
        ('r#"// a /* b"#', "raw_string"),
        ('br"// a /* b"', "raw_string"),
        ('cr"// a /* b"', "raw_string"),
        ("'/'", "char"),
        ("b'/'", "char"),
    ],
)
def test_literals_comment_markers_inside_stay_literal(rust_definition, literal, kind):
    result = scanned(literal + " // c", rust_definition)
    assert shape(result) == [
        (RegionKind.LITERAL, literal),
        (RegionKind.WHITESPACE, " "),
        (RegionKind.COMMENT, "// c"),
    ]
    assert spelled(result) == [(kind, literal), ("whitespace", " "), ("line", "// c")]


def test_literals_prefix_inside_a_word_opens_nothing(rust_definition):
    result = scanned('bar"x"', rust_definition)
    assert shape(result) == [(RegionKind.CODE, "bar"), (RegionKind.LITERAL, '"x"')]
    assert spelled(result) == [("word", "bar"), ("string", '"x"')]
    result = scanned('xr#"a"#', rust_definition)
    assert spelled(result) == [
        ("word", "xr"),
        ("punct", "#"),
        ("string", '"a"'),
        ("punct", "#"),
    ]


def test_literals_prefix_after_a_digit_opens_nothing(rust_definition):
    result = scanned("1r\"a\" 1b'x'", rust_definition)
    assert shape(result) == [
        (RegionKind.CODE, "1r"),
        (RegionKind.LITERAL, '"a"'),
        (RegionKind.WHITESPACE, " "),
        (RegionKind.CODE, "1b"),
        (RegionKind.LITERAL, "'x'"),
    ]
    assert spelled(result) == [
        ("punct", "1"),
        ("word", "r"),
        ("string", '"a"'),
        ("whitespace", " "),
        ("punct", "1"),
        ("word", "b"),
        ("char", "'x'"),
    ]


def test_literals_raw_identifier_is_a_word(rust_definition):
    result = scanned("r#ident = 1", rust_definition)
    assert shape(result) == [
        (RegionKind.CODE, "r#ident"),
        (RegionKind.WHITESPACE, " "),
        (RegionKind.CODE, "="),
        (RegionKind.WHITESPACE, " "),
        (RegionKind.CODE, "1"),
    ]
    assert spelled(result)[0] == ("word", "r#ident")


@pytest.mark.parametrize(
    ("text", "code", "start", "end"),
    [
        ('x "a', "unterminated-string", 2, 3),
        ('b"a\\"', "unterminated-string", 0, 2),
        ('c"a', "unterminated-string", 0, 2),
        ('r"a', "unterminated-raw-string", 0, 2),
        ('r#"a"', "unterminated-raw-string", 0, 3),
        ('r##"a"#', "unterminated-raw-string", 0, 4),
        ('br"a', "unterminated-raw-string", 0, 3),
        ('cr#"a"', "unterminated-raw-string", 0, 4),
        ("'\\n", "unterminated-char", 0, 1),
        ("b'ab'", "unterminated-char", 0, 2),
        ("y '", "unterminated-char", 2, 3),
    ],
)
def test_literals_unterminated_form_fails_at_its_opener(
    rust_definition, text, code, start, end
):
    refused(text, rust_definition, code, start, end)


@pytest.mark.parametrize(
    "literal", ["'a'", "'\\''", "'\\u{10FFFF}'", "'\\x7f'", "b'x'", "b'\\n'", "' '"]
)
def test_quotes_character_literals(rust_definition, literal):
    result = scanned(literal + " // c", rust_definition)
    assert shape(result) == [
        (RegionKind.LITERAL, literal),
        (RegionKind.WHITESPACE, " "),
        (RegionKind.COMMENT, "// c"),
    ]
    assert spelled(result) == [
        ("char", literal),
        ("whitespace", " "),
        ("line", "// c"),
    ]


@pytest.mark.parametrize("lifetime", ["'a", "'static", "'_", "'r#a"])
def test_quotes_lifetimes_are_code(rust_definition, lifetime):
    result = scanned(lifetime + " // c", rust_definition)
    assert shape(result) == [
        (RegionKind.CODE, lifetime),
        (RegionKind.WHITESPACE, " "),
        (RegionKind.COMMENT, "// c"),
    ]
    assert spelled(result) == [
        ("lifetime", lifetime),
        ("whitespace", " "),
        ("line", "// c"),
    ]


def test_quotes_lifetime_in_a_reference_type(rust_definition):
    result = scanned("&'a T", rust_definition)
    assert shape(result) == [
        (RegionKind.CODE, "&'a"),
        (RegionKind.WHITESPACE, " "),
        (RegionKind.CODE, "T"),
    ]
    assert spelled(result) == [
        ("punct", "&"),
        ("lifetime", "'a"),
        ("whitespace", " "),
        ("word", "T"),
    ]


def test_quotes_apostrophe_inside_a_string(rust_definition):
    result = scanned('"it\'s" // c', rust_definition)
    assert shape(result) == [
        (RegionKind.LITERAL, '"it\'s"'),
        (RegionKind.WHITESPACE, " "),
        (RegionKind.COMMENT, "// c"),
    ]
    assert spelled(result) == [
        ("string", '"it\'s"'),
        ("whitespace", " "),
        ("line", "// c"),
    ]


def test_attribute_extent_derive(rust_definition):
    result = scanned("#[derive(Debug)]\nfn", rust_definition)
    assert shape(result) == [
        (RegionKind.CODE, "#[derive(Debug)]"),
        (RegionKind.WHITESPACE, "\n"),
        (RegionKind.CODE, "fn"),
    ]
    assert spelled(result) == [
        ("outer_attribute", "#[derive(Debug)]"),
        ("punct", "#"),
        ("open", "["),
        ("word", "derive"),
        ("open", "("),
        ("word", "Debug"),
        ("close", ")"),
        ("close", "]"),
        ("whitespace", "\n"),
        ("word", "fn"),
    ]


@pytest.mark.parametrize(
    ("text", "attribute"),
    [
        ("#[cfg(\n    a,\n)]\nfn", "#[cfg(\n    a,\n)]"),
        ('#[doc = "]"] x', '#[doc = "]"]'),
        ('#[doc = "x"] x', '#[doc = "x"]'),
        ("#[cfg(any(a, b))] x", "#[cfg(any(a, b))]"),
        ("#[a[b[c]]] x", "#[a[b[c]]]"),
        ("#[a /* ] */ // ]\n] x", "#[a /* ] */ // ]\n]"),
        ("x #[a] y", "#[a]"),
    ],
    ids=["multi-line", "string-close", "doc", "nested", "brackets", "comments", "mid"],
)
def test_attribute_extent_spans_to_its_matching_close(rust_definition, text, attribute):
    result = scanned(text, rust_definition)
    (token,) = [
        t for t in result.tokens if t.kind is records.RustTokenKind.OUTER_ATTRIBUTE
    ]
    assert text[token.span.start : token.span.end] == attribute


def test_attribute_extent_keeps_inner_literals_and_comments(rust_definition):
    result = scanned('#[doc = "]"/* c */]', rust_definition)
    assert shape(result) == [
        (RegionKind.CODE, "#[doc"),
        (RegionKind.WHITESPACE, " "),
        (RegionKind.CODE, "="),
        (RegionKind.WHITESPACE, " "),
        (RegionKind.LITERAL, '"]"'),
        (RegionKind.COMMENT, "/* c */"),
        (RegionKind.CODE, "]"),
    ]
    assert spelled(result) == [
        ("outer_attribute", '#[doc = "]"/* c */]'),
        ("punct", "#"),
        ("open", "["),
        ("word", "doc"),
        ("whitespace", " "),
        ("punct", "="),
        ("whitespace", " "),
        ("string", '"]"'),
        ("delimited_comment", "/* c */"),
        ("close", "]"),
    ]


def test_attribute_extent_inner_attribute(rust_definition):
    result = scanned("#![allow(x)]\n", rust_definition)
    assert shape(result) == [
        (RegionKind.CODE, "#![allow(x)]"),
        (RegionKind.WHITESPACE, "\n"),
    ]
    assert spelled(result) == [
        ("inner_attribute", "#![allow(x)]"),
        ("punct", "#"),
        ("punct", "!"),
        ("open", "["),
        ("word", "allow"),
        ("open", "("),
        ("word", "x"),
        ("close", ")"),
        ("close", "]"),
        ("whitespace", "\n"),
    ]


def test_attribute_extent_shebang_line_is_not_an_attribute(rust_definition):
    result = scanned("#!/bin/x\n", rust_definition)
    assert spelled(result)[0] == ("shebang", "#!/bin/x")
    assert all(kind != "inner_attribute" for kind, _ in spelled(result))


@pytest.mark.parametrize(
    ("text", "start", "end"),
    [("x\n#[cfg(a)", 2, 4), ("#![a", 0, 3), ('#[doc = "]"', 0, 2)],
)
def test_attribute_extent_unclosed_attribute_fails_at_its_opener(
    rust_definition, text, start, end
):
    refused(text, rust_definition, "unterminated-attribute", start, end)


def placement_of(text, definition):
    try:
        structure = import_module("comment_review.reading.rust.structure")
    except ModuleNotFoundError:
        pytest.fail("Rust structure is not implemented", pytrace=False)
    return structure.place_declarations(scanned(text, definition), definition)


def anchor_lines(text, placement):
    """Each declaration's anchor line, 1-based."""
    return tuple(text.count("\n", 0, d.anchor) + 1 for d in placement.declarations)


def placed(text, definition):
    """Each placed owner as (kind, head first line)."""
    placement = placement_of(text, definition)
    assert not isinstance(placement, ReadFailure), placement
    assert placement.detached == ()
    found = [
        (owner.kind, text.count("\n", 0, owner.anchor) + 1)
        for owner in placement.declarations
    ]
    for owner in placement.declarations:
        assert owner.anchor == owner.header.start
    return found


def test_owners_every_item_keyword_at_file_level(rust_definition):
    text = (
        "fn f() {}\n"
        "struct S;\n"
        "enum E {}\n"
        "union U { a: u8 }\n"
        "trait T {}\n"
        "impl S {}\n"
        "mod m;\n"
        "type A = u8;\n"
        "const C: u8 = 1;\n"
        "static X: u8 = 1;\n"
        "extern crate k;\n"
        "use a::b;\n"
        'extern "C" {}\n'
        "macro_rules! mac { () => {} }\n"
    )
    assert placed(text, rust_definition) == [("item", line) for line in range(1, 15)]


def test_owners_empty_source_has_no_owner(rust_definition):
    assert placed("", rust_definition) == []


def test_owners_nested_module(rust_definition):
    text = "mod x {\n    fn y() {}\n}\n"
    assert placed(text, rust_definition) == [("item", 1), ("item", 2)]


def test_owners_associated_items_and_items_in_extern(rust_definition):
    text = (
        "impl S {\n"
        "    const K: u8 = 1;\n"
        "    fn a(&self) {}\n"
        "}\n"
        "trait T {\n"
        "    type O;\n"
        "    fn b();\n"
        "}\n"
        'extern "C" {\n'
        "    fn f();\n"
        "    static G: u8;\n"
        "}\n"
    )
    assert placed(text, rust_definition) == [
        ("item", 1),
        ("associated-item", 2),
        ("associated-item", 3),
        ("item", 5),
        ("associated-item", 6),
        ("associated-item", 7),
        ("item", 9),
        ("item", 10),
        ("item", 11),
    ]


def test_owners_fields_and_variants(rust_definition):
    text = (
        "struct P {\n"
        "    pub x: i32,\n"
        "    #[serde] y: u8,\n"
        "}\n"
        "struct Q(\n"
        "    i32,\n"
        "    pub(crate) u8,\n"
        ");\n"
        "enum E {\n"
        "    A,\n"
        "    B(i32),\n"
        "    C {\n"
        "        d: u8,\n"
        "    },\n"
        "    D = 4,\n"
        "}\n"
        "union V {\n"
        "    w: u8,\n"
        "}\n"
    )
    assert placed(text, rust_definition) == [
        ("item", 1),
        ("field", 2),
        ("field", 3),
        ("item", 5),
        ("field", 6),
        ("field", 7),
        ("item", 9),
        ("variant", 10),
        ("variant", 11),
        ("variant", 12),
        ("field", 13),
        ("variant", 15),
        ("item", 17),
        ("field", 18),
    ]


def test_owners_tuple_variant_fields_are_opaque(rust_definition):
    text = "enum E {\n    B(\n        i32,\n    ),\n}\n"
    assert placed(text, rust_definition) == [("item", 1), ("variant", 2)]


def test_owners_items_in_a_function_body_and_no_statements(rust_definition):
    text = (
        "fn outer(a: u8, b: u8) -> u8 {\n"
        "    let x = a;\n"
        "    struct Local;\n"
        "    match x {\n"
        "        0 => 1,\n"
        "        _ => b,\n"
        "    };\n"
        '    println!("{}", x);\n'
        "    fn inner<T>() {}\n"
        "    {\n"
        "        const K: u8 = 2;\n"
        "    }\n"
        "    x\n"
        "}\n"
    )
    assert placed(text, rust_definition) == [
        ("item", 1),
        ("nested-item", 3),
        ("nested-item", 9),
        ("nested-item", 11),
    ]


def test_owners_parameters_and_generic_parameters_get_none(rust_definition):
    text = (
        "fn g<\n"
        "    T,\n"
        "    U,\n"
        ">(\n"
        "    a: T,\n"
        "    b: U,\n"
        ") {}\n"
        "struct W<\n"
        "    T,\n"
        "> {\n"
        "    t: T,\n"
        "}\n"
    )
    assert placed(text, rust_definition) == [("item", 1), ("item", 8), ("field", 11)]


def test_owners_braces_after_qualifiers_are_not_items(rust_definition):
    text = "fn f() {\n    const { 1 };\n    unsafe { g() };\n    async {};\n}\n"
    assert placed(text, rust_definition) == [("item", 1)]


def test_owners_same_line_members_get_none(rust_definition):
    text = (
        "enum Dir { N, S }\n"
        "struct P(i32, i32);\n"
        "struct R { x: i32,\n"
        "    y: i32 }\n"
        "fn a() {} fn b() {}\n"
        "#[derive(Debug)]\n"
        "struct T { z: u8,\n"
        "}\n"
    )
    assert placed(text, rust_definition) == [
        ("item", 1),
        ("item", 2),
        ("item", 3),
        ("field", 4),
        ("item", 5),
        ("item", 6),
    ]


@pytest.mark.parametrize(
    "text",
    [
        "fn a() {\n} fn b() {}\n",
        "fn a() {\n    let x = 1; fn f() {}\n}\n",
        "enum E\n{ A,\n}\n",
        "fn f(\n    x: u8,\n) { fn inner() {} }\n",
        "struct W<\n    T,\n> { t: T,\n}\n",
    ],
    ids=[
        "after-close",
        "after-statement",
        "after-open",
        "after-params",
        "after-generics",
    ],
)
def test_owners_get_no_place_behind_code_on_their_line(rust_definition, text):
    assert placed(text, rust_definition) == [("item", 1)]


def test_owners_attribute_leading_its_line_gives_a_place(rust_definition):
    assert placed("x;\n#[a] fn f() {}\n", rust_definition) == [("item", 2)]
    assert placed("x; #[a] fn f() {}\n", rust_definition) == []


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (
            "# [derive(Debug)]\npub struct P {\n    x: u8,\n}\n",
            [("item", 1), ("field", 3)],
        ),
        ("#\n/* c */ [a]\nfn f() {}\n", [("item", 1)]),
        ("#! [allow(x)]\nfn f() {}\n", [("item", 2)]),
    ],
    ids=["spaced-outer", "comment-between", "spaced-inner"],
)
def test_owners_an_attribute_opener_may_be_spaced(rust_definition, text, expected):
    assert placed(text, rust_definition) == expected


def test_owners_code_before_ends_where_a_multi_line_literal_closes(rust_definition):
    text = 'const S: &str = "a\nb"; fn f() {}\nfn g() {}\n'
    assert placed(text, rust_definition) == [("item", 1), ("item", 3)]


def test_owners_separators_inside_generic_arguments_are_not_members(rust_definition):
    text = "struct S {\n    map: HashMap<\n        String,\n        u8,\n    >,\n}\n"
    assert placed(text, rust_definition) == [("item", 1), ("field", 2)]


@pytest.mark.parametrize(
    ("text", "kind"),
    [
        ("enum E {\n    A = 1 << 0,\n    B = 1 << 1,\n    C,\n}\n", "variant"),
        ("enum E {\n    A = 2 >> 1,\n    B = 1 < 2,\n    C,\n}\n", "variant"),
        ("struct S {\n    a: Vec<u8> = 1 << 0,\n    b: u8,\n    c: u8,\n}\n", "field"),
    ],
    ids=["shift", "closer-then-opener", "default-value"],
)
def test_owners_angles_after_a_members_value_are_operators(rust_definition, text, kind):
    assert placed(text, rust_definition) == [
        ("item", 1),
        (kind, 2),
        (kind, 3),
        (kind, 4),
    ]


def test_owners_an_equals_inside_generic_arguments_is_not_a_value(rust_definition):
    text = (
        "struct S {\n    a: Box<dyn Iterator<Item = u8>>,\n"
        "    b: HashMap<\n        u8,\n        u8,\n    >,\n}\n"
    )
    assert placed(text, rust_definition) == [("item", 1), ("field", 2), ("field", 3)]


@pytest.mark.parametrize(
    ("text", "member"),
    [
        ("struct S<F: Fn() -> (u8)> {\n    x: F,\n}\n", ("field", 2)),
        ("struct S<const N: usize = {3}> {\n    x: u8,\n}\n", ("field", 2)),
        ("impl Foo<{ N }> {\n    fn a() {}\n}\n", ("associated-item", 2)),
        ("struct T<F: Fn() -> u8>(\n    F,\n);\n", ("field", 2)),
    ],
    ids=["arrow", "const-default", "const-argument", "tuple-after-arrow"],
)
def test_owners_body_opens_after_generic_arguments_close(rust_definition, text, member):
    assert placed(text, rust_definition) == [("item", 1), member]


def with_owners(definition, owners):
    """The definition with `[rules.documentation].owners` replaced."""
    from dataclasses import replace

    documentation = dict(definition.rules["documentation"])
    documentation["owners"] = owners
    rules = dict(definition.rules)
    rules["documentation"] = documentation
    return replace(definition, rules=rules)


def owners_refusal(definition, owners):
    from comment_review.reading.rust.definition import validate_rust

    return validate_rust(with_owners(definition, owners))


@pytest.mark.parametrize(
    "owners",
    [("item", "statement"), ("item", "field", "item"), ()],
    ids=["unknown", "duplicate", "empty"],
)
def test_owners_validator_refuses_an_unsupported_list(rust_definition, owners):
    failure = owners_refusal(rust_definition, owners)
    assert isinstance(failure, ReadFailure)
    assert failure.diagnostics[0].code == "invalid-language-definition"


def test_owners_validator_accepts_a_subset(rust_definition):
    assert owners_refusal(rust_definition, ("module", "item")) is None


def test_owners_kind_not_in_the_definition_owners_gets_no_place(rust_definition):
    shipped = rust_definition.rules["documentation"]["owners"]
    narrowed = with_owners(
        rust_definition, tuple(owner for owner in shipped if owner != "variant")
    )
    structure = import_module("comment_review.reading.rust.structure")
    text = "enum E {\n    A,\n    B {\n        c: u8,\n    },\n}\n"
    result = structure.place_declarations(scanned(text, narrowed), narrowed)
    assert not isinstance(result, ReadFailure)
    assert [
        (d.kind, text.count("\n", 0, d.anchor) + 1) for d in result.declarations
    ] == [
        ("item", 1),
        ("field", 4),
    ]
    assert placed(text, rust_definition) == [
        ("item", 1),
        ("variant", 2),
        ("variant", 3),
        ("field", 4),
    ]


def test_owners_qualifier_or_keyword_resolves_once(rust_definition):
    text = (
        "const fn f() {}\n"
        "const X: u8 = 1;\n"
        "extern crate a;\n"
        'extern "C" fn g() {}\n'
        'extern "C" {\n'
        "    fn h();\n"
        "}\n"
        'unsafe extern "C" fn k() {}\n'
        "pub unsafe auto trait Z {}\n"
    )
    assert placed(text, rust_definition) == [
        ("item", 1),
        ("item", 2),
        ("item", 3),
        ("item", 4),
        ("item", 5),
        ("item", 6),
        ("item", 8),
        ("item", 9),
    ]


def test_owners_visibility_scopes(rust_definition):
    text = "pub(crate) fn v() {}\npub(in a::b) struct W;\npub(super) mod m;\n"
    assert placed(text, rust_definition) == [("item", 1), ("item", 2), ("item", 3)]


def test_owners_union_as_an_identifier_is_not_an_item(rust_definition):
    text = "fn f() {\n    let union = 1;\n    union = 2;\n}\nunion U {\n    a: u8,\n}\n"
    assert placed(text, rust_definition) == [("item", 1), ("item", 5), ("field", 6)]


def test_owners_refuses_an_invalid_definition(rust_definition):
    from dataclasses import replace

    scan_result = scanned("fn f() {}", rust_definition)
    structure = import_module("comment_review.reading.rust.structure")
    result = structure.place_declarations(
        scan_result, replace(rust_definition, revision="9")
    )
    assert isinstance(result, ReadFailure)


@pytest.mark.parametrize(
    "attribute",
    ["#[test]", "#[cfg(\n    x,\n)]", '#[doc = "]"]'],
    ids=["single-line", "multi-line", "string-close"],
)
def test_heads_start_at_the_attribute(rust_definition, attribute):
    text = f"fn z() {{}}\n\n{attribute}\nfn a() {{}}\n"
    assert placed(text, rust_definition) == [("item", 1), ("item", 3)]


def test_heads_two_attributes_give_the_first(rust_definition):
    text = "#[a]\n// note\n#[b]\nfn c() {}\n"
    assert placed(text, rust_definition) == [("item", 1)]


def test_heads_attribute_on_the_item_line(rust_definition):
    text = "fn z() {}\n#[inline] fn f() {}\n"
    assert placed(text, rust_definition) == [("item", 1), ("item", 2)]


def test_heads_header_runs_from_the_head_to_the_keyword_line_code(rust_definition):
    text = "#[a]\npub fn f(\n    x: u8,\n) {} // tail\nstruct S { // c\n}\n"
    placement = placement_of(text, rust_definition)
    assert not isinstance(placement, ReadFailure)
    assert [text[d.header.start : d.header.end] for d in placement.declarations] == [
        "#[a]\npub fn f(",
        "struct S {",
    ]


def test_heads_attributes_on_statements_arms_and_parameters_create_no_place(
    rust_definition,
):
    text = (
        "fn f(#[a] x: u8) {\n"
        "    #[allow(unused)]\n"
        "    let y = x;\n"
        "    match y {\n"
        "        #[cfg(a)]\n"
        "        0 => {}\n"
        "        _ => {}\n"
        "    }\n"
        "}\n"
    )
    assert placed(text, rust_definition) == [("item", 1)]


def test_heads_member_attribute(rust_definition):
    text = "struct P {\n    #[a]\n    #[b]\n    x: u8,\n}\n"
    assert placed(text, rust_definition) == [("item", 1), ("field", 2)]


def test_macros_bodies_hold_no_places(rust_definition):
    text = (
        "macro_rules! m {\n"
        "    () => {\n"
        "        fn hidden() {}\n"
        "    };\n"
        "}\n"
        "foo! {\n"
        "    fn also_hidden() {}\n"
        "}\n"
        "bar!(\n"
        "    fn too() {}\n"
        ");\n"
        "fn seen() {}\n"
    )
    assert placed(text, rust_definition) == [("item", 1), ("item", 12)]


def test_macros_invocation_above_an_item_is_not_its_head(rust_definition):
    text = "#[a]\nfoo! {}\nfn x() {}\nmacro_rules! n ( () => {} );\nfn y() {}\n"
    assert placed(text, rust_definition) == [("item", 3), ("item", 4), ("item", 5)]


def line_of(text, offset):
    return text.count("\n", 0, offset) + 1


def documentation_of(text, definition):
    try:
        documentation = import_module("comment_review.reading.rust.documentation")
    except ModuleNotFoundError:
        pytest.fail("Rust documentation is not implemented", pytrace=False)
    structure = import_module("comment_review.reading.rust.structure")
    scan_result = scanned(text, definition)
    placement = structure.place_declarations(scan_result, definition)
    assert not isinstance(placement, ReadFailure), placement
    result = documentation.documentation_in(scan_result, placement, definition)
    assert not isinstance(result, ReadFailure), result
    return result


def sections_of(text, result):
    """Each section as (form, its exact text)."""
    return [
        (section.form, text[section.span.start : section.span.end])
        for section in result.sections
    ]


def owners_of(text, result):
    """Each owned section's text, with its owner's (kind, head line) or None."""
    found = []
    for owner in result.owners:
        span = result.sections[owner.section].span
        declaration = (
            None
            if owner.declaration is None
            else result.placement.declarations[owner.declaration]
        )
        found.append(
            (
                text[span.start : span.end],
                None
                if declaration is None
                else (declaration.kind, line_of(text, declaration.anchor)),
            )
        )
    return found


def detached_of(text, result):
    """Each detached run's text, and each warning's text and the lines it names."""
    runs = [text[run.span.start : run.span.end] for run in result.placement.detached]
    notes = []
    for warning in result.warnings:
        assert warning.stage is ReadStage.PLACE
        assert warning.code == "detached-documentation"
        assert warning.span is not None
        notes.append(
            (
                text[warning.span.start : warning.span.end],
                [int(n) for n in re.findall(r"line (\d+)", warning.message)],
            )
        )
    return runs, notes


def test_sections_comments_and_a_detached_doc_with_no_code_between_are_one(
    rust_definition,
):
    text = "fn a() {}\n// one\n/// two\n// three\nfn b() {}\n"
    result = documentation_of(text, rust_definition)
    assert sections_of(text, result) == [("comment", "// one\n/// two\n// three")]
    # The detached run keeps its own record and warning.
    assert detached_of(text, result) == (
        ["/// two"],
        [("/// two", [3, 5])],
    )


def test_sections_code_between_comments_ends_a_section(rust_definition):
    text = "fn a() {}\n// one\n\n// two\nfn b() {}\n// three\nfn c() {}\n"
    result = documentation_of(text, rust_definition)
    assert sections_of(text, result) == [
        ("comment", "// one\n\n// two"),
        ("comment", "// three"),
    ]


def test_attachment_doc_above_a_multi_line_attribute_across_blank_lines(
    rust_definition,
):
    text = "/// Doc.\n\n#[cfg(\n    x,\n)]\nfn f() {}\n"
    result = documentation_of(text, rust_definition)
    assert sections_of(text, result) == [("outer_doc", "/// Doc.")]
    assert owners_of(text, result) == [("/// Doc.", ("item", 3))]
    assert anchor_lines(text, result.placement) == (3,)
    assert result.placement.detached == ()
    assert result.warnings == ()


def test_attachment_a_doc_run_stays_whole_across_blank_lines(rust_definition):
    text = "fn z() {}\n/// a\n\n/// b\nfn f() {}\n"
    result = documentation_of(text, rust_definition)
    assert sections_of(text, result) == [("outer_doc", "/// a\n\n/// b")]
    assert owners_of(text, result) == [("/// a\n\n/// b", ("item", 5))]


def test_attachment_doc_above_a_field_and_a_variant(rust_definition):
    text = (
        "struct S {\n    /// x doc\n    x: u8,\n}\nenum E {\n    /// A doc\n    A,\n}\n"
    )
    result = documentation_of(text, rust_definition)
    assert owners_of(text, result) == [
        ("/// x doc", ("field", 3)),
        ("/// A doc", ("variant", 7)),
    ]


def test_attachment_delimited_outer_doc_attaches(rust_definition):
    text = "/** Doc\n * more. */\nfn f() {}\n"
    result = documentation_of(text, rust_definition)
    assert sections_of(text, result) == [("outer_doc", "/** Doc\n * more. */")]
    assert owners_of(text, result) == [("/** Doc\n * more. */", ("item", 3))]


@pytest.mark.parametrize(
    "text",
    [
        "fn f() {\n    /// stray\n}\n",
        "fn f() {\n    /// stray\n    let x = 1;\n}\n",
        "fn f() {}\n/// stray\n",
    ],
    ids=["before-close", "before-statement", "end-of-file"],
)
def test_attachment_doc_with_no_following_owner_is_ordinary(rust_definition, text):
    result = documentation_of(text, rust_definition)
    assert sections_of(text, result) == [("comment", "/// stray")]
    assert result.owners == ()
    assert result.placement.detached == ()
    assert result.warnings == ()


def test_attachment_inner_doc_at_file_head_is_the_module(rust_definition):
    text = "//! Crate doc.\n\nfn f() {}\n"
    result = documentation_of(text, rust_definition)
    assert sections_of(text, result) == [("inner_doc", "//! Crate doc.")]
    assert owners_of(text, result) == [("//! Crate doc.", None)]
    assert anchor_lines(text, result.placement) == (3,)


def test_detached_inner_doc_after_an_inner_attribute(rust_definition):
    """Code before the module's doc, an inner attribute, keeps it from `a0`,
    which the page sets at the file head."""
    text = "#![allow(x)]\n/*! Crate doc. */\nfn f() {}\n"
    result = documentation_of(text, rust_definition)
    assert sections_of(text, result) == [("comment", "/*! Crate doc. */")]
    assert result.owners == ()
    assert detached_of(text, result) == (
        ["/*! Crate doc. */"],
        [("/*! Crate doc. */", [2])],
    )
    assert anchor_lines(text, result.placement) == (3,)


@pytest.mark.parametrize(
    ("text", "doc", "doc_line"),
    [
        ("mod x {\n    //! Inner.\n    fn g() {}\n}\n", "//! Inner.", 2),
        ("fn f() {\n    //! Inner.\n}\n", "//! Inner.", 2),
        ("impl S {\n    /*! Inner. */\n    fn g() {}\n}\n", "/*! Inner. */", 2),
        (
            "mod x {\n    #![allow(x)]\n    //! Late.\n    fn g() {}\n}\n",
            "//! Late.",
            3,
        ),
        ("fn f() {\n    let x = 1;\n    //! Mid.\n}\n", "//! Mid.", 3),
        ("fn f() {\n    if x {\n        //! Deep.\n    }\n}\n", "//! Deep.", 3),
    ],
    ids=["mod", "fn", "impl", "after-inner-attribute", "after-a-statement", "block"],
)
def test_detached_inner_doc_in_a_body_names_the_item_that_holds_it(
    rust_definition, text, doc, doc_line
):
    result = documentation_of(text, rust_definition)
    assert sections_of(text, result) == [("comment", doc)]
    assert result.owners == ()
    assert detached_of(text, result) == ([doc], [(doc, [doc_line, 1])])
    # The item that holds the doc is the first declaration, on line 1.
    assert anchor_lines(text, result.placement)[0] == 1


def test_attachment_ordinary_comment_above_an_item_is_not_documentation(
    rust_definition,
):
    text = "fn z() {}\n// note\nfn f() {}\n"
    result = documentation_of(text, rust_definition)
    assert sections_of(text, result) == [("comment", "// note")]
    assert result.owners == ()


def test_attachment_outer_doc_and_adjacent_ordinary_comment_are_separate(
    rust_definition,
):
    text = "fn z() {}\n// note\n/// Doc.\nfn f() {}\n"
    result = documentation_of(text, rust_definition)
    assert sections_of(text, result) == [
        ("comment", "// note"),
        ("outer_doc", "/// Doc."),
    ]
    assert owners_of(text, result) == [("/// Doc.", ("item", 4))]


def test_attachment_trailing_comment_is_its_own_section(rust_definition):
    text = "fn z() {} // tail\n// next\nfn f() {}\n"
    result = documentation_of(text, rust_definition)
    assert sections_of(text, result) == [
        ("comment", "// tail"),
        ("comment", "// next"),
    ]


def test_attachment_module_not_in_owners_leaves_the_head_inner_doc_ordinary(
    rust_definition,
):
    shipped = rust_definition.rules["documentation"]["owners"]
    narrowed = with_owners(
        rust_definition, tuple(owner for owner in shipped if owner != "module")
    )
    assert (
        owners_refusal(rust_definition, narrowed.rules["documentation"]["owners"])
        is None
    )
    text = "//! Crate doc.\nfn f() {}\n"
    result = documentation_of(text, narrowed)
    # Documenting nothing, the run opening the file is its matter.
    assert sections_of(text, result) == [("matter", "//! Crate doc.")]
    assert result.owners == ()
    assert anchor_lines(text, result.placement) == (2,)
    assert result.warnings == ()


def test_attachment_inline_module_inner_doc_follows_its_declaration_kind(
    rust_definition,
):
    shipped = rust_definition.rules["documentation"]["owners"]
    narrowed = with_owners(
        rust_definition, tuple(owner for owner in shipped if owner != "item")
    )
    text = "mod x {\n    //! Inner.\n}\n"
    result = documentation_of(text, narrowed)
    assert sections_of(text, result) == [("comment", "//! Inner.")]
    assert result.owners == ()


@pytest.mark.parametrize(
    ("text", "sections", "owners", "detached"),
    [
        (
            "/// a\n// b\nfn f() {}\n",
            # Both open the file, so both are its matter.
            [("matter", "/// a"), ("matter", "// b")],
            [],
            ("/// a", 3, 1),
        ),
        (
            "#[inline]\n/// a\nfn f() {}\n",
            [("comment", "/// a")],
            [],
            ("/// a", 1, 2),
        ),
        (
            "/// a\n#[inline]\n/// b\nfn f() {}\n",
            [("outer_doc", "/// a"), ("comment", "/// b")],
            [("/// a", ("item", 2))],
            ("/// b", 2, 3),
        ),
    ],
    ids=["behind-ordinary-comment", "behind-attribute", "second-run"],
)
def test_detached_documentation_is_ordinary_with_a_warning(
    rust_definition, text, sections, owners, detached
):
    run, head_line, run_line = detached
    result = documentation_of(text, rust_definition)
    assert sections_of(text, result) == sections
    assert owners_of(text, result) == owners
    assert detached_of(text, result) == (
        [run],
        [(run, [run_line, head_line])],
    )


def test_detached_inner_doc_behind_a_comment_in_its_body(rust_definition):
    text = "fn f() {\n    // a\n    //! inner\n}\n"
    result = documentation_of(text, rust_definition)
    assert sections_of(text, result) == [("comment", "// a\n    //! inner")]
    assert result.owners == ()
    assert detached_of(text, result) == (
        ["//! inner"],
        [("//! inner", [3, 1])],
    )
    assert anchor_lines(text, result.placement) == (1,)


def test_detached_inner_doc_on_its_owner_head_line(rust_definition):
    text = "fn f() { //! same line\n}\n"
    result = documentation_of(text, rust_definition)
    assert sections_of(text, result) == [("comment", "//! same line")]
    assert result.owners == ()
    assert detached_of(text, result) == (
        ["//! same line"],
        [("//! same line", [1, 1])],
    )


def test_detached_module_doc_behind_a_comment_that_is_not_matter(rust_definition):
    text = "\n// a\n//! m\n// c\nfn f() {}\n"
    result = documentation_of(text, rust_definition)
    assert sections_of(text, result) == [("comment", "// a\n//! m\n// c")]
    assert result.owners == ()
    assert detached_of(text, result) == (["//! m"], [("//! m", [3])])
    assert anchor_lines(text, result.placement) == (5,)


def test_detached_module_doc_behind_a_trailing_comment(rust_definition):
    text = "#![allow(x)] // c\n//! m\nfn f() {}\n"
    result = documentation_of(text, rust_definition)
    assert sections_of(text, result) == [("comment", "// c"), ("comment", "//! m")]
    assert detached_of(text, result) == (["//! m"], [("//! m", [2])])


@pytest.mark.parametrize(
    ("text", "lines"),
    [
        ("// Copyright\n//! m\nfn f() {}\n", (3,)),
        ("#!/usr/bin/env rust-script\n// Copyright\n//! m\nfn f() {}\n", (4,)),
    ],
    ids=["plain", "shebang"],
)
def test_attachment_module_doc_behind_front_matter(rust_definition, text, lines):
    result = documentation_of(text, rust_definition)
    assert sections_of(text, result) == [
        ("matter", "// Copyright"),
        ("inner_doc", "//! m"),
    ]
    assert owners_of(text, result) == [("//! m", None)]
    assert result.placement.detached == ()
    assert anchor_lines(text, result.placement) == lines


def test_matter_opening_detached_doc_is_matter(rust_definition):
    text = "/** Doc. */\n// c\nfn f() {}\n"
    result = documentation_of(text, rust_definition)
    assert sections_of(text, result) == [("matter", "/** Doc. */"), ("matter", "// c")]
    assert detached_of(text, result) == (
        ["/** Doc. */"],
        [("/** Doc. */", [1, 3])],
    )
    assert anchor_lines(text, result.placement) == (3,)


def test_matter_ends_at_the_module_doc(rust_definition):
    text = "// Copyright\n//! m\n// c\nfn f() {}\n"
    result = documentation_of(text, rust_definition)
    assert sections_of(text, result) == [
        ("matter", "// Copyright"),
        ("inner_doc", "//! m"),
        ("comment", "// c"),
    ]


def test_detached_inner_doc_first_in_its_body_after_a_blank_line(
    rust_definition,
):
    text = "fn f() {\n\n    //! inner\n    // after\n}\n"
    result = documentation_of(text, rust_definition)
    assert result.owners == ()
    assert detached_of(text, result) == (
        ["//! inner"],
        [("//! inner", [3, 1])],
    )


def test_detached_second_inner_doc_in_an_inline_module(rust_definition):
    text = "/// Outer.\nmod x {\n    //! Inner.\n}\n"
    result = documentation_of(text, rust_definition)
    assert sections_of(text, result) == [
        ("outer_doc", "/// Outer."),
        ("comment", "//! Inner."),
    ]
    assert owners_of(text, result) == [("/// Outer.", ("item", 2))]
    assert detached_of(text, result) == (
        ["//! Inner."],
        [("//! Inner.", [3, 2])],
    )


def test_detached_second_inner_doc_for_the_module(
    rust_definition,
):
    text = "//! a\n#![allow(x)]\n//! b\nfn f() {}\n"
    result = documentation_of(text, rust_definition)
    assert sections_of(text, result) == [
        ("inner_doc", "//! a"),
        ("comment", "//! b"),
    ]
    assert owners_of(text, result) == [("//! a", None)]
    assert detached_of(text, result) == (["//! b"], [("//! b", [3])])
    assert anchor_lines(text, result.placement) == (4,)


def test_attachment_doc_on_its_owner_head_line_is_code(rust_definition):
    text = "/** d */ fn f() {}\n"
    result = documentation_of(text, rust_definition)
    assert sections_of(text, result) == []
    assert result.owners == ()
    assert detached_of(text, result) == ([], [])


def test_detached_trailing_doc_above_an_owner(rust_definition):
    text = "fn z() {} /// t\nfn f() {}\n"
    result = documentation_of(text, rust_definition)
    assert sections_of(text, result) == [("comment", "/// t")]
    assert result.owners == ()
    assert detached_of(text, result) == (["/// t"], [("/// t", [1, 2])])


def documentation_record(detached, warned):
    """A RustDocumentation over two comment sections, `a` and `b`, and one item."""
    spans = {"a": SourceSpan(0, 5), "b": SourceSpan(6, 11)}
    placement = records.RustPlacement(
        (SourceDeclaration(SourceSpan(12, 14), 12, "item"),),
        tuple(records.DetachedRun(spans[name]) for name in detached),
    )
    return records.RustDocumentation(
        tuple(SourceSection(span, "comment") for span in spans.values()),
        (),
        placement,
        tuple(warning(spans[name]) for name in warned),
    )


def test_detached_records_accept_warnings_aligned_with_runs():
    documentation_record("ab", "ab")


@pytest.mark.parametrize(
    ("detached", "warned"),
    [("ab", "a"), ("a", "ab"), ("ab", "ba")],
    ids=["extra-run", "missing-run", "reordered"],
)
def test_detached_records_refuse_misaligned_warnings(detached, warned):
    with pytest.raises(ValueError):
        documentation_record(detached, warned)


@pytest.mark.parametrize(
    ("declaration", "refused"), [(None, False), (0, True)], ids=["module", "item"]
)
def test_detached_records_let_an_inner_doc_document_only_the_module(
    declaration, refused
):
    placement = records.RustPlacement(
        (SourceDeclaration(SourceSpan(12, 14), 12, "item"),), ()
    )

    def made():
        return records.RustDocumentation(
            (SourceSection(SourceSpan(0, 5), "inner_doc"),),
            (DocumentationOwner(0, declaration),),
            placement,
            (),
        )

    if refused:
        with pytest.raises(ValueError, match="only the module"):
            made()
    else:
        made()


def test_matter_excludes_a_comment_with_code_after_it_on_its_line(rust_definition):
    text = "/* a */ fn f() {}\n"
    result = documentation_of(text, rust_definition)
    assert sections_of(text, result) == []
    assert anchor_lines(text, result.placement) == (1,)


def test_matter_opening_ordinary_run_is_not_the_item_doc(rust_definition):
    text = "// Copyright 2026 Someone.\n// Licensed.\nfn main() {}\n"
    result = documentation_of(text, rust_definition)
    assert sections_of(text, result) == [
        ("matter", "// Copyright 2026 Someone.\n// Licensed."),
    ]
    assert result.owners == ()
    assert anchor_lines(text, result.placement) == (3,)


def test_matter_follows_a_shebang(rust_definition):
    """The run directly below the shebang opens the file, so it is matter."""
    text = "#!/usr/bin/env run-cargo-script\n// Copyright.\n\nfn main() {}\n"
    result = documentation_of(text, rust_definition)
    assert sections_of(text, result) == [("matter", "// Copyright.")]
    assert anchor_lines(text, result.placement) == (4,)


def test_comment_below_a_shebang_and_a_blank_line_is_not_matter(rust_definition):
    text = "#!/usr/bin/env run-cargo-script\n\n// Copyright.\nfn main() {}\n"
    result = documentation_of(text, rust_definition)
    assert sections_of(text, result) == [("comment", "// Copyright.")]


def test_comment_below_a_blank_line_one_is_not_matter(rust_definition):
    text = "\n// Copyright.\nfn main() {}\n"
    result = documentation_of(text, rust_definition)
    assert sections_of(text, result) == [("comment", "// Copyright.")]


def test_matter_then_a_doc_gives_the_item_its_doc(rust_definition):
    text = "// Copyright.\n/// Doc.\nfn main() {}\n"
    result = documentation_of(text, rust_definition)
    assert sections_of(text, result) == [
        ("matter", "// Copyright."),
        ("outer_doc", "/// Doc."),
    ]
    assert owners_of(text, result) == [("/// Doc.", ("item", 3))]
    assert anchor_lines(text, result.placement) == (3,)


def directives_of(text, definition):
    try:
        directives = import_module("comment_review.reading.rust.directives")
    except ModuleNotFoundError:
        pytest.fail("Rust directives are not implemented", pytrace=False)
    return directives.directives_in(scanned(text, definition), definition)


def test_directives_shebang_is_a_protected_directive(rust_definition):
    text = "#!/usr/bin/env run-cargo-script\nfn main() {}\n"
    result = scanned(text, rust_definition)
    assert shape(result)[0] == (
        RegionKind.DIRECTIVE,
        "#!/usr/bin/env run-cargo-script",
    )
    assert directives_of(text, rust_definition) == (SourceSpan(0, 31),)
    assert anchor_lines(text, documentation_of(text, rust_definition).placement) == (2,)


@pytest.mark.parametrize(
    ("text", "span"),
    [
        ("\ufeff#!/bin/x\n", SourceSpan(1, 9)),
        ("#!/bin/x\r\nfn f() {}", SourceSpan(0, 8)),
    ],
    ids=["byte-order-mark", "crlf"],
)
def test_directives_shebang_runs_to_the_end_of_line_one(rust_definition, text, span):
    assert directives_of(text, rust_definition) == (span,)


@pytest.mark.parametrize(
    "text",
    [
        "#![allow(x)]\n",
        "#! [x]\n",
        "#!/*c*/[x]\n",
        "#!\n// c\n[x]\n",
        "fn f() {}\n#!/x\n",
    ],
    ids=["inner-attribute", "spaced", "comment", "next-line", "not-line-one"],
)
def test_directives_bang_before_a_bracket_is_code(rust_definition, text):
    result = scanned(text, rust_definition)
    assert all(region.kind is not RegionKind.DIRECTIVE for region in result.regions)
    assert directives_of(text, rust_definition) == ()


PAGE = Path("src/lib.rs")


def rust_read(text, definition):
    """The composed Rust read of `text`, which must not fail."""
    result = import_module("comment_review.reading.rust").read_rust(text, definition)
    assert isinstance(result, records.RustRead), result
    return result


def projection_of(text, definition):
    """The read's paragraphs and its code lines."""
    result = rust_read(text, definition)
    paragraphs = result.paragraphs(PAGE)
    assert not isinstance(paragraphs, ReadFailure), paragraphs
    return paragraphs, result.code_lines()


def code_of(lines):
    """Each code line's number and code, for tests that check only the code."""
    return {line.line: line.code for line in lines}


def paragraph(start, end, kind, raw, *, anchor_line=None, anchor=""):
    return Paragraph(
        PAGE.as_posix(),
        start,
        end,
        kind,
        anchor=anchor,
        anchor_line=anchor_line,
        raw_lines=raw,
    )


def test_projection_of_docs_comments_code_and_declarations(rust_definition):
    text = (
        "//! Crate doc.\n"
        "\n"
        "/// A point.\n"
        "#[derive(Debug)]\n"
        "struct P {\n"
        "    /// Across.\n"
        "    x: u8,\n"
        "}\n"
        "\n"
        "fn go() -> u8 { 1 } // tail\n"
        "fn mix() -> u8 { 2 /* why */ + 3 }\n"
    )
    paragraphs, lines = projection_of(text, rust_definition)
    assert paragraphs == [
        # The inner doc is the module's and names no line; each item doc names
        # its item's declaring line, the attribute above `struct P` included.
        paragraph(1, 1, Kind.DOCSTRING, ["//! Crate doc."]),
        paragraph(3, 3, Kind.DOCSTRING, ["/// A point."], anchor_line=4),
        paragraph(6, 6, Kind.DOCSTRING, ["    /// Across."], anchor_line=7),
        paragraph(10, 10, Kind.TRAILING, [" // tail"], anchor="fn go() -> u8 { 1 }"),
    ]
    assert lines == [
        CodeLine(4, "#[derive(Debug)]", DocPlace(4, True)),
        CodeLine(5, "struct P {", None),
        CodeLine(7, "    x: u8,", DocPlace(7, True)),
        CodeLine(8, "}", None),
        CodeLine(10, "fn go() -> u8 { 1 }", DocPlace(10, True)),
        CodeLine(11, "fn mix() -> u8 { 2 /* why */ + 3 }", DocPlace(11, True)),
    ]


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (
            "x; /** a */ // b\n",
            [paragraph(1, 1, Kind.TRAILING, [" /** a */ // b"], anchor="x;")],
        ),
        (
            "x; /* a */ /** b */\n",
            [paragraph(1, 1, Kind.TRAILING, [" /* a */ /** b */"], anchor="x;")],
        ),
        (
            # The outer doc has a comment after it on its line, the inner doc
            # one before it: both are detached, and all three open the file.
            "/** a */ /*! b */ /* c */\nfn f() {}\n",
            [
                paragraph(
                    1,
                    1,
                    Kind.MATTER,
                    ["/** a */ /*! b */ /* c */"],
                )
            ],
        ),
        (
            # The comments on the trailing comment's last line share its place.
            "fn a() {} /* one\n two */ /** three */ // four\nfn b() {}\n",
            [
                paragraph(
                    1,
                    2,
                    Kind.TRAILING,
                    [" /* one", " two */ /** three */ // four"],
                    anchor="fn a() {}",
                )
            ],
        ),
        (
            "/// a\n/** b */ // c\n//! d\n",
            [
                paragraph(1, 2, Kind.MATTER, ["/// a", "/** b */ // c"]),
                paragraph(3, 3, Kind.DOCSTRING, ["//! d"]),
            ],
        ),
    ],
)
def test_projection_sections_sharing_a_line_are_one_paragraph(
    rust_definition, text, expected
):
    paragraphs, _ = projection_of(text, rust_definition)
    assert paragraphs == expected
    lines = [line for p in paragraphs for line in range(p.start, p.end + 1)]
    assert len(lines) == len(set(lines))


@pytest.mark.parametrize(
    ("text", "expected", "code"),
    [
        (
            "// x\n/* y */ fn f() {}\n",
            [paragraph(1, 1, Kind.MATTER, ["// x"])],
            {2: "/* y */ fn f() {}"},
        ),
        (
            "/// a\n/** b */ fn f() {}\n",
            [paragraph(1, 1, Kind.MATTER, ["/// a"])],
            {2: "/** b */ fn f() {}"},
        ),
        (
            "#[x]\n/// a\n/** b */ fn f() {}\n",
            [paragraph(2, 2, Kind.COMMENT, ["/// a"])],
            {1: "#[x]", 3: "/** b */ fn f() {}"},
        ),
        (
            "fn z() {}\n// a\n// b /* c */\n/* d */ fn f() {}\n",
            [paragraph(2, 3, Kind.COMMENT, ["// a", "// b /* c */"])],
            {1: "fn z() {}", 4: "/* d */ fn f() {}"},
        ),
    ],
    ids=[
        "comment-above",
        "doc-above",
        "doc-between-attribute-and-item",
        "comment-run-above",
    ],
)
def test_projection_only_the_code_bounded_comment_is_code(
    rust_definition, text, expected, code
):
    result = rust_read(text, rust_definition)
    assert result.paragraphs(PAGE) == expected
    assert code_of(result.code_lines()) == code
    assert [w.span for w in result.warnings] == [r.span for r in result.detached]


def test_projection_read_refuses_a_doc_section_sharing_a_line(rust_definition):
    """Two comment sections may share a line; a documentation section may not,
    since its `a` place holds the doc alone."""
    from dataclasses import replace

    result = rust_read("x; /** a */ // b\n", rust_definition)
    doc, comment = result.source.sections
    assert (doc.form, comment.form) == ("comment", "comment")
    shared = SourceSection(doc.span, "outer_doc")
    with pytest.raises(ValueError, match="share"):
        replace(result, source=replace(result.source, sections=(shared, comment)))


@pytest.mark.parametrize(
    ("text", "paragraphs", "code"),
    [
        ("let_x /* c */ + 1;\n", [], {1: "let_x /* c */ + 1;"}),
        (
            "/* a */ fn f() {} // b\n",
            [paragraph(1, 1, Kind.TRAILING, [" // b"], anchor="/* a */ fn f() {}")],
            {1: "/* a */ fn f() {}"},
        ),
        (
            "fn a() {} /* one\n two */ fn b() {}\n",
            [],
            {1: "fn a() {} /* one", 2: " two */ fn b() {}"},
        ),
    ],
    ids=["between-code", "before-code-and-a-trailing-comment", "across-lines"],
)
def test_projection_delimited_comment_with_code_after_it_stays_code(
    rust_definition, text, paragraphs, code
):
    found, lines = projection_of(text, rust_definition)
    assert found == paragraphs
    assert code_of(lines) == code


def test_projection_delimited_comment_with_only_a_comment_after_it_is_prose(
    rust_definition,
):
    found, lines = projection_of("x; /** a */ // b\n", rust_definition)
    assert found == [paragraph(1, 1, Kind.TRAILING, [" /** a */ // b"], anchor="x;")]
    assert code_of(lines) == {1: "x;"}


@pytest.mark.parametrize(
    ("text", "code"),
    [
        (
            'fn f() {\n    let s = "a\n\nb";\n}\n',
            {1: "fn f() {", 2: '    let s = "a', 4: 'b";', 5: "}"},
        ),
        (
            'fn f() {\n    let s = r"a\n   \nb"; // c\n}\n',
            {1: "fn f() {", 2: '    let s = r"a', 4: 'b";', 5: "}"},
        ),
    ],
    ids=["blank", "whitespace-only"],
)
def test_projection_literal_line_with_no_code_is_absent(rust_definition, text, code):
    _, lines = projection_of(text, rust_definition)
    assert code_of(lines) == code


@pytest.mark.parametrize(
    "text",
    [
        'fn f() {\n    let s = "a   \nb";\n}\n',
        'fn f() {\n    let s = r"a \t\n  b  "; // c\n}\n',
        'let s = "a  \n" ;  \n',
    ],
    ids=["literal-ends-its-line", "literal-then-trailing-comment", "spaces-after"],
)
def test_projection_code_and_its_c_text_rebuild_the_line(rust_definition, text):
    """A line's code is what it holds before its prose, right-trimmed: the code
    plus the trailing paragraph's first raw line, or plus the whitespace after
    the code when no paragraph trails it, is the source line."""
    paragraphs, lines = projection_of(text, rust_definition)
    source = text.split("\n")
    trailing = {p.start: p for p in paragraphs if p.kind == Kind.TRAILING}
    for line in lines:
        whole = source[line.line - 1]
        assert line.code == line.code.rstrip()
        if line.line in trailing:
            assert trailing[line.line].anchor == line.code
            rest = trailing[line.line].raw_lines[0]
        else:
            rest = whole[len(whole.rstrip()) :]
        assert line.code + rest == whole


def test_projection_delimited_comment_with_code_only_before_it_trails(
    rust_definition,
):
    paragraphs, lines = projection_of("fn f() {} /* t */\n", rust_definition)
    assert paragraphs == [
        paragraph(1, 1, Kind.TRAILING, [" /* t */"], anchor="fn f() {}")
    ]
    assert code_of(lines) == {1: "fn f() {}"}


@pytest.mark.parametrize(
    "text",
    ["/** d */ fn f() {}\n", "/*! m */ fn f() {}\n"],
    ids=["outer-on-its-head-line", "inner-before-code"],
)
def test_projection_doc_with_code_after_it_is_code_and_documents_nothing(
    rust_definition, text
):
    result = rust_read(text, rust_definition)
    assert result.paragraphs(PAGE) == []
    assert code_of(result.code_lines()) == {1: text.rstrip("\n")}
    assert result.source.sections == ()
    assert result.source.documentation == ()
    assert result.warnings == ()
    assert result.detached == ()


def test_projection_rust_whitespace_is_not_code(rust_definition):
    text = "fn f() {}\v// t\nfn z() {}\n/* a */ \t\nfn g() {}\n"
    paragraphs, lines = projection_of(text, rust_definition)
    assert paragraphs == [
        paragraph(1, 1, Kind.TRAILING, ["\v// t"], anchor="fn f() {}"),
        paragraph(3, 3, Kind.COMMENT, ["/* a */ \t"]),
    ]
    assert code_of(lines) == {1: "fn f() {}", 2: "fn z() {}", 4: "fn g() {}"}


def test_projection_opening_run_is_matter_up_to_its_first_blank_line(
    rust_definition,
):
    """The place rules divide a section that spans the first blank line: the
    part above it is the file's matter, the part below an ordinary comment."""
    text = "// Copyright 2026 Someone.\n\n// note on f\nfn f() {}\n"
    paragraphs, lines = projection_of(text, rust_definition)
    assert paragraphs == [
        paragraph(
            1,
            1,
            Kind.MATTER,
            ["// Copyright 2026 Someone."],
        ),
        paragraph(3, 3, Kind.COMMENT, ["// note on f"]),
    ]
    assert lines == [CodeLine(4, "fn f() {}", DocPlace(4, True))]


def test_projection_opening_matter_takes_every_form_up_to_the_first_blank(
    rust_definition,
):
    text = "/* a */\n/// b\n// c\n\n// d\nfn f() {}\n"
    paragraphs, lines = projection_of(text, rust_definition)
    assert paragraphs == [
        paragraph(
            1,
            3,
            Kind.MATTER,
            ["/* a */", "/// b", "// c"],
        ),
        paragraph(5, 5, Kind.COMMENT, ["// d"]),
    ]
    assert lines == [CodeLine(6, "fn f() {}", DocPlace(6, True))]


def test_projection_opening_and_closing_matter_of_a_codeless_file(rust_definition):
    text = "// a\n\n// b\n"
    paragraphs, _ = projection_of(text, rust_definition)
    assert paragraphs == [
        paragraph(1, 1, Kind.MATTER, ["// a"]),
        paragraph(3, 3, Kind.MATTER, ["// b"]),
    ]


def test_projection_closing_run_at_end_of_file_is_matter(rust_definition):
    text = "fn f() {}\n// end one\n// end two\n"
    paragraphs, _ = projection_of(text, rust_definition)
    assert paragraphs == [paragraph(2, 3, Kind.MATTER, ["// end one", "// end two"])]


def test_projection_closing_run_of_two_forms_is_one_matter(rust_definition):
    text = "fn f() {}\n/// a\n// b\n"
    paragraphs, _ = projection_of(text, rust_definition)
    assert paragraphs == [paragraph(2, 3, Kind.MATTER, ["/// a", "// b"])]


def test_projection_closing_run_splits_at_its_last_blank_line(rust_definition):
    text = "fn f() {}\n// a\n\n// b\n/// c\n"
    paragraphs, _ = projection_of(text, rust_definition)
    assert paragraphs == [
        paragraph(2, 2, Kind.COMMENT, ["// a"]),
        paragraph(4, 5, Kind.MATTER, ["// b", "/// c"]),
    ]


def test_projection_comments_in_one_gap_with_a_detached_module_doc_are_one(
    rust_definition,
):
    text = "\n// a\n//! m\n// c\nfn f() {}\n"
    paragraphs, lines = projection_of(text, rust_definition)
    assert paragraphs == [
        paragraph(
            2,
            4,
            Kind.COMMENT,
            ["// a", "//! m", "// c"],
        ),
    ]
    assert lines == [CodeLine(5, "fn f() {}", DocPlace(5, True))]


def test_projection_comment_and_detached_doc_after_code_are_one_comment(
    rust_definition,
):
    text = "fn a() {}\n// one\n/// two\n// three\nfn b() {}\n"
    paragraphs, _ = projection_of(text, rust_definition)
    assert paragraphs == [
        paragraph(
            2,
            4,
            Kind.COMMENT,
            ["// one", "/// two", "// three"],
        )
    ]


def test_projection_code_ends_a_comment_section(rust_definition):
    # The first section joins three runs (comment, detached doc, comment).
    text = "fn a() {}\n// one\n/// two\n// three\nfn b() {}\n// four\nfn c() {}\n"
    paragraphs, _ = projection_of(text, rust_definition)
    assert [(p.start, p.end, p.kind) for p in paragraphs] == [
        (2, 4, Kind.COMMENT),
        (6, 6, Kind.COMMENT),
    ]


def test_projection_ordinary_comment_above_an_item_is_a_comment(rust_definition):
    text = "fn z() {}\n// note\nfn f() {}\n"
    paragraphs, _ = projection_of(text, rust_definition)
    assert paragraphs == [paragraph(2, 2, Kind.COMMENT, ["// note"])]


def test_projection_docs_and_comments_never_merge(rust_definition):
    text = "fn z() {}\n// note\n/// Doc.\nfn f() {}\n"
    paragraphs, _ = projection_of(text, rust_definition)
    assert [(p.kind, p.raw_lines, p.anchor_line) for p in paragraphs] == [
        (Kind.COMMENT, ["// note"], None),
        (Kind.DOCSTRING, ["/// Doc."], 4),
    ]


def test_projection_detached_run_joins_its_gap_comment_with_one_warning(
    rust_definition,
):
    text = "fn z() {}\n/// a\n// b\nfn f() {}\n"
    result = rust_read(text, rust_definition)
    paragraphs = result.paragraphs(PAGE)
    # One place holds one paragraph: the detached run joins the comment below.
    assert paragraphs == [
        paragraph(
            2,
            3,
            Kind.COMMENT,
            ["/// a", "// b"],
        ),
    ]
    assert len(result.warnings) == 1
    assert result.detached == (records.DetachedRun(result.warnings[0].span),)


def test_projection_detached_trailing_run_keeps_its_anchor(rust_definition):
    text = "fn z() {} /// t\nfn f() {}\n"
    paragraphs, _ = projection_of(text, rust_definition)
    assert paragraphs == [
        paragraph(
            1,
            1,
            Kind.TRAILING,
            [" /// t"],
            anchor="fn z() {}",
        )
    ]


def test_projection_module_doc_behind_an_attribute_has_one_warning(rust_definition):
    text = "//! a\n#![allow(x)]\n//! b\nfn f() {}\n"
    result = rust_read(text, rust_definition)
    assert len(result.detached) == 1
    assert [w.span for w in result.warnings] == [r.span for r in result.detached]


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"detached": ()}, "align"),
        ({"warnings": ()}, "align"),
    ],
    ids=["run-without-warning", "warning-without-run"],
)
def test_projection_read_refuses_misaligned_records(rust_definition, change, message):
    result = rust_read("//! a\n#![allow(x)]\n//! b\nfn f() {}\n", rust_definition)
    fields = {
        "source": result.source,
        "protected": result.protected,
        "warnings": result.warnings,
        "detached": result.detached,
    }
    with pytest.raises(ValueError, match=message):
        records.RustRead(**{**fields, **change})


def test_projection_shebang_line_is_not_code(rust_definition):
    text = "#!/usr/bin/env run-cargo-script\nfn main() {}\n"
    result = rust_read(text, rust_definition)
    assert result.protected == (SourceSpan(0, 31),)
    paragraphs, lines = projection_of(text, rust_definition)
    shebang = "#!/usr/bin/env run-cargo-script"
    assert paragraphs == [paragraph(1, 1, Kind.MATTER, [shebang])]
    assert lines == [CodeLine(2, "fn main() {}", DocPlace(2, True))]


@pytest.mark.parametrize(
    "text, inner",
    [
        ("fn f() {\n    //! inner\n}\n", 2),
        ("mod m {\n\n    //! doc\n    fn g() {}\n}\n", 3),
    ],
    ids=["fn", "mod"],
)
def test_projection_body_inner_doc_leaves_its_item_inserting_at_its_head(
    rust_definition, text, inner
):
    paragraphs, lines = projection_of(text, rust_definition)
    assert lines[0].documents == DocPlace(1, True)
    assert [(p.start, p.kind) for p in paragraphs] == [(inner, Kind.COMMENT)]


def test_projection_read_rust_refuses_an_unterminated_comment(rust_definition):
    rust = import_module("comment_review.reading.rust")
    result = rust.read_rust("fn f() {}\n/* open\n", rust_definition)
    assert isinstance(result, ReadFailure)
    assert result.diagnostics[0].span == SourceSpan(10, 12)


def test_projection_reader_record_is_satisfied_by_a_python_read():
    from comment_review.reading.language import INSTALLED_REGISTRY
    from comment_review.reading.proof import ReaderRecord
    from comment_review.reading.python import read_python
    from comment_review.reading.python.records import PythonRead

    def warned(record: ReaderRecord) -> int:
        return len(record.warnings)

    definition = INSTALLED_REGISTRY.for_path(Path("x.py"))
    assert definition is not None
    result = read_python('"""Doc."""\n\ndef f():\n    pass\n', definition)
    assert isinstance(result, PythonRead)
    assert warned(result) == 0
    assert result.code_lines() == [
        CodeLine(3, "def f():", DocPlace(3, False)),
        CodeLine(4, "    pass", None),
    ]
    paragraphs = result.paragraphs(Path("x.py"))
    assert not isinstance(paragraphs, ReadFailure)
    assert [(p.kind, p.anchor_line) for p in paragraphs] == [(Kind.DOCSTRING, None)]


def test_projection_rust_read_answers_the_record_methods(rust_definition):
    result = rust_read("fn f() {}\n", rust_definition)
    assert result.warnings == ()
    assert result.paragraphs(PAGE) == []
    assert result.code_lines() == [CodeLine(1, "fn f() {}", DocPlace(1, True))]


def test_projection_a_line_declaring_two_items_documents_the_first(
    rust_definition,
):
    text = "/// Doc.\nfn a() {} fn b() {}\n"
    result = rust_read(text, rust_definition)
    paragraphs, lines = projection_of(text, rust_definition)
    assert lines == [CodeLine(2, "fn a() {} fn b() {}", DocPlace(2, True))]
    assert paragraphs == [paragraph(1, 1, Kind.DOCSTRING, ["/// Doc."], anchor_line=2)]
    assert result.warnings == ()
    assert result.detached == ()


def test_projection_read_source_returns_the_rust_record():
    from comment_review.reading.readers import read_source

    result = read_source(PAGE, "// note\nfn f() {}\n")
    assert isinstance(result, records.RustRead)
    assert result.paragraphs(PAGE) == [paragraph(1, 1, Kind.MATTER, ["// note"])]


def test_a_rust_page_always_has_an_a_series():
    from comment_review.reading.readers import read_source

    result = read_source(PAGE, "")
    assert isinstance(result, records.RustRead)
    assert result.a_series is True
