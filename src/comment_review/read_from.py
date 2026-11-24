"""Validate the gathered-tree header shared by binders, copies and proofs.

`BINDER_VERSION` is the binder's format number. `read_from_problem` names it
in the refusal for a header with no `read_from`, and `binder.binder`
imports it as `VERSION`.
"""

# The shape's own version, so a reader can say which format it refused rather
# than only that it could not read one.
#
# `Binder.deserialize` refuses on it: a binder whose `version` is not `BINDER_VERSION`
# is refused by name, and one at version "2" is told it carries no saved
# reading context.
BINDER_VERSION = "4"


def read_from_problem(loaded: dict) -> str:
    """Why a `read_from` cannot be used, or `""`: a binder's, an edit copy's, a proof's.

    `{"root": str, "revise": int}`, and `"stage": str` where `stage open`
    built the tree for a stage.

    The check is here, not in `seed` alone: `commands.distribute.main` calls
    `seed` immediately after `load_binder` returns a binder, and
    `Binder.deserialize` runs this function once its `pages` read, so a field
    `seed` requires and nothing checked could only surface as a crash. Raising
    is not refusing: a refusal in this module is a named reason, which a command
    turns into an exit code, which is what a reader can act on.

    ! The shape is checked, not only the presence. A `read_from` of `"oops"`,
    `None`, `[]` or `{"root": 7}` would otherwise build a binder and pass `ty`,
    and `seed` would copy it verbatim onto the `edit_copy` handed to an
    editorial role.
    """
    if "read_from" not in loaded:
        return (
            "carries no `read_from` -- a binder written before 2026-08-28 "
            f'(version "1"); re-run `gather` to get a version "{BINDER_VERSION}" one'
        )
    read_from = loaded["read_from"]
    if not isinstance(read_from, dict):
        kind = type(read_from).__name__
        return f"`read_from` is a JSON {kind}, not a mapping of `root` and `revise`"
    if not isinstance(read_from.get("root"), str):
        return "`read_from` carries no `root` string -- which tree was gathered?"
    if not isinstance(read_from.get("revise"), int):
        return "`read_from` carries no `revise` number -- 0 is the original"
    # `stage open` stamps the stage the tree was built for; a plain gather does not.
    if not isinstance(read_from.get("stage", ""), str):
        return "`read_from`'s `stage` is not a stage name"
    return ""
