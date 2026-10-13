from dataclasses import FrozenInstanceError, replace
from importlib import import_module

import pytest

from comment_review.reading.diagnostics import ReadDiagnostic, ReadStage
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
