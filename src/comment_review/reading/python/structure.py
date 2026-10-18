"""Place documentation cues over preserved Python source boundaries."""

from collections.abc import Mapping
from typing import cast

from comment_review.reading.definitions import LanguageDefinition
from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage
from comment_review.reading.python.definition import validate_python
from comment_review.reading.python.records import (
    LogicalLine,
    PythonPlacement,
    PythonScan,
)
from comment_review.reading.source import SourceDeclaration, SourceSpan


def logical_lines(
    scan: PythonScan, definition: LanguageDefinition
) -> tuple[LogicalLine, ...] | ReadFailure:
    """Read continued physical lines with literal and interpolation text opaque.

    Spans include the first physical line's indentation and the terminating
    newline, if present. Token indices exclude comments and continuation markers.
    """
    failure = validate_python(definition)
    if failure is not None:
        return failure
    layout = cast(Mapping[str, object], definition.rules["layout"])
    pairs = dict(cast(tuple[tuple[str, str], ...], layout["implicit_pairs"]))
    closers = frozenset(pairs.values())
    brackets: list[tuple[str, SourceSpan]] = []
    lines: list[LogicalLine] = []
    significant: list[int] = []
    start = 0
    line_start = 0
    indentation = 0
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
                        lines.append(
                            LogicalLine(
                                SourceSpan(start, token.span.end),
                                tuple(significant),
                                indentation,
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
            indentation = _indentation(scan.text, start, layout)
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
        if token.kind == "boundary":
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
        return _failure("unfinished-continuation", brackets[-1][1])
    if significant:
        lines.append(
            LogicalLine(
                SourceSpan(start, len(scan.text)), tuple(significant), indentation
            )
        )
    return tuple(lines)


def _indentation(text: str, start: int, layout: Mapping[str, object]) -> int:
    """Read leading source spacing only for declaration/documentation placement."""
    width = cast(int, layout["tab_width"])
    indent = 0
    end = 1 if start == 0 and text.startswith("\ufeff") else start
    while end < len(text) and text[end] in " \t\f":
        char = text[end]
        if char == "\t":
            indent = (indent // width + 1) * width
        elif char == "\f" and layout["formfeed"] == "reset-leading":
            indent = 0
        else:
            indent += 1
        end += 1
    return indent


def _failure(code: str, span: SourceSpan) -> ReadFailure:
    return ReadFailure(
        (ReadDiagnostic(ReadStage.LEX, code, code.replace("-", " "), span),)
    )


def outer_boundaries(
    scan: PythonScan, tokens: tuple[int, ...], *, include_code: bool = False
) -> tuple[int, ...]:
    """Locate unshielded punctuation and optionally its coarse source-code spans."""
    depth = interpolation = 0
    outer: list[int] = []
    for index in tokens:
        token = scan.tokens[index]
        if token.kind == "interpolation_start":
            interpolation += 1
        elif token.kind == "interpolation_end":
            interpolation -= 1
        elif not interpolation and token.kind == "boundary":
            spelling = scan.text[token.span.start : token.span.end]
            if spelling in "([{":
                depth += 1
            elif spelling in ")]}":
                depth -= 1
            elif not depth:
                outer.append(index)
        elif include_code and not interpolation and not depth and token.kind == "code":
            outer.append(index)
    return tuple(outer)


def place_declarations(
    scan: PythonScan,
    lines: tuple[LogicalLine, ...],
    definition: LanguageDefinition,
) -> PythonPlacement | ReadFailure:
    """Keep declaration headers and their first source positions, without a tree."""
    import re

    failure = validate_python(definition)
    if failure is not None:
        return failure
    rules = cast(Mapping[str, object], definition.rules["declarations"])
    keywords = cast(tuple[str, ...], rules["keywords"])
    asynchronous = cast(str, rules["async_keyword"])
    whitespace = r"(?:[ \t\f]|\\(?:\r\n|\r|\n))+"
    prefix = re.compile(
        rf"(?:(?P<async>{re.escape(asynchronous)}){whitespace})?"
        rf"(?P<keyword>{'|'.join(re.escape(word) for word in keywords)}){whitespace}"
    )
    # Keep neighboring non-ASCII spelling opaque without validating identifiers.
    lambda_keyword = re.compile(
        r"(?<![a-zA-Z0-9_\x80-\U0010ffff])lambda"
        r"(?![a-zA-Z0-9_\x80-\U0010ffff])"
    )
    declarations: list[SourceDeclaration] = []
    insertions = [scan.tokens[lines[0].tokens[0]].span.start if lines else 0]
    delimiter = cast(Mapping[str, object], definition.rules["layout"])[
        "suite_delimiter"
    ]
    for position, line in enumerate(lines):
        first = scan.tokens[line.tokens[0]]
        if first.kind != "code":
            continue
        match = prefix.match(scan.text, first.span.start, line.span.end)
        if match is None:
            continue
        colon = None
        annotation = False
        pending_colons = 0
        for index in outer_boundaries(scan, line.tokens, include_code=True):
            token = scan.tokens[index]
            spelling = scan.text[token.span.start : token.span.end]
            if token.kind == "code":
                if not annotation and "->" in spelling:
                    annotation = True
                    spelling = spelling.split("->", 1)[1]
                if annotation:
                    # An unparenthesized lambda annotation owns its next colon.
                    pending_colons += len(lambda_keyword.findall(spelling))
            elif spelling == delimiter:
                if pending_colons:
                    pending_colons -= 1
                else:
                    colon = index
                    break
        if colon is None:
            continue
        header = SourceSpan(first.span.start, scan.tokens[colon].span.end)
        kind = "class" if match["keyword"] == "class" else "function"
        if match["async"]:
            kind = "async-" + kind
        declarations.append(SourceDeclaration(header, header.start, kind))
        following = [index for index in line.tokens if index > colon]
        if following:
            insertion = scan.tokens[following[0]].span.start
        elif position + 1 < len(lines) and lines[position + 1].indent > line.indent:
            insertion = scan.tokens[lines[position + 1].tokens[0]].span.start
        else:
            insertion = line.span.end
        insertions.append(insertion)
    return PythonPlacement(lines, tuple(declarations), tuple(insertions))
