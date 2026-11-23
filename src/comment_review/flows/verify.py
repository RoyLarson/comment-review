"""One admission: whether the fold takes a stage's returned copies, and why not.

    admit(copies, root, ...)   every rule its inputs allow, then the trial fold
    Admission                  what it found, and the fold it ran

`collate`, `check`, `mark` and `proof --copy` each call `admit`, and they
differ only in the inputs they pass. Each rule runs exactly when its input is
given, so an entry point that lacks an input does not ask the rule that reads
it, and its own docstring names the input.

The first step admits each page's identity once for the load
(`flows.reading_context.admit_pages`), or takes the table a caller that already
admitted the copy hands it (`flows.fill`); a refusal there is reported apart, as
`Admission.unadmitted`, and nothing else is asked. Then each question the desk
cannot ask is settled against the pages: whether a quote is on the page and a
cite resolves, whether an address names a place a real page carries, whether a
role carried back everything it was handed, and whether every dispatch came
back. Then the fold itself runs over the copies (`desk.work.fold.Fold`), so
what a mark's row reads at each place and whether marks at one place compose
are the fold's own answers. A human query is an ask, never fold input: the
fold refuses one, so it is left out of the trial fold, which runs whether or
not questions stand.

Every finding is a `desk.collator.Problem` -- reported, never raised, so the
findings stack and each can be sent back to the role that owes it.
"""

from collections.abc import Mapping
from dataclasses import replace
from pathlib import Path
from typing import NamedTuple

from comment_review.binder.addresses import handed
from comment_review.binder.binder import Binder
from comment_review.desk import report as events
from comment_review.desk.collator import Cache, Problem, verify_report
from comment_review.desk.marks.table import INSTRUCTIONS, Stance
from comment_review.desk.proof.edit_copy import EditCopy
from comment_review.desk.proof.mark import Touch
from comment_review.desk.stages import Stage, deals, not_admitted
from comment_review.desk.work.fold import Fold
from comment_review.flows.human import (
    HumanAnswer,
    HumanQuery,
    answered,
    corrections_to_matter,
    queries_in_copies,
)
from comment_review.flows.mark_errors import mark_errors
from comment_review.flows.on_the_page import (
    PageCache,
    held_at,
    no_page,
    page_named,
    printed_name,
)
from comment_review.flows.places import bases_and_anchors, places_of
from comment_review.flows.reading_context import admit_pages
from comment_review.reading.addresser import address_for, cue_of, folded
from comment_review.reading.context import Imprint
from comment_review.reading.diagnostics import ReadFailure


class Admission(NamedTuple):
    """What one admission found, and the trial fold it ran.

    Attributes:
        imprints: the identity table of the load, real path -> sha and reading.
        pages: every page read, by real path, for a caller that records them.
        unadmitted: one per page identity that will not admit, routed to the
            role whose input claimed it. Where any is, nothing else was asked.
        problems: every refusal, the rules' first and then the fold's.
        asks: each human question, with the human's answer where the answers
            file holds one.
        approvals: each change to the file's matter the answers file has not
            approved.
        fold: the trial fold, or None where it was not run. With no problems
            and no asks it has committed, and it is the stage's fold.
    """

    imprints: dict[str, Imprint]
    pages: PageCache
    unadmitted: list[Problem]
    problems: list[Problem]
    asks: list[tuple[HumanQuery, HumanAnswer | None]]
    approvals: list[HumanQuery]
    fold: Fold | None


def admit(
    copies: list[EditCopy],
    root: Path,
    *,
    binder: Binder | None = None,
    received: tuple[Binder, ...] | None = None,
    stage: str | None = None,
    row: Stage | None = None,
    human: tuple[HumanAnswer, ...] = (),
    only: frozenset[str] | None = None,
    imprints: Mapping[str, Imprint] | None = None,
) -> Admission:
    """Every rule the inputs allow, then the trial fold over the copies.

    Args:
        copies: the parsed copies, as they came back.
        root: the checkout every page and every cited file is read from.
        binder: the binder the copies were seeded from. Without it no place
            is required of a copy, so neither an unruled place nor coverage is
            asked, and an address resolves through the copies' own sheets.
        received: each copy's received binder, in the copies' order; with a
            `binder`, each is checked against it and defines its copy's share.
        stage: the stage label being folded; each copy's own `stage` is
            compared with it.
        row: the stage as the topology declares it; it decides what the stage
            admits, which places it deals, and how many dispatches are owed.
        human: the human's answers file, read.
        only: the addresses one ruling touches. A finding at any other
            address is dropped.
        imprints: the identity table the caller already admitted for these
            copies' sheets in this load, given with no binder -- `flows.fill`
            admits a copy before it places a ruling. Given, the pages are not
            admitted again; None admits every input's pages here.

    Returns:
        The `Admission`.
    """
    table, unadmitted = _table(copies, binder, received, imprints)
    problems: list[Problem] = []
    if received is not None and len(received) != len(copies):
        problems.append(Problem("", "", "each edit copy needs one received binder"))
    if unadmitted or problems:
        return Admission(table, {}, unadmitted, problems, [], [], None)
    paths = (
        [page.path for page in binder.pages]
        if binder is not None
        else list(dict.fromkeys(s.path for copy in copies for s in copy.sheets))
    )
    # ! One cache of each for the whole stage, not one per copy: the roles cite
    # the same evidence and mark the same pages, so a per-copy cache reads one
    # file once per citing role.
    cache: Cache = {}
    pages: PageCache = {}
    for copy in copies:
        problems += [
            *verify_report(
                copy, _texts_at(copy, paths, root, pages, table), root, cache
            ),
            *_resolution_problems(copy, paths, root, pages, table),
        ]
    required = [frozenset[str]()] * len(copies)
    if received is not None:
        required = [_required_places(one) for one in received]
    elif binder is not None:
        required = [_required_places(binder, row)] * len(copies)
    # ! `where` rather than `address`, and the two differ in one case only:
    # an entry that named no place. `where` is that entry's own address
    # wherever it has one, and the page and the entry's position where it has
    # none -- so a reader always has somewhere to look.
    problems += [
        Problem(one.role, one.where, "; ".join(one.reasons))
        for one in mark_errors(copies, required)
    ]
    if received is not None and binder is not None:
        problems += _received_problems(copies, received, binder, row)
    elif binder is not None:
        for copy in copies:
            problems += _coverage_problems([copy], binder, row)
            if problem := _gathered_tree_problem(copy, binder):
                problems.append(problem)
    if stage is not None:
        problems += _dealt_problems(copies, stage)
    problems += _admitted_problems(copies, row)
    if row is not None:
        problems += _stage_problems(row, copies)
    queries = queries_in_copies(copies)
    asks = answered(queries, list(human))
    approvals = corrections_to_matter(copies, human)

    # The trial fold. A human query is left out of it, since the fold refuses
    # one; with no queries the copies are folded as they are, so a commit's
    # positions are the copies' own.
    folding = [_without_queries(copy) for copy in copies] if queries else copies
    held = bases_and_anchors(
        folding, lambda address: held_at(address, paths, root, pages, imprints=table)
    )
    fold = None
    if isinstance(held, ReadFailure):
        # A page a mark's address names and no page answers for is already
        # refused by resolution; this one is reported only where nothing is.
        if not problems:
            problems += [
                Problem(copy.role, "", d.message)
                for copy in copies
                for d in held.diagnostics
            ]
    else:
        fold = Fold(places_of(folding, *held)).run()
        problems += [
            Problem(one.role, one.address, reason)
            for one in fold.events
            if isinstance(one, events.Refused)
            for reason in one.reasons
        ]
    if only is not None:
        problems = [one for one in problems if one.address in only]
    return Admission(table, pages, [], problems, asks, approvals, fold)


def _table(
    copies: list[EditCopy],
    binder: Binder | None,
    received: tuple[Binder, ...] | None,
    imprints: Mapping[str, Imprint] | None,
) -> tuple[dict[str, Imprint], list[Problem]]:
    """The load's identity table, and one refusal per identity that will not admit.

    A table the caller admitted is taken as it is. Otherwise the stage binder
    is the reference; each received binder, then each copy, is one later claim
    on the pages it holds. A refusal goes to the role whose input it names, and
    one about the stage binder to no role.
    """
    if imprints is not None:
        return dict(imprints), []
    sources = [
        *([("stage binder", binder.pages, "")] if binder is not None else []),
        *(
            (
                f"received binder {i}",
                one.pages,
                copies[i - 1].role if i <= len(copies) else "",
            )
            for i, one in enumerate(received or (), 1)
        ),
        *((f"edit_copy: {copy.role}", copy.sheets, copy.role) for copy in copies),
    ]
    owner = {label: role for label, _, role in sources}
    table, why = admit_pages(*((label, records) for label, records, _ in sources))
    return table, [Problem(owner[one.source], "", one.text) for one in why]


def _without_queries(copy: EditCopy) -> EditCopy:
    """The copy with every human query taken off its sheets."""
    return replace(
        copy,
        sheets=tuple(
            replace(
                sheet,
                marks=tuple(
                    mark
                    for mark in sheet.marks
                    if INSTRUCTIONS[mark.instruction].pairs(mark)
                    is not Stance.UNSETTLABLE
                ),
            )
            for sheet in copy.sheets
        ),
    )


def _gathered_tree_problem(copy: EditCopy, binder: Binder) -> Problem | None:
    """Name a copy whose gathered tree differs from the binder's."""
    if copy.read_from == binder.read_from:
        return None
    return Problem(
        copy.role,
        "",
        f"copy and binder name different gathered trees: "
        f"{copy.read_from!r} and {binder.read_from!r}",
    )


def _resolution_problems(
    copy: EditCopy,
    paths: list[str],
    root: Path,
    cache: PageCache,
    imprints: Mapping[str, Imprint],
) -> list[Problem]:
    """One `Problem` per ruled mark whose address resolves against no page.

    An address resolves when a page can be read at its path and that page
    carries its cue. Where this checkout holds no readable page there, the
    address resolves against nothing and is reported, as a quote there is
    refused. An address the binder lacks is not thereby unresolved: the page
    is read, not the binder, and the page carries every place a series has,
    filled or not.

    The address a mark names its destination under -- `claim.to` on a
    `move`, its type's `names_destination` -- is an address as well, and
    resolves the same way. An address that is not `path@cue` resolves against
    nothing -- `path@cue` is the only address built -- and one resolves only
    as it is printed: the binder's spelling of its path, or the checkout's for
    a page the binder lacks, and the page's spelling of its cue. A case slip or stray
    whitespace is refused, naming the printed address; a file system that
    ignores case would otherwise open the page, and the docket would carry it
    as a second page.

    Args:
        copy: one parsed edit_copy, as it came back.
        paths: the binder's own page paths, for `flows.on_the_page.real_path`.
        root: the checkout every page is read from.
        cache: shared across the stage's copies, keyed by real path.
        imprints: the identity table admitted for this load.

    Returns:
        One `Problem` per mark whose path no page can be read at, or whose
        cue its page does not carry, and one per mark whose destination
        fails the same way, at the mark's own address and naming the claim
        key it was read under, in sheet then mark order. A mark with no
        address has no place to resolve: `desk.marks.table.Row.places` leaves
        it out, and `clean` is the one row that may carry none.
    """
    out: list[Problem] = []
    for sheet in copy.sheets:
        for mark in sheet.marks:
            row = INSTRUCTIONS[mark.instruction]
            for where, touch in row.places(mark):
                why = _unresolved(where, paths, root, cache, imprints)
                if not why:
                    continue
                if touch is Touch.DESTINATION:
                    out.append(
                        Problem(
                            copy.role,
                            mark.address,
                            f"`claim.{mark.names_destination}` {where!r} resolves"
                            f" against no page -- {why}",
                        )
                    )
                else:
                    out.append(
                        Problem(copy.role, where, f"resolves against no page -- {why}")
                    )
    return out


def _unresolved(
    address: str,
    paths: list[str],
    root: Path,
    cache: PageCache,
    imprints: Mapping[str, Imprint],
) -> str:
    """Why `address` resolves against no page, or "" where it resolves.

    The page and the place are found under `reading.addresser.folded`, so a
    misspelling is named with the address it misspells rather than as a
    missing page or cue.

    Args:
        address: a mark's own address, or the destination its row names.
        paths: the binder's own page paths, for `flows.on_the_page.real_path`.
        root: the checkout every page is read from.
        cache: shared across the stage's copies, keyed by real path.
        imprints: the identity table admitted for this load.
    """
    addr = cue_of(address)
    if not addr.path or not addr.cue:
        return "it is not a `path@cue` address"
    name = printed_name(addr.path, paths, root) or addr.path
    real, page = page_named(name, paths, root, cache, imprints=imprints)
    if isinstance(page, ReadFailure):
        return no_page(real) + ": " + "; ".join(d.message for d in page.diagnostics)
    cue = next((c for c in page.cues.places if folded(c) == folded(addr.cue)), "")
    if not cue:
        return f"{real} carries no place {addr.cue!r}"
    printed = address_for(name, cue)
    if address != printed:
        return f"it is spelled otherwise than the page prints it, {printed!r}"
    return ""


def _texts_at(
    copy: EditCopy,
    paths: list[str],
    root: Path,
    pages: PageCache,
    imprints: Mapping[str, Imprint],
) -> dict[str, tuple[str, ...]]:
    """Every text a quote on `copy` may be in, keyed by the mark's address.

    Each successful lookup offers the page's text at the mark's own address,
    including an empty string for an absent paragraph or place. A failed read
    is omitted rather than offered as empty text; `_resolution_problems`
    reports it.
    """
    out: dict[str, tuple[str, ...]] = {}
    for sheet in copy.sheets:
        for mark in sheet.marks:
            if mark.address in out:
                continue
            result = held_at(mark.address, paths, root, pages, imprints=imprints)
            if not isinstance(result, ReadFailure):
                out[mark.address] = (result.text,)
    return out


def _required_places(binder: Binder, stage: Stage | None = None) -> frozenset[str]:
    """The review addresses required by this binder and stage.

    ! The places a role was handed, not every address the binder carries --
    `binder.addresses.handed` is the one definition, and the seed reads it too.
    They are narrowed by the same `deals` the seed used, so the two cannot
    disagree about which places a stage dealt.
    """
    return frozenset(
        b.address for b in handed(binder.paragraphs) if stage is None or deals(stage, b)
    )


def _received_problems(
    copies: list[EditCopy],
    binders: tuple[Binder, ...],
    binder: Binder,
    stage: Stage | None,
) -> list[Problem]:
    """Check paired binders, given that one is paired with each copy."""
    known = _required_places(binder, stage)
    paths = {page.path for page in binder.pages}
    by_role: dict[str, set[str]] = {}
    pages_by_role: dict[str, set[str]] = {}
    out = []
    for copy, received in zip(copies, binders, strict=True):
        assigned = _required_places(received)
        received_paths = {page.path for page in received.pages}
        if received.read_from != binder.read_from:
            out.append(
                Problem(
                    copy.role,
                    "",
                    "received binder and stage binder name different gathered trees",
                )
            )
        elif problem := _gathered_tree_problem(copy, received):
            out.append(problem)
        if assigned - known or received_paths - paths:
            out.append(
                Problem(copy.role, "", "received binder exceeds the stage assignment")
            )
        covered = by_role.setdefault(copy.role, set())
        covered_pages = pages_by_role.setdefault(copy.role, set())
        if covered & assigned or covered_pages & received_paths:
            out.append(
                Problem(copy.role, "", "received binders overlap within this role")
            )
        covered.update(assigned)
        covered_pages.update(received_paths)
        out.extend(_coverage_problems([copy], received))
    for role, covered in by_role.items():
        missing = sorted(known - covered)
        missing_pages = sorted(paths - pages_by_role[role])
        if missing or missing_pages:
            out.append(
                Problem(
                    role,
                    "",
                    "received binders miss " + ", ".join(missing or missing_pages),
                )
            )
    return out


def _coverage_problems(
    edit_copies: list[EditCopy], binder: Binder, stage: Stage | None = None
) -> list[Problem]:
    """One `Problem` per role whose copies do not carry the binder's addresses.

    !! `flows.fan_out.dealt` refuses at the dispatch and does not read the
    return. It raises `OverlappingShards` and `UncoveredPage` over the pages it
    is about to hand out; a role that then answers for three of the four files
    in its shard is found here.

    !! The union across a role's copies, never one copy against the binder.
    Under fan-out each copy carries only its own shard, so comparing per copy
    would report every shard of a correctly partitioned role as incomplete.

    ! Stage coverage is a different question and cannot be answered from here.
    A role that returned nothing leaves nothing behind to be missing from,
    since `flows.distribute.seed` stamps a copy with `role`, `read_from` and
    `sheets` and no dispatch identity. That one is `_stage_problems`, which
    takes the `Stage`.

    Args:
        edit_copies: the copies as they came back, already parsed.
        binder: the binder they were seeded from.
        stage: the stage they were dealt in, where the caller has the row.
            A stage that deals part of the binder is owed that part and no
            more. None measures against every
            place a role is handed, which is what an ordinary stage deals.

    Returns:
        One `Problem` per short role, naming every address that role did not
        carry, sorted so a reader can re-derive the list. Empty where every
        role is complete. Reported rather than raised, so the findings stack;
        each one rolls the round back, and none of the places that did come
        back is decided.

    ! An empty binder yields nothing. There is no address to be missing.

    A stage that deals part of the binder and is collated without its row is
    reported short, and correctly: nothing else in the run says which places
    were dealt, so a caller that names no topology is asking this to measure
    against the whole binder.
    """
    known = _required_places(binder, stage)
    if not known:
        return []
    # !! All three kinds count as carried, and that is the whole point of this
    # check. It asks whether the copy came back with the binder's addresses, not
    # whether the role ruled on them -- an untouched slot and an entry that
    # would not parse are both places the role still has. Whether it answered is
    # `flows.mark_errors`' question, which `admit` runs beside this one.
    # ! A refused entry with no address contributes nothing, since there is no
    # place to say it carried.
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
            # !! The addresses lead, and the count follows, so a reader
            # reaches a place to look as soon as possible. This line's
            # `address` field is empty -- the finding is about the copy, so
            # the places it names can only be in the message. Every other line
            # opens with its place; this one does too.
            #
            # !! Counted over the intersection, not over everything returned.
            # `carried` holds every address the role sent back, including any
            # the binder never held, so `len(carried)` can equal `len(known)`
            # while something is still missing: a role that dropped `m.py@b5`
            # and invented `m.py@b9` against a two-place binder would report
            # 2 of 2 places while naming `m.py@b5` missing.
            #
            # ! An address the binder never held is not reported at all. A
            # role may cite a place the filter dropped or a
            # file the run never gathered; whether the page has it is
            # `_resolution_problems`' question, which reads the page. This
            # counts what came back against what was handed out, and nothing
            # more.
            out.append(
                Problem(
                    role,
                    "",
                    f"missing {', '.join(missing)} -- answered for "
                    f"{len(carried & known)} of {len(known)} places",
                )
            )
    return out


def _stage_problems(dispatches: Stage, edit_copies: list[EditCopy]) -> list[Problem]:
    """One `Problem` per role that returned fewer copies than the stage dispatched.

    ! Stage coverage, as against shard coverage. `_coverage_problems` asks
    whether a copy that came back carries the addresses it was handed; this
    asks whether every dispatch the topology named came back at all. A role
    dispatched twice under fan-out that returned once leaves nothing behind to
    be short -- only the topology knows a second copy was owed.
    """
    returned: dict[str, int] = {}
    for copy in edit_copies:
        returned[copy.role] = returned.get(copy.role, 0) + 1
    owed: dict[str, int] = {}
    for dispatch in dispatches.dispatches:
        owed[str(dispatch.role)] = owed.get(str(dispatch.role), 0) + 1
    return [
        Problem(
            role,
            "",
            f"stage {dispatches.name}: {role} returned {returned.get(role, 0)}"
            f" of {want} dispatches",
        )
        for role, want in owed.items()
        if returned.get(role, 0) < want
    ]


def _dealt_problems(copies: list[EditCopy], stage: str) -> list[Problem]:
    """One `Problem` per copy dealt in a stage other than the one being folded.

    A copy folds only in the stage it was dealt in: its `admits` and its
    places are that stage's, so a stage-6 copy handed to stage 4 would be
    held to the wrong row -- and without a topology, to none. A copy that
    names no stage (`""`, seeded without a row) is not compared.

    Returns:
        One `Problem` per copy whose own `stage` names another, with no
        address -- the finding is about the document.
    """
    return [
        Problem(
            copy.role,
            "",
            f"was dealt in stage {copy.stage!r}, and this is stage {stage!r} -- a"
            " copy folds only in the stage it was dealt in",
        )
        for copy in copies
        if copy.stage and copy.stage != stage
    ]


def _admitted_problems(copies: list[EditCopy], stage: Stage | None) -> list[Problem]:
    """One `Problem` per mark filed under an instruction its stage does not admit.

    Args:
        copies: the parsed copies, as they came back.
        stage: the row they were dealt under, where the caller has it. None
            leaves the copy's own `admits` as the only statement there is.

    Returns:
        One `Problem` per refused mark, at that mark's address, and one per
        copy whose own `admits` disagrees with the row, with no address --
        that finding is about the document. Empty where every mark is one its
        stage admits.

    The field is compared rather than trusted. A copy that widened its
    `admits` passes wherever no row is given, and one that cleared the
    field reads as every instruction there; comparing it with the row is
    what makes either loud instead of silent.
    """
    problems: list[Problem] = []
    for copy in copies:
        admits = tuple(stage.admits) if stage is not None else copy.admits
        named = stage.name if stage is not None else copy.stage
        if stage is not None and copy.admits != tuple(stage.admits):
            problems.append(
                Problem(
                    copy.role,
                    "",
                    f"says it may file {_named(copy.admits)}, and stage"
                    f" {stage.name}'s row admits {_named(stage.admits)} -- what a"
                    " stage admits is the row's, not the copy's",
                )
            )
        problems += [
            Problem(copy.role, mark.address, why)
            for sheet in copy.sheets
            for mark in sheet.marks
            for why in [not_admitted(named, admits, str(mark.instruction))]
            if why
        ]
    return problems


def _named(admits: tuple[str, ...]) -> str:
    """What a set of admitted instructions is called in a reason."""
    return ", ".join(admits) if admits else "every instruction"
