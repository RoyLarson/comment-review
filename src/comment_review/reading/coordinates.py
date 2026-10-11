"""Physical line coordinates for immutable source text."""

from bisect import bisect_right
from dataclasses import dataclass, field


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


@dataclass(frozen=True)
class SourceCoordinates:
    """Source text with physical line starts cached once at construction."""

    text: str
    _line_starts: tuple[int, ...] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Validate text and cache LF, CRLF, and lone-CR boundaries."""
        if not isinstance(self.text, str):
            raise ValueError("text must be a string")
        line_starts = [0]
        offset = 0
        while offset < len(self.text):
            character = self.text[offset]
            offset += 1
            if character == "\r":
                if offset < len(self.text) and self.text[offset] == "\n":
                    offset += 1
                line_starts.append(offset)
            elif character == "\n":
                line_starts.append(offset)
        object.__setattr__(self, "_line_starts", tuple(line_starts))

    def position(self, offset: int) -> SourcePosition:
        """Locate a character offset, including EOF, in cached physical lines."""
        if (
            not isinstance(offset, int)
            or isinstance(offset, bool)
            or not 0 <= offset <= len(self.text)
        ):
            raise ValueError("Position offset must be an integer within text")
        line = bisect_right(self._line_starts, offset)
        return SourcePosition(line, offset - self._line_starts[line - 1])
