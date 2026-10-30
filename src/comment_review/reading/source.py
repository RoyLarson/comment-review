"""Immutable source records and exact character partition validation.

Beside them is the contract a reader hands the page its code lines by:
`CodeLine`, each line of code with the `DocPlace` it declares, built by
`lines_of_code`.
"""

from collections.abc import Collection, Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from typing import NamedTuple

from comment_review.reading.coordinates import SourceCoordinates
from comment_review.reading.coordinates import SourcePosition as SourcePosition


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


class DocPlace(NamedTuple):
    """Where a declaration's documentation is set, against one code line."""

    #: The code line the documentation is set against.
    at: int
    #: True: above that line; False: after it, inside the declaration.
    above: bool


class CodeLine(NamedTuple):
    """One line of code, and the documentation place it declares, if any."""

    #: The 1-based source line.
    line: int
    #: The line's code with trailing whitespace removed: what a `c`'s anchor is.
    code: str
    #: Set when this line declares something documentable.
    documents: DocPlace | None
    #: True when this line and the code line directly above it are one unit
    #: for the `a` and `b` series: one gap above the unit and one `a` for it.
    #: Each line of a unit keeps its own `c`.
    joins: bool = False


def lines_of_code(
    code: Mapping[int, str],
    declared: Mapping[int, DocPlace],
    joined: Collection[int] = (),
) -> list[CodeLine]:
    """Each code line in order, carrying the documentation place declared on it.

    A line declares at most one documentable thing, so `declared` holds one
    place per line; a reader keeps the first declaration on a line when it
    builds it.

    Args:
        code: each 1-based line that holds code -> its code, ascending.
        declared: each declaring line -> its documentation place.
        joined: each line that is one unit with the code line directly above
            it, such as a declaring line under its annotation.

    Raises:
        ValueError: when a declaring line, or the line a documentation place
            is set against, is not a code line; or when a joined line, or the
            line directly above it, is not a code line.
    """
    for line, place in declared.items():
        for named in (line, place.at):
            if named not in code:
                raise ValueError(
                    f"a documentation place names line {named}, not a code line"
                )
    joins = set(joined)
    for line in joins:
        if line not in code or line - 1 not in code:
            raise ValueError(f"line {line} joins no code line directly above it")
    return [CodeLine(n, text, declared.get(n), n in joins) for n, text in code.items()]


@dataclass(frozen=True)
class SourceStructure:
    """Exact source text partitioned into immutable reader records."""

    text: str
    regions: tuple[SourceRegion, ...]
    sections: tuple[SourceSection, ...]
    declarations: tuple[SourceDeclaration, ...]
    documentation: tuple[DocumentationOwner, ...]
    _coordinates: SourceCoordinates = field(init=False, repr=False)

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

        object.__setattr__(self, "_coordinates", SourceCoordinates(self.text))

    def position(self, offset: int) -> SourcePosition:
        """Locate a character offset, including EOF, in cached physical lines."""
        return self._coordinates.position(offset)

    def line_span(self, line: int) -> tuple[int, int]:
        """Start and end offset of a physical line, its line break excluded."""
        return self._coordinates.line_span(line)

    def declaring_line(self, declaration: SourceDeclaration) -> int:
        """The code line that declares this.

        It is the line a doc's `anchor_line` names where a unit is one line.
        """
        return self.position(declaration.anchor).line

    def slice(self, span: SourceSpan) -> str:
        """Return exact characters from a half-open span within the source."""
        if not isinstance(span, SourceSpan) or span.end > len(self.text):
            raise ValueError("Slice span must be within text")
        return self.text[span.start : span.end]

    def reconstruct(self) -> str:
        """Concatenate the exact slices of the ordered source regions."""
        return "".join(self.slice(region.span) for region in self.regions)
