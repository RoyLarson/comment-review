"""Retained source context and report formatting for read failures."""

from dataclasses import dataclass

from comment_review.reading.coordinates import SourceCoordinates
from comment_review.reading.diagnostics import ReadFailure


@dataclass(frozen=True)
class LocatedReadFailure(ReadFailure):
    """A read failure retaining its path, language, and exact available text."""

    path: str
    language: str | None
    text: str | None

    def __post_init__(self) -> None:
        """Validate diagnostics and their locations against retained text."""
        super().__post_init__()
        _validate_context(self, self.path, self.language, self.text)


@dataclass(frozen=True)
class ContextAdmissionFailure(LocatedReadFailure):
    """Installed metadata cannot admit the context supplied for a page."""


def _validate_context(
    failure: ReadFailure, path: str, language: str | None, text: str | None
) -> None:
    """Reject invalid context and character spans without in-bounds text."""
    if not isinstance(failure, ReadFailure):
        raise ValueError("failure must be a ReadFailure")
    if not isinstance(path, str):
        raise ValueError("path must be a string")
    if language is not None and not isinstance(language, str):
        raise ValueError("language must be a string or None")
    if text is not None and not isinstance(text, str):
        raise ValueError("text must be a string or None")
    for diagnostic in failure.diagnostics:
        if diagnostic.span is not None and (
            text is None or diagnostic.span.end > len(text)
        ):
            raise ValueError("Diagnostic character span requires text within bounds")


def format_failure(
    failure: ReadFailure,
    *,
    path: str,
    language: str | None = None,
    text: str | None = None,
) -> str:
    """Render diagnostics in order with known byte or character locations."""
    if isinstance(failure, LocatedReadFailure):
        if language is None:
            language = failure.language
        if text is None:
            text = failure.text
    _validate_context(failure, path, language, text)
    coordinates = SourceCoordinates(text) if text is not None else None
    lines = []
    label = path + (f" [{language}]" if language is not None else "")
    for diagnostic in failure.diagnostics:
        location = ""
        if diagnostic.span is not None:
            assert coordinates is not None
            position = coordinates.position(diagnostic.span.start)
            location = (
                f" (line {position.line}, one-based; "
                f"column {position.column}, zero-based)"
            )
        elif diagnostic.byte_offset is not None:
            location = f" (byte offset {diagnostic.byte_offset}, zero-based)"
        line = (
            f"{label} {diagnostic.stage.value}/{diagnostic.code}: "
            f"{diagnostic.message}{location}"
        )
        lines.append(line.replace("\r", "\\r").replace("\n", "\\n"))
    return "\n".join(lines)
