"""Immutable Python reader stages with character spans and explicit references."""

from dataclasses import dataclass

from comment_review.reading.diagnostics import ReadDiagnostic
from comment_review.reading.source import (
    SourceDeclaration,
    SourceRegion,
    SourceSpan,
    SourceStructure,
)


def _index(value: object, name: str) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer")


def _optional_index(value: object, name: str) -> None:
    if value is not None:
        _index(value, name)


def _name(value: object, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a nonblank string")


def _span(value: object, name: str) -> None:
    if not isinstance(value, SourceSpan):
        raise ValueError(f"{name} must be a SourceSpan")


def _tuple(value: object, record_type: type, name: str) -> None:
    if not isinstance(value, tuple) or any(
        not isinstance(item, record_type) for item in value
    ):
        raise ValueError(f"{name} must be a tuple of {record_type.__name__}")


def _indices(value: tuple[int, ...], name: str) -> None:
    _tuple(value, int, name)
    previous = -1
    for item in value:
        _index(item, name)
        if item <= previous:
            raise ValueError(f"{name} must be unique and in increasing order")
        previous = item


def _contains(outer: SourceSpan, inner: SourceSpan) -> bool:
    return outer.start <= inner.start <= inner.end <= outer.end


def _ordered(spans: tuple[SourceSpan, ...], end: int, name: str) -> None:
    boundary = 0
    for span in spans:
        if span.start < boundary or span.end > end:
            raise ValueError(f"{name} must be ordered, nonoverlapping and in bounds")
        boundary = span.end


@dataclass(frozen=True)
class PythonToken:
    """A significant token classified by the scanner."""

    kind: str
    span: SourceSpan

    def __post_init__(self) -> None:
        """Require a kind and a character span without assigning grammar."""
        _name(self.kind, "token kind")
        _span(self.span, "token span")
        if self.span.start == self.span.end:
            raise ValueError("token span must be nonempty")


@dataclass(frozen=True)
class ProtectedSource:
    """Observable source with an optional attachment to another source span."""

    span: SourceSpan
    kind: str
    attachment: SourceSpan | None

    def __post_init__(self) -> None:
        """Validate local fields while allowing nested protection."""
        _span(self.span, "protected span")
        _name(self.kind, "protected kind")
        if self.attachment is not None:
            _span(self.attachment, "protected attachment")


def _scan_records(
    end: int,
    regions: tuple[SourceRegion, ...],
    tokens: tuple[PythonToken, ...],
    protected: tuple[ProtectedSource, ...],
) -> None:
    _tuple(regions, SourceRegion, "regions")
    _tuple(tokens, PythonToken, "tokens")
    _tuple(protected, ProtectedSource, "protected")
    _ordered(tuple(region.span for region in regions), end, "regions")
    _ordered(tuple(token.span for token in tokens), end, "tokens")
    for item in protected:
        if item.span.end > end or (
            item.attachment is not None and item.attachment.end > end
        ):
            raise ValueError("protected span or attachment is outside source")


@dataclass(frozen=True)
class PythonScan:
    """Exact source and the scanner's complete region partition."""

    text: str
    regions: tuple[SourceRegion, ...]
    tokens: tuple[PythonToken, ...]
    protected: tuple[ProtectedSource, ...]

    def __post_init__(self) -> None:
        """Require a complete partition and source-bounded scanner records."""
        if not isinstance(self.text, str):
            raise ValueError("scan text must be a string")
        _scan_records(len(self.text), self.regions, self.tokens, self.protected)
        boundary = 0
        for region in self.regions:
            if region.span.start != boundary:
                raise ValueError("regions must completely partition source")
            boundary = region.span.end
        if boundary != len(self.text):
            raise ValueError("regions must completely partition source")


@dataclass(frozen=True)
class InterpolationScan:
    """Scanner records for a fragment ending at an absolute source offset."""

    end: int
    regions: tuple[SourceRegion, ...]
    tokens: tuple[PythonToken, ...]
    protected: tuple[ProtectedSource, ...]

    def __post_init__(self) -> None:
        """Validate fragment bounds without requiring a global partition."""
        _index(self.end, "fragment end")
        _scan_records(self.end, self.regions, self.tokens, self.protected)


@dataclass(frozen=True)
class LogicalLine:
    """A logical source line and its ordered significant token indices."""

    span: SourceSpan
    tokens: tuple[int, ...]
    indent: int

    def __post_init__(self) -> None:
        """Require a source span, ordered indices, and nonnegative indentation."""
        _span(self.span, "logical line span")
        _indices(self.tokens, "logical line tokens")
        _index(self.indent, "indent")


@dataclass(frozen=True)
class PythonPlacement:
    """Transient source boundaries and declaration positions for classification."""

    lines: tuple[LogicalLine, ...]
    declarations: tuple[SourceDeclaration, ...]
    insertions: tuple[int, ...]

    def __post_init__(self) -> None:
        """Require source records and one insertion per documentation owner."""
        _tuple(self.lines, LogicalLine, "lines")
        _tuple(self.declarations, SourceDeclaration, "declarations")
        _tuple(self.insertions, int, "insertions")
        if len(self.insertions) != len(self.declarations) + 1:
            raise ValueError("insertions must match module and declarations")
        for insertion in self.insertions:
            _index(insertion, "insertion")


@dataclass(frozen=True)
class DocumentationExpression:
    """A documentation statement with ordered literal component token spans."""

    statement: SourceSpan
    components: tuple[SourceSpan, ...]
    declaration: int | None

    def __post_init__(self) -> None:
        """Require literal spans inside the statement and an optional owner index."""
        _span(self.statement, "documentation statement")
        _tuple(self.components, SourceSpan, "documentation components")
        _optional_index(self.declaration, "documentation declaration")
        if not self.components:
            raise ValueError("documentation expression requires literal components")
        _ordered(self.components, self.statement.end, "documentation components")
        if any(
            not _contains(self.statement, span) or span.start == span.end
            for span in self.components
        ):
            raise ValueError("literal components must be nonempty and inside statement")


@dataclass(frozen=True)
class DocumentationPayload:
    """Complete decoded prose and the source expression used for raw extraction."""

    expression: DocumentationExpression
    text: str

    def __post_init__(self) -> None:
        """Require the recognized expression and its complete decoded text."""
        if not isinstance(self.expression, DocumentationExpression):
            raise ValueError("payload expression must be a DocumentationExpression")
        if not isinstance(self.text, str):
            raise ValueError("payload text must be a string")


@dataclass(frozen=True)
class PythonRead:
    """A complete Python read reusing the exact source structure."""

    source: SourceStructure
    payloads: tuple[DocumentationPayload, ...]
    protected: tuple[ProtectedSource, ...]
    insertions: tuple[int, ...]

    def __post_init__(self) -> None:
        """Check source bounds, documentation owners, and ordered insertion slots."""
        if not isinstance(self.source, SourceStructure):
            raise ValueError("read source must be a SourceStructure")
        _tuple(self.protected, ProtectedSource, "protected")
        end = len(self.source.text)
        for item in self.protected:
            if item.span.end > end or (
                item.attachment is not None and item.attachment.end > end
            ):
                raise ValueError("protected span or attachment is outside source")
        _tuple(self.insertions, int, "insertions")
        if len(self.insertions) != len(self.source.declarations) + 1:
            raise ValueError("insertions must match module and source declarations")
        for insertion in self.insertions:
            _index(insertion, "documentation insertion")
            if insertion > end:
                raise ValueError("documentation insertion is outside source")
        _tuple(self.payloads, DocumentationPayload, "payloads")
        if len(self.payloads) != len(self.source.documentation):
            raise ValueError("payloads must match source documentation owners")
        for payload, owner in zip(
            self.payloads, self.source.documentation, strict=True
        ):
            expression = payload.expression
            section = self.source.sections[owner.section]
            if (
                expression.declaration != owner.declaration
                or expression.statement != section.span
            ):
                raise ValueError(
                    "payload statement and owner must match source documentation"
                )


@dataclass(frozen=True)
class PreservationResult:
    """A preservation decision with diagnostics only when source changed."""

    unchanged: bool
    diagnostics: tuple[ReadDiagnostic, ...]

    def __post_init__(self) -> None:
        """Require a Boolean decision and the corresponding diagnostic presence."""
        if not isinstance(self.unchanged, bool):
            raise ValueError("unchanged must be a bool")
        _tuple(self.diagnostics, ReadDiagnostic, "diagnostics")
        if self.unchanged == bool(self.diagnostics):
            raise ValueError(
                "unchanged results have no diagnostics; changed results require them"
            )
