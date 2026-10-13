"""Encode edited documentation inside its retained Python statement shell."""

from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage
from comment_review.reading.python.records import PythonRead
from comment_review.reading.source import SourceSpan


def _failure(code: str, span: SourceSpan) -> ReadFailure:
    """Locate an ownership refusal in the retained source."""
    return ReadFailure(
        (ReadDiagnostic(ReadStage.PLACE, code, code.replace("-", " "), span),)
    )


def _literal(prose: str) -> str:
    """Encode every payload character in one ASCII plain string literal."""
    escapes = {"\\": "\\\\", '"': '\\"', "\n": "\\n", "\r": "\\r", "\t": "\\t"}
    encoded = []
    for char in prose:
        point = ord(char)
        if char in escapes:
            encoded.append(escapes[char])
        elif 32 <= point < 127:
            encoded.append(char)
        elif point < 256:
            encoded.append(f"\\x{point:02x}")
        elif point <= 0xFFFF:
            encoded.append(f"\\u{point:04x}")
        else:
            encoded.append(f"\\U{point:08x}")
    return '"' + "".join(encoded) + '"'


def render_documentation(
    read: PythonRead, declaration: int | None, prose: str
) -> str | ReadFailure:
    """Render one existing owner's complete documentation statement.

    Literal component spans delimit the edits; their decoded mappings partition
    the new payload. Parentheses, gaps, comments, and an owned semicolon retain
    their exact source spelling. An unchanged payload returns the original span.
    """
    text = read.source.text
    if declaration is None:
        suites = [i for i, suite in enumerate(read.suites) if suite.kind == "module"]
        location = SourceSpan(0, 0)
    else:
        facts = [
            fact
            for fact in read.declarations
            if not isinstance(declaration, bool) and fact.declaration == declaration
        ]
        if len(facts) != 1:
            return _failure("absent-documentation-owner", SourceSpan(0, 0))
        suites = [facts[0].suite]
        location = read.source.declarations[declaration].header
    if len(suites) != 1:
        return _failure("ambiguous-documentation-owner", location)
    payloads = [
        payload
        for payload in read.payloads
        if payload.expression.declaration == declaration
        and any(
            statement.span == payload.expression.statement
            and statement.suite == suites[0]
            for statement in read.statements
        )
    ]
    if len(payloads) != 1:
        return _failure(
            "absent-documentation" if not payloads else "ambiguous-documentation",
            location,
        )
    payload = payloads[0]
    expression = payload.expression
    if payload.text == prose:
        return text[expression.statement.start : expression.statement.end]
    out = []
    boundary = expression.statement.start
    decoded = 0
    for index, component in enumerate(expression.components):
        length = sum(
            piece.decoded.end - piece.decoded.start
            for piece in payload.mapping
            if all(
                component.start <= raw.start <= raw.end <= component.end
                for raw in piece.raw
            )
        )
        end = decoded + length if index < len(expression.components) - 1 else len(prose)
        out.append(text[boundary : component.start])
        out.append(_literal(prose[decoded:end]))
        decoded = end
        boundary = component.end
    out.append(text[boundary : expression.statement.end])
    return "".join(out)
