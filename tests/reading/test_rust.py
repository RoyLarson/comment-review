from importlib import import_module
from importlib.resources import files

import pytest

from comment_review.reading.definitions import LanguageDefinition, decode_definition
from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage
from comment_review.reading.rust import records
from comment_review.reading.source import (
    RegionKind,
    SourceDeclaration,
    SourceRegion,
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


def read(insertions=(1,), protected=(DIRECTIVE,), warnings=(), declarations=()):
    return records.RustRead(
        source(declarations=declarations), protected, insertions, warnings
    )


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
    scan = records.RustScan(TEXT, regions(), tokens())
    assert "".join(TEXT[r.span.start : r.span.end] for r in scan.regions) == TEXT


def test_records_empty_text_has_no_regions():
    records.RustScan("", (), ())
    with pytest.raises(ValueError):
        records.RustScan("", regions(), ())


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
        records.RustScan(TEXT, bad, ())


def test_records_token_requires_nonempty_span():
    with pytest.raises(ValueError):
        records.RustToken(records.RustTokenKind.WORD, SourceSpan(3, 3))


def test_records_scan_rejects_tokens_out_of_order_or_overlapping():
    first, second, third = tokens()
    with pytest.raises(ValueError):
        records.RustScan(TEXT, regions(), (second, first, third))
    overlap = records.RustToken(records.RustTokenKind.WORD, SourceSpan(9, 12))
    with pytest.raises(ValueError):
        records.RustScan(TEXT, regions(), (first, second, overlap, third))
    outside = records.RustToken(records.RustTokenKind.WORD, SourceSpan(30, 40))
    with pytest.raises(ValueError):
        records.RustScan(TEXT, regions(), (first, second, outside))


def test_records_comment_token_must_equal_a_comment_region():
    kind = records.RustTokenKind
    short = records.RustToken(kind.LINE, SourceSpan(0, 5))
    with pytest.raises(ValueError):
        records.RustScan(TEXT, regions(), (short,))
    on_code = records.RustToken(kind.DELIMITED_COMMENT, CODE)
    with pytest.raises(ValueError):
        records.RustScan(TEXT, regions(), (on_code,))


def test_records_literal_token_must_lie_in_a_literal_region():
    token = records.RustToken(records.RustTokenKind.STRING, SourceSpan(8, 10))
    with pytest.raises(ValueError):
        records.RustScan(TEXT, regions(), (token,))


def test_records_scan_accepts_a_literal_token_inside_a_literal_region():
    kind = records.RustTokenKind
    found = (
        SourceRegion(COMMENT, RegionKind.COMMENT),
        SourceRegion(SourceSpan(7, 12), RegionKind.LITERAL),
        SourceRegion(SourceSpan(12, 32), RegionKind.CODE),
    )
    scan = records.RustScan(
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
    records.RustScan(TEXT, regions(), inside)
    nested = (
        records.RustToken(kind.OUTER_ATTRIBUTE, DIRECTIVE),
        records.RustToken(kind.INNER_ATTRIBUTE, SourceSpan(21, 31)),
        records.RustToken(kind.WORD, SourceSpan(22, 27)),
    )
    records.RustScan(TEXT, regions(), nested)


def test_records_scan_rejects_partial_overlap_with_an_attribute():
    kind = records.RustTokenKind
    attribute = records.RustToken(kind.OUTER_ATTRIBUTE, DIRECTIVE)
    runs_past = records.RustToken(kind.WORD, SourceSpan(28, 32))
    with pytest.raises(ValueError):
        records.RustScan(TEXT, regions(), (attribute, runs_past))
    starts_before = records.RustToken(kind.WORD, SourceSpan(17, 21))
    with pytest.raises(ValueError):
        records.RustScan(TEXT, regions(), (starts_before, attribute))
    nested_past = records.RustToken(kind.INNER_ATTRIBUTE, SourceSpan(25, 32))
    with pytest.raises(ValueError):
        records.RustScan(TEXT, regions(), (attribute, nested_past))


def test_records_scan_rejects_a_non_attribute_token_enclosing_another():
    kind = records.RustTokenKind
    outer = records.RustToken(kind.PUNCT, DIRECTIVE)
    inner = records.RustToken(kind.WORD, SourceSpan(22, 27))
    with pytest.raises(ValueError):
        records.RustScan(TEXT, regions(), (outer, inner))


def test_records_placement_accepts_one_insertion_per_declaration():
    one = declaration()
    records.RustPlacement((one,), (1, 2), (records.DetachedRun(COMMENT, 0),))
    records.RustPlacement((), (1,), ())
    records.RustPlacement((one, declaration(10)), (1, 2, 3), ())


@pytest.mark.parametrize("insertions", [(1,), (1, 2, 3), (0, 2), (1, 0), (-1, 2)])
def test_records_placement_rejects_bad_insertions(insertions):
    with pytest.raises(ValueError):
        records.RustPlacement((declaration(),), insertions, ())


@pytest.mark.parametrize("insertions", [(1, 3, 3), (1, 4, 3)], ids=["equal", "falling"])
def test_records_placement_rejects_non_increasing_declaration_insertions(insertions):
    with pytest.raises(ValueError):
        records.RustPlacement((declaration(), declaration(10)), insertions, ())


def test_records_placement_rejects_detached_owner_out_of_range():
    with pytest.raises(ValueError):
        records.RustPlacement(
            (declaration(),), (1, 2), (records.DetachedRun(COMMENT, 1),)
        )
    with pytest.raises(ValueError):
        records.RustPlacement(
            (declaration(),), (1, 2), (records.DetachedRun(COMMENT, -1),)
        )


def test_records_read_accepts_a_consistent_read():
    result = read(warnings=(warning(),))
    assert result.insertions == (1,)
    read(insertions=(1, 2), declarations=(declaration(),))


def test_records_read_rejects_bad_insertions():
    with pytest.raises(ValueError):
        read(insertions=(1, 2))
    with pytest.raises(ValueError):
        read(insertions=(1, 2, 2), declarations=(declaration(), declaration(10)))


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
    code = {kind.WORD, kind.PUNCT, kind.OPEN, kind.CLOSE}
    for token in result.tokens:
        (region,) = [
            r
            for r in result.regions
            if r.span.start <= token.span.start and token.span.end <= r.span.end
        ]
        if token.kind in records.COMMENT_KINDS:
            assert region.kind is RegionKind.COMMENT and region.span == token.span
        elif token.kind in code:
            assert region.kind is RegionKind.CODE
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
