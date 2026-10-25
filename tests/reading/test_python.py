import ast
from dataclasses import FrozenInstanceError, replace
from importlib import import_module
from importlib.resources import files

import pytest

from comment_review.reading.definitions import LanguageDefinition, decode_definition
from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage
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


@pytest.fixture
def records():
    try:
        return import_module("comment_review.reading.python.records")
    except ModuleNotFoundError:
        pytest.skip("Python source record module is not implemented")


def literal_value(text, payload):
    """The value of a payload's literals: which docstring the read recognized."""
    return "".join(
        ast.literal_eval(text[span.start : span.end])
        for span in payload.expression.components
    )


def test_records_module_exists():
    try:
        import_module("comment_review.reading.python.records")
    except ModuleNotFoundError:
        pytest.fail("Python source record module is not implemented", pytrace=False)


def test_completed_read_projects_documentation_from_source_positions(python_definition):
    from pathlib import Path

    from comment_review.reading.python.projection import (
        code_lines_for,
        paragraphs_for,
    )
    from comment_review.reading.python.records import PythonRead

    text = (
        '# heading\r\n"module\\nprose"\r\n'
        "@mark\r\ndef render(\r\n    value,\r\n):\r\n"
        '    "body " "prose"; return value # detail\r\n'
        "class Container:\r\n    pass\r\n"
    )
    result = import_module("comment_review.reading.python").read_python(
        text, python_definition
    )
    assert isinstance(result, PythonRead)
    reduced = PythonRead(result.source, result.payloads, result.protected)
    paragraphs = paragraphs_for(Path("invented.py"), reduced)
    assert not isinstance(paragraphs, ReadFailure)
    assert [(p.raw_lines, p.address, p.anchor) for p in paragraphs] == [
        (["# heading"], "", ""),
        (['"module\\nprose"'], "a0", ""),
        (['    "body " "prose"'], "a1", ""),
        ([" # detail"], "", "    return value"),
    ]
    lines = code_lines_for(reduced)
    assert [(c.line, c.documents) for c in lines if c.documents] == [
        (4, DocPlace(6, False)),
        (9, DocPlace(9, False)),
    ]
    assert 7 not in [c.line for c in lines]
    assert [c.code for c in lines if c.line == 8] == ["    return value"]
    assert literal_value(reduced.source.text, reduced.payloads[0]) == "module\nprose"
    assert reduced.source.reconstruct() == text.replace(
        '"prose"; return', '"prose"\r\n    return'
    )


@pytest.mark.parametrize(
    "expression",
    [
        '"  First\\t  second.\\n "',
        'r"  First\t  second.  "',
        '("  First "\n     "\\tsecond.\\n ")',
        '"""\n  First\t second.\n"""',
        '" \\t\\n "',
        '""',
    ],
)
def test_documentation_paragraph_preserves_payload_and_source(
    python_definition, expression
):
    from pathlib import Path

    from comment_review.reading.python import read_python
    from comment_review.reading.python.projection import paragraphs_for

    text = expression + "\r\nvalue = 1\r\n"
    result = read_python(text, python_definition)
    assert not isinstance(result, ReadFailure)
    source = result.source
    payload = result.payloads[0]
    paragraphs = paragraphs_for(Path("invented.py"), result)
    assert not isinstance(paragraphs, ReadFailure)
    assert len(paragraphs) == 1
    assert paragraphs[0].raw_lines == expression.splitlines()
    assert paragraphs[0].address == "a0"
    assert result.source is source
    assert result.payloads[0] is payload
    assert payload.expression.statement == SourceSpan(0, len(expression))
    assert source.slice(payload.expression.statement) == expression
    assert source.reconstruct() == text


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
    payload = records.DocumentationPayload(expression)
    return records.PythonRead(source, (payload,), ())


def test_records_empty_read_preserves_exact_source(records):
    source = SourceStructure("", (), (), (), ())
    result = records.PythonRead(source, (), ())
    assert result.source is source
    assert result.source.reconstruct() == ""
    assert records.PythonScan("", (), (), ()).text == ""


def test_records_documented_read_reconstructs_and_is_frozen(records):
    result = documented_read(records)
    assert result.source.reconstruct() == 'def f():\n    "a\\n" "b"\n'
    assert result.source.slice(result.payloads[0].expression.statement) == '"a\\n" "b"'
    with pytest.raises(FrozenInstanceError):
        result.payloads[0].expression = result.payloads[0].expression


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


def test_records_payload_keeps_raw_expression(records):
    expression = records.DocumentationExpression(
        SourceSpan(0, 13), (SourceSpan(0, 7), SourceSpan(8, 13)), None
    )
    assert records.DocumentationPayload(expression).expression is expression


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
        lambda r: r.PythonPlacement((), (), (0,)),
        lambda r: r.PythonPlacement((), (), (-1,)),
        lambda r: r.PythonPlacement((), (), (True,)),
        lambda r: r.DocumentationExpression(
            SourceSpan(2, 4), (SourceSpan(0, 3),), None
        ),
        lambda r: r.DocumentationExpression(
            SourceSpan(0, 4), (SourceSpan(0, 3), SourceSpan(2, 4)), None
        ),
        lambda r: r.DocumentationPayload(None),
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


def test_records_reject_protection_outside_the_source(records):
    result = documented_read(records)
    for changed in (
        {"protected": (records.ProtectedSource(SourceSpan(0, 99), "literal", None),)},
        {
            "protected": (
                records.ProtectedSource(
                    SourceSpan(0, 1), "directive", SourceSpan(0, 99)
                ),
            )
        },
    ):
        with pytest.raises(ValueError):
            replace(result, **changed)


def test_records_allow_declaration_positions_without_a_tree(records):
    declaration = SourceDeclaration(SourceSpan(5, 13), 5, "function")
    placement = records.PythonPlacement((), (declaration,), (15,))
    assert placement.declarations == (declaration,)
    assert placement.insertions == (15,)
    assert not any(
        hasattr(placement, name) for name in ("facts", "suites", "statements")
    )


def test_records_reject_payload_wrong_statement_and_owner(records):
    result = documented_read(records)
    payload = result.payloads[0]
    for changes in (
        {"payloads": ()},
        {
            "payloads": (
                replace(
                    payload,
                    expression=replace(
                        payload.expression, statement=SourceSpan(12, 22)
                    ),
                ),
            )
        },
    ):
        with pytest.raises(ValueError):
            replace(result, **changes)
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


def test_records_nested_declarations_keep_only_source_positions(records):
    declarations = (
        SourceDeclaration(SourceSpan(0, 8), 0, "function"),
        SourceDeclaration(SourceSpan(13, 21), 13, "function"),
    )
    placement = records.PythonPlacement((), declarations, (13, 25))
    assert placement.declarations == declarations
    assert placement.insertions == (13, 25)


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


@pytest.mark.parametrize(
    "preamble",
    [
        b"",
        b"# coding: utf-8\r\n",
        b"# header\r\n# coding: UTF_8_SIG\r\n",
        b"\r\n# coding: utf-8-anything\r\n",
    ],
)
def test_read_python_initial_bom_preserves_exact_source_and_documentation(
    python_definition, preamble
):
    from comment_review.machine.repo import source_from_bytes
    from comment_review.reading.python import read_python

    raw = b"\xef\xbb\xbf" + preamble + b'"module"\r\nx=1\r\n'
    source = source_from_bytes(raw)
    result = read_python(source.text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert result.source.text is source.text
    assert result.source.reconstruct().encode("utf-8") == raw
    assert literal_value(result.source.text, result.payloads[0]) == "module"
    statement = result.payloads[0].expression.statement
    assert statement.start == 1 + len(preamble)
    assert result.source.slice(statement) == '"module"'
    assert [item.kind for item in result.protected] == (
        ["encoding"] if preamble else []
    )


def test_read_python_bom_does_not_hide_indentation(python_definition):
    from comment_review.reading.python import read_python

    text = '\ufeff    "doc"\n'
    result = read_python(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert result.payloads == ()
    assert result.source.reconstruct() == text


def test_read_python_bom_cookie_still_rejects_incompatible_encoding(python_definition):
    from comment_review.reading.python import read_python

    result = read_python('\ufeff# coding: latin-1\n"doc"\n', python_definition)
    assert isinstance(result, ReadFailure)
    assert result.diagnostics[0].code == "unsupported-source-encoding"
    assert result.diagnostics[0].span == SourceSpan(1, 18)


@pytest.mark.parametrize(
    "text",
    [
        "\x00",
        "# nul\x00\n",
        "x='a\x00b'\n",
        'x=f"a\x00{value}"\n',
        '"doc\x00"\n',
    ],
)
def test_tokens_source_nul_refuses_even_inside_literals_and_comments(
    python_definition, text
):
    result = scan_tokens(text, python_definition)
    assert isinstance(result, ReadFailure)
    at = text.index("\x00")
    assert result.diagnostics == (
        ReadDiagnostic(
            ReadStage.LEX, "source-nul", "source nul", SourceSpan(at, at + 1)
        ),
    )


def scan_tokens(text, definition):
    try:
        scanner = import_module("comment_review.reading.python.scanner")
    except ModuleNotFoundError:
        pytest.fail("Python token scanner is not implemented", pytrace=False)
    return scanner.scan_python(text, definition)


@pytest.mark.parametrize("ending", ["", "\r", "\n", "\r\n"])
@pytest.mark.parametrize(
    "code",
    ["0x", "0b2", "0123", "1e+", "1__2", "3_", "1e_2", "0x1j", "$!", "\u200b"],
)
def test_scanner_opaque_code_exposes_exact_comment_and_shields_literal(
    python_definition, code, ending
):
    text = code + ' "# literal" # actual' + ending
    result = scan_tokens(text, python_definition)
    assert not isinstance(result, ReadFailure)
    start = text.index("# actual")
    assert [
        region.span for region in result.regions if region.kind == RegionKind.COMMENT
    ] == [SourceSpan(start, start + len("# actual"))]
    assert "".join(text[r.span.start : r.span.end] for r in result.regions) == text
    assert all(
        t.kind not in {"identifier", "number", "operator"} for t in result.tokens
    )


@pytest.mark.parametrize(
    "name", ["stuff", "buffer", "raft", "prefixfr", "1f", "\u03c0f"]
)
def test_scanner_literal_prefix_requires_name_boundary(python_definition, name):
    text = name + '"{# literal}"# actual'
    result = scan_tokens(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert [(r.kind, text[r.span.start : r.span.end]) for r in result.regions] == [
        (RegionKind.CODE, name),
        (RegionKind.LITERAL, '"{# literal}"'),
        (RegionKind.COMMENT, "# actual"),
    ]
    assert [t.kind for t in result.tokens] == ["code", "string", "comment"]


@pytest.mark.parametrize("prefix", ["f", "t"])
@pytest.mark.parametrize(
    "expression", ["0b2", "$", "a==b", "a!=b", "a<=b", "a>=b", "(a:=b)"]
)
def test_scanner_opaque_interpolation_code_keeps_field_boundaries(
    python_definition, prefix, expression
):
    text = prefix + '"{' + expression + ' # field\r\n} # literal"# actual'
    result = scan_tokens(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert [
        text[r.span.start : r.span.end]
        for r in result.regions
        if r.kind == RegionKind.COMMENT
    ] == ["# field", "# actual"]
    assert not any(p.kind == "debug-expression" for p in result.protected)
    assert "".join(text[r.span.start : r.span.end] for r in result.regions) == text


def test_read_python_opaque_code_preserves_documentation_and_comment_anchor(
    python_definition,
):
    from pathlib import Path

    from comment_review.reading.python.projection import paragraphs_for

    text = '"module"\r\n$! = 0b2 # actual\r\ndef render():\r\n    "body"\r\n'
    result = import_module("comment_review.reading.python").read_python(
        text, python_definition
    )
    assert not isinstance(result, ReadFailure)
    assert result.source.reconstruct() == text
    assert [
        literal_value(result.source.text, payload) for payload in result.payloads
    ] == ["module", "body"]
    paragraphs = paragraphs_for(Path("invented.py"), result)
    assert not isinstance(paragraphs, ReadFailure)
    assert [(p.raw_lines, p.anchor) for p in paragraphs] == [
        (['"module"'], ""),
        ([" # actual"], "$! = 0b2"),
        (['    "body"'], ""),
    ]


@pytest.mark.parametrize("keyword", ["except*", "except *"])
def test_opaque_exception_headers_preserve_nested_documentation(
    python_definition, keyword
):
    text = "try:\n    pass\n" + keyword + ' Error:\n    def render():\n        "body"\n'
    _, result = read_placement(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert [text[d.header.start : d.header.end] for d in result.declarations] == [
        "def render():"
    ]
    expressions = read_documentation(text, python_definition)[2]
    assert [text[e.statement.start : e.statement.end] for e in expressions] == [
        '"body"'
    ]
    assert expressions[0].declaration == 0
    assert scan_tokens(text, python_definition).text == text


@pytest.mark.parametrize(
    ("preamble", "header", "indent"),
    [
        ("", "if~ready:", 4),
        ("", "while~ready:", 4),
        ("if ready:\n    pass\n", "elif+ready:", 4),
        ("try:\n    pass\n", "except*ValueError:", 4),
        ("try:\n    pass\n", "except *ValueError:", 4),
        ("try:\n    pass\n", "except+Error:", 4),
        ("", "match-value:\n    case _:", 8),
        ("", "match value:\n    case-1:", 8),
        ("", "for*x, in [[1]]:", 4),
        ("", "async for*x, in [[1]]:", 4),
        ("", "with~resource:", 4),
        ("", "async with~resource:", 4),
        ("", "if lambda*x: 0:", 4),
        ("", "if+lambda*x: 0:", 4),
        ("", "if lambda*x: lambda*y: 0:", 4),
    ],
)
def test_compact_header_spelling_preserves_nested_documentation_positions(
    python_definition, preamble, header, indent
):

    body = " " * indent + "def render():\n" + " " * (indent + 4) + '"body"\n'
    text = preamble + header + "\n" + body
    result = import_module("comment_review.reading.python").read_python(
        text, python_definition
    )
    assert not isinstance(result, ReadFailure)
    assert result.source.reconstruct() == text
    assert [
        literal_value(result.source.text, payload) for payload in result.payloads
    ] == ["body"]
    declaration = result.source.declarations[0]
    start = text.index("def render():")
    document = text.index('"body"')
    assert declaration.header == SourceSpan(start, start + len("def render():"))
    assert declaration.anchor == start
    assert result.payloads[0].expression.statement == SourceSpan(document, document + 6)
    assert result.payloads[0].expression.declaration == 0


@pytest.mark.parametrize(
    ("text", "regions", "events"),
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
                ("code", "match"),
                ("code", "_x2"),
                ("code", "\u03c0"),
                ("code", "e\u0301"),
                ("code", "\U00011f02x"),
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
                ("code", "x"),
                ("boundary", "="),
                ("code", "1"),
                ("comment", "# end"),
                ("newline", "\r\n"),
                ("comment", "#tail"),
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
                ("code", "a"),
                ("newline", "\r\n"),
                ("code", "b"),
                ("newline", "\r"),
                ("code", "c"),
                ("newline", "\n"),
                ("continuation", "\\"),
                ("newline", "\r\n"),
                ("code", "d"),
            ],
        ),
        (
            "1+0xff;0b_10,0o7:1_000",
            [("code", 0, 22)],
            [
                ("code", "1+0xff"),
                ("boundary", ";"),
                ("code", "0b_10,0o7"),
                ("boundary", ":"),
                ("code", "1_000"),
            ],
        ),
        (
            ".5+1.e-2+3_0.2_5e+1_0J",
            [("code", 0, 22)],
            [("code", ".5+1.e-2+3_0.2_5e+1_0J")],
        ),
        ("00j+0_0+12j+1..2", [("code", 0, 16)], [("code", "00j+0_0+12j+1..2")]),
        (
            "**=//=<<=>>=:=...!=->()[]{};:@,~",
            [("code", 0, 32)],
            [
                ("code", "**=//=<<=>>=:=...!=->"),
                ("boundary", "("),
                ("boundary", ")"),
                ("boundary", "["),
                ("boundary", "]"),
                ("boundary", "{"),
                ("boundary", "}"),
                ("boundary", ";"),
                ("boundary", ":"),
                ("code", "@,~"),
            ],
        ),
    ],
)
def test_tokens_exact_partition_and_spelling(python_definition, text, regions, events):
    result = scan_tokens(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert result.text == text
    assert [(r.kind.value, r.span.start, r.span.end) for r in result.regions] == regions
    assert [(t.kind, text[t.span.start : t.span.end]) for t in result.tokens] == events
    assert "".join(text[r.span.start : r.span.end] for r in result.regions) == text
    assert result.protected == ()


@pytest.mark.parametrize(
    ("text", "start", "end"),
    [
        ("x \\", 2, 3),
        ("\\ \n", 0, 1),
    ],
)
def test_tokens_fail_locally_on_incomplete_continuation(
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
        ("code", SourceSpan(0, len(spelling)))
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
def test_tokens_punctuation_spelling_remains_code(python_definition, spelling):
    result = scan_tokens(spelling, python_definition)
    assert not isinstance(result, ReadFailure)
    assert [(r.kind, r.span) for r in result.regions] == [
        (RegionKind.CODE, SourceSpan(0, len(spelling)))
    ]
    assert all(t.kind in {"code", "boundary"} for t in result.tokens)
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
        ("code", SourceSpan(0, 1)),
        ("boundary", SourceSpan(1, 2)),
        ("string", SourceSpan(2, end)),
        ("code", SourceSpan(end, end + 2)),
        ("comment", SourceSpan(end + 2, end + 8)),
        ("newline", SourceSpan(end + 8, end + 10)),
    ]
    assert text[result.tokens[2].span.start : result.tokens[2].span.end] == literal
    assert text[result.tokens[4].span.start : result.tokens[4].span.end] == "# real"
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
        ("code", SourceSpan(0, 4)),
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
        ("code", "x"),
        ("boundary", "="),
        ("interpolation_start", prefix + quote),
        ("field_start", "{"),
        ("code", "x"),
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
    "text",
    [
        "1in [1]",
        "1if True else 0",
        "0x1or 2",
        "1and 2",
        "1jand 2",
        "1else",
        "1for",
        "1is",
        "0x1for 2",
        "1e2or",
    ],
)
def test_tokens_numeric_keyword_spelling_is_opaque(python_definition, text):
    result = scan_tokens(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert all(t.kind in {"code", "boundary"} for t in result.tokens)
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
def test_tokens_numeric_suffix_spelling_is_opaque(python_definition, text, end):
    result = scan_tokens(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert [(r.kind, r.span) for r in result.regions] == [
        (RegionKind.CODE, SourceSpan(0, end))
    ]
    assert [(t.kind, t.span) for t in result.tokens] == [("code", SourceSpan(0, end))]
    assert "".join(text[r.span.start : r.span.end] for r in result.regions) == text


def read_logical_lines(text, definition):
    scan = scan_tokens(text, definition)
    assert not isinstance(scan, ReadFailure)
    try:
        structure = import_module("comment_review.reading.python.structure")
    except ModuleNotFoundError:
        pytest.fail("Python logical lines are not implemented", pytrace=False)
    return scan, structure.logical_lines(scan, definition)


def read_placement(text, definition):
    scan, lines = read_logical_lines(text, definition)
    if isinstance(lines, ReadFailure):
        return scan, lines
    structure = import_module("comment_review.reading.python.structure")
    assert hasattr(structure, "place_declarations"), (
        "Python declaration placement is not implemented"
    )
    return scan, structure.place_declarations(scan, lines, definition)


@pytest.mark.parametrize("text", ["", "# comment\n\n"])
def test_placement_empty_module(python_definition, text):
    _, result = read_placement(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert result.declarations == ()
    assert result.lines == ()
    assert result.insertions == ()
    assert scan_tokens(text, python_definition).text == text


def test_declarations_decorated_headers_and_async_anchor(python_definition):
    text = (
        '@factory("class: def", lambda: {"key": value[1:3]})\n'
        "# between decorator and declaration\n"
        "class C[T](Base):\n"
        "    @decorate\n"
        "    # before method\n"
        "    async \\\n"
        "    def method[U](\n"
        '        item: dict[str, int] = {"key": value[1:3]},\n'
        "        callback=(lambda x: x),\n"
        '        message=f"{value:{width}}",\n'
        "    ) -> tuple[U, int]:\n"
        "        # before body\n"
        "        return item\n"
    )
    _, result = read_placement(text, python_definition)
    assert not isinstance(result, ReadFailure)
    class_start = text.index("class C")
    async_start = text.index("async ")
    method_end = text.index(") -> tuple[U, int]:") + len(") -> tuple[U, int]:")
    assert result.declarations == (
        SourceDeclaration(
            SourceSpan(class_start, class_start + len("class C[T](Base):")),
            class_start,
            "class",
        ),
        SourceDeclaration(
            SourceSpan(async_start, method_end), async_start, "async-function"
        ),
    )
    assert result.insertions == (text.index("@decorate"), text.index("return item"))
    assert scan_tokens(text, python_definition).text == text


def test_modern_syntax_type_parameters_aliases_and_soft_keyword_names(
    python_definition,
):
    text = (
        "class Crate[\n"
        "    T: (int, str) = int,\n"
        "    *Ts = tuple[int, ...],\n"
        "](Base):\n"
        "    def build[U: Value = Default](\n"
        "        value: U = factory(\n"
        '            {"# is literal text": (lambda item: (item,))},\n'
        "        ),\n"
        "    ) -> U:\n"
        "        return value\n"
        "type Pair[Item = str] = tuple[Item, Item]\n"
        "match = 1\n"
        "case = 2\n"
        "type = value\n"
        "lazy = value\n"
        "def match():\n"
        "    pass\n"
        "def case():\n"
        "    pass\n"
        "def type():\n"
        "    pass\n"
        "def lazy():\n"
        "    pass\n"
        "# one real comment\n"
    )
    scan, result = read_placement(text, python_definition)
    assert not isinstance(result, ReadFailure)

    assert [
        text[item.header.start : item.header.end] for item in result.declarations
    ] == [
        "class Crate[\n    T: (int, str) = int,\n    *Ts = tuple[int, ...],\n](Base):",
        "def build[U: Value = Default](\n        value: U = factory(\n"
        '            {"# is literal text": (lambda item: (item,))},\n'
        "        ),\n    ) -> U:",
        "def match():",
        "def case():",
        "def type():",
        "def lazy():",
    ]
    assert [
        region.span for region in scan.regions if region.kind == RegionKind.COMMENT
    ] == [SourceSpan(text.index("# one real comment"), len(text) - 1)]
    assert [
        text[token.span.start : token.span.end]
        for token in scan.tokens
        if token.kind == "code"
        and text[token.span.start : token.span.end] in {"match", "case", "type", "lazy"}
    ] == ["type", "match", "case", "type", "lazy", "match", "case", "type", "lazy"]
    assert scan.text == text
    assert len(result.insertions) == 6


def test_modern_syntax_match_case_lazy_imports_and_async_ownership(
    python_definition,
):
    text = (
        "lazy import json\n"
        "lazy from pathlib import Path\n"
        "lazy = value\n"
        "async def collect[Item = object](source):\n"
        "    match source:\n"
        "        case [first, *rest] if ready(first):\n"
        "            async with acquire(first) as lease:\n"
        "                async for item in lease.items():\n"
        "                    await consume(item)\n"
        '                    rendered = f"{lookup["item"]!r} # literal"\n'
        '                    template = t"item={lookup["item"]}"\n'
    )
    scan, result = read_placement(text, python_definition)
    assert not isinstance(result, ReadFailure)
    start = text.index("async def")
    assert result.declarations == (
        SourceDeclaration(
            SourceSpan(start, text.index(":", start) + 1), start, "async-function"
        ),
    )
    assert result.insertions == (text.index("match source:"),)
    assert scan.text == text
    assert not any(region.kind == RegionKind.COMMENT for region in scan.regions)
    assert read_documentation(text, python_definition)[2] == ()


def test_modern_syntax_unpacked_comprehensions_remain_expression_tokens(
    python_definition,
):
    text = (
        "def flatten(groups):\n"
        "    listed = [*parts for parts in groups]\n"
        "    unique = {*parts for parts in groups}\n"
        "    generated = (*parts for parts in groups)\n"
        "    mapped = {**pairs for pairs in groups}\n"
        "    nested = [*(value for value in part) for part in groups]\n"
        "    return listed, unique, generated, mapped, nested\n"
    )
    scan, result = read_placement(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert result.declarations == (SourceDeclaration(SourceSpan(0, 20), 0, "function"),)
    assert result.insertions == (text.index("listed ="),)
    assert read_documentation(text, python_definition)[2] == ()
    assert scan.text == text


def test_nested_declaration_headers_and_insertions_under_opaque_controls(
    python_definition,
):
    text = (
        "def outer():\n"
        "    if ready:\n"
        "        def repeated(): pass\n"
        "    else:\n"
        "        class repeated:\n"
        "            try:\n"
        "                @decorate\n"
        "                def repeated(): pass\n"
        "            finally: cleanup()\n"
        "if other:\n"
        "    def repeated(): pass\n"
    )
    _, result = read_placement(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert [text[d.header.start : d.header.end] for d in result.declarations] == [
        "def outer():",
        "def repeated():",
        "class repeated:",
        "def repeated():",
        "def repeated():",
    ]
    assert result.insertions == (
        text.index("if ready:"),
        text.index("pass"),
        text.index("try:"),
        text.index("pass", text.index("@decorate")),
        text.rindex("pass"),
    )
    assert scan_tokens(text, python_definition).text == text


@pytest.mark.parametrize(
    ("text", "header", "insertion"),
    [
        ("def f(): pass; work()\n", "def f():", 9),
        ("class C: # trailing\n    # body\n", "class C:", 20),
        ("def f():", "def f():", 8),
        ("def f():\nx=1\n", "def f():", 9),
        ("def f():\n    # body\n    x=1\n", "def f():", 24),
        ("def f():\n    @decorate\n    def g(): pass\n", "def f():", 13),
    ],
)
def test_declarations_body_insertion_is_absolute_and_bounded(
    python_definition, text, header, insertion
):
    _, result = read_placement(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert result.declarations[0] == SourceDeclaration(
        SourceSpan(0, len(header)),
        0,
        "class" if header.startswith("class") else "function",
    )
    assert result.insertions[0] == insertion
    assert 0 <= insertion <= len(text)


def test_declarations_keep_exact_identifier_spelling(python_definition):
    text = "def \u212a(): pass\nclass \ufb03: pass\n"
    _, result = read_placement(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert [text[d.header.start : d.header.end] for d in result.declarations] == [
        "def \u212a():",
        "class \ufb03:",
    ]


@pytest.mark.parametrize(
    "text", ["def (): pass\n", "class (): pass\n", "async def (): pass\n"]
)
def test_declaration_name_spelling_is_opaque(python_definition, text):
    _, result = read_placement(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert len(result.declarations) == 1
    assert result.insertions[0] == text.index("pass")
    assert read_documentation(text, python_definition)[2] == ()
    assert scan_tokens(text, python_definition).text == text


def test_declarations_ignore_names_literals_comments_and_type_aliases(
    python_definition,
):
    text = (
        "# def fake():\n"
        'message = "class C: async def fake():"\n'
        'formatted = f"{value:{width}} def fake():"\n'
        "defector = lambda item: item\n"
        "obj.class_factory(); obj.async_function()\n"
        "type Alias[T] = dict[str, T]\n"
        "match = case = type = lazy = 1\n"
        "@decorate(lambda: 'def hidden():')\n"
        "def class_factory(): pass\n"
    )
    _, result = read_placement(text, python_definition)
    assert not isinstance(result, ReadFailure)
    start = text.index("def class_factory")
    assert result.declarations == (
        SourceDeclaration(
            SourceSpan(start, start + len("def class_factory():")), start, "function"
        ),
    )


def test_nested_declaration_documentation_and_semicolons(python_definition):
    text = (
        'class C:\n    def f():\n        # before\n        "doc"; x=1\n    y=2\nz=3\n'
    )
    scan, result = read_placement(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert [text[d.header.start : d.header.end] for d in result.declarations] == [
        "class C:",
        "def f():",
    ]
    assert result.insertions == (13, 47)
    expressions = read_documentation(text, python_definition)[2]
    assert len(expressions) == 1
    assert expressions[0].declaration == 1
    assert (
        text[expressions[0].statement.start : expressions[0].statement.end] == '"doc";'
    )
    assert scan.text == text


def test_opaque_inline_control_code_cannot_claim_docs(python_definition):
    text = 'if x: "doc"; y=2;\nelif y: z=3\nelse: w=4\n'
    scan, result = read_placement(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert scan_tokens(text, python_definition).text == text
    assert read_documentation(text, python_definition)[2] == ()


@pytest.mark.parametrize(
    "text",
    [
        "for x in xs:\n    if x:\n        a()\n"
        "    else:\n        b()\nelse:\n    c()\n",
        "try: a()\nexcept E: b()\nexcept F: c()\nelse: d()\nfinally: e()\n",
        "try: a()\nexcept* E: b()\nfinally: c()\n",
        "async def f():\n    async for x in xs:\n"
        "        async with cm:\n            a()\n    else:\n        b()\n",
        "match x:\n    case {'a': y} if y:\n        a()\n    case _:\n        b()\n",
        "while x:\n    with cm:\n        a()\nelse:\n    b()\n",
    ],
)
def test_opaque_control_layout_preserves_source(python_definition, text):
    _, result = read_placement(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert scan_tokens(text, python_definition).text == text
    assert read_documentation(text, python_definition)[2] == ()


@pytest.mark.parametrize(
    "text",
    [
        "value: dict[str, int] = {'a': xs[1:]}\n",
        "callback = lambda x: (lambda y: x+y)\n",
        'value = f"{dict(a=lambda: x):{width}};:"; next=1\n',
        'value = t"{dict(a=lambda: x):{width}};:"; next=1\n',
        "match = {'case': lambda: x}; case: int = 1\n",
        "match(x); case(x); type=1; lazy=2\n",
        "match.attr: int = 1\n",
        "match: int; case: str; type: int; lazy: int\n",
    ],
)
def test_opaque_contextual_colons_cannot_claim_docs(python_definition, text):
    _, result = read_placement(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert scan_tokens(text, python_definition).text == text
    assert read_documentation(text, python_definition)[2] == ()


@pytest.mark.parametrize(
    "header",
    [
        "if lambda x: x:",
        "if (lambda x: x):",
        "if {'a': xs[1:]}:",
        'if f"{dict(a=lambda: x):{width}};:":',
        "def f(x: int) -> dict[str, int]:",
    ],
)
def test_header_boundaries_shield_nested_expressions(python_definition, header):
    text = header + "\n    value=1\n"
    scan, result = read_placement(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert scan.text == text
    expected = (
        (SourceDeclaration(SourceSpan(0, len(header)), 0, "function"),)
        if header.startswith("def ")
        else ()
    )
    assert result.declarations == expected
    assert read_documentation(text, python_definition)[2] == ()


@pytest.mark.parametrize(
    ("text", "body", "membership"),
    [
        ("def f():", SourceSpan(8, 8), ()),
        ("def f():\n    # removed\n\n", SourceSpan(9, 24), ()),
        ("def f():\n# c\nx=1\n", SourceSpan(9, 13), ()),
        ("if x:\n    def f():\n        # removed\ny=1\n", SourceSpan(19, 37), ()),
    ],
)
def test_empty_declarations_retain_bounded_insertion(
    python_definition, text, body, membership
):
    _, result = read_placement(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert result.insertions[-1] == body.start
    assert 0 <= result.insertions[-1] <= len(text)
    assert read_documentation(text, python_definition)[2] == ()


@pytest.mark.parametrize(
    "text",
    [
        "    x=1\n",
        "x=1\n    y=2\n",
        "if x: y=1\n    z=2\n",
        "if x:\n    y=1\n  z=2\n",
        "else: x=1\n",
        "if x: a()\nelse: b()\nelif y: c()\n",
        "for x in xs: a()\nelif y: b()\n",
        "try: a()\nelse: b()\n",
        "try: a()\nexcept E: b()\nexcept* F: c()\n",
        "match x:\n    y=1\n",
        "if x: if y: a()\n",
        "if x\n    y=1\n",
        "x=1;; y=2\n",
    ],
)
def test_opaque_grammar_spellings_preserve_source(python_definition, text):
    _, result = read_placement(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert scan_tokens(text, python_definition).text == text
    assert read_documentation(text, python_definition)[2] == ()


def test_classification_reads_source_boundaries_without_statement_records(
    python_definition,
):
    text = "x=1\ny=2 # detail\n"
    result = import_module("comment_review.reading.python").read_python(
        text, python_definition
    )
    assert not isinstance(result, ReadFailure)
    assert result.source.reconstruct() == text
    assert result.source.slice(result.source.sections[0].span) == "# detail\n"
    assert result.source.position(result.source.sections[0].span.start).column == 4


@pytest.mark.parametrize("prefix", ["f", "t"])
def test_opaque_control_interpolation_punctuation_cannot_claim_docs(
    python_definition, prefix
):
    text = f'if {prefix}"{{x; y}}": "doc"; z=1\n'
    scan, result = read_placement(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert scan_tokens(text, python_definition).text == text
    assert read_documentation(text, python_definition)[2] == ()


def test_multiline_declaration_headers_use_canonical_spans(python_definition):
    text = "def f(\r\n    x: int,\r\n):\r\n    # c\r\n    value=1\r\n"
    _, result = read_placement(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert result.declarations == (SourceDeclaration(SourceSpan(0, 23), 0, "function"),)
    assert result.insertions == (38,)
    assert scan_tokens(text, python_definition).text == text


@pytest.mark.parametrize(
    "text",
    [
        "x=1\n    y=2\n",
        "else: x=1\n",
        "if x\n",
        "x=1;; y=2\n",
    ],
)
def test_opaque_grammar_needs_no_diagnostics(python_definition, text):
    _, result = read_placement(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert scan_tokens(text, python_definition).text == text
    assert read_documentation(text, python_definition)[2] == ()


def test_placement_rejects_invalid_definition(python_definition):
    scan, lines = read_logical_lines("x=1\n", python_definition)
    assert not isinstance(lines, ReadFailure)
    structure = import_module("comment_review.reading.python.structure")
    result = structure.place_declarations(
        scan, lines, replace(python_definition, rules={})
    )
    assert isinstance(result, ReadFailure)
    assert result.diagnostics[0].stage == ReadStage.SELECT


@pytest.mark.parametrize(
    "text",
    [
        "match[0]: int\n",
        "match[0].attr[1]: list[int]; next=1\n",
        "match [0]:\n    case _: a()\n",
        "match x:\n    case _:\n        case[0]: int\n",
    ],
)
def test_opaque_soft_keyword_annotations_preserve_source(python_definition, text):
    _, result = read_placement(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert scan_tokens(text, python_definition).text == text
    assert read_documentation(text, python_definition)[2] == ()


@pytest.mark.parametrize("text", ["match x: a()\n", "match [0] + other: a()\n"])
def test_opaque_inline_match_preserves_source(python_definition, text):
    _, result = read_placement(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert scan_tokens(text, python_definition).text == text
    assert read_documentation(text, python_definition)[2] == ()


@pytest.mark.parametrize(
    ("text", "expected", "spellings"),
    [
        ("", [], []),
        ("  # c\r\n\t\n# last", [], []),
        ("x=1\n", [(0, 4, (0, 1, 2), 0)], [["x", "=", "1"]]),
        ("  x=1", [(0, 5, (0, 1, 2), 2)], [["x", "=", "1"]]),
        (
            "x=(\n 1, # c\n [2]\n)\ny=3",
            [(0, 19, (0, 1, 2, 4, 7, 8, 9, 11), 0), (19, 22, (13, 14, 15), 0)],
            [["x", "=", "(", "1,", "[", "2", "]", ")"], ["y", "=", "3"]],
        ),
        (
            "  x=1+\\\r\n  2\r\nz=3",
            [(0, 14, (0, 1, 2, 5), 2), (14, 17, (7, 8, 9), 0)],
            [["x", "=", "1+", "2"], ["z", "=", "3"]],
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
        ("x=(1\n", "unfinished-continuation", SourceSpan(2, 3)),
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
    if code in {"inconsistent-indentation", "ambiguous-indentation"}:
        assert not isinstance(result, ReadFailure)
        assert scan_tokens(text, python_definition).text == text
        assert read_documentation(text, python_definition)[2] == ()
    else:
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
                ("code", "x"),
                ("boundary", "="),
                ("interpolation_start", 'f"'),
                ("interpolation_literal", "#"),
                ("field_start", "{"),
                ("code", "a"),
                ("boundary", "["),
                ("string", '"x"'),
                ("boundary", "]"),
                ("conversion", "!r"),
                ("format_start", ":"),
                ("interpolation_literal", ">"),
                ("field_start", "{"),
                ("code", "w"),
                ("field_end", "}"),
                ("interpolation_literal", "."),
                ("field_start", "{"),
                ("code", "p"),
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
                ("code", "x"),
                ("comment", '# }" fake'),
                ("newline", "\r\n"),
                ("code", "+"),
                ("code", "2"),
                ("field_end", "}"),
                ("interpolation_end", '"'),
                ("boundary", ";"),
                ("code", "y"),
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


def test_fstrings_multiline_literal_and_expression_comment_boundaries(
    python_definition,
):
    text = (
        'message = f"""# This is literal output.\n'
        "Total: {\n"
        "    subtotal + tax  # This is a comment.\n"
        "}\n"
        "# This is also literal output.\n"
        '"""\n'
        "after()  # This is a final real comment.\n"
    )
    scan = scan_tokens(text, python_definition)
    assert not isinstance(scan, ReadFailure)
    source = SourceStructure(text, scan.regions, (), (), ())
    comments = [region for region in scan.regions if region.kind == RegionKind.COMMENT]
    assert [(region.span, source.slice(region.span)) for region in comments] == [
        (SourceSpan(69, 89), "# This is a comment."),
        (SourceSpan(136, 167), "# This is a final real comment."),
    ]
    assert [
        (
            source.position(region.span.start).line,
            source.position(region.span.start).column,
        )
        for region in comments
    ] == [(3, 20), (7, 9)]
    assert [
        (region.kind, source.slice(region.span))
        for region in scan.regions
        if region.kind == RegionKind.LITERAL
    ] == [
        (RegionKind.LITERAL, 'f"""# This is literal output.\nTotal: '),
        (RegionKind.LITERAL, '\n# This is also literal output.\n"""'),
    ]
    assert [
        (region.span, source.slice(region.span))
        for region in scan.regions
        if region.kind == RegionKind.CODE and 47 <= region.span.start < 91
    ] == [
        (SourceSpan(47, 48), "{"),
        (SourceSpan(53, 61), "subtotal"),
        (SourceSpan(62, 63), "+"),
        (SourceSpan(64, 67), "tax"),
        (SourceSpan(90, 91), "}"),
    ]
    assert [
        (token.kind, source.slice(token.span))
        for token in scan.tokens
        if token.kind in ("field_start", "field_end", "interpolation_end")
    ] == [("field_start", "{"), ("field_end", "}"), ("interpolation_end", '"""')]
    assert any(
        region.kind == RegionKind.CODE and source.slice(region.span) == "after()"
        for region in scan.regions
    )
    assert scan.protected == ()
    assert scan.text == text
    assert source.reconstruct() == text


@pytest.mark.parametrize("prefix", ["f", "t"])
@pytest.mark.parametrize("quote", ["'", '"'])
def test_interpolation_escaped_quote_keeps_hash_and_brace_inside_field_string(
    python_definition, prefix, quote
):
    spelling = quote + "escaped \\" + quote + "# } literal" + quote
    text = prefix + '"""{' + spelling + ' # real } """\n}# literal\n"""# after\n'
    scan = scan_tokens(text, python_definition)
    assert not isinstance(scan, ReadFailure)
    assert [
        text[token.span.start : token.span.end]
        for token in scan.tokens
        if token.kind == "string"
    ] == [spelling]
    assert [
        text[region.span.start : region.span.end]
        for region in scan.regions
        if region.kind == RegionKind.COMMENT
    ] == ['# real } """', "# after"]
    assert [token.span.start for token in scan.tokens if token.kind == "field_end"] == [
        text.index("\n}") + 1
    ]
    assert [
        (item.kind, text[item.span.start : item.span.end]) for item in scan.protected
    ] == (
        [("template-expression", spelling + ' # real } """\n')] if prefix == "t" else []
    )
    assert SourceStructure(text, scan.regions, (), (), ()).reconstruct() == text


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
        text[t.span.start : t.span.end] for t in scan.tokens if t.kind == "code"
    ] == fields


@pytest.mark.parametrize("flag", ["s", "r", "a"])
def test_fstrings_conversions(python_definition, flag):
    text = 'f"{x!' + flag + '}"'
    scan = scan_tokens(text, python_definition)
    assert not isinstance(scan, ReadFailure)
    assert [(t.kind, text[t.span.start : t.span.end]) for t in scan.tokens] == [
        ("interpolation_start", 'f"'),
        ("field_start", "{"),
        ("code", "x"),
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
        ("code", 6, 7),
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
        if t.kind in ("conversion", "format_start")
        or (t.kind == "code" and text[t.span.start : t.span.end] == "!=")
    ] == (
        [("code", "!=")]
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
        ("code", "x"),
        ("boundary", "="),
        ("interpolation_start", 't"'),
        ("interpolation_literal", "before "),
        ("field_start", "{"),
        ("code", "value"),
        ("conversion", "!s"),
        ("format_start", ":"),
        ("interpolation_literal", ">"),
        ("field_start", "{"),
        ("code", "width"),
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


def read_documentation(text, definition):
    scan, structure = read_placement(text, definition)
    assert not isinstance(structure, ReadFailure)
    try:
        documentation = import_module("comment_review.reading.python.documentation")
    except ModuleNotFoundError:
        pytest.fail("Python documentation ownership is not implemented", pytrace=False)
    return scan, structure, documentation.documentation_in(scan, structure, definition)


@pytest.mark.parametrize(
    ("text", "statement", "components", "owner"),
    [
        ('# leading\n\n"module"\n', '"module"', ['"module"'], None),
        ('class C:\n    # leading\n\n    "class"\n', '"class"', ['"class"'], 0),
        ('def f():\n    "function"\n', '"function"', ['"function"'], 0),
        ('async def f():\n    "async"\n', '"async"', ['"async"'], 0),
        ('class C: "inline"; pass\n', '"inline";', ['"inline"'], 0),
        ('def f(): "inline"; pass\n', '"inline";', ['"inline"'], 0),
        ('async def f(): "inline"; pass\n', '"inline";', ['"inline"'], 0),
        ('""\n', '""', ['""'], None),
        ('( ( "" ) ) ; pass\n', '( ( "" ) ) ;', ['""'], None),
        (
            '(\n    "a" # retained comment\n    R"b" U"c"\n)\n',
            '(\n    "a" # retained comment\n    R"b" U"c"\n)',
            ['"a"', 'R"b"', 'U"c"'],
            None,
        ),
        ('((r"a" u"b" "c"))\n', '((r"a" u"b" "c"))', ['r"a"', 'u"b"', '"c"'], None),
        ('"a" \\\n "b"\n', '"a" \\\n "b"', ['"a"', '"b"'], None),
        ('"doc"; "later"\n', '"doc";', ['"doc"'], None),
        ('"""multi\nline""";\n', '"""multi\nline""";', ['"""multi\nline"""'], None),
    ],
)
def test_doc_ownership_complete_statement_and_component_spans(
    python_definition, text, statement, components, owner
):
    scan, structure, result = read_documentation(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert len(result) == 1
    expression = result[0]
    assert expression.statement == SourceSpan(
        text.index(statement), text.index(statement) + len(statement)
    )
    assert expression.components == tuple(
        SourceSpan(text.index(component), text.index(component) + len(component))
        for component in components
    )
    assert expression.declaration == owner
    if owner is not None:
        assert structure.insertions[owner] == expression.statement.start
    assert "".join(text[r.span.start : r.span.end] for r in scan.regions) == text
    assert [
        text[t.span.start : t.span.end] for t in scan.tokens if t.kind == "comment"
    ] == [line[line.index("#") :] for line in text.splitlines() if "#" in line]


@pytest.mark.parametrize(
    "expression",
    [
        'value = "doc"',
        '("doc",)',
        '"doc", "other"',
        '+"doc"',
        '-"doc"',
        '"doc" + "other"',
        '"doc" * 2',
        '"doc"()',
        '("doc")("other")',
        '"doc" ("other")',
        '"doc"[0]',
        '"doc".upper',
        'b"doc"',
        'BR"doc"',
        'f"doc"',
        'f"{value}"',
        't"doc"',
        't"{value}"',
        '"plain" f"formatted"',
        '("plain" t"{value}")',
        '"plain" b"bytes"',
        'await "doc"',
    ],
)
@pytest.mark.parametrize("prefix", ["", "def f():\n    "])
def test_doc_ownership_excluded_shapes_remain_executable(
    python_definition, expression, prefix
):
    text = prefix + expression + "\n"
    scan, structure, result = read_documentation(text, python_definition)
    assert result == ()
    assert scan.text == text
    assert structure.insertions == ((len(prefix),) if prefix else ())
    assert any(region.kind == RegionKind.LITERAL for region in scan.regions)


@pytest.mark.parametrize(
    "text",
    [
        'pass\n"later"\n',
        'pass; "later"\n',
        'b"bytes"; "later"\n',
        'f"formatted"; "later"\n',
        't"template"; "later"\n',
        'def f(): pass; "later"\n',
        'def f():\n    pass\n    "later"\n',
        'if ready:\n    "control"\n"later"\n',
        'def f():\n    if ready:\n        "control"\n    "later"\n',
        'if ready: "control"\nelse: "clause"\n',
        'while ready: "control"\nelse: "clause"\n',
        'try: "control"\nexcept Error: "clause"\nfinally: "final"\n',
        'with context: "control"\n',
        'for item in items: "control"\n',
        'match value:\n    case _: "control"\n',
    ],
)
def test_doc_ownership_first_expression_is_local_to_documentation_owner(
    python_definition, text
):
    _, _, result = read_documentation(text, python_definition)
    assert result == ()


def test_doc_ownership_nested_declarations_under_controls(python_definition):
    text = (
        '"module"\n'
        "class Outer:\n"
        '    "outer"\n'
        "    if ready:\n"
        '        "control"\n'
        "        def method():\n"
        '            "method"\n'
        '            async def inner(): "inner"; pass\n'
        "    class Empty:\n"
        "        pass\n"
        '    def sibling(): "sibling"\n'
    )
    _, _, result = read_documentation(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert [
        (
            text[e.statement.start : e.statement.end],
            e.declaration,
            [text[c.start : c.end] for c in e.components],
        )
        for e in result
    ] == [
        ('"module"', None, ['"module"']),
        ('"outer"', 0, ['"outer"']),
        ('"method"', 1, ['"method"']),
        ('"inner";', 2, ['"inner"']),
        ('"sibling"', 4, ['"sibling"']),
    ]


def test_doc_ownership_semicolon_siblings_and_repeated_empty_components(
    python_definition,
):
    text = '"" ""; "later"; pass\n'
    _, structure, result = read_documentation(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert len(result) == 1
    assert result[0].statement == SourceSpan(0, 6)
    assert result[0].components == (SourceSpan(0, 2), SourceSpan(3, 5))
    assert result[0].declaration is None
    assert structure.insertions == ()
    assert scan_tokens(text, python_definition).text == text


def test_doc_ownership_uses_existing_declaration_indices(python_definition):
    text = 'def first(): "first"\ndef second(): "second"\n'
    scan, structure = read_placement(text, python_definition)
    documentation = import_module("comment_review.reading.python.documentation")
    result = documentation.documentation_in(scan, structure, python_definition)
    assert not isinstance(result, ReadFailure)
    assert [
        (text[e.statement.start : e.statement.end], e.declaration) for e in result
    ] == [('"first"', 0), ('"second"', 1)]
    assert [text[d.header.start : d.header.end] for d in structure.declarations] == [
        "def first():",
        "def second():",
    ]


@pytest.mark.parametrize("text", ["", "# comment\n\n", "class Empty:\n"])
def test_doc_ownership_empty_declarations(python_definition, text):
    _, _, result = read_documentation(text, python_definition)
    assert result == ()


def test_doc_ownership_rejects_invalid_definition(python_definition):
    scan, structure = read_placement('"doc"\n', python_definition)
    assert not isinstance(structure, ReadFailure)
    definition = replace(python_definition, revision="unsupported")
    documentation = import_module("comment_review.reading.python.documentation")
    result = documentation.documentation_in(scan, structure, definition)
    assert isinstance(result, ReadFailure)
    assert result.diagnostics[0].stage == ReadStage.SELECT
    assert result.diagnostics[0].code == "invalid-language-definition"


def read_payload(text, definition):
    scan, _, expressions = read_documentation(text, definition)
    assert not isinstance(expressions, ReadFailure)
    assert len(expressions) == 1
    documentation = import_module("comment_review.reading.python.documentation")
    decoder = getattr(documentation, "decode_documentation", None)
    assert callable(decoder), "Python documentation payload decoding is not implemented"
    return scan, expressions[0], decoder(scan, expressions[0], definition)


@pytest.mark.parametrize(
    "literal",
    [
        '"hello"',
        "u'caf\u00e9'",
        'U"\u03bb\U0001f40d"',
        '""',
        "r'''\\n\\x41'''",
        'R"\\u03bb\\N{NOT A NAME}"',
        r'''"\"\'\\"''',
        r'"\a\b\f\n\r\t\v"',
        r'"\0\07\101\7777"',
        r'"\08"',
        r'"\x41\xFf"',
        r'"\u03bb\U0001F40D"',
        r'"\uD800\U0010FFFF"',
        r'"\N{LATIN CAPITAL LETTER A}\N{LF}"',
        r'"before\qafter\8\z"',
        'r"quote\\" slash\\\\"',
    ],
)
def test_payloads_admit_valid_escapes_and_record_the_raw_expression(
    python_definition, literal
):
    scan, expression, payload = read_payload(literal + "\n", python_definition)
    assert not isinstance(payload, ReadFailure)
    assert payload.expression is expression
    assert expression.components == (SourceSpan(0, len(literal)),)
    assert scan.text[expression.statement.start : expression.statement.end] == literal
    assert scan.text == literal + "\n"


@pytest.mark.parametrize(
    "literal",
    [
        '"""a\nb"""',
        '"""a\r\nb"""',
        '"""a\rb"""',
        'r"""a\r\nb"""',
        'r"""a\rb"""',
        '"a\\\nb"',
        '"a\\\r\nb"',
        '"a\\\rb"',
        '"\\\n"',
        'r"a\\\nb"',
        'r"a\\\r\nb"',
        'r"a\\\rb"',
    ],
)
def test_payloads_admit_physical_newlines_and_preserve_source(
    python_definition, literal
):
    scan, expression, payload = read_payload(literal + "\n", python_definition)
    assert not isinstance(payload, ReadFailure)
    assert scan.text[expression.statement.start : expression.statement.end] == literal
    assert (
        "".join(scan.text[r.span.start : r.span.end] for r in scan.regions) == scan.text
    )


def test_payloads_complete_adjacent_prose_excludes_layout_and_following_source(
    python_definition,
):
    text = (
        '(\n "one " # separator\n R"\\n" u\' two\' ""\n)'
        '; later = "ignored" # following\n'
    )
    _, expression, payload = read_payload(text, python_definition)
    assert not isinstance(payload, ReadFailure)
    assert expression.components == (
        SourceSpan(3, 9),
        SourceSpan(23, 28),
        SourceSpan(29, 36),
        SourceSpan(37, 39),
    )
    assert expression.statement == SourceSpan(0, 42)


def test_payloads_empty_components_do_not_invent_prose(python_definition):
    _, expression, payload = read_payload('"" r"" U"" "a" ""\n', python_definition)
    assert not isinstance(payload, ReadFailure)
    assert len(expression.components) == 5


@pytest.mark.parametrize(
    ("literal", "code", "span"),
    [
        (r'"\x"', "invalid-documentation-escape", SourceSpan(1, 3)),
        (r'"\x1"', "invalid-documentation-escape", SourceSpan(1, 4)),
        (r'"\xG1"', "invalid-documentation-escape", SourceSpan(1, 5)),
        (r'"\u123"', "invalid-documentation-escape", SourceSpan(1, 6)),
        (r'"\u12z4"', "invalid-documentation-escape", SourceSpan(1, 7)),
        (r'"\U0001f40"', "invalid-documentation-escape", SourceSpan(1, 10)),
        (r'"\U00110000"', "invalid-documentation-escape", SourceSpan(1, 11)),
        (r'"\N"', "invalid-documentation-escape", SourceSpan(1, 3)),
        (r'"\Nx"', "invalid-documentation-escape", SourceSpan(1, 3)),
        (r'"\N{LF"', "invalid-documentation-escape", SourceSpan(1, 6)),
        (r'"\N{}"', "invalid-documentation-escape", SourceSpan(1, 5)),
        (r'"\N{NOT A UNICODE CHARACTER}"', "unknown-unicode-name", SourceSpan(1, 28)),
        (r'"\N{KEYCAP DIGIT ONE}"', "unknown-unicode-name", SourceSpan(1, 21)),
    ],
)
def test_payloads_required_escapes_and_unavailable_names_fail_at_raw_escape(
    python_definition, literal, code, span
):
    _, _, result = read_payload(literal + "\n", python_definition)
    assert isinstance(result, ReadFailure)
    assert result.diagnostics[0].stage == ReadStage.PLACE
    assert result.diagnostics[0].code == code
    assert result.diagnostics[0].span == span


def test_payloads_reject_invalid_definition(python_definition):
    scan, expression, _ = read_payload('"doc"\n', python_definition)
    definition = replace(python_definition, revision="unsupported")
    documentation = import_module("comment_review.reading.python.documentation")
    result = documentation.decode_documentation(scan, expression, definition)
    assert isinstance(result, ReadFailure)
    assert result.diagnostics[0].stage == ReadStage.SELECT
    assert result.diagnostics[0].code == "invalid-language-definition"


def read_directives(text, definition):
    scan, structure = read_placement(text, definition)
    assert not isinstance(structure, ReadFailure)
    try:
        directives = import_module("comment_review.reading.python.directives")
    except ModuleNotFoundError:
        pytest.fail("Python directive recognition is not implemented", pytrace=False)
    return scan, structure, directives.directives_in(scan, structure, definition)


def section_inputs(text, definition):
    scan, structure, expressions = read_documentation(text, definition)
    assert not isinstance(expressions, ReadFailure)
    documentation = import_module("comment_review.reading.python.documentation")
    payloads = tuple(
        documentation.decode_documentation(scan, expression, definition)
        for expression in expressions
    )
    assert all(not isinstance(payload, ReadFailure) for payload in payloads)
    directives = import_module("comment_review.reading.python.directives")
    protected = directives.directives_in(scan, structure, definition)
    assert not isinstance(protected, ReadFailure)
    return scan, structure, payloads, protected


def project_sections(text, definition):
    scan, structure, payloads, protected = section_inputs(text, definition)
    try:
        projection = import_module("comment_review.reading.python.projection")
    except ModuleNotFoundError:
        pytest.fail("Python whole-source sections are not implemented", pytrace=False)
    result = projection.sections_for(scan, structure, payloads, definition, protected)
    return scan, structure, payloads, protected, result


@pytest.mark.parametrize(
    "text, spans, raw",
    [
        ("", (), []),
        (" \r\n", (), []),
        ("# a\n\n# b\nx=1\n", ((0, 9),), ["# a\n\n# b\n"]),
        ("x=1\n# a\n\n# b\nx=2\n", ((4, 13),), ["# a\n\n# b\n"]),
        ("x=1\n# a\n\n# b\n", ((4, 13),), ["# a\n\n# b\n"]),
        (
            "x=1 # a\n\n# b\nx=2\n",
            ((4, 8), (9, 13)),
            ["# a\n", "# b\n"],
        ),
        ("# a\r\n \t\r# b\nx=1\r", ((0, 12),), ["# a\r\n \t\r# b\n"]),
        ("x=1\n  # a\n\n", ((4, 10),), ["  # a\n"]),
        ("# a", ((0, 3),), ["# a"]),
    ],
)
def test_sections_whole_same_form_runs_preserve_exact_extent(
    python_definition, text, spans, raw
):
    scan, structure, payloads, protected, result = project_sections(
        text, python_definition
    )
    assert not isinstance(result, ReadFailure)
    assert result.source.sections == tuple(
        SourceSection(SourceSpan(start, end), "#") for start, end in spans
    )
    assert [
        result.source.slice(section.span) for section in result.source.sections
    ] == raw
    assert result.source.reconstruct() == text
    assert result.source.text is scan.text
    assert result.source.regions is scan.regions
    assert result.source.declarations is structure.declarations
    assert result.payloads is payloads
    assert result.protected == scan.protected + protected
    assert result.source.documentation == ()


def test_sections_documentation_owns_complete_concatenated_statement(python_definition):
    text = '# head\n("a\\n" r"b"); x=1 # tail\n'
    _, _, payloads, _, result = project_sections(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert result.source.sections == (
        SourceSection(SourceSpan(0, 7), "#"),
        SourceSection(SourceSpan(7, 20), "docstring"),
        SourceSection(SourceSpan(25, 32), "#"),
    )
    assert [
        result.source.slice(section.span) for section in result.source.sections
    ] == [
        "# head\n",
        '("a\\n" r"b");',
        "# tail\n",
    ]
    assert result.source.documentation == (DocumentationOwner(1, None),)
    assert literal_value(result.source.text, payloads[0]) == "a\nb"
    assert payloads[0].expression.components == (SourceSpan(8, 13), SourceSpan(14, 18))
    assert result.source.slice(SourceSpan(20, 25)) == " x=1 "
    assert result.source.reconstruct() == text


@pytest.mark.parametrize("ending", ["\n", "\r\n"])
@pytest.mark.parametrize(
    "text, raw, place, code",
    [
        (
            'x=f"{value # note\n}"; after()\n',
            "# note\n",
            "c0",
            {1: 'x=f"{value ', 2: '}"; after()'},
        ),
        (
            'x=f"""{\n    # note\n    value\n}"""; after()\n',
            "    # note\n",
            "b1",
            {1: 'x=f"""{', 3: "    value", 4: '}"""; after()'},
        ),
        (
            'x=f"""{value # first\n\n    # second\n}"""; after()\n',
            ("# first\n", "    # second\n"),
            ("c0", "b1"),
            {1: 'x=f"""{value ', 4: '}"""; after()'},
        ),
        (
            'x=f"""{\n    # first\n\n    # second\n    value\n}"""; after()\n',
            "    # first\n\n    # second\n",
            "b1",
            {1: 'x=f"""{', 5: "    value", 6: '}"""; after()'},
        ),
        (
            'x=f"""{f\'{\n    # note\n    value\n}\'}"""; after()\n',
            "    # note\n",
            "b1",
            {1: 'x=f"""{f\'{', 3: "    value", 4: '}\'}"""; after()'},
        ),
        (
            'x=f"{before}{value # note\n}{after}"; work()\n',
            "# note\n",
            "c0",
            {1: 'x=f"{before}{value ', 2: '}{after}"; work()'},
        ),
        (
            'x=f"{value:{width # note\n}}"; work()\n',
            "# note\n",
            "c0",
            {1: 'x=f"{value:{width ', 2: '}}"; work()'},
        ),
        (
            'x=f"{value # note } f\' x\n}"; after()\n',
            "# note } f' x\n",
            "c0",
            {1: 'x=f"{value ', 2: '}"; after()'},
        ),
    ],
)
def test_expression_comments_existing_places_preserve_expression_on_set_and_edit(
    python_definition, ending, text, raw, place, code
):
    from conftest import build

    from comment_review.binder.page import Page, attach, code_lines, tie_leading
    from comment_review.reading.addresser import address_for, cue
    from comment_review.reading.paragraph import Paragraph
    from comment_review.results.compositor import set_page

    text = text.replace("\n", ending)
    raws = tuple(
        part.replace("\n", ending) for part in ((raw,) if isinstance(raw, str) else raw)
    )
    places = (place,) if isinstance(place, str) else place
    scan, _, _, _, result = project_sections(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert result.source.sections == tuple(
        SourceSection(SourceSpan(text.index(raw), text.index(raw) + len(raw)), "#")
        for raw in raws
    )
    assert [
        text[token.span.start : token.span.end]
        for token in scan.tokens
        if token.kind == "comment"
    ] == [line.lstrip() for raw in raws for line in raw.splitlines() if line.strip()]
    paragraphs = []
    for section, raw in zip(result.source.sections, raws, strict=True):
        position = result.source.position(section.span.start)
        first_line = position.line
        last_line = result.source.position(section.span.end - 1).line
        prefix = text[section.span.start - position.column : section.span.start]
        paragraphs.append(
            Paragraph(
                path="m.py",
                start=first_line,
                end=last_line,
                kind="trailing-comment" if prefix.strip() else "comment",
                text=raw,
                anchor=prefix,
                raw_lines=result.source.slice(section.span).splitlines(),
            )
        )
    anchors = code_lines(text, [vars(paragraph) for paragraph in paragraphs])
    assert anchors == code
    cues = cue([CodeLine(n, code, None) for n, code in anchors.items()], a_series=False)
    for paragraph, place in zip(paragraphs, places, strict=True):
        assert attach(vars(paragraph), cues) == place
        assert paragraph.original_start is not None
        assert paragraph.original_end is not None
        assert cues.anchor_line(place) == (
            paragraph.original_start
            if place.startswith("c")
            else paragraph.original_end + 1
        )
        paragraph.address = address_for("m.py", place)
    leading = [p for p in build(text) if p.kind == "leading"]
    laid_out = sorted([*paragraphs, *leading], key=lambda p: p.start)
    page = Page(
        "m.py",
        text,
        "held",
        laid_out,
        cues,
        build("").reading,
        build(text).read,
        leading=tie_leading(laid_out, cues),
    )
    assert set_page(page) == text
    original_anchors = dict(cues.places)
    for paragraph, place, raw in zip(paragraphs, places, raws, strict=True):
        start = text.index(raw)
        end = start + len(raw)
        replacement = raw.replace("# note", "# edited").replace("# first", "# edited")
        replacement += "    # added" + ending
        paragraph.raw_lines = replacement.splitlines()
        assert set_page(page) == text[:start] + replacement + text[end:]
        paragraph.raw_lines = []
        assert (
            set_page(page)
            == text[:start] + (ending if place.startswith("c") else "") + text[end:]
        )
        assert cues.places == original_anchors
        paragraph.raw_lines = raw.splitlines()


@pytest.mark.parametrize(
    "text, kind",
    [
        ('x=t"{ value # observable\n }"; after()\n', "template-expression"),
        ('x=f"{ value # observable\n = }"; after()\n', "debug-expression"),
        ("x=t\"{f'{value # observable\n}'}\"; after()\n", "template-expression"),
        ("x=f\"{f'{value # observable\n}'=}\"; after()\n", "debug-expression"),
    ],
)
def test_expression_comments_protected_outer_spans_keep_nested_recognition(
    python_definition, text, kind
):
    scan, _, _, _, result = project_sections(text, python_definition)
    assert not isinstance(result, ReadFailure)
    comment = next(
        region for region in result.source.regions if region.kind == RegionKind.COMMENT
    )
    assert text[comment.span.start : comment.span.end] == "# observable"
    assert any(
        protected.kind == kind
        and protected.span.start <= comment.span.start
        and comment.span.end <= protected.span.end
        for protected in result.protected
    )
    assert any(
        region.kind == RegionKind.COMMENT and region.span == comment.span
        for region in result.source.regions
    )
    assert result.source.sections == (
        SourceSection(SourceSpan(comment.span.start, comment.span.end + 1), "#"),
    )
    assert result.source.reconstruct() == text


def test_sections_documentation_retains_same_line_header_and_following_code(
    python_definition,
):
    text = 'def f(): "doc"; pass # tail\n'
    _, structure, _, _, result = project_sections(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert result.source.sections == (
        SourceSection(SourceSpan(9, 15), "docstring"),
        SourceSection(SourceSpan(21, 28), "#"),
    )
    assert result.source.documentation == (DocumentationOwner(0, 0),)
    assert literal_value(result.source.text, result.payloads[0]) == "doc"
    assert result.source.slice(SourceSpan(0, 9)) == "def f(): "
    assert result.source.slice(SourceSpan(15, 21)) == " pass "
    assert result.source.declarations == structure.declarations
    assert result.source.reconstruct() == text


def test_sections_directive_comments_retain_same_form_run_and_protection(
    python_definition,
):
    text = "# a\n# type: ignore\n# b\n"
    _, _, _, protected, result = project_sections(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert result.source.sections == (SourceSection(SourceSpan(0, len(text)), "#"),)
    assert result.protected == protected
    assert [
        (region.span, region.kind)
        for region in result.source.regions
        if region.kind == RegionKind.COMMENT
    ] == [
        (SourceSpan(0, 3), RegionKind.COMMENT),
        (SourceSpan(4, 18), RegionKind.COMMENT),
        (SourceSpan(19, 22), RegionKind.COMMENT),
    ]
    assert result.protected[0].span == SourceSpan(4, 18)
    assert result.source.reconstruct() == text


def test_sections_interior_documentation_comment_belongs_to_whole_owner(
    python_definition,
):
    text = '("a" # note\n "b")\n'
    scan, _, payloads, _, result = project_sections(text, python_definition)
    assert literal_value(result.source.text, payloads[0]) == "ab"
    assert payloads[0].expression.statement == SourceSpan(0, 17)
    assert not isinstance(result, ReadFailure)
    assert result.source.sections == (SourceSection(SourceSpan(0, 17), "docstring"),)
    assert result.source.documentation == (DocumentationOwner(0, None),)
    assert result.source.reconstruct() == text
    assert scan.text == text


def test_sections_reject_invalid_definition_before_projection(python_definition):
    scan, structure, payloads, protected = section_inputs("# a\n", python_definition)
    try:
        projection = import_module("comment_review.reading.python.projection")
    except ModuleNotFoundError:
        pytest.fail("Python whole-source sections are not implemented", pytrace=False)
    result = projection.sections_for(
        scan, structure, payloads, replace(python_definition, revision="bad"), protected
    )
    assert isinstance(result, ReadFailure)
    assert result.diagnostics[0].stage == ReadStage.SELECT
    assert result.diagnostics[0].code == "invalid-language-definition"


def test_sections_multiple_documentation_owners_keep_source_order(python_definition):
    text = '"m"\n# a\nclass C:\n    "c"\n    def f(): "f"\n'
    _, _, _, _, result = project_sections(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert result.source.sections == (
        SourceSection(SourceSpan(0, 3), "docstring"),
        SourceSection(SourceSpan(4, 8), "#"),
        SourceSection(SourceSpan(21, 24), "docstring"),
        SourceSection(SourceSpan(38, 41), "docstring"),
    )
    assert result.source.documentation == (
        DocumentationOwner(0, None),
        DocumentationOwner(2, 0),
        DocumentationOwner(3, 1),
    )
    assert [
        literal_value(result.source.text, payload) for payload in result.payloads
    ] == ["m", "c", "f"]
    assert result.source.reconstruct() == text


@pytest.mark.parametrize(
    "text",
    [
        "#!/usr/bin/python\n# coding: utf-8\n# type: ignore\n",
        'x=t"{ value # observable\n }"\n',
        'x=f"{ value # observable\n = }"\n',
    ],
)
def test_sections_protected_comments_remain_regions_and_classified_sections(
    python_definition, text
):
    scan, _, _, directives, result = project_sections(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert result.source.documentation == result.payloads == ()
    assert len(result.source.sections) == 1
    assert result.source.sections[0].form == "#"
    assert result.protected == scan.protected + directives
    assert result.protected
    assert [
        result.source.slice(region.span)
        for region in result.source.regions
        if region.kind in (RegionKind.COMMENT, RegionKind.DIRECTIVE)
    ] == (
        ["#!/usr/bin/python", "# coding: utf-8", "# type: ignore"]
        if text.startswith("#!")
        else ["# observable"]
    )
    assert result.source.reconstruct() == text


def test_sections_protected_interior_documentation_comment_keeps_whole_owner(
    python_definition,
):
    text = '("a" # type: ignore\n "b")\n'
    _, _, _, directives, result = project_sections(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert result.source.sections == (SourceSection(SourceSpan(0, 25), "docstring"),)
    assert result.source.documentation == (DocumentationOwner(0, None),)
    assert literal_value(result.source.text, result.payloads[0]) == "ab"
    assert result.protected == directives
    assert result.source.reconstruct() == text


def test_sections_only_compose_completed_stages(python_definition, monkeypatch):
    scan, structure, payloads, directives = section_inputs(
        '"doc"\n# a\nx=1\n', python_definition
    )

    def forbidden(*args):
        pytest.fail("Section projection must consume retained records")

    for module, functions in (
        ("scanner", ("scan_python",)),
        ("structure", ("logical_lines", "place_declarations")),
        ("documentation", ("documentation_in", "decode_documentation")),
        ("directives", ("directives_in",)),
    ):
        stage = import_module("comment_review.reading.python." + module)
        for function in functions:
            monkeypatch.setattr(stage, function, forbidden)
    projection = import_module("comment_review.reading.python.projection")
    result = projection.sections_for(
        scan, structure, payloads, python_definition, directives
    )
    assert not isinstance(result, ReadFailure)
    assert result.source.sections == (
        SourceSection(SourceSpan(0, 5), "docstring"),
        SourceSection(SourceSpan(6, 10), "#"),
    )
    assert result.source.reconstruct() == '"doc"\n# a\nx=1\n'


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("#!/usr/bin/python\nx=1\n", [("shebang", "#!/usr/bin/python", "")]),
        (" #!/usr/bin/python\nx=1\n", []),
        ("\n#!/usr/bin/python\nx=1\n", []),
        ("# coding: utf-8\nx=1\n", [("encoding", "# coding: utf-8", "")]),
        ("# coding=utf8\nx=1\n", [("encoding", "# coding=utf8", "")]),
        (
            "# -*- coding: UTF_8 -*- prose\nx=1\n",
            [("encoding", "# -*- coding: UTF_8 -*- prose", "")],
        ),
        ("# comment\n# coding: utf-8\nx=1\n", [("encoding", "# coding: utf-8", "")]),
        (" \t\f\r\n# coding: utf-8\nx=1\n", [("encoding", "# coding: utf-8", "")]),
        (
            "#!/usr/bin/python\r\n# coding: utf-8\r\nx=1\r\n",
            [("shebang", "#!/usr/bin/python", ""), ("encoding", "# coding: utf-8", "")],
        ),
        ("x=1\n# coding: latin-1\n", []),
        ("x=1 # coding: latin-1\n", []),
        ("\n\n# coding: latin-1\n", []),
        ("# coding: utf-8\n# coding: latin-1\n", [("encoding", "# coding: utf-8", "")]),
        ('"# coding: latin-1"\n# coding: latin-1\n', []),
        ('text = "#! # type: ignore # coding: latin-1"\n', []),
        ("# Coding: latin-1\nx=1\n", []),
        ("# coding : latin-1\nx=1\n", []),
        ("# coding: \nx=1\n", []),
    ],
)
def test_directives_effective_preamble_and_literal_lookalikes(
    python_definition, text, expected
):
    scan, _, result = read_directives(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert [
        (
            item.kind,
            text[item.span.start : item.span.end],
            text[item.attachment.start : item.attachment.end],
        )
        for item in result
    ] == expected
    assert all(item.attachment == SourceSpan(0, 0) for item in result)
    assert scan.text == text


@pytest.mark.parametrize(
    "encoding", ["latin-1", "ascii", "utf-8sig", "utf-8.anything", "unknown-codec"]
)
def test_directives_incompatible_encoding_refuses_at_effective_cookie(
    python_definition, encoding
):
    cookie = "# coding: " + encoding
    text = "# header\n" + cookie + "\nvalue = 1\n"
    _, _, result = read_directives(text, python_definition)
    assert isinstance(result, ReadFailure)
    diagnostic = result.diagnostics[0]
    assert diagnostic.stage == ReadStage.PLACE
    assert diagnostic.code == "unsupported-source-encoding"
    assert diagnostic.span == SourceSpan(9, 9 + len(cookie))


@pytest.mark.parametrize(
    "encoding",
    ["utf-8-sig", "UTF_8_SIG", "utf-8-anything", "uTf_8_AnYtHiNg", "utf-8-"],
)
def test_directives_source_cookie_normalization_preserves_utf8_bytes(
    python_definition, encoding
):
    from comment_review.machine.repo import source_from_bytes

    cookie = "# coding: " + encoding
    raw = cookie.encode("ascii") + b"\r\nvalue = 'caf\xc3\xa9'\r\n"
    source = source_from_bytes(raw)
    scan, _, result = read_directives(source.text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert len(result) == 1
    assert result[0].kind == "encoding"
    assert result[0].span == SourceSpan(0, len(cookie))
    assert source.text[result[0].span.start : result[0].span.end] == cookie
    assert result[0].attachment == SourceSpan(0, 0)
    assert scan.text.encode("utf-8") == raw


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("x=1 # type: int prose\n", [("type-comment", "# type: int prose", "x=1")]),
        ("x=1 #\t type:\tint\n", [("type-comment", "#\t type:\tint", "x=1")]),
        (
            "x=1 # type:ignore[attr-defined] prose\n",
            [("type-ignore", "# type:ignore[attr-defined] prose", "x=1")],
        ),
        ("x=1 # type: ignore-me\n", [("type-ignore", "# type: ignore-me", "x=1")]),
        ("x=1 # type: ignores\n", [("type-comment", "# type: ignores", "x=1")]),
        ("x=1 # type: Ignore\n", [("type-comment", "# type: Ignore", "x=1")]),
        ("x=1; y=2 # type: int\n", [("type-comment", "# type: int", "y=2")]),
        ("x=1; y=2 # type: ignore\n", [("type-ignore", "# type: ignore", "x=1; y=2")]),
        (
            "x=(\n  1, # type: ignore\n  2,\n)\n",
            [("type-ignore", "# type: ignore", "1,")],
        ),
        (
            "x=(\n  1,\n  2,\n) # type: tuple\n",
            [("type-comment", "# type: tuple", "x=(\n  1,\n  2,\n)")],
        ),
        (
            "def f(x):\n    # type: (int) -> int\n    # explanation\n    return x\n",
            [("type-comment", "# type: (int) -> int", "def f(x):")],
        ),
        (
            "# type: ignore\n# explanation\nx=1\n",
            [("type-ignore", "# type: ignore", "")],
        ),
        ("x=1\n# type: ignore\n", [("type-ignore", "# type: ignore", "")]),
        ("# type: int\n", [("type-comment", "# type: int", "")]),
        ("x=1 # prose type: int\n", []),
        ("x=1 # Type: int\n", []),
        ("x=1 # type : int\n", []),
        ("x=1 ## type: int\n", []),
        ("x=1 # noqa\n", []),
    ],
)
def test_directives_complete_type_comments_and_effective_targets(
    python_definition, text, expected
):
    _, _, result = read_directives(text, python_definition)
    assert not isinstance(result, ReadFailure)
    assert [
        (
            item.kind,
            text[item.span.start : item.span.end],
            text[item.attachment.start : item.attachment.end],
        )
        for item in result
    ] == expected


def test_directives_standalone_boundary_uses_following_source_or_eof(python_definition):
    for text, boundary in [
        ("# type: ignore\nx=1\n", 15),
        ("x=1\n# type: ignore\n", 19),
    ]:
        _, _, result = read_directives(text, python_definition)
        assert not isinstance(result, ReadFailure)
        assert result[0].attachment == SourceSpan(boundary, boundary)


def test_directives_prose_insertion_preserves_ownership_and_movement_changes_it(
    python_definition,
):
    targets = []
    for text in [
        "x=1 # type: int\ny=2\n",
        "# explanation\nx=1 # type: int\ny=2\n",
        "x=1\ny=2 # type: int\n",
    ]:
        _, structure, result = read_directives(text, python_definition)
        assert not isinstance(result, ReadFailure)
        attachment = result[0].attachment
        assert any(
            line.span.start <= attachment.start < attachment.end <= line.span.end
            for line in structure.lines
        )
        targets.append(text[attachment.start : attachment.end])
    assert targets == ["x=1", "x=1", "y=2"]


def test_directives_line_layout_changes_ignore_attachment_without_comment_change(
    python_definition,
):
    targets = []
    for text in ["x=1; y=2 # type: ignore\n", "x=1\ny=2 # type: ignore\n"]:
        _, _, result = read_directives(text, python_definition)
        assert not isinstance(result, ReadFailure)
        assert text[result[0].span.start : result[0].span.end] == "# type: ignore"
        attachment = result[0].attachment
        targets.append(text[attachment.start : attachment.end])
    assert targets == ["x=1; y=2", "y=2"]


def test_directives_preamble_insertion_detects_loss_of_effectiveness(python_definition):
    _, _, before = read_directives(
        "#!/usr/bin/python\n# coding: utf-8\nx=1\n", python_definition
    )
    _, _, after = read_directives(
        '"documentation"\n#!/usr/bin/python\n# coding: utf-8\nx=1\n', python_definition
    )
    assert not isinstance(before, ReadFailure)
    assert [item.kind for item in before] == ["shebang", "encoding"]
    assert after == ()


def test_directives_reject_invalid_definition(python_definition):
    scan, structure = read_placement("x=1 # type: int\n", python_definition)
    directives = import_module("comment_review.reading.python.directives")
    result = directives.directives_in(
        scan, structure, replace(python_definition, rules={})
    )
    assert isinstance(result, ReadFailure)
    assert result.diagnostics[0].stage == ReadStage.SELECT


@pytest.mark.parametrize(
    ("text", "kind", "target"),
    [
        ('x="""one\ntwo""" # type: str\n', "type-comment", 'x="""one\ntwo"""'),
        ('x="""one\ntwo""" # type: ignore\n', "type-ignore", 'two"""'),
        ("x=1 # type: ignore_why\n", "type-ignore", "x=1"),
        ("x=1 # type: ignore\u00e9\n", "type-comment", "x=1"),
        ("x=1 # type: ignore\u200b\n", "type-comment", "x=1"),
        ("x=1 #\f type: int\n", None, None),
    ],
)
def test_directives_multiline_token_attachment_and_ignore_suffix(
    python_definition, text, kind, target
):
    _, _, result = read_directives(text, python_definition)
    assert not isinstance(result, ReadFailure)
    if kind is None:
        assert result == ()
    else:
        assert len(result) == 1
        assert result[0].kind == kind
        attachment = result[0].attachment
        assert text[attachment.start : attachment.end] == target


def test_directives_standalone_prose_insertion_keeps_function_and_boundary_targets(
    python_definition,
):
    for extra in ["", "    # explanation\n"]:
        text = "def f():\n    # type: () -> int\n" + extra + "    return 1\n"
        _, _, result = read_directives(text, python_definition)
        assert not isinstance(result, ReadFailure)
        attachment = result[0].attachment
        assert text[attachment.start : attachment.end] == "def f():"
    for extra in ["", "# explanation\n"]:
        text = "# type: ignore\n" + extra + "x=1\n"
        _, _, result = read_directives(text, python_definition)
        assert not isinstance(result, ReadFailure)
        assert result[0].attachment == SourceSpan(text.index("x=1"), text.index("x=1"))


def test_directives_move_within_joined_statement_changes_ignore_target(
    python_definition,
):
    targets = []
    for text in [
        "x=(\n  1, # type: ignore\n  2,\n)\n",
        "x=(\n  1,\n  2, # type: ignore\n)\n",
    ]:
        _, _, result = read_directives(text, python_definition)
        assert not isinstance(result, ReadFailure)
        attachment = result[0].attachment
        targets.append(text[attachment.start : attachment.end])
    assert targets == ["1,", "2,"]


@pytest.mark.parametrize(
    "header",
    [
        "if~ready:",
        "except*ValueError:",
        "case-1:",
        "for*x, in [[1]]:",
        "if lambda*x: 0:",
        "unknown 00clause:",
        "elif missing context:",
        "else nonsense:",
        "try anything:",
    ],
)
def test_opaque_control_code_keeps_comment_and_nested_doc_positions(
    python_definition, header
):
    text = (
        header + "\n    # before declaration\n"
        '    async def 00name[T = 00value]():\n        (r"full " "documentation")\n'
    )
    result = import_module("comment_review.reading.python").read_python(
        text, python_definition
    )
    assert not isinstance(result, ReadFailure)
    assert result.source.reconstruct() == text
    assert [
        literal_value(result.source.text, payload) for payload in result.payloads
    ] == ["full documentation"]
    assert result.source.declarations[0].kind == "async-function"


def test_generic_indentation_cannot_claim_module_documentation(python_definition):
    text = (
        'arbitrary 00code\n    "not module docs"\n    def odd-name(): "actual docs"\n'
    )
    result = import_module("comment_review.reading.python").read_python(
        text, python_definition
    )
    assert not isinstance(result, ReadFailure)
    assert [
        literal_value(result.source.text, payload) for payload in result.payloads
    ] == ["actual docs"]
    assert [owner.declaration for owner in result.source.documentation] == [0]


@pytest.mark.parametrize("ending", ["\n", "\r\n", "\r"])
def test_classification_exact_physical_code_and_comment_positions(
    python_definition, ending
):
    from pathlib import Path

    from comment_review.reading.python.projection import (
        code_lines_for,
        paragraphs_for,
    )
    from comment_review.reading.series import Kind

    text = ending.join(
        [
            "CONSTANT = 10 # constant",
            "def my_funct(x: int, y: tuple): # tail comment",
            "    call()",
            "    # whole-line comment",
            "    call_again()",
            "",
        ]
    )
    result = import_module("comment_review.reading.python").read_python(
        text, python_definition
    )
    assert not isinstance(result, ReadFailure)
    comments = [
        region.span
        for region in result.source.regions
        if region.kind == RegionKind.COMMENT
    ]
    assert [
        (
            result.source.position(span.start).line,
            result.source.position(span.start).column,
            result.source.slice(span),
        )
        for span in comments
    ] == [
        (1, 14, "# constant"),
        (2, 32, "# tail comment"),
        (4, 4, "# whole-line comment"),
    ]
    assert code_lines_for(result) == [
        CodeLine(1, "CONSTANT = 10", None),
        CodeLine(2, "def my_funct(x: int, y: tuple):", DocPlace(2, False)),
        CodeLine(3, "    call()", None),
        CodeLine(5, "    call_again()", None),
    ]
    assert [
        (
            result.source.position(region.span.start).line,
            result.source.position(region.span.start).column,
            result.source.position(region.span.end).column,
            result.source.slice(region.span),
        )
        for region in result.source.regions
        if region.kind == RegionKind.CODE
    ] == [
        (1, 0, 8, "CONSTANT"),
        (1, 9, 10, "="),
        (1, 11, 13, "10"),
        (2, 0, 3, "def"),
        (2, 4, 15, "my_funct(x:"),
        (2, 16, 20, "int,"),
        (2, 21, 23, "y:"),
        (2, 24, 31, "tuple):"),
        (3, 4, 10, "call()"),
        (5, 4, 16, "call_again()"),
    ]
    paragraphs = paragraphs_for(Path("m.py"), result)
    assert not isinstance(paragraphs, ReadFailure)
    assert [(p.start, p.end, p.kind, p.raw_lines, p.anchor) for p in paragraphs] == [
        (1, 1, Kind.TRAILING, [" # constant"], "CONSTANT = 10"),
        (
            2,
            2,
            Kind.TRAILING,
            [" # tail comment"],
            "def my_funct(x: int, y: tuple):",
        ),
        (4, 4, Kind.COMMENT, ["    # whole-line comment"], ""),
    ]
    assert result.source.reconstruct() == text


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (
            "def f(\n    a,\n) -> int:\n    return a\n",
            [(1, DocPlace(3, False))],
        ),
        ("def f(): return 1\n", [(1, DocPlace(1, False))]),
        ("def f(\n    a,\n) -> int: ...\n", [(1, DocPlace(3, False))]),
        (
            "class C:\n    def f(self):\n        pass\n",
            [
                (1, DocPlace(1, False)),
                (2, DocPlace(2, False)),
            ],
        ),
    ],
    ids=["wrapped-signature", "one-line-def", "wrapped-one-line-body", "nested"],
)
def test_a_docstring_is_set_after_the_line_that_ends_the_signature(
    python_definition, text, expected
):
    from comment_review.reading.python.projection import code_lines_for

    result = import_module("comment_review.reading.python").read_python(
        text, python_definition
    )
    assert not isinstance(result, ReadFailure)
    lines = code_lines_for(result)
    assert [(c.line, c.documents) for c in lines if c.documents] == expected


@pytest.mark.parametrize("ending", ["\n", "\r\n", "\r"])
def test_classification_closing_doc_comment_has_one_owner(python_definition, ending):
    from pathlib import Path

    from comment_review.reading.python.projection import (
        code_lines_for,
        paragraphs_for,
    )
    from comment_review.reading.series import Kind

    text = ending.join(
        [
            "def f():",
            '    r"""full',
            '    docs""" # closing note',
            "    work() # detail",
            "",
        ]
    )
    result = import_module("comment_review.reading.python").read_python(
        text, python_definition
    )
    assert not isinstance(result, ReadFailure)
    assert len(result.payloads) == len(result.source.documentation) == 1
    paragraphs = paragraphs_for(Path("m.py"), result)
    assert not isinstance(paragraphs, ReadFailure)
    assert [(p.kind, p.start, p.end, p.raw_lines, p.anchor) for p in paragraphs] == [
        (
            Kind.DOCSTRING,
            2,
            3,
            ['    r"""full', '    docs""" # closing note'],
            "",
        ),
        (Kind.TRAILING, 4, 4, [" # detail"], "    work()"),
    ]
    assert paragraphs[0].address == "a1"
    assert code_lines_for(result) == [
        CodeLine(1, "def f():", DocPlace(1, False)),
        CodeLine(4, "    work()", None),
    ]
    assert (
        result.source.slice(result.source.sections[0].span)
        == 'r"""full' + ending + '    docs""" # closing note'
    )
    assert result.source.reconstruct() == text


@pytest.mark.parametrize(
    "header",
    [
        'def f(x: dict[str, int] = {"key": value[1:3]}) -> (lambda x: x):',
        "async def f(x=(lambda y: y)) -> dict[str, int]:",
        "class C[T: (int, str) = int](factory(lambda x: x)):",
    ],
)
def test_documentation_header_colons_inside_expressions_are_shielded(
    python_definition, header
):
    text = header + '\n    ("complete " r"docs") # closer\n    work() # detail\n'
    result = import_module("comment_review.reading.python").read_python(
        text, python_definition
    )
    assert not isinstance(result, ReadFailure)
    assert result.source.declarations[0].header == SourceSpan(0, len(header))
    assert literal_value(result.source.text, result.payloads[0]) == "complete docs"
    assert result.payloads[0].expression.declaration == 0
    assert (
        result.source.slice(result.source.sections[0].span)
        == '("complete " r"docs") # closer'
    )
    assert result.source.slice(result.source.sections[1].span) == "# detail\n"
    assert result.source.reconstruct() == text


@pytest.mark.parametrize("annotation", ["lambda x: x", "lambda x: lambda y: y"])
def test_declaration_annotation_lambda_colons_keep_documentation_position(
    python_definition, annotation
):
    header = "def f() -> " + annotation + ":"
    text = header + '\n    "complete docs"\n    pass\n'
    result = import_module("comment_review.reading.python").read_python(
        text, python_definition
    )
    assert not isinstance(result, ReadFailure)
    assert result.source.declarations == (
        SourceDeclaration(SourceSpan(0, len(header)), 0, "function"),
    )
    assert [
        literal_value(result.source.text, payload) for payload in result.payloads
    ] == ["complete docs"]
    assert result.source.reconstruct() == text


@pytest.mark.parametrize("spelling", ["lambda\u0301", "lambda\u203f", "lambda\u00b7x"])
def test_declaration_annotation_unicode_spelling_is_not_lambda_keyword(
    python_definition, spelling
):
    header = "def f() -> " + spelling + ":"
    text = header + '\n    "docs"\n'
    result = import_module("comment_review.reading.python").read_python(
        text, python_definition
    )
    assert not isinstance(result, ReadFailure)
    assert result.source.declarations == (
        SourceDeclaration(SourceSpan(0, len(header)), 0, "function"),
    )
    assert [
        literal_value(result.source.text, payload) for payload in result.payloads
    ] == ["docs"]
    assert result.payloads[0].expression.declaration == 0
    assert result.source.slice(result.source.sections[0].span) == '"docs"'
    position = result.source.position(result.source.sections[0].span.start)
    assert (position.line, position.column) == (2, 4)
    assert result.source.reconstruct() == text


@pytest.mark.parametrize(
    ("shared", "broken"),
    [
        ('def fn(): "doc"; y = 42\n', 'def fn():\n    "doc"\n    y = 42\n'),
        ('def fn(): "doc"\n', 'def fn():\n    "doc"\n'),
        ('class C: "doc"; y = 42\n', 'class C:\n    "doc"\n    y = 42\n'),
        (
            'class C:\n  def m(self): "doc"; y = 42  # note\n',
            'class C:\n  def m(self):\n    "doc"\n    y = 42  # note\n',
        ),
        ('if x:\n   pass\ndef fn(): "doc"\n', 'if x:\n   pass\ndef fn():\n   "doc"\n'),
        ('def f():\n\t"""Doc."""; y = 42\n', 'def f():\n\t"""Doc."""\n\ty = 42\n'),
        ('"""Mod."""; y = 42\n', '"""Mod."""\ny = 42\n'),
        (
            'def fn(): "doc"; a = 1; b = 2  # note\n',
            'def fn():\n    "doc"\n    a = 1; b = 2  # note\n',
        ),
        (
            'def f():\r\n    """Doc.""" ; y = 42\r\n',
            'def f():\r\n    """Doc."""\r\n    y = 42\r\n',
        ),
    ],
)
def test_a_docstring_sharing_its_line_reads_as_its_broken_source(shared, broken):
    from conftest import build

    compile(shared, "m.py", "exec")
    compile(broken, "m.py", "exec")
    page, expected = build(shared), build(broken)
    assert page.text == broken
    assert [(p.address, p.kind, p.raw_text, p.anchor) for p in page] == [
        (p.address, p.kind, p.raw_text, p.anchor) for p in expected
    ]
