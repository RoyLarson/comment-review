"""Rust source boundaries and documentation classification.

`read_rust` is the reader bound to `rust-lexical`: it composes the scan, the
declarations, the documentation and the directives into one `RustRead`.
"""

from comment_review.reading.definitions import LanguageDefinition
from comment_review.reading.diagnostics import ReadFailure
from comment_review.reading.rust.directives import directives_in
from comment_review.reading.rust.documentation import documentation_in
from comment_review.reading.rust.projection import sections_for
from comment_review.reading.rust.records import RustRead
from comment_review.reading.rust.scanner import scan_rust
from comment_review.reading.rust.structure import place_declarations


def read_rust(text: str, definition: LanguageDefinition) -> RustRead | ReadFailure:
    """Read one source string, or return the first stage's refusal."""
    scan = scan_rust(text, definition)
    if isinstance(scan, ReadFailure):
        return scan
    placement = place_declarations(scan, definition)
    if isinstance(placement, ReadFailure):
        return placement
    documentation = documentation_in(scan, placement, definition)
    if isinstance(documentation, ReadFailure):
        return documentation
    protected = directives_in(scan, definition)
    if isinstance(protected, ReadFailure):
        return protected
    return sections_for(scan, documentation, protected)
