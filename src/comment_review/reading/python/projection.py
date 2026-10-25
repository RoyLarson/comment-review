"""Project retained Python records into whole editable source sections."""

from pathlib import Path

from comment_review import constants
from comment_review.reading.coordinates import SourceCoordinates
from comment_review.reading.definitions import LanguageDefinition
from comment_review.reading.diagnostics import ReadFailure
from comment_review.reading.paragraph import Paragraph
from comment_review.reading.python.definition import validate_python
from comment_review.reading.python.records import (
    DocumentationPayload,
    ProtectedSource,
    PythonPlacement,
    PythonRead,
    PythonScan,
)
from comment_review.reading.series import Kind
from comment_review.reading.source import (
    CodeLine,
    DocPlace,
    DocumentationOwner,
    RegionKind,
    SourceSection,
    SourceSpan,
    SourceStructure,
    lines_of_code,
)


def sections_for(
    scan: PythonScan,
    structure: PythonPlacement,
    documentation: tuple[DocumentationPayload, ...],
    definition: LanguageDefinition,
    directives: tuple[ProtectedSource, ...],
) -> PythonRead | ReadFailure:
    """Retain full statements, comment runs by placement, and completed protection.

    Forms describe source syntax; paragraph adaptation owns address kinds.
    Documentation owns enclosed and closing-line comments. Protection remains
    attached to exact source without removing comments from classification.
    """
    failure = validate_python(definition)
    if failure is not None:
        return failure
    protected = scan.protected + directives
    coordinates = SourceCoordinates(scan.text)
    comments: list[SourceSection] = []
    previous_whole = False
    for token in scan.tokens:
        if token.kind != "comment":
            continue
        if any(
            payload.expression.statement.start <= token.span.start
            and token.span.end <= payload.expression.statement.end
            for payload in documentation
        ):
            continue
        start = token.span.start
        line_start = start - coordinates.position(start).column
        whole = not scan.text[line_start:start].strip(" \t\f\ufeff")
        if whole:
            start = line_start
        end = token.span.end
        if scan.text.startswith("\r\n", end):
            end += 2
        elif end < len(scan.text) and scan.text[end] in "\r\n":
            end += 1
        if (
            comments
            and whole == previous_whole
            and not scan.text[comments[-1].span.end : start].strip(" \t\f\r\n")
        ):
            start = comments.pop().span.start
        comments.append(SourceSection(SourceSpan(start, end), "#"))
        previous_whole = whole

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
    source = SourceStructure(
        scan.text, scan.regions, sections, structure.declarations, owners
    )
    return PythonRead(source, documentation, protected)


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
                    anchor=before.rstrip() if trailing else "",
                    raw_lines=raw,
                )
            )
    return paragraphs


def code_lines_for(read: PythonRead) -> list[CodeLine]:
    """Each code line, with a docstring's place on the line that declares it.

    A docstring is set after the code line that ends its declaration's
    signature: the line its header's closing colon is on.
    """
    source = read.source
    return lines_of_code(
        _code(read),
        (
            (
                source.position(declaration.anchor).line,
                DocPlace(source.position(declaration.header.end - 1).line, False),
            )
            for declaration in source.declarations
        ),
    )


def _code(read: PythonRead) -> dict[int, str]:
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
