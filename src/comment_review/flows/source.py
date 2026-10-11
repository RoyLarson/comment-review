"""Source acquisition outcomes for filesystem and revision reads."""

import subprocess
from pathlib import Path

from comment_review.machine.repo import Source, git, read_revision_source, read_source
from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage

ACQUIRE_ERRORS = (OSError, subprocess.SubprocessError)


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


def _acquire_failure(error: Exception, code: str = "io-error") -> ReadFailure:
    """Keep the acquisition reason in a stage-specific diagnostic."""
    message = str(error) or type(error).__name__
    if isinstance(error, subprocess.CalledProcessError) and error.stderr:
        reason = error.stderr
        if isinstance(reason, bytes):
            reason = reason.decode("utf-8", errors="replace")
        message = f"{message}: {reason.strip()}"
    return ReadFailure((ReadDiagnostic(ReadStage.ACQUIRE, code, message),))


def source_of(path: Path) -> Source | ReadFailure:
    """Read a filesystem source or report an expected acquisition/decode failure."""
    try:
        return read_source(path)
    except UnicodeDecodeError as error:
        return _decode_failure(error)
    except ACQUIRE_ERRORS as error:
        return _acquire_failure(error)


def revision_source_of(repo: Path, ref: str, rel: str) -> Source | ReadFailure:
    """Read a Git blob or report its expected acquisition/decode failure."""
    try:
        return read_revision_source(repo, ref, rel)
    except UnicodeDecodeError as error:
        return _decode_failure(error)
    except subprocess.CalledProcessError as error:
        try:
            repository = git(repo, "rev-parse", "--git-dir")
        except ACQUIRE_ERRORS:
            return _acquire_failure(error)
        code = "missing-revision-source" if repository.returncode == 0 else "io-error"
        return _acquire_failure(error, code)
    except ACQUIRE_ERRORS as error:
        return _acquire_failure(error)
