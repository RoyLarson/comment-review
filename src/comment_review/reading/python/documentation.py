"""Identify plain documentation expressions in their retained owner suites."""

from collections.abc import Mapping
from typing import cast

from comment_review.reading.definitions import LanguageDefinition
from comment_review.reading.diagnostics import ReadFailure
from comment_review.reading.python.definition import validate_python
from comment_review.reading.python.records import (
    DocumentationExpression,
    PythonScan,
    PythonStructure,
    PythonToken,
)
from comment_review.reading.source import SourceSpan


def documentation_in(
    scan: PythonScan, structure: PythonStructure, definition: LanguageDefinition
) -> tuple[DocumentationExpression, ...] | ReadFailure:
    """Retain the first complete plain-string statement in each documentation body.

    Declaration indices come from the structural facts. Statement spans include
    any owned semicolon; component spans identify only the ordered literal tokens.
    """
    failure = validate_python(definition)
    if failure is not None:
        return failure
    documentation = cast(Mapping[str, object], definition.rules["documentation"])
    literals = cast(Mapping[str, object], definition.rules["literals"])
    layout = cast(Mapping[str, object], definition.rules["layout"])
    owners = cast(tuple[str, ...], documentation["owners"])
    groups = cast(tuple[str, ...], documentation["literal_groups"])
    prefixes = cast(Mapping[str, tuple[str, ...]], literals["prefixes"])
    allowed = frozenset(prefix for group in groups for prefix in prefixes[group])
    quotes = cast(tuple[str, ...], literals["short_quotes"])
    pairs = dict(cast(tuple[tuple[str, str], ...], layout["implicit_pairs"]))
    separator = cast(str, layout["statement_separator"])
    case_insensitive = cast(bool, literals["case_insensitive_prefixes"])
    body_owners = {fact.suite: fact.declaration for fact in structure.facts}
    expressions: list[DocumentationExpression] = []
    for index, suite in enumerate(structure.suites):
        if suite.kind not in owners or not suite.statements:
            continue
        if suite.kind == "module":
            declaration = None
        elif index in body_owners:
            declaration = body_owners[index]
        else:
            continue
        statement = structure.statements[suite.statements[0]]
        tokens = tuple(scan.tokens[token] for token in statement.tokens)
        components = _components(
            scan.text, tokens, allowed, quotes, pairs["("], separator, case_insensitive
        )
        if components:
            expressions.append(
                DocumentationExpression(statement.span, components, declaration)
            )
    return tuple(sorted(expressions, key=lambda expression: expression.statement.start))


def _components(
    text: str,
    tokens: tuple[PythonToken, ...],
    prefixes: frozenset[str],
    quotes: tuple[str, ...],
    closer: str,
    separator: str,
    case_insensitive: bool,
) -> tuple[SourceSpan, ...]:
    """Accept adjacent plain literals enclosed only by whole-expression parentheses."""
    spellings = [text[token.span.start : token.span.end] for token in tokens]
    start, end = 0, len(tokens)
    if end and tokens[end - 1].kind == "operator" and spellings[end - 1] == separator:
        end -= 1
    while (
        end - start >= 2
        and tokens[start].kind == tokens[end - 1].kind == "operator"
        and spellings[start] == "("
        and spellings[end - 1] == closer
    ):
        start += 1
        end -= 1
    components: list[SourceSpan] = []
    for token, spelling in zip(tokens[start:end], spellings[start:end], strict=True):
        if token.kind != "string":
            return ()
        quote = next((i for i, char in enumerate(spelling) if char in quotes), None)
        if quote is None:
            return ()
        prefix = spelling[:quote]
        if case_insensitive:
            prefix = prefix.lower()
        if prefix not in prefixes:
            return ()
        components.append(token.span)
    return tuple(components)
