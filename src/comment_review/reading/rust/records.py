"""Immutable Rust reader records: the scan, the place model and the completed read."""

from bisect import bisect_right
from dataclasses import dataclass
from enum import StrEnum

from comment_review.reading.diagnostics import ReadDiagnostic, ReadStage
from comment_review.reading.source import (
    DocumentationOwner,
    RegionKind,
    SourceDeclaration,
    SourceRegion,
    SourceSection,
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
    OUTER_DOC and INNER_DOC section to its declaration, None for the module.
    `placement` carries the module insertion line and the detached runs.
    Each warning marks one COMMENT section that is detached documentation:
    every detached run has one, and so does a second inner doc run for the
    module, which no DetachedRun can name.
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
        _tuple(self.warnings, ReadDiagnostic, "warnings")
        comments = {
            section.span
            for section in self.sections
            if section.form == RustSectionForm.COMMENT
        }
        warned = [warning.span for warning in self.warnings]
        for warning in self.warnings:
            if (
                warning.code != DETACHED_DOCUMENTATION
                or warning.stage != ReadStage.PLACE
            ):
                raise ValueError("warnings must be detached-documentation place notes")
            if warning.span not in comments:
                raise ValueError("a warning must mark a comment section")
        if any(run.span not in warned for run in self.placement.detached):
            raise ValueError("every detached run must have a warning")


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
