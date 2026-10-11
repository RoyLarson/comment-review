"""Immutable source records and exact character partition validation."""

from bisect import bisect_right
from dataclasses import dataclass, field
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
        """Require a nonempty validated span and a RegionKind classification."""
        if not isinstance(self.span, SourceSpan) or self.span.start == self.span.end:
            raise ValueError("Region span must be a nonempty SourceSpan")
        if not isinstance(self.kind, RegionKind):
            raise ValueError("Region kind must be a RegionKind")


@dataclass(frozen=True)
class SourceSection:
    """A source span and the section form supplied by a reader."""

    span: SourceSpan
    form: str

    def __post_init__(self) -> None:
        """Require a nonempty span and preserve the nonblank form identifier."""
        if not isinstance(self.span, SourceSpan) or self.span.start == self.span.end:
            raise ValueError("Section span must be a nonempty SourceSpan")
        if not isinstance(self.form, str) or not self.form.strip():
            raise ValueError("Section form must be a nonblank string")


@dataclass(frozen=True)
class SourceDeclaration:
    """A declaration header, source anchor, and reader-supplied kind."""

    header: SourceSpan
    anchor: int
    kind: str

    def __post_init__(self) -> None:
        """Require a nonempty header, absolute anchor, and nonblank kind."""
        if (
            not isinstance(self.header, SourceSpan)
            or self.header.start == self.header.end
        ):
            raise ValueError("Declaration header must be a nonempty SourceSpan")
        if (
            not isinstance(self.anchor, int)
            or isinstance(self.anchor, bool)
            or not self.header.start <= self.anchor < self.header.end
        ):
            raise ValueError("Declaration anchor must be an integer within header")
        if not isinstance(self.kind, str) or not self.kind.strip():
            raise ValueError("Declaration kind must be a nonblank string")


@dataclass(frozen=True)
class DocumentationOwner:
    """Section and optional declaration indices for documentation."""

    section: int
    declaration: int | None

    def __post_init__(self) -> None:
        """Require zero-based indices, with None for module ownership."""
        for name in ("section", "declaration"):
            index = getattr(self, name)
            if name == "declaration" and index is None:
                continue
            if not isinstance(index, int) or isinstance(index, bool) or index < 0:
                raise ValueError(
                    f"documentation {name} index {index!r} "
                    "must be a nonnegative integer"
                )


@dataclass(frozen=True)
class SourceStructure:
    """Exact source text partitioned into immutable reader records."""

    text: str
    regions: tuple[SourceRegion, ...]
    sections: tuple[SourceSection, ...]
    declarations: tuple[SourceDeclaration, ...]
    documentation: tuple[DocumentationOwner, ...]
    _line_starts: tuple[int, ...] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Validate string text and source records, then cache line boundaries."""
        if not isinstance(self.text, str):
            raise ValueError("text must be a string")
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

        section_end = 0
        for index, section in enumerate(self.sections):
            if section.span.end > len(self.text):
                raise ValueError(f"sections[{index}] span ends outside text")
            if section.span.start < section_end:
                raise ValueError(
                    f"sections[{index}] span must be in source order and nonoverlapping"
                )
            section_end = section.span.end

        declaration_start = 0
        for index, declaration in enumerate(self.declarations):
            if declaration.header.end > len(self.text):
                raise ValueError(f"declarations[{index}] header ends outside text")
            if declaration.header.start < declaration_start:
                raise ValueError(
                    f"declarations[{index}] header must be in source order"
                )
            declaration_start = declaration.header.start

        previous_section = -1
        owners: set[int | None] = set()
        for index, link in enumerate(self.documentation):
            if link.section >= len(self.sections):
                raise ValueError(
                    f"documentation[{index}] section index {link.section} "
                    "does not exist"
                )
            if link.declaration is not None and link.declaration >= len(
                self.declarations
            ):
                raise ValueError(
                    f"documentation[{index}] declaration index "
                    f"{link.declaration} does not exist"
                )
            if link.section <= previous_section:
                raise ValueError(
                    f"documentation[{index}] section index {link.section} "
                    "must be unique and in section order"
                )
            if link.declaration in owners:
                raise ValueError(
                    f"documentation[{index}] owner index {link.declaration} "
                    "already has a section"
                )
            previous_section = link.section
            owners.add(link.declaration)

        line_starts = [0]
        offset = 0
        while offset < len(self.text):
            character = self.text[offset]
            offset += 1
            if character == "\r":
                if offset < len(self.text) and self.text[offset] == "\n":
                    offset += 1
                line_starts.append(offset)
            elif character == "\n":
                line_starts.append(offset)
        object.__setattr__(self, "_line_starts", tuple(line_starts))

    def position(self, offset: int) -> SourcePosition:
        """Locate a character offset, including EOF, in cached physical lines."""
        if (
            not isinstance(offset, int)
            or isinstance(offset, bool)
            or not 0 <= offset <= len(self.text)
        ):
            raise ValueError("Position offset must be an integer within text")
        line = bisect_right(self._line_starts, offset)
        return SourcePosition(line, offset - self._line_starts[line - 1])

    def slice(self, span: SourceSpan) -> str:
        """Return exact characters from a half-open span within the source."""
        if not isinstance(span, SourceSpan) or span.end > len(self.text):
            raise ValueError("Slice span must be within text")
        return self.text[span.start : span.end]

    def reconstruct(self) -> str:
        """Concatenate the exact slices of the ordered source regions."""
        return "".join(self.slice(region.span) for region in self.regions)
