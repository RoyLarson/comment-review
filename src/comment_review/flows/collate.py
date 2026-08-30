"""COLLATE -- one stage's returned edit_copies, folded into the chief's own.

    collate(stage, edit_copies, binder) -> Collated

Seven acts, in order:

    CHECK      every copy's marks, stacked -- `desk.collator.problems_in`
    DRIFT      a returned `raw_text` that is not the seeded one
    DROP       every mark `CHECK` already reported, from what `RECONCILE`
               sees -- `_reconcilable`
    GATHER     `desk.proof.gather` -- the master_proof
    PLACE      `desk.collator.places` -- marks grouped by the place they touch
    RECONCILE  `desk.collator.reconcile` -- settled, escalated, re-read
    RESOLVE    the automatic resolutions, then the fold

!! THE RESOLUTIONS SIT DOWNSTREAM OF `reconcile`, WHICH IS UNTOUCHED.
`desk.collator.Reconciled` is the INTERMEDIATE -- `decision-log.md
Vocabulary: #30` -- and keeps its three lists. What this flow adds is which of
those places need no person, so the collator goes on answering one question.

!! WHAT IT CANNOT RESOLVE IT CARRIES FORWARD NAMED, resolving nothing on its
own. `Process: #22`: sending a place back is an act someone is on record for.

! THE CHECK DOES NOT STOP AT THE FIRST BAD COPY. Roy, 2026-08-30: *"the errors
should be stacked and capable of being read off correctly so that each can be
fixed or sent back to the role."* That is verification's discipline, which
`desk/collator.py`'s own header already states against reconciliation's raise.

!! AND THE DROP IS WHAT LETS THE CHECK'S DISCIPLINE SURVIVE PAST IT.
`desk.collator.places` -- what `reconcile` calls first -- RAISES
`MalformedMark` on the first entry it cannot parse, so handing it a copy
`CHECK` already found broken would abort the whole fold on ONE bad mark
rather than routing it back to its role while the rest of the stage settles.
`_reconcilable` removes every such entry, over a COPY of the edit_copy -- the
caller's own is never mutated. See `_reconcilable`'s own docstring for why
this is a drop and not a stand-down to `desk.mark.untouched`.
"""

from dataclasses import dataclass, field

from comment_review.desk.collator import (
    Placed,
    Problem,
    base_texts,
    drift_in,
    problems_in,
    reconcile,
    tally,
    unruled,
)
from comment_review.desk.mark import Instruction, Mark, parse, untouched
from comment_review.desk.proof import gather
from comment_review.reading.addresser import cue_of, unflatten
from comment_review.results.differences import CannotCompose, compose


@dataclass(frozen=True)
class Collated:
    """What one stage came to, and what is left for a person.

    Attributes:
        chief: the copy chief's `edit_copy` -- one mark per RESOLVED place.
            An ordinary edit_copy; `desk.containers.parse_edit_copy` accepts it
            with no second shape.
        problems: every copy's malformed marks, stacked in copy then mark
            order, each naming the role to send it back to.
        drift: a returned `raw_text` that is not the one the place was seeded
            with, same shape and same routing.
        escalations: places carried forward -- two or more owing marks ruling
            on ONE sentence with different answers.
        rereads: places carried forward -- marks on different sentences whose
            compose refused, plus every place an `add` touches, plus every end
            of a `move` in a cycle.
        unruled: role -> the addresses nobody wrote in.
        tally: role -> how many of each instruction that copy carried.
    """

    chief: dict
    problems: list[Problem] = field(default_factory=list)
    drift: list[Problem] = field(default_factory=list)
    escalations: list[dict] = field(default_factory=list)
    rereads: list[dict] = field(default_factory=list)
    unruled: dict[str, list[str]] = field(default_factory=dict)
    tally: dict[str, dict] = field(default_factory=dict)


def _identical(owing: list[Placed]) -> Mark | None:
    """The one mark to take where every owing mark says the same thing.

    !! SAME INSTRUCTION AND BYTE-IDENTICAL `change`. Two roles that reached one
    answer are not a contest, whatever `reconcile` had to call them -- it
    groups by the sentence ruled on and cannot see that the answers agree.

    ! A DIFFERING INSTRUCTION REFUSES even where the text matches, so no mark
    on the chief's copy ever carries an instruction chosen between two that
    disagreed.

    Returns:
        The role-sorted first mark, or None where they do not all agree.
    """
    first = owing[0].mark
    for placed in owing[1:]:
        if placed.mark.instruction is not first.instruction:
            return None
        if placed.mark.change != first.change:
            return None
    return min(owing, key=lambda placed: placed.role).mark


def _composition(entry: dict, base: str) -> Mark | None:
    """The composed mark for a place whose sides touched no common span.

    !! THE COMPOSED MARK IS A SYNTHESIZED `correct` WHOSE `claim.false` IS THE
    WHOLE BASE, which is true: the whole paragraph is being replaced. It parses,
    which is what lets the chief's copy be an ordinary `edit_copy`.

    ! `sources` IS BOTH SIDES', IN ROLE ORDER. `correct` owes sources, and the
    union is what each side actually cited.

    ! ATTRIBUTION RIDES IN `reason`. `Mark` carries no `set_by`, and what the
    DOCKET says about who set a page is `P4`'s question in SP-4.

    Returns:
        The composed `Mark`, or None where the sides met on some span or where
        fewer than two roles proposed anything.
    """
    owing = entry["marks"]
    sides = {placed.role: placed.mark.change for placed in owing}
    if len(sides) < 2:
        return None
    if len({placed.mark.instruction for placed in owing}) != 1:
        return None
    try:
        text = compose(base, sides)
    except CannotCompose:
        return None
    roles = sorted(sides)
    return Mark(
        address=entry["address"],
        anchor=owing[0].mark.anchor,
        raw_text=base,
        instruction=Instruction.CORRECT,
        claim={"false": base, "true": text},
        reason=(
            "composed from disjoint edits by "
            + ", ".join(roles)
            + " -- each touched a span the others did not"
        ),
        sources=tuple(source for placed in owing for source in placed.mark.sources),
        change=text,
    )


def _resolve(reconciled, base: dict[str, str]) -> tuple[dict, list[dict], list[dict]]:
    """The automatic resolutions over `reconcile`'s three lists.

    Returns:
        `(address -> the one Mark for it, escalations left, rereads left)`.
    """
    resolved: dict[str, Mark] = {}
    escalations: list[dict] = []
    rereads: list[dict] = []

    for entry in reconciled.settled:
        resolved[entry["address"]] = entry["marks"][0].mark

    for entry in reconciled.escalations:
        agreed = _identical(entry["marks"])
        if agreed is None:
            escalations.append(entry)
        else:
            resolved[entry["address"]] = agreed

    for entry in reconciled.rereads:
        composed = _composition(entry, base.get(entry["address"], ""))
        if composed is None:
            rereads.append(entry)
        else:
            resolved[entry["address"]] = composed

    return resolved, escalations, rereads


def _chief_copy(read_from: dict, resolved: dict[str, Mark], proof: dict) -> dict:
    """The copy chief's `edit_copy` -- one mark per resolved place.

    !! ONLY RESOLVED PLACES GET AN ENTRY. `desk.mark.untouched` means NOBODY
    WROTE HERE; a place two roles wrote on that nothing resolved is a different
    fact, so it rides beside this copy in `Collated` rather than being written
    as an empty slot.

    ! PATHS ARE THE REAL ONES. An address carries the FLATTENED path;
    `unflatten` resolves it against the proof's own sheet paths, exactly as
    `docket_from` does, so the sheets name files that are actually there.
    """
    # ! DUPLICATES `desk.collator._real_pages`, which builds the identical
    # (paths, shas) pair over the identical proof shape for `docket_from`.
    # `_real_pages` is a private name in a file this module must not edit, so
    # this loop is its own copy rather than an import of an underscore-prefixed
    # function from another module.
    paths: list[str] = []
    shas: dict[str, str] = {}
    for copy in proof.get("edit_copies", []):
        for sheet in copy.get("sheets", []):
            path = sheet.get("path") if isinstance(sheet, dict) else None
            if isinstance(path, str) and path and path not in shas:
                paths.append(path)
                shas[path] = str(sheet.get("sha", ""))

    sheets: dict[str, dict] = {}
    for address, mark in resolved.items():
        addr = cue_of(address)
        real = unflatten(addr.path, paths) or addr.path
        sheet = sheets.setdefault(
            real, {"path": real, "sha": shas.get(real, ""), "marks": []}
        )
        sheet["marks"].append(mark.as_entry())
    return {
        "role": "copy-chief",
        "read_from": {**read_from},
        "sheets": list(sheets.values()),
    }


def _reconcilable(copy: dict) -> dict:
    """This role's edit_copy with every malformed mark dropped.

    !! FORCED BY THE TESTS, NOT IN THE ORIGINAL BRIEF. `desk.collator.places`
    -- what `reconcile` calls first -- RAISES `MalformedMark` on the first
    entry `desk.mark.parse` refuses, and `problems_in` parses every entry the
    same way, so anything this function drops was already reported in
    `Collated.problems` before `collate` ever reaches `reconcile`.

    !! NECESSARY BECAUSE THE ALTERNATIVE BLOCKS THREE ROLES OVER ONE. A
    simpler fix -- refuse the whole run where `problems` is non-empty -- was
    considered and rejected, ruled by Roy 2026-08-30: `Problem(role, address,
    message)` exists precisely so "the errors should be stacked and capable
    of being read off correctly so that each can be fixed or sent back to the
    role." Per-role routing means one role's bad mark must not stop the other
    roles' work from settling; a refusal here would do exactly that, over the
    whole stage, for a defect that names one role and one place.

    ! A MALFORMED ENTRY IS DROPPED, NOT STOOD DOWN TO `desk.mark.untouched`.
    `places` already skips a `marks` entry two ways -- when `untouched(entry)`
    is True, and when the entry is simply absent from the list -- and dropping
    takes the second path. Standing one down to `Mark.seed`'s shape would
    write `instruction: None`, which is what `untouched` reads as *nobody
    wrote here*; a malformed mark means a role DID write here and got the
    shape wrong. Giving those two facts one representation is the same
    conflation `untouched`'s own docstring exists to forbid, in the other
    direction. Dropping keeps them apart, and needs no `Mark.seed` call.

    ! THE INFORMATION IS NOT LOST EITHER WAY. `problems_in` runs on the
    ORIGINAL copy, before this function touches it, so the role and the
    address are already captured in `Collated.problems` by the time this
    drops the entry from what `reconcile` sees.

    Returns:
        A NEW edit_copy dict -- new `sheets` and `marks` lists -- so the
        caller's own containers are never mutated. A sheet or a `marks` list
        that is not the expected shape is passed through unchanged; the check
        above has already named that as its own problem.
    """
    sheets = []
    for sheet in copy.get("sheets", []):
        if not isinstance(sheet, dict) or not isinstance(sheet.get("marks"), list):
            sheets.append(sheet)
            continue
        marks = []
        for entry in sheet["marks"]:
            if not isinstance(entry, dict):
                continue
            if untouched(entry):
                marks.append(entry)
                continue
            where = str(entry.get("address") or "a mark")
            mark, _why = parse(where, entry)
            if mark is not None:
                marks.append(entry)
        sheets.append({**sheet, "marks": marks})
    return {**copy, "sheets": sheets}


def collate(stage: str, edit_copies: list[dict], binder: dict) -> Collated:
    """One stage's returned copies, checked, reconciled and folded.

    Args:
        stage: the label these copies were dispatched under -- "4a", "4c".
        edit_copies: one per role, or one per SHARD under fan-out, as each came
            back.
        binder: the binder they were seeded from. ! IT SUPPLIES THE BASE AND
            THE OTHER SIDE OF THE DRIFT CHECK, and nothing else -- address
            integrity over the docket is `P28`'s.

    Returns:
        A `Collated`.

    Raises:
        desk.collator.UnnamedRole: a copy carries no `role`. ! `_reconcilable`
            works entry by entry and cannot repair this -- a missing `role` is
            a fact about the whole copy, not about any one mark -- so it is
            the one way `places` still refuses here.
        desk.proof.MismatchedRoot: two copies were censused from different
            roots.

    ! `desk.collator.MalformedMark` NEVER REACHES A CALLER OF `collate`.
    `_reconcilable` drops every entry `places` would otherwise refuse before
    `reconcile` runs, so the raise `places` itself still documents cannot fire
    from here.
    """
    base = base_texts(binder)
    problems: list[Problem] = []
    drift: list[Problem] = []
    left: dict[str, list[str]] = {}
    counts: dict[str, dict] = {}
    for copy in edit_copies:
        found, _ruled = problems_in(copy)
        problems += found
        drift += drift_in(copy, base)
        role = str(copy.get("role") or "")
        left[role] = unruled(copy)
        counts[role] = tally(copy)

    proof = gather(stage, [_reconcilable(copy) for copy in edit_copies])
    reconciled = reconcile(proof)
    resolved, escalations, rereads = _resolve(reconciled, base)
    return Collated(
        chief=_chief_copy(proof.get("read_from", {}), resolved, proof),
        problems=problems,
        drift=drift,
        escalations=escalations,
        rereads=rereads,
        unruled=left,
        tally=counts,
    )
