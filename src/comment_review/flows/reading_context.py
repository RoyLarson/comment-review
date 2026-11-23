"""Resolve installed reading metadata and admit saved reading contexts."""

from collections.abc import Mapping
from pathlib import Path

from comment_review.binder.binder import Binder
from comment_review.binder.page import Page, RedactedPage
from comment_review.desk.proof.edit_copy import EditCopy
from comment_review.desk.proof.master_proof import (
    MasterProof,
    referenced_reading_problems,
)
from comment_review.desk.proof.sheet import Sheet
from comment_review.docket.docket import Docket, Schedule
from comment_review.reading.context import ReadingContext, resolve_context
from comment_review.reading.context_io import context_from_wire, context_to_wire
from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage
from comment_review.reading.language import INSTALLED_REGISTRY
from comment_review.reading.readers import reader_for
from comment_review.reading.registry import LanguageRegistry


def proof_reading_problems(
    proof: MasterProof | dict, where: str = "master_proof"
) -> list[str]:
    """Admit saved proof metadata before any address-dependent work."""
    if isinstance(proof, MasterProof):
        problems = proof.reading_problems(where)
        if problems:
            return problems
        records = proof.page_readings
        sheets = [sheet for copy in proof.edit_copies for sheet in copy.sheets]
    else:
        records = proof.get("page_readings")
        copies = proof.get("edit_copies", [])
        if not isinstance(copies, list):
            return [f"{where}: edit_copies must be a list; regather"]
        sheets = []
        for copy in copies:
            if not isinstance(copy, dict) or not isinstance(copy.get("sheets"), list):
                return [f"{where}: edit_copy sheets must be a list; regather"]
            sheets.extend(copy["sheets"])
        problems = referenced_reading_problems(proof, where)
        if problems:
            return problems
    if not isinstance(records, dict):
        return [f"{where}: page_readings is missing or malformed; regather"]
    admitted, why = _reading_contexts(
        [
            {
                "path": path,
                "reading": context_to_wire(value)
                if isinstance(value, ReadingContext)
                else value,
            }
            for path, value in records.items()
        ],
        where,
    )
    problems.extend(why)
    sheet_contexts, why = _reading_contexts(sheets, where)
    problems.extend(why)
    for path, context in sheet_contexts.items():
        if admitted.get(path) != context:
            problems.append(
                f"{where}: {path}: sheet reading disagrees with page_readings; regather"
            )
    return problems


def copy_reading_problems(copy: object, where: str = "edit_copy") -> list[str]:
    """Admit sheet metadata without parsing marks or resolving saved addresses."""
    return copy_reading_contexts(copy, where)[1]


def copy_reading_contexts(
    copy: object, where: str = "edit_copy"
) -> tuple[dict[str, ReadingContext], list[str]]:
    """Return admitted saved contexts for readers of a copy's pages."""
    if isinstance(copy, EditCopy):
        role, sheets = copy.role, copy.sheets
    elif isinstance(copy, dict):
        role, sheets = copy.get("role", ""), copy.get("sheets")
    else:
        return {}, [f"{where}: an edit_copy must be an object; regather"]
    location = f"{where}: {role}"
    if not isinstance(sheets, (list, tuple)):
        return {}, [f"{location}: sheets must be a list; regather"]
    return _reading_contexts(sheets, location)


def binder_reading_contexts(
    binder: Binder, where: str = "binder"
) -> tuple[dict[str, ReadingContext], list[str]]:
    """Admit page metadata using the same installed policy as returned sheets."""
    return _reading_contexts(binder.pages, where)


def page_reading_contexts(
    pages: list | tuple, where: str = "pages"
) -> tuple[dict[str, ReadingContext], list[str]]:
    """Admit supplied pages before resolving their saved cues."""
    return _reading_contexts(pages, where)


def docket_reading_contexts(
    docket: Docket, where: str = "docket"
) -> tuple[dict[str, ReadingContext], list[str]]:
    """Admit scheduled contexts before a revise creates output."""
    return _reading_contexts(docket.schedules, where)


def _reading_contexts(
    sheets: list | tuple, location: str
) -> tuple[dict[str, ReadingContext], list[str]]:
    contexts: dict[str, ReadingContext] = {}
    problems: list[str] = []
    for index, sheet in enumerate(sheets, 1):
        label = f"{location} sheet {index}"
        if isinstance(sheet, (Sheet, Page, RedactedPage, Schedule)):
            path, value = sheet.path, sheet.reading
        elif isinstance(sheet, dict):
            path, value = sheet.get("path"), sheet.get("reading")
        else:
            problems.append(f"{label}: a sheet must be an object; regather")
            continue
        if isinstance(value, ReadingContext):
            try:
                validated = ReadingContext(value.language, value.reader)
                value = context_to_wire(validated)
            except (TypeError, ValueError):
                problems.append(f"{label}: malformed reading context; regather")
                continue
        if not isinstance(path, str) or not path:
            problems.append(f"{label}: sheet path is missing; regather")
            continue
        saved, why = context_from_wire(f"{label} {path}", value)
        if saved is None:
            problems.extend(why)
            continue
        current = context_for(Path(path))
        if isinstance(current, ReadFailure):
            problems.extend(
                f"{label} {path}: {diagnostic.message}; regather"
                for diagnostic in current.diagnostics
            )
            continue
        problems.extend(
            f"{label}: {problem}; regather to save a fresh reading context"
            for problem in reading_problems({Path(path): saved}, {Path(path): current})
        )
        if path in contexts and contexts[path] != saved:
            problems.append(f"{label} {path}: conflicting reading contexts; regather")
        contexts[path] = saved
    return ({}, problems) if problems else (contexts, [])


def context_for(
    path: Path,
    *,
    registry: LanguageRegistry = INSTALLED_REGISTRY,
) -> ReadingContext | ReadFailure:
    """Derive the current context from the installed definition and reader."""
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
    return resolve_context(selected[0])


def reading_problems(
    saved: Mapping[Path, ReadingContext], current: Mapping[Path, ReadingContext]
) -> list[str]:
    """Compare saved metadata without reading source or consulting addresses."""
    return [
        f"{path.as_posix()}: current reading context is missing"
        if path not in current
        else f"{path.as_posix()}: reading context differs from saved context"
        for path in sorted(saved)
        if path not in current or saved[path] != current[path]
    ]
