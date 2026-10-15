"""Compare retained Python source while excluding narrowly editable prose."""

from collections.abc import Collection, Iterator
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
    before: PythonRead | ReadFailure,
    after: PythonRead | ReadFailure,
    *,
    allowed_documentation_owners: Collection[int | None] = (),
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

    Selected source owners (None for the module, otherwise a declaration index)
    may add or remove whole documentation expressions. A later ordinary literal
    promoted by removal must still match its original exact executable source.
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
    if any(
        owner is not None
        and (
            not isinstance(owner, int)
            or isinstance(owner, bool)
            or not 0 <= owner < len(before.source.declarations)
            or owner >= len(after.source.declarations)
        )
        for owner in allowed_documentation_owners
    ):
        return _changed(
            "documentation-owner-missing", "Requested source owner does not exist"
        )
    selected = frozenset(allowed_documentation_owners)
    removed = frozenset(
        index
        for index, payload in enumerate(before.payloads)
        if payload.expression.declaration in selected
    )
    was = _project(before, removed)
    candidates = frozenset(
        index
        for index, payload in enumerate(after.payloads)
        if payload.expression.declaration in selected
    )
    now_removed = frozenset()
    if candidates:
        retained = _project(after, literal_documentation=candidates)
        choices = _correspondence(was, after, retained, candidates)
        if len(choices) != 1:
            return _changed(
                "code-changed",
                "Documentation has no unique retained source correspondence",
            )
        now = _project(after, choices[0], candidates - choices[0])
        now_removed = choices[0]
    else:
        now = _project(after)
    if was.units != now.units:
        return _changed(
            "code-changed",
            "Retained executable source or documentation ownership changed",
        )
    if _declarations(before, was) != _declarations(after, now):
        return _changed(
            "declaration-changed", "Retained declaration source context changed"
        )
    if _protection(before, was, removed) != _protection(after, now, now_removed):
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


def _documentation_span(read: PythonRead, index: int) -> SourceSpan:
    """Include only the acquired expression and its otherwise empty line trivia."""
    text = read.source.text
    statement = read.payloads[index].expression.statement
    start, end = statement.start, statement.end
    line_start = max(text.rfind("\n", 0, start), text.rfind("\r", 0, start)) + 1
    line_end = end
    while line_end < len(text) and text[line_end] not in "\r\n":
        line_end += 1
    if not text[end:line_end].strip(_HORIZONTAL):
        end = line_end
        if not text[line_start:start].strip(_HORIZONTAL):
            start = line_start
            if end < len(text):
                end += 2 if text.startswith("\r\n", end) else 1
        else:
            while start > line_start and text[start - 1] in _HORIZONTAL:
                start -= 1
    else:
        while end < line_end and text[end] in _HORIZONTAL:
            end += 1
    return SourceSpan(start, end)


def _correspondence(
    before: _Projection,
    after: PythonRead,
    retained: _Projection,
    candidates: frozenset[int],
) -> tuple[frozenset[int], ...]:
    """Match exact units with optional acquired documentation spans; cap ambiguity."""
    bounded = before.units + (("line", ""),)
    states: dict[int, set[frozenset[int]]] = {0: {frozenset()}}
    previous = 0
    for index in sorted(candidates):
        span = _documentation_span(after, index)
        start, end = retained.offsets[span.start], retained.offsets[span.end]
        fixed = retained.units[previous:start]
        optional = retained.units[start:end]
        following: dict[int, set[frozenset[int]]] = {}
        for position, paths in states.items():
            if bounded[position : position + len(fixed)] != fixed:
                continue
            position += len(fixed)
            skipped = following.setdefault(position, set())
            skipped.update(path | {index} for path in paths)
            if len(skipped) > 2:
                following[position] = set(tuple(skipped)[:2])
            if bounded[position : position + len(optional)] == optional:
                position += len(optional)
                kept = following.setdefault(position, set())
                kept.update(paths)
                if len(kept) > 2:
                    following[position] = set(tuple(kept)[:2])
        states = following
        previous = end
    suffix = retained.units[previous:]
    results: set[frozenset[int]] = set()
    for position, paths in states.items():
        remainder = before.units[position:]
        if suffix == remainder or suffix == bounded[position:]:
            results.update(paths)
            if len(results) > 1:
                break
    return tuple(results)


def _project(
    read: PythonRead,
    removed: frozenset[int] = frozenset(),
    literal_documentation: frozenset[int] = frozenset(),
) -> _Projection:
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
    for index, payload in enumerate(read.payloads):
        if index in removed:
            span = _documentation_span(read, index)
            keep[span.start : span.end] = [False] * (span.end - span.start)
            exact[span.start : span.end] = [False] * (span.end - span.start)
            line_start = (
                max(text.rfind("\n", 0, span.start), text.rfind("\r", 0, span.start))
                + 1
            )
            if line_start < span.start and not text[line_start : span.start].strip(
                _HORIZONTAL
            ):
                # A retained suffix still uses the expression's opening indentation.
                exact[line_start : span.start] = [True] * (span.start - line_start)
            continue
        if index in literal_documentation:
            continue
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


def _protection(
    read: PythonRead, projection: _Projection, removed: frozenset[int] = frozenset()
) -> tuple:
    envelopes: _Projection | None = None

    def context(
        span: SourceSpan, chosen: _Projection = projection, origin: int = 0
    ) -> tuple:
        start, end = chosen.offsets[span.start], chosen.offsets[span.end]
        return start - origin, end - origin, chosen.units[start:end]

    def documentation_context(span: SourceSpan, attachment: SourceSpan | None) -> tuple:
        """Keep protected placement inside erased docs while masking their prose."""
        nonlocal envelopes
        evidence = []
        for index in sorted(removed):
            expression = read.payloads[index].expression
            statement = expression.statement
            if not any(
                other is not None
                and other.start < statement.end
                and (
                    statement.start < other.end
                    or other.start == other.end == statement.start
                )
                for other in (span, attachment)
            ):
                continue
            if envelopes is None:
                envelopes = _project(read)
            origin = envelopes.offsets[statement.start]
            evidence.append(
                (
                    expression.declaration,
                    context(statement, envelopes, origin),
                    context(span, envelopes, origin),
                    None
                    if attachment is None
                    else context(attachment, envelopes, origin),
                )
            )
        return tuple(evidence)

    return tuple(
        (
            item.kind,
            read.source.slice(item.span),
            context(item.span),
            None if item.attachment is None else context(item.attachment),
            documentation_context(item.span, item.attachment),
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
