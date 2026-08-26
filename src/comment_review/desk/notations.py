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

from comment_review.reading.addresser import cue_of


def read(text: str) -> tuple[dict[str, str | None], str]:
    """The notations, or the reason they could not be read.

    !! IT REFUSES RATHER THAN COPING, which is the shape `binder.read` already
    uses and for the same measured reason: a guess that is wrong reads as an
    EMPTY input, and downstream that is indistinguishable from a run with
    nothing to do.

    !! AN EMPTY NOTATIONS FILE IS REFUSED BY NAME, which is the same floor
    `binder.read` puts under a missing `pages` key. Measured 2026-08-25:
    `read("{}")` answered `({}, "")`, `proof_setter.run` drafted nothing and
    `commands/proof.py` printed `0 page(s) drafted for review` at exit 0 -- the
    empty-reads-as-success shape this module's own paragraph above forbids.

    ! IT REACHES `commands/galley.py --edits` TOO, which read the same shape
    with a bare `json.loads` until 2026-08-25 and printed `0 page(s) set` at
    exit 0 on `{}`. `SKILL.md` wires a stage to that command, so a run with
    nothing to set has to SKIP the stage rather than call it with an empty file
    -- `TODO/empty-edits-fails-a-stage.md`.

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
    if not loaded:
        return {}, (
            "no notations -- an empty file is not a run with nothing to do."
            " Say which places are being set"
        )
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


def by_page(
    notations: dict[str, str | None],
) -> tuple[dict[str, dict[str, str | None]], list[str]]:
    """Group notations by the file they land on, refusing malformed addresses.

    !! THE ADDRESS ITSELF DETERMINES THE PATH AND CUE. Roy, 2026-08-25:
    *"besides reading the sha and file path/name you should not be assuming
    any binder things make it this far."* Split each address using `cue_of`
    from the addresser. Validation of whether a place exists on the page
    happens in `galley.reset` when the page is read.

    !! THE KEY IS THE FLATTENED PATH -- `pkg:a:util.py`, NOT `pkg/a/util.py`.
    An address carries `flatten`'s form, `cue_of` splits that form back out
    unchanged, and this function KEEPS NO BINDER to turn it into a real path.
    Roy ruled that: the binder does not reach here. `addresser.unflatten` is
    what recovers the path, and the caller holding the page paths is where it
    runs -- `proof_setter.run`.

    ! MEASURED 2026-08-25, BEFORE THAT WAS SAID HERE: `proof_setter.run` used
    this key both as a binder key and as a filesystem path, so every notation
    on a file below the repo root refused -- `repo / "pkg:a:util.py"` is
    invalid on Windows and missing on POSIX. Every test hand-wrote its address
    with `/`, so none of them could disagree.

    !! ONE REFUSAL REFUSES THE WHOLE SET, by ruling. Roy, 2026-08-25: *"fails
    loud amd stops is the right answer for now."* PROVISIONAL -- the
    per-page resumable form belongs to the workflow that writes for real.

    Args:
        notations: address -> replacement text, or None to delete.

    Returns:
        `({flattened path: {cue: replacement}}, [])`, or `({}, refusals)`.
    """
    refused = []
    for address in notations:
        addr = cue_of(address)
        if not addr.path or not addr.cue:
            refused.append(address)
    if refused:
        return {}, [f"{a}: malformed address" for a in sorted(refused)]
    grouped: dict[str, dict[str, str | None]] = {}
    for address, replacement in notations.items():
        addr = cue_of(address)
        grouped.setdefault(str(addr.path), {})[str(addr.cue)] = replacement
    return grouped, []
