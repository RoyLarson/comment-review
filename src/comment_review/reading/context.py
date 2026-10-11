"""Immutable identities and effective settings for a saved reading."""

from dataclasses import dataclass
from re import fullmatch


@dataclass(frozen=True)
class ReadingContext:
    """The language, reader, compatibility digest, and effective settings."""

    language: str
    reader: str
    compatibility: str
    settings: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        """Validate identities and settings, then sort settings by key."""
        for name, value in (("language", self.language), ("reader", self.reader)):
            if not isinstance(value, str) or not value:
                raise ValueError(f"{name} must be a nonempty string")
        if not isinstance(self.compatibility, str) or not fullmatch(
            "[0-9a-f]{64}", self.compatibility
        ):
            raise ValueError("compatibility must be a lower-case SHA-256 hex digest")
        if not isinstance(self.settings, tuple):
            raise ValueError("settings must be a tuple of string pairs")
        keys: set[str] = set()
        for pair in self.settings:
            if not isinstance(pair, tuple) or len(pair) != 2:
                raise ValueError("settings must contain tuple pairs")
            key, value = pair
            if not isinstance(key, str) or not key or not isinstance(value, str):
                raise ValueError(
                    "settings require nonempty string keys and string values"
                )
            if key in keys:
                raise ValueError("settings keys must be unique")
            keys.add(key)
        object.__setattr__(self, "settings", tuple(sorted(self.settings)))


def compatible_contexts(saved: ReadingContext, current: ReadingContext) -> bool:
    """Return whether all saved and current context fields match."""
    return saved == current
