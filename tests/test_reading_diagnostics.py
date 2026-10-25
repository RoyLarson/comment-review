from dataclasses import FrozenInstanceError
from pathlib import Path
from typing import Any, cast, get_args

import pytest

from comment_review.flows.language_definitions import installed_registry
from comment_review.flows.read_diagnostics import LocatedReadFailure, format_failure
from comment_review.reading import lexer, readers
from comment_review.reading.diagnostics import (
    ReadDiagnostic,
    ReadFailure,
    ReadStage,
    SourceRead,
)
from comment_review.reading.paragraph import Paragraph
from comment_review.reading.python.projection import paragraphs_for
from comment_review.reading.python.records import PythonRead
from comment_review.reading.source import SourceSpan, SourceStructure


@pytest.mark.parametrize(
    "text",
    [
        "x = [1,",
        "def f(:\n    pass\n",
        'x = """open',
    ],
)
def test_read_paragraphs_reports_python_refusal(text):
    registry = installed_registry()
    assert not isinstance(registry, ReadFailure)
    result = readers.read_paragraphs(
        Path("m.py"), text, lexer.LANGUAGES[0], registry=registry
    )
    assert isinstance(result, ReadFailure)
    assert result.diagnostics[0].stage == ReadStage.LEX
    assert result.diagnostics[0].span is not None


def test_read_paragraphs_unterminated_comment_before_decoration(monkeypatch):
    path = Path("m.c")
    text = "int x;\r\n/* open\r\nstill open"
    lang = lexer.language_for(path)
    assert lang is not None

    def conceal(*args):
        pytest.fail("Refused paragraphs must not reach decoration")

    monkeypatch.setattr(readers, "flag_structural_docs", conceal)
    result = readers.read_paragraphs(path, text, lang)
    assert isinstance(result, ReadFailure)
    assert [(d.stage, d.code, d.span) for d in result.diagnostics] == [
        (ReadStage.LEX, "unterminated-comment", SourceSpan(8, len(text)))
    ]


def test_read_paragraphs_retains_signal_order(monkeypatch):
    records = [
        Paragraph("m.py", 1, 1, "unparsed", "unsupported reading"),
        Paragraph("m.py", 2, 2, "comment", "open"),
    ]
    records[1].annotations.add("unterminated-paragraph-comment")
    monkeypatch.setattr(readers, "paragraphs_lexical", lambda *args: records)
    lang = lexer.language_for(Path("m.c"))
    assert lang is not None
    result = readers.read_paragraphs(Path("m.c"), "code\n# open", lang)
    assert isinstance(result, ReadFailure)
    assert [(d.code, d.span) for d in result.diagnostics] == [
        ("incomplete-read", None),
        ("unterminated-comment", SourceSpan(5, 11)),
    ]


def test_read_paragraphs_invalid_record_and_unexpected_error_propagate(monkeypatch):
    def broken(*args):
        raise RuntimeError("reader defect")

    lang = lexer.language_for(Path("m.c"))
    assert lang is not None
    monkeypatch.setattr(readers, "paragraphs_lexical", broken)
    with pytest.raises(RuntimeError, match="reader defect"):
        readers.read_paragraphs(Path("m.c"), "", lang)
    record = Paragraph("m.py", 3, 3, "comment", "open")
    record.annotations.add("unterminated-paragraph-comment")
    monkeypatch.setattr(readers, "paragraphs_lexical", lambda *args: [record])
    with pytest.raises(ValueError, match="source lines"):
        readers.read_paragraphs(Path("m.c"), "# open", lang)


@pytest.mark.parametrize("text", ["", "/* note */\nint x;\n"])
def test_read_paragraphs_preserves_supported_readings(text):
    path = Path("m.c")
    lang = lexer.language_for(path)
    assert lang is not None
    expected = lexer.paragraphs_lexical(path, text, lang)
    lexer.flag_structural_docs(expected, text, lang)
    registry = installed_registry()
    assert not isinstance(registry, ReadFailure)
    result = readers.read_source(path, text, registry=registry)
    assert isinstance(result, lexer.LexicalRead)
    assert result.paragraphs(path) == expected


@pytest.mark.parametrize(
    "text,expected",
    [("", []), ("# note\nx=1\n", [(1, 1, "matter", ["# note"])])],
)
def test_read_source_gives_python_its_lexical_read(text, expected):
    path = Path("m.py")
    registry = installed_registry()
    assert not isinstance(registry, ReadFailure)
    result = readers.read_source(path, text, registry=registry)
    assert isinstance(result, PythonRead)
    assert result.source.text is text
    assert result.a_series is True
    paragraphs = paragraphs_for(path, result)
    assert not isinstance(paragraphs, ReadFailure)
    assert [(p.start, p.end, p.kind, p.raw_lines) for p in paragraphs] == expected


def test_python_paragraph_adapter_recognizes_source_once(monkeypatch):
    registry = installed_registry()
    assert not isinstance(registry, ReadFailure)
    calls = []
    recognize = readers.read_python

    def counted(text, definition):
        result = recognize(text, definition)
        calls.append(result)
        return result

    monkeypatch.setattr(readers, "read_python", counted)
    text = 'def f(): "doc"; return 1\n'
    result = readers.read_paragraphs(
        Path("m.py"), text, lexer.LANGUAGES[0], registry=registry
    )
    assert isinstance(result, list)
    assert len(calls) == 1
    assert result == paragraphs_for(Path("m.py"), calls[0])
    assert isinstance(result[0], Paragraph)
    assert result[0].raw_lines == ['    "doc"']


def test_stage_values_and_source_read_alternatives():
    assert [(stage.name, stage.value) for stage in ReadStage] == [
        ("ACQUIRE", "acquire"),
        ("DECODE", "decode"),
        ("SELECT", "select"),
        ("LEX", "lex"),
        ("PLACE", "place"),
    ]
    assert get_args(SourceRead) == (SourceStructure, ReadFailure)
    success = SourceStructure("", (), (), (), ())
    failure = ReadFailure((ReadDiagnostic(ReadStage.ACQUIRE, "io-error", "Oops"),))
    assert success.text == ""
    assert not isinstance(success, ReadFailure)
    assert success != failure


@pytest.mark.parametrize("stage", ["decode", None, 1, True])
def test_diagnostic_rejects_invalid_stage(stage):
    with pytest.raises(ValueError):
        ReadDiagnostic(stage, "code", "message")


@pytest.mark.parametrize("field", ["code", "message"])
@pytest.mark.parametrize("value", ["", " ", "\t\r\n", None, 1, True, b"text"])
def test_diagnostic_requires_nonblank_strings(field, value):
    values: dict[str, Any] = {
        "stage": ReadStage.LEX,
        "code": "code",
        "message": "message",
    }
    values[field] = value
    with pytest.raises(ValueError):
        ReadDiagnostic(**values)


@pytest.mark.parametrize("span", [(0, 1), 0, True, "span"])
def test_diagnostic_rejects_invalid_span(span):
    with pytest.raises(ValueError):
        ReadDiagnostic(ReadStage.LEX, "code", "message", span=span)


@pytest.mark.parametrize("offset", [-1, True, False, 0.0, "0", b"0"])
def test_diagnostic_rejects_invalid_byte_offset(offset):
    with pytest.raises(ValueError):
        ReadDiagnostic(ReadStage.DECODE, "code", "message", byte_offset=offset)


@pytest.mark.parametrize("stage", list(ReadStage))
def test_locations_obey_stage_boundaries(stage):
    assert ReadDiagnostic(stage, "code", "message").span is None
    if stage in (ReadStage.LEX, ReadStage.PLACE):
        span = SourceSpan(100, 100)
        assert ReadDiagnostic(stage, "code", "message", span).span is span
    else:
        with pytest.raises(ValueError):
            ReadDiagnostic(stage, "code", "message", SourceSpan(0, 1))
    if stage == ReadStage.DECODE:
        for offset in (0, 100):
            assert (
                ReadDiagnostic(stage, "code", "message", byte_offset=offset).byte_offset
                == offset
            )
    else:
        with pytest.raises(ValueError):
            ReadDiagnostic(stage, "code", "message", byte_offset=0)
    with pytest.raises(ValueError):
        ReadDiagnostic(stage, "code", "message", SourceSpan(0, 1), 0)


def test_diagnostic_preserves_supplied_values():
    span = SourceSpan(3, 99)
    diagnostic = ReadDiagnostic(ReadStage.LEX, " custom/code\t", " message \n", span)
    assert diagnostic.stage is ReadStage.LEX
    assert diagnostic.code == " custom/code\t"
    assert diagnostic.message == " message \n"
    assert diagnostic.span is span
    assert diagnostic.byte_offset is None


@pytest.mark.parametrize("field", ["stage", "code", "message", "span", "byte_offset"])
def test_diagnostic_is_frozen(field):
    diagnostic = ReadDiagnostic(ReadStage.LEX, "code", "message")
    with pytest.raises(FrozenInstanceError):
        setattr(diagnostic, field, None)


@pytest.mark.parametrize("records", [[], (), None, "diagnostics", (None,), ("bad",)])
def test_failure_rejects_invalid_diagnostics(records):
    with pytest.raises(ValueError):
        ReadFailure(records)


def test_failure_preserves_order_duplicates_and_immutable_tuple():
    first = ReadDiagnostic(ReadStage.LEX, "unterminated-comment", "Open comment")
    second = ReadDiagnostic(ReadStage.PLACE, "unsupported-placement", "No owner")
    records = (second, first, second)
    failure = ReadFailure(records)
    assert failure.diagnostics is records
    assert failure.diagnostics == (second, first, second)
    with pytest.raises(FrozenInstanceError):
        cast(Any, failure).diagnostics = (first,)
    with pytest.raises(TypeError):
        cast(Any, failure.diagnostics)[0] = first


def test_failure_renderer_uses_retained_context_and_encounter_order():
    text = "\t\u0065\u0301\r\nZ"
    diagnostics = (
        ReadDiagnostic(ReadStage.PLACE, "owner", "No owner", SourceSpan(5, 6)),
        ReadDiagnostic(ReadStage.LEX, "open", "Open literal", SourceSpan(4, 4)),
    )
    failure = LocatedReadFailure(diagnostics, "missing/example.py", "python", text)
    assert failure.text is text
    assert failure.diagnostics is diagnostics
    assert isinstance(failure, ReadFailure)
    assert format_failure(failure, path=failure.path).splitlines() == [
        "missing/example.py [python] place/owner: No owner "
        "(line 2, one-based; column 0, zero-based)",
        "missing/example.py [python] lex/open: Open literal "
        "(line 1, one-based; column 4, zero-based)",
    ]


def test_failure_renderer_distinguishes_bytes_and_omitted_context():
    failure = ReadFailure(
        (ReadDiagnostic(ReadStage.DECODE, "utf8", "Bad byte", byte_offset=7),)
    )
    assert format_failure(failure, path="example.py") == (
        "example.py decode/utf8: Bad byte (byte offset 7, zero-based)"
    )
    acquire = ReadFailure((ReadDiagnostic(ReadStage.ACQUIRE, "io", "Missing file"),))
    assert (
        format_failure(acquire, path="example.py")
        == "example.py acquire/io: Missing file"
    )


def test_failure_renderer_requires_text_for_character_spans_and_allows_empty_eof():
    failure = ReadFailure(
        (ReadDiagnostic(ReadStage.LEX, "open", "Open", SourceSpan(0, 0)),)
    )
    with pytest.raises(ValueError):
        format_failure(failure, path="example.py")
    assert "line 1, one-based; column 0, zero-based" in format_failure(
        failure, path="example.py", text=""
    )
    assert LocatedReadFailure(failure.diagnostics, "example.py", None, "").text == ""


@pytest.mark.parametrize("text", [None, "", "x"])
def test_character_failure_rejects_spans_outside_retained_text(text):
    failure = ReadFailure(
        (ReadDiagnostic(ReadStage.LEX, "open", "Open", SourceSpan(1, 2)),)
    )
    with pytest.raises(ValueError):
        LocatedReadFailure(failure.diagnostics, "example.py", None, text)
    with pytest.raises(ValueError):
        format_failure(failure, path="example.py", text=text)


@pytest.mark.parametrize(
    "field,value", [("path", None), ("path", 1), ("language", 1), ("text", b"x")]
)
def test_located_failure_rejects_invalid_context_types(field, value):
    values: dict[str, Any] = dict(path="example.py", language=None, text=None)
    values[field] = value
    records = (ReadDiagnostic(ReadStage.ACQUIRE, "io", "Missing"),)
    with pytest.raises(ValueError):
        LocatedReadFailure(records, **values)
    with pytest.raises(ValueError):
        format_failure(ReadFailure(records), **values)


@pytest.mark.parametrize("field", ["diagnostics", "path", "language", "text"])
def test_located_failure_is_frozen(field):
    failure = LocatedReadFailure(
        (ReadDiagnostic(ReadStage.ACQUIRE, "io", "Missing"),), "example.py", None, None
    )
    with pytest.raises(FrozenInstanceError):
        setattr(failure, field, None)


def test_failure_renderer_explicit_context_overrides_retained_values():
    failure = LocatedReadFailure(
        (ReadDiagnostic(ReadStage.LEX, "open", "Open", SourceSpan(1, 1)),),
        "old.py",
        "python",
        "\nx",
    )
    rendered = format_failure(failure, path="new.js", language="javascript", text="ab")
    assert rendered == (
        "new.js [javascript] lex/open: Open (line 1, one-based; column 1, zero-based)"
    )
    with pytest.raises(ValueError):
        format_failure(failure, path="new.py", text="")


def test_failure_renderer_keeps_multiline_messages_on_one_report_line():
    failure = ReadFailure((ReadDiagnostic(ReadStage.ACQUIRE, "io", "Missing\nfile\r"),))
    assert format_failure(failure, path="example.py").splitlines() == [
        "example.py acquire/io: Missing\\nfile\\r"
    ]


@pytest.mark.parametrize("records", [[], (), (None,)])
def test_located_failure_preserves_base_diagnostic_validation(records):
    with pytest.raises(ValueError):
        LocatedReadFailure(records, "example.py", None, None)


def test_failure_renderer_rejects_non_failure_input():
    with pytest.raises(ValueError):
        format_failure(cast(Any, None), path="example.py")
