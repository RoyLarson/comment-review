"""Recognize logical Python lines using exact scanner tokens and layout rules."""

from collections.abc import Mapping
from typing import cast

from comment_review.reading.definitions import LanguageDefinition
from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage
from comment_review.reading.python.definition import validate_python
from comment_review.reading.python.records import LogicalLine, PythonScan
from comment_review.reading.source import SourceSpan


def logical_lines(
    scan: PythonScan, definition: LanguageDefinition
) -> tuple[LogicalLine, ...] | ReadFailure:
    """Join physical lines and validate indentation without compiling suites.

    Spans include the first physical line's indentation and the terminating
    newline, if present. Token indices exclude comments and joining markers.
    """
    failure = validate_python(definition)
    if failure is not None:
        return failure
    layout = cast(Mapping[str, object], definition.rules["layout"])
    pairs = dict(cast(tuple[tuple[str, str], ...], layout["implicit_pairs"]))
    closers = frozenset(pairs.values())
    brackets: list[tuple[str, SourceSpan]] = []
    lines: list[LogicalLine] = []
    levels = [(0, 0)]
    significant: list[int] = []
    start = 0
    line_start = 0
    indentation = (0, 0)
    indent_span = SourceSpan(0, 0)
    active = False
    continuation: SourceSpan | None = None
    awaiting_line: SourceSpan | None = None
    interpolation_depth = 0

    for index, token in enumerate(scan.tokens):
        if token.kind == "newline":
            if interpolation_depth:
                continuation = None
                line_start = token.span.end
                continue
            if continuation is not None:
                awaiting_line = continuation
                continuation = None
            else:
                awaiting_line = None
                if not brackets:
                    if significant:
                        failure = _check_indent(levels, indentation, indent_span)
                        if failure is not None:
                            return failure
                        lines.append(
                            LogicalLine(
                                SourceSpan(start, token.span.end),
                                tuple(significant),
                                indentation[0],
                            )
                        )
                    significant = []
                    active = False
            line_start = token.span.end
            continue
        awaiting_line = None
        if token.kind == "comment":
            continue
        if not active:
            start = line_start
            indentation, indent_span = _indentation(scan.text, start, layout)
            active = True
        spelling = scan.text[token.span.start : token.span.end]
        if token.kind == "interpolation_start":
            interpolation_depth += 1
        elif token.kind == "interpolation_end":
            interpolation_depth -= 1
        if token.kind == "continuation":
            if (
                spelling != layout["explicit_join"]
                or index + 1 == len(scan.tokens)
                or scan.tokens[index + 1].kind != "newline"
                or scan.tokens[index + 1].span.start != token.span.end
            ):
                return _failure("incomplete-continuation", token.span)
            continuation = token.span
            continue
        if token.kind == "operator":
            if spelling in pairs:
                brackets.append((pairs[spelling], token.span))
            elif spelling in closers:
                if not brackets or brackets[-1][0] != spelling:
                    return _failure("mismatched-bracket", token.span)
                brackets.pop()
        significant.append(index)

    if awaiting_line is not None and line_start == len(scan.text):
        return _failure("incomplete-continuation", awaiting_line)
    if brackets:
        return _failure("unfinished-join", brackets[-1][1])
    if significant:
        failure = _check_indent(levels, indentation, indent_span)
        if failure is not None:
            return failure
        lines.append(
            LogicalLine(
                SourceSpan(start, len(scan.text)), tuple(significant), indentation[0]
            )
        )
    return tuple(lines)


def _indentation(
    text: str, start: int, layout: Mapping[str, object]
) -> tuple[tuple[int, int], SourceSpan]:
    width = cast(int, layout["tab_width"])
    normal = alternate = 0
    end = start
    while end < len(text) and text[end] in " \t\f":
        char = text[end]
        if char == "\t":
            normal = (normal // width + 1) * width
            alternate += 1
        elif char == "\f" and layout["formfeed"] == "reset-leading":
            normal = alternate = 0
        else:
            normal += 1
            alternate += 1
        end += 1
    return (normal, alternate), SourceSpan(start, end)


def _check_indent(
    levels: list[tuple[int, int]], indentation: tuple[int, int], span: SourceSpan
) -> ReadFailure | None:
    normal, alternate = indentation
    if normal > levels[-1][0]:
        if alternate <= levels[-1][1]:
            return _failure("ambiguous-indentation", span)
        levels.append(indentation)
        return None
    while normal < levels[-1][0]:
        levels.pop()
    if normal != levels[-1][0]:
        return _failure("inconsistent-indentation", span)
    if alternate != levels[-1][1]:
        return _failure("ambiguous-indentation", span)
    return None


def _failure(code: str, span: SourceSpan) -> ReadFailure:
    return ReadFailure(
        (ReadDiagnostic(ReadStage.LEX, code, code.replace("-", " "), span),)
    )
