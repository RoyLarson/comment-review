"""The imprimatur: the docstrings `proof` was approved to change, per page.

`proof --jacket` writes it beside its drafts and `prove_unchanged` reads it, so
stage 7b lets the same docstrings appear or disappear that stage 7a's proof
let, and no others. It maps each drafted page's repo path to the cues of the
`a` places an accepted alteration set there. A page it does not name may
change none.

A cue names the same declaration on every reading of a page whose code is
unchanged, so one cue holds at the pre-edit ref, at every stage and in the
final draft.
"""

import json
from collections.abc import Collection, Mapping
from pathlib import Path

from comment_review import exceptions
from comment_review.machine.json_object import object_of
from comment_review.machine.repo import write_raw

#: The record's file name in `proof`'s `--out`. No reader claims a `.json`
#: file, so no draft is ever written at this path.
NAME = "imprimatur.json"


def save(out: Path, documented: Mapping[str, Collection[str]]) -> Path:
    """Write the record into `out`; return its path."""
    record = {path: sorted(cues) for path, cues in sorted(documented.items())}
    return write_raw(out / NAME, json.dumps(record, indent=2) + "\n")


def load(path: Path) -> tuple[dict[str, frozenset[str]] | None, list[str]]:
    """The record at `path`, or `(None, every reason it does not read)`."""
    try:
        text = path.read_text(encoding="utf-8")
    except exceptions.READ_ERRORS as err:
        return None, [f"{path}: cannot read ({type(err).__name__})"]
    loaded, why = object_of(text, "record of approved docstrings")
    if why:
        return None, [f"{path}: {why}"]
    bad = [
        f"{path}: {page!r} does not map to a list of cues"
        for page, cues in loaded.items()
        if not isinstance(cues, list) or not all(isinstance(c, str) for c in cues)
    ]
    if bad:
        return None, bad
    return {page: frozenset(cues) for page, cues in loaded.items()}, []
