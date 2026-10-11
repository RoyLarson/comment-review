"""Validated character spans and physical source positions."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SourceSpan:
    """A half-open interval of character offsets, including empty points."""

    start: int
    end: int

    def __post_init__(self) -> None:
        """Reject non-integer, negative, or reversed bounds."""
        if (
            not isinstance(self.start, int)
            or isinstance(self.start, bool)
            or not isinstance(self.end, int)
            or isinstance(self.end, bool)
            or not 0 <= self.start <= self.end
        ):
            raise ValueError("Source span requires integer bounds 0 <= start <= end")


@dataclass(frozen=True)
class SourcePosition:
    """A one-based physical line and zero-based character column."""

    line: int
    column: int

    def __post_init__(self) -> None:
        """Reject non-integer values and positions below their lower limits."""
        if (
            not isinstance(self.line, int)
            or isinstance(self.line, bool)
            or not isinstance(self.column, int)
            or isinstance(self.column, bool)
            or self.line < 1
            or self.column < 0
        ):
            raise ValueError(
                "Source position requires integer line >= 1 and column >= 0"
            )
