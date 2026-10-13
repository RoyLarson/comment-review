"""Protect Python directive comments and their retained source attachments."""

import re
from codecs import lookup
from collections.abc import Mapping
from typing import cast

from comment_review.reading.coordinates import SourceCoordinates
from comment_review.reading.definitions import LanguageDefinition
from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage
from comment_review.reading.python.definition import validate_python
from comment_review.reading.python.records import (
    ProtectedSource,
    PythonScan,
    PythonStructure,
)
from comment_review.reading.source import SourceSpan


def directives_in(
    scan: PythonScan, structure: PythonStructure, definition: LanguageDefinition
) -> tuple[ProtectedSource, ...] | ReadFailure:
    """Retain whole comments, effective preamble placement, and source ownership.

    Preamble directives attach to source start. Inline type comments attach to
    retained statements; ignores attach to the significant source on their line.
    Standalone comments use function headers or the next owned token boundary.
    """
    failure = validate_python(definition)
    if failure is not None:
        return failure
    rules = cast(Mapping[str, object], definition.rules["directives"])
    comment_marker = cast(Mapping[str, object], definition.rules["comments"])["marker"]
    markers = cast(tuple[str, ...], rules["encoding_markers"])
    encoding_pattern = re.compile(
        "(?:"
        + "|".join(re.escape(marker) for marker in markers)
        + r")[ \t]*([-_.a-zA-Z0-9]+)"
    )
    coordinates = SourceCoordinates(scan.text)
    protected: list[ProtectedSource] = []
    encoding_found = False
    first_line_end = min(
        (token.span.start for token in scan.tokens if token.kind == "newline"),
        default=len(scan.text),
    )
    first_line = scan.text[:first_line_end].lstrip(" \t\f")
    second_allowed = rules[
        "encoding_second_line"
    ] == "comment-or-blank-first-line" and (
        not first_line or first_line.startswith(cast(str, comment_marker))
    )
    for token in scan.tokens:
        if token.kind != "comment":
            continue
        span = token.span
        text = scan.text[span.start : span.end]
        position = coordinates.position(span.start)
        line_start = span.start - position.column
        if (
            position.line == rules["shebang_line"]
            and position.column == rules["shebang_column"]
            and text.startswith(cast(str, rules["shebang"]))
        ):
            protected.append(ProtectedSource(span, "shebang", SourceSpan(0, 0)))
        if (
            not encoding_found
            and position.line in cast(tuple[int, ...], rules["encoding_lines"])
            and (position.line != 2 or second_allowed)
            and (
                not rules["encoding_own_line"]
                or not scan.text[line_start : span.start].strip(" \t\f")
            )
        ):
            match = encoding_pattern.search(text)
            if match is not None:
                encoding = match.group(1)
                try:
                    supported = lookup(encoding).name == "utf-8"
                except LookupError:
                    supported = False
                if not supported:
                    return ReadFailure(
                        (
                            ReadDiagnostic(
                                ReadStage.PLACE,
                                "unsupported-source-encoding",
                                f"Encoding cookie {encoding!r} is incompatible "
                                "with strict UTF-8 source I/O",
                                span,
                            ),
                        )
                    )
                protected.append(ProtectedSource(span, "encoding", SourceSpan(0, 0)))
                encoding_found = True
        body = text[len(cast(str, comment_marker)) :].lstrip(" \t")
        marker = cast(str, rules["type_marker"])
        if rules[
            "type_position"
        ] != "comment-start-after-whitespace" or not body.startswith(marker):
            continue
        payload = body[len(marker) :].lstrip(" \t")
        suffix = payload[len("ignore") :]
        ignored = payload.startswith("ignore") and (
            not suffix or (ord(suffix[0]) < 128 and not suffix[0].isalnum())
        )
        attachment = _type_attachment(scan, structure, span, line_start, ignored)
        protected.append(
            ProtectedSource(
                span, "type-ignore" if ignored else "type-comment", attachment
            )
        )
    return tuple(protected)


def _type_attachment(
    scan: PythonScan,
    structure: PythonStructure,
    comment: SourceSpan,
    line_start: int,
    ignored: bool,
) -> SourceSpan:
    owned = [
        (statement, scan.tokens[index].span)
        for statement in structure.statements
        for index in statement.tokens
    ]
    on_line = [
        (statement, span)
        for statement, span in owned
        if span.end > line_start and span.start < comment.start
    ]
    if on_line:
        if ignored:
            return SourceSpan(max(line_start, on_line[0][1].start), on_line[-1][1].end)
        statement = on_line[-1][0]
        if statement.span.end <= comment.start:
            return statement.span
        return SourceSpan(max(line_start, on_line[0][1].start), on_line[-1][1].end)
    containing = [
        suite
        for suite in structure.suites
        if suite.span.start <= comment.start < suite.span.end
    ]
    suite = min(containing, key=lambda item: item.span.end - item.span.start)
    if (
        not ignored
        and suite.kind in {"function", "async-function"}
        and suite.header is not None
        and (
            not suite.statements
            or comment.end <= structure.statements[suite.statements[0]].span.start
        )
    ):
        return suite.header
    following = [
        span.start
        for statement, span in owned
        if comment.end <= span.start <= suite.span.end
    ]
    boundary = min(following, default=suite.span.end)
    return SourceSpan(boundary, boundary)
