"""Explicit installed paragraph readers and language grammar validation."""

import re
import unicodedata
from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace
from functools import partial
from pathlib import Path
from types import MappingProxyType
from typing import TypeAlias

from comment_review.reading.coordinates import SourceCoordinates
from comment_review.reading.definitions import LanguageDefinition
from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage
from comment_review.reading.language import (
    INSTALLED_REGISTRY,
    READER_METADATA,
    Language,
    language_from_definition,
    validate_language_definition,
)
from comment_review.reading.lexer import (
    LexicalRead,
    read_lexical,
)
from comment_review.reading.paragraph import Paragraph
from comment_review.reading.python import read_python
from comment_review.reading.python.definition import validate_python
from comment_review.reading.python.records import PythonRead
from comment_review.reading.registry import LanguageRegistry
from comment_review.reading.rust import read_rust
from comment_review.reading.rust.definition import validate_rust
from comment_review.reading.rust.records import RustRead
from comment_review.reading.source import SourceSpan

SourceReader: TypeAlias = Callable[
    [Path, str, LanguageDefinition],
    LexicalRead | PythonRead | RustRead | ReadFailure,
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


def read_paragraphs(
    path: Path,
    text: str,
    lang: Language,
    *,
    registry: LanguageRegistry = INSTALLED_REGISTRY,
) -> list[Paragraph] | ReadFailure:
    """Adapt the admitted interpretation without repeating source recognition."""
    result = read_source(path, text, registry=registry)
    if isinstance(result, ReadFailure):
        return result
    return result.paragraphs(path)


def read_source(
    path: Path,
    text: str,
    *,
    registry: LanguageRegistry = INSTALLED_REGISTRY,
) -> LexicalRead | PythonRead | RustRead | ReadFailure:
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


def _read_paragraphs(
    path: Path, text: str, definition: LanguageDefinition
) -> LexicalRead | ReadFailure:
    """Run the selected engine and retain its refusal diagnostics."""
    coordinates = SourceCoordinates(text)
    lang = language_from_definition(definition)
    read = read_lexical(path, text, lang)
    diagnostics: list[ReadDiagnostic] = []
    for paragraph in read.found:
        if not isinstance(paragraph, Paragraph):
            raise ValueError("Reader records must be Paragraph values")
        if paragraph.kind == "unparsed":
            diagnostics.append(
                ReadDiagnostic(ReadStage.LEX, "incomplete-read", paragraph.text)
            )
        if "unterminated-paragraph-comment" in paragraph.annotations:
            diagnostics.append(
                ReadDiagnostic(
                    ReadStage.LEX,
                    "unterminated-comment",
                    "Comment has no closing delimiter before end of source",
                    span=_paragraph_source_span(paragraph, coordinates),
                )
            )
    if diagnostics:
        return ReadFailure(tuple(diagnostics))
    return read


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
        **{
            metadata.reader: ReaderBinding(
                reader=metadata.reader,
                revision=metadata.revision,
                capabilities=metadata.capabilities,
                grammar_identity="",
                read=_read_paragraphs,
                validate=partial(validate_language_definition, name),
            )
            for name, metadata in READER_METADATA.items()
        },
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


def tier_for(lang: Language, registry: LanguageRegistry = INSTALLED_REGISTRY) -> str:
    """Validated installed coverage for a language, or empty when unavailable."""
    definition = registry.for_language(lang.name)
    if definition is None:
        return ""
    binding = bind_reader(definition, INSTALLED_BINDINGS)
    return "" if isinstance(binding, ReadFailure) else definition.capabilities[-1]


def _paragraph_source_span(
    paragraph: Paragraph, coordinates: SourceCoordinates
) -> SourceSpan | None:
    """Locate an annotated paragraph's original physical source lines."""
    first, last = paragraph.original_start, paragraph.original_end
    if first is None and last is None:
        return None
    breaks = list(re.finditer(r"\r\n|\r|\n", coordinates.text))
    starts = [0, *(match.end() for match in breaks)]
    if (
        not isinstance(first, int)
        or isinstance(first, bool)
        or not isinstance(last, int)
        or isinstance(last, bool)
        or not 1 <= first <= last <= len(starts)
    ):
        raise ValueError("Paragraph original source lines are invalid")
    start = starts[first - 1]
    end = breaks[last - 1].start() if last <= len(breaks) else len(coordinates.text)
    coordinates.position(start)
    coordinates.position(end)
    return SourceSpan(start, end)
