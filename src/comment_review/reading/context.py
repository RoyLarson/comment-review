"""The immutable identity of a saved reading: its language and reader."""

from dataclasses import dataclass

from comment_review.reading.definitions import LanguageDefinition


@dataclass(frozen=True)
class ReadingContext:
    """The language and reader a file was read with."""

    language: str
    reader: str

    def __post_init__(self) -> None:
        """Require both identities to be nonempty strings."""
        for name, value in (("language", self.language), ("reader", self.reader)):
            if not isinstance(value, str) or not value:
                raise ValueError(f"{name} must be a nonempty string")


def compatible_contexts(saved: ReadingContext, current: ReadingContext) -> bool:
    """Return whether all saved and current context fields match."""
    return saved == current


def resolve_context(definition: LanguageDefinition) -> ReadingContext:
    """Return the reading context a definition reads with."""
    return ReadingContext(definition.language, definition.reader)
