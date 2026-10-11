from dataclasses import FrozenInstanceError
from typing import Any, cast, get_args

import pytest

from comment_review.reading.diagnostics import (
    ReadDiagnostic,
    ReadFailure,
    ReadStage,
    SourceRead,
)
from comment_review.reading.source import SourceSpan, SourceStructure


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
