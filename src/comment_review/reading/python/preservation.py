"""Compare retained Python source while excluding narrowly editable prose."""

from collections.abc import Iterator
from dataclasses import dataclass

from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage
from comment_review.reading.python.records import PreservationResult, PythonRead
from comment_review.reading.source import RegionKind, SourceSpan

_HORIZONTAL = " \t\f"


@dataclass(frozen=True)
class _Projection:
    units: tuple[tuple[str, str], ...]
    offsets: tuple[int, ...]


def compare_preservation(
    before: PythonRead | ReadFailure, after: PythonRead | ReadFailure
) -> PreservationResult:
    """Compare acquired reads without interpreting or reacquiring their code.

    Ordinary comments, blank physical lines, and trailing horizontal whitespace
    may change. Other code whitespace remains significant. Code line endings
    share one boundary marker, with an optional final boundary; literal and
    protected source characters remain exact. Existing documentation literal
    envelopes become owner markers, preserving their presence and code position.

    Protected attachments compare their retained source context and position,
    allowing ordinary prose inside the attachment to change. Read failures
    retain their diagnostics and never produce a successful comparison.
    """
    failures = tuple(
        diagnostic
        for read in (before, after)
        if isinstance(read, ReadFailure)
        for diagnostic in read.diagnostics
    )
    if failures:
        return PreservationResult(False, failures)
    assert isinstance(before, PythonRead) and isinstance(after, PythonRead)
    was, now = _project(before), _project(after)
    if was.units != now.units:
        return _changed(
            "code-changed",
            "Retained executable source or documentation ownership changed",
        )
    if _declarations(before, was) != _declarations(after, now):
        return _changed(
            "declaration-changed", "Retained declaration source context changed"
        )
    if _protection(before, was) != _protection(after, now):
        return _changed(
            "protected-source-changed",
            "Protected source text or its retained attachment changed",
        )
    return PreservationResult(True, ())


def _changed(code: str, message: str) -> PreservationResult:
    return PreservationResult(False, (ReadDiagnostic(ReadStage.PLACE, code, message),))


def _physical_lines(text: str) -> Iterator[tuple[int, int, int]]:
    start = 0
    while start < len(text):
        end = start
        while end < len(text) and text[end] not in "\r\n":
            end += 1
        following = end
        if following < len(text):
            following += 2 if text.startswith("\r\n", end) else 1
        yield start, end, following
        start = following


def _project(read: PythonRead) -> _Projection:
    text = read.source.text
    keep = [True] * len(text)
    exact = [False] * len(text)
    comments: list[SourceSpan] = []
    for region in read.source.regions:
        start, end = region.span.start, region.span.end
        if region.kind == RegionKind.COMMENT:
            keep[start:end] = [False] * (end - start)
            comments.append(region.span)
        elif region.kind in (RegionKind.LITERAL, RegionKind.DIRECTIVE):
            exact[start:end] = [True] * (end - start)
    for protected in read.protected:
        start, end = protected.span.start, protected.span.end
        keep[start:end] = [True] * (end - start)
        exact[start:end] = [True] * (end - start)
    ordinary_comments = [
        comment for comment in comments if not any(exact[comment.start : comment.end])
    ]
    documentation: dict[int, str] = {}
    documentation_ends: set[int] = set()
    for payload in read.payloads:
        expression = payload.expression
        start, end = expression.components[0].start, expression.components[-1].end
        keep[start:end] = [False] * (end - start)
        exact[start:end] = [False] * (end - start)
        documentation[start] = str(expression.declaration)
        documentation_ends.add(end - 1)
    for comment in ordinary_comments:
        cursor = comment.start
        while cursor and text[cursor - 1] in _HORIZONTAL and not exact[cursor - 1]:
            cursor -= 1
            keep[cursor] = False
    newlines: dict[int, int] = {}
    for start, end, following in _physical_lines(text):
        cursor = end
        while (
            cursor > start and text[cursor - 1] in _HORIZONTAL and not exact[cursor - 1]
        ):
            cursor -= 1
            keep[cursor] = False
        visible = any(
            offset in documentation
            or offset in documentation_ends
            or (keep[offset] and (exact[offset] or text[offset] not in _HORIZONTAL))
            for offset in range(start, end)
        )
        if not visible and not any(exact[end:following]):
            keep[start:following] = [False] * (following - start)
        if end < following and not any(exact[end:following]):
            newlines[end] = following
    units: list[tuple[str, str]] = []
    offsets: list[int] = []
    normalized_end = -1
    for offset, character in enumerate(text):
        offsets.append(len(units))
        if offset in documentation:
            units.append(("documentation", documentation[offset]))
        if not keep[offset] or offset < normalized_end:
            continue
        if offset in newlines:
            units.append(("line", ""))
            normalized_end = newlines[offset]
        else:
            units.append(("source", character))
    offsets.append(len(units))
    if units and units[-1][0] == "line":
        units.pop()
        offsets = [min(offset, len(units)) for offset in offsets]
    return _Projection(tuple(units), tuple(offsets))


def _protection(read: PythonRead, projection: _Projection) -> tuple:
    def context(span: SourceSpan) -> tuple:
        start, end = projection.offsets[span.start], projection.offsets[span.end]
        return start, end, projection.units[start:end]

    return tuple(
        (
            item.kind,
            read.source.slice(item.span),
            context(item.span),
            None if item.attachment is None else context(item.attachment),
        )
        for item in read.protected
    )


def _declarations(read: PythonRead, projection: _Projection) -> tuple:
    return tuple(
        (
            declaration.kind,
            projection.offsets[declaration.header.start],
            projection.offsets[declaration.header.end],
            projection.offsets[declaration.anchor],
        )
        for declaration in read.source.declarations
    )
