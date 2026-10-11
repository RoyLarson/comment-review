"""Explicit installed paragraph readers and language grammar validation."""

import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias

from comment_review.reading.coordinates import SourceCoordinates
from comment_review.reading.definitions import LanguageDefinition
from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage
from comment_review.reading.language import Language
from comment_review.reading.lexer import (
    flag_structural_docs,
    paragraphs_lexical,
    paragraphs_stdlib,
)
from comment_review.reading.paragraph import Paragraph
from comment_review.reading.source import SourceSpan

ParagraphReader: TypeAlias = Callable[
    [Path, str, Language], list[Paragraph] | ReadFailure
]


@dataclass(frozen=True)
class ReaderBinding:
    """Installed callables and metadata independent of the source being read."""

    reader: str
    revision: str
    capabilities: tuple[str, ...]
    grammar_identity: str
    read: ParagraphReader
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
    path: Path, text: str, lang: Language
) -> list[Paragraph] | ReadFailure:
    """Read paragraphs or retain explicit reader refusals before decoration."""
    coordinates = SourceCoordinates(text)
    paragraphs = (
        paragraphs_stdlib(path, text)
        if lang.name == "python"
        else paragraphs_lexical(path, text, lang)
    )
    diagnostics: list[ReadDiagnostic] = []
    for paragraph in paragraphs:
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
    if lang.name != "python":
        flag_structural_docs(paragraphs, text, lang)
    return paragraphs


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
