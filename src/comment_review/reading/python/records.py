"""Immutable Python reader stages with character spans and explicit references."""

from collections.abc import Collection
from dataclasses import dataclass
from pathlib import Path
from typing import Self, final

from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage
from comment_review.reading.paragraph import Paragraph
from comment_review.reading.proof import UNIDENTIFIED_OWNER, PreservationResult
from comment_review.reading.source import (
    CodeLine,
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
        """Require source records and one insertion per declaration."""
        _tuple(self.lines, LogicalLine, "lines")
        _tuple(self.declarations, SourceDeclaration, "declarations")
        _tuple(self.insertions, int, "insertions")
        if len(self.insertions) != len(self.declarations):
            raise ValueError("insertions must match declarations")
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
    """A documentation expression whose every literal decodes."""

    expression: DocumentationExpression

    def __post_init__(self) -> None:
        """Require the recognized expression."""
        if not isinstance(self.expression, DocumentationExpression):
            raise ValueError("payload expression must be a DocumentationExpression")


@final
@dataclass(frozen=True)
class PythonRead:
    """A complete Python read reusing the exact source structure."""

    source: SourceStructure
    payloads: tuple[DocumentationPayload, ...]
    protected: tuple[ProtectedSource, ...]

    def __post_init__(self) -> None:
        """Check source bounds and documentation owners."""
        if not isinstance(self.source, SourceStructure):
            raise ValueError("read source must be a SourceStructure")
        _tuple(self.protected, ProtectedSource, "protected")
        end = len(self.source.text)
        for item in self.protected:
            if item.span.end > end or (
                item.attachment is not None and item.attachment.end > end
            ):
                raise ValueError("protected span or attachment is outside source")
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

    @property
    def proof(self) -> str:
        """The comparison's name, as a proof report prints it."""
        return "lexical"

    @property
    def warnings(self) -> tuple[ReadDiagnostic, ...]:
        """The read's warnings: a Python read reports none."""
        return ()

    def paragraphs(self, path: Path) -> list[Paragraph] | ReadFailure:
        """Every retained section of this read as a page paragraph."""
        # Imported here because `projection` reads this module's records.
        from comment_review.reading.python.projection import paragraphs_for

        return paragraphs_for(path, self)

    def code_lines(self) -> list[CodeLine]:
        """Each code line, with a docstring's place on its declaring line."""
        from comment_review.reading.python.projection import code_lines_for

        return code_lines_for(self)

    @property
    def a_series(self) -> bool:
        """Whether the page has an `a` series: always, for Python.

        Python documents its module, its classes and its functions.
        """
        return True

    @property
    def closing_docstring(self) -> bool:
        """Whether the module's documentation can sit at the file's foot: never.

        A string after the last statement is an expression, not `__doc__`.
        """
        return False

    def owner_at(self, anchor_line: int | None) -> tuple[int | None, ...]:
        """The declaration documented from this anchor line; None for the module.

        Empty unless exactly one declaration is anchored on that line.
        """
        if anchor_line is None:
            return (None,)
        owners = tuple(
            index
            for index, declaration in enumerate(self.source.declarations)
            if self.source.position(declaration.anchor).line == anchor_line
        )
        return owners if len(owners) == 1 else ()

    def preserved(
        self,
        after: Self,
        *,
        documented: Collection[tuple[int | None, int | None]] | None = None,
    ) -> PreservationResult:
        """Whether `after` holds this read's executable source unchanged.

        A docstring is code in Python, so each approved alteration must name the
        same single declaration on both sides before its docstring is set aside.
        """
        # Imported here because `preservation` reads this module's records.
        from comment_review.reading.python.preservation import compare_preservation

        owners: set[int | None] = set()
        if documented is None:
            owners = {None, *range(len(self.source.declarations))}
        for was, now in documented or ():
            before_owner, after_owner = self.owner_at(was), after.owner_at(now)
            if not before_owner or before_owner != after_owner:
                return PreservationResult(
                    False,
                    (
                        ReadDiagnostic(
                            ReadStage.PLACE,
                            UNIDENTIFIED_OWNER,
                            "an approved docstring's declaration is not identified",
                        ),
                    ),
                )
            owners.add(before_owner[0])
        return compare_preservation(self, after, allowed_documentation_owners=owners)
