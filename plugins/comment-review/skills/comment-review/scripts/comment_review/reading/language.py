"""Language grammar: the shipped definition files.

`references/languages/*.toml` is loaded at import, one file per language, into
`SHIPPED_DEFINITIONS`. Python and Rust are defined that way, and a file no
definition claims has no reader.
"""

from collections.abc import Mapping
from importlib.resources import files
from pathlib import Path

from comment_review.reading.definitions import LanguageDefinition, decode_definition
from comment_review.reading.diagnostics import ReadFailure
from comment_review.reading.registry import LanguageRegistry


def _shipped_definitions() -> tuple[LanguageDefinition, ...]:
    """Every definition file under `references/languages/`, in name order.

    Raises:
        ValueError: a shipped file does not decode; the message names the file.
    """
    folder = files("comment_review").joinpath("references", "languages")
    decoded = []
    for entry in sorted(folder.iterdir(), key=lambda item: item.name):
        if not entry.name.endswith(".toml"):
            continue
        definition = decode_definition(entry.read_text(encoding="utf-8"))
        if isinstance(definition, ReadFailure):
            raise ValueError(f"{entry.name}: {definition.diagnostics[0].message}")
        decoded.append(definition)
    return tuple(decoded)


SHIPPED_DEFINITIONS = _shipped_definitions()
INSTALLED_REGISTRY = LanguageRegistry(SHIPPED_DEFINITIONS)


def line_comment_marker(path: Path) -> str:
    """The marker that opens a line comment in the path's language.

    Python's definition file states it as `marker` under `comments`. Empty
    when a definition does not: a language whose reader scans its own comments,
    as Rust's does, is split by that reader.
    """
    value = INSTALLED_REGISTRY.for_path(path)
    comments = value.rules.get("comments") if value is not None else None
    if not isinstance(comments, Mapping):
        return ""
    marker = comments.get("marker")
    return marker if isinstance(marker, str) else ""


def documents_in_literals(path: Path) -> bool:
    """Whether the path's language documents in the first statement of a body.

    That documentation is a string literal, not a comment, and its definition
    states the position as `first-statement` -- as Python's does.
    """
    value = INSTALLED_REGISTRY.for_path(path)
    if value is None:
        return False
    documentation = value.rules.get("documentation")
    return (
        isinstance(documentation, Mapping)
        and documentation.get("position") == "first-statement"
    )
