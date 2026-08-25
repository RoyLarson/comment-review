"""What the reviewers' marks become, on the way to the galley.

    {"<address>": "<the replacement paragraph>"}   set this place to this text
    {"<address>": null}                            delete what is here

!! A STAND-IN, AND DELIBERATELY SO. Roy, 2026-08-25: *"It is a prototype or
stand in for what might need to be built. It will probably not be what gets
built so don't over engineer it. We need the shape not the concrete
implementation."* The write side is known to work and the middle is not
designed, so this exists to give the chain something to build TO.

! THE NAME IS NOT SETTLED. `notations` sits one letter from the `annotations`
that `binder/annotate.py` already owns for candidate flags on a paragraph.
Deferred, by ruling, until the middle is rewritten --
`TODO/notations-collides-with-annotations.md`.

!! `None` IS THE DELETE AND AN EMPTY STRING IS REFUSED. Roy, 2026-08-25: *"None
is explicit enough."* ! The galley took `""` as its vacation signal until this
landed, and a key whose value failed to serialise arrives looking exactly like
a deliberate deletion. Two spellings for one act is how a bug upstream becomes
a deletion downstream at exit 0.
"""

import json


def read(text: str) -> tuple[dict[str, str | None], str]:
    """The notations, or the reason they could not be read.

    !! IT REFUSES RATHER THAN COPING, which is the shape `binder.read` already
    uses and for the same measured reason: a guess that is wrong reads as an
    EMPTY input, and downstream that is indistinguishable from a run with
    nothing to do.

    Args:
        text: the notations file's contents.

    Returns:
        `(notations, "")` when it reads, or `({}, reason)` when it does not.
    """
    try:
        loaded = json.loads(text)
    # ! ONE CLASS, NOT A TUPLE, so the shipped-code rule against a tuple literal
    # in an `except` does not bite. This is the spelling `binder.read` uses.
    except json.JSONDecodeError as e:
        return {}, f"not JSON ({e})"
    if not isinstance(loaded, dict):
        return {}, f"a JSON {type(loaded).__name__}, not a notations file"
    for address, replacement in loaded.items():
        if replacement is None:
            continue
        if not isinstance(replacement, str):
            return {}, (
                f"{address}: a replacement must be text or null, not"
                f" {type(replacement).__name__}"
            )
        if not replacement:
            return {}, (
                f"{address}: an empty string is not a delete -- null is."
                " Two spellings for one act is how a serialisation bug becomes"
                " a deletion"
            )
    return loaded, ""
