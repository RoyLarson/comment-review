from dataclasses import FrozenInstanceError

import pytest

from comment_review.reading.source import SourcePosition, SourceSpan


@pytest.mark.parametrize("start,end", [(-1, 0), (0, -1), (2, 1)])
def test_span_rejects_invalid_bounds(start, end):
    with pytest.raises(ValueError):
        SourceSpan(start, end)


@pytest.mark.parametrize("offset", [0, 3])
def test_span_allows_empty_bounds(offset):
    span = SourceSpan(offset, offset)
    assert span.start == span.end == offset


def test_span_selects_half_open_character_offsets():
    source = "a\u00e9\U0001f680z"
    span = SourceSpan(1, 3)
    assert source[span.start : span.end] == "\u00e9\U0001f680"


@pytest.mark.parametrize("field", ["start", "end"])
def test_span_record_is_immutable(field):
    span = SourceSpan(0, 1)
    with pytest.raises(FrozenInstanceError):
        setattr(span, field, 2)


@pytest.mark.parametrize("field", ["line", "column"])
def test_span_position_record_is_immutable(field):
    position = SourcePosition(1, 0)
    with pytest.raises(FrozenInstanceError):
        setattr(position, field, 2)


@pytest.mark.parametrize("line,column", [(0, 0), (-1, 0), (1, -1)])
def test_span_position_rejects_invalid_limits(line, column):
    with pytest.raises(ValueError):
        SourcePosition(line, column)


@pytest.mark.parametrize("line,column", [(1, 0), (3, 12)])
def test_span_position_accepts_valid_limits(line, column):
    position = SourcePosition(line, column)
    assert (position.line, position.column) == (line, column)


@pytest.mark.parametrize("value", [True, False, 1.0, "1", None])
@pytest.mark.parametrize("field", ["start", "end"])
def test_span_rejects_non_integer_bounds(field, value):
    bounds = {"start": 0, "end": 1}
    bounds[field] = value
    with pytest.raises(ValueError):
        SourceSpan(**bounds)


@pytest.mark.parametrize("value", [True, False, 1.0, "1", None])
@pytest.mark.parametrize("field", ["line", "column"])
def test_span_position_rejects_non_integer_values(field, value):
    values = {"line": 1, "column": 0}
    values[field] = value
    with pytest.raises(ValueError):
        SourcePosition(**values)
