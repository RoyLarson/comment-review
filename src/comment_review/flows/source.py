"""Source acquisition outcomes for filesystem reads."""

from pathlib import Path

from comment_review import constants
from comment_review.machine.repo import Source, read_source
from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage


def _decode_failure(error: UnicodeDecodeError) -> ReadFailure:
    """Retain a decoding reason and an in-bounds byte location when available."""
    offset = error.start if 0 <= error.start < len(error.object) else None
    return ReadFailure(
        (
            ReadDiagnostic(
                ReadStage.DECODE, "invalid-utf8", str(error), byte_offset=offset
            ),
        )
    )


def _acquire_failure(error: OSError) -> ReadFailure:
    """Keep the acquisition reason in a stage-specific diagnostic."""
    message = str(error) or type(error).__name__
    return ReadFailure((ReadDiagnostic(ReadStage.ACQUIRE, "io-error", message),))


def _without_lone_cr(source: Source) -> Source | ReadFailure:
    """The source, or a decode failure when it holds a lone CR."""
    if not constants.holds_lone_cr(source.text):
        return source
    message = "the text holds a CR that no LF follows"
    return ReadFailure((ReadDiagnostic(ReadStage.DECODE, "lone-cr", message),))


def source_of(path: Path) -> Source | ReadFailure:
    """Read a filesystem source or report an expected acquisition/decode failure."""
    try:
        return _without_lone_cr(read_source(path))
    except UnicodeDecodeError as error:
        return _decode_failure(error)
    except OSError as error:
        return _acquire_failure(error)
