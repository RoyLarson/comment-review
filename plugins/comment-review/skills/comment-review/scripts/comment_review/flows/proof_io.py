"""The middle's artifacts on disk: the shared loads and saves, and nothing between.

    load_binder(path) -> (Binder | None, problems)
    load_copy(path)   -> (the edit_copy wire dict, problems)
    load_proof(path)  -> (MasterProof | None, problems)
    load_batch(path)  -> (role -> slots, problems)
    load_value(path)  -> (any JSON value, problems)      a role's answers, the rulings
    load_text(path)   -> (the text | None, problems)     the jacket's text
    save_proof(path, proof), save_batch(path, batch)
    save_wire(path, copy)   a role's copy mid-fill, every slot kept

Raw JSON exists at the load and the save only, and each load is three steps: the read
is this module's, the decode is `machine.json_object.object_of`'s, and whether the
object is the artifact it claims is the container's. `load_value` decodes with
`json.loads` itself, because its value need not be an object. A command that reads
through here refuses a file in one wording, and a change to the read is one edit.

Not every read and write is here. `commands/proof.py` reads its docket, proof or copy
itself. `commands/distribute.py` and `commands/topology.py` read a topology with
`Path.read_text`, and `commands/report.py` reads the human's answers file the same way.
`commands/carry.py`, `commands/distribute.py` and `commands/topology.py` write their
own files.
"""

import json
from pathlib import Path

from comment_review import exceptions
from comment_review.binder.binder import Binder
from comment_review.desk.proof.master_proof import MasterProof
from comment_review.machine.json_object import object_of
from comment_review.machine.repo import write_raw


def load_text(path: Path) -> tuple[str | None, list[str]]:
    """The file's text, or the one reason there is none."""
    try:
        return path.read_text(encoding="utf-8"), []
    except exceptions.READ_ERRORS as err:
        return None, [f"cannot read {path}: {err}"]


def _object(path: Path, noun: str) -> tuple[dict | None, list[str]]:
    """The file as a JSON object, or every reason it is not one -- read, then decode."""
    text, why = load_text(path)
    if text is None:
        return None, why
    loaded, problem = object_of(text, noun)
    if problem:
        return None, [f"{path} is {problem}"]
    return loaded, []


def load_value(path: Path) -> tuple[object, list[str]]:
    """The file as any JSON value, or the reason there is none.

    A role's answered batch and the chief's rulings are lists, which
    `object_of` refuses by design; the shape is the caller's question.
    """
    text, why = load_text(path)
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
    """One edit_copy off disk as its wire dict, or `({}, why)`.

    ! A copy loads as its wire dict, not as an `EditCopy`. `commands/collate.py`
    parses the copies itself and reports each refusal beside the role that owes
    it, and `flows.fill` mutates the dicts in place; a loader that parsed them
    here would parse them twice and refuse them once, in the wrong place.
    """
    loaded, why = _object(path, "edit_copy")
    return (loaded, []) if loaded is not None else ({}, why)


def load_proof(path: Path) -> tuple[MasterProof | None, list[str]]:
    """One master proof off disk, or every reason it is not one."""
    loaded, why = _object(path, "master_proof")
    if loaded is None:
        return None, why
    return MasterProof.deserialize(str(path), loaded)


def load_batch(path: Path) -> tuple[dict[str, list], list[str]]:
    """A turn's batch off disk -- role -> its slots, as the fold wrote them.

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


def save_batch(path: Path, batch: dict[str, list[dict]]) -> None:
    """A turn's batch as JSON at `path` -- role -> slots, as the fold shaped them."""
    _dump(path, batch)


def save_wire(path: Path, copy: dict) -> None:
    """A role's copy as its wire dict at `path`, every slot kept.

    ! The dict, not a parsed `EditCopy`. `EditCopy.serialize` writes each sheet through
    `Sheet.serialize`, which writes only the rulings -- a copy mid-fill holds slots
    nobody has ruled on yet, and parsing it to save it would drop every one.
    `commands/mark.py` writes the dict `load_copy` returned, with one ruling placed on
    it or withdrawn from it.
    """
    _dump(path, copy)
