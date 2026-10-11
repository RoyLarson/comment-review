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
        ("sections", SourceSection(SourceSpan(0, 1), "sample")),
        ("declarations", SourceDeclaration(SourceSpan(0, 1), 0, "sample")),
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
    starts = source._line_starts
    assert starts == (0, 3, 5, 7)
    field = source.__dataclass_fields__["_line_starts"]
    assert not field.init
    assert not field.repr
    assert "_line_starts" not in repr(source)
    for _ in range(3):
        assert source.position(2) == SourcePosition(1, 2)
        assert source.position(7) == SourcePosition(4, 0)
        assert source._line_starts is starts
    with pytest.raises(FrozenInstanceError):
        source._line_starts = (0,)


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
        DocumentationOwner(None, None)


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
