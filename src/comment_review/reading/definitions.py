"""Validated immutable language-specific reader configuration."""

from __future__ import annotations

import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import cast

from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage

_WIRE_FIELDS = frozenset(
    {
        "format",
        "language",
        "suffixes",
        "reader",
        "revision",
        "capabilities",
        "defaults",
        "choices",
        "rules",
    }
)


def _array_tuple(value: object, field: str) -> tuple[str, ...]:
    """Require a TOML array before adapting it for value validation."""
    if not isinstance(value, list):
        raise ValueError(f"{field} must be an array of strings")
    return cast(tuple[str, ...], tuple(value))


def decode_definition(text: str) -> LanguageDefinition | ReadFailure:
    """Decode a complete TOML definition, returning expected configuration failures."""
    try:
        fields = tomllib.loads(text)
    except tomllib.TOMLDecodeError as error:
        return _definition_failure(str(error))
    missing = _WIRE_FIELDS - fields.keys()
    if missing:
        return _definition_failure(f"missing fields: {', '.join(sorted(missing))}")
    unknown = fields.keys() - _WIRE_FIELDS
    if unknown:
        return _definition_failure(f"unknown fields: {', '.join(sorted(unknown))}")
    if type(fields["format"]) is not int or fields["format"] != 1:
        return _definition_failure("format must be integer 1")
    try:
        choices = {
            key: _array_tuple(value, f"choices.{key}")
            for key, value in _mapping(fields["choices"], "choices").items()
        }
        return LanguageDefinition(
            language=fields["language"],
            suffixes=_array_tuple(fields["suffixes"], "suffixes"),
            reader=fields["reader"],
            revision=fields["revision"],
            capabilities=_array_tuple(fields["capabilities"], "capabilities"),
            defaults=fields["defaults"],
            choices=choices,
            rules=fields["rules"],
        )
    except ValueError as error:
        return _definition_failure(str(error))


def _definition_failure(message: str) -> ReadFailure:
    """Describe invalid language configuration at reader selection."""
    return ReadFailure(
        (ReadDiagnostic(ReadStage.SELECT, "invalid-language-definition", message),)
    )


def _string_tuple(
    value: object, field: str, *, allow_empty: bool = False
) -> tuple[str, ...]:
    """Validate a tuple of unique strings without changing its spelling."""
    if not isinstance(value, tuple):
        raise ValueError(f"{field} must be a tuple of strings")
    if any(
        not isinstance(item, str) or (not allow_empty and not item) for item in value
    ):
        qualifier = "" if allow_empty else "nonempty "
        raise ValueError(f"{field} must contain {qualifier}strings")
    if len(set(value)) != len(value):
        raise ValueError(f"{field} must contain unique strings")
    return cast(tuple[str, ...], value)


def _mapping(value: object, field: str) -> Mapping[str, object]:
    """Require a mapping with string keys."""
    if not isinstance(value, Mapping):
        raise ValueError(f"{field} must be a mapping")
    if any(not isinstance(key, str) for key in value):
        raise ValueError(f"{field} keys must be strings")
    return cast(Mapping[str, object], value)


def _freeze_rule(value: object, path: str) -> object:
    """Copy rule tables and arrays into immutable containers."""
    if isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, (list, tuple)):
        return tuple(
            _freeze_rule(item, f"{path}[{index}]") for index, item in enumerate(value)
        )
    if isinstance(value, Mapping):
        return MappingProxyType(
            {
                key: _freeze_rule(item, f"{path}.{key}")
                for key, item in _mapping(value, path).items()
            }
        )
    raise ValueError(f"{path} contains unsupported rule value {type(value).__name__}")


@dataclass(frozen=True)
class LanguageDefinition:
    """A complete reader definition with deeply immutable configuration."""

    language: str
    suffixes: tuple[str, ...]
    reader: str
    revision: str
    capabilities: tuple[str, ...]
    defaults: Mapping[str, str]
    choices: Mapping[str, tuple[str, ...]]
    rules: Mapping[str, object]

    def __post_init__(self) -> None:
        """Validate configuration and detach it from caller-owned mappings."""
        for field in ("language", "reader", "revision"):
            value = getattr(self, field)
            if not isinstance(value, str) or not value:
                raise ValueError(f"{field} must be a nonempty string")
        _string_tuple(self.suffixes, "suffixes")
        if any(not suffix.startswith(".") for suffix in self.suffixes):
            raise ValueError("suffixes must start with a dot")
        if len({suffix.lower() for suffix in self.suffixes}) != len(self.suffixes):
            raise ValueError("suffixes must be unique after lowercasing")
        _string_tuple(self.capabilities, "capabilities")
        defaults = _mapping(self.defaults, "defaults")
        choices = _mapping(self.choices, "choices")
        if defaults.keys() != choices.keys():
            raise ValueError("defaults and choices must have the same settings keys")
        for key, raw_options in choices.items():
            if not key:
                raise ValueError("setting keys must be nonempty strings")
            options = _string_tuple(raw_options, f"choices.{key}", allow_empty=True)
            if not options:
                raise ValueError(f"choices.{key} must be nonempty")
            default = defaults[key]
            if not isinstance(default, str) or default not in options:
                raise ValueError(f"defaults.{key} must be a declared string choice")
        object.__setattr__(self, "defaults", MappingProxyType(dict(defaults)))
        object.__setattr__(self, "choices", MappingProxyType(dict(choices)))
        rules = _mapping(self.rules, "rules")
        object.__setattr__(self, "rules", _freeze_rule(rules, "rules"))
