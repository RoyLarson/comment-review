"""Protect Python directive comments and their retained source attachments."""

import re
from codecs import lookup
from collections.abc import Mapping
from typing import cast

from comment_review import constants
from comment_review.reading.coordinates import SourceCoordinates
from comment_review.reading.definitions import LanguageDefinition
from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage
from comment_review.reading.python.definition import validate_python
from comment_review.reading.python.records import (
    ProtectedSource,
    PythonPlacement,
    PythonScan,
)
from comment_review.reading.python.structure import outer_boundaries
from comment_review.reading.source import SourceSpan


def directives_in(
    scan: PythonScan, structure: PythonPlacement, definition: LanguageDefinition
) -> tuple[ProtectedSource, ...] | ReadFailure:
    """Retain whole comments, effective preamble placement, and source ownership.

    Preamble directives attach to source start. Inline type comments attach to
    joined source boundaries; ignores attach to significant source on their line.
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
    preamble_start = 1 if scan.text.startswith(constants.BYTE_ORDER_MARK) else 0
    first_line = scan.text[preamble_start:first_line_end].lstrip(" \t\f")
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
                or not scan.text[max(line_start, preamble_start) : span.start].strip(
                    " \t\f"
                )
            )
        ):
            match = encoding_pattern.search(text)
            if match is not None:
                encoding = match.group(1)
                normalized = encoding[:12].lower().replace("_", "-")
                codec_name = (
                    "utf-8"
                    if normalized == "utf-8" or normalized.startswith("utf-8-")
                    else encoding
                )
                try:
                    supported = lookup(codec_name).name == "utf-8"
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
    structure: PythonPlacement,
    comment: SourceSpan,
    line_start: int,
    ignored: bool,
) -> SourceSpan:
    significant = [
        token
        for token in scan.tokens
        if token.kind not in {"comment", "newline", "continuation"}
    ]
    on_line = [
        token.span
        for token in significant
        if token.span.end > line_start and token.span.start < comment.start
    ]
    if on_line:
        physical = SourceSpan(max(line_start, on_line[0].start), on_line[-1].end)
        if ignored:
            return physical
        line = next(
            line
            for line in structure.lines
            if line.span.start <= comment.start < line.span.end
        )
        preceding = tuple(
            index
            for index in line.tokens
            if scan.tokens[index].span.end <= comment.start
        )
        following = next(
            (
                index
                for index in line.tokens
                if scan.tokens[index].span.start >= comment.end
            ),
            None,
        )
        if following is not None:
            return physical
        separators = [
            index
            for index in outer_boundaries(scan, preceding)
            if scan.text[scan.tokens[index].span.start : scan.tokens[index].span.end]
            == ";"
        ]
        if separators:
            preceding = tuple(index for index in preceding if index > separators[-1])
        if preceding:
            return SourceSpan(
                scan.tokens[preceding[0]].span.start,
                scan.tokens[preceding[-1]].span.end,
            )
        return physical
    if not ignored:
        for declaration, insertion in reversed(
            tuple(zip(structure.declarations, structure.insertions, strict=True))
        ):
            if (
                declaration.kind in {"function", "async-function"}
                and declaration.header.end <= comment.start < insertion
            ):
                return declaration.header
    boundary = min(
        (token.span.start for token in significant if token.span.start >= comment.end),
        default=len(scan.text),
    )
    return SourceSpan(boundary, boundary)
