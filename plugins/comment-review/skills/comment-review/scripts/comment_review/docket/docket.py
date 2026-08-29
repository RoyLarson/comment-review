"""THE DOCKET: every alteration the write chain is asked to make.

    {"pages": [
        {"path": "pkg/a/util.py",
         "sha":  "e3b0c44298fc",
         "role":  "block-context",
         "alterations": [{"cue": "b1", "text": "# the new comment"},
                         {"cue": "c0", "text": null}]}]}

!! IT IS THE WRITE SIDE'S BINDER, AND THE THREE LEVELS MIRROR IT. Roy,
2026-08-26: *"like the binder we have three levels of containers -- paragraph,
page, binder. We have to be able to unwind the alterations pretty close to the
same way."*

    level       READ                    WRITE
    one place   a row                   an ALTERATION -- a cue, and its text
    one file    a page: path, sha, rows a SCHEDULE: path, sha, alterations
    the whole   the binder: pages       the DOCKET: pages

! A DOCKET IN PRINT PRODUCTION is the instruction paperwork that travels with a
job, which is what this is: what the desk hands the chain that sets type.

!! THE NESTING IS NOT TIDINESS -- IT REMOVES TWO COUPLINGS. Flat, the docket was
one map from address to text, so the per-page grouping had to be DERIVED by
splitting every address, and the path an address carries is FLATTENED
(`pkg:a:util.py`), so something else had to turn it back. `proof_setter` used
the binder's page paths for that, and for the sha.

    flat    address -> text     grouping derived; path flattened; sha from the binder
    nested  pages -> schedule   grouping structural; path real; sha on the page

! MEASURED, on the flat form: `proof_setter.run` used the flattened key both as
a binder key and as a filesystem path, so every alteration on a file below the
repo root refused -- `repo / "pkg:a:util.py"` is invalid on Windows and missing
on POSIX. Every test hand-wrote its address with `/`, so none could disagree.
The nested form has no flattened path to recover.

!! SO THE BINDER DOES NOT REACH THE WRITE CHAIN AT ALL. Roy, 2026-08-25:
*"besides reading the sha and file path/name you should not be assuming any
binder things make it this far."* The docket carries both, which is what makes
that literally true rather than nearly true.

!! THE SHA IS RECORDED, NEVER RECOMPUTED. Roy, 2026-08-25: *"we can't assume
that the file didn't change between original read and loading to write and so
getting it out of the json blob is important."* A sha taken from the file at
write time would ask whether the file equals itself, which cannot fail.

!! IT WAS `desk/notations.py`, A STAND-IN, AND THE NAME COLLIDED. `notations`
sat one letter from the `annotations` that `binder/annotate.py` owns. ! The
instinct was right and that is why it collided -- Roy, 2026-08-26: *"if I was
writing between the lines with marks in red pen I think of those red marks as
notations."* The trade calls those PROOF CORRECTION MARKS, and `mark` is already
this system's word for what a role emits. What needed a name was what the DESK
makes of those marks. `decision-log.md Vocabulary: #14`.

!! `None` IS THE DELETE AND AN EMPTY STRING IS REFUSED. Roy, 2026-08-25: *"None
is explicit enough."* ! The galley took `""` as its vacation signal until this
landed, and a key whose value failed to serialise arrives looking exactly like
a deliberate deletion. Two spellings for one act is how a bug upstream becomes
a deletion downstream at exit 0.

! `role` IS OPTIONAL AND, WHEN PRESENT, ONE PER PAGE -- the role whose mark
settled every alteration this schedule carries. `desk.collator.docket_from`
is what writes it, from T4.2's settled places; `flows.revise.pull._set_by`
reads it back into `address -> role`, the provenance P6's reversal pairs
against. A docket with no `role` field maps every one of its addresses to
`""`, unchanged from before this field existed.
"""

from typing import NamedTuple

from comment_review.machine.json_object import object_of


class Schedule(NamedTuple):
    """One page's alterations, and the page they are checked against.

    Attributes:
        path: as the REPO sees it -- `pkg/a/util.py`, NOT flattened. It is
            joined to the checkout and to the draft directory, so it is the one
            field a containment guard has to rule on.
        sha: of the page's text when the agents read it. `proof_setter` compares
            it against the file it is about to set.
        alterations: cue -> the replacement text, or None to delete.
        role: the role whose mark settled every alteration here, or "" when
            the docket carries none. `proof_setter` does not read this --
            `flows.revise.pull._set_by` does, straight off the raw docket
            dict; carried here so a caller unwinding a docket through
            `schedules_of` sees every field the format defines.
    """

    path: str
    sha: str
    alterations: dict[str, str | None]
    role: str = ""


def read(text: str) -> tuple[dict, str]:
    """The docket, or the reason it could not be read.

    !! IT REFUSES RATHER THAN COPING, which is the shape `binder.read` already
    uses and for the same measured reason: a guess that is wrong reads as an
    EMPTY input, and downstream that is indistinguishable from a run with
    nothing to do.

    !! AN EMPTY DOCKET IS REFUSED BY NAME, which is the same floor `binder.read`
    puts under a missing `pages` key. Measured 2026-08-25 on the flat form:
    `read("{}")` answered `({}, "")`, `proof_setter.run` drafted nothing and
    `commands/proof.py` printed `0 page(s) drafted for review` at exit 0.

    ! THE SHAPE IS CHECKED HERE SO NOTHING DOWNSTREAM HAS TO. `schedules_of`
    unwinds what this returned and asks nothing about it, exactly as
    `binder.rows_of` trusts `binder.read`.

    Args:
        text: the docket file's contents.

    Returns:
        `(docket, "")` when it reads, or `({}, reason)` when it does not.
    """
    loaded, why = object_of(text, "docket")
    if why:
        return {}, why
    if "pages" not in loaded:
        return {}, "no `pages` key -- a docket names the pages it alters"
    pages = loaded["pages"]
    if not isinstance(pages, list) or not pages:
        return {}, "`pages` must be a non-empty list of pages"
    seen: set[str] = set()
    for page in pages:
        if not isinstance(page, dict):
            return {}, f"a page must be an object, not {type(page).__name__}"
        path = page.get("path")
        if not isinstance(path, str) or not path:
            return {}, "every page needs a `path`, as the repo names it"
        # ! ONE SCHEDULE PER PAGE. Two would let a later one silently win, and
        # which of them applied would depend on iteration order.
        if path in seen:
            return {}, f"{path}: two schedules for one page"
        seen.add(path)
        if not isinstance(page.get("sha"), str) or not page["sha"]:
            return {}, f"{path}: every page needs the `sha` it was read at"
        role = page.get("role")
        if role is not None and (not isinstance(role, str) or not role):
            return {}, f"{path}: `role`, when present, must be a non-empty string"
        alterations = page.get("alterations")
        if not isinstance(alterations, list) or not alterations:
            return {}, f"{path}: `alterations` must be a non-empty list"
        cues: set[str] = set()
        for one in alterations:
            if not isinstance(one, dict):
                return {}, f"{path}: an alteration must be an object"
            cue = one.get("cue")
            if not isinstance(cue, str) or not cue:
                return {}, f"{path}: every alteration needs a `cue`"
            if cue in cues:
                return {}, f"{path}@{cue}: two alterations for one place"
            cues.add(cue)
            if "text" not in one:
                return {}, f"{path}@{cue}: an alteration needs `text` (null deletes)"
            replacement = one["text"]
            if replacement is None:
                continue
            if not isinstance(replacement, str):
                return {}, (
                    f"{path}@{cue}: a replacement must be text or null, not"
                    f" {type(replacement).__name__}"
                )
            if not replacement:
                return {}, (
                    f"{path}@{cue}: an empty string is not a delete -- null is."
                    " Two spellings for one act is how a serialisation bug"
                    " becomes a deletion"
                )
    return loaded, ""


def schedules_of(docket: dict) -> list[Schedule]:
    """One `Schedule` per page, in the order the docket lists them.

    !! IT IS NAMED FOR WHAT IT PRODUCES, mirroring `binder.rows_of`. It was
    `by_page`, which named the mechanism -- and the mechanism is what changed
    when the docket started carrying its schedules instead of deriving them.

    ! IT REFUSES NOTHING, and that is the point of the nesting. The flat form
    returned refusals because it had to split an address to find the path, and
    a malformed one could not be split. There is nothing here that can fail:
    `read` has already ruled on the shape.

    Args:
        docket: as `read` returned it.
    """
    return [
        Schedule(
            path=str(page["path"]),
            sha=str(page["sha"]),
            alterations={str(one["cue"]): one["text"] for one in page["alterations"]},
            role=str(page.get("role", "")),
        )
        for page in docket.get("pages", [])
    ]
