"""THE DOCKET: every alteration the write chain is asked to make.

    {"<address>": "<the replacement paragraph>"}   set this place to this text
    {"<address>": null}                            delete what is here

!! IT IS THE WRITE SIDE'S BINDER, AND THE THREE LEVELS MIRROR IT. Roy,
2026-08-26: *"like the binder we have three levels of containers -- paragraph,
page, binder. We have to be able to unwind the alterations pretty close to the
same way."*

    level       READ            WRITE
    one place   a row           an ALTERATION -- the cue, and what it becomes
    one file    a page          a SCHEDULE -- that page's alterations
    the whole   the binder      the DOCKET

! A DOCKET IN PRINT PRODUCTION is the instruction paperwork that travels with a
job, which is what this is: what the desk hands the chain that sets type.

!! THE SHAPE IS STILL FLAT, AND THE THREE LEVELS ARE NOT BUILT YET. What is on
disk is one map from address to text; `schedules_of` derives the per-page
grouping by splitting each address. The nested form -- pages, each carrying its
path, its sha and its schedule -- is task 4 of
`TODO/notations-collides-with-annotations.md`. ! Until it lands, the sha still
comes from the binder, which is the coupling the nested form exists to remove.

!! IT WAS `desk/notations.py`, A STAND-IN, AND THE NAME COLLIDED. Roy,
2026-08-25, naming it: *"It is a prototype or stand in for what might need to be
built ... We need the shape not the concrete implementation."* `notations` sat
one letter from the `annotations` that `binder/annotate.py` owns for candidate
flags on a paragraph. ! The instinct was right and that is why it collided --
Roy, 2026-08-26: *"if I was writing between the lines with marks in red pen I
think of those red marks as notations."* The trade calls those PROOF CORRECTION
MARKS, and `mark` is already this system's word for what a role emits. What
needed a name was what the DESK makes of those marks. `decision-log.md
Vocabulary: #14`.

!! `None` IS THE DELETE AND AN EMPTY STRING IS REFUSED. Roy, 2026-08-25: *"None
is explicit enough."* ! The galley took `""` as its vacation signal until this
landed, and a key whose value failed to serialise arrives looking exactly like
a deliberate deletion. Two spellings for one act is how a bug upstream becomes
a deletion downstream at exit 0.
"""

from comment_review.machine.json_object import object_of
from comment_review.reading.addresser import cue_of


def read(text: str) -> tuple[dict[str, str | None], str]:
    """The docket, or the reason it could not be read.

    !! IT REFUSES RATHER THAN COPING, which is the shape `binder.read` already
    uses and for the same measured reason: a guess that is wrong reads as an
    EMPTY input, and downstream that is indistinguishable from a run with
    nothing to do.

    !! AN EMPTY DOCKET IS REFUSED BY NAME, which is the same floor `binder.read`
    puts under a missing `pages` key. Measured 2026-08-25: `read("{}")` answered
    `({}, "")`, `proof_setter.run` drafted nothing and `commands/proof.py`
    printed `0 page(s) drafted for review` at exit 0 -- the empty-reads-as-
    success shape this module's own paragraph above forbids.

    ! IT REACHED THE GALLEY COMMAND'S `--edits` TOO, which read the same shape
    with a bare `json.loads` until 2026-08-25 and printed `0 page(s) set` at
    exit 0 on `{}`; that command is now the old NAME for `proof` and reads
    nothing of its own -- `docs/history.md`. `SKILL.md` still wires a stage to
    the name, so a run with nothing to set has to SKIP the stage rather than
    call it with an empty file -- `TODO/empty-edits-fails-a-stage.md`.

    Args:
        text: the docket file's contents.

    Returns:
        `(alterations, "")` when it reads, or `({}, reason)` when it does not.
    """
    # ! THE PARSE AND THE OBJECT GUARD ARE `json_object.object_of`'s. They were
    # spelled out here and in `binder.read`, byte-identical but for the noun.
    # What stays here is what a DOCKET is: non-empty, text or null.
    loaded, why = object_of(text, "docket")
    if why:
        return {}, why
    if not loaded:
        return {}, (
            "no alterations -- an empty docket is not a run with nothing to do."
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


def schedules_of(
    alterations: dict[str, str | None],
) -> tuple[dict[str, dict[str, str | None]], list[str]]:
    """One schedule per page: the alterations landing on each file.

    !! IT IS NAMED FOR WHAT IT PRODUCES, mirroring `binder.rows_of`. It was
    `by_page`, which named the mechanism -- and the mechanism is the part that
    changes when the docket carries its schedules instead of deriving them.

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
    this key both as a binder key and as a filesystem path, so every alteration
    on a file below the repo root refused -- `repo / "pkg:a:util.py"` is
    invalid on Windows and missing on POSIX. Every test hand-wrote its address
    with `/`, so none of them could disagree.

    !! ONE REFUSAL REFUSES THE WHOLE SET, by ruling. Roy, 2026-08-25: *"fails
    loud amd stops is the right answer for now."* PROVISIONAL -- the
    per-page resumable form belongs to the workflow that writes for real.

    Args:
        alterations: address -> replacement text, or None to delete.

    Returns:
        `({flattened path: {cue: replacement}}, [])`, or `({}, refusals)`.
    """
    # ! ONE `cue_of` PER ADDRESS. It was split into a checking pass and a
    # grouping pass, each taking the address apart again, so the two could read
    # one address as two different splits.
    refused = []
    schedules: dict[str, dict[str, str | None]] = {}
    for address, replacement in alterations.items():
        addr = cue_of(address)
        if not addr.path or not addr.cue:
            refused.append(address)
            continue
        schedules.setdefault(str(addr.path), {})[str(addr.cue)] = replacement
    if refused:
        return {}, [f"{a}: malformed address" for a in sorted(refused)]
    return schedules, []
