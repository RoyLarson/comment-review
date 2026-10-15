"""Python source boundaries and documentation classification."""

from comment_review.reading.definitions import LanguageDefinition
from comment_review.reading.diagnostics import ReadFailure
from comment_review.reading.python.directives import directives_in
from comment_review.reading.python.documentation import (
    decode_documentation,
    documentation_in,
)
from comment_review.reading.python.projection import paragraphs_for as paragraphs_for
from comment_review.reading.python.projection import sections_for
from comment_review.reading.python.records import PythonRead
from comment_review.reading.python.scanner import scan_python
from comment_review.reading.python.structure import logical_lines, place_declarations


def read_python(text: str, definition: LanguageDefinition) -> PythonRead | ReadFailure:
    """Compose completed recognition stages over one canonical source string."""
    scan = scan_python(text, definition)
    if isinstance(scan, ReadFailure):
        return scan
    lines = logical_lines(scan, definition)
    if isinstance(lines, ReadFailure):
        return lines
    structure = place_declarations(scan, lines, definition)
    if isinstance(structure, ReadFailure):
        return structure
    expressions = documentation_in(scan, structure, definition)
    if isinstance(expressions, ReadFailure):
        return expressions
    payloads = []
    for expression in expressions:
        payload = decode_documentation(scan, expression, definition)
        if isinstance(payload, ReadFailure):
            return payload
        payloads.append(payload)
    directives = directives_in(scan, structure, definition)
    if isinstance(directives, ReadFailure):
        return directives
    return sections_for(scan, structure, tuple(payloads), definition, directives)
