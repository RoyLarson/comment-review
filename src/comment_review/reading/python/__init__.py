"""Python source boundaries and documentation classification.

`read_python` composes the scan, the declarations, the documentation and the
directives into one `PythonRead`; `paragraphs_for` is re-exported from
`projection`.
"""

from comment_review.reading.definitions import LanguageDefinition
from comment_review.reading.diagnostics import ReadFailure
from comment_review.reading.python.directives import directives_in
from comment_review.reading.python.documentation import (
    decode_documentation,
    documentation_in,
)
from comment_review.reading.python.line_breaks import broken_lines
from comment_review.reading.python.projection import paragraphs_for as paragraphs_for
from comment_review.reading.python.projection import sections_for
from comment_review.reading.python.records import (
    DocumentationExpression,
    PythonPlacement,
    PythonRead,
    PythonScan,
)
from comment_review.reading.python.scanner import scan_python
from comment_review.reading.python.structure import logical_lines, place_declarations


def read_python(text: str, definition: LanguageDefinition) -> PythonRead | ReadFailure:
    """Compose completed recognition stages over one canonical source string.

    A docstring sharing its line with code is first broken onto lines of its
    own, so the read, and every place assigned from it, is of the broken text.
    """
    recognized = _recognize(text, definition)
    if isinstance(recognized, ReadFailure):
        return recognized
    broken = broken_lines(*recognized, definition)
    if broken is not None:
        recognized = _recognize(broken, definition)
        if isinstance(recognized, ReadFailure):
            return recognized
    scan, structure, expressions = recognized
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


def _recognize(
    text: str, definition: LanguageDefinition
) -> (
    tuple[PythonScan, PythonPlacement, tuple[DocumentationExpression, ...]]
    | ReadFailure
):
    """Scan, place declarations and find documentation in one source string."""
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
    return scan, structure, expressions
