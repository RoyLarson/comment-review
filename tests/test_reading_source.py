from dataclasses import FrozenInstanceError

import pytest

from comment_review.reading.source import (
    DocumentationOwner,
    RegionKind,
    SourceDeclaration,
    SourcePosition,
    SourceRegion,
    SourceSection,
    SourceSpan,
    SourceStructure,
)


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


def structure(text, bounds):
    return SourceStructure(
        text,
        tuple(
            SourceRegion(SourceSpan(start, end), kind) for start, end, kind in bounds
        ),
        (),
        (),
        (),
    )


def test_partition_preserves_exact_source_and_classifications():
    source = structure(
        'a "b"#c!',
        [
            (0, 1, RegionKind.CODE),
            (1, 2, RegionKind.WHITESPACE),
            (2, 5, RegionKind.LITERAL),
            (5, 7, RegionKind.COMMENT),
            (7, 8, RegionKind.DIRECTIVE),
        ],
    )
    assert source.text == 'a "b"#c!'
    assert [region.kind.value for region in source.regions] == [
        "code",
        "whitespace",
        "literal",
        "comment",
        "directive",
    ]


def test_partition_accepts_empty_text():
    assert structure("", []).regions == ()


@pytest.mark.parametrize(
    "bounds,index",
    [
        ([(0, 1), (2, 3)], 1),
        ([(0, 2), (1, 3)], 1),
        ([(2, 3), (0, 2)], 0),
        ([(1, 3)], 0),
        ([(0, 2)], 1),
        ([(0, 4)], 0),
        ([], 0),
    ],
)
def test_partition_rejects_gap_overlap_order_missing_coverage_and_overshoot(
    bounds, index
):
    with pytest.raises(ValueError, match=rf"regions.*{index}"):
        structure("abc", [(start, end, RegionKind.CODE) for start, end in bounds])


def test_partition_rejects_empty_region():
    with pytest.raises(ValueError, match="span"):
        SourceRegion(SourceSpan(1, 1), RegionKind.CODE)


@pytest.mark.parametrize(
    "field", ["regions", "sections", "declarations", "documentation"]
)
@pytest.mark.parametrize("value", [[], None, ""])
def test_partition_rejects_invalid_tuple_inputs(field, value):
    values = dict(text="", regions=(), sections=(), declarations=(), documentation=())
    values[field] = value
    with pytest.raises(ValueError, match=field):
        SourceStructure(**values)


@pytest.mark.parametrize(
    "field", ["regions", "sections", "declarations", "documentation"]
)
def test_partition_rejects_invalid_referenced_record_types(field):
    values = dict(
        text="a",
        regions=(SourceRegion(SourceSpan(0, 1), RegionKind.CODE),),
        sections=(),
        declarations=(),
        documentation=(),
    )
    values[field] = (object(),)
    with pytest.raises(ValueError, match=rf"{field}.*0"):
        SourceStructure(**values)


@pytest.mark.parametrize(
    "field,value",
    [
        ("regions", SourceRegion(SourceSpan(0, 1), RegionKind.CODE)),
        ("sections", SourceSection(SourceSpan(0, 0), "sample")),
        ("declarations", SourceDeclaration(SourceSpan(0, 0), 0, "sample")),
        ("documentation", DocumentationOwner(0, None)),
    ],
)
def test_partition_empty_text_rejects_nonempty_collections(field, value):
    values = dict(text="", regions=(), sections=(), declarations=(), documentation=())
    values[field] = (value,)
    with pytest.raises(ValueError, match=rf"{field}.*0"):
        SourceStructure(**values)


def test_partition_records_are_frozen():
    records = [
        SourceRegion(SourceSpan(0, 1), RegionKind.CODE),
        SourceSection(SourceSpan(0, 1), "sample"),
        SourceDeclaration(SourceSpan(0, 1), 0, "sample"),
        DocumentationOwner(0, None),
        structure("a", [(0, 1, RegionKind.CODE)]),
    ]
    for record in records:
        field = next(iter(record.__dataclass_fields__))
        with pytest.raises(FrozenInstanceError):
            setattr(record, field, None)


@pytest.mark.parametrize(
    "start,end,expected",
    [(0, 1, "a"), (1, 3, "bc"), (0, 3, "abc"), (1, 1, ""), (3, 3, "")],
)
def test_span_structure_slice_is_exact_and_half_open(start, end, expected):
    source = structure("abc", [(0, 3, RegionKind.CODE)])
    assert source.slice(SourceSpan(start, end)) == expected


def test_span_structure_slice_accepts_empty_source_eof():
    assert structure("", []).slice(SourceSpan(0, 0)) == ""


@pytest.mark.parametrize("start,end", [(0, 4), (4, 4)])
def test_span_structure_slice_rejects_out_of_range(start, end):
    source = structure("abc", [(0, 3, RegionKind.CODE)])
    with pytest.raises(ValueError, match="span"):
        source.slice(SourceSpan(start, end))


def test_span_structure_slice_uses_unicode_character_indices():
    source = structure("a\u00e9\U0001f680z", [(0, 4, RegionKind.CODE)])
    assert source.slice(SourceSpan(1, 3)) == "\u00e9\U0001f680"


def test_reconstruct_concatenates_differently_classified_region_slices(monkeypatch):
    source = structure(
        'a "b"#c!',
        [
            (0, 1, RegionKind.CODE),
            (1, 2, RegionKind.WHITESPACE),
            (2, 5, RegionKind.LITERAL),
            (5, 7, RegionKind.COMMENT),
            (7, 8, RegionKind.DIRECTIVE),
        ],
    )
    calls = []
    original_slice = SourceStructure.slice

    def record_slice(self, span):
        calls.append((span.start, span.end))
        return original_slice(self, span)

    monkeypatch.setattr(SourceStructure, "slice", record_slice)
    assert source.reconstruct() == 'a "b"#c!'
    assert calls == [(0, 1), (1, 2), (2, 5), (5, 7), (7, 8)]
    assert [source.slice(region.span) for region in source.regions] == [
        "a",
        " ",
        '"b"',
        "#c",
        "!",
    ]


def test_reconstruct_empty_source():
    source = structure("", [])
    assert source.reconstruct() == ""
    assert source.regions == ()


@pytest.mark.parametrize(
    "text,bounds,components",
    [
        (
            "\ufeffa",
            [(0, 1, RegionKind.WHITESPACE), (1, 2, RegionKind.CODE)],
            ["\ufeff", "a"],
        ),
        (
            "\u00e9e\u0301\U0001f680",
            [(0, 2, RegionKind.CODE), (2, 4, RegionKind.LITERAL)],
            ["\u00e9e", "\u0301\U0001f680"],
        ),
        (
            "a\r\nb\nc\rd",
            [
                (0, 3, RegionKind.CODE),
                (3, 5, RegionKind.COMMENT),
                (5, 8, RegionKind.LITERAL),
            ],
            ["a\r\n", "b\n", "c\rd"],
        ),
        (
            "x",
            [(0, 1, RegionKind.CODE)],
            ["x"],
        ),
        (
            "x\n",
            [(0, 1, RegionKind.CODE), (1, 2, RegionKind.WHITESPACE)],
            ["x", "\n"],
        ),
        (
            '" a\t "# b\t  \r\n',
            [(0, 6, RegionKind.LITERAL), (6, 14, RegionKind.COMMENT)],
            ['" a\t "', "# b\t  \r\n"],
        ),
    ],
    ids=[
        "decoded-bom",
        "unicode-combining",
        "mixed-endings",
        "no-final-newline",
        "final-newline",
        "literal-comment-whitespace",
    ],
)
def test_reconstruct_preserves_every_character(text, bounds, components):
    source = structure(text, bounds)
    assert [source.slice(region.span) for region in source.regions] == components
    assert source.reconstruct() == text
