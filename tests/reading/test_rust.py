from dataclasses import replace

import pytest

from comment_review.reading.diagnostics import ReadDiagnostic, ReadStage
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


def test_records_placement_accepts_one_insertion_per_declaration():
    one = declaration()
    records.RustPlacement((one,), (1, 2), (records.DetachedRun(COMMENT, 0),))
    records.RustPlacement((), (1,), ())


@pytest.mark.parametrize(
    "insertions", [(1,), (1, 2, 3), (1, 3, 3), (1, 4, 3), (0, 2), (1, 0), (-1, 2)]
)
def test_records_placement_rejects_bad_insertions(insertions):
    with pytest.raises(ValueError):
        records.RustPlacement((declaration(),), insertions, ())


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


def test_records_read_holds_no_second_copy_of_the_text():
    result = read()
    assert not hasattr(result, "text")
    assert replace(result, protected=()).source is result.source
