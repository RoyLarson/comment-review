"""Name the Rust source a read must keep exactly: the shebang line."""

from comment_review.reading.definitions import LanguageDefinition
from comment_review.reading.diagnostics import ReadFailure
from comment_review.reading.rust.definition import validate_rust
from comment_review.reading.rust.records import RustScan, RustTokenKind
from comment_review.reading.source import SourceSpan


def directives_in(
    scan: RustScan, definition: LanguageDefinition
) -> tuple[SourceSpan, ...] | ReadFailure:
    """The shebang's span, or nothing where the source opens without one.

    The scanner decides what is a shebang from `[rules.directives]` and gives
    it one token and one DIRECTIVE region, so the span is that token's.
    """
    failure = validate_rust(definition)
    if failure is not None:
        return failure
    return tuple(
        token.span for token in scan.tokens if token.kind is RustTokenKind.SHEBANG
    )
