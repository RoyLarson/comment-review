"""Scan formatted literals with an explicit stack and absolute source events."""

from dataclasses import dataclass, field

from comment_review.reading.definitions import LanguageDefinition
from comment_review.reading.diagnostics import ReadFailure
from comment_review.reading.python.definition import validate_python
from comment_review.reading.python.records import InterpolationScan, PythonToken
from comment_review.reading.python.scanner import _failure, _next_token, _Syntax
from comment_review.reading.source import RegionKind, SourceRegion, SourceSpan


@dataclass
class _Literal:
    start: int
    quote: str
    raw: bool


@dataclass
class _Field:
    start: int
    literal: _Literal
    mode: str = "expression"
    brackets: list[str] = field(default_factory=list)
    nonempty: bool = False


class _Events:
    def __init__(self) -> None:
        self.regions: list[SourceRegion] = []
        self.tokens: list[PythonToken] = []

    def emit(self, kind: str, start: int, end: int, region: RegionKind) -> None:
        if end == start:
            return
        span = SourceSpan(start, end)
        if kind:
            self.tokens.append(PythonToken(kind, span))
        if self.regions and self.regions[-1].kind == region:
            self.regions[-1] = SourceRegion(
                SourceSpan(self.regions[-1].span.start, end), region
            )
        else:
            self.regions.append(SourceRegion(span, region))


def _literal(text: str, start: int, end: int) -> _Literal | ReadFailure:
    quote_start = start
    while text[quote_start] not in "'\"":
        quote_start += 1
    prefix = text[start:quote_start].lower()
    if "t" in prefix:
        return _failure("unsupported-interpolation", start, end)
    return _Literal(start, text[quote_start:end], "r" in prefix)


def scan_interpolation(
    text: str, start: int, definition: LanguageDefinition
) -> InterpolationScan | ReadFailure:
    """Scan from the prefix through the matching quote, keeping absolute spans.

    Start/end events delimit formatted literals; field_start/field_end delimit
    replacement fields. format_start and conversion preserve field boundaries.
    interpolation_literal identifies payload rather than ordinary string tokens.
    Code, comments and physical newlines keep the ordinary scanner's kinds.
    """
    failure = validate_python(definition)
    if failure is not None:
        return failure
    if not 0 <= start < len(text):
        return _failure("expected-interpolation", max(0, start), max(0, start))
    syntax = _Syntax.from_definition(definition)
    initial = _next_token(text, start, syntax)
    if isinstance(initial, ReadFailure):
        return initial
    kind, position, _ = initial
    if kind != "interpolation":
        return _failure("expected-interpolation", start, position)
    literal = _literal(text, start, position)
    if isinstance(literal, ReadFailure):
        return literal
    events = _Events()
    events.emit("interpolation_start", start, position, RegionKind.LITERAL)
    stack: list[_Literal | _Field] = [literal]
    pairs = {"(": ")", "[": "]", "{": "}"}

    while stack and position < len(text):
        frame = stack[-1]
        if isinstance(frame, _Literal) or frame.mode == "format":
            literal = frame if isinstance(frame, _Literal) else frame.literal
            payload_start = position
            while position < len(text):
                char = text[position]
                if text.startswith(literal.quote, position):
                    break
                if char in "{}":
                    if isinstance(frame, _Literal) and text.startswith(
                        char * 2, position
                    ):
                        position += 2
                        continue
                    break
                if char in "\r\n" and len(literal.quote) == 1:
                    return _failure("unterminated-literal", literal.start, position)
                if char == syntax.escape:
                    escaped = _escape_end(text, position, literal)
                    if isinstance(escaped, ReadFailure):
                        return escaped
                    position = escaped
                else:
                    position += 1
            events.emit(
                "interpolation_literal", payload_start, position, RegionKind.LITERAL
            )
            if position == len(text):
                break
            if text.startswith(literal.quote, position):
                if isinstance(frame, _Field):
                    return _failure("unfinished-field", frame.start, position)
                end = position + len(literal.quote)
                events.emit("interpolation_end", position, end, RegionKind.LITERAL)
                stack.pop()
                position = end
            elif text[position] == "{":
                events.emit("field_start", position, position + 1, RegionKind.CODE)
                stack.append(_Field(position, literal))
                position += 1
            elif isinstance(frame, _Field):
                events.emit("field_end", position, position + 1, RegionKind.CODE)
                stack.pop()
                position += 1
            else:
                return _failure("unmatched-field-closer", position, position + 1)
            continue

        char = text[position]
        if not frame.brackets and char in "}:!" and not text.startswith("!=", position):
            if not frame.nonempty:
                return _failure("empty-field", frame.start, position + 1)
            if char == "}":
                events.emit("field_end", position, position + 1, RegionKind.CODE)
                stack.pop()
                position += 1
            elif char == ":":
                events.emit("format_start", position, position + 1, RegionKind.CODE)
                frame.mode = "format"
                position += 1
            else:
                if (
                    frame.mode != "expression"
                    or position + 1 == len(text)
                    or text[position + 1] not in "sra"
                ):
                    return _failure(
                        "invalid-conversion", position, min(position + 2, len(text))
                    )
                events.emit("conversion", position, position + 2, RegionKind.CODE)
                position += 2
                frame.mode = "converted"
            continue
        if frame.mode == "converted":
            return _failure("invalid-conversion", position, position + 1)
        result = _next_token(text, position, syntax)
        if isinstance(result, ReadFailure):
            return result
        kind, end, region = result
        if kind == "interpolation":
            nested = _literal(text, position, end)
            if isinstance(nested, ReadFailure):
                return nested
            events.emit("interpolation_start", position, end, RegionKind.LITERAL)
            stack.append(nested)
            frame.nonempty = True
        else:
            spelling = text[position:end]
            if kind == "operator":
                if spelling in pairs:
                    frame.brackets.append(pairs[spelling])
                elif spelling in pairs.values():
                    if not frame.brackets or frame.brackets.pop() != spelling:
                        return _failure("mismatched-bracket", position, end)
            events.emit(kind, position, end, region)
            if kind and kind not in ("comment", "newline", "continuation"):
                frame.nonempty = True
        position = end

    if stack:
        frame = stack[-1]
        code = (
            "unfinished-field" if isinstance(frame, _Field) else "unterminated-literal"
        )
        return _failure(code, frame.start, len(text))
    return InterpolationScan(position, tuple(events.regions), tuple(events.tokens), ())


def _escape_end(text: str, start: int, literal: _Literal) -> int | ReadFailure:
    end = start + 1
    if end == len(text) or text[end] in "{}":
        return end
    if not literal.raw and text.startswith("N{", end):
        close = text.find("}", end + 2)
        if close == -1 or any(char in "\r\n'\"" for char in text[end + 2 : close]):
            return _failure("unfinished-unicode-escape", start, len(text))
        return close + 1
    return end + (2 if text.startswith("\r\n", end) else 1)
