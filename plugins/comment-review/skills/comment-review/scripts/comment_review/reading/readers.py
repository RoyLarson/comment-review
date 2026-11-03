"""Explicit installed paragraph readers and language grammar validation."""

import unicodedata
from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace
from pathlib import Path
from types import MappingProxyType
from typing import TypeAlias

from comment_review.reading.definitions import LanguageDefinition
from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage
from comment_review.reading.language import INSTALLED_REGISTRY
from comment_review.reading.python import read_python
from comment_review.reading.python.definition import validate_python
from comment_review.reading.python.records import PythonRead
from comment_review.reading.registry import LanguageRegistry
from comment_review.reading.rust import read_rust
from comment_review.reading.rust.definition import validate_rust
from comment_review.reading.rust.records import RustRead

SourceReader: TypeAlias = Callable[
    [Path, str, LanguageDefinition],
    PythonRead | RustRead | ReadFailure,
]


@dataclass(frozen=True)
class ReaderBinding:
    """Installed callables and metadata independent of the source being read."""

    reader: str
    revision: str
    capabilities: tuple[str, ...]
    grammar_identity: str
    read: SourceReader
    validate: Callable[[LanguageDefinition], ReadFailure | None]

    def __post_init__(self) -> None:
        """Require explicit identities, unique capabilities and callable operations."""
        for field in ("reader", "revision"):
            value = getattr(self, field)
            if not isinstance(value, str) or not value:
                raise ValueError(f"{field} must be a nonempty string")
        if (
            not isinstance(self.capabilities, tuple)
            or any(not isinstance(value, str) for value in self.capabilities)
            or len(set(self.capabilities)) != len(self.capabilities)
        ):
            raise ValueError("capabilities must be a tuple of unique strings")
        if not isinstance(self.grammar_identity, str):
            raise ValueError("grammar_identity must be a string")
        for field in ("read", "validate"):
            if not callable(getattr(self, field)):
                raise ValueError(f"{field} must be callable")


def bind_reader(
    definition: LanguageDefinition, bindings: Mapping[str, ReaderBinding]
) -> ReaderBinding | ReadFailure:
    """Select an installed reader and validate its language rules before reading."""
    binding = bindings.get(definition.reader)
    if (
        binding is None
        or binding.reader != definition.reader
        or not set(definition.capabilities).issubset(binding.capabilities)
    ):
        return ReadFailure(
            (
                ReadDiagnostic(
                    ReadStage.SELECT,
                    "unavailable-reader",
                    f"Reader {definition.reader!r} is unavailable "
                    "for the claimed capabilities",
                ),
            )
        )
    failure = binding.validate(definition)
    return failure if failure is not None else binding


def read_source(
    path: Path,
    text: str,
    *,
    registry: LanguageRegistry = INSTALLED_REGISTRY,
) -> PythonRead | RustRead | ReadFailure:
    """Return the selected reader's admitted records before paragraph decoration."""
    selected = reader_for(path, registry)
    if isinstance(selected, ReadFailure):
        return selected
    if selected is None:
        return ReadFailure(
            (
                ReadDiagnostic(
                    ReadStage.SELECT,
                    "unsupported-language",
                    "No installed code reader for this suffix",
                ),
            )
        )
    definition, binding = selected
    return binding.read(path, text, definition)


def _read_python(
    path: Path, text: str, definition: LanguageDefinition
) -> PythonRead | ReadFailure:
    """Bind canonical Python recognition without paragraph rediscovery."""
    return read_python(text, definition)


def _read_rust(
    path: Path, text: str, definition: LanguageDefinition
) -> RustRead | ReadFailure:
    """Bind Rust recognition without paragraph rediscovery."""
    return read_rust(text, definition)


INSTALLED_BINDINGS = MappingProxyType(
    {
        "rust-lexical": ReaderBinding(
            "rust-lexical",
            "2",
            (
                "comments",
                "strings",
                "declarations",
                "documentation",
                "protected-directives",
                "lexical",
            ),
            "Rust Reference lexical",
            _read_rust,
            validate_rust,
        ),
        "python-lexical": ReaderBinding(
            "python-lexical",
            "2",
            (
                "comments",
                "strings",
                "declarations",
                "documentation",
                "protected-directives",
                "lexical",
            ),
            "Python 3.15 lexical",
            _read_python,
            validate_python,
        ),
    }
)


def reader_for(
    path: Path,
    registry: LanguageRegistry = INSTALLED_REGISTRY,
) -> tuple[LanguageDefinition, ReaderBinding] | ReadFailure | None:
    """Select installed code grammar and validate its binding without reading source."""
    definition = registry.for_path(path)
    if definition is None:
        return None
    binding = bind_reader(definition, INSTALLED_BINDINGS)
    if isinstance(binding, ReadFailure):
        return binding
    if binding.reader == "python-lexical":
        binding = replace(
            binding,
            grammar_identity=(
                f"{binding.grammar_identity}; Unicode {unicodedata.unidata_version}"
            ),
        )
    return definition, binding


def supported_definitions(
    registry: LanguageRegistry = INSTALLED_REGISTRY,
) -> tuple[LanguageDefinition, ...]:
    """Installed coverage whose implementations accept their declared grammar."""
    return tuple(
        definition
        for definition in registry.definitions
        if not isinstance(bind_reader(definition, INSTALLED_BINDINGS), ReadFailure)
    )
