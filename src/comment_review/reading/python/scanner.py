"""Pure Python token boundaries with exact spelling and physical line endings."""

import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import cast

from comment_review.reading.definitions import LanguageDefinition
from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage
from comment_review.reading.python.definition import validate_python
from comment_review.reading.python.records import PythonScan, PythonToken
from comment_review.reading.source import RegionKind, SourceRegion, SourceSpan

_DIGITS = r"[0-9](?:_?[0-9])*"
_EXPONENT = rf"[eE][+-]?{_DIGITS}"
_FLOAT = (
    rf"(?:{_DIGITS}\.(?:{_DIGITS})?(?:{_EXPONENT})?"
    rf"|\.{_DIGITS}(?:{_EXPONENT})?|{_DIGITS}{_EXPONENT})"
)
_NUMBER = re.compile(
    rf"(?:{_FLOAT}|{_DIGITS})[jJ]|{_FLOAT}"
    r"|0[xX](?:_?[0-9a-fA-F])+|0[oO](?:_?[0-7])+|0[bB](?:_?[01])+"
    r"|[1-9](?:_?[0-9])*|0(?:_?0)*"
)
_OPERATORS = (
    "**=",
    "//=",
    ">>=",
    "<<=",
    "...",
    "**",
    "//",
    "<<",
    ">>",
    ":=",
    "<=",
    ">=",
    "==",
    "!=",
    "->",
    "+=",
    "-=",
    "*=",
    "/=",
    "%=",
    "@=",
    "&=",
    "|=",
    "^=",
    *"+-*/%@&|^~<>=.,",
)


@dataclass(frozen=True)
class _Syntax:
    comment: str
    join: str
    quotes: tuple[str, ...]
    prefixes: frozenset[str]
    operators: tuple[str, ...]

    @classmethod
    def from_definition(cls, definition: LanguageDefinition) -> "_Syntax":
        comments = cast(Mapping[str, object], definition.rules["comments"])
        layout = cast(Mapping[str, object], definition.rules["layout"])
        literals = cast(Mapping[str, object], definition.rules["literals"])
        prefixes = cast(Mapping[str, tuple[str, ...]], literals["prefixes"])
        pairs = cast(tuple[tuple[str, str], ...], layout["implicit_pairs"])
        operators = (
            *_OPERATORS,
            *(char for pair in pairs for char in pair),
            cast(str, layout["statement_separator"]),
            cast(str, layout["suite_delimiter"]),
        )
        return cls(
            cast(str, comments["marker"]),
            cast(str, layout["explicit_join"]),
            cast(tuple[str, ...], literals["short_quotes"]),
            frozenset(prefix for group in prefixes.values() for prefix in group),
            tuple(sorted(operators, key=len, reverse=True)),
        )


def scan_python(text: str, definition: LanguageDefinition) -> PythonScan | ReadFailure:
    """Partition Python source, failing at unsupported or incomplete lexical state."""
    failure = validate_python(definition)
    if failure is not None:
        return failure
    syntax = _Syntax.from_definition(definition)
    regions: list[SourceRegion] = []
    tokens: list[PythonToken] = []
    start = 0
    while start < len(text):
        result = _next_token(text, start, syntax)
        if isinstance(result, ReadFailure):
            return result
        kind, end, region_kind = result
        span = SourceSpan(start, end)
        if kind:
            tokens.append(PythonToken(kind, span))
        if regions and regions[-1].kind == region_kind:
            regions[-1] = SourceRegion(
                SourceSpan(regions[-1].span.start, end), region_kind
            )
        else:
            regions.append(SourceRegion(span, region_kind))
        start = end
    return PythonScan(text, tuple(regions), tuple(tokens), ())


def _next_token(
    text: str, start: int, syntax: _Syntax
) -> tuple[str, int, RegionKind] | ReadFailure:
    char = text[start]
    if char in " \t\f":
        end = start + 1
        while end < len(text) and text[end] in " \t\f":
            end += 1
        return "", end, RegionKind.WHITESPACE
    if char in "\r\n":
        end = start + (2 if text.startswith("\r\n", start) else 1)
        return "newline", end, RegionKind.WHITESPACE
    if text.startswith(syntax.comment, start):
        end = start + len(syntax.comment)
        while end < len(text) and text[end] not in "\r\n":
            end += 1
        return "comment", end, RegionKind.COMMENT
    if char in syntax.quotes:
        return _failure("unsupported-literal", start, start + 1)
    if text.startswith(syntax.join, start):
        end = start + len(syntax.join)
        if end == len(text) or text[end] not in "\r\n":
            return _failure("incomplete-continuation", start, end)
        return "continuation", end, RegionKind.CODE
    if _name_start(char):
        end = start + 1
        while end < len(text) and _name_continue(text[end]):
            end += 1
        if (
            end < len(text)
            and text[end] in syntax.quotes
            and text[start:end].lower() in syntax.prefixes
        ):
            return _failure("unsupported-literal", start, end + 1)
        return "identifier", end, RegionKind.CODE
    if char in "0123456789" or (
        char == "." and start + 1 < len(text) and text[start + 1] in "0123456789"
    ):
        result = _number_end(text, start)
        if isinstance(result, ReadFailure):
            return result
        return "number", result, RegionKind.CODE
    for operator in syntax.operators:
        if text.startswith(operator, start):
            return "operator", start + len(operator), RegionKind.CODE
    return _failure("unsupported-character", start, start + 1)


def _name_start(char: str) -> bool:
    return char in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_" or (
        ord(char) >= 128
    )


def _name_continue(char: str) -> bool:
    return _name_start(char) or char in "0123456789"


def _number_end(text: str, start: int) -> int | ReadFailure:
    match = _NUMBER.match(text, start)
    if match is not None:
        end = match.end()
        if end == len(text) or not _name_continue(text[end]):
            return end
    end = start + 1
    while end < len(text):
        if _name_continue(text[end]) or text[end] == ".":
            end += 1
        elif text[end] in "+-" and text[end - 1] in "eE":
            end += 1
        else:
            break
    return _failure("invalid-number", start, end)


def _failure(code: str, start: int, end: int) -> ReadFailure:
    return ReadFailure(
        (
            ReadDiagnostic(
                ReadStage.LEX, code, code.replace("-", " "), SourceSpan(start, end)
            ),
        )
    )
