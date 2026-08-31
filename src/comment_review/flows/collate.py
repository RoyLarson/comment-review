"""COLLATE -- one stage's returned edit_copies, folded into the chief's own.

    collate(stage, edit_copies, binder) -> Collated

Eight acts, in order:

    CHECK      every copy's marks, stacked -- `desk.collator.problems_in`
    DRIFT      a returned `raw_text` that is not the seeded one
    DROP       every mark `CHECK` already reported, from what `RECONCILE`
               sees -- `_reconcilable`
    GATHER     `desk.proof.gather` -- the master_proof
    PLACE      `desk.collator.places` -- marks grouped by the place they touch
    RECONCILE  `desk.collator.reconcile` -- settled, escalated, re-read
    RESOLVE    the automatic resolutions -- `_resolve`
    ORDER      a `move` at one end only is withdrawn, then the survivors are
               ordered vacate-before-fill or carried forward as a named cycle
               -- `_pair_moves`, `_move_order` -- before the fold

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
from comment_review.desk.containers import EditCopy, Sheet, parse_edit_copy
from comment_review.desk.mark import Instruction, Mark, parse, untouched
from comment_review.desk.proof import gather
from comment_review.reading.addresser import cue_of, unflatten
from comment_review.results.differences import CannotCompose, compose


@dataclass(frozen=True)
class Collated:
    """What one stage came to, and what is left for a person.

    Attributes:
        chief: the copy chief's `edit_copy` -- one mark per RESOLVED place,
            except a `move`, whose two resolved places (origin and
            destination) share the ONE entry `_chief_copy` writes at the
            origin -- see that function's docstring for why a second entry
            at the destination cannot parse. An ordinary edit_copy;
            `desk.containers.parse_edit_copy` accepts it with no second shape.
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
        order: the resolved `move` origins, in an order that vacates every
            address before it is filled. Ties broken by address, so a stranger
            re-derives it. Empty where no move resolved.
    """

    chief: dict
    problems: list[Problem] = field(default_factory=list)
    drift: list[Problem] = field(default_factory=list)
    escalations: list[dict] = field(default_factory=list)
    rereads: list[dict] = field(default_factory=list)
    unruled: dict[str, list[str]] = field(default_factory=dict)
    tally: dict[str, dict] = field(default_factory=dict)
    order: list[str] = field(default_factory=list)


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
    # !! `sources` WALKS `roles`, THE SAME ALPHABETICAL ORDER AS `reason`
    # BELOW -- not `owing`'s DISPATCH order, which is an accident of how
    # `edit_copies` was handed to `collate` and not a property of the data.
    # `differences.compose` already sorts its own `roles` the same way, so
    # alphabetical is the order a reader can re-derive without knowing what
    # order the copies arrived in.
    sources_by_role = {placed.role: placed.mark.sources for placed in owing}
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
        sources=tuple(source for role in roles for source in sources_by_role[role]),
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


def _touched_by(mark: Mark) -> list[str]:
    """Every address one mark lands on -- its own, and a `move`'s destination.

    ! THE SAME RULE `desk.collator._touches` APPLIES ONE LAYER UP, restated
    here rather than imported because that function is private to the module
    that groups places, and this one decides an ORDER. Both are read off
    `Instruction.MOVE` and `claim.to`, so neither can drift into a different
    idea of what a move touches without the other's tests going red.
    """
    touched = [mark.address] if mark.address else []
    if mark.instruction is Instruction.MOVE:
        destination = mark.claim.get("to")
        if isinstance(destination, str) and destination and destination not in touched:
            touched.append(destination)
    return touched


def _pair_moves(resolved: dict[str, Mark]) -> set[str]:
    """Addresses to withdraw, so no `move` is resolved at one end only.

    !! A `move` IS ONE INSTRUCTION AT TWO PLACES -- a delete at the origin and
    a write at the destination -- so resolving one end and not the other
    applies HALF of it: the paragraph read twice, or deleted and never
    rewritten. `desk.collator._join_moves` states the same rule over outcomes;
    this states it over resolutions.

    ! IT RUNS TO A FIXED POINT, because moves chain: withdrawing one pair can
    orphan the next.

    !! THE WITHDRAWAL BRANCH CANNOT FIRE THROUGH `collate()` TODAY. Per
    `TODO/collator-defects.md` T15's ruling on `TODO/galley-refusals-cannot-fire.md`
    -- a guard at the boundary and a guard at the point of use is defensible
    depth, and the guard stays, but say which one is load-bearing -- the
    load-bearing guard here is `desk.collator._join_moves`, called inside
    `reconcile`: it gives both ends of one `move` the SAME outcome (`settled`,
    `escalations` or `rereads`) before `_resolve` ever builds `resolved`, so a
    `move` cannot enter `resolved` at one end without its other end beside it.
    This function is depth -- reachable only if a caller assembled `resolved`
    some other way, which is exactly what `tests/test_collate.py`'s direct-call
    tests do, since `TODO/collator-defects.md` T15's template is a guard proved
    checkable on its own rather than merely asserted.

    Returns:
        The addresses whose resolution must be given up.
    """
    withdrawn: set[str] = set()
    changed = True
    while changed:
        changed = False
        for address, mark in resolved.items():
            if address in withdrawn or mark.instruction is not Instruction.MOVE:
                continue
            ends = _touched_by(mark)
            if any(end not in resolved or end in withdrawn for end in ends):
                for end in ends:
                    if end in resolved and end not in withdrawn:
                        withdrawn.add(end)
                        changed = True
    return withdrawn


def _move_order(resolved: dict[str, Mark]) -> tuple[list[str], list[str]]:
    """The resolved MOVES in an order safe to apply, and any caught in a cycle.

    !! THE EDGE IS "VACATE BEFORE FILL". For two moves B and A, B must run
    first when B's ORIGIN is A's DESTINATION -- otherwise A writes that address
    and B then deletes it, and A's change is gone.

    ! TIES ARE BROKEN BY ADDRESS, so a stranger can re-derive the order and two
    runs over the same inputs produce the same list.

    ! A CYCLE IS RETURNED, NOT RAISED. Roy, 2026-08-30: *"we can't allow
    circles so it has to resolve from a DAG."* The caller carries those places
    forward as re-reads and names them, which is what `Process: #22` asks --
    sending a place back is an act someone is on record for.

    ! A SELF-MOVE CANNOT REACH HERE. `desk.mark.parse` refuses `claim.to ==
    address` (Task 5), so the length-one cycle is gone before resolution.

    !! AND NO CYCLE OR CHAIN OF LENGTH TWO OR MORE REACHES HERE THROUGH
    `collate()` TODAY EITHER. `desk.collator._sentence_key` returns `id(mark)`
    for a `move`, so two moves sharing a touched address never compare as the
    SAME sentence, and `reconcile` sends that place to `rereads` rather than
    `settled` -- MEASURED 2026-08-30, before this function existed. That is a
    side effect of a function whose docstring is about two `add`s, not a rule
    about moves, which is why `tests/test_collate.py` drives this function
    with a `resolved` dict built directly rather than through `collate`.

    Args:
        resolved: address -> the one Mark for it, moves and non-moves alike.
            Keyed by the mark's OWN address, so a move appears once.

    Returns:
        `(the move origins in a safe order, the origins caught in a cycle)`.
    """
    moves = {
        address: mark
        for address, mark in resolved.items()
        if mark.instruction is Instruction.MOVE and address == mark.address
    }
    needs: dict[str, set[str]] = {}
    for origin, mark in moves.items():
        destination = str(mark.claim.get("to", ""))
        needs[origin] = {destination} if destination in moves else set()

    out: list[str] = []
    remaining = dict(needs)
    while remaining:
        ready = sorted(
            origin
            for origin, wanted in remaining.items()
            if not (wanted & set(remaining))
        )
        if not ready:
            return out, sorted(remaining)
        for origin in ready:
            out.append(origin)
            del remaining[origin]
    return out, []


def _chief_copy(read_from: dict, resolved: dict[str, Mark], proof: dict) -> dict:
    """The copy chief's `edit_copy` -- one mark per resolved place.

    !! ONLY RESOLVED PLACES GET AN ENTRY. `desk.mark.untouched` means NOBODY
    WROTE HERE; a place two roles wrote on that nothing resolved is a different
    fact, so it rides beside this copy in `Collated` rather than being written
    as an empty slot.

    ! PATHS ARE THE REAL ONES. An address carries the FLATTENED path;
    `unflatten` resolves it against the proof's own sheet paths, exactly as
    `docket_from` does, so the sheets name files that are actually there.

    !! A `move` IS ONE ENTRY, WRITTEN ONCE, AT ITS OWN `address`. `resolved`
    carries a move's `Mark` under TWO keys -- its origin and its destination,
    `desk.collator._join_moves`' doing -- but the mark's own `.address` is
    always the origin (`docs/the-mark.md`), and `desk.mark.parse` REFUSES an
    entry whose `address` equals its own `claim.to`
    (`desk.mark._destination_problems`). Writing a second entry at the
    destination, with `address` rewritten to match, is therefore not an entry
    `parse` can accept -- it reads as a move to where the paragraph already
    is. `seen` dedups by `id(mark)` so the SAME `Mark` object, reached under
    either of its two keys, contributes its one entry once, always placed by
    `mark.address` rather than by whichever key `resolved` happened to
    iterate to first.

    !! PROVISIONAL, over a shape Roy has since ruled against, 2026-08-30:
    *"A move needs to be what it is and that is a composite Mark - Drop Here
    Add There. They have to go together ... Nothing else acts on two places
    at once."* A SENTENCE can move without the paragraph moving, so the
    origin is not always emptied -- both ends can carry their own new text,
    which today's singular `Mark` (one `address`, one `change`) cannot
    express. The composite is a separate scope, not this fix. `seen`'s dedup
    is the SMALLEST stand-in for that shape: once a move is two ordinary
    marks (a `drop` at the origin, an `add` at the destination), each has its
    own `address` and its own `id()`, `resolved` never carries one `Mark`
    under two keys, and `seen` never finds a repeat -- so this dedup becomes
    dead code, deletable outright, with no entry ever built two different
    ways.
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
                # ! `.get("sha", "")` DEFAULTS ONLY WHEN THE KEY IS ABSENT. A
                # sheet carrying `"sha": null` reaches here with the key
                # PRESENT and holding None, so `.get` returns None and
                # `str(None)` is the four-character word "None" -- folded
                # into the same missing-sha case instead, matching
                # `desk.collator._real_pages`.
                raw_sha = sheet.get("sha")
                shas[path] = raw_sha if isinstance(raw_sha, str) else ""

    sheets: dict[str, dict] = {}
    seen: set[int] = set()
    for mark in resolved.values():
        if id(mark) in seen:
            continue
        seen.add(id(mark))
        addr = cue_of(mark.address)
        real = unflatten(addr.path, paths) or addr.path
        sheet = sheets.setdefault(
            real, Sheet.seed(path=real, sha=shas.get(real, ""), marks=[])
        )
        sheet["marks"].append(mark.as_entry())
    # ! WRITTEN THROUGH THE TYPES since 2026-08-31 -- `decision-log.md Process:
    # #64`, and it matters most here: the chief's copy is an ordinary
    # `EditCopy`, so the one place that BUILDS a copy from scratch rather than
    # from a binder is the one a rename would leave writing the old key.
    return EditCopy.seed(
        role="copy-chief", read_from=read_from, sheets=list(sheets.values())
    )


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

    !! AND IT IS NOT WRITTEN THROUGH `EditCopy.seed`, WHICH THE REST OF THIS
    MODULE IS. `Process: #64` puts the write half with the read half at every
    site that BUILDS a container; this one FILTERS an existing one, and the
    difference is load-bearing. MEASURED 2026-08-31, when it was written that
    way for one commit: `EditCopy.seed` requires every declared field, so a
    copy carrying no `read_from` came out holding `{}` -- and `desk.proof.gather`
    subscripts that key precisely so an absent one raises. Its own docstring
    records the same defect being closed there: *"Reading `copy.get("read_from",
    {})` made every copy that carried none agree on `{}`."*
    `tests/test_collate_command.py::TestExitCodes::
    test_a_copy_missing_read_from_exits_one_not_a_traceback` is what failed.

    ! `collate` CAN NO LONGER REACH THIS FUNCTION WITH THE FIELD MISSING, since
    the envelope parse landed the same day and reports it one step earlier. The
    rule still binds the function, so it is asserted on the function itself --
    `tests/test_collate.py::TestTheStackedCheck::
    test_reconcilable_preserves_an_absent_read_from`.

    ! SO THE UPDATE FORM PRESERVES AN ABSENCE, and a producer cannot. A field
    this function fabricates is a field the boundary below it can no longer
    refuse.

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
        desk.proof.MismatchedRoot: two copies were censused from different
            roots. ! THE ONLY RAISE LEFT, and it cannot become a `Problem`:
            copies answering to different address spaces have no reconciliation
            between them, so there is no `Collated` to hand back. An `a0` in one
            tells nothing about the `a0` in the other.

    ! `desk.collator.MalformedMark` NEVER REACHES A CALLER OF `collate`.
    `_reconcilable` drops every entry `places` would otherwise refuse before
    `reconcile` runs, so the raise `places` itself still documents cannot fire
    from here.

    ! NEITHER DOES `desk.collator.UnnamedRole`, since 2026-08-31. It was listed
    here as *"the one way `places` still refuses"*; the envelope parse now names
    a copy with no `role` as a `Problem` and returns before `places` is called.

    !! THE ENVELOPE IS PARSED FIRST, AND A FAILURE IS REPORTED RATHER THAN
    RAISED -- `P21`, `decision-log.md Process: #57`. A container answers *is
    this document a copy at all*; `problems_in` answers *what did this role
    write in this slot*. Both run, envelope first, because a document that is
    not a copy has no contents to rule on.

    !! REPORTED, BECAUSE RAISING HERE EMPTIES THE REPORT FOR EVERY OTHER ROLE.
    `commands/collate.py` catches around this whole call, so a raise discards
    the `Problem`s already accumulated -- measured 2026-08-30 as exit 1 with an
    EMPTY stdout. Reporting keeps Roy's rule that the errors stack so each can
    be sent back to the role that owes it, and the run still errors out: the
    command returns BROKEN on a non-empty `problems` and writes no chief copy.

    !! AND IT RETURNS EARLY, SO NO CHIEF COPY IS EVER FOLDED FROM A PARTIAL SET.
    A copy that does not parse cannot be reconciled, and folding the rest would
    write a chief silently missing one role's rulings -- the outcome both the
    refusal and the report exist to prevent.

    ! WHAT IT CATCHES THAT `problems_in` CANNOT. That function's sheet walk
    reads `if not isinstance(marks, list): continue`, so a sheet that is not an
    object and a sheet whose `marks` is not a list are SKIPPED, and `path` is
    never its question. MEASURED 2026-08-31, before this landed: all three gave
    `problems == []` at exit 0, with a chief copy written without that page's
    marks.
    """
    base = base_texts(binder)
    problems: list[Problem] = []
    drift: list[Problem] = []
    left: dict[str, list[str]] = {}
    counts: dict[str, dict] = {}

    # ! THE ROLE MAY BE THE MISSING THING. `parse_edit_copy` refuses a copy with
    # no `role` before it can name one, and `Problem` needs a role to route on --
    # so the copy's position stands in, which a reader can act on where "" cannot.
    envelope: list[Problem] = []
    intact: list[dict] = []
    for i, copy in enumerate(edit_copies, 1):
        where = f"copy {i}"
        parsed, why = parse_edit_copy(where, copy)
        named = copy.get("role") if isinstance(copy, dict) else None
        who = named if isinstance(named, str) and named.strip() else where
        envelope += [Problem(who, "", message) for message in why]
        if parsed is not None:
            intact.append(copy)
    if envelope:
        # !! `problems_in` RUNS ONLY OVER THE COPIES THAT PARSED. Running it
        # over a refused one reports the same fact twice in two vocabularies --
        # measured on a copy with no `sheets`, which both boundaries answer --
        # and that is the duplication `Problem` exists to avoid, stated at
        # `desk.collator.drift_in`. A document that is not a copy has no
        # contents to rule on.
        for copy in intact:
            found, _ruled = problems_in(copy)
            problems += found
        return Collated(
            chief=EditCopy.seed(role="copy-chief", read_from={}, sheets=[]),
            problems=envelope + problems,
        )

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

    # !! BOTH ENDS OR NEITHER, THEN AN ORDER. D8 of the SP-1 spec: a set of
    # moves is a graph over addresses, and half a move is worse than none.
    by_address = {
        entry["address"]: entry
        for entry in reconciled.settled + reconciled.escalations + reconciled.rereads
    }
    for address in _pair_moves(resolved):
        del resolved[address]
        entry = by_address.get(address)
        if entry is not None and entry not in rereads:
            rereads.append(entry)

    order, cycle = _move_order(resolved)
    if cycle:
        # ! SNAPSHOT BEFORE POPPING. `cycle` names every address caught, and a
        # two-cycle's ends touch each other -- popping the first end's touched
        # addresses can remove the second end from `resolved` before its own
        # turn reads it, which is a KeyError over the exact input this rule
        # exists to handle.
        caught = {address: resolved[address] for address in cycle}
        for mark in caught.values():
            for end in _touched_by(mark):
                resolved.pop(end, None)
                entry = by_address.get(end)
                if entry is not None and entry not in rereads:
                    rereads.append(entry)
        order, _again = _move_order(resolved)

    return Collated(
        chief=_chief_copy(proof.get("read_from", {}), resolved, proof),
        problems=problems,
        drift=drift,
        escalations=escalations,
        rereads=rereads,
        unruled=left,
        tally=counts,
        order=order,
    )
