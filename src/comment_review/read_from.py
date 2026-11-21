"""Validate the gathered-tree header shared by binders, copies and proofs."""

# The shape's own version, so a reader can say which format it refused rather
# than only that it could not read one.
#
# `Binder.deserialize` refuses on it: a binder whose `version` is not `VERSION`
# is refused by name, and one at version "2" is told it carries no saved
# reading context.
BINDER_VERSION = "4"


def read_from_problem(loaded: dict) -> str:
    """Why a `read_from` cannot be used, or `""`: a binder's, an edit copy's, a proof's.

    MEASURED 2026-08-28, and it is why the check moved here from `seed` alone:
    `distribute --seed` over a version-"1" binder exited 1 with `KeyError:
    'read_from'` and an eight-frame traceback on stderr and nothing on stdout,
    past `main`'s own promise of *"2 when an input could not be read"*.
    `commands/distribute.py:122` calls `seed` immediately after `load_binder`
    returns a binder, and `Binder.deserialize` runs this function first, so a
    field `seed` requires could only surface as a crash. Raising is not
    refusing: a refusal in this module is a named reason, which a command turns
    into an exit code, which is what a reader can act on.

    ! AND THE SHAPE IS CHECKED, NOT ONLY THE PRESENCE. MEASURED the same day:
    `read_from="oops"`, `None`, `[]` and `{"root": 7}` each built a binder, each
    passed `ty`, and `seed` copied the value verbatim onto the `edit_copy`
    handed to an editorial role.
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
    return ""
