"""Identify documentation expressions and decode their complete prose."""

from collections.abc import Iterator, Mapping
from typing import cast
from unicodedata import lookup

from comment_review.reading.definitions import LanguageDefinition
from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage
from comment_review.reading.python.definition import validate_python
from comment_review.reading.python.records import (
    DocumentationExpression,
    DocumentationPayload,
    LogicalLine,
    PythonPlacement,
    PythonScan,
    PythonToken,
)
from comment_review.reading.python.structure import outer_boundaries
from comment_review.reading.source import SourceSpan


def documentation_in(
    scan: PythonScan, structure: PythonPlacement, definition: LanguageDefinition
) -> tuple[DocumentationExpression, ...] | ReadFailure:
    """Retain the first complete plain-string statement in each documentation body.

    Declaration indices and first positions come from preserved source placement.
    Component spans identify only literals; the section also owns its closing tail.
    """
    failure = validate_python(definition)
    if failure is not None:
        return failure
    documentation = cast(Mapping[str, object], definition.rules["documentation"])
    literals = cast(Mapping[str, object], definition.rules["literals"])
    layout = cast(Mapping[str, object], definition.rules["layout"])
    owners = cast(tuple[str, ...], documentation["owners"])
    groups = cast(tuple[str, ...], documentation["literal_groups"])
    prefixes = cast(Mapping[str, tuple[str, ...]], literals["prefixes"])
    allowed = frozenset(prefix for group in groups for prefix in prefixes[group])
    quotes = cast(tuple[str, ...], literals["short_quotes"])
    pairs = dict(cast(tuple[tuple[str, str], ...], layout["implicit_pairs"]))
    separator = cast(str, layout["statement_separator"])
    case_insensitive = cast(bool, literals["case_insensitive_prefixes"])
    expressions: list[DocumentationExpression] = []
    for declaration, line, insertion in _bodies(scan, structure, owners):
        indices = tuple(
            index for index in line.tokens if scan.tokens[index].span.start >= insertion
        )
        stop = next(
            (
                index
                for index in outer_boundaries(scan, indices)
                if scan.text[
                    scan.tokens[index].span.start : scan.tokens[index].span.end
                ]
                == separator
            ),
            None,
        )
        if stop is not None:
            indices = tuple(index for index in indices if index <= stop)
        tokens = tuple(scan.tokens[index] for index in indices)
        components = _components(
            scan.text, tokens, allowed, quotes, pairs["("], separator, case_insensitive
        )
        if not components:
            continue
        end = tokens[-1].span.end
        trailing = next(
            (
                token
                for token in scan.tokens
                if token.kind == "comment" and token.span.start >= end
            ),
            None,
        )
        if trailing is not None and not scan.text[end : trailing.span.start].strip(
            " \t\f"
        ):
            end = trailing.span.end
        expressions.append(
            DocumentationExpression(
                SourceSpan(tokens[0].span.start, end), components, declaration
            )
        )
    return tuple(sorted(expressions, key=lambda expression: expression.statement.start))


def _bodies(
    scan: PythonScan, structure: PythonPlacement, owners: tuple[str, ...]
) -> Iterator[tuple[int | None, LogicalLine, int]]:
    """Each owner whose body may open with documentation, and where it opens.

    Yields the declaration index, None for the module; the logical line the
    body's first statement is on; and that statement's first offset. The
    module's body is an unindented first line.
    """
    if "module" in owners and structure.lines and not structure.lines[0].indent:
        first = structure.lines[0]
        yield None, first, scan.tokens[first.tokens[0]].span.start
    for declaration, (header, insertion) in enumerate(
        zip(structure.declarations, structure.insertions, strict=True)
    ):
        if header.kind not in owners:
            continue
        header_line = next(
            line
            for line in structure.lines
            if line.span.start <= header.anchor < line.span.end
        )
        line = next(
            (
                line
                for line in structure.lines
                if any(
                    scan.tokens[index].span.start == insertion for index in line.tokens
                )
            ),
            None,
        )
        if line is None or (
            line is not header_line and line.indent <= header_line.indent
        ):
            continue
        yield declaration, line, insertion


def _components(
    text: str,
    tokens: tuple[PythonToken, ...],
    prefixes: frozenset[str],
    quotes: tuple[str, ...],
    closer: str,
    separator: str,
    case_insensitive: bool,
) -> tuple[SourceSpan, ...]:
    """Accept adjacent plain literals enclosed only by whole-expression parentheses."""
    spellings = [text[token.span.start : token.span.end] for token in tokens]
    start, end = 0, len(tokens)
    if end and tokens[end - 1].kind == "boundary" and spellings[end - 1] == separator:
        end -= 1
    while (
        end - start >= 2
        and tokens[start].kind == tokens[end - 1].kind == "boundary"
        and spellings[start] == "("
        and spellings[end - 1] == closer
    ):
        start += 1
        end -= 1
    components: list[SourceSpan] = []
    for token, spelling in zip(tokens[start:end], spellings[start:end], strict=True):
        if token.kind != "string":
            return ()
        quote = next((i for i, char in enumerate(spelling) if char in quotes), None)
        if quote is None:
            return ()
        prefix = spelling[:quote]
        if case_insensitive:
            prefix = prefix.lower()
        if prefix not in prefixes:
            return ()
        components.append(token.span)
    return tuple(components)


def decode_documentation(
    scan: PythonScan,
    expression: DocumentationExpression,
    definition: LanguageDefinition,
) -> DocumentationPayload | ReadFailure:
    """Concatenate complete literal contents, decoding escapes and physical newlines."""
    failure = validate_python(definition)
    if failure is not None:
        return failure
    literals = cast(Mapping[str, object], definition.rules["literals"])
    decoding = cast(Mapping[str, object], literals["decoding"])
    prefixes = cast(Mapping[str, tuple[str, ...]], literals["prefixes"])
    quotes = cast(tuple[str, ...], literals["short_quotes"])
    triples = cast(tuple[str, ...], literals["triple_quotes"])
    escape = cast(str, literals["escape_marker"])
    chunks: list[str] = []
    text = scan.text
    for component in expression.components:
        quote_start = next(
            index
            for index in range(component.start, component.end)
            if text[index] in quotes
        )
        prefix = text[component.start : quote_start]
        if literals["case_insensitive_prefixes"]:
            prefix = prefix.lower()
        quote = next(
            (quote for quote in triples if text.startswith(quote, quote_start)),
            text[quote_start],
        )
        raw = prefix in prefixes["raw"] and decoding["raw_escape"] == "preserve"
        start = quote_start + len(quote)
        end = component.end - len(quote)
        while start < end:
            if text[start] in "\r\n":
                following = _newline_end(text, start, end)
                decoded = "\n"
            elif not raw and text.startswith(escape, start):
                result = _decode_escape(text, start, end, escape, decoding)
                if isinstance(result, ReadFailure):
                    return result
                decoded, following = result
            else:
                following = start + 1
                while following < end and text[following] not in "\r\n":
                    if not raw and text.startswith(escape, following):
                        break
                    following += 1
                decoded = text[start:following]
            chunks.append(decoded)
            start = following
    return DocumentationPayload(expression, "".join(chunks))


def _newline_end(text: str, start: int, end: int) -> int:
    return start + (2 if text.startswith("\r\n", start, end) else 1)


def _decode_escape(
    text: str,
    start: int,
    end: int,
    marker: str,
    decoding: Mapping[str, object],
) -> tuple[str, int] | ReadFailure:
    suffix = start + len(marker)
    if suffix == end:
        return _payload_failure("invalid-documentation-escape", start, end)
    char = text[suffix]
    if char in "\r\n" and decoding["escaped_newline"] == "remove":
        return "", _newline_end(text, suffix, end)
    if char in cast(tuple[str, ...], decoding["simple_escapes"]):
        controls = dict(zip("abfnrtv", "\a\b\f\n\r\t\v", strict=True))
        return controls.get(char, char), suffix + 1
    if char in "01234567":
        following = suffix + 1
        maximum = cast(int, decoding["octal_max_digits"])
        while (
            following < end
            and following - suffix < maximum
            and text[following] in "01234567"
        ):
            following += 1
        return chr(int(text[suffix:following], 8)), following
    widths = {
        "x": cast(int, decoding["hex_digits"]),
        "u": cast(int, decoding["unicode_short_digits"]),
        "U": cast(int, decoding["unicode_long_digits"]),
    }
    if char in widths:
        digits_start = suffix + 1
        following = min(digits_start + widths[char], end)
        digits = text[digits_start:following]
        if len(digits) != widths[char] or any(
            digit not in "0123456789abcdefABCDEF" for digit in digits
        ):
            return _payload_failure("invalid-documentation-escape", start, following)
        value = int(digits, 16)
        if value > 0x10FFFF:
            return _payload_failure("invalid-documentation-escape", start, following)
        return chr(value), following
    if char == "N" and decoding["named_unicode"]:
        return _decode_name(text, start, suffix + 1, end)
    if decoding["unknown_escape"] == "preserve":
        return text[start : suffix + 1], suffix + 1
    return _payload_failure("invalid-documentation-escape", start, suffix + 1)


def _decode_name(
    text: str, start: int, opening: int, end: int
) -> tuple[str, int] | ReadFailure:
    if opening == end or text[opening] != "{":
        return _payload_failure("invalid-documentation-escape", start, opening)
    closing = text.find("}", opening + 1, end)
    if closing == -1:
        return _payload_failure("invalid-documentation-escape", start, end)
    if closing == opening + 1:
        return _payload_failure("invalid-documentation-escape", start, closing + 1)
    try:
        decoded = lookup(text[opening + 1 : closing])
    except KeyError:
        return _payload_failure("unknown-unicode-name", start, closing + 1)
    if len(decoded) != 1:
        return _payload_failure("unknown-unicode-name", start, closing + 1)
    return decoded, closing + 1


def _payload_failure(code: str, start: int, end: int) -> ReadFailure:
    return ReadFailure(
        (
            ReadDiagnostic(
                ReadStage.PLACE, code, code.replace("-", " "), SourceSpan(start, end)
            ),
        )
    )
