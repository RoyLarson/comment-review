"""Immutable read failures with stage-specific source locations."""

from dataclasses import dataclass
from enum import StrEnum
from typing import TypeAlias

from comment_review.reading.source import SourceSpan, SourceStructure


class ReadStage(StrEnum):
    """The operation that reported a read condition."""

    ACQUIRE = "acquire"
    DECODE = "decode"
    SELECT = "select"
    LEX = "lex"
    PLACE = "place"


@dataclass(frozen=True)
class ReadDiagnostic:
    """A read condition with an optional byte or character location."""

    stage: ReadStage
    code: str
    message: str
    span: SourceSpan | None = None
    byte_offset: int | None = None

    def __post_init__(self) -> None:
        """Validate field types and the location allowed at each stage."""
        if not isinstance(self.stage, ReadStage):
            raise ValueError("Diagnostic stage must be a ReadStage")
        for name in ("code", "message"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"Diagnostic {name} must be a nonblank string")
        if self.span is not None and not isinstance(self.span, SourceSpan):
            raise ValueError("Diagnostic span must be a SourceSpan or None")
        if self.byte_offset is not None and (
            not isinstance(self.byte_offset, int)
            or isinstance(self.byte_offset, bool)
            or self.byte_offset < 0
        ):
            raise ValueError("Diagnostic byte_offset must be a nonnegative integer")
        if self.span is not None and self.byte_offset is not None:
            raise ValueError("Diagnostic character and byte locations are exclusive")
        if self.span is not None and self.stage not in (ReadStage.LEX, ReadStage.PLACE):
            raise ValueError("Diagnostic character spans require lex or place stage")
        if self.byte_offset is not None and self.stage != ReadStage.DECODE:
            raise ValueError("Diagnostic byte locations require decode stage")


@dataclass(frozen=True)
class ReadFailure:
    """A nonempty immutable tuple of read diagnostics."""

    diagnostics: tuple[ReadDiagnostic, ...]

    def __post_init__(self) -> None:
        """Require at least one diagnostic without coercing supplied records."""
        if not isinstance(self.diagnostics, tuple) or not self.diagnostics:
            raise ValueError("Read failure diagnostics must be a nonempty tuple")
        if any(not isinstance(item, ReadDiagnostic) for item in self.diagnostics):
            raise ValueError(
                "Read failure diagnostics must contain ReadDiagnostic values"
            )


SourceRead: TypeAlias = SourceStructure | ReadFailure
