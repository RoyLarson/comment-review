"""Recognize Python lines, statement boundaries, and suite ownership from tokens."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import cast

from comment_review.reading.definitions import LanguageDefinition
from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage
from comment_review.reading.python.definition import validate_python
from comment_review.reading.python.records import (
    DeclarationFacts,
    LogicalLine,
    PythonScan,
    PythonStatement,
    PythonStructure,
    PythonSuite,
)
from comment_review.reading.source import SourceDeclaration, SourceSpan


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


def recognize_structure(
    scan: PythonScan,
    lines: tuple[LogicalLine, ...],
    definition: LanguageDefinition,
) -> PythonStructure | ReadFailure:
    """Place header-only compound statements and simple statements in body suites.

    Each significant token has one statement owner. A separating semicolon belongs
    to its preceding simple statement. Body spans include intervening layout up
    to the next dedenting line or EOF; empty bodies retain their start as an
    insertion point. Declaration facts retain exact names and enclosing owners.
    """
    failure = validate_python(definition)
    if failure is not None:
        return failure
    recognizer = _Suites(scan, lines, definition)
    try:
        recognizer.check_lines()
        recognizer.block(0, 0, 0)
        declarations, facts = recognizer.declaration_records()
    except _StructureError as error:
        return error.failure
    return PythonStructure(
        declarations,
        facts,
        tuple(suite.record() for suite in recognizer.suites),
        tuple(recognizer.statements),
    )


class _StructureError(Exception):
    """Abort structural recognition with a source-located failure."""

    def __init__(self, code: str, span: SourceSpan) -> None:
        """Retain the diagnostic instead of returning partial ownership facts."""
        super().__init__(code)
        self.failure = _failure(code, span)


@dataclass
class _Suite:
    """Accumulate direct members until the body's dedenting boundary is known."""

    span: SourceSpan
    parent: int | None
    header: SourceSpan | None
    kind: str
    statements: list[int] = field(default_factory=list)

    def record(self) -> PythonSuite:
        """Freeze the reconciled body and its ordered direct membership."""
        return PythonSuite(
            self.span, self.parent, self.header, tuple(self.statements), self.kind
        )


class _Suites:
    """Consume logical lines in source order, recursing only into indented bodies."""

    def __init__(
        self,
        scan: PythonScan,
        lines: tuple[LogicalLine, ...],
        definition: LanguageDefinition,
    ) -> None:
        """Use the Python definition's punctuation and declaration spellings."""
        self.scan = scan
        self.lines = lines
        layout = cast(Mapping[str, object], definition.rules["layout"])
        declarations = cast(Mapping[str, object], definition.rules["declarations"])
        self.pairs = dict(cast(tuple[tuple[str, str], ...], layout["implicit_pairs"]))
        self.separator = cast(str, layout["statement_separator"])
        self.delimiter = cast(str, layout["suite_delimiter"])
        self.declarations = cast(tuple[str, ...], declarations["keywords"])
        self.async_keyword = cast(str, declarations["async_keyword"])
        self.statements: list[PythonStatement] = []
        self.suites = [_Suite(SourceSpan(0, len(scan.text)), None, None, "module")]

    def check_lines(self) -> None:
        """Refuse token omissions, overlaps, or source-inconsistent line records."""
        boundary = 0
        owned: list[int] = []
        for line in self.lines:
            if (
                line.span.start < boundary
                or line.span.end > len(self.scan.text)
                or not line.tokens
            ):
                raise _StructureError("inconsistent-line-boundary", line.span)
            for index in line.tokens:
                if index >= len(self.scan.tokens):
                    raise _StructureError("inconsistent-line-boundary", line.span)
                token = self.scan.tokens[index]
                if (
                    token.span.start < line.span.start
                    or token.span.end > line.span.end
                    or token.kind in {"comment", "newline", "continuation"}
                ):
                    raise _StructureError("inconsistent-line-boundary", line.span)
            owned.extend(line.tokens)
            boundary = line.span.end
        expected = [
            i
            for i, token in enumerate(self.scan.tokens)
            if token.kind not in {"comment", "newline", "continuation"}
        ]
        if owned != expected:
            span = (
                self.lines[-1].span
                if self.lines
                else SourceSpan(0, len(self.scan.text))
            )
            raise _StructureError("inconsistent-line-boundary", span)

    def spelling(self, index: int) -> str:
        """Read a token's exact spelling from its canonical source span."""
        span = self.scan.tokens[index].span
        return self.scan.text[span.start : span.end]

    def declaration_records(
        self,
    ) -> tuple[tuple[SourceDeclaration, ...], tuple[DeclarationFacts, ...]]:
        """Bind declaration headers to exact names, enclosing owners, and bodies."""
        headers = {statement.span: statement for statement in self.statements}
        declarations: list[SourceDeclaration] = []
        facts: list[DeclarationFacts] = []
        owners: dict[int, int] = {}
        for index, suite in enumerate(self.suites):
            if suite.kind not in {"class", "function", "async-function"}:
                continue
            header = suite.header
            assert header is not None
            tokens = headers[header].tokens
            name_position = 2 if self.spelling(tokens[0]) == self.async_keyword else 1
            name = self.scan.tokens[tokens[name_position]]
            if name.kind != "identifier":
                raise _StructureError("missing-declaration-name", name.span)
            enclosing = suite.parent
            while enclosing is not None and enclosing not in owners:
                enclosing = self.suites[enclosing].parent
            parent = owners[enclosing] if enclosing is not None else None
            declaration = len(declarations)
            declarations.append(SourceDeclaration(header, header.start, suite.kind))
            insertion = (
                self.statements[suite.statements[0]].span.start
                if suite.statements
                else suite.span.start
            )
            facts.append(
                DeclarationFacts(
                    declaration,
                    self.spelling(tokens[name_position]),
                    parent,
                    index,
                    insertion,
                )
            )
            owners[index] = declaration
        return tuple(declarations), tuple(facts)

    def surface(self, tokens: tuple[int, ...]) -> list[tuple[int, str]]:
        """Find outer punctuation while keeping brackets and interpolation opaque."""
        result: list[tuple[int, str]] = []
        brackets: list[str] = []
        opaque: list[str] = []
        openings = {
            "interpolation_start": "interpolation_end",
            "field_start": "field_end",
        }
        endings = frozenset(openings.values())
        for position, index in enumerate(tokens):
            token = self.scan.tokens[index]
            spelling = self.spelling(index)
            if token.kind in openings:
                if not opaque and not brackets:
                    result.append((position, spelling))
                opaque.append(openings[token.kind])
                continue
            if token.kind in endings:
                if not opaque or opaque.pop() != token.kind:
                    raise _StructureError(
                        "inconsistent-interpolation-boundary", token.span
                    )
                continue
            if opaque:
                continue
            if token.kind == "operator" and spelling in self.pairs:
                if not brackets:
                    result.append((position, spelling))
                brackets.append(self.pairs[spelling])
            elif token.kind == "operator" and spelling in self.pairs.values():
                if not brackets or brackets.pop() != spelling:
                    raise _StructureError("mismatched-bracket", token.span)
                if not brackets:
                    result.append((position, spelling))
            elif not brackets:
                result.append((position, spelling))
        if brackets or opaque:
            raise _StructureError(
                "unfinished-statement-boundary", self.scan.tokens[tokens[-1]].span
            )
        return result

    def header(
        self,
        tokens: tuple[int, ...],
        in_match: bool = False,
    ) -> tuple[str, int] | None:
        """Recognize contextual compound starts and their outer, non-lambda colon."""
        outer = self.surface(tokens)
        first = self.spelling(tokens[0])
        prefix = 1
        kind = first
        if first == self.async_keyword:
            if len(tokens) < 2 or self.spelling(tokens[1]) not in {
                "def",
                "for",
                "with",
            }:
                return None
            first = self.spelling(tokens[1])
            kind = "async-function" if first == "def" else "async-" + first
            prefix = 2
        elif first in self.declarations:
            kind = "function" if first == "def" else "class"
        elif first in {"match", "case"}:
            if first == "case" and not in_match:
                return None
            if len(outer) < 3 or outer[1][1] in {
                self.delimiter,
                "=",
                ":=",
                ".",
                "+=",
                "-=",
                "*=",
                "/=",
                "|=",
                "&=",
                "^=",
                "%=",
                "**=",
                "//=",
                "<<=",
                ">>=",
                "@=",
            }:
                return None
        elif first not in {
            "if",
            "elif",
            "else",
            "for",
            "while",
            "try",
            "except",
            "finally",
            "with",
        }:
            return None
        if first == "except" and len(tokens) > 1 and self.spelling(tokens[1]) == "*":
            kind = "except*"
            prefix = 2
        lambdas = 0
        for position, spelling in outer:
            if (
                spelling == "lambda"
                and self.scan.tokens[tokens[position]].kind == "identifier"
            ):
                lambdas += 1
            elif spelling == self.separator:
                break
            elif spelling == self.delimiter:
                if lambdas:
                    lambdas -= 1
                    continue
                if (
                    kind == "match"
                    and position + 1 < len(tokens)
                    and self.subscript_target(tokens, outer, position)
                ):
                    return None
                if (
                    position < prefix
                    or (
                        position == prefix
                        and first not in {"else", "try", "except", "finally"}
                    )
                    or (kind == "except*" and position == prefix)
                ):
                    raise _StructureError(
                        "incomplete-suite-header", self.scan.tokens[tokens[0]].span
                    )
                return kind, position
        if first in {"match", "case"}:
            return None
        raise _StructureError(
            "missing-suite-delimiter", self.scan.tokens[tokens[0]].span
        )

    def subscript_target(
        self,
        tokens: tuple[int, ...],
        outer: list[tuple[int, str]],
        colon: int,
    ) -> bool:
        """Distinguish a soft-name subscript annotation from a list-subject match."""
        target = [
            (position, spelling) for position, spelling in outer[1:] if position < colon
        ]
        position = 0
        if not target or target[0][1] != "[":
            return False
        while position < len(target):
            if target[position][1] == "[":
                if position + 1 >= len(target) or target[position + 1][1] != "]":
                    return False
            elif target[position][1] == ".":
                if (
                    position + 1 >= len(target)
                    or self.scan.tokens[tokens[target[position + 1][0]]].kind
                    != "identifier"
                ):
                    return False
            else:
                return False
            position += 2
        return True

    def statement(self, tokens: tuple[int, ...], suite: int) -> SourceSpan:
        """Assign exact tokens once, excluding surrounding indentation and comments."""
        span = SourceSpan(
            self.scan.tokens[tokens[0]].span.start,
            self.scan.tokens[tokens[-1]].span.end,
        )
        self.suites[suite].statements.append(len(self.statements))
        self.statements.append(PythonStatement(span, tokens, suite))
        return span

    def simple(self, tokens: tuple[int, ...], suite: int) -> None:
        """Split only outer semicolons and reject compound starts in simple bodies."""
        separators = [
            position
            for position, spelling in self.surface(tokens)
            if spelling == self.separator
        ]
        start = 0
        for end in [*separators, len(tokens)]:
            if start == end:
                if end == len(tokens):
                    return
                raise _StructureError(
                    "empty-simple-statement", self.scan.tokens[tokens[end]].span
                )
            segment = tokens[start:end]
            if self.header(segment) is not None:
                raise _StructureError(
                    "compound-in-simple-suite", self.scan.tokens[segment[0]].span
                )
            self.statement(tokens[start : end + (end < len(tokens))], suite)
            start = end + 1

    def chain(
        self,
        previous: tuple[str, str] | None,
        kind: str,
        span: SourceSpan,
    ) -> tuple[str, str] | None:
        """Require clauses to continue an immediately preceding compatible chain."""
        if kind not in {"elif", "else", "except", "except*", "finally"}:
            return (
                (kind, kind)
                if kind in {"if", "for", "async-for", "while", "try"}
                else None
            )
        root, last = previous if previous is not None else ("", "")
        valid = (
            (kind == "elif" and root == "if" and last in {"if", "elif"})
            or (
                kind == "else"
                and (
                    (root == "if" and last in {"if", "elif"})
                    or (root in {"for", "async-for", "while"} and last == root)
                    or (root == "try" and last in {"except", "except*"})
                )
            )
            or (
                kind in {"except", "except*"}
                and root == "try"
                and last in {"try", kind}
            )
            or (
                kind == "finally"
                and root == "try"
                and last in {"try", "except", "except*", "else"}
            )
        )
        if not valid:
            raise _StructureError("inconsistent-clause-owner", span)
        return root, kind

    def block(self, suite: int, position: int, indent: int) -> int:
        """Consume direct members and their bodies until the suite dedents."""
        previous: tuple[str, str] | None = None
        while position < len(self.lines):
            line = self.lines[position]
            if line.indent < indent:
                break
            if line.indent > indent:
                raise _StructureError("unexpected-indentation", line.span)
            header = self.header(line.tokens, self.suites[suite].kind == "match")
            if self.suites[suite].kind == "match" and (
                header is None or header[0] != "case"
            ):
                raise _StructureError("inconsistent-case-owner", line.span)
            if header is None:
                self.simple(line.tokens, suite)
                previous = None
                position += 1
                continue
            kind, colon = header
            previous = self.chain(previous, kind, self.scan.tokens[line.tokens[0]].span)
            span = self.statement(line.tokens[: colon + 1], suite)
            inline = line.tokens[colon + 1 :]
            start = span.end if inline else line.span.end
            child = len(self.suites)
            self.suites.append(_Suite(SourceSpan(start, start), suite, span, kind))
            position += 1
            if inline:
                if kind == "match":
                    raise _StructureError("inline-match-body", span)
                self.simple(inline, child)
                end = line.span.end
            else:
                if position < len(self.lines) and self.lines[position].indent > indent:
                    position = self.block(child, position, self.lines[position].indent)
                end = (
                    self.lines[position].span.start
                    if position < len(self.lines)
                    else len(self.scan.text)
                )
            self.suites[child].span = SourceSpan(start, end)
        return position
