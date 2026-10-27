"""Project retained Python records into whole editable source sections."""

from bisect import bisect_right
from pathlib import Path

from comment_review import constants
from comment_review.reading.coordinates import SourceCoordinates
from comment_review.reading.definitions import LanguageDefinition
from comment_review.reading.diagnostics import ReadFailure
from comment_review.reading.matter import file_matter
from comment_review.reading.paragraph import Paragraph
from comment_review.reading.python.definition import validate_python
from comment_review.reading.python.records import (
    DocumentationExpression,
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
    documentation: tuple[DocumentationExpression, ...],
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
            payload.statement.start <= token.span.start
            and token.span.end <= payload.statement.end
            for payload in documentation
        ):
            continue
        start = token.span.start
        line_start = start - coordinates.position(start).column
        whole = not scan.text[line_start:start].strip(
            " \t\f" + constants.BYTE_ORDER_MARK
        )
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
                    SourceSection(payload.statement, "docstring")
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
            documentation_sections[payload.statement],
            payload.declaration,
        )
        for payload in documentation
    )
    source = SourceStructure(
        scan.text, scan.regions, sections, structure.declarations, owners
    )
    return PythonRead(source, documentation, protected)


def paragraphs_for(path: Path, read: PythonRead) -> list[Paragraph] | ReadFailure:
    """Adapt retained sections, cutting comment runs only at file-matter edges.

    A comment section with code before it on its first line is TRAILING. Every
    other comment section is cut at the edges `reading.matter` gives, and each
    part is MATTER inside the file's own matter and COMMENT outside it.
    """
    text = read.source.text
    coordinates = SourceCoordinates(text)
    lines = constants.text_lines(text)
    # A Python shebang or encoding line is a comment, so the matter opens on
    # line 1.
    prose = _prose(read, coordinates)
    matter = file_matter(len(lines), 1, prose)
    payloads = {payload.statement: payload for payload in read.payloads}
    paragraphs: list[Paragraph] = []
    for section in read.source.sections:
        span = section.span
        first = coordinates.position(span.start)
        last = coordinates.position(max(span.start, span.end - 1))
        if section.form == "docstring":
            ordinal = payloads[span].declaration
            # None for the module's own docstring.
            declaring = (
                None
                if ordinal is None
                else read.source.declaring_line(read.source.declarations[ordinal])
            )
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
                    anchor_line=declaring,
                    raw_lines=constants.text_lines(text[raw_start : span.end]),
                )
            )
            continue
        before = lines[first.line - 1][: first.column]
        if before.strip(" \t\f" + constants.BYTE_ORDER_MARK):
            raw = lines[first.line - 1 : last.line]
            raw[0] = raw[0][len(before.rstrip()) :]
            paragraphs.append(
                Paragraph(
                    path.as_posix(),
                    first.line,
                    last.line,
                    Kind.TRAILING,
                    anchor=before.rstrip(),
                    raw_lines=raw,
                )
            )
            continue
        for start, end, is_matter in matter.parts(first.line, last.line, prose):
            paragraphs.append(
                Paragraph(
                    path.as_posix(),
                    start,
                    end,
                    Kind.MATTER if is_matter else Kind.COMMENT,
                    raw_lines=lines[start - 1 : end],
                )
            )
    return paragraphs


def _prose(read: PythonRead, coordinates: SourceCoordinates) -> set[int]:
    """The prose lines, for `reading.matter`: each line a whole-line comment is on.

    A docstring is a statement, so no comment is documentation.
    """
    text = read.source.text
    spans = [s.span for s in read.source.sections if s.form == "#"]
    starts = [span.start for span in spans]
    prose: set[int] = set()
    for region in read.source.regions:
        if region.kind != RegionKind.COMMENT:
            continue
        at = bisect_right(starts, region.span.start) - 1
        if at < 0 or region.span.start >= spans[at].end:
            continue
        position = coordinates.position(region.span.start)
        head = text[region.span.start - position.column : region.span.start]
        if not head.strip(" \t\f" + constants.BYTE_ORDER_MARK):
            prose.add(position.line)
    return prose


def code_lines_for(read: PythonRead) -> list[CodeLine]:
    """Each code line, with a docstring's place on the line that declares it.

    A docstring is set after the code line that ends its declaration's
    signature: the line its header's closing colon is on.
    """
    source = read.source
    declared: dict[int, DocPlace] = {}
    for declaration in source.declarations:
        declared[source.declaring_line(declaration)] = DocPlace(
            source.position(declaration.header.end - 1).line, False
        )
    return lines_of_code(_code(read), declared)


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
        if anchor.strip(" \t\f" + constants.BYTE_ORDER_MARK):
            code[number] = anchor
        offset = end
        if text.startswith("\r\n", offset):
            offset += 2
        elif offset < len(text) and text[offset] in "\r\n":
            offset += 1
    return code
