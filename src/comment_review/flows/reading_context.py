"""Resolve installed reading metadata and validate fresh per-file overrides."""

from collections.abc import Mapping
from pathlib import Path, PureWindowsPath
from typing import cast

from comment_review.binder.binder import Binder
from comment_review.binder.page import Page, RedactedPage
from comment_review.desk.proof.edit_copy import EditCopy
from comment_review.desk.proof.master_proof import MasterProof
from comment_review.desk.proof.sheet import Sheet
from comment_review.flows.proof_io import load_value
from comment_review.machine.digests import sha256_hex
from comment_review.reading.context import ReadingContext, resolve_context
from comment_review.reading.context_io import context_from_wire, context_to_wire
from comment_review.reading.diagnostics import ReadDiagnostic, ReadFailure, ReadStage
from comment_review.reading.readers import reader_for

PLACEMENT_REVISION = "1"


def proof_reading_problems(
    proof: MasterProof | dict, where: str = "master_proof"
) -> list[str]:
    """Admit saved proof metadata before any address-dependent work."""
    if isinstance(proof, MasterProof):
        problems = proof.reading_problems(where)
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
        problems = []
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


def _reading_contexts(
    sheets: list | tuple, location: str
) -> tuple[dict[str, ReadingContext], list[str]]:
    contexts: dict[str, ReadingContext] = {}
    problems: list[str] = []
    for index, sheet in enumerate(sheets, 1):
        label = f"{location} sheet {index}"
        if isinstance(sheet, (Sheet, Page, RedactedPage)):
            path, value = sheet.path, sheet.reading
            if isinstance(value, ReadingContext):
                try:
                    validated = ReadingContext(
                        value.language,
                        value.reader,
                        value.compatibility,
                        value.settings,
                    )
                    value = context_to_wire(validated)
                except (TypeError, ValueError):
                    problems.append(f"{label}: malformed reading context; regather")
                    continue
        elif isinstance(sheet, dict):
            path, value = sheet.get("path"), sheet.get("reading")
        else:
            problems.append(f"{label}: a sheet must be an object; regather")
            continue
        if not isinstance(path, str) or not path:
            problems.append(f"{label}: sheet path is missing; regather")
            continue
        saved, why = context_from_wire(f"{label} {path}", value)
        if saved is None:
            problems.extend(why)
            continue
        current = context_for(Path(path), dict(saved.settings))
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
    path: Path, settings: Mapping[str, str]
) -> ReadingContext | ReadFailure:
    """Derive current context from installed definition and runtime metadata."""
    selected = reader_for(path)
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
    return resolve_context(
        definition,
        settings,
        reader_revision=binding.revision,
        placement_revision=PLACEMENT_REVISION,
        grammar_identity=binding.grammar_identity,
        digest=sha256_hex,
    )


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


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """Reject repeated JSON names before a dictionary can discard them."""
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate raw key {key!r}")
        result[key] = value
    return result


def load_settings(
    path: Path, repo: Path
) -> tuple[dict[Path, dict[str, str]], list[str]]:
    """Acquire settings through artifact I/O and normalize relative path keys."""
    value, problems = load_value(path, object_pairs_hook=_unique_object)
    if problems:
        return {}, problems
    if not isinstance(value, dict):
        return {}, [f"{path}: reading settings must be a JSON object"]
    root = repo.resolve()
    result: dict[Path, dict[str, str]] = {}
    for raw, settings in value.items():
        where = f"{path}: entry {raw!r}"
        if not isinstance(raw, str):
            problems.append(f"{where}: path keys must be strings")
            continue
        windows = PureWindowsPath(raw)
        parts = raw.replace("\\", "/").split("/")
        normalized: list[str] = []
        if not raw or windows.drive or windows.root or "\x00" in raw:
            problems.append(f"{where}: path must be nonempty and repo-relative")
            continue
        escaped = False
        for part in parts:
            if part in ("", "."):
                continue
            if part == "..":
                if not normalized:
                    escaped = True
                    break
                normalized.pop()
            else:
                normalized.append(part)
        if escaped or not normalized:
            problems.append(f"{where}: path is empty or escapes the repo")
            continue
        target = (root / Path(*normalized)).resolve()
        if not target.is_relative_to(root):
            problems.append(f"{where}: path escapes the repo")
            continue
        if not isinstance(settings, dict) or any(
            not isinstance(key, str) or not key or not isinstance(item, str)
            for key, item in settings.items()
        ):
            problems.append(
                f"{where}: settings must be an object of nonempty string keys "
                "and string values"
            )
            continue
        if target in result and result[target] != settings:
            problems.append(
                f"{where}: conflicting normalized path "
                f"{target.relative_to(root).as_posix()!r}"
            )
            continue
        choices = cast(dict[str, str], settings)
        context = context_for(target, choices)
        if isinstance(context, ReadFailure):
            problems.extend(
                f"{where}: {diagnostic.message}" for diagnostic in context.diagnostics
            )
            continue
        result[target] = choices
    return ({}, problems) if problems else (result, [])
