"""Rust source boundaries and documentation classification.

`read_rust` is the reader bound to `rust-lexical`; it reads nothing yet.
"""

from comment_review.reading.definitions import LanguageDefinition
from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage


def read_rust(text: str, definition: LanguageDefinition) -> ReadFailure:
    """Refuse every source: the Rust reader is not finished."""
    return ReadFailure(
        (
            ReadDiagnostic(
                ReadStage.LEX,
                "reader-unfinished",
                "The Rust reader is not finished and reads no source",
            ),
        )
    )
