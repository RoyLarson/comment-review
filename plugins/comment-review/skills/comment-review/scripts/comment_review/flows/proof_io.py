"""The middle's artifacts on disk: every load and every save, and nothing between.

    load_binder(path) -> (Binder | None, problems)
    load_copy(path)   -> (the edit_copy wire dict, problems)
    load_proof(path)  -> (MasterProof | None, problems)
    load_batch(path)  -> (role -> slots, problems)
    load_value(path)  -> (any JSON value, problems)      a role's answers, the rulings
    save_proof(path, proof), save_copy(path, copy), save_batch(path, batch)

`decision-log.md Process: #65`, `#67`: raw JSON exists at the load and the
save only, and each load is three steps -- the read is this module's, the
decode is `machine.json_object`'s, and whether the object is the artifact it
claims is the container's. Every command reads through here, so a file is
refused in one wording and a change to the read is one edit.

! A COPY LOADS AS ITS WIRE DICT, NOT AS AN `EditCopy`. The fold parses the
copies itself and reports each refusal beside the role that owes it
(`flows.collate.collate`), and `flows.turn.apply` mutates the dicts in place;
a loader that parsed them here would parse them twice and refuse them once,
in the wrong place.

! THE SAVE IS `machine.repo.write_raw`, the tree's one `newline=""` writer.
`Process: #87`: the master proof is the state between turns -- the copies as
they stand, the turn record, every Determined, the unsettlable places -- so
`collate` saves it and the verbs that advance and close a turn load it.
"""

import json
from pathlib import Path

from comment_review.binder.binder import Binder
from comment_review.desk.containers import EditCopy, MasterProof
from comment_review.machine import exceptions
from comment_review.machine.json_object import object_of
from comment_review.machine.repo import write_raw


def _text(path: Path) -> tuple[str | None, list[str]]:
    """The file's text, or the one reason there is none."""
    try:
        return path.read_text(encoding="utf-8"), []
    except exceptions.READ_ERRORS as err:
        return None, [f"cannot read {path}: {err}"]


def _object(path: Path, noun: str) -> tuple[dict | None, list[str]]:
    """The file as a JSON object, or every reason it is not one -- read, then decode."""
    text, why = _text(path)
    if text is None:
        return None, why
    loaded, problem = object_of(text, noun)
    if problem:
        return None, [f"{path} is {problem}"]
    return loaded, []


def load_value(path: Path) -> tuple[object, list[str]]:
    """The file as ANY JSON value, or the reason there is none.

    A role's answered batch and the chief's rulings are lists, which
    `object_of` refuses by design; the shape is the caller's question.
    """
    text, why = _text(path)
    if text is None:
        return None, why
    try:
        return json.loads(text), []
    except ValueError as err:
        return None, [f"{path} is not JSON: {err}"]


def load_binder(path: Path) -> tuple[Binder | None, list[str]]:
    """One binder off disk, or every reason it is not one."""
    loaded, why = _object(path, "binder")
    if loaded is None:
        return None, why
    return Binder.deserialize(str(path), loaded)


def load_copy(path: Path) -> tuple[dict, list[str]]:
    """One edit_copy off disk as its wire dict, or `({}, why)` -- see the header."""
    loaded, why = _object(path, "edit_copy")
    return (loaded, []) if loaded is not None else ({}, why)


def load_proof(path: Path) -> tuple[MasterProof | None, list[str]]:
    """One master proof off disk, or every reason it is not one."""
    loaded, why = _object(path, "master_proof")
    if loaded is None:
        return None, why
    return MasterProof.deserialize(str(path), loaded)


def load_batch(path: Path) -> tuple[dict[str, list], list[str]]:
    """A turn's batch off disk -- role -> its slots, as `batch_for` wrote it.

    Returns:
        `(batch, [])`, or `({}, [why])` when the file is not an object or
        names no role's slots. A role whose value is not a list is left out.
    """
    loaded, why = _object(path, "batch")
    if loaded is None:
        return {}, why
    batch = {
        role: list(slots) for role, slots in loaded.items() if isinstance(slots, list)
    }
    if not batch:
        return {}, [f"{path} names no role's slots"]
    return batch, []


def _dump(path: Path, data: object) -> None:
    """The one dump: two-space JSON through `write_raw`, endings untouched."""
    write_raw(path, json.dumps(data, indent=2))


def save_proof(path: Path, proof: MasterProof) -> None:
    """The proof as JSON at `path` -- the container's own `serialize`, dumped here."""
    _dump(path, proof.serialize())


def save_copy(path: Path, copy: EditCopy) -> None:
    """An edit_copy as JSON at `path` -- the chief's, as `collate` and `cap` write."""
    _dump(path, copy.serialize())


def save_batch(path: Path, batch: dict[str, list[dict]]) -> None:
    """A turn's batch as JSON at `path` -- role -> slots, as `batch_for` shaped it."""
    _dump(path, batch)
