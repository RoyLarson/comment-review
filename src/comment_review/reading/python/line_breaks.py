"""Break the line where Python code shares it with a docstring.

A docstring sharing its physical line with code cannot grow without moving
that code, so the read sets the docstring and the code after it on lines of
their own before any place is assigned:

    def fn(): "Doc."; y = 42        def fn():
                                        "Doc."
                                        y = 42

    '''Doc.'''; y = 42              '''Doc.'''
                                    y = 42

Python admits only simple statements after a `;` or a one-line suite's `:`,
so a broken line sits at most one level below its header. That level is the
file's own first indent step, or four spaces in a file that indents nothing.
"""

from collections.abc import Mapping
from itertools import pairwise
from typing import cast

from comment_review import constants
from comment_review.reading.definitions import LanguageDefinition
from comment_review.reading.python.records import (
    DocumentationExpression,
    LogicalLine,
    PythonPlacement,
    PythonScan,
)

FALLBACK_STEP = "    "
_BLANK = " \t\f"


def broken_lines(
    scan: PythonScan,
    structure: PythonPlacement,
    expressions: tuple[DocumentationExpression, ...],
    definition: LanguageDefinition,
) -> str | None:
    """Return the source with every shared docstring line broken, or None if none is."""
    layout = cast(Mapping[str, object], definition.rules["layout"])
    separator = cast(str, layout["statement_separator"])
    text = scan.text
    newline = _newline(text)
    edits: list[tuple[int, int, str]] = []
    for expression in expressions:
        statement = expression.statement
        line = next(
            line
            for line in structure.lines
            if line.span.start <= statement.start < line.span.end
        )
        indent = _leading(text, line.span.start)
        if expression.declaration is not None and _after_code(text, statement.start):
            header = structure.declarations[expression.declaration].header
            indent += _step(text, structure.lines)
            edits.append((header.end, statement.start, newline + indent))
        following = [
            scan.tokens[index]
            for index in line.tokens
            if scan.tokens[index].span.start >= statement.end
        ]
        if not following:
            continue
        mark = next(
            scan.tokens[index]
            for index in line.tokens
            if scan.tokens[index].span.end == statement.end
        )
        assert text[mark.span.start : mark.span.end] == separator
        start = mark.span.start
        while start > statement.start and text[start - 1] in _BLANK:
            start -= 1
        edits.append((start, following[0].span.start, newline + indent))
    if not edits:
        return None
    for start, end, replacement in sorted(edits, reverse=True):
        text = text[:start] + replacement + text[end:]
    return text


def _leading(text: str, start: int) -> str:
    """The indentation opening the physical line at `start`."""
    if start == 0 and text.startswith(constants.BYTE_ORDER_MARK):
        start = 1
    end = start
    while end < len(text) and text[end] in _BLANK:
        end += 1
    return text[start:end]


def _after_code(text: str, position: int) -> bool:
    """Whether source text precedes `position` on its physical line."""
    line_start = max(text.rfind("\n", 0, position), text.rfind("\r", 0, position)) + 1
    return bool(text[line_start:position].strip(_BLANK + constants.BYTE_ORDER_MARK))


def _step(text: str, lines: tuple[LogicalLine, ...]) -> str:
    """The indentation the file's first indented line adds to its parent.

    Four spaces when no line is indented, or when that line's indentation does
    not begin with its parent's.
    """
    for parent, child in pairwise(lines):
        if child.indent > parent.indent:
            outer = _leading(text, parent.span.start)
            inner = _leading(text, child.span.start)
            if inner.startswith(outer) and len(inner) > len(outer):
                return inner[len(outer) :]
            return FALLBACK_STEP
    return FALLBACK_STEP


def _newline(text: str) -> str:
    """The ending of the file's first line, or a newline in a file with none."""
    index = next((i for i, char in enumerate(text) if char in "\r\n"), None)
    if index is None:
        return "\n"
    return "\r\n" if text.startswith("\r\n", index) else text[index]
