"""What one stage's returned copies can be wrong about against the pages.

    copy_problems        one copy against the pages and the files it cites
    texts_at             every text a quote on one copy may be in
    resolution_problems  a ruled mark whose address resolves against no page
    coverage_problems    a role whose copies do not carry the binder's addresses
    stage_problems       a dispatch the topology named that never came back

Each asks a question the desk cannot: `desk.marks.mark.parse` holds no
binder, no page and no filesystem, so whether an address names a place a real
page carries, and whether a role carried back everything it was handed, are
settled here instead.

`flows.bus` runs `copy_problems` over every copy, then the two coverage
checks, before it opens a fold; `commands/check.py` runs `copy_problems` over
the one copy it is handed, so a role learns before it returns its copy what
the fold would refuse. Every finding is a `desk.collator.Problem` -- reported,
never raised, so the findings stack and each can be sent back to the role
that owes it.

One page is read once per stage. The caller owns a
`flows.on_the_page.PageCache` and hands the same one to every copy, as it
keeps one `desk.collator.Cache` for the files the marks cite.
"""

from pathlib import Path

from comment_review.binder.addresses import handed
from comment_review.binder.binder import Binder
from comment_review.desk.collator import Cache, Problem, verify_report
from comment_review.desk.containers import EditCopy
from comment_review.desk.marks.table import INSTRUCTIONS
from comment_review.desk.stages import Stage, deals
from comment_review.flows.on_the_page import PageCache, held_at, no_page, page_named
from comment_review.reading.addresser import cue_of


def copy_problems(
    copy: EditCopy, paths: list[str], root: Path, cache: Cache, pages: PageCache
) -> list[Problem]:
    """What one copy is wrong about against the pages and the files it cites.

    Source verification over the texts the page holds at each mark's place
    (`desk.collator.verify_report`, `texts_at`), then the resolution check.
    `flows.bus` runs it over every copy of a stage before it opens a fold, and
    `commands/check.py` runs it over the one copy it is handed, so the two
    hold a copy to one list.

    Args:
        copy: one parsed edit_copy, as it came back.
        paths: the binder's own page paths, for `flows.on_the_page.real_path`.
        root: the checkout every page and every cited file is read from.
        cache: the cited files, shared across the stage's copies.
        pages: the pages, shared across the stage's copies.

    Returns:
        Every problem found, source verification's first.
    """
    return [
        *verify_report(copy, texts_at(copy, paths, root, pages), root, cache),
        *resolution_problems(copy, paths, root, pages),
    ]


def resolution_problems(
    copy: EditCopy, paths: list[str], root: Path, cache: PageCache
) -> list[Problem]:
    """One `Problem` per ruled mark whose address resolves against no page.

    An address resolves when a page can be read at its path and that page
    carries its cue. Where this checkout holds no readable page there, the
    address resolves against nothing and is reported, as a quote there is
    refused (`decision-log.md Process: #122`). An address the binder lacks is
    not thereby unresolved: the page is read, not the binder (`Process: #97`),
    and the page carries every place a series has, filled or not.

    A `move`'s `claim.to` is an address as well, and resolves the same way
    (`Process: #111`). A destination that is not `path@cue` resolves against
    nothing -- `path@cue` is the only address built (`Addressing: #21`).

    Verify: an invented cue is refused, a valid empty place is not -- the case
    `Process: #97` settled, restated against the real page rather than the
    redacted binder.

    Args:
        copy: one parsed edit_copy, as it came back.
        paths: the binder's own page paths, for `flows.on_the_page.real_path`.
        root: the checkout every page is read from.
        cache: shared across the stage's copies, keyed by real path.

    Returns:
        One `Problem` per mark whose path no page can be read at, or whose
        cue its page does not carry, and one per `move` whose `claim.to`
        fails the same way, at the move's own address, in sheet then mark
        order. An empty address is skipped -- `clean` is the one row a mark
        may carry none for, and there is no place to resolve.
    """
    out: list[Problem] = []
    for sheet in copy.sheets:
        for mark in sheet.marks:
            addr = cue_of(mark.address)
            if addr.path and addr.cue:
                why = _unresolved(mark.address, paths, root, cache)
                if why:
                    out.append(
                        Problem(
                            copy.role,
                            mark.address,
                            f"resolves against no page -- {why}",
                        )
                    )
            if INSTRUCTIONS[mark.instruction].owes_destination:
                to = str(mark.claim.get("to", ""))
                why = _unresolved(to, paths, root, cache)
                if why:
                    out.append(
                        Problem(
                            copy.role,
                            mark.address,
                            f"`claim.to` {to!r} resolves against no page -- {why}",
                        )
                    )
    return out


def _unresolved(address: str, paths: list[str], root: Path, cache: PageCache) -> str:
    """Why `address` resolves against no page, or "" where it resolves.

    Args:
        address: a mark's own address, or a `move`'s `claim.to`.
        paths: the binder's own page paths, for `flows.on_the_page.real_path`.
        root: the checkout every page is read from.
        cache: shared across the stage's copies, keyed by real path.
    """
    addr = cue_of(address)
    if not addr.path or not addr.cue:
        return "it is not a `path@cue` address"
    real, page = page_named(addr.path, paths, root, cache)
    if page is None:
        return no_page(real)
    if addr.cue not in page.cues.places:
        return f"{real} carries no place {addr.cue!r}"
    return ""


def texts_at(
    copy: EditCopy, paths: list[str], root: Path, pages: PageCache
) -> dict[str, tuple[str, ...]]:
    """Every text a quote on `copy` may be in, keyed by the mark's address.

    `decision-log.md Process: #119`: the text at the mark's own address, read
    from the page whether or not the binder holds that place or its file. It
    is "" where no page can be read or the page holds nothing at the place.

    Args:
        copy: one parsed edit_copy.
        paths: the binder's own page paths, for `flows.on_the_page.real_path`.
        root: the checkout every page is read from.
        pages: shared across the stage's copies, keyed by real path.

    Returns:
        address -> the texts, one entry per address a ruled mark carries. The
        tuple holds the page's own text and nothing else; it is a tuple
        because `desk.collator.verify_report` asks whether a quote is in any
        of the texts a place offers.
    """
    out: dict[str, tuple[str, ...]] = {}
    for sheet in copy.sheets:
        for mark in sheet.marks:
            if mark.address in out:
                continue
            out[mark.address] = (held_at(mark.address, paths, root, pages).text,)
    return out


def coverage_problems(
    edit_copies: list[EditCopy], binder: Binder, stage: Stage | None = None
) -> list[Problem]:
    """One `Problem` per role whose copies do not carry the binder's addresses.

    !! `flows.fan_out.fan` REFUSES AT THE DISPATCH AND NOTHING READ THE RETURN.
    It raises `OverlappingShards` and `UncoveredPage` over the pages it is about
    to hand out; a role that then answered for three of the four files in its
    shard was invisible.

    !! THE UNION ACROSS A ROLE'S COPIES, NEVER ONE COPY AGAINST THE BINDER.
    Under fan-out each copy carries only its own shard, so comparing per copy
    would report every shard of a correctly partitioned role as incomplete.

    ! STAGE COVERAGE IS A DIFFERENT QUESTION and cannot be answered from here.
    A role that returned nothing leaves nothing behind to be missing from,
    since `flows.distribute.seed` stamps a copy with `role`, `read_from` and
    `sheets` and no dispatch identity. That one is `stage_problems`, which
    takes the `Stage`.

    Args:
        edit_copies: the copies as they came back, already parsed.
        binder: the binder they were seeded from.
        stage: the stage they were dealt in, where the caller has the row.
            A stage that deals part of the binder is owed that part and no
            more -- `decision-log.md Process: #193`, Roy: only the places over
            the length limit are touched, and all the others are
            automatically clean for this role. None measures against every
            place a role is handed, which is what an ordinary stage deals.

    Returns:
        One `Problem` per short role, naming every address that role did not
        carry, sorted so a reader can re-derive the list. Empty where every
        role is complete. Reported rather than raised, so the findings stack;
        each one rolls the round back, and none of the places that did come
        back settles (`Process: #186`).

    ! AN EMPTY BINDER YIELDS NOTHING. There is no address to be missing, and a
    run over one is what `tests/test_brief_worked_example.py` drives.

    A stage that deals part of the binder and is collated without its row is
    reported short, and correctly: nothing else in the run says which places
    were dealt, so a caller that names no topology is asking this to measure
    against the whole binder.
    """
    # ! THE PLACES A ROLE WAS HANDED, not every address the binder carries --
    # `binder.addresses.handed` is the one definition, and the seed reads it too.
    # And narrowed by the same `deals` the seed used, so the two cannot
    # disagree about which places a stage dealt.
    known = frozenset(
        b.address for b in handed(binder.paragraphs) if stage is None or deals(stage, b)
    )
    if not known:
        return []
    # !! ALL THREE KINDS COUNT AS CARRIED, and that is the whole point of this
    # check. It asks whether the copy came BACK with the binder's addresses, not
    # whether the role ruled on them -- an untouched slot and an entry that
    # would not parse are both places the role still HAS. Whether it answered
    # is `flows.mark_errors`' question, and `commands/collate.py` reports that
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
            # ! AN ADDRESS THE BINDER NEVER HELD IS NOT REPORTED AT ALL --
            # `Process: #97`. A role may cite a place the filter dropped or a
            # file the run never gathered; whether the page has it is
            # `resolution_problems`' question, which reads the page. This
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


def stage_problems(dispatches: Stage, edit_copies: list[EditCopy]) -> list[Problem]:
    """One `Problem` per role that returned fewer copies than the stage dispatched.

    ! STAGE COVERAGE, as against shard coverage. `coverage_problems` asks
    whether a copy that came back carries the addresses it was handed; this
    asks whether every dispatch the topology named came back AT ALL. A role
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
