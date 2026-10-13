"""Project retained Python records into whole editable source sections."""

from comment_review.reading.coordinates import SourceCoordinates
from comment_review.reading.definitions import LanguageDefinition
from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage
from comment_review.reading.python.definition import validate_python
from comment_review.reading.python.records import (
    DocumentationPayload,
    ProtectedSource,
    PythonRead,
    PythonScan,
    PythonStructure,
)
from comment_review.reading.source import (
    DocumentationOwner,
    RegionKind,
    SourceRegion,
    SourceSection,
    SourceSpan,
    SourceStructure,
)


def sections_for(
    scan: PythonScan,
    structure: PythonStructure,
    documentation: tuple[DocumentationPayload, ...],
    definition: LanguageDefinition,
    directives: tuple[ProtectedSource, ...],
) -> PythonRead | ReadFailure:
    """Retain full statements, whole comment runs, and completed protection.

    Forms describe source syntax; paragraph adaptation owns address kinds.
    Editable comments inside documentation fail because their independent span
    overlaps the complete documentation statement required by PythonRead.
    """
    failure = validate_python(definition)
    if failure is not None:
        return failure
    protected = scan.protected + directives
    coordinates = SourceCoordinates(scan.text)
    comments: list[SourceSection] = []
    for token in scan.tokens:
        if token.kind != "comment":
            continue
        if any(
            token.span.start < item.span.end and item.span.start < token.span.end
            for item in protected
        ):
            continue
        if any(
            payload.expression.statement.start <= token.span.start
            and token.span.end <= payload.expression.statement.end
            for payload in documentation
        ):
            return ReadFailure(
                (
                    ReadDiagnostic(
                        ReadStage.PLACE,
                        "unsupported-documentation-comment",
                        "An editable comment inside documentation overlaps its "
                        "complete statement section",
                        token.span,
                    ),
                )
            )
        start = token.span.start
        line_start = start - coordinates.position(start).column
        if not scan.text[line_start:start].strip(" \t\f"):
            start = line_start
        end = token.span.end
        if scan.text.startswith("\r\n", end):
            end += 2
        elif end < len(scan.text) and scan.text[end] in "\r\n":
            end += 1
        if comments and not scan.text[comments[-1].span.end : start].strip(" \t\f\r\n"):
            start = comments.pop().span.start
        comments.append(SourceSection(SourceSpan(start, end), "#"))

    sections = tuple(
        sorted(
            (
                *comments,
                *(
                    SourceSection(payload.expression.statement, "docstring")
                    for payload in documentation
                ),
            ),
            key=lambda section: section.span.start,
        )
    )
    documentation_sections = {
        section.span: index
        for index, section in enumerate(sections)
        if section.form == "docstring"
    }
    owners = tuple(
        DocumentationOwner(
            documentation_sections[payload.expression.statement],
            payload.expression.declaration,
        )
        for payload in documentation
    )
    directive_spans = {item.span for item in directives}
    regions = (
        tuple(
            SourceRegion(region.span, RegionKind.DIRECTIVE)
            if region.kind == RegionKind.COMMENT and region.span in directive_spans
            else region
            for region in scan.regions
        )
        if directives
        else scan.regions
    )
    source = SourceStructure(
        scan.text, regions, sections, structure.declarations, owners
    )
    return PythonRead(
        source,
        scan.tokens,
        structure.suites,
        structure.statements,
        structure.facts,
        documentation,
        protected,
    )
