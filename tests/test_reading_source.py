import subprocess
import sys
from dataclasses import FrozenInstanceError, fields
from pathlib import Path
from typing import Any, cast

import pytest

from comment_review.reading.coordinates import SourceCoordinates
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


def test_coordinates_share_positions_without_a_source_partition():
    text = "\t\u0065\u0301\r\nZ\rQ\n"
    coordinates = SourceCoordinates(text)
    assert coordinates.text is text
    assert [coordinates.position(i) for i in range(10)] == [
        SourcePosition(1, 0),
        SourcePosition(1, 1),
        SourcePosition(1, 2),
        SourcePosition(1, 3),
        SourcePosition(1, 4),
        SourcePosition(2, 0),
        SourcePosition(2, 1),
        SourcePosition(3, 0),
        SourcePosition(3, 1),
        SourcePosition(4, 0),
    ]


@pytest.mark.parametrize(
    "text,spans",
    [
        ("", []),
        ("a", [(0, 1)]),
        ("a\n", [(0, 1)]),
        ("a\r\n\nb\rc", [(0, 1), (3, 3), (4, 5), (6, 7)]),
        ("a\r\rb\r", [(0, 1), (2, 2), (3, 4)]),
    ],
)
def test_coordinates_line_span_leaves_out_the_line_break(text, spans):
    coordinates = SourceCoordinates(text)
    assert [coordinates.line_span(n) for n in range(1, len(spans) + 1)] == spans
    for number in (0, len(spans) + 1):
        with pytest.raises(ValueError):
            coordinates.line_span(number)


@pytest.mark.parametrize("text", [None, b"", 1, True])
def test_coordinates_reject_non_string_text(text):
    with pytest.raises(ValueError):
        SourceCoordinates(text)


@pytest.mark.parametrize("offset", [-1, 2, None, True, 0.0])
def test_coordinates_reject_invalid_offsets(offset):
    with pytest.raises(ValueError):
        SourceCoordinates("x").position(offset)


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


@pytest.mark.parametrize("kind", ["unknown", "code", None, []])
def test_region_rejects_non_enum_kind(kind: object):
    with pytest.raises(ValueError, match="kind"):
        SourceRegion(SourceSpan(0, 1), cast(RegionKind, kind))


@pytest.mark.parametrize("kind", list(RegionKind))
def test_region_preserves_enum_kind(kind: RegionKind):
    assert SourceRegion(SourceSpan(0, 1), kind).kind is kind


@pytest.mark.parametrize("text", [["x"], b"x", None, [], b""])
def test_structure_rejects_non_string_text(text: object):
    regions = (SourceRegion(SourceSpan(0, 1), RegionKind.CODE),)
    with pytest.raises(ValueError, match=r"^text\b"):
        SourceStructure(cast(str, text), regions, (), (), ())


def test_structure_validates_text_before_collections():
    with pytest.raises(ValueError, match=r"^text\b"):
        SourceStructure(cast(str, None), cast(Any, []), (), (), ())


@pytest.mark.parametrize("text", ["", "x", "\ufeffx\r\n\u00e9\t"])
def test_structure_preserves_exact_string_input(text: str):
    source = structure(text, [(0, len(text), RegionKind.CODE)] if text else [])
    assert source.text is text
    assert source.reconstruct() == text


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


def test_a_declaration_is_declared_on_its_anchors_line():
    # The header opens on line 1 and its anchor, past the attribute, is on line 2.
    text = "@d\ndef f(): pass\n"
    declaration = SourceDeclaration(SourceSpan(0, 16), 3, "def")
    source = SourceStructure(
        text,
        (SourceRegion(SourceSpan(0, len(text)), RegionKind.CODE),),
        (),
        (declaration,),
        (),
    )
    assert source.declaring_line(declaration) == 2


def test_classification_reference_distinguishes_literal_comment_and_directive():
    text = 'let note = "# fake /* data */"; // real\n@keep\n'
    source = structure(
        text,
        [
            (0, 3, RegionKind.CODE),
            (3, 4, RegionKind.WHITESPACE),
            (4, 8, RegionKind.CODE),
            (8, 9, RegionKind.WHITESPACE),
            (9, 10, RegionKind.CODE),
            (10, 11, RegionKind.WHITESPACE),
            (11, 30, RegionKind.LITERAL),
            (30, 31, RegionKind.CODE),
            (31, 32, RegionKind.WHITESPACE),
            (32, 39, RegionKind.COMMENT),
            (39, 40, RegionKind.WHITESPACE),
            (40, 45, RegionKind.DIRECTIVE),
            (45, 46, RegionKind.WHITESPACE),
        ],
    )
    expected = [
        (0, 3, "let", "code"),
        (3, 4, " ", "whitespace"),
        (4, 8, "note", "code"),
        (8, 9, " ", "whitespace"),
        (9, 10, "=", "code"),
        (10, 11, " ", "whitespace"),
        (11, 30, '"# fake /* data */"', "literal"),
        (30, 31, ";", "code"),
        (31, 32, " ", "whitespace"),
        (32, 39, "// real", "comment"),
        (39, 40, "\n", "whitespace"),
        (40, 45, "@keep", "directive"),
        (45, 46, "\n", "whitespace"),
    ]
    actual = [
        (
            region.span.start,
            region.span.end,
            source.slice(region.span),
            region.kind.value,
        )
        for region in source.regions
    ]
    assert actual == expected
    assert source.reconstruct() == text

    relabelled = SourceStructure(
        text,
        tuple(
            SourceRegion(region.span, RegionKind.COMMENT) if index == 6 else region
            for index, region in enumerate(source.regions)
        ),
        (),
        (),
        (),
    )
    relabelled_actual = [
        (
            region.span.start,
            region.span.end,
            relabelled.slice(region.span),
            region.kind.value,
        )
        for region in relabelled.regions
    ]
    assert relabelled.reconstruct() == text
    assert relabelled_actual != expected
    assert [
        (wanted, observed)
        for wanted, observed in zip(expected, relabelled_actual, strict=True)
        if wanted != observed
    ] == [
        (
            (11, 30, '"# fake /* data */"', "literal"),
            (11, 30, '"# fake /* data */"', "comment"),
        )
    ]


def test_classification_documentation_literal_and_interpolation_keep_separate_facts():
    text = 'item flux\n"""Read # data."""\nf"left # {flux} right //"\n'
    source = SourceStructure(
        text,
        (
            SourceRegion(SourceSpan(0, 4), RegionKind.CODE),
            SourceRegion(SourceSpan(4, 5), RegionKind.WHITESPACE),
            SourceRegion(SourceSpan(5, 9), RegionKind.CODE),
            SourceRegion(SourceSpan(9, 10), RegionKind.WHITESPACE),
            SourceRegion(SourceSpan(10, 28), RegionKind.LITERAL),
            SourceRegion(SourceSpan(28, 29), RegionKind.WHITESPACE),
            SourceRegion(SourceSpan(29, 38), RegionKind.LITERAL),
            SourceRegion(SourceSpan(38, 44), RegionKind.CODE),
            SourceRegion(SourceSpan(44, 54), RegionKind.LITERAL),
            SourceRegion(SourceSpan(54, 55), RegionKind.WHITESPACE),
        ),
        (SourceSection(SourceSpan(10, 28), "atlas/documentation-literal"),),
        (SourceDeclaration(SourceSpan(0, 9), 5, "atlas/item"),),
        (DocumentationOwner(0, 0),),
    )
    assert [
        (
            region.span.start,
            region.span.end,
            source.slice(region.span),
            region.kind.value,
        )
        for region in source.regions
    ] == [
        (0, 4, "item", "code"),
        (4, 5, " ", "whitespace"),
        (5, 9, "flux", "code"),
        (9, 10, "\n", "whitespace"),
        (10, 28, '"""Read # data."""', "literal"),
        (28, 29, "\n", "whitespace"),
        (29, 38, 'f"left # ', "literal"),
        (38, 44, "{flux}", "code"),
        (44, 54, ' right //"', "literal"),
        (54, 55, "\n", "whitespace"),
    ]
    assert source.reconstruct() == text
    assert source.documentation == (DocumentationOwner(0, 0),)
    assert source.sections == (
        SourceSection(SourceSpan(10, 28), "atlas/documentation-literal"),
    )
    assert source.slice(source.sections[0].span) == '"""Read # data."""'
    assert source.regions[4].kind is RegionKind.LITERAL
    assert source.slice(source.declarations[0].header) == "item flux"


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
    values: dict[str, Any] = dict(
        text="", regions=(), sections=(), declarations=(), documentation=()
    )
    values[field] = value
    with pytest.raises(ValueError, match=field):
        SourceStructure(**values)


@pytest.mark.parametrize(
    "field", ["regions", "sections", "declarations", "documentation"]
)
def test_partition_rejects_invalid_referenced_record_types(field):
    values: dict[str, Any] = dict(
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
        ("sections", SourceSection(SourceSpan(0, 1), "sample")),
        ("declarations", SourceDeclaration(SourceSpan(0, 1), 0, "sample")),
        ("documentation", DocumentationOwner(0, None)),
    ],
)
def test_partition_empty_text_rejects_nonempty_collections(field, value):
    values: dict[str, Any] = dict(
        text="", regions=(), sections=(), declarations=(), documentation=()
    )
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


def test_position_reports_explicit_mixed_newline_coordinates():
    source = structure("a\r\nb\nc\rd", [(0, 8, RegionKind.CODE)])
    expected = [(1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (3, 0), (3, 1), (4, 0), (4, 1)]
    assert [source.position(offset) for offset in range(9)] == [
        SourcePosition(line, column) for line, column in expected
    ]


@pytest.mark.parametrize("text", ["", "\r", "\n", "\r\n", "a\r", "a\n", "a\r\n"])
def test_position_empty_source_and_newline_eof(text):
    source = structure(text, [(0, len(text), RegionKind.CODE)] if text else [])
    assert source.position(len(text)) == SourcePosition(2 if text else 1, 0)


def test_position_counts_characters_and_preserves_unicode_separators():
    text = "\ufeff\t\u00e9e\u0301\U0001f680\v\f\x85\u2028\u2029"
    source = structure(text, [(0, 11, RegionKind.CODE)])
    assert [source.position(offset) for offset in range(12)] == [
        SourcePosition(1, column) for column in range(12)
    ]


@pytest.mark.parametrize("offset", [-1, 4, True, False, 1.0, "1", None])
def test_position_rejects_invalid_offsets(offset):
    source = structure("abc", [(0, 3, RegionKind.CODE)])
    with pytest.raises(ValueError):
        source.position(offset)


def test_position_caches_immutable_derived_line_starts():
    source = structure("a\r\nb\nc\rd", [(0, 8, RegionKind.CODE)])
    coordinates = source._coordinates
    assert coordinates.text is source.text
    starts = coordinates._line_starts
    assert starts == (0, 3, 5, 7)
    field = coordinates.__dataclass_fields__["_line_starts"]
    assert not field.init
    assert not field.repr
    assert "_line_starts" not in repr(coordinates)
    for _ in range(3):
        assert source.position(2) == SourcePosition(1, 2)
        assert source.position(7) == SourcePosition(4, 0)
        assert source._coordinates is coordinates
        assert coordinates._line_starts is starts
    with pytest.raises(FrozenInstanceError):
        coordinates._line_starts = (0,)


@pytest.mark.parametrize("span", [SourceSpan(2, 2), None, (0, 1)])
def test_declaration_section_requires_nonempty_span(span):
    with pytest.raises(ValueError, match="span"):
        SourceSection(span, "section")


@pytest.mark.parametrize("header", [SourceSpan(2, 2), None, (0, 1)])
def test_declaration_requires_nonempty_header(header):
    with pytest.raises(ValueError, match="header"):
        SourceDeclaration(header, 2, "declaration")


@pytest.mark.parametrize("identifier", ["", " ", "\t\r\n", None, 1])
def test_declaration_section_requires_nonblank_form(identifier):
    with pytest.raises(ValueError, match="form"):
        SourceSection(SourceSpan(2, 4), identifier)


@pytest.mark.parametrize("identifier", ["", " ", "\t\r\n", None, 1])
def test_declaration_requires_nonblank_kind(identifier):
    with pytest.raises(ValueError, match="kind"):
        SourceDeclaration(SourceSpan(2, 4), 2, identifier)


@pytest.mark.parametrize("anchor", [1, 4, 5, -1, True, False, 2.0, "2", None])
def test_declaration_rejects_anchor_outside_header_or_noninteger(anchor):
    with pytest.raises(ValueError, match="anchor"):
        SourceDeclaration(SourceSpan(2, 4), anchor, "declaration")


@pytest.mark.parametrize("anchor", [2, 3])
def test_declaration_anchor_is_absolute_and_includes_header_start(anchor):
    declaration = SourceDeclaration(SourceSpan(2, 4), anchor, "declaration")
    assert declaration.anchor == anchor


def declaration_structure(text, sections=(), declarations=()):
    return SourceStructure(
        text,
        (SourceRegion(SourceSpan(0, len(text)), RegionKind.CODE),),
        sections,
        declarations,
        (),
    )


@pytest.mark.parametrize("span", [SourceSpan(0, 7), SourceSpan(6, 7)])
def test_declaration_structure_rejects_section_outside_source(span):
    with pytest.raises(ValueError, match=r"sections\[1\].*span"):
        declaration_structure(
            "abcdef",
            (SourceSection(SourceSpan(0, 1), "first"), SourceSection(span, "second")),
        )


@pytest.mark.parametrize("header", [SourceSpan(0, 7), SourceSpan(6, 7)])
def test_declaration_structure_rejects_header_outside_source(header):
    with pytest.raises(ValueError, match=r"declarations\[1\].*header"):
        declaration_structure(
            "abcdef",
            declarations=(
                SourceDeclaration(SourceSpan(0, 1), 0, "first"),
                SourceDeclaration(header, header.start, "second"),
            ),
        )


@pytest.mark.parametrize("second", [SourceSpan(1, 4), SourceSpan(0, 1)])
def test_declaration_structure_rejects_section_overlap_and_order(second):
    with pytest.raises(ValueError, match=r"sections\[1\]"):
        declaration_structure(
            "abcdef",
            (
                SourceSection(SourceSpan(1, 3), "first"),
                SourceSection(second, "second"),
            ),
        )


def test_declaration_structure_rejects_header_order():
    with pytest.raises(ValueError, match=r"declarations\[1\]"):
        declaration_structure(
            "abcdef",
            declarations=(
                SourceDeclaration(SourceSpan(3, 5), 3, "first"),
                SourceDeclaration(SourceSpan(1, 2), 1, "second"),
            ),
        )


def test_declaration_structure_accepts_nested_bodies_and_same_line_headers():
    source = declaration_structure(
        "outer { inner {} } next {}",
        sections=(
            SourceSection(SourceSpan(0, 19), "block"),
            SourceSection(SourceSpan(19, 26), "block"),
        ),
        declarations=(
            SourceDeclaration(SourceSpan(0, 5), 0, "outer"),
            SourceDeclaration(SourceSpan(8, 13), 8, "inner"),
            SourceDeclaration(SourceSpan(19, 23), 19, "next"),
        ),
    )
    assert [source.slice(record.header) for record in source.declarations] == [
        "outer",
        "inner",
        "next",
    ]


def test_declaration_structure_orders_headers_by_start_without_extent_rules():
    source = declaration_structure(
        "abcdef",
        declarations=(
            SourceDeclaration(SourceSpan(0, 6), 1, "first"),
            SourceDeclaration(SourceSpan(0, 2), 0, "same-start"),
            SourceDeclaration(SourceSpan(1, 3), 2, "overlapping"),
        ),
    )
    assert len(source.declarations) == 3


def test_declaration_preserves_exact_form_and_kind_identifiers():
    source = declaration_structure(
        "abcdef",
        sections=(SourceSection(SourceSpan(0, 6), "  Custom/Form\t"),),
        declarations=(SourceDeclaration(SourceSpan(1, 4), 2, " Kind/Custom "),),
    )
    assert source.sections[0].form == "  Custom/Form\t"
    assert source.declarations[0].kind == " Kind/Custom "


def test_section_keeps_separated_comment_fragments_in_one_owned_span():
    source = SourceStructure(
        "before\n## first\n\n\n## second\nafter",
        (
            SourceRegion(SourceSpan(0, 6), RegionKind.CODE),
            SourceRegion(SourceSpan(6, 7), RegionKind.WHITESPACE),
            SourceRegion(SourceSpan(7, 15), RegionKind.COMMENT),
            SourceRegion(SourceSpan(15, 18), RegionKind.WHITESPACE),
            SourceRegion(SourceSpan(18, 27), RegionKind.COMMENT),
            SourceRegion(SourceSpan(27, 28), RegionKind.WHITESPACE),
            SourceRegion(SourceSpan(28, 33), RegionKind.CODE),
        ),
        (SourceSection(SourceSpan(7, 27), "atlas/double-mark"),),
        (SourceDeclaration(SourceSpan(28, 33), 28, "atlas/item"),),
        (DocumentationOwner(0, 0),),
    )

    assert len(source.sections) == 1
    section = source.sections[0]
    assert (section.span.start, section.span.end) == (7, 27)
    assert section.form == "atlas/double-mark"
    assert source.slice(section.span) == "## first\n\n\n## second"
    assert [source.slice(region.span) for region in source.regions] == [
        "before",
        "\n",
        "## first",
        "\n\n\n",
        "## second",
        "\n",
        "after",
    ]
    assert source.reconstruct() == "before\n## first\n\n\n## second\nafter"
    assert source.documentation == (DocumentationOwner(0, 0),)
    owner_index = source.documentation[0].declaration
    assert owner_index is not None
    owner = source.declarations[owner_index]
    assert (owner.header.start, owner.header.end, owner.anchor) == (28, 33, 28)
    assert source.slice(owner.header) == "after"


def test_section_preserves_independent_forms_and_exact_spans_beside_code():
    source = SourceStructure(
        '#a x /*b*/ y """c"""',
        (
            SourceRegion(SourceSpan(0, 2), RegionKind.COMMENT),
            SourceRegion(SourceSpan(2, 3), RegionKind.WHITESPACE),
            SourceRegion(SourceSpan(3, 4), RegionKind.CODE),
            SourceRegion(SourceSpan(4, 5), RegionKind.WHITESPACE),
            SourceRegion(SourceSpan(5, 10), RegionKind.COMMENT),
            SourceRegion(SourceSpan(10, 11), RegionKind.WHITESPACE),
            SourceRegion(SourceSpan(11, 12), RegionKind.CODE),
            SourceRegion(SourceSpan(12, 13), RegionKind.WHITESPACE),
            SourceRegion(SourceSpan(13, 20), RegionKind.LITERAL),
        ),
        (
            SourceSection(SourceSpan(0, 2), " Atlas/line\t"),
            SourceSection(SourceSpan(5, 10), "Boreal:BLOCK"),
            SourceSection(SourceSpan(13, 20), "cedar.literal/v2 "),
        ),
        (
            SourceDeclaration(SourceSpan(3, 4), 3, "atlas/item"),
            SourceDeclaration(SourceSpan(11, 12), 11, "boreal/item"),
        ),
        (
            DocumentationOwner(0, None),
            DocumentationOwner(1, 0),
            DocumentationOwner(2, 1),
        ),
    )

    assert [(section.span.start, section.span.end) for section in source.sections] == [
        (0, 2),
        (5, 10),
        (13, 20),
    ]
    assert [section.form for section in source.sections] == [
        " Atlas/line\t",
        "Boreal:BLOCK",
        "cedar.literal/v2 ",
    ]
    assert [source.slice(section.span) for section in source.sections] == [
        "#a",
        "/*b*/",
        '"""c"""',
    ]
    assert [source.slice(region.span) for region in source.regions] == [
        "#a",
        " ",
        "x",
        " ",
        "/*b*/",
        " ",
        "y",
        " ",
        '"""c"""',
    ]
    assert source.reconstruct() == '#a x /*b*/ y """c"""'
    assert [(link.section, link.declaration) for link in source.documentation] == [
        (0, None),
        (1, 0),
        (2, 1),
    ]
    assert [source.slice(record.header) for record in source.declarations] == ["x", "y"]


@pytest.mark.parametrize(
    "text,span",
    [
        ("before\n## first\n\n\n## second\nafter", SourceSpan(7, 34)),
        ('#a x /*b*/ y """c"""', SourceSpan(13, 21)),
    ],
)
def test_section_rejects_whole_span_past_exact_source_boundary(text, span):
    with pytest.raises(ValueError, match=r"sections\[0\].*outside text"):
        SourceStructure(
            text,
            (SourceRegion(SourceSpan(0, len(text)), RegionKind.CODE),),
            (SourceSection(span, "atlas/whole"),),
            (),
            (),
        )


def ownership_structure(documentation):
    text = "module\n\nnotes\nfirst\nordinary\nsecond"
    return SourceStructure(
        text,
        (SourceRegion(SourceSpan(0, len(text)), RegionKind.COMMENT),),
        (
            SourceSection(SourceSpan(0, 13), "prose"),
            SourceSection(SourceSpan(14, 19), "prose"),
            SourceSection(SourceSpan(20, 28), "prose"),
            SourceSection(SourceSpan(29, 35), "prose"),
        ),
        (
            SourceDeclaration(SourceSpan(14, 19), 14, "first"),
            SourceDeclaration(SourceSpan(29, 35), 29, "second"),
        ),
        documentation,
    )


def test_ownership_module_first_and_distinct_declarations_preserve_links():
    links = (
        DocumentationOwner(0, None),
        DocumentationOwner(1, 0),
        DocumentationOwner(3, 1),
    )
    source = ownership_structure(links)
    assert source.documentation is links
    assert source.documentation[0].declaration is None
    assert source.documentation[1].declaration == 0
    assert source.documentation[2].declaration == 1
    assert source.slice(source.sections[0].span) == "module\n\nnotes"


def test_ownership_allows_ordinary_unowned_comments():
    source = ownership_structure(())
    assert len(source.sections) == 4
    assert source.documentation == ()


@pytest.mark.parametrize("field", ["section", "declaration"])
@pytest.mark.parametrize("value", [-1, True, False, 0.0, "0"])
def test_ownership_rejects_invalid_index_fields(field, value):
    values = {"section": 0, "declaration": None}
    values[field] = value
    with pytest.raises(ValueError, match=rf"documentation.*{field}.*{value}"):
        DocumentationOwner(**values)


def test_ownership_requires_section_index():
    with pytest.raises(ValueError, match=r"documentation.*section.*None"):
        DocumentationOwner(cast(Any, None), None)


@pytest.mark.parametrize(
    "link,field,index",
    [
        (DocumentationOwner(4, None), "section", 4),
        (DocumentationOwner(0, 2), "declaration", 2),
    ],
)
def test_ownership_rejects_unknown_section_or_owner(link, field, index):
    with pytest.raises(ValueError, match=rf"documentation\[0\].*{field}.*{index}"):
        ownership_structure((link,))


def test_ownership_rejects_duplicate_section():
    with pytest.raises(ValueError, match=r"documentation\[1\].*section.*0"):
        ownership_structure((DocumentationOwner(0, None), DocumentationOwner(0, 0)))


@pytest.mark.parametrize("owner", [None, 0, 1])
def test_ownership_rejects_duplicate_module_or_declaration_owner(owner):
    with pytest.raises(ValueError, match=rf"documentation\[1\].*owner.*{owner}"):
        ownership_structure(
            (DocumentationOwner(0, owner), DocumentationOwner(1, owner))
        )


def test_ownership_rejects_wrong_link_order():
    with pytest.raises(ValueError, match=r"documentation\[1\].*section.*0"):
        ownership_structure((DocumentationOwner(3, 1), DocumentationOwner(0, None)))


def boundary_structure():
    return SourceStructure(
        "item\n# note",
        (SourceRegion(SourceSpan(0, 11), RegionKind.CODE),),
        (SourceSection(SourceSpan(5, 11), "atlas/line"),),
        (SourceDeclaration(SourceSpan(0, 4), 0, "atlas/item"),),
        (DocumentationOwner(0, 0),),
    )


def test_boundary_all_source_record_and_container_fields_are_frozen():
    source = boundary_structure()
    records = (
        source,
        source.regions[0],
        source.sections[0],
        source.declarations[0],
        source.documentation[0],
        source.regions[0].span,
        source.position(0),
    )
    for record in records:
        for record_field in fields(record):
            with pytest.raises(FrozenInstanceError):
                setattr(record, record_field.name, None)
            with pytest.raises(FrozenInstanceError):
                delattr(record, record_field.name)


@pytest.mark.parametrize(
    "field", ["regions", "sections", "declarations", "documentation", "_line_starts"]
)
def test_boundary_source_collections_and_derived_line_starts_are_tuples(field):
    source = boundary_structure()
    collection = getattr(
        source._coordinates if field == "_line_starts" else source, field
    )
    assert isinstance(collection, tuple)
    assert collection
    with pytest.raises(TypeError):
        collection[0] = None
    with pytest.raises(AttributeError):
        collection.append(None)
    assert source._coordinates._line_starts == (0, 5)
    assert source.reconstruct() == "item\n# note"


@pytest.mark.parametrize(
    "field", ["regions", "sections", "declarations", "documentation"]
)
@pytest.mark.parametrize("empty", [False, True])
def test_boundary_constructor_rejects_mutable_list_collections(field, empty):
    source = boundary_structure()
    values: dict[str, Any] = {
        "text": source.text,
        "regions": source.regions,
        "sections": source.sections,
        "declarations": source.declarations,
        "documentation": source.documentation,
    }
    values[field] = [] if empty else list(values[field])
    with pytest.raises(ValueError, match=rf"^{field} must be a tuple$"):
        SourceStructure(**values)


def test_code_lines_carry_the_documentation_place_of_their_line():
    from comment_review.reading.source import CodeLine, DocPlace, lines_of_code

    code = {1: "def f(", 2: "):", 4: "    pass"}
    assert lines_of_code(code, {1: DocPlace(2, False)}) == [
        CodeLine(1, "def f(", DocPlace(2, False)),
        CodeLine(2, "):", None),
        CodeLine(4, "    pass", None),
    ]


@pytest.mark.parametrize(
    ("line", "at"), [(2, 2), (1, 3)], ids=["declaring-line", "documentation-line"]
)
def test_a_documentation_place_off_the_code_lines_is_refused(line, at):
    from comment_review.reading.source import DocPlace, lines_of_code

    with pytest.raises(ValueError, match="not a code line"):
        lines_of_code({1: "def f():", 4: "    pass"}, {line: DocPlace(at, False)})


def test_boundary_source_import_does_not_load_workflow_modules():
    src = Path(__file__).resolve().parents[1] / "src"
    script = """
import sys

sys.path.insert(0, sys.argv[1])
import comment_review.reading.source

forbidden = {"binder", "desk", "flows", "results", "lexer", "paragraph", "addresser"}
loaded = sorted(
    name for name in sys.modules
    if name.startswith("comment_review.")
    and forbidden.intersection(name.split("."))
)
assert not loaded, f"Source import loaded workflow modules: {loaded}"
"""
    result = subprocess.run(
        [sys.executable, "-I", "-c", script, str(src)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
