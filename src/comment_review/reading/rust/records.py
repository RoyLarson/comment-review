"""Immutable Rust reader records: the scan, the place model and the completed read."""

from bisect import bisect_right
from collections.abc import Collection
from dataclasses import dataclass
from enum import StrEnum
from itertools import pairwise
from pathlib import Path
from typing import Self, final

from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage
from comment_review.reading.paragraph import Paragraph
from comment_review.reading.proof import UNPROVABLE, PreservationResult
from comment_review.reading.source import (
    CodeLine,
    DocumentationOwner,
    RegionKind,
    SourceDeclaration,
    SourceRegion,
    SourceSection,
    SourceSpan,
    SourceStructure,
)

DETACHED_DOC_CODE = "detached-documentation"


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


ATTRIBUTE_KINDS = frozenset(
    {RustTokenKind.OUTER_ATTRIBUTE, RustTokenKind.INNER_ATTRIBUTE}
)


def _nesting(tokens: "tuple[RustToken, ...]", end: int) -> None:
    """Order tokens by start, enclosing attribute first; only attributes enclose."""
    cursor = 0
    open_attributes: list[SourceSpan] = []
    for token in tokens:
        span = token.span
        while open_attributes and open_attributes[-1].end <= span.start:
            cursor = max(cursor, open_attributes.pop().end)
        if span.start < cursor or span.end > end:
            raise ValueError("tokens must be ordered, nonoverlapping and in bounds")
        if open_attributes and span.end > open_attributes[-1].end:
            raise ValueError("a token may not overlap the end of an attribute")
        if token.kind in ATTRIBUTE_KINDS:
            open_attributes.append(span)
            cursor = span.start
        else:
            cursor = span.end


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


# Tokens no structural reading consults: layout, prose and the shebang line.
UNREAD_KINDS = COMMENT_KINDS | {RustTokenKind.WHITESPACE, RustTokenKind.SHEBANG}


def significant_tokens(tokens: tuple[RustToken, ...]) -> list[RustToken]:
    """The code tokens, each attribute standing for everything inside it."""
    kept: list[RustToken] = []
    inside = 0
    for token in tokens:
        if token.span.start < inside or token.kind in UNREAD_KINDS:
            continue
        kept.append(token)
        if token.kind in ATTRIBUTE_KINDS:
            inside = token.span.end
    return kept


@dataclass(frozen=True)
class RustScan:
    """The source text, its complete region partition and its ordered tokens."""

    text: str
    regions: tuple[SourceRegion, ...]
    tokens: tuple[RustToken, ...]

    def __post_init__(self) -> None:
        """Require a contiguous partition and tokens that agree with it."""
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
        _nesting(self.tokens, len(self.text))
        starts = [region.span.start for region in self.regions]
        for token in self.tokens:
            if token.kind not in COMMENT_KINDS and token.kind not in LITERAL_KINDS:
                continue
            region = self.regions[bisect_right(starts, token.span.start) - 1]
            if token.kind in COMMENT_KINDS and not (
                region.kind is RegionKind.COMMENT and region.span == token.span
            ):
                raise ValueError("comment token must equal a comment region")
            if token.kind in LITERAL_KINDS and not (
                region.kind is RegionKind.LITERAL and token.span.end <= region.span.end
            ):
                raise ValueError("literal token must lie inside a literal region")


@dataclass(frozen=True)
class DetachedRun:
    """A documentation run the place model cannot hold."""

    span: SourceSpan

    def __post_init__(self) -> None:
        """Require a SourceSpan."""
        if not isinstance(self.span, SourceSpan):
            raise ValueError("detached span must be a SourceSpan")


@dataclass(frozen=True)
class RustPlacement:
    """Declarations and detached runs."""

    declarations: tuple[SourceDeclaration, ...]
    detached: tuple[DetachedRun, ...]

    def __post_init__(self) -> None:
        """Require declarations and detached runs."""
        _tuple(self.declarations, SourceDeclaration, "declarations")
        _tuple(self.detached, DetachedRun, "detached")


class RustSectionForm(StrEnum):
    """What a comment section is, once documentation has been assigned.

    A doc comment that documents nothing, or is detached, is a COMMENT.
    """

    COMMENT = "comment"
    OUTER_DOC = "outer_doc"
    INNER_DOC = "inner_doc"
    MATTER = "matter"


@dataclass(frozen=True)
class RustDocumentation:
    """Every comment section, the ones that document an owner, and the placement.

    Each section's form is a RustSectionForm value. `owners` links each
    OUTER_DOC section to its declaration and each INNER_DOC section to the
    module, as declaration None: an inner doc in a body documents no owner.
    `placement` carries the declarations and the detached runs.
    Each warning marks one COMMENT or MATTER section that is detached
    documentation, and the warnings align one-to-one, in order, with
    `placement.detached`.
    """

    sections: tuple[SourceSection, ...]
    owners: tuple[DocumentationOwner, ...]
    placement: RustPlacement
    warnings: tuple[ReadDiagnostic, ...]

    def __post_init__(self) -> None:
        """Require ordered sections, owners that index them, and place warnings."""
        _tuple(self.sections, SourceSection, "sections")
        _tuple(self.owners, DocumentationOwner, "owners")
        if not isinstance(self.placement, RustPlacement):
            raise ValueError("placement must be a RustPlacement")
        for before, after in zip(self.sections, self.sections[1:], strict=False):
            if after.span.start < before.span.end:
                raise ValueError("sections must be ordered and nonoverlapping")
        if any(section.form not in set(RustSectionForm) for section in self.sections):
            raise ValueError("section form must be a RustSectionForm")
        documented = {RustSectionForm.OUTER_DOC, RustSectionForm.INNER_DOC}
        owned = [owner.section for owner in self.owners]
        if owned != sorted(set(owned)):
            raise ValueError("owners must name distinct sections in order")
        expected = [
            index
            for index, section in enumerate(self.sections)
            if section.form in documented
        ]
        if owned != expected:
            raise ValueError("owners must name exactly the documentation sections")
        declarations = [owner.declaration for owner in self.owners]
        if len(set(declarations)) != len(declarations) or any(
            index is not None and index >= len(self.placement.declarations)
            for index in declarations
        ):
            raise ValueError("owners must name distinct existing declarations")
        if any(
            owner.declaration is not None
            and self.sections[owner.section].form == RustSectionForm.INNER_DOC
            for owner in self.owners
        ):
            raise ValueError("an inner doc section may document only the module")
        _tuple(self.warnings, ReadDiagnostic, "warnings")
        comments = [
            section.span
            for section in self.sections
            if section.form in (RustSectionForm.COMMENT, RustSectionForm.MATTER)
        ]
        for warning in self.warnings:
            if warning.code != DETACHED_DOC_CODE or warning.stage != ReadStage.PLACE:
                raise ValueError("warnings must be detached-documentation place notes")
            if not any(
                warning.span is not None and span.start <= warning.span.start < span.end
                for span in comments
            ):
                raise ValueError("a warning must mark a comment or matter section")
        if [warning.span for warning in self.warnings] != [
            run.span for run in self.placement.detached
        ]:
            raise ValueError("warnings must align, in order, with detached runs")


def _section_start(section: SourceSection) -> int:
    return section.span.start


@final
@dataclass(frozen=True)
class RustRead:
    """A completed Rust read: the source structure and what the read must keep.

    `detached` aligns one-to-one, in order, with `warnings`. A COMMENT region
    in no section is code. Each
    declaration anchors on its own line, below the one before it, and its
    documentation goes above that line. A documentation section shares no
    physical line with another section, so an `a` place holds its doc alone;
    other sections may share a line, and the projection makes them one
    paragraph.
    """

    source: SourceStructure
    protected: tuple[SourceSpan, ...]
    warnings: tuple[ReadDiagnostic, ...]
    detached: tuple[DetachedRun, ...]

    def __post_init__(self) -> None:
        """Check declaration lines, protected spans, warnings and detached runs."""
        if not isinstance(self.source, SourceStructure):
            raise ValueError("read source must be a SourceStructure")
        lines = [
            self.source.position(declaration.anchor).line
            for declaration in self.source.declarations
        ]
        if any(after <= before for before, after in pairwise(lines)):
            raise ValueError("each declaration must anchor on its own line")
        documented = {RustSectionForm.OUTER_DOC, RustSectionForm.INNER_DOC}
        for before, after in pairwise(self.source.sections):
            if (
                self.source.position(after.span.start).line
                <= self.source.position(before.span.end - 1).line
            ) and (before.form in documented or after.form in documented):
                raise ValueError(
                    "a documentation section may not share a physical line"
                )
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
            if warning.code != DETACHED_DOC_CODE or warning.stage != ReadStage.PLACE:
                raise ValueError("warnings must be detached-documentation place notes")
            if warning.span is None or warning.span.end > len(self.source.text):
                raise ValueError("warning span must lie inside source")
        _tuple(self.detached, DetachedRun, "detached")
        if [warning.span for warning in self.warnings] != [
            run.span for run in self.detached
        ]:
            raise ValueError("warnings must align, in order, with detached runs")

    @property
    def proof(self) -> str:
        """The comparison's name, as a proof report prints it."""
        return "rust-lexical"

    def preserved(
        self,
        after: Self,
        *,
        documented: Collection[tuple[int | None, int | None]] | None = None,
    ) -> PreservationResult:
        """Whether `after` holds this read's code unchanged.

        Every comment the read makes a section of is prose to the comparison,
        documentation included, so `documented` is accepted and not read. An
        `after` that is not a Rust read is unprovable.
        """
        # Imported here because `preservation` reads this module's records.
        from comment_review.reading.rust.preservation import compare_preservation

        if not isinstance(after, RustRead):
            return PreservationResult(
                False,
                (
                    ReadDiagnostic(
                        ReadStage.PLACE,
                        UNPROVABLE,
                        "the other side is not a Rust read",
                    ),
                ),
            )
        return compare_preservation(self, after)

    def is_prose(self, region: SourceRegion) -> bool:
        """Whether the region is a comment inside a section, so prose, not code."""
        if region.kind is not RegionKind.COMMENT:
            return False
        sections = self.source.sections
        at = bisect_right(sections, region.span.start, key=_section_start) - 1
        return at >= 0 and region.span.start < sections[at].span.end

    def paragraphs(self, path: Path) -> list[Paragraph] | ReadFailure:
        """Every comment section of this read as a page paragraph."""
        # Imported here because `projection` reads this module's records.
        from comment_review.reading.rust.projection import paragraphs_for

        return paragraphs_for(path, self)

    def code_lines(self) -> list[CodeLine]:
        """Each code line, with a declaration's documentation place above it."""
        from comment_review.reading.rust.projection import code_lines_for

        return code_lines_for(self)

    @property
    def a_series(self) -> bool:
        """Whether the page has an `a` series: always, for Rust.

        Rust documents its crate or module and its items.
        """
        return True
