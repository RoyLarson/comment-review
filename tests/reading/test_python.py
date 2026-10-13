from dataclasses import FrozenInstanceError, replace
from importlib import import_module
from importlib.resources import files

import pytest

from comment_review.reading.definitions import LanguageDefinition, decode_definition
from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage
from comment_review.reading.source import (
    DocumentationOwner,
    RegionKind,
    SourceDeclaration,
    SourceRegion,
    SourceSection,
    SourceSpan,
    SourceStructure,
)


@pytest.fixture
def records():
    try:
        return import_module("comment_review.reading.python.records")
    except ModuleNotFoundError:
        pytest.skip("Python source record module is not implemented")


def test_records_module_exists():
    try:
        import_module("comment_review.reading.python.records")
    except ModuleNotFoundError:
        pytest.fail("Python source record module is not implemented", pytrace=False)


def documented_read(records):
    text = 'def f():\n    "a\\n" "b"\n'
    header = SourceSpan(0, 8)
    statement = SourceSpan(13, 22)
    components = (SourceSpan(13, 18), SourceSpan(19, 22))
    declaration = SourceDeclaration(header, 0, "function")
    regions = (SourceRegion(SourceSpan(0, len(text)), RegionKind.CODE),)
    source = SourceStructure(
        text,
        regions,
        (SourceSection(statement, "docstring"),),
        (declaration,),
        (DocumentationOwner(0, 0),),
    )
    expression = records.DocumentationExpression(statement, components, 0)
    payload = records.DocumentationPayload(
        expression,
        "a\nb",
        (
            records.PayloadPiece(SourceSpan(0, 1), (SourceSpan(14, 15),)),
            records.PayloadPiece(SourceSpan(1, 2), (SourceSpan(15, 17),)),
            records.PayloadPiece(SourceSpan(2, 3), (SourceSpan(20, 21),)),
        ),
    )
    tokens = (
        records.PythonToken("name", SourceSpan(0, 3)),
        records.PythonToken("name", SourceSpan(4, 5)),
        records.PythonToken("punctuation", SourceSpan(5, 8)),
        *(records.PythonToken("literal", span) for span in components),
    )
    suites = (
        records.PythonSuite(SourceSpan(0, len(text)), None, None, (0,), "module"),
        records.PythonSuite(SourceSpan(13, len(text)), 0, header, (1,), "function"),
    )
    statements = (
        records.PythonStatement(header, (0, 1, 2), 0),
        records.PythonStatement(statement, (3, 4), 1),
    )
    facts = (records.DeclarationFacts(0, "f", None, 1, 13),)
    return records.PythonRead(source, tokens, suites, statements, facts, (payload,), ())


def test_records_empty_read_preserves_exact_source(records):
    source = SourceStructure("", (), (), (), ())
    suite = records.PythonSuite(SourceSpan(0, 0), None, None, (), "module")
    result = records.PythonRead(source, (), (suite,), (), (), (), ())
    assert result.source is source
    assert result.source.reconstruct() == ""
    assert records.PythonScan("", (), (), ()).text == ""


def test_records_documented_read_reconstructs_and_is_frozen(records):
    result = documented_read(records)
    assert result.source.reconstruct() == 'def f():\n    "a\\n" "b"\n'
    assert result.payloads[0].text == "a\nb"
    assert result.payloads[0].mapping[1].raw == (SourceSpan(15, 17),)
    with pytest.raises(FrozenInstanceError):
        result.payloads[0].text = "changed"


def test_records_nested_protection_and_fragment_offsets(records):
    protection = (
        records.ProtectedSource(SourceSpan(10, 20), "interpolation", None),
        records.ProtectedSource(SourceSpan(12, 15), "literal", SourceSpan(5, 8)),
    )
    region = SourceRegion(SourceSpan(10, 20), RegionKind.LITERAL)
    token = records.PythonToken("literal", SourceSpan(12, 15))
    fragment = records.InterpolationScan(20, (region,), (token,), protection)
    assert fragment.end == 20
    scan = records.PythonScan(
        "x" * 20,
        (SourceRegion(SourceSpan(0, 20), RegionKind.LITERAL),),
        (token,),
        protection,
    )
    assert scan.protected == protection


def test_records_payload_keeps_zero_output_and_multiple_raw_spans(records):
    expression = records.DocumentationExpression(
        SourceSpan(0, 13), (SourceSpan(0, 7), SourceSpan(8, 13)), None
    )
    pieces = (
        records.PayloadPiece(SourceSpan(0, 1), (SourceSpan(1, 2),)),
        records.PayloadPiece(SourceSpan(1, 1), (SourceSpan(2, 4),)),
        records.PayloadPiece(SourceSpan(1, 3), (SourceSpan(4, 6), SourceSpan(9, 10))),
    )
    assert records.DocumentationPayload(expression, "abc", pieces).mapping == pieces
    empty = records.DocumentationExpression(SourceSpan(0, 2), (SourceSpan(0, 2),), None)
    assert records.DocumentationPayload(empty, "", ()).text == ""


@pytest.mark.parametrize(
    "factory",
    [
        lambda r: r.PythonToken("", SourceSpan(0, 1)),
        lambda r: r.PythonToken("name", (0, 1)),
        lambda r: r.ProtectedSource(SourceSpan(0, 1), "literal", False),
        lambda r: r.PythonScan("x", (), (), ()),
        lambda r: r.PythonScan(
            "x", (SourceRegion(SourceSpan(0, 2), RegionKind.CODE),), (), ()
        ),
        lambda r: r.PythonScan(
            "x", [SourceRegion(SourceSpan(0, 1), RegionKind.CODE)], (), ()
        ),
        lambda r: r.InterpolationScan(True, (), (), ()),
        lambda r: r.InterpolationScan(
            1, (), (r.PythonToken("name", SourceSpan(0, 2)),), ()
        ),
        lambda r: r.LogicalLine(SourceSpan(0, 1), (1, 0), 0),
        lambda r: r.LogicalLine(SourceSpan(0, 1), (True,), 0),
        lambda r: r.LogicalLine(SourceSpan(0, 1), (), -1),
        lambda r: r.PythonStatement(SourceSpan(0, 1), (), True),
        lambda r: r.PythonSuite(SourceSpan(0, 1), 0, None, (), "module"),
        lambda r: r.DeclarationFacts(0, "", None, 0, 0),
        lambda r: r.DeclarationFacts(-1, "f", None, 0, 0),
        lambda r: r.DocumentationExpression(
            SourceSpan(2, 4), (SourceSpan(0, 3),), None
        ),
        lambda r: r.DocumentationExpression(
            SourceSpan(0, 4), (SourceSpan(0, 3), SourceSpan(2, 4)), None
        ),
        lambda r: r.PayloadPiece(SourceSpan(0, 1), [SourceSpan(0, 1)]),
        lambda r: r.PreservationResult(
            True, (ReadDiagnostic(ReadStage.PLACE, "changed", "changed"),)
        ),
        lambda r: r.PreservationResult(False, ()),
        lambda r: r.PreservationResult(1, ()),
    ],
)
def test_records_reject_invalid_local_values(records, factory):
    with pytest.raises(ValueError):
        factory(records)


def test_records_reject_overlapping_tokens_and_partition_gaps(records):
    with pytest.raises(ValueError):
        records.PythonScan(
            "abc",
            (
                SourceRegion(SourceSpan(0, 1), RegionKind.CODE),
                SourceRegion(SourceSpan(2, 3), RegionKind.CODE),
            ),
            (),
            (),
        )
    with pytest.raises(ValueError):
        records.InterpolationScan(
            10,
            (),
            (
                records.PythonToken("a", SourceSpan(2, 5)),
                records.PythonToken("b", SourceSpan(4, 6)),
            ),
            (),
        )


def test_records_reject_bad_structure_relationships(records):
    result = documented_read(records)
    for changed in (
        {"statements": (result.statements[0], replace(result.statements[1], suite=9))},
        {"suites": (result.suites[0], replace(result.suites[1], parent=1))},
        {"suites": (result.suites[0], replace(result.suites[1], statements=()))},
        {"declarations": (replace(result.declarations[0], declaration=1),)},
        {"declarations": (replace(result.declarations[0], parent=0),)},
        {"declarations": (replace(result.declarations[0], insertion=99),)},
        {"declarations": result.declarations * 2},
        {"tokens": (records.PythonToken("name", SourceSpan(0, 99)),)},
    ):
        with pytest.raises(ValueError):
            replace(result, **changed)


def test_records_allow_declaration_body_below_control_suite_and_empty_suite(records):
    declaration = SourceDeclaration(SourceSpan(5, 13), 5, "function")
    suites = (
        records.PythonSuite(SourceSpan(0, 15), None, None, (0,), "module"),
        records.PythonSuite(SourceSpan(5, 15), 0, SourceSpan(0, 4), (1,), "control"),
        records.PythonSuite(SourceSpan(15, 15), 1, declaration.header, (), "function"),
    )
    statements = (
        records.PythonStatement(SourceSpan(0, 4), (), 0),
        records.PythonStatement(declaration.header, (), 1),
    )
    facts = (records.DeclarationFacts(0, "f", None, 2, 15),)
    assert (
        records.PythonStructure((declaration,), facts, suites, statements).facts
        == facts
    )


def test_records_reject_payload_gaps_bounds_and_wrong_owner(records):
    result = documented_read(records)
    payload = result.payloads[0]
    for changes in (
        {"mapping": payload.mapping[1:]},
        {"mapping": (records.PayloadPiece(SourceSpan(0, 4), (SourceSpan(14, 15),)),)},
        {"mapping": (records.PayloadPiece(SourceSpan(0, 3), (SourceSpan(0, 3),)),)},
    ):
        with pytest.raises(ValueError):
            replace(payload, **changes)
    with pytest.raises(ValueError):
        replace(
            result,
            payloads=(
                replace(
                    payload, expression=replace(payload.expression, declaration=None)
                ),
            ),
        )


def test_records_preservation_results_require_matching_diagnostics(records):
    diagnostic = ReadDiagnostic(ReadStage.PLACE, "changed", "source changed")
    assert records.PreservationResult(True, ()).unchanged
    assert records.PreservationResult(False, (diagnostic,)).diagnostics == (diagnostic,)


def test_records_declaration_parent_matches_enclosing_declaration(records):
    declarations = (
        SourceDeclaration(SourceSpan(0, 8), 0, "function"),
        SourceDeclaration(SourceSpan(13, 21), 13, "function"),
    )
    suites = (
        records.PythonSuite(SourceSpan(0, 25), None, None, (), "module"),
        records.PythonSuite(
            SourceSpan(13, 25), 0, declarations[0].header, (), "function"
        ),
        records.PythonSuite(
            SourceSpan(25, 25), 1, declarations[1].header, (), "function"
        ),
    )
    facts = (
        records.DeclarationFacts(0, "outer", None, 1, 13),
        records.DeclarationFacts(1, "inner", 0, 2, 25),
    )
    result = records.PythonStructure(declarations, facts, suites, ())
    assert result.facts[1].parent == 0
    with pytest.raises(ValueError):
        replace(result, facts=(facts[0], replace(facts[1], parent=None)))


@pytest.fixture
def python_definition():
    text = (
        files("comment_review")
        .joinpath("references/languages/python.toml")
        .read_text(encoding="utf-8")
    )
    definition = decode_definition(text)
    assert isinstance(definition, LanguageDefinition)
    return definition


def scan_tokens(text, definition):
    try:
        scanner = import_module("comment_review.reading.python.scanner")
    except ModuleNotFoundError:
        pytest.fail("Python token scanner is not implemented", pytrace=False)
    return scanner.scan_python(text, definition)


@pytest.mark.parametrize(
    ("text", "regions", "tokens"),
    [
        ("", [], []),
        (
            "match _x2 \u03c0 e\u0301 \U00011f02x",
            [
                ("code", 0, 5),
                ("whitespace", 5, 6),
                ("code", 6, 9),
                ("whitespace", 9, 10),
                ("code", 10, 11),
                ("whitespace", 11, 12),
                ("code", 12, 14),
                ("whitespace", 14, 15),
                ("code", 15, 17),
            ],
            [
                ("identifier", 0, 5, "match"),
                ("identifier", 6, 9, "_x2"),
                ("identifier", 10, 11, "\u03c0"),
                ("identifier", 12, 14, "e\u0301"),
                ("identifier", 15, 17, "\U00011f02x"),
            ],
        ),
        (
            " \t\fx=1# end\r\n#tail",
            [
                ("whitespace", 0, 3),
                ("code", 3, 6),
                ("comment", 6, 11),
                ("whitespace", 11, 13),
                ("comment", 13, 18),
            ],
            [
                ("identifier", 3, 4, "x"),
                ("operator", 4, 5, "="),
                ("number", 5, 6, "1"),
                ("comment", 6, 11, "# end"),
                ("newline", 11, 13, "\r\n"),
                ("comment", 13, 18, "#tail"),
            ],
        ),
        (
            "a\r\nb\rc\n\\\r\nd",
            [
                ("code", 0, 1),
                ("whitespace", 1, 3),
                ("code", 3, 4),
                ("whitespace", 4, 5),
                ("code", 5, 6),
                ("whitespace", 6, 7),
                ("code", 7, 8),
                ("whitespace", 8, 10),
                ("code", 10, 11),
            ],
            [
                ("identifier", 0, 1, "a"),
                ("newline", 1, 3, "\r\n"),
                ("identifier", 3, 4, "b"),
                ("newline", 4, 5, "\r"),
                ("identifier", 5, 6, "c"),
                ("newline", 6, 7, "\n"),
                ("continuation", 7, 8, "\\"),
                ("newline", 8, 10, "\r\n"),
                ("identifier", 10, 11, "d"),
            ],
        ),
        (
            "1+0xff;0b_10,0o7:1_000",
            [("code", 0, 22)],
            [
                ("number", 0, 1, "1"),
                ("operator", 1, 2, "+"),
                ("number", 2, 6, "0xff"),
                ("operator", 6, 7, ";"),
                ("number", 7, 12, "0b_10"),
                ("operator", 12, 13, ","),
                ("number", 13, 16, "0o7"),
                ("operator", 16, 17, ":"),
                ("number", 17, 22, "1_000"),
            ],
        ),
        (
            ".5+1.e-2+3_0.2_5e+1_0J",
            [("code", 0, 22)],
            [
                ("number", 0, 2, ".5"),
                ("operator", 2, 3, "+"),
                ("number", 3, 8, "1.e-2"),
                ("operator", 8, 9, "+"),
                ("number", 9, 22, "3_0.2_5e+1_0J"),
            ],
        ),
        (
            "00j+0_0+12j+1..2",
            [("code", 0, 16)],
            [
                ("number", 0, 3, "00j"),
                ("operator", 3, 4, "+"),
                ("number", 4, 7, "0_0"),
                ("operator", 7, 8, "+"),
                ("number", 8, 11, "12j"),
                ("operator", 11, 12, "+"),
                ("number", 12, 14, "1."),
                ("number", 14, 16, ".2"),
            ],
        ),
        (
            "**=//=<<=>>=:=...!=->()[]{};:@,~",
            [("code", 0, 32)],
            [
                ("operator", 0, 3, "**="),
                ("operator", 3, 6, "//="),
                ("operator", 6, 9, "<<="),
                ("operator", 9, 12, ">>="),
                ("operator", 12, 14, ":="),
                ("operator", 14, 17, "..."),
                ("operator", 17, 19, "!="),
                ("operator", 19, 21, "->"),
                ("operator", 21, 22, "("),
                ("operator", 22, 23, ")"),
                ("operator", 23, 24, "["),
                ("operator", 24, 25, "]"),
                ("operator", 25, 26, "{"),
                ("operator", 26, 27, "}"),
                ("operator", 27, 28, ";"),
                ("operator", 28, 29, ":"),
                ("operator", 29, 30, "@"),
                ("operator", 30, 31, ","),
                ("operator", 31, 32, "~"),
            ],
        ),
    ],
)
def test_tokens_exact_partition_and_spelling(python_definition, text, regions, tokens):
    result = scan_tokens(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert result.text == text
    assert [(r.kind.value, r.span.start, r.span.end) for r in result.regions] == regions
    assert [
        (t.kind, t.span.start, t.span.end, text[t.span.start : t.span.end])
        for t in result.tokens
    ] == tokens
    assert "".join(text[r.span.start : r.span.end] for r in result.regions) == text
    assert result.protected == ()


@pytest.mark.parametrize(
    ("text", "start", "end"),
    [
        ("0x", 0, 2),
        ("0b2", 0, 3),
        ("0123", 0, 4),
        ("1e+", 0, 3),
        ("1__2", 0, 4),
        ("3_", 0, 2),
        ("1e_2", 0, 4),
        ("0x1j", 0, 4),
        ("x \\", 2, 3),
        ("\\ \n", 0, 1),
        ("$", 0, 1),
        ("!", 0, 1),
    ],
)
def test_tokens_fail_locally_on_unsupported_or_incomplete_state(
    python_definition, text, start, end
):
    result = scan_tokens(text, python_definition)
    assert isinstance(result, ReadFailure)
    assert result.diagnostics[0].stage == ReadStage.LEX
    assert result.diagnostics[0].span == SourceSpan(start, end)


def test_tokens_reject_invalid_definition_before_recognition(python_definition):
    definition = replace(python_definition, rules={})
    result = scan_tokens("x", definition)
    assert isinstance(result, ReadFailure)
    assert result.diagnostics[0].stage == ReadStage.SELECT


@pytest.mark.parametrize(
    "spelling",
    [
        "0",
        "000",
        "0_0_0",
        "123_456",
        "0X_FF",
        "0B_1_0",
        "0O_7_0",
        "1.",
        ".1",
        "001.0",
        "0_1e0",
        "1e+2",
        "1E-2",
        "1.e3",
        ".1e2",
        "2j",
        "0_1J",
        ".5j",
        "1.e2j",
        "1_2.3_4e5_6J",
    ],
)
def test_tokens_numeric_forms_keep_one_complete_spelling(python_definition, spelling):
    result = scan_tokens(spelling, python_definition)
    assert not isinstance(result, ReadFailure)
    assert [(r.kind, r.span) for r in result.regions] == [
        (RegionKind.CODE, SourceSpan(0, len(spelling)))
    ]
    assert [(t.kind, t.span) for t in result.tokens] == [
        ("number", SourceSpan(0, len(spelling)))
    ]
    assert (
        result.text[result.tokens[0].span.start : result.tokens[0].span.end] == spelling
    )
    assert (
        "".join(result.text[r.span.start : r.span.end] for r in result.regions)
        == spelling
    )


@pytest.mark.parametrize(
    "spelling",
    [
        "+",
        "-",
        "*",
        "**",
        "/",
        "//",
        "%",
        "@",
        "<<",
        ">>",
        "&",
        "|",
        "^",
        "~",
        "<",
        ">",
        "<=",
        ">=",
        "==",
        "!=",
        "=",
        "+=",
        "-=",
        "*=",
        "/=",
        "//=",
        "%=",
        "@=",
        "&=",
        "|=",
        "^=",
        ">>=",
        "<<=",
        "**=",
        "->",
        ":=",
        ".",
        "...",
        ",",
        ";",
        ":",
        "(",
        ")",
        "[",
        "]",
        "{",
        "}",
    ],
)
def test_tokens_operator_forms_use_longest_match(python_definition, spelling):
    result = scan_tokens(spelling, python_definition)
    assert not isinstance(result, ReadFailure)
    assert [(r.kind, r.span) for r in result.regions] == [
        (RegionKind.CODE, SourceSpan(0, len(spelling)))
    ]
    assert [(t.kind, t.span) for t in result.tokens] == [
        ("operator", SourceSpan(0, len(spelling)))
    ]
    assert (
        result.text[result.tokens[0].span.start : result.tokens[0].span.end] == spelling
    )
    assert (
        "".join(result.text[r.span.start : r.span.end] for r in result.regions)
        == spelling
    )


@pytest.mark.parametrize("prefix", ["f", "fr", "rf", "t", "tr", "rt"])
def test_tokens_literal_prefixes_are_never_classified_as_code(
    python_definition, prefix
):
    text = prefix.upper() + "'text'"
    result = scan_tokens(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert [(r.kind, r.span) for r in result.regions] == [
        (RegionKind.LITERAL, SourceSpan(0, len(text)))
    ]
    assert [t.kind for t in result.tokens] == [
        "interpolation_start",
        "interpolation_literal",
        "interpolation_end",
    ]


@pytest.mark.parametrize(
    "prefix",
    ["", "u", "U", "r", "R", "b", "B", "br", "Br", "bR", "BR", "rb", "Rb", "rB", "RB"],
)
@pytest.mark.parametrize("quote", ["'", '"', "'''", '"""'])
@pytest.mark.parametrize("payload", ["", "value", "value # {braces}  "])
def test_literals_ordinary_forms_preserve_spans_and_resume(
    python_definition, prefix, quote, payload
):
    literal = prefix + quote + payload + quote
    text = "x=" + literal + "+y# real\r\n"
    end = 2 + len(literal)
    result = scan_tokens(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert result.text == text
    assert [(r.kind, r.span) for r in result.regions] == [
        (RegionKind.CODE, SourceSpan(0, 2)),
        (RegionKind.LITERAL, SourceSpan(2, end)),
        (RegionKind.CODE, SourceSpan(end, end + 2)),
        (RegionKind.COMMENT, SourceSpan(end + 2, end + 8)),
        (RegionKind.WHITESPACE, SourceSpan(end + 8, end + 10)),
    ]
    assert [(t.kind, t.span) for t in result.tokens] == [
        ("identifier", SourceSpan(0, 1)),
        ("operator", SourceSpan(1, 2)),
        ("string", SourceSpan(2, end)),
        ("operator", SourceSpan(end, end + 1)),
        ("identifier", SourceSpan(end + 1, end + 2)),
        ("comment", SourceSpan(end + 2, end + 8)),
        ("newline", SourceSpan(end + 8, end + 10)),
    ]
    assert text[result.tokens[2].span.start : result.tokens[2].span.end] == literal
    assert text[result.tokens[5].span.start : result.tokens[5].span.end] == "# real"
    assert "".join(text[r.span.start : r.span.end] for r in result.regions) == text
    assert result.protected == ()


@pytest.mark.parametrize("prefix", ["", "u", "r", "b", "br", "rb"])
@pytest.mark.parametrize("quote", ["'", '"', "'''", '"""'])
@pytest.mark.parametrize("slashes", range(6))
def test_literals_escaped_delimiter_parity(python_definition, prefix, quote, slashes):
    payload = "a" + "\\" * slashes
    literal = prefix + quote + payload + quote
    if slashes % 2:
        literal += "more" + quote
    result = scan_tokens(literal, python_definition)
    assert not isinstance(result, ReadFailure)
    assert [(t.kind, t.span) for t in result.tokens] == [
        ("string", SourceSpan(0, len(literal)))
    ]
    assert [(r.kind, r.span) for r in result.regions] == [
        (RegionKind.LITERAL, SourceSpan(0, len(literal)))
    ]
    assert result.text == literal
    assert (
        "".join(literal[r.span.start : r.span.end] for r in result.regions) == literal
    )


@pytest.mark.parametrize("prefix", ["", "u", "r", "b", "br", "rb"])
@pytest.mark.parametrize("quote", ["'", '"', "'''", '"""'])
@pytest.mark.parametrize("newline", ["\r", "\n", "\r\n"])
def test_literals_physical_escaped_newlines(python_definition, prefix, quote, newline):
    literal = prefix + quote + "before\\" + newline + "# after  " + quote
    result = scan_tokens(literal, python_definition)
    assert not isinstance(result, ReadFailure)
    assert [(t.kind, t.span) for t in result.tokens] == [
        ("string", SourceSpan(0, len(literal)))
    ]
    assert [(r.kind, r.span) for r in result.regions] == [
        (RegionKind.LITERAL, SourceSpan(0, len(literal)))
    ]
    assert result.text == literal
    assert (
        "".join(literal[r.span.start : r.span.end] for r in result.regions) == literal
    )


@pytest.mark.parametrize("prefix", ["", "u", "r", "b", "br", "rb"])
@pytest.mark.parametrize("quote", ["'''", '"""'])
@pytest.mark.parametrize("newline", ["\r", "\n", "\r\n"])
def test_literals_triple_payload_keeps_double_delimiters_and_blank_lines(
    python_definition, prefix, quote, newline
):
    literal = (
        prefix
        + quote
        + "# first  "
        + newline * 2
        + quote[:2]
        + "{x}  "
        + newline
        + quote
    )
    result = scan_tokens(literal, python_definition)
    assert not isinstance(result, ReadFailure)
    assert [(t.kind, t.span) for t in result.tokens] == [
        ("string", SourceSpan(0, len(literal)))
    ]
    assert [(r.kind, r.span) for r in result.regions] == [
        (RegionKind.LITERAL, SourceSpan(0, len(literal)))
    ]
    assert result.text == literal
    assert (
        "".join(literal[r.span.start : r.span.end] for r in result.regions) == literal
    )


def test_literals_adjacent_boundaries_and_nonprefix_identifier(python_definition):
    text = 'name"value"R""b' + "'''next'''# tail"
    result = scan_tokens(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert [(t.kind, t.span) for t in result.tokens] == [
        ("identifier", SourceSpan(0, 4)),
        ("string", SourceSpan(4, 11)),
        ("string", SourceSpan(11, 14)),
        ("string", SourceSpan(14, 25)),
        ("comment", SourceSpan(25, 31)),
    ]
    assert [(r.kind, r.span) for r in result.regions] == [
        (RegionKind.CODE, SourceSpan(0, 4)),
        (RegionKind.LITERAL, SourceSpan(4, 11)),
        (RegionKind.LITERAL, SourceSpan(11, 14)),
        (RegionKind.LITERAL, SourceSpan(14, 25)),
        (RegionKind.COMMENT, SourceSpan(25, 31)),
    ]
    assert [text[t.span.start : t.span.end] for t in result.tokens] == [
        "name",
        '"value"',
        'R""',
        "b'''next'''",
        "# tail",
    ]
    assert "".join(text[r.span.start : r.span.end] for r in result.regions) == text


@pytest.mark.parametrize(
    "literal",
    [
        "'",
        '"unterminated',
        "u'",
        "r'tail\\'",
        'b"tail\\',
        "br'''tail",
        "rb'''tail''",
        '"""tail\\"""',
        "'tail\\\n",
        "r'tail\\\r\n",
    ],
)
def test_literals_truncated_or_escaped_closer_is_unterminated(
    python_definition, literal
):
    text = "x=" + literal
    result = scan_tokens(text, python_definition)
    assert isinstance(result, ReadFailure)
    diagnostic = result.diagnostics[0]
    assert diagnostic.stage == ReadStage.LEX
    assert diagnostic.code == "unterminated-literal"
    assert diagnostic.span == SourceSpan(2, len(text))


@pytest.mark.parametrize("prefix", ["", "u", "r", "b", "br", "rb"])
@pytest.mark.parametrize("quote", ["'", '"'])
@pytest.mark.parametrize("newline", ["\r", "\n", "\r\n"])
@pytest.mark.parametrize("slashes", [0, 2, 4])
def test_literals_unescaped_short_newline_fails_before_following_source(
    python_definition, prefix, quote, newline, slashes
):
    text = "x=" + prefix + quote + "tail" + "\\" * slashes + newline + "# real\nnext=1"
    result = scan_tokens(text, python_definition)
    assert isinstance(result, ReadFailure)
    diagnostic = result.diagnostics[0]
    assert diagnostic.stage == ReadStage.LEX
    assert diagnostic.code == "unterminated-literal"
    assert diagnostic.span == SourceSpan(2, 2 + len(prefix) + len(quote) + 4 + slashes)


@pytest.mark.parametrize(
    "prefix", ["t", "T", "tr", "tR", "Tr", "TR", "rt", "rT", "Rt", "RT"]
)
@pytest.mark.parametrize("quote", ["'", '"', "'''", '"""'])
def test_template_observable_source_prefixes_are_executable_literals(
    python_definition, prefix, quote
):
    text = "x=" + prefix + quote + "{x} # data" + quote
    result = scan_tokens(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert [(t.kind, text[t.span.start : t.span.end]) for t in result.tokens] == [
        ("identifier", "x"),
        ("operator", "="),
        ("interpolation_start", prefix + quote),
        ("field_start", "{"),
        ("identifier", "x"),
        ("field_end", "}"),
        ("interpolation_literal", " # data"),
        ("interpolation_end", quote),
    ]
    assert [
        (p.kind, p.span, text[p.span.start : p.span.end], p.attachment)
        for p in result.protected
    ] == [
        (
            "template-expression",
            SourceSpan(3 + len(prefix) + len(quote), 4 + len(prefix) + len(quote)),
            "x",
            None,
        )
    ]


def test_tokens_horizontal_whitespace_never_creates_a_token(python_definition):
    text = " \t\n\f"
    result = scan_tokens(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert [(r.kind, r.span) for r in result.regions] == [
        (RegionKind.WHITESPACE, SourceSpan(0, 4))
    ]
    assert [(t.kind, t.span) for t in result.tokens] == [("newline", SourceSpan(2, 3))]
    assert result.text[2:3] == "\n"
    assert (
        "".join(result.text[r.span.start : r.span.end] for r in result.regions) == text
    )


@pytest.mark.parametrize(
    ("text", "regions", "tokens"),
    [
        (
            "1in [1]",
            [("code", 0, 3), ("whitespace", 3, 4), ("code", 4, 7)],
            [
                ("number", 0, 1, "1"),
                ("identifier", 1, 3, "in"),
                ("operator", 4, 5, "["),
                ("number", 5, 6, "1"),
                ("operator", 6, 7, "]"),
            ],
        ),
        (
            "1if True else 0",
            [
                ("code", 0, 3),
                ("whitespace", 3, 4),
                ("code", 4, 8),
                ("whitespace", 8, 9),
                ("code", 9, 13),
                ("whitespace", 13, 14),
                ("code", 14, 15),
            ],
            [
                ("number", 0, 1, "1"),
                ("identifier", 1, 3, "if"),
                ("identifier", 4, 8, "True"),
                ("identifier", 9, 13, "else"),
                ("number", 14, 15, "0"),
            ],
        ),
        (
            "0x1or 2",
            [("code", 0, 5), ("whitespace", 5, 6), ("code", 6, 7)],
            [
                ("number", 0, 3, "0x1"),
                ("identifier", 3, 5, "or"),
                ("number", 6, 7, "2"),
            ],
        ),
        (
            "1and 2",
            [("code", 0, 4), ("whitespace", 4, 5), ("code", 5, 6)],
            [("number", 0, 1, "1"), ("identifier", 1, 4, "and"), ("number", 5, 6, "2")],
        ),
        (
            "1jand 2",
            [("code", 0, 5), ("whitespace", 5, 6), ("code", 6, 7)],
            [
                ("number", 0, 2, "1j"),
                ("identifier", 2, 5, "and"),
                ("number", 6, 7, "2"),
            ],
        ),
        (
            "1else",
            [("code", 0, 5)],
            [("number", 0, 1, "1"), ("identifier", 1, 5, "else")],
        ),
        (
            "1for",
            [("code", 0, 4)],
            [("number", 0, 1, "1"), ("identifier", 1, 4, "for")],
        ),
        (
            "1is",
            [("code", 0, 3)],
            [("number", 0, 1, "1"), ("identifier", 1, 3, "is")],
        ),
        (
            "0x1for 2",
            [("code", 0, 6), ("whitespace", 6, 7), ("code", 7, 8)],
            [
                ("number", 0, 4, "0x1f"),
                ("identifier", 4, 6, "or"),
                ("number", 7, 8, "2"),
            ],
        ),
        (
            "1e2or",
            [("code", 0, 5)],
            [("number", 0, 3, "1e2"), ("identifier", 3, 5, "or")],
        ),
    ],
)
def test_tokens_numeric_keyword_boundaries(python_definition, text, regions, tokens):
    result = scan_tokens(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert [(r.kind.value, r.span.start, r.span.end) for r in result.regions] == regions
    assert [
        (t.kind, t.span.start, t.span.end, text[t.span.start : t.span.end])
        for t in result.tokens
    ] == tokens
    assert "".join(text[r.span.start : r.span.end] for r in result.regions) == text


@pytest.mark.parametrize(
    ("text", "end"),
    [
        ("1index", 6),
        ("1or2", 4),
        ("1and_value", 10),
        ("1in\u03c0", 4),
        ("1elif", 5),
        ("1In", 3),
        ("0x1and", 6),
        ("0x1else", 7),
        ("1e+", 3),
        ("1__2", 4),
        ("0x", 2),
    ],
)
def test_tokens_numeric_keyword_boundaries_reject_false_suffixes(
    python_definition, text, end
):
    result = scan_tokens(text, python_definition)
    assert isinstance(result, ReadFailure)
    assert result.diagnostics[0].stage == ReadStage.LEX
    assert result.diagnostics[0].span == SourceSpan(0, end)


def read_logical_lines(text, definition):
    scan = scan_tokens(text, definition)
    assert not isinstance(scan, ReadFailure)
    try:
        structure = import_module("comment_review.reading.python.structure")
    except ModuleNotFoundError:
        pytest.fail("Python logical lines are not implemented", pytrace=False)
    return scan, structure.logical_lines(scan, definition)


@pytest.mark.parametrize(
    ("text", "expected", "spellings"),
    [
        ("", [], []),
        ("  # c\r\n\t\n# last", [], []),
        ("x=1\n", [(0, 4, (0, 1, 2), 0)], [["x", "=", "1"]]),
        ("  x=1", [(0, 5, (0, 1, 2), 2)], [["x", "=", "1"]]),
        (
            "x=(\n 1, # c\n [2]\n)\ny=3",
            [(0, 19, (0, 1, 2, 4, 5, 8, 9, 10, 12), 0), (19, 22, (14, 15, 16), 0)],
            [["x", "=", "(", "1", ",", "[", "2", "]", ")"], ["y", "=", "3"]],
        ),
        (
            "  x=1+\\\r\n  2\r\nz=3",
            [(0, 14, (0, 1, 2, 3, 6), 2), (14, 17, (8, 9, 10), 0)],
            [["x", "=", "1", "+", "2"], ["z", "=", "3"]],
        ),
        (
            "if x:\n\ty=1\n\tz=2\nw=3\n",
            [
                (0, 6, (0, 1, 2), 0),
                (6, 11, (4, 5, 6), 8),
                (11, 16, (8, 9, 10), 8),
                (16, 20, (12, 13, 14), 0),
            ],
            [["if", "x", ":"], ["y", "=", "1"], ["z", "=", "2"], ["w", "=", "3"]],
        ),
        ("\t \fy=1\n", [(0, 7, (0, 1, 2), 0)], [["y", "=", "1"]]),
        (
            "x=1;y=2 # c\n",
            [(0, 12, (0, 1, 2, 3, 4, 5, 6), 0)],
            [["x", "=", "1", ";", "y", "=", "2"]],
        ),
        (
            "x=1\\\n\ny=2",
            [(0, 6, (0, 1, 2), 0), (6, 9, (6, 7, 8), 0)],
            [["x", "=", "1"], ["y", "=", "2"]],
        ),
        ("    \\\n x=1\n", [(0, 11, (2, 3, 4), 4)], [["x", "=", "1"]]),
        (
            "x=1\r\ny=2\rz=3\n",
            [(0, 5, (0, 1, 2), 0), (5, 9, (4, 5, 6), 0), (9, 13, (8, 9, 10), 0)],
            [["x", "=", "1"], ["y", "=", "2"], ["z", "=", "3"]],
        ),
    ],
)
def test_logical_lines_exact_boundaries_and_significant_tokens(
    python_definition, text, expected, spellings
):
    scan, result = read_logical_lines(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert isinstance(result, tuple)
    assert [
        (line.span.start, line.span.end, line.tokens, line.indent) for line in result
    ] == expected
    assert [
        [text[scan.tokens[i].span.start : scan.tokens[i].span.end] for i in line.tokens]
        for line in result
    ] == spellings
    assert scan.text == text


def test_logical_lines_comments_and_blanks_leave_first_body_statement(
    python_definition,
):
    text = 'def f():\n # c\n\n    "doc"\n'
    scan, result = read_logical_lines(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert [(line.span, line.tokens, line.indent) for line in result] == [
        (SourceSpan(0, 9), (0, 1, 2, 3, 4), 0),
        (SourceSpan(15, 25), (9,), 4),
    ]
    assert SourceRegion(SourceSpan(10, 13), RegionKind.COMMENT) in scan.regions
    assert (
        text[scan.tokens[result[1].tokens[0]].span.start : scan.tokens[9].span.end]
        == '"doc"'
    )


def test_logical_lines_literal_interiors_are_opaque(python_definition):
    text = 'x="""[\n# }\r\n)"""\ny="[ # ]"'
    scan, result = read_logical_lines(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert [(line.span, line.tokens, line.indent) for line in result] == [
        (SourceSpan(0, 17), (0, 1, 2), 0),
        (SourceSpan(17, 26), (4, 5, 6), 0),
    ]
    assert (
        text[scan.tokens[2].span.start : scan.tokens[2].span.end] == '"""[\n# }\r\n)"""'
    )


@pytest.mark.parametrize(
    ("text", "code", "span"),
    [
        ("x=(]\n", "mismatched-bracket", SourceSpan(3, 4)),
        ("x=)\n", "mismatched-bracket", SourceSpan(2, 3)),
        ("x=(1\n", "unfinished-join", SourceSpan(2, 3)),
        ("x=1\\\n", "incomplete-continuation", SourceSpan(3, 4)),
        ("\\\r\n", "incomplete-continuation", SourceSpan(0, 1)),
        ("x\n    y\n  z\n", "inconsistent-indentation", SourceSpan(8, 10)),
        ("x\n\ty\n        z\n", "ambiguous-indentation", SourceSpan(5, 13)),
        ("x\n    y\n\tz\n", "ambiguous-indentation", SourceSpan(8, 9)),
        ("x\n\ty\n\t z\n        w\n", "ambiguous-indentation", SourceSpan(9, 17)),
    ],
)
def test_logical_lines_located_failures(python_definition, text, code, span):
    _, result = read_logical_lines(text, python_definition)
    assert isinstance(result, ReadFailure)
    diagnostic = result.diagnostics[0]
    assert diagnostic.stage == ReadStage.LEX
    assert diagnostic.code == code
    assert diagnostic.span == span


@pytest.mark.parametrize("text", ["x=1\\ # c\n", "x=1\\ \n", "x=1\\", "x=1\\y\n"])
def test_logical_lines_invalid_backslash_placement_is_located(python_definition, text):
    result = scan_tokens(text, python_definition)
    assert isinstance(result, ReadFailure)
    assert result.diagnostics[0].stage == ReadStage.LEX
    assert result.diagnostics[0].span == SourceSpan(3, 4)


@pytest.mark.parametrize(
    ("text", "end"),
    [
        ("x=1\\\n ", 6),
        ("x=1\\\n\t", 6),
        ("x=1\\\r\n ", 7),
        ("x=1\\\r\n\t", 7),
        ("x=1\\\r ", 6),
        ("x=1\\\r\t", 6),
    ],
)
def test_logical_lines_final_whitespace_completes_explicit_join(
    python_definition, text, end
):
    scan, result = read_logical_lines(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert [(line.span, line.tokens, line.indent) for line in result] == [
        (SourceSpan(0, end), (0, 1, 2), 0)
    ]
    assert [
        text[scan.tokens[i].span.start : scan.tokens[i].span.end]
        for i in result[0].tokens
    ] == ["x", "=", "1"]
    assert scan.regions[-1] == SourceRegion(SourceSpan(4, end), RegionKind.WHITESPACE)
    assert scan.text == text


@pytest.mark.parametrize("text", ["x=1\\\n", "x=1\\\r\n", "x=1\\\r"])
def test_logical_lines_immediate_eof_leaves_explicit_join_unfinished(
    python_definition, text
):
    _, result = read_logical_lines(text, python_definition)
    assert isinstance(result, ReadFailure)
    assert result.diagnostics[0].stage == ReadStage.LEX
    assert result.diagnostics[0].code == "incomplete-continuation"
    assert result.diagnostics[0].span == SourceSpan(3, 4)


@pytest.mark.parametrize(
    ("text", "tokens", "regions", "end"),
    [
        (
            'x=f"#{a["x"]!r:>{w}.{p}f}" # end\n',
            [
                ("identifier", "x"),
                ("operator", "="),
                ("interpolation_start", 'f"'),
                ("interpolation_literal", "#"),
                ("field_start", "{"),
                ("identifier", "a"),
                ("operator", "["),
                ("string", '"x"'),
                ("operator", "]"),
                ("conversion", "!r"),
                ("format_start", ":"),
                ("interpolation_literal", ">"),
                ("field_start", "{"),
                ("identifier", "w"),
                ("field_end", "}"),
                ("interpolation_literal", "."),
                ("field_start", "{"),
                ("identifier", "p"),
                ("field_end", "}"),
                ("interpolation_literal", "f"),
                ("field_end", "}"),
                ("interpolation_end", '"'),
                ("comment", "# end"),
                ("newline", "\n"),
            ],
            [
                ("code", "x="),
                ("literal", 'f"#'),
                ("code", "{a["),
                ("literal", '"x"'),
                ("code", "]!r:"),
                ("literal", ">"),
                ("code", "{w}"),
                ("literal", "."),
                ("code", "{p}"),
                ("literal", "f"),
                ("code", "}"),
                ("literal", '"'),
                ("whitespace", " "),
                ("comment", "# end"),
                ("whitespace", "\n"),
            ],
            26,
        ),
        (
            'f"{x # }" fake\r\n + 2}";y',
            [
                ("interpolation_start", 'f"'),
                ("field_start", "{"),
                ("identifier", "x"),
                ("comment", '# }" fake'),
                ("newline", "\r\n"),
                ("operator", "+"),
                ("number", "2"),
                ("field_end", "}"),
                ("interpolation_end", '"'),
                ("operator", ";"),
                ("identifier", "y"),
            ],
            [
                ("literal", 'f"'),
                ("code", "{x"),
                ("whitespace", " "),
                ("comment", '# }" fake'),
                ("whitespace", "\r\n "),
                ("code", "+"),
                ("whitespace", " "),
                ("code", "2}"),
                ("literal", '"'),
                ("code", ";y"),
            ],
            22,
        ),
    ],
)
def test_fstrings_exact_events_regions_and_fragment_end(
    python_definition, text, tokens, regions, end
):
    scan = scan_tokens(text, python_definition)
    assert not isinstance(scan, ReadFailure)
    assert [(t.kind, text[t.span.start : t.span.end]) for t in scan.tokens] == tokens
    assert [
        (r.kind.value, text[r.span.start : r.span.end]) for r in scan.regions
    ] == regions
    assert "".join(text[r.span.start : r.span.end] for r in scan.regions) == text
    assert all(
        a.span.end <= b.span.start
        for a, b in zip(scan.tokens, scan.tokens[1:], strict=False)
    )
    fragment = import_module(
        "comment_review.reading.python.interpolation"
    ).scan_interpolation(text, 2 if text.startswith("x=") else 0, python_definition)
    assert not isinstance(fragment, ReadFailure)
    assert fragment.end == end
    assert fragment.protected == ()


@pytest.mark.parametrize(
    ("text", "strings", "formats"),
    [
        ('f"{f"{f"{f"{f"{x}"}"}"}"}"', ['f"'] * 5, []),
        ("f\"{f'{x}'}\"", ['f"', "f'"], []),
        ('f"{ {"a": seq[1:3]} }"', ['f"'], []),
        ('f"{(lambda x: x)(2)} {(x := 4)}"', ['f"'], []),
        ('f"{value:{width}.{precision}f}"', ['f"'], [":"]),
        ('f"{value:{width:{precision}}}"', ['f"'], [":", ":"]),
        ('FR"{x}"', ['FR"'], []),
    ],
)
def test_fstrings_nested_fields_and_code_colons(
    python_definition, text, strings, formats
):
    result = scan_tokens(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert [
        text[t.span.start : t.span.end]
        for t in result.tokens
        if t.kind == "interpolation_start"
    ] == strings
    assert [
        text[t.span.start : t.span.end]
        for t in result.tokens
        if t.kind == "format_start"
    ] == formats
    assert result.tokens[-1].span.end == len(text)


@pytest.mark.parametrize("newline", ["\n", "\r", "\r\n"])
def test_fstrings_multiline_expression_is_one_logical_line(python_definition, newline):
    text = 'x=f"{a # }' + newline + " + \\" + newline + ' b}"' + newline + "y=2"
    scan, lines = read_logical_lines(text, python_definition)
    assert not isinstance(lines, ReadFailure)
    assert [text[line.span.start : line.span.end] for line in lines] == [
        'x=f"{a # }' + newline + " + \\" + newline + ' b}"' + newline,
        "y=2",
    ]
    assert all(
        scan.tokens[i].kind not in ("newline", "comment", "continuation")
        for line in lines
        for i in line.tokens
    )


@pytest.mark.parametrize(
    ("text", "payload", "fields"),
    [
        ('f"{{}}"', ["{{}}"], []),
        ('f"\\N{LEFT CURLY BRACKET}{x}"', ["\\N{LEFT CURLY BRACKET}"], ["x"]),
        ('rf"\\N{x}"', ["\\N"], ["x"]),
        ('f"\\{x}"', ["\\"], ["x"]),
        ('rf"\\{x}"', ["\\"], ["x"]),
        ('f"{x:=10}"', ["=10"], ["x"]),
    ],
)
def test_fstrings_literal_braces_and_escape_boundaries(
    python_definition, text, payload, fields
):
    scan = scan_tokens(text, python_definition)
    assert not isinstance(scan, ReadFailure)
    assert [
        text[t.span.start : t.span.end]
        for t in scan.tokens
        if t.kind == "interpolation_literal"
    ] == payload
    assert [
        text[t.span.start : t.span.end] for t in scan.tokens if t.kind == "identifier"
    ] == fields


@pytest.mark.parametrize("flag", ["s", "r", "a"])
def test_fstrings_conversions(python_definition, flag):
    text = 'f"{x!' + flag + '}"'
    scan = scan_tokens(text, python_definition)
    assert not isinstance(scan, ReadFailure)
    assert [(t.kind, text[t.span.start : t.span.end]) for t in scan.tokens] == [
        ("interpolation_start", 'f"'),
        ("field_start", "{"),
        ("identifier", "x"),
        ("conversion", "!" + flag),
        ("field_end", "}"),
        ("interpolation_end", '"'),
    ]


@pytest.mark.parametrize(
    "text",
    [
        'f"}"',
        'f"{"',
        'f"{}"',
        'f"{x!}"',
        'f"{x!q}"',
        'f"{x!rr}"',
        'f"{x!r',
        'f"{x:{w',
        'f"{x:{w}',
        'f"{f"{x',
        'f"{f"{x}"',
        'f"{[x}"',
        'f"text',
        'f"\\N{ABC',
        'f"abc\n"',
    ],
)
def test_fstrings_unfinished_nested_state_returns_located_failure(
    python_definition, text
):
    result = scan_tokens(text, python_definition)
    assert isinstance(result, ReadFailure)
    assert result.diagnostics[0].stage == ReadStage.LEX
    assert result.diagnostics[0].span is not None
    assert (
        0
        <= result.diagnostics[0].span.start
        <= result.diagnostics[0].span.end
        <= len(text)
    )


@pytest.mark.parametrize(
    ("text", "code", "span"),
    [
        ('f"}"', "unmatched-field-closer", SourceSpan(2, 3)),
        ('f"{}"', "empty-field", SourceSpan(2, 4)),
        ('f"{x!q}"', "invalid-conversion", SourceSpan(4, 6)),
        ('f"{x!rr}"', "invalid-conversion", SourceSpan(6, 7)),
        ('f"{x:{w', "unfinished-field", SourceSpan(5, 7)),
        ('f"{x:{w}', "unfinished-field", SourceSpan(2, 8)),
        ('f"{f"{x', "unfinished-field", SourceSpan(5, 7)),
        ('f"{f"{x}"', "unfinished-field", SourceSpan(2, 9)),
        ('f"{[x}"', "mismatched-bracket", SourceSpan(5, 6)),
    ],
)
def test_fstrings_failures_locate_innermost_open_state(
    python_definition, text, code, span
):
    result = scan_tokens(text, python_definition)
    assert isinstance(result, ReadFailure)
    assert result.diagnostics[0].code == code
    assert result.diagnostics[0].span == span


def test_fstrings_each_nested_truncation_fails_without_internal_exceptions(
    python_definition,
):
    text = 'f"{f"{f"{f"{f"{x}"}"}"}"}"'
    for end in range(2, len(text)):
        result = scan_tokens(text[:end], python_definition)
        assert isinstance(result, ReadFailure), end
        assert result.diagnostics[0].stage == ReadStage.LEX


def test_fstrings_nested_exact_offsets_and_regions(python_definition):
    text = "f\"{f'{x}'}\""
    result = scan_tokens(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert [(t.kind, t.span.start, t.span.end) for t in result.tokens] == [
        ("interpolation_start", 0, 2),
        ("field_start", 2, 3),
        ("interpolation_start", 3, 5),
        ("field_start", 5, 6),
        ("identifier", 6, 7),
        ("field_end", 7, 8),
        ("interpolation_end", 8, 9),
        ("field_end", 9, 10),
        ("interpolation_end", 10, 11),
    ]
    assert [(r.kind.value, r.span.start, r.span.end) for r in result.regions] == [
        ("literal", 0, 2),
        ("code", 2, 3),
        ("literal", 3, 5),
        ("code", 5, 8),
        ("literal", 8, 9),
        ("code", 9, 10),
        ("literal", 10, 11),
    ]


@pytest.mark.parametrize("text", ['f"{x != y}"', 'f"{x!r:}"'])
def test_fstrings_not_equal_and_conversion_with_empty_format(python_definition, text):
    result = scan_tokens(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert [
        (t.kind, text[t.span.start : t.span.end])
        for t in result.tokens
        if t.kind in ("operator", "conversion", "format_start")
    ] == (
        [("operator", "!=")]
        if text == 'f"{x != y}"'
        else [("conversion", "!r"), ("format_start", ":")]
    )


@pytest.mark.parametrize(
    ("text", "protection"),
    [
        ('x=f"{  value + 1 = \t }";tail', [("debug-expression", "  value + 1 = \t ")]),
        ('f"{ value =  !r:>{w}}"', [("debug-expression", " value =  ")]),
        ('f"{value=:}"', [("debug-expression", "value=")]),
        ('f"{value == other}"', []),
        ('f"{value != other}"', []),
        ('f"{(value := other)}"', []),
        ('t"{ value + 1 }"', [("template-expression", " value + 1 ")]),
        ('t"{ value + 1 !r:>{w}}"', [("template-expression", " value + 1 ")]),
        (
            't"{ value =  !r:>{w}}"',
            [
                ("template-expression", " value "),
                ("debug-expression", " value =  "),
            ],
        ),
        ('t"{ (x := 1) == 1 }"', [("template-expression", " (x := 1) == 1 ")]),
        ('rt"\\N{ value }\\n"', [("template-expression", " value ")]),
        (
            'f"{(\n value # spelling\n)= \n\t}"',
            [
                ("debug-expression", "(\n value # spelling\n)= \n\t"),
            ],
        ),
        (
            't"{\r\n value # spelling\r\n + 1 \r\n}"',
            [
                ("template-expression", "\r\n value # spelling\r\n + 1 \r\n"),
            ],
        ),
        (
            "t\"{ f'{x # nested\n}' + value # outer\n }\"",
            [
                ("template-expression", " f'{x # nested\n}' + value # outer\n "),
            ],
        ),
        (
            "f\"{ f'{x # nested\n}' + value # outer\n = }\"",
            [
                ("debug-expression", " f'{x # nested\n}' + value # outer\n = "),
            ],
        ),
        (
            "t\"{ f'{ value = }' }\"",
            [
                ("template-expression", " f'{ value = }' "),
                ("debug-expression", " value = "),
            ],
        ),
        (
            "f\"{ t'{ value }' = }\"",
            [
                ("debug-expression", " t'{ value }' = "),
                ("template-expression", " value "),
            ],
        ),
        (
            "t\"{t'{ x }'} { y }\"",
            [
                ("template-expression", "t'{ x }'"),
                ("template-expression", " x "),
                ("template-expression", " y "),
            ],
        ),
    ],
)
def test_interpolation_observable_source_exact_spelling(
    python_definition, text, protection
):
    result = scan_tokens(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert [
        (p.kind, text[p.span.start : p.span.end]) for p in result.protected
    ] == protection
    for record, (_, spelling) in zip(result.protected, protection, strict=True):
        start = text.index(spelling)
        assert record.span == SourceSpan(start, start + len(spelling))
        assert record.attachment is None
    assert "".join(text[r.span.start : r.span.end] for r in result.regions) == text
    assert all(
        a.span.end <= b.span.start
        for a, b in zip(result.tokens, result.tokens[1:], strict=False)
    )
    start = 2 if text.startswith("x=") else 0
    fragment = import_module(
        "comment_review.reading.python.interpolation"
    ).scan_interpolation(text, start, python_definition)
    assert not isinstance(fragment, ReadFailure)
    assert fragment.protected == result.protected
    assert fragment.end == (
        text.index(";tail") if text.endswith(";tail") else len(text)
    )


def test_template_observable_source_conversion_and_format_events(python_definition):
    text = 'x=t"before { value !s:>{width}} after"'
    result = scan_tokens(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert [(t.kind, text[t.span.start : t.span.end]) for t in result.tokens] == [
        ("identifier", "x"),
        ("operator", "="),
        ("interpolation_start", 't"'),
        ("interpolation_literal", "before "),
        ("field_start", "{"),
        ("identifier", "value"),
        ("conversion", "!s"),
        ("format_start", ":"),
        ("interpolation_literal", ">"),
        ("field_start", "{"),
        ("identifier", "width"),
        ("field_end", "}"),
        ("field_end", "}"),
        ("interpolation_literal", " after"),
        ("interpolation_end", '"'),
    ]
    assert [(p.kind, p.span) for p in result.protected] == [
        ("template-expression", SourceSpan(12, 19)),
    ]


@pytest.mark.parametrize(
    ("text", "comments", "protected_comments"),
    [
        ('f"{x # ordinary\n}"', ["# ordinary"], []),
        (
            't"{f\'{x # inner\n}\' # outer\n}" f"{y # ordinary\n}"',
            ["# inner", "# outer", "# ordinary"],
            ["# inner", "# outer"],
        ),
        (
            'f"{f\'{x # inner\n}\' # outer\n = }" f"{y # ordinary\n}"',
            ["# inner", "# outer", "# ordinary"],
            ["# inner", "# outer"],
        ),
        (
            "f\"{t'{x # inner\n}' # ordinary\n}\"",
            ["# inner", "# ordinary"],
            ["# inner"],
        ),
    ],
)
def test_interpolation_observable_source_comments_keep_nested_protection(
    python_definition, text, comments, protected_comments
):
    result = scan_tokens(text, python_definition)
    assert not isinstance(result, ReadFailure)
    comment_tokens = [t for t in result.tokens if t.kind == "comment"]
    assert [text[t.span.start : t.span.end] for t in comment_tokens] == comments
    assert [
        text[t.span.start : t.span.end]
        for t in comment_tokens
        if any(
            p.span.start <= t.span.start < t.span.end <= p.span.end
            for p in result.protected
        )
    ] == protected_comments


@pytest.mark.parametrize(
    ("text", "code", "span"),
    [
        ('t"}"', "unmatched-field-closer", SourceSpan(2, 3)),
        ('t"{}"', "empty-field", SourceSpan(2, 4)),
        ('t"{=}"', "empty-field", SourceSpan(2, 4)),
        ('t"{x!q}"', "invalid-conversion", SourceSpan(4, 6)),
        ('t"{x:{w}', "unfinished-field", SourceSpan(2, 8)),
        ("t\"{f'{x", "unfinished-field", SourceSpan(5, 7)),
        ('t"{[x}"', "mismatched-bracket", SourceSpan(5, 6)),
        ('t"{x=other}"', "invalid-debug-expression", SourceSpan(5, 10)),
        ('f"{x=other}"', "invalid-debug-expression", SourceSpan(5, 10)),
    ],
)
def test_interpolation_observable_source_malformed_replacements_are_located(
    python_definition, text, code, span
):
    result = scan_tokens(text, python_definition)
    assert isinstance(result, ReadFailure)
    assert result.diagnostics[0].stage == ReadStage.LEX
    assert result.diagnostics[0].code == code
    assert result.diagnostics[0].span == span
