"""Immutable identities and effective settings for a saved reading."""

import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass, fields
from re import fullmatch

from comment_review.reading.definitions import LanguageDefinition
from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage


def _json_value(value: object) -> object:
    """Convert immutable definition containers to JSON tables and arrays."""
    if isinstance(value, Mapping):
        return {key: _json_value(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    return value


def compatibility_identity(
    definition: LanguageDefinition,
    *,
    reader_revision: str,
    placement_revision: str,
    grammar_identity: str,
    digest: Callable[[bytes], str],
) -> str:
    """Hash the complete definition and explicit recognition revisions."""
    for name, value in (
        ("reader_revision", reader_revision),
        ("placement_revision", placement_revision),
    ):
        if not isinstance(value, str) or not value:
            raise ValueError(f"{name} must be a nonempty string")
    if not isinstance(grammar_identity, str):
        raise ValueError("grammar_identity must be a string")
    canonical = json.dumps(
        {
            "definition": {
                field.name: _json_value(getattr(definition, field.name))
                for field in fields(definition)
            },
            "reader_revision": reader_revision,
            "placement_revision": placement_revision,
            "grammar_identity": grammar_identity,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return digest(canonical.encode("utf-8"))


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


def resolve_context(
    definition: LanguageDefinition,
    overrides: Mapping[str, str],
    *,
    reader_revision: str,
    placement_revision: str,
    grammar_identity: str,
    digest: Callable[[bytes], str],
) -> ReadingContext | ReadFailure:
    """Resolve fresh settings using only the definition's declared choices."""
    problems: list[str] = []
    if not isinstance(overrides, Mapping):
        problems.append("settings must be a mapping of string choices")
    else:
        for key, value in overrides.items():
            if not isinstance(key, str) or not key or not isinstance(value, str):
                problems.append(
                    "settings require nonempty string keys and string values"
                )
            elif key not in definition.choices:
                problems.append(f"unknown setting {key!r} for {definition.language}")
            elif value not in definition.choices[key]:
                problems.append(f"unsupported choice {value!r} for setting {key!r}")
    if problems:
        return ReadFailure(
            tuple(
                ReadDiagnostic(ReadStage.SELECT, "invalid-reading-settings", message)
                for message in problems
            )
        )
    effective = dict(definition.defaults)
    effective.update(overrides)
    return ReadingContext(
        definition.language,
        definition.reader,
        compatibility_identity(
            definition,
            reader_revision=reader_revision,
            placement_revision=placement_revision,
            grammar_identity=grammar_identity,
            digest=digest,
        ),
        tuple(sorted(effective.items())),
    )
