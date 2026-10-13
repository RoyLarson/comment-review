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
class PythonStatement:
    """A complete statement referring to tokens and its containing suite."""

    span: SourceSpan
    tokens: tuple[int, ...]
    suite: int

    def __post_init__(self) -> None:
        """Require local spans and indices; containers check references."""
        _span(self.span, "statement span")
        _indices(self.tokens, "statement tokens")
        _index(self.suite, "statement suite")


@dataclass(frozen=True)
class PythonSuite:
    """A suite body, its optional header, and its direct statement indices."""

    span: SourceSpan
    parent: int | None
    header: SourceSpan | None
    statements: tuple[int, ...]
    kind: str

    def __post_init__(self) -> None:
        """Validate module identity and local fields, including empty bodies."""
        _span(self.span, "suite span")
        _optional_index(self.parent, "suite parent")
        if self.header is not None:
            _span(self.header, "suite header")
        _indices(self.statements, "suite statements")
        _name(self.kind, "suite kind")
        if self.kind == "module" and (
            self.parent is not None or self.header is not None
        ):
            raise ValueError("module suite has no parent or header")


@dataclass(frozen=True)
class DeclarationFacts:
    """Python placement facts for one existing source declaration."""

    declaration: int
    name: str
    parent: int | None
    suite: int
    insertion: int

    def __post_init__(self) -> None:
        """Require a name, references, and an absolute insertion offset."""
        _index(self.declaration, "declaration")
        _name(self.name, "declaration name")
        _optional_index(self.parent, "declaration parent")
        _index(self.suite, "declaration suite")
        _index(self.insertion, "declaration insertion")


@dataclass(frozen=True)
class PythonStructure:
    """Declarations, suites, and statements with reconciled structural references."""

    declarations: tuple[SourceDeclaration, ...]
    facts: tuple[DeclarationFacts, ...]
    suites: tuple[PythonSuite, ...]
    statements: tuple[PythonStatement, ...]

    def __post_init__(self) -> None:
        """Validate parent trees, direct memberships, and declaration placement."""
        _tuple(self.declarations, SourceDeclaration, "declarations")
        _tuple(self.facts, DeclarationFacts, "facts")
        _tuple(self.suites, PythonSuite, "suites")
        _tuple(self.statements, PythonStatement, "statements")
        modules = [
            index for index, suite in enumerate(self.suites) if suite.kind == "module"
        ]
        if len(modules) != 1:
            raise ValueError("structure requires exactly one module suite")
        membership: set[int] = set()
        for index, suite in enumerate(self.suites):
            if suite.kind != "module" and suite.parent is None:
                raise ValueError("nonmodule suite requires a parent")
            ancestors: set[int] = {index}
            parent = suite.parent
            while parent is not None:
                if parent >= len(self.suites) or parent in ancestors:
                    raise ValueError("suite parents must be in range and acyclic")
                ancestors.add(parent)
                parent = self.suites[parent].parent
            if suite.parent is not None:
                parent_span = self.suites[suite.parent].span
                if not _contains(parent_span, suite.span) or (
                    suite.header is not None
                    and not _contains(parent_span, suite.header)
                ):
                    raise ValueError("parent suite must contain child body and header")
            for statement in suite.statements:
                if statement >= len(self.statements) or statement in membership:
                    raise ValueError(
                        "suite statement references must be unique and in range"
                    )
                item = self.statements[statement]
                if item.suite != index or not _contains(suite.span, item.span):
                    raise ValueError("statement must belong to and fit its suite")
                membership.add(statement)
        if membership != set(range(len(self.statements))):
            raise ValueError("every statement must belong to a suite")
        facts = {fact.declaration: fact for fact in self.facts}
        if len(facts) != len(self.facts) or set(facts) != set(
            range(len(self.declarations))
        ):
            raise ValueError("declaration facts must uniquely map every declaration")
        body_owners = {fact.suite: fact.declaration for fact in self.facts}
        if len(body_owners) != len(self.facts):
            raise ValueError("each declaration requires its own body suite")
        for fact in self.facts:
            if fact.suite >= len(self.suites):
                raise ValueError("declaration suite does not exist")
            suite = self.suites[fact.suite]
            declaration = self.declarations[fact.declaration]
            if suite.header != declaration.header or suite.parent is None:
                raise ValueError("declaration must identify its body suite header")
            if not suite.span.start <= fact.insertion <= suite.span.end:
                raise ValueError("declaration insertion must be within its body")
            enclosing_suite = suite.parent
            while enclosing_suite is not None and enclosing_suite not in body_owners:
                enclosing_suite = self.suites[enclosing_suite].parent
            enclosing_declaration = (
                body_owners[enclosing_suite] if enclosing_suite is not None else None
            )
            if fact.parent != enclosing_declaration:
                raise ValueError("declaration parent must match enclosing declaration")
            ancestors = {fact.declaration}
            parent = fact.parent
            while parent is not None:
                if parent not in facts or parent in ancestors:
                    raise ValueError("declaration parents must be in range and acyclic")
                ancestors.add(parent)
                parent = facts[parent].parent
            if fact.parent is not None:
                parent_suite_index = facts[fact.parent].suite
                parent_span = self.suites[parent_suite_index].span
                if not _contains(parent_span, declaration.header) or not _contains(
                    parent_span, suite.span
                ):
                    raise ValueError(
                        "parent declaration must contain child declaration"
                    )
                ancestor_suite = suite.parent
                while (
                    ancestor_suite is not None and ancestor_suite != parent_suite_index
                ):
                    ancestor_suite = self.suites[ancestor_suite].parent
                if ancestor_suite is None:
                    raise ValueError("declaration parent must enclose the body suite")


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
class PayloadPiece:
    """One decoded span and the original spans that produced it."""

    decoded: SourceSpan
    raw: tuple[SourceSpan, ...]

    def __post_init__(self) -> None:
        """Keep zero-output mappings and multiple ordered original spans."""
        _span(self.decoded, "decoded span")
        _tuple(self.raw, SourceSpan, "raw spans")
        if not self.raw or any(span.start == span.end for span in self.raw):
            raise ValueError("payload piece requires nonempty raw spans")
        _ordered(self.raw, self.raw[-1].end, "raw spans")


@dataclass(frozen=True)
class DocumentationPayload:
    """Decoded documentation with complete decoded-to-source mapping."""

    expression: DocumentationExpression
    text: str
    mapping: tuple[PayloadPiece, ...]

    def __post_init__(self) -> None:
        """Validate decoded coverage and raw spans within literal components."""
        if not isinstance(self.expression, DocumentationExpression):
            raise ValueError("payload expression must be a DocumentationExpression")
        if not isinstance(self.text, str):
            raise ValueError("payload text must be a string")
        _tuple(self.mapping, PayloadPiece, "payload mapping")
        boundary = 0
        raw_end = 0
        for piece in self.mapping:
            if piece.decoded.start != boundary or piece.decoded.end > len(self.text):
                raise ValueError("payload mapping must completely cover decoded text")
            boundary = piece.decoded.end
            for span in piece.raw:
                if span.start < raw_end or not any(
                    _contains(component, span)
                    for component in self.expression.components
                ):
                    raise ValueError(
                        "payload raw spans must be ordered inside literal components"
                    )
                raw_end = span.end
        if boundary != len(self.text):
            raise ValueError("payload mapping must completely cover decoded text")


@dataclass(frozen=True)
class PythonRead:
    """A complete Python read reusing the exact source structure."""

    source: SourceStructure
    tokens: tuple[PythonToken, ...]
    suites: tuple[PythonSuite, ...]
    statements: tuple[PythonStatement, ...]
    declarations: tuple[DeclarationFacts, ...]
    payloads: tuple[DocumentationPayload, ...]
    protected: tuple[ProtectedSource, ...]

    def __post_init__(self) -> None:
        """Reconcile final source bounds, token references, and documentation owners."""
        if not isinstance(self.source, SourceStructure):
            raise ValueError("read source must be a SourceStructure")
        _scan_records(
            len(self.source.text), self.source.regions, self.tokens, self.protected
        )
        PythonStructure(
            self.source.declarations, self.declarations, self.suites, self.statements
        )
        _tuple(self.payloads, DocumentationPayload, "payloads")
        if any(suite.span.end > len(self.source.text) for suite in self.suites):
            raise ValueError("suite ends outside source")
        for statement in self.statements:
            for index in statement.tokens:
                if index >= len(self.tokens) or not _contains(
                    statement.span, self.tokens[index].span
                ):
                    raise ValueError("statement token must exist and fit the statement")
        if len(self.payloads) != len(self.source.documentation):
            raise ValueError("payloads must match source documentation owners")
        facts = {fact.declaration: fact for fact in self.declarations}
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
            expected_suite = (
                facts[owner.declaration].suite
                if owner.declaration is not None
                else next(
                    index
                    for index, suite in enumerate(self.suites)
                    if suite.kind == "module"
                )
            )
            matching = [
                statement
                for statement in self.statements
                if statement.span == expression.statement
                and statement.suite == expected_suite
            ]
            if len(matching) != 1:
                raise ValueError(
                    "documentation must identify a complete statement "
                    "in its owner suite"
                )
            token_spans = {self.tokens[index].span for index in matching[0].tokens}
            if any(component not in token_spans for component in expression.components):
                raise ValueError(
                    "documentation components must identify statement tokens"
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
