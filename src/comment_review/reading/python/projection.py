"""Project retained Python records into whole editable source sections."""

import re
from pathlib import Path

from comment_review import constants
from comment_review.reading.coordinates import SourceCoordinates
from comment_review.reading.definitions import LanguageDefinition
from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage
from comment_review.reading.paragraph import Paragraph
from comment_review.reading.python.definition import validate_python
from comment_review.reading.python.records import (
    DocumentationPayload,
    ProtectedSource,
    PythonRead,
    PythonScan,
    PythonStructure,
)
from comment_review.reading.series import Kind
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
    module = structure.suites[0]
    module_insertion = (
        structure.statements[module.statements[0]].span.start
        if module.statements
        else 0
    )
    declaration_insertions = {
        fact.declaration: fact.insertion for fact in structure.facts
    }
    insertions = (
        module_insertion,
        *(declaration_insertions[index] for index in range(len(source.declarations))),
    )
    return PythonRead(source, documentation, protected, insertions)


def paragraphs_for(path: Path, read: PythonRead) -> list[Paragraph] | ReadFailure:
    """Adapt retained sections, splitting comment runs only at file-matter edges."""
    text = read.source.text
    coordinates = SourceCoordinates(text)
    lines = constants.text_lines(text)
    payloads = {payload.expression.statement: payload for payload in read.payloads}
    paragraphs: list[Paragraph] = []
    for section in read.source.sections:
        span = section.span
        first = coordinates.position(span.start)
        last = coordinates.position(max(span.start, span.end - 1))
        if section.form == "docstring":
            payload = payloads[span]
            ordinal = payload.expression.declaration
            line_start = span.start - first.column
            raw_start = (
                line_start
                if not text[line_start : span.start].strip(" \t\f")
                else span.start
            )
            paragraphs.append(
                Paragraph(
                    path.as_posix(),
                    first.line,
                    last.line,
                    Kind.DOCSTRING,
                    last.line - first.line + 1,
                    payload.text,
                    address=f"a{0 if ordinal is None else ordinal + 1}",
                    raw_lines=constants.text_lines(text[raw_start : span.end]),
                )
            )
            continue
        comments = [
            region
            for region in read.source.regions
            if region.kind == RegionKind.COMMENT
            and span.start <= region.span.start < span.end
        ]
        groups = [comments]
        first_comment = coordinates.position(comments[0].span.start)
        first_whole = not lines[first_comment.line - 1][: first_comment.column].strip(
            " \t\f\ufeff"
        )
        if first_whole and first.line == 1:
            split = next(
                (
                    i
                    for i in range(1, len(comments))
                    if coordinates.position(comments[i].span.start).line
                    > coordinates.position(comments[i - 1].span.start).line + 1
                ),
                None,
            )
            if split is not None:
                groups = [comments[:split], comments[split:]]
        tail = groups[-1]
        tail_start = coordinates.position(tail[0].span.start)
        tail_whole = not lines[tail_start.line - 1][: tail_start.column].strip(
            " \t\f\ufeff"
        )
        if tail_whole and coordinates.position(tail[-1].span.start).line == len(lines):
            split = next(
                (
                    i
                    for i in range(len(tail) - 1, 0, -1)
                    if coordinates.position(tail[i].span.start).line
                    > coordinates.position(tail[i - 1].span.start).line + 1
                ),
                None,
            )
            if split is not None:
                groups[-1:] = [tail[:split], tail[split:]]
        for group in groups:
            start = coordinates.position(group[0].span.start)
            end = coordinates.position(group[-1].span.end)
            before = lines[start.line - 1][: start.column]
            trailing = bool(before.strip(" \t\f\ufeff"))
            kind = Kind.TRAILING if trailing else Kind.COMMENT
            if not trailing and (start.line == 1 or end.line == len(lines)):
                kind = Kind.MATTER
            raw = lines[start.line - 1 : end.line]
            if trailing:
                raw[0] = raw[0][len(before.rstrip()) :]
            paragraphs.append(
                Paragraph(
                    path.as_posix(),
                    start.line,
                    end.line,
                    kind,
                    len(raw),
                    re.sub(
                        r"\s+",
                        " ",
                        " ".join(
                            text[region.span.start + 1 : region.span.end].strip()
                            for region in group
                        ),
                    ).strip(),
                    anchor=before.rstrip() if trailing else "",
                    raw_lines=raw,
                )
            )
    return paragraphs


def code_for(read: PythonRead) -> dict[int, str]:
    """Project place anchors from executable text and trailing-comment context."""
    text = read.source.text
    sections = read.source.sections
    code: dict[int, str] = {}
    offset = 0
    for number, line in enumerate(constants.text_lines(text), 1):
        end = offset + len(line)
        spans = [
            section.span
            for section in sections
            if section.span.start < end and offset < section.span.end
        ]
        chunks = []
        boundary = offset
        for span in spans:
            chunks.append(text[boundary : max(boundary, span.start)])
            boundary = min(end, span.end)
        chunks.append(text[boundary:end])
        anchor = "".join(chunks).rstrip()
        if not anchor.strip(" \t\f\ufeff"):
            # A documentation-only line can still anchor its separate c place.
            # Its retained comment boundary preserves the physical prefix without
            # assigning the documentation's characters to the comment section.
            trailing = next(
                (
                    section.span.start
                    for section in sections
                    if section.form == "#" and offset < section.span.start < end
                ),
                None,
            )
            if trailing is not None:
                anchor = text[offset:trailing].rstrip()
        if anchor.strip(" \t\f\ufeff"):
            code[number] = anchor
        offset = end
        if text.startswith("\r\n", offset):
            offset += 2
        elif offset < len(text) and text[offset] in "\r\n":
            offset += 1
    return code


def declarations_for(read: PythonRead) -> list[tuple[int, int, bool]]:
    """Translate retained declaration and insertion offsets into page coordinates."""
    source = read.source
    return [
        (0, source.position(read.insertions[0]).line, False),
        *(
            (
                source.position(declaration.anchor).line,
                source.position(insertion).line,
                False,
            )
            for declaration, insertion in zip(
                source.declarations, read.insertions[1:], strict=True
            )
        ),
    ]
