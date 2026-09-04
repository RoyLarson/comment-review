"""The master proof on disk: the load and the save, and nothing between.

    load_proof(path) -> (MasterProof | None, problems)
    save_proof(path, proof) -> None

`decision-log.md Process: #65`, `#67`: raw JSON exists at the load and the
save only. The read is this module's, the decode is `machine.json_object`'s,
and whether the object is a master proof is `MasterProof.deserialize`'s --
the three steps `commands/collate.py`'s `_load` gives an edit_copy.

`Process: #87`: the master proof is the state between turns -- the copies as
they stand, the turn record, every Determined, the unsettlable places -- so
`collate` saves it and the verbs that advance and close a turn load it.
"""

import json
from pathlib import Path

from comment_review.desk.containers import MasterProof
from comment_review.machine import exceptions
from comment_review.machine.json_object import object_of


def load_proof(path: Path) -> tuple[MasterProof | None, list[str]]:
    """One master proof off disk, or every reason it is not one.

    Returns:
        `(MasterProof, [])`, or `(None, [messages])` -- the path unreadable,
        the text not an object, or the object refused by the container.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except exceptions.READ_ERRORS as err:
        return None, [f"cannot read {path}: {err}"]
    loaded, why = object_of(text, "master_proof")
    if why:
        return None, [f"{path} is {why}"]
    return MasterProof.deserialize(str(path), loaded)


def save_proof(path: Path, proof: MasterProof) -> None:
    """The proof as JSON at `path` -- the container's own `serialize`, dumped here."""
    path.write_text(
        json.dumps(proof.serialize(), indent=2), encoding="utf-8", newline=""
    )
