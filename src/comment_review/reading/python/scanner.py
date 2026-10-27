"""Pure Python token boundaries with exact spelling and physical line endings."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import cast

from comment_review import constants
from comment_review.reading.definitions import LanguageDefinition
from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage
from comment_review.reading.python.definition import validate_python
from comment_review.reading.python.records import (
    ProtectedSource,
    PythonScan,
    PythonToken,
)
from comment_review.reading.source import RegionKind, SourceRegion, SourceSpan


@dataclass(frozen=True)
class _Syntax:
    comment: str
    continuation: str
    quotes: tuple[str, ...]
    triple_quotes: tuple[str, ...]
    prefixes: frozenset[str]
    interpolated_prefixes: frozenset[str]
    case_insensitive_prefixes: bool
    escape: str
    delimiters: frozenset[str]
    prefix_lengths: tuple[int, ...]

    @classmethod
    def from_definition(cls, definition: LanguageDefinition) -> "_Syntax":
        comments = cast(Mapping[str, object], definition.rules["comments"])
        layout = cast(Mapping[str, object], definition.rules["layout"])
        literals = cast(Mapping[str, object], definition.rules["literals"])
        prefixes = cast(Mapping[str, tuple[str, ...]], literals["prefixes"])
        forms = frozenset(prefix for group in prefixes.values() for prefix in group)
        pairs = cast(tuple[tuple[str, str], ...], layout["implicit_pairs"])
        delimiters = (
            *(char for pair in pairs for char in pair),
            cast(str, layout["statement_separator"]),
            cast(str, layout["suite_delimiter"]),
        )
        return cls(
            cast(str, comments["marker"]),
            cast(str, layout["explicit_join"]),
            cast(tuple[str, ...], literals["short_quotes"]),
            cast(tuple[str, ...], literals["triple_quotes"]),
            forms,
            frozenset(
                prefix
                for group in ("formatted", "raw_formatted", "template", "raw_template")
                for prefix in prefixes[group]
            ),
            cast(bool, literals["case_insensitive_prefixes"]),
            cast(str, literals["escape_marker"]),
            frozenset(delimiters),
            tuple(sorted({len(prefix) for prefix in forms if prefix}, reverse=True)),
        )


def scan_python(text: str, definition: LanguageDefinition) -> PythonScan | ReadFailure:
    """Partition Python source, failing at unsupported or incomplete lexical state."""
    from comment_review.reading.python.interpolation import scan_interpolation

    failure = validate_python(definition)
    if failure is not None:
        return failure
    nul = text.find("\x00")
    if nul >= 0:
        return _failure("source-nul", nul, nul + 1)
    syntax = _Syntax.from_definition(definition)
    regions: list[SourceRegion] = []
    tokens: list[PythonToken] = []
    protected: list[ProtectedSource] = []
    start = 0
    while start < len(text):
        result = _next_token(text, start, syntax)
        if isinstance(result, ReadFailure):
            return result
        kind, end, region_kind = result
        if kind == "interpolation":
            fragment = scan_interpolation(text, start, definition)
            if isinstance(fragment, ReadFailure):
                return fragment
            regions.extend(fragment.regions)
            tokens.extend(fragment.tokens)
            protected.extend(fragment.protected)
            start = fragment.end
            continue
        span = SourceSpan(start, end)
        if kind:
            tokens.append(PythonToken(kind, span))
        if (
            regions
            and regions[-1].kind == region_kind
            and region_kind != RegionKind.LITERAL
        ):
            regions[-1] = SourceRegion(
                SourceSpan(regions[-1].span.start, end), region_kind
            )
        else:
            regions.append(SourceRegion(span, region_kind))
        start = end
    return PythonScan(text, tuple(regions), tuple(tokens), tuple(protected))


def _next_token(
    text: str, start: int, syntax: _Syntax, *, field: bool = False
) -> tuple[str, int, RegionKind] | ReadFailure:
    char = text[start]
    if start == 0 and char == constants.BYTE_ORDER_MARK:
        return "", 1, RegionKind.WHITESPACE
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
        return _literal_token(text, start, start, "", syntax)
    if text.startswith(syntax.continuation, start):
        end = start + len(syntax.continuation)
        if end == len(text) or text[end] not in "\r\n":
            return _failure("incomplete-continuation", start, end)
        return "continuation", end, RegionKind.CODE
    prefixed = _prefix_at(text, start, syntax)
    if prefixed is not None:
        prefix, end = prefixed
        return _literal_token(text, start, end, prefix, syntax)
    if _boundary_at(text, start, syntax, field=field):
        return "boundary", start + 1, RegionKind.CODE
    end = start + 1
    while end < len(text):
        if (
            text[end] in " \t\f\r\n"
            or text[end] in syntax.quotes
            or text.startswith(syntax.comment, end)
            or text.startswith(syntax.continuation, end)
            or _boundary_at(text, end, syntax, field=field)
            or _prefix_at(text, end, syntax) is not None
        ):
            break
        end += 1
    return "code", end, RegionKind.CODE


def _literal_token(
    text: str, start: int, quote_start: int, prefix: str, syntax: _Syntax
) -> tuple[str, int, RegionKind] | ReadFailure:
    quote = next(
        (
            quote
            for quote in syntax.triple_quotes
            if text.startswith(quote, quote_start)
        ),
        text[quote_start],
    )
    end = quote_start + len(quote)
    if prefix in syntax.interpolated_prefixes:
        return "interpolation", end, RegionKind.LITERAL
    triple = quote in syntax.triple_quotes
    while end < len(text):
        if text.startswith(quote, end):
            return "string", end + len(quote), RegionKind.LITERAL
        if text.startswith(syntax.escape, end):
            end += len(syntax.escape)
            if end < len(text):
                end += 2 if text.startswith("\r\n", end) else 1
        elif not triple and text[end] in "\r\n":
            return _failure("unterminated-literal", start, end)
        else:
            end += 1
    return _failure("unterminated-literal", start, end)


def _prefix_at(text: str, start: int, syntax: _Syntax) -> tuple[str, int] | None:
    if start and (
        text[start - 1]
        in ("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789")
        or ord(text[start - 1]) >= 128
    ):
        return None
    for length in syntax.prefix_lengths:
        end = start + length
        if end >= len(text) or text[end] not in syntax.quotes:
            continue
        prefix = text[start:end]
        if syntax.case_insensitive_prefixes:
            prefix = prefix.lower()
        if prefix in syntax.prefixes:
            return prefix, end
    return None


def _boundary_at(text: str, start: int, syntax: _Syntax, *, field: bool) -> bool:
    char = text[start]
    if char == "!":
        return field and not text.startswith("!=", start)
    if char == ":" and text.startswith(":=", start) and not field:
        return False
    if char in syntax.delimiters:
        return True
    if char != "=":
        return False
    return not (
        text.startswith("==", start) or (start and text[start - 1] in "=!:<>+-*/%@&|^")
    )


def _failure(code: str, start: int, end: int) -> ReadFailure:
    return ReadFailure(
        (
            ReadDiagnostic(
                ReadStage.LEX, code, code.replace("-", " "), SourceSpan(start, end)
            ),
        )
    )
