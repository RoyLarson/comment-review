"""Partition Rust source into comment, code and whitespace regions and their tokens."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import cast

from comment_review.reading.definitions import LanguageDefinition
from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage
from comment_review.reading.rust.definition import validate_rust
from comment_review.reading.rust.records import RustScan, RustToken, RustTokenKind
from comment_review.reading.source import RegionKind, SourceRegion, SourceSpan

BYTE_ORDER_MARK = "\ufeff"
# The Rust Reference's whitespace: Pattern_White_Space.
WHITESPACE = frozenset("\t\n\v\f\r \x85\u200e\u200f\u2028\u2029")
OPENERS = frozenset("{([")
CLOSERS = frozenset("})]")


@dataclass(frozen=True)
class _Comments:
    line: str
    outer_line: str
    inner_line: str
    opener: str
    closer: str
    outer_delimited: str
    inner_delimited: str
    empty: str

    @classmethod
    def from_definition(cls, definition: LanguageDefinition) -> "_Comments":
        comments = cast(Mapping[str, object], definition.rules["comments"])
        opener, closer = cast(tuple[str, str], comments["block_comment"])
        return cls(
            cast(str, comments["line"]),
            cast(str, comments["outer_doc_line"]),
            cast(str, comments["inner_doc_line"]),
            opener,
            closer,
            cast(str, comments["outer_doc_block"]),
            cast(str, comments["inner_doc_block"]),
            cast(str, comments["empty_block_comment"]),
        )


def scan_rust(text: str, definition: LanguageDefinition) -> RustScan | ReadFailure:
    """Partition Rust source, failing at NUL or an unterminated delimited comment.

    Adjacent code tokens share one CODE region and adjacent whitespace one
    WHITESPACE region; every comment is its own COMMENT region.

    Rust's grammar fixes two comment rules: a delimited comment nests, closing
    only when every opener inside it has closed, and an outer doc marker whose
    last character repeats (`////`, `/***`) opens an ordinary comment.
    """
    failure = validate_rust(definition)
    if failure is not None:
        return failure
    nul = text.find("\x00")
    if nul >= 0:
        return _failure("source-nul", nul, nul + 1)
    comments = _Comments.from_definition(definition)
    regions: list[SourceRegion] = []
    tokens: list[RustToken] = []
    start = 0
    while start < len(text):
        result = _next_token(text, start, comments)
        if isinstance(result, ReadFailure):
            return result
        kind, end, region_kind = result
        span = SourceSpan(start, end)
        if kind is not None:
            tokens.append(RustToken(kind, span))
        if (
            regions
            and regions[-1].kind is region_kind
            and region_kind is not RegionKind.COMMENT
        ):
            regions[-1] = SourceRegion(
                SourceSpan(regions[-1].span.start, end), region_kind
            )
        else:
            regions.append(SourceRegion(span, region_kind))
        start = end
    return RustScan(text, tuple(regions), tuple(tokens))


def _next_token(
    text: str, start: int, comments: _Comments
) -> tuple[RustTokenKind | None, int, RegionKind] | ReadFailure:
    """The token at `start`: its kind (None for a byte-order mark), end and region."""
    char = text[start]
    if start == 0 and char == BYTE_ORDER_MARK:
        return None, 1, RegionKind.WHITESPACE
    if char in WHITESPACE:
        end = start + 1
        while end < len(text) and text[end] in WHITESPACE:
            end += 1
        return RustTokenKind.WHITESPACE, end, RegionKind.WHITESPACE
    if text.startswith(comments.opener, start):
        return _delimited(text, start, comments)
    if text.startswith(comments.line, start):
        return _line(text, start, comments), _line_end(text, start), RegionKind.COMMENT
    # Literal, lifetime and attribute openers are not read yet; they belong here,
    # ahead of the code tokens, which would otherwise split them.
    if char in OPENERS:
        return RustTokenKind.OPEN, start + 1, RegionKind.CODE
    if char in CLOSERS:
        return RustTokenKind.CLOSE, start + 1, RegionKind.CODE
    if char.isidentifier():
        end = start + 1
        while end < len(text) and f"_{text[end]}".isidentifier():
            end += 1
        return RustTokenKind.WORD, end, RegionKind.CODE
    return RustTokenKind.PUNCT, start + 1, RegionKind.CODE


def _line(text: str, start: int, comments: _Comments) -> RustTokenKind:
    if text.startswith(comments.inner_line, start):
        return RustTokenKind.INNER_DOC_LINE
    if text.startswith(comments.outer_line, start) and not _repeated(
        text, start, comments.outer_line
    ):
        return RustTokenKind.OUTER_DOC_LINE
    return RustTokenKind.LINE


def _line_end(text: str, start: int) -> int:
    """Where a line comment ends: before its LF or CRLF, or at end of text."""
    end = text.find("\n", start)
    if end < 0:
        return len(text)
    return end - 1 if text[end - 1] == "\r" else end


def _delimited(
    text: str, start: int, comments: _Comments
) -> tuple[RustTokenKind, int, RegionKind] | ReadFailure:
    """Read a delimited comment to the close of its outermost layer."""
    depth = 1
    end = start + len(comments.opener)
    while end < len(text):
        if text.startswith(comments.opener, end):
            depth += 1
            end += len(comments.opener)
        elif text.startswith(comments.closer, end):
            depth -= 1
            end += len(comments.closer)
            if depth == 0:
                return _delimited_kind(text, start, comments), end, RegionKind.COMMENT
        else:
            end += 1
    return _failure("unterminated-comment", start, start + len(comments.opener))


def _delimited_kind(text: str, start: int, comments: _Comments) -> RustTokenKind:
    if text.startswith(comments.empty, start):
        return RustTokenKind.DELIMITED_COMMENT
    if text.startswith(comments.inner_delimited, start):
        return RustTokenKind.INNER_DOC_DELIMITED
    if text.startswith(comments.outer_delimited, start) and not _repeated(
        text, start, comments.outer_delimited
    ):
        return RustTokenKind.OUTER_DOC_DELIMITED
    return RustTokenKind.DELIMITED_COMMENT


def _repeated(text: str, start: int, marker: str) -> bool:
    """Whether an outer doc marker's last character repeats right after it."""
    return text.startswith(marker[-1], start + len(marker))


def _failure(code: str, start: int, end: int) -> ReadFailure:
    return ReadFailure(
        (
            ReadDiagnostic(
                ReadStage.LEX, code, code.replace("-", " "), SourceSpan(start, end)
            ),
        )
    )
