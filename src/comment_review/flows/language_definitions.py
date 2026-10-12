"""Acquire and decode complete sets of language definition files."""

from collections.abc import Sequence
from dataclasses import replace
from pathlib import Path

from comment_review.flows.source import source_of
from comment_review.reading.definitions import LanguageDefinition, decode_definition
from comment_review.reading.diagnostics import ReadFailure


def load_definitions(
    paths: Sequence[Path],
) -> tuple[LanguageDefinition, ...] | ReadFailure:
    """Read definitions in order or return a failure identifying its file."""
    definitions = []
    for path in paths:
        source = source_of(path)
        if isinstance(source, ReadFailure):
            return _with_path(source, path)
        definition = decode_definition(source.text)
        if isinstance(definition, ReadFailure):
            return _with_path(definition, path)
        definitions.append(definition)
    return tuple(definitions)


def _with_path(failure: ReadFailure, path: Path) -> ReadFailure:
    """Retain diagnostic details while identifying the originating file."""
    return ReadFailure(
        tuple(
            replace(diagnostic, message=f"{path}: {diagnostic.message}")
            for diagnostic in failure.diagnostics
        )
    )
