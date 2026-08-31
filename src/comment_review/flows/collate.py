"""COLLATE -- one stage's returned edit_copies, folded into the chief's own.

    collate(stage, edit_copies, binder, root) -> Collated

Twelve acts, in the order the body runs them:

    ENVELOPE   is each document the shape a copy must be --
               `desk.containers.parse_edit_copy`. Reported, never raised
    CHECK      every copy's marks, stacked -- `desk.collator.problems_in`,
               over the copies ENVELOPE admitted. ! ONLY AN *ENVELOPE* FAILURE
               RETURNS EARLY. A malformed MARK is reported and the round goes
               on without it -- `_reconcilable` drops it, and its docstring
               says why refusing here would block three roles over one
    COVERAGE   did each role carry back every address the binder holds --
               `_coverage_problems`. `fan_out` refuses an uncovered page at the
               DISPATCH; this is the RETURN
    VERIFY     each ruled mark's address, quoted sentence and citations --
               `desk.collator.verify_report`, the three questions
               `desk.mark.parse` cannot ask because it holds no binder, no page
               and no filesystem
    DRIFT      a returned `raw_text` that is not the seeded one
    DROP       every mark `CHECK` already reported, from what `RECONCILE`
               sees -- `_reconcilable`
    GATHER     `desk.proof.gather` -- the master_proof
    PROOF      is that master_proof the shape a proof must be --
               `desk.containers.parse_master_proof`, on ENVELOPE's terms
    PLACE      `desk.collator.places` -- marks grouped by the place they touch
    RECONCILE  `desk.collator.reconcile` -- settled, escalated, re-read
    RESOLVE    the automatic resolutions -- `_resolve`
    ORDER      a `move` at one end only is withdrawn, then the survivors are
               ordered vacate-before-fill or carried forward as a named cycle
               -- `_pair_moves`, `_move_order` -- before the fold

!! THIS LIST IS READ AS A MAP AND MUST MATCH THE BODY. Until 2026-08-31 it put
COVERAGE before CHECK, which is the reverse of what runs, and folded
`parse_master_proof` into ENVELOPE at position one when it is called after
GATHER -- so a reader using it to find a stage landed in the wrong place twice.

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
from pathlib import Path

from comment_review.desk.collator import (
    Cache,
    Placed,
    Problem,
    base_texts,
    drift_in,
    known_addresses,
    problems_in,
    reconcile,
    tally,
    unruled,
    verify_report,
)
from comment_review.desk.containers import (
    EditCopy,
    Sheet,
    parse_edit_copy,
    parse_master_proof,
)
from comment_review.desk.mark import Instruction, Mark, filled, parse, untouched
from comment_review.desk.proof import MismatchedRoot, gather
from comment_review.reading.addresser import cue_of, unflatten
from comment_review.results.differences import CannotCompose, compose


class CannotCollate(Exception):
    """The set cannot be folded, WITH everything the pass found on the way.

    !! IT EXISTS SO A REFUSAL DOES NOT EMPTY THE REPORT. MEASURED 2026-08-30 by
    running the real CLI: `commands/collate.py` catches around the whole
    `collate()` call, and `collate` accumulates its `Problem`s into a local list
    that only reaches a caller through `return Collated(...)` -- so a raise past
    that point gave exit 1 with an EMPTY stdout, and one copy's incompatible
    header blocked routing for every other role.

    ! THE REFUSAL ITSELF IS RIGHT AND STAYS. `desk.proof.MismatchedRoot` means
    two copies answer to different address spaces, so there is no fold between
    them -- an `a0` in one tells nothing about the `a0` in the other. What was
    wrong was throwing away the routable problems alongside it.

    Attributes:
        problems: every `Problem` the per-copy pass had already computed, in
            copy then mark order -- the same list `Collated.problems` would
            have carried had the fold completed.
    """

    def __init__(self, message: str, problems: list[Problem]) -> None:
        """Hold the refusal's own message and the problems found before it.

        Args:
            message: why the set cannot be folded, as the underlying refusal
                stated it -- it already names both disagreeing values.
            problems: what the per-copy pass had computed by then. May be
                empty, which says the set was incompatible and otherwise clean.
        """
        super().__init__(message)
        self.problems = problems


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
        coverage: a role whose copies do not between them carry the binder's
            address set, same shape and same routing.
            !! ITS OWN LIST, NOT `problems`, since 2026-08-31 -- `Process: #63`
            says a missing answer ROUTES and does not VOID the round, and the
            command returns BROKEN and writes nothing on a non-empty
            `problems`. Folded in there, a short shard did exactly what the
            ruling forbids.
            ! IT RESEMBLES `drift` AND IS NOT MODELLED ON IT. `Process: #62`
            ruled `drift_in` OUT -- the middle has no stake in whether the tree
            moved -- and `ac8cbbd` giving drift an exit code is on the record as
            a fix pointing the wrong way. Coverage stands on `#63` alone: it
            asks whether a role ANSWERED, which is a fact about the round and
            not about the tree. The shape they share is temporary, because one
            of them is going.
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
    coverage: list[Problem] = field(default_factory=list)
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
    # !! THE ENVELOPE GUARANTEES `path` AND `marks`, AND NOT `sha`. `parse_sheet`
    # REFUSES a sheet whose `path` is not filled and whose `marks` is not a list,
    # so those are the envelope's to decide and subscripting them here is safe.
    # It ADMITS a sheet with no `sha` at all and normalizes the absence to `""`
    # -- but into the `Sheet` DATACLASS, which this flow discards. The raw dict
    # it goes on walking still has no key.
    #
    # !! MEASURED 2026-08-31, AFTER T4 CUT THE GUARD ON EXACTLY THAT CONFUSION.
    # A seeded copy with `sha` deleted gives `parse_edit_copy` problems `[]`,
    # then `collate` raised `KeyError: 'sha'` here -- which the CLI catches as a
    # refusal, printing `REFUSED ... a copy carries no 'sha'` with an EMPTY
    # stdout. That discards every routable `Problem`, the precise defect
    # `CannotCollate` was added to end.
    #
    # ! SO THE TEST FOR CUTTING A GUARD IS WHAT THE ENVELOPE DECIDES ABOUT THE
    # VALUE THIS CODE READS, not what it decides about the object it returns.
    # `Process: #65` is the standing fix -- carry the parsed container instead
    # of the dict, and the normalization arrives with it.
    paths: list[str] = []
    shas: dict[str, str] = {}
    for copy in proof.get("edit_copies", []):
        for sheet in copy.get("sheets", []):
            path = sheet["path"]
            if path not in shas:
                paths.append(path)
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
        caller's own containers are never mutated.

        ! IT NO LONGER PASSES A MALFORMED SHEET THROUGH, because one cannot
        reach it: `collate` parses every copy at its boundary first, and a copy
        whose sheets are not the shape a sheet must be never gets this far.
    """
    sheets = []
    for sheet in copy.get("sheets", []):
        marks = []
        # ! THE SHEET SHAPE IS THE ENVELOPE'S, NOT THIS FUNCTION'S, since
        # 2026-08-31. `parse_edit_copy` decides that a sheet is a dict with a
        # `marks` list before `collate` reaches here; the pass-through branch
        # that used to stand in for it was the second definition `P21` removes.
        #
        # ! AN ENTRY IS STILL CHECKED, AND THAT IS NOT THE SAME QUESTION.
        # `Sheet.marks` is typed `tuple[object, ...]` deliberately -- an entry
        # that is not an object is CARRIED so `desk.mark.parse` can refuse it by
        # name, which is exactly what this loop then does.
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


def _nothing_settled() -> dict:
    """The chief's copy for a round that folded nothing.

    ! ONE SPELLING, TWO EXITS. `collate` returns early twice -- a copy that is
    not a copy, and a proof that is not a proof -- and each said so by writing
    this literal out again. *A round that settled nothing* is one fact, and two
    hand-written copies of it are two places for the sentinel to drift apart.
    """
    return EditCopy.seed(role="copy-chief", read_from={}, sheets=[])


def _coverage_problems(edit_copies: list[dict], binder: dict) -> list[Problem]:
    """One `Problem` per role whose copies do not carry the binder's addresses.

    !! `flows.fan_out.fan` REFUSES AT THE DISPATCH AND NOTHING READ THE RETURN.
    It raises `OverlappingShards` and `UncoveredPage` over the pages it is about
    to hand out; a role that then answered for three of the four files in its
    shard was invisible. `P27`, and
    `TODO/containers-and-verification-are-unwired.md` T6.

    !! THE UNION ACROSS A ROLE'S COPIES, NEVER ONE COPY AGAINST THE BINDER.
    Under fan-out each copy carries only its own shard, so comparing per copy
    would report every shard of a correctly partitioned role as incomplete.
    That is the shape `unruled` and `tally` already have -- both keyed by role,
    both clobbering under fan-out -- and it is deliberately not copied here.

    !! IT NEEDS NO NEW INPUT, which is why `P27` is in SP-2 and `P26` is not.
    `collate` already holds the WHOLE binder: `base_texts` needs every address,
    so what it is handed cannot be a shard. **Stage coverage is a different
    question and cannot be answered from here** -- a role that returned nothing
    leaves nothing behind to be missing from, since `flows.distribute.seed`
    stamps a copy with `role`, `read_from` and `sheets` and no dispatch
    identity. That one takes the `Stage`, in SP-3.

    Args:
        edit_copies: the copies as they came back, already parsed.
        binder: the binder they were seeded from.

    Returns:
        One `Problem` per short role, naming every address that role did not
        carry, sorted so a reader can re-derive the list. Empty where every
        role is complete. ! REPORTED, NOT RAISED -- `Process: #63`: the places
        that did come back still settle.

    ! AN EMPTY BINDER YIELDS NOTHING. There is no address to be missing, and a
    run over one is what `tests/test_brief_worked_example.py` drives.
    """
    known = known_addresses(binder)
    if not known:
        return []
    by_role: dict[str, set[str]] = {}
    for copy in edit_copies:
        role = str(copy.get("role") or "")
        carried = by_role.setdefault(role, set())
        for sheet in copy.get("sheets", []):
            # ! THE ENTRY IS CHECKED AND THE SHEET IS NOT. The envelope decides
            # the sheet; `Sheet.marks` deliberately carries an entry that is not
            # an object, so that one is this function's own question.
            for entry in sheet["marks"]:
                if isinstance(entry, dict) and isinstance(entry.get("address"), str):
                    carried.add(entry["address"])
    out: list[Problem] = []
    for role, carried in by_role.items():
        missing = sorted(known - carried)
        if missing:
            # !! COUNTED OVER THE INTERSECTION, NOT OVER EVERYTHING RETURNED.
            # `carried` holds every address the role sent back, including any
            # the binder never held, so `len(carried)` can equal `len(known)`
            # while something is still missing. MEASURED 2026-08-31: a role
            # that dropped `m.py@b5` and invented `m.py@b9` against a two-place
            # binder reported *"answered for 2 of 2 places -- missing
            # m.py@b5"*, which contradicts itself on its own line.
            #
            # ! AN INVENTED ADDRESS IS NOT THIS FUNCTION'S TO REPORT.
            # `desk.collator.address_problems` answers that one, per mark, and
            # naming it here too would be the same fact in two vocabularies.
            out.append(
                Problem(
                    role,
                    "",
                    f"answered for {len(carried & known)} of {len(known)} "
                    f"places -- missing {', '.join(missing)}",
                )
            )
    return out


def collate(stage: str, edit_copies: list[dict], binder: dict, root: Path) -> Collated:
    """One stage's returned copies, checked, reconciled and folded.

    Args:
        stage: the label these copies were dispatched under -- "4a", "4c".
        edit_copies: one per role, or one per SHARD under fan-out, as each came
            back.
        binder: the binder they were seeded from. ! IT SUPPLIES THE BASE, THE
            OTHER SIDE OF THE DRIFT CHECK, AND THE KNOWN ADDRESSES SOURCE
            VERIFICATION MEASURES AGAINST -- address integrity over the DOCKET
            is a different question and is `P28`'s.
        root: the checkout every `sources` citation is resolved against. ! IT
            IS NOT A PAGE ROOT. `Process: #62` bars the middle from a page
            under review; what this reads is evidence, which carries no `sha`
            because nothing writes it.

    Returns:
        A `Collated`.

    Raises:
        CannotCollate: two copies were censused from different roots --
            `desk.proof.MismatchedRoot`, re-raised carrying every `Problem` the
            per-copy pass had already found. ! THE ONLY RAISE LEFT, and it
            cannot become a `Problem` itself: copies answering to different
            address spaces have no reconciliation between them, so there is no
            `Collated` to hand back. An `a0` in one tells nothing about the
            `a0` in the other.

    ! `desk.collator.MalformedMark` NEVER REACHES A CALLER OF `collate`.
    `_reconcilable` drops every entry `places` would otherwise refuse before
    `reconcile` runs, so the raise `places` itself still documents cannot fire
    from here.

    ! NEITHER DOES `desk.collator.UnnamedRole`, since 2026-08-31. It was listed
    here as *"the one way `places` still refuses"*; the envelope parse now names
    a copy with no `role` as a `Problem` and returns before `places` is called.

    !! THE ENVELOPE IS PARSED FIRST, AND A FAILURE IS REPORTED RATHER THAN
    RAISED -- `P21`, `decision-log.md Process: #57`. **What the two boundaries
    are is stated once, in `desk/containers.py`'s module docstring**, and not
    restated here: a rule in two places is a rule that will disagree with
    itself. What is this function's own is the ORDER and the response --
    envelope first, because a document that is not a copy has no contents to
    rule on, and reported rather than raised.

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
    # ENVELOPE -- is each document a copy at all.
    envelope: list[Problem] = []
    are_copies: list[dict] = []
    for i, copy in enumerate(edit_copies, 1):
        where = f"copy {i}"
        parsed, why = parse_edit_copy(where, copy)
        if why:
            named = copy.get("role") if isinstance(copy, dict) else None
            envelope += [
                Problem(named if filled(named) else where, "", message)
                for message in why
            ]
        if parsed is not None:
            are_copies.append(copy)

    # CHECK -- what each role wrote in each slot.
    #
    # !! A SEPARATE PASS, AND IT STAYS ONE. The two are named as separate acts in
    # this module's own header, and folding CHECK into the loop above for one
    # fewer iteration made the code stop matching that list -- one loop carrying
    # two acts under one conditional, which is the shape `galley.py` was split
    # for. The saving was never the pass; it was running `problems_in` ONCE,
    # which it does either way.
    #
    # !! AND IT RUNS ONLY OVER THE COPIES THAT PARSED. Running it over a refused
    # one reports the same fact twice in two vocabularies -- measured on a copy
    # with no `sheets`, which both boundaries answer -- and that is the
    # duplication `Problem` exists to avoid, stated at `desk.collator.drift_in`.
    # A document that is not a copy has no contents to rule on.
    for copy in are_copies:
        found, _ruled = problems_in(copy)
        problems += found

    if envelope:
        return Collated(chief=_nothing_settled(), problems=envelope + problems)

    coverage = _coverage_problems(edit_copies, binder)

    # ! ONE CACHE FOR THE WHOLE STAGE, not one per copy. Roles cite the same
    # evidence, and a cache built inside `verify_report` re-read a file once per
    # citing role -- four reads of one line for four roles, measured 2026-08-31.
    cache: Cache = {}

    for copy in edit_copies:
        # ! `problems_in` ALREADY RAN, in the envelope pass above. It is the one
        # check that must happen for a copy the fold will not reach, so it lives
        # there rather than here; running it again would report every malformed
        # mark twice on the happy path.
        #
        # !! SOURCE VERIFICATION RUNS HERE -- `P25`, `Process: #58`. Roy: *"the
        # source-verification side needs to be wired into the flow - same as 1)
        # the flow coordinates the things in the modules do."* It asks what
        # `desk.mark.parse` cannot: parse imports no binder, no page and no
        # filesystem, so a claim quoting a sentence that is not in its paragraph
        # and a `cite` naming a file that does not exist both reach it clean.
        #
        # ! IT READS FILES, AND THAT IS NOT `Process: #62`'s "no files". The
        # test is the `sha`: a page under review carries one because it will be
        # written, and the middle must not touch it; a cited evidence file
        # carries none because nothing writes it, and reading it is what
        # settling a citation means. Roy, 2026-08-30, on exactly this call.
        problems += verify_report(copy, binder, root, cache)
        drift += drift_in(copy, base)
        role = str(copy.get("role") or "")
        left[role] = unruled(copy)
        counts[role] = tally(copy)

    # !! THE REFUSAL CARRIES WHAT THE PASS ALREADY FOUND. Everything above this
    # line accumulated `Problem`s into a local list; a bare raise from here
    # discards all of them, which `commands/collate.py` was measured doing on
    # 2026-08-30 -- exit 1 with an EMPTY stdout. See `CannotCollate`.
    try:
        proof = gather(stage, [_reconcilable(copy) for copy in edit_copies])
    except MismatchedRoot as err:
        raise CannotCollate(str(err), problems) from err
    # !! THE PROOF IS PARSED AT ITS OWN BOUNDARY, the same rule one level up --
    # `P21`, `Process: #57`. `gather` builds it and nothing stated what a proof
    # IS before `reconcile` walked it. ! IT REPORTS AND RETURNS EARLY, exactly
    # as the copy boundary above does; the two differ only in what they hold.
    #
    # ! WHAT REACHES HERE IS NOT WHAT A ROLE HANDED BACK. Every copy has already
    # parsed, so this cannot fire on a role's mistake -- it answers for what
    # `gather` and `_reconcilable` between them produced. That makes it a guard
    # on THIS code rather than on its input, which is why the test that proves
    # it can fail has to replace `gather` to reach it.
    _proof, why_proof = parse_master_proof(stage, proof)
    if why_proof:
        return Collated(
            chief=_nothing_settled(),
            problems=problems + [Problem("copy-chief", "", m) for m in why_proof],
            drift=drift,
            coverage=coverage,
            unruled=left,
            tally=counts,
        )
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
        coverage=coverage,
        escalations=escalations,
        rereads=rereads,
        unruled=left,
        tally=counts,
        order=order,
    )
