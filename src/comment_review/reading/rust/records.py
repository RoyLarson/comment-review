"""Immutable Rust reader records: the scan, the place model and the completed read."""

from dataclasses import dataclass
from enum import StrEnum

from comment_review.reading.diagnostics import ReadDiagnostic, ReadStage
from comment_review.reading.source import (
    RegionKind,
    SourceDeclaration,
    SourceRegion,
    SourceSpan,
    SourceStructure,
)

DETACHED_DOCUMENTATION = "detached-documentation"


class RustTokenKind(StrEnum):
    """The closed vocabulary of token kinds the scanner emits."""

    LINE = "line"
    OUTER_DOC_LINE = "outer_doc_line"
    INNER_DOC_LINE = "inner_doc_line"
    DELIMITED_COMMENT = "delimited_comment"
    OUTER_DOC_DELIMITED = "outer_doc_delimited"
    INNER_DOC_DELIMITED = "inner_doc_delimited"
    STRING = "string"
    RAW_STRING = "raw_string"
    CHAR = "char"
    LIFETIME = "lifetime"
    OUTER_ATTRIBUTE = "outer_attribute"
    INNER_ATTRIBUTE = "inner_attribute"
    OPEN = "open"
    CLOSE = "close"
    WORD = "word"
    PUNCT = "punct"
    WHITESPACE = "whitespace"
    SHEBANG = "shebang"


COMMENT_KINDS = frozenset(
    {
        RustTokenKind.LINE,
        RustTokenKind.OUTER_DOC_LINE,
        RustTokenKind.INNER_DOC_LINE,
        RustTokenKind.DELIMITED_COMMENT,
        RustTokenKind.OUTER_DOC_DELIMITED,
        RustTokenKind.INNER_DOC_DELIMITED,
    }
)
LITERAL_KINDS = frozenset(
    {RustTokenKind.STRING, RustTokenKind.RAW_STRING, RustTokenKind.CHAR}
)


def _tuple(value: object, record_type: type, name: str) -> None:
    if not isinstance(value, tuple) or any(
        not isinstance(item, record_type) for item in value
    ):
        raise ValueError(f"{name} must be a tuple of {record_type.__name__}")


def _ordered(spans: tuple[SourceSpan, ...], end: int, name: str) -> None:
    boundary = 0
    for span in spans:
        if span.start < boundary or span.end > end:
            raise ValueError(f"{name} must be ordered, nonoverlapping and in bounds")
        boundary = span.end


def _insertions(insertions: tuple[int, ...], declarations: int) -> None:
    _tuple(insertions, int, "insertions")
    if len(insertions) != declarations + 1:
        raise ValueError("insertions must match module and declarations")
    if any(isinstance(item, bool) or item < 1 for item in insertions):
        raise ValueError("insertions must be positive line numbers")
    for before, after in zip(insertions[1:], insertions[2:], strict=False):
        if after <= before:
            raise ValueError("declaration insertions must be strictly increasing")


@dataclass(frozen=True)
class RustToken:
    """A scanner token: a kind and the nonempty source span it covers."""

    kind: RustTokenKind
    span: SourceSpan

    def __post_init__(self) -> None:
        """Require a RustTokenKind and a nonempty SourceSpan."""
        if not isinstance(self.kind, RustTokenKind):
            raise ValueError("token kind must be a RustTokenKind")
        if not isinstance(self.span, SourceSpan):
            raise ValueError("token span must be a SourceSpan")
        if self.span.start == self.span.end:
            raise ValueError("token span must be nonempty")


@dataclass(frozen=True)
class RustScan:
    """The source text, its complete region partition and its ordered tokens."""

    text: str
    regions: tuple[SourceRegion, ...]
    tokens: tuple[RustToken, ...]

    def __post_init__(self) -> None:
        """Require a contiguous partition and tokens that agree with the regions."""
        if not isinstance(self.text, str):
            raise ValueError("scan text must be a string")
        _tuple(self.regions, SourceRegion, "regions")
        _tuple(self.tokens, RustToken, "tokens")
        boundary = 0
        for region in self.regions:
            if region.span.start != boundary:
                raise ValueError("regions must completely partition source")
            boundary = region.span.end
        if boundary != len(self.text):
            raise ValueError("regions must completely partition source")
        _ordered(tuple(token.span for token in self.tokens), len(self.text), "tokens")
        spans = {
            kind: {r.span for r in self.regions if r.kind is kind}
            for kind in (RegionKind.COMMENT, RegionKind.LITERAL)
        }
        for token in self.tokens:
            if (
                token.kind in COMMENT_KINDS
                and token.span not in spans[RegionKind.COMMENT]
            ):
                raise ValueError("comment token must equal a comment region")
            if token.kind in LITERAL_KINDS and not any(
                r.kind is RegionKind.LITERAL
                and r.span.start <= token.span.start
                and token.span.end <= r.span.end
                for r in self.regions
            ):
                raise ValueError("literal token must lie inside a literal region")


@dataclass(frozen=True)
class DetachedRun:
    """A documentation run the place model cannot hold, and its would-be owner."""

    span: SourceSpan
    owner: int

    def __post_init__(self) -> None:
        """Require a SourceSpan and a nonnegative declaration index."""
        if not isinstance(self.span, SourceSpan):
            raise ValueError("detached span must be a SourceSpan")
        if (
            not isinstance(self.owner, int)
            or isinstance(self.owner, bool)
            or self.owner < 0
        ):
            raise ValueError("detached owner must be a nonnegative integer")


@dataclass(frozen=True)
class RustPlacement:
    """Declarations, their documentation insertion lines, and detached runs.

    `insertions[0]` is the 1-based line for an added module document;
    `insertions[i + 1]` is the 1-based head-first line of `declarations[i]`.
    """

    declarations: tuple[SourceDeclaration, ...]
    insertions: tuple[int, ...]
    detached: tuple[DetachedRun, ...]

    def __post_init__(self) -> None:
        """Require one insertion per declaration and detached owners that exist."""
        _tuple(self.declarations, SourceDeclaration, "declarations")
        _insertions(self.insertions, len(self.declarations))
        _tuple(self.detached, DetachedRun, "detached")
        if any(run.owner >= len(self.declarations) for run in self.detached):
            raise ValueError("detached owner must index declarations")


@dataclass(frozen=True)
class RustRead:
    """A completed Rust read: the source structure and what the read must keep."""

    source: SourceStructure
    protected: tuple[SourceSpan, ...]
    insertions: tuple[int, ...]
    warnings: tuple[ReadDiagnostic, ...]

    def __post_init__(self) -> None:
        """Check insertions, protected directive spans and place warnings."""
        if not isinstance(self.source, SourceStructure):
            raise ValueError("read source must be a SourceStructure")
        _insertions(self.insertions, len(self.source.declarations))
        _tuple(self.protected, SourceSpan, "protected")
        directives = {
            region.span
            for region in self.source.regions
            if region.kind is RegionKind.DIRECTIVE
        }
        for span in self.protected:
            if span.end > len(self.source.text):
                raise ValueError("protected span is outside source")
            if span not in directives:
                raise ValueError("protected span must coincide with a directive region")
        _tuple(self.warnings, ReadDiagnostic, "warnings")
        for warning in self.warnings:
            if (
                warning.code != DETACHED_DOCUMENTATION
                or warning.stage != ReadStage.PLACE
            ):
                raise ValueError("warnings must be detached-documentation place notes")
            if warning.span is None or warning.span.end > len(self.source.text):
                raise ValueError("warning span must lie inside source")
