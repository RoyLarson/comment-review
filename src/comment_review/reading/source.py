"""Immutable source records and exact character partition validation."""

from dataclasses import dataclass
from enum import StrEnum


@dataclass(frozen=True)
class SourceSpan:
    """A half-open interval of character offsets, including empty points."""

    start: int
    end: int

    def __post_init__(self) -> None:
        """Reject non-integer, negative, or reversed bounds."""
        if (
            not isinstance(self.start, int)
            or isinstance(self.start, bool)
            or not isinstance(self.end, int)
            or isinstance(self.end, bool)
            or not 0 <= self.start <= self.end
        ):
            raise ValueError("Source span requires integer bounds 0 <= start <= end")


@dataclass(frozen=True)
class SourcePosition:
    """A one-based physical line and zero-based character column."""

    line: int
    column: int

    def __post_init__(self) -> None:
        """Reject non-integer values and positions below their lower limits."""
        if (
            not isinstance(self.line, int)
            or isinstance(self.line, bool)
            or not isinstance(self.column, int)
            or isinstance(self.column, bool)
            or self.line < 1
            or self.column < 0
        ):
            raise ValueError(
                "Source position requires integer line >= 1 and column >= 0"
            )


class RegionKind(StrEnum):
    """Reader-supplied classification of a source region."""

    CODE = "code"
    LITERAL = "literal"
    COMMENT = "comment"
    WHITESPACE = "whitespace"
    DIRECTIVE = "directive"


@dataclass(frozen=True)
class SourceRegion:
    """A nonempty source span with its reader-supplied classification."""

    span: SourceSpan
    kind: RegionKind

    def __post_init__(self) -> None:
        """Require a nonempty validated span."""
        if not isinstance(self.span, SourceSpan) or self.span.start == self.span.end:
            raise ValueError("Region span must be a nonempty SourceSpan")


@dataclass(frozen=True)
class SourceSection:
    """A source span and the section form supplied by a reader."""

    span: SourceSpan
    form: str


@dataclass(frozen=True)
class SourceDeclaration:
    """A declaration header, source anchor, and reader-supplied kind."""

    header: SourceSpan
    anchor: int
    kind: str


@dataclass(frozen=True)
class DocumentationOwner:
    """Section and optional declaration indices for documentation."""

    section: int
    declaration: int | None


@dataclass(frozen=True)
class SourceStructure:
    """Exact source text partitioned into immutable reader records."""

    text: str
    regions: tuple[SourceRegion, ...]
    sections: tuple[SourceSection, ...]
    declarations: tuple[SourceDeclaration, ...]
    documentation: tuple[DocumentationOwner, ...]

    def __post_init__(self) -> None:
        """Validate collection shapes and complete ordered region coverage."""
        for name, record_type in (
            ("regions", SourceRegion),
            ("sections", SourceSection),
            ("declarations", SourceDeclaration),
            ("documentation", DocumentationOwner),
        ):
            records = getattr(self, name)
            if not isinstance(records, tuple):
                raise ValueError(f"{name} must be a tuple")
            for index, record in enumerate(records):
                if not isinstance(record, record_type):
                    raise ValueError(f"{name}[{index}] must be {record_type.__name__}")
            if not self.text and records:
                raise ValueError(f"{name}[0] must be absent for empty text")

        boundary = 0
        for index, region in enumerate(self.regions):
            if region.span.start != boundary:
                raise ValueError(f"regions[{index}] must start at boundary {boundary}")
            if region.span.end > len(self.text):
                raise ValueError(f"regions[{index}] ends outside text")
            boundary = region.span.end
        if boundary != len(self.text):
            raise ValueError(
                f"regions[{len(self.regions)}] missing coverage "
                f"from boundary {boundary}"
            )

    def slice(self, span: SourceSpan) -> str:
        """Return exact characters from a half-open span within the source."""
        if not isinstance(span, SourceSpan) or span.end > len(self.text):
            raise ValueError("Slice span must be within text")
        return self.text[span.start : span.end]
