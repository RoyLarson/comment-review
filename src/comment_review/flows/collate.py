"""COLLATE -- one stage's returned edit_copies, folded into the chief's own.

    collate(stage, edit_copies, binder, root) -> Collated

Ten acts, in the order the body runs them:

    ENVELOPE   is each document the shape a copy must be --
               `desk.containers.EditCopy.deserialize`. Reported, never raised.
               !! IT IS THE ONLY PARSE IN THE FLOW, and what it returns is what
               every act below reads -- `P42`, and since `P51` that includes
               every MARK: a copy arrives sorted into what ruled, what was left
               unruled, and what would not read at all
    CHECK      every place a role must go back to -- one left unruled, one
               whose entry would not read -- `flows.mark_errors`, over the
               copies ENVELOPE admitted. ! ONLY AN *ENVELOPE* FAILURE RETURNS
               EARLY. A malformed MARK is carried in `revisit` and the round
               goes on without it, because it never became a mark to begin with
    COVERAGE   did each role carry back every address the binder holds --
               `_coverage_problems`. `fan_out` refuses an uncovered page at the
               DISPATCH; this is the RETURN
    VERIFY     each ruled mark's address, quoted sentence and citations --
               `desk.collator.verify_report`, the three questions
               `desk.mark.parse` cannot ask because it holds no binder, no page
               and no filesystem
    DRIFT      a returned `raw_text` that is not the seeded one
    GATHER     `desk.proof.gather` -- the master_proof
    PLACE      `desk.collator.places` -- marks grouped by the place they touch
    RECONCILE  `desk.collator.reconcile` -- settled, escalated, re-read
    RESOLVE    the automatic resolutions -- `_resolve`
    ORDER      a `move` at one end only is withdrawn, then the survivors are
               ordered vacate-before-fill or carried forward as a named cycle
               -- `_pair_moves`, `_move_order` -- before the fold

!! THIS LIST IS READ AS A MAP AND MUST MATCH THE BODY. Until 2026-08-31 it put
COVERAGE before CHECK, which is the reverse of what runs, and folded
`MasterProof.deserialize` into ENVELOPE at position one when it is called after
GATHER -- so a reader using it to find a stage landed in the wrong place twice.
! IT HELD A TWELFTH ACT, `PROOF`, UNTIL `P42` retired it: `gather` returns a
`MasterProof` rather than a dict, so there is no document left to rule on.

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

!! AND THAT DISCIPLINE IS STRUCTURAL SINCE `P51`, WHERE IT USED TO BE A STEP.
`desk.collator.places` RAISED `MalformedMark` on the first entry it could not
parse, so an eleventh act -- DROP, `_reconcilable` -- ran between CHECK and
GATHER to remove every such entry before the fold could abort on one role's bad
mark. `Sheet.marks` holds only marks that parsed, so there is nothing to drop:
an entry that will not read is `Sheet.refused`, and it routes to the role that
wrote it while the rest of the stage settles.
"""

from dataclasses import dataclass, field
from pathlib import Path

from comment_review.binder.binder import Binder
from comment_review.desk.collator import (
    Cache,
    Placed,
    Problem,
    base_texts,
    drift_in,
    known_addresses,
    reconcile,
    tally,
    verify_report,
)
from comment_review.desk.containers import (
    EditCopy,
    MasterProof,
    Sheet,
)
from comment_review.desk.mark import Instruction, Mark, filled
from comment_review.desk.proof import MismatchedRoot, gather
from comment_review.flows.mark_errors import Revisit, mark_errors
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
        revisit: the same for `Collated.revisit`.
            !! IT WAS ADDED WITH `P52` AND HAD TO BE. That step moved every
            malformed mark out of `problems` and into `revisit`, so a refusal
            carrying only `problems` would have dropped exactly the findings
            this exception exists to preserve -- the defect it was written for,
            reintroduced by the list it was written against moving.
            MEASURED by `tests/test_collate_command.py::TestExitCodes::
            test_a_refusal_still_prints_the_problems_the_pass_found`, which
            went red on the change and is why this field is here.
    """

    def __init__(
        self,
        message: str,
        problems: list[Problem],
        revisit: list[Revisit] | None = None,
    ) -> None:
        """Hold the refusal's own message and everything found before it.

        Args:
            message: why the set cannot be folded, as the underlying refusal
                stated it -- it already names both disagreeing values.
            problems: what the per-copy pass had computed by then. May be
                empty, which says the set was incompatible and otherwise clean.
            revisit: the places a role must go back to, same terms.
        """
        super().__init__(message)
        self.problems = problems
        self.revisit = revisit or []


@dataclass(frozen=True)
class Collated:
    """What one stage came to, and what is left for a person.

    Attributes:
        chief: the copy chief's `edit_copy` -- one mark per RESOLVED place,
            except a `move`, whose two resolved places (origin and
            destination) share the ONE entry `_chief_copy` writes at the
            origin -- see that function's docstring for why a second entry
            at the destination cannot parse. An ordinary edit_copy;
            `desk.containers.EditCopy.deserialize` accepts it with no second shape.
        problems: what SOURCE VERIFICATION found -- an address the binder does
            not carry, a claim quoting a sentence that is not in its paragraph,
            a `cite` that does not resolve -- plus any copy-level refusal from
            the envelope, each naming the role to send it back to.
            !! IT CARRIED THE MALFORMED MARKS TOO UNTIL `P52`, and they are
            `revisit` now. Both lists said *this role must go back to this
            place*, in two vocabularies, assembled in two modules; the reason
            they split rather than merged is that a mark that will not read and
            a claim that does not hold are answered by different work.
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
        revisit: every place a role must go back to -- one it was handed and
            left alone, or one it wrote in whose entry would not read. Role
            then address order, from `flows.mark_errors`.
            !! IT REPLACES `unruled`, WHICH WAS `role -> addresses` AND HALF THE
            ANSWER. The other half sat in `problems`, and the command assembled
            the unruled side into `Problem`s itself -- so *what a role still
            owes* was computed in two modules and printed as two lists. This is
            the one artifact, and `Process: #72` is the shape it takes.
        tally: role -> how many of each instruction that copy carried.
        order: the resolved `move` origins, in an order that vacates every
            address before it is filled. Ties broken by address, so a stranger
            re-derives it. Empty where no move resolved.
    """

    chief: EditCopy
    problems: list[Problem] = field(default_factory=list)
    drift: list[Problem] = field(default_factory=list)
    coverage: list[Problem] = field(default_factory=list)
    escalations: list[dict] = field(default_factory=list)
    rereads: list[dict] = field(default_factory=list)
    revisit: list[Revisit] = field(default_factory=list)
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


def _chief_copy(
    read_from: dict, resolved: dict[str, Mark], proof: MasterProof
) -> EditCopy:
    """The copy chief's `edit_copy` -- one mark per resolved place.

    !! ONLY RESOLVED PLACES GET AN ENTRY. `desk.mark.untouched` means NOBODY
    WROTE HERE; a place two roles wrote on that nothing resolved is a different
    fact, so it rides beside this copy in `Collated` rather than being written
    as an empty slot.

    ! PATHS ARE THE REAL ONES. An address carries the FLATTENED path;
    `unflatten` resolves it against the proof's own sheet paths, so the sheets
    name files that are actually there -- and `flows.revise.docket_of` then
    reads those paths straight off the sheets, resolving nothing again.

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
    # !! IT IS THE ONLY (paths, shas) WALK IN THE TREE, since `P55`. It
    # DUPLICATED `desk.collator._real_pages` -- the identical pair over the
    # identical shape, kept as its own copy because `_real_pages` was a private
    # name in a file this module must not edit. That function had exactly one
    # caller, `docket_from`, and both left `desk/` together when the docket
    # transcription moved to `flows/revise.py::docket_of`. The duplication ended
    # by the other copy going, not by either module reaching across.
    # !! IT WALKS THE PARSED `MasterProof`, NOT THE DICT, since 2026-08-31 --
    # `Process: #65` in the small. `Sheet.sha` is a `str` because `Sheet.deserialize`
    # made it one; there is nothing left to fold here, and no sixth site
    # tracking that rule by hand.
    #
    # !! IT TOOK A DICT AND HAND-FOLDED THE SHA FOR ONE COMMIT, AND THAT IS THE
    # MEASUREMENT WORTH KEEPING. T4 cut the guard believing the envelope
    # guaranteed a `str` sha; it guarantees `path` and `marks`, and ADMITS a
    # sheet with no `sha`, normalizing the absence into the `Sheet` -- an
    # object the flow then discarded. A seeded copy with `sha` deleted gave
    # `EditCopy.deserialize` problems `[]` and then `KeyError: 'sha'` here, which
    # the CLI turned into a refusal with an EMPTY stdout, discarding every
    # routable `Problem`.
    #
    # ! THE FIX FIRST TRIED WAS TO RESTORE THE FOLD, and the parsed proof was
    # sitting unused in `collate`'s own scope one statement above it. Reading
    # what the container already decided is both smaller and the direction the
    # ruling points.
    paths: list[str] = []
    shas: dict[str, str] = {}
    for copy in proof.edit_copies:
        for sheet in copy.sheets:
            if sheet.path not in shas:
                paths.append(sheet.path)
                shas[sheet.path] = sheet.sha

    # ! THE MARKS ARE CARRIED AS MARKS since `P51`, and were serialized here
    # into wire dicts. `Sheet.marks` holds `Mark`s now, and the one place the
    # chief's copy becomes a document is `commands/collate.py`'s save -- which
    # is where `Process: #65` puts it.
    marks_of: dict[str, list[Mark]] = {}
    shas_of: dict[str, str] = {}
    seen: set[int] = set()
    for mark in resolved.values():
        if id(mark) in seen:
            continue
        seen.add(id(mark))
        addr = cue_of(mark.address)
        real = unflatten(addr.path, paths) or addr.path
        shas_of.setdefault(real, shas.get(real, ""))
        marks_of.setdefault(real, []).append(mark)
    # ! BUILT AS THE CONTAINER, NOT AS THE WIRE DICT, since `P42`. It is the one
    # place that BUILDS a copy from scratch rather than from a binder, so it is
    # the one a rename would otherwise leave writing the old key -- which is
    # what `EditCopy.seed` answered while this returned a dict.
    return EditCopy(
        role="copy-chief",
        read_from={**read_from},
        sheets=tuple(
            Sheet(path=real, sha=shas_of[real], marks=tuple(mine))
            for real, mine in marks_of.items()
        ),
    )


#: !! `_reconcilable` AND `_keeps` ARE DELETED, `P51`. Their whole job was
#: dropping every entry `desk.mark.parse` refuses, so `desk.collator.places`
#: would not raise `MalformedMark` on the first one and abort a stage over one
#: role's bad mark. `Sheet.marks` holds only marks that parsed, so there is
#: nothing left to drop and no raise left to avoid.
#: ! WHAT THEY PROTECTED IS UNCHANGED AND IS NOW STRUCTURAL -- Roy, 2026-08-30:
#: *"the errors should be stacked and capable of being read off correctly so
#: that each can be fixed or sent back to the role."* A refused entry is
#: `Sheet.refused`, an address and its reasons, routed to the role that wrote
#: it -- `decision-log.md Process: #72`.
#: ! AND THE DISTINCTION `_reconcilable` KEPT IS KEPT BY THE PARSE: a malformed
#: mark means a role DID write here and got the shape wrong, which is not the
#: same fact as `untouched`. They are two fields now, not one dropped entry.


def _nothing_settled() -> EditCopy:
    """The chief's copy for a round that folded nothing.

    ! ONE SPELLING, TWO EXITS. `collate` returns early twice -- a copy that is
    not a copy, and a proof that is not a proof -- and each said so by writing
    this literal out again. *A round that settled nothing* is one fact, and two
    hand-written copies of it are two places for the sentinel to drift apart.
    """
    return EditCopy(role="copy-chief", read_from={}, sheets=())


def _coverage_problems(edit_copies: list[EditCopy], binder: Binder) -> list[Problem]:
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
    # !! ALL THREE KINDS COUNT AS CARRIED, and that is the whole point of this
    # check. It asks whether the copy came BACK with the binder's addresses, not
    # whether the role ruled on them -- an untouched slot and an entry that
    # would not parse are both places the role still HAS. Whether it answered
    # is `unruled`'s question, and `commands/collate.py` reports that
    # separately. ! A REFUSED ENTRY WITH NO ADDRESS contributes nothing, since
    # there is no place to say it carried.
    by_role: dict[str, set[str]] = {}
    for copy in edit_copies:
        carried = by_role.setdefault(copy.role, set())
        for sheet in copy.sheets:
            carried.update(mark.address for mark in sheet.marks)
            carried.update(sheet.unruled)
            carried.update(one.address for one in sheet.refused if one.address)
    out: list[Problem] = []
    for role, carried in by_role.items():
        missing = sorted(known - carried)
        if missing:
            # !! THE ADDRESSES LEAD, AND THE COUNT FOLLOWS. Roy, 2026-09-01:
            # *"That way the potential address comes as soon as possible."* This
            # is the ONE line in the report whose `address` field is empty --
            # the finding is about the copy, so the places it names can only be
            # in the message -- and a reader scanning for somewhere to look had
            # to read past a count to reach them. Every other line opens with
            # its place; this one now does too.
            #
            # !! COUNTED OVER THE INTERSECTION, NOT OVER EVERYTHING RETURNED.
            # `carried` holds every address the role sent back, including any
            # the binder never held, so `len(carried)` can equal `len(known)`
            # while something is still missing. MEASURED 2026-08-31, and quoted
            # in the order it printed then: a role that dropped `m.py@b5` and
            # invented `m.py@b9` against a two-place binder reported
            # *"answered for 2 of 2 places -- missing m.py@b5"*, which
            # contradicts itself on its own line.
            #
            # ! AN INVENTED ADDRESS IS NOT THIS FUNCTION'S TO REPORT.
            # `desk.collator.address_problems` answers that one, per mark, and
            # naming it here too would be the same fact in two vocabularies.
            out.append(
                Problem(
                    role,
                    "",
                    f"missing {', '.join(missing)} -- answered for "
                    f"{len(carried & known)} of {len(known)} places",
                )
            )
    return out


def collate(
    stage: str, edit_copies: list[dict], binder: Binder, root: Path
) -> Collated:
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

    ! `desk.collator.UnnamedRole` IS GONE ENTIRELY, `P42`. It was listed here as
    *"the one way `places` still refuses"*, then as unreachable once the
    envelope parse named a copy with no `role` as a `Problem`; `places` takes a
    `MasterProof` now, so the state it refused cannot be assembled at all.

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

    ! WHAT IT CATCHES THAT THE PER-MARK PASS CANNOT. That walk
    reads `if not isinstance(marks, list): continue`, so a sheet that is not an
    object and a sheet whose `marks` is not a list are SKIPPED, and `path` is
    never its question. MEASURED 2026-08-31, before this landed: all three gave
    `problems == []` at exit 0, with a chief copy written without that page's
    marks.
    """
    base = base_texts(binder)
    problems: list[Problem] = []
    drift: list[Problem] = []
    counts: dict[str, dict] = {}

    # ! THE ROLE MAY BE THE MISSING THING. `EditCopy.deserialize` refuses a copy with
    # no `role` before it can name one, and `Problem` needs a role to route on --
    # so the copy's position stands in, which a reader can act on where "" cannot.
    # ENVELOPE -- is each document a copy at all.
    #
    # !! AND WHAT IT PRODUCES IS WHAT EVERY LATER STEP READS, since `P42`. The
    # raw documents are not carried past this loop: `copies` is the parsed list,
    # and nothing below re-derives `.get("sheets")` or folds a sha by hand.
    envelope: list[Problem] = []
    copies: list[EditCopy] = []
    for i, document in enumerate(edit_copies, 1):
        where = f"copy {i}"
        parsed, why = EditCopy.deserialize(where, document)
        if why:
            named = document.get("role") if isinstance(document, dict) else None
            envelope += [
                Problem(named if filled(named) else where, "", message)
                for message in why
            ]
        if parsed is not None:
            copies.append(parsed)

    # CHECK -- what each role wrote in each slot, and what it left alone.
    #
    # !! ONE ASSEMBLER SINCE `P52`, WHERE THERE WERE TWO. `problems_in` turned
    # `Sheet.refused` into `Problem`s here and `commands/collate.py` turned
    # `Sheet.unruled` into its own -- so the same stage's unfinished work was
    # assembled in two places, in two vocabularies, one of them inside a console
    # face. `flows.mark_errors` is the single place both now come from, which is
    # what Roy asked the flow for: something the task agent can point at.
    #
    # !! AND IT RUNS ONLY OVER THE COPIES THAT PARSED. Running it over a refused
    # one reports the same fact twice -- measured on a copy with no `sheets`,
    # which both boundaries answer -- and that is the duplication `Problem`
    # exists to avoid, stated at `desk.collator.drift_in`. A document that is
    # not a copy has no contents to rule on.
    revisit = mark_errors(copies)

    if envelope:
        return Collated(
            chief=_nothing_settled(),
            problems=envelope + problems,
            revisit=revisit,
        )

    coverage = _coverage_problems(copies, binder)

    # ! ONE CACHE FOR THE WHOLE STAGE, not one per copy. Roles cite the same
    # evidence, and a cache built inside `verify_report` re-read a file once per
    # citing role -- four reads of one line for four roles, measured 2026-08-31.
    cache: Cache = {}

    for copy in copies:
        # ! `mark_errors` ALREADY RAN, in the pass above. It is the one thing
        # that must happen for a copy the fold will not reach, so it lives
        # there rather than here.
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
        counts[copy.role] = tally(copy)

    # !! THE REFUSAL CARRIES WHAT THE PASS ALREADY FOUND. Everything above this
    # line accumulated `Problem`s into a local list; a bare raise from here
    # discards all of them, which `commands/collate.py` was measured doing on
    # 2026-08-30 -- exit 1 with an EMPTY stdout. See `CannotCollate`.
    try:
        proof = gather(stage, copies)
    except MismatchedRoot as err:
        raise CannotCollate(str(err), problems, revisit) from err
    # !! THE PROOF BOUNDARY IS GONE, AND `P42` IS WHY. `MasterProof.deserialize`
    # ran here, over the dict `gather` returned, and reported a proof that was
    # not one. `gather` now RETURNS a `MasterProof`, so reaching that parse
    # would mean serializing a container in order to read it back -- and every
    # rule it enforced is already settled upstream: each copy's `read_from`
    # by `EditCopy.deserialize`, the agreement between them by `MismatchedRoot`
    # two lines above, and the `edit_copies` list by the type.
    #
    # ! IT WAS ALREADY A GUARD ON THIS CODE RATHER THAN ON ITS INPUT -- its own
    # comment said so, and said the test that proved it could fail had to
    # REPLACE `gather` to reach it. That is the shape `docs/gates.md` names: a
    # check reachable only by breaking the producer is answering a question the
    # types now answer.
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
        chief=_chief_copy(proof.read_from, resolved, proof),
        problems=problems,
        drift=drift,
        coverage=coverage,
        escalations=escalations,
        rereads=rereads,
        revisit=revisit,
        tally=counts,
        order=order,
    )
