"""Immutable language registration and selection refusals."""

from dataclasses import dataclass
from pathlib import Path

from comment_review.reading.definitions import LanguageDefinition
from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage

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


class _RegistryError(ValueError):
    """A construction refusal carrying its selection diagnostic code."""

    def __init__(self, code: str, message: str) -> None:
        """Retain classification alongside the useful value error message."""
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class LanguageRegistry:
    """Unique language definitions whose code suffix claims do not overlap."""

    definitions: tuple[LanguageDefinition, ...]

    def __post_init__(self) -> None:
        """Reject invalid values and collisions before exposing selection."""
        if not isinstance(self.definitions, tuple) or any(
            not isinstance(value, LanguageDefinition) for value in self.definitions
        ):
            raise _RegistryError(
                "invalid-language-definition",
                "definitions must be a tuple of LanguageDefinition values",
            )
        identities: set[str] = set()
        for value in self.definitions:
            if value.language in identities:
                raise _RegistryError(
                    "duplicate-language",
                    f"duplicate language identity {value.language!r}",
                )
            identities.add(value.language)
        claims: dict[str, str] = {}
        for value in self.definitions:
            for suffix in value.suffixes:
                normalized = suffix.lower()
                if normalized in _EXCLUDED_SUFFIXES:
                    raise _RegistryError(
                        "invalid-language-definition",
                        f"language {value.language!r} claims excluded "
                        f"suffix {suffix!r}",
                    )
                if normalized in claims:
                    raise _RegistryError(
                        "ambiguous-language",
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

    def for_language(self, name: str) -> LanguageDefinition | None:
        """Select an exact declared language identity."""
        return next(
            (value for value in self.definitions if value.language == name), None
        )


def registry_for(
    definitions: tuple[LanguageDefinition, ...],
) -> LanguageRegistry | ReadFailure:
    """Construct a registry or report an expected selection refusal."""
    try:
        return LanguageRegistry(definitions)
    except _RegistryError as error:
        return ReadFailure((ReadDiagnostic(ReadStage.SELECT, error.code, str(error)),))
