"""Immutable language registration and selection refusals."""

from dataclasses import dataclass
from pathlib import Path

from comment_review.reading.definitions import LanguageDefinition

_EXCLUDED_SUFFIXES = frozenset(
    {
        ".toml",
        ".ini",
        ".yaml",
        ".yml",
        ".json",
        ".jsonl",
        ".md",
        ".markdown",
        ".rst",
        ".txt",
        ".html",
        ".htm",
        ".css",
    }
)


#: The suffixes of source files with no reader. The gather lists these for the
#: reviewers to read as they stand; any other file with no reader is not source
#: and no reviewer is handed it.
_FREEFORM_SUFFIXES = frozenset(
    {
        ".bash",
        ".c",
        ".cc",
        ".cjs",
        ".cpp",
        ".cs",
        ".cts",
        ".cxx",
        ".go",
        ".h",
        ".hpp",
        ".java",
        ".js",
        ".jsx",
        ".kt",
        ".kts",
        ".lua",
        ".mjs",
        ".mts",
        ".rb",
        ".sh",
        ".sql",
        ".swift",
        ".ts",
        ".tsx",
        ".zsh",
    }
)


def is_freeform(path: Path) -> bool:
    """Whether `path` is a source file with no reader, ignoring suffix case."""
    return path.suffix.lower() in _FREEFORM_SUFFIXES


@dataclass(frozen=True)
class LanguageRegistry:
    """Unique language definitions whose code suffix claims do not overlap."""

    definitions: tuple[LanguageDefinition, ...]

    def __post_init__(self) -> None:
        """Reject invalid values and collisions before exposing selection."""
        if not isinstance(self.definitions, tuple) or any(
            not isinstance(value, LanguageDefinition) for value in self.definitions
        ):
            raise ValueError(
                "definitions must be a tuple of LanguageDefinition values",
            )
        identities: set[str] = set()
        for value in self.definitions:
            if value.language in identities:
                raise ValueError(
                    f"duplicate language identity {value.language!r}",
                )
            identities.add(value.language)
        claims: dict[str, str] = {}
        for value in self.definitions:
            for suffix in value.suffixes:
                normalized = suffix.lower()
                if normalized in _EXCLUDED_SUFFIXES:
                    raise ValueError(
                        f"language {value.language!r} claims excluded "
                        f"suffix {suffix!r}",
                    )
                if normalized in claims:
                    raise ValueError(
                        f"suffix {normalized!r} is claimed by languages "
                        f"{claims[normalized]!r} and {value.language!r}",
                    )
                claims[normalized] = value.language

    def for_path(self, path: Path) -> LanguageDefinition | None:
        """Select by the final suffix, ignoring suffix letter case."""
        suffix = path.suffix.lower()
        return next(
            (
                value
                for value in self.definitions
                if any(claim.lower() == suffix for claim in value.suffixes)
            ),
            None,
        )
