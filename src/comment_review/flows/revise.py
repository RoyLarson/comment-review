"""Pull a revise: a second proof of the whole tree, one stage's corrections set.

    the docket           the settled alterations for one editorial boundary
        -> copy the repo         FIRST, so every file the docket does not
                                  name is still present under the revise root
        -> proof_setter.run      into a SCRATCH directory, disjoint from both
                                  the checkout and the copy
        -> overlay each draft    onto the copy, at the page path it names
        -> the revise root       what the next stage reads instead of the repo

`TODO/the-flow-assumes-every-role-reads-at-once.md` names the revise as the
trade's word for this -- *"the second proof, pulled after the marked
corrections have been set"* -- and T3 is what this module delivers.

!! A REFUSAL DISCARDS THE WHOLE REVISE, not only the drafts `proof_setter`
already discards. `docs/decision-log.md Process: #20` -- *"a refusal aborts
the run whole"* -- is `proof_setter.run`'s own ruling for ITS directory; this
module carries the same ruling one level up, for the copy `pull` made. A
revise root that held some of a stage's corrections and not the rest would be
indistinguishable from one that held all of them, so nothing partial is left
on disk: `Pulled.root` does not exist after a refusal.

! `proof_setter.run` PROVES EACH DRAFT; NOTHING HERE RE-PROVES IT. What
`pull` adds is the assembly -- the untouched files a docket says nothing
about, moved from a copy rather than re-read -- and `prove_unchanged` run
over the ASSEMBLED root is what task 8's own step 5 checks, once, from
outside this module.
"""

import shutil
import tempfile
from pathlib import Path
from typing import NamedTuple

from comment_review.binder.binder import Binder, bind
from comment_review.desk.collator import known_addresses
from comment_review.desk.containers import EditCopy
from comment_review.desk.mark import Instruction, text_at
from comment_review.docket.docket import Alteration, Docket, Schedule
from comment_review.flows import proof_setter
from comment_review.flows.page_for import page_of
from comment_review.machine.repo import remove_tree, walk_files
from comment_review.reading.addresser import address_for, cue_of
from comment_review.reading.lexer import language_for


class Pulled(NamedTuple):
    """One revise: where it landed, which number it is, and who set what.

    Attributes:
        root: the revise -- a full copy of the repo with the docket's pages
            overlaid. Absent when `refusals` is non-empty.
        revise: the number this revise was pulled as. Passed through, never
            computed here -- `TODO/the-flow-assumes-every-role-reads-at-once.md`
            T2 is what a binder later reads this against.
        set_by: address -> the role that set it, over every alteration the
            docket named. This is the provenance a later phase (P6) routes
            on, not decoration. `role` is one per page in `docket.py`'s
            schema (`path`, `sha`, `role`, `alterations`) and optional --
            `desk.collator.docket_from` is what writes it, from T4.2's
            settled places; a docket with none maps every one of its
            addresses to `""`.
        refusals: every `proof_setter.Refusal`, or `[]` on success. Non-empty
            means `root` was discarded and does not exist.
    """

    root: Path
    revise: int
    set_by: dict[str, str]
    refusals: list[proof_setter.Refusal]


class AddressesMoved(Exception):
    """`pulled.root` does not address the same places `original` did.

    !! THE WHOLE SAFETY ARGUMENT FOR THE STAGED DESIGN -- `docs/decision-log.md
    Process: #35`. Everything downstream assumes a mark written at a later
    stage against `foo.py@b7` names the place an earlier stage saw, which is
    true only while the executable code is byte-identical. This names the one
    way that stops holding: a revise whose code moved, so a place below the
    change renumbers under it.
    """


def docket_of(copy: EditCopy) -> Docket:
    """One edit_copy, transcribed into the docket the write chain reads.

    !! ANY COPY, NOT ONLY THE COPY CHIEF'S. Roy, 2026-09-02: *"it could also be
    ownership contexts edit-copy or any intermediate edit-copy which allows the
    stage outputs to run."* A stage's own output therefore becomes a revise,
    which is the mechanism `reads = "revise:N"` and stage `4b` both need.
    `decision-log.md Process: #76`.

    !! A `move` IS ONE MARK AND TWO ALTERATIONS. `INSTRUCTIONS[MOVE].claim_all`
    is `("from", "to")`, so the single entry a copy carries names both places:
    the delete at its own `address`, the text at `claim.to`. **The copy does not
    have to carry a move twice** -- `flows.collate._chief_copy` writes it once,
    and once is sufficient because the mark holds both ends.

    ! WHEN `move-is-a-composite-mark` LANDS this collapses to one alteration per
    mark: a `drop` at the origin and an `add` at the destination are two marks
    with two addresses, and the branch below has nothing left to do.

    !! IT LIVES IN THE FLOW BECAUSE A FLOW MAY REACH BOTH ENDS AND NEITHER END
    MAY REACH THE OTHER. Roy, 2026-08-31: *"No direct coupling inside of ends and
    middle, flows are neither they run the steps."* `Docket.of(edit_copy)` was
    offered and declined -- it would put a middle type in `docket/docket.py`,
    which imports nothing at all today.

    Args:
        copy: a returned edit_copy, already through `EditCopy.deserialize`.

    Returns:
        A `Docket` -- one `Schedule` per sheet that carries at least one mark,
        each naming that sheet's own path and sha and the COPY's role.

    ! A SHEET WITH NO MARKS GETS NO SCHEDULE. A seeded copy holds a slot for
    every place; only the ones a role filled are edits, and an empty schedule
    would tell the write end to set a page from nothing.
    """
    schedules = []
    for sheet in copy.sheets:
        alterations = []
        for mark in sheet.marks:
            alterations.append(
                Alteration(
                    cue=cue_of(mark.address).cue,
                    text=text_at(mark.address, mark),
                )
            )
            if mark.instruction is Instruction.MOVE:
                destination = mark.claim["to"]
                alterations.append(
                    Alteration(
                        cue=cue_of(destination).cue,
                        text=text_at(destination, mark),
                    )
                )
        if alterations:
            schedules.append(
                Schedule(
                    path=sheet.path,
                    sha=sheet.sha,
                    alterations=tuple(alterations),
                    role=copy.role,
                )
            )
    return Docket(schedules=tuple(schedules))


def pull(docket: Docket, repo: Path, into: Path, revise: int) -> Pulled:
    """The whole tree, with `docket`'s corrections set -- or nothing at all.

    Args:
        docket: the deserialized docket -- the settled alterations for
            one editorial boundary.
        repo: the checkout the docket's pages are read from.
        into: where the revise lands. Must not exist yet -- `shutil.copytree`
            makes it from `repo`.
        revise: the number this revise is pulled as, carried onto `Pulled`
            unexamined.

    Returns:
        `Pulled(into, revise, set_by, [])` when every page in the docket
        passed, or `Pulled(into, revise, {}, refusals)` with `into` removed
        again when any page refused.
    """
    repo = Path(repo)
    into = Path(into)
    # !! THE COPY IS FIRST, so a docket naming only SOME of the tree's pages
    # still leaves a revise root that holds every file -- `proof_setter.run`
    # only ever produces drafts for the pages a docket names.
    shutil.copytree(repo, into)

    # !! THE SCRATCH DIRECTORY IS A SIBLING OF `into`, MADE AFTER THE COPY.
    # `proof_setter.undraftable` refuses a draft directory that overlaps the
    # repo it drafts from, so scratch must be disjoint from `repo`; a fresh,
    # randomly-named directory is disjoint from `into`, and `into.parent` is
    # guaranteed to exist once `into` itself does.
    #
    # ! THIS SAID "DISJOINT FROM BOTH BY CONSTRUCTION" UNTIL 2026-08-28, AND
    # THAT IS A PRECONDITION RATHER THAN A GUARANTEE. It holds while
    # `into.parent` is outside `repo`; call `pull` with an `into` nested inside
    # the checkout and scratch lands inside it too, and `undraftable` then
    # refuses every page. ! The `proof` command is protected by its own
    # `undraftable(out, repo)` check before it gets here; `pull` as a flow is
    # not, so the caller owns this.
    scratch = Path(tempfile.mkdtemp(prefix="revise-scratch-", dir=into.parent))
    try:
        drafted, refusals = proof_setter.run(docket, repo, scratch)
        if refusals:
            # !! ONE RULING, CARRIED UP A LEVEL. `proof_setter.run` already
            # discarded every draft IT wrote on this refusal; what is left
            # here is the copy `pull` made before calling it, and
            # `Process: #20` applies to that copy exactly as it applies to
            # the drafts.
            #
            # !! `repo.remove_tree`, NOT `shutil.rmtree`, SINCE 2026-08-29 --
            # the copy above includes `.git`, whose loose objects git writes
            # READ-ONLY and Windows refuses to unlink. MEASURED on this
            # machine: `shutil.rmtree` raised `PermissionError: [WinError 5]`
            # and left 15 entries, so a refused `proof` run on the platform
            # `CLAUDE.md` names as primary exited with a traceback AND left a
            # complete-looking revise root holding none of the corrections --
            # falsifying `Pulled.refusals`' own docstring.
            remove_tree(into)
            return Pulled(root=into, revise=revise, set_by={}, refusals=refusals)

        for made in drafted:
            target = into / made.path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(made.draft, target)

        pulled = Pulled(root=into, revise=revise, set_by=_set_by(docket), refusals=[])
        # !! THE GATE RUNS BEFORE THE SUCCESS RETURN, on every pull -- this is
        # `Process: #35`'s check, not an opt-in. `AddressesMoved` propagates
        # uncaught: a mismatch here means the assembled revise cannot be
        # trusted, which is a defect in this run, not a state to paper over.
        #
        # !! AND THE COPY GOES WITH IT, WHICH IT DID NOT UNTIL 2026-08-28. The
        # raise left a complete, ordinary-looking revise root on disk -- and a
        # root whose ADDRESSES MOVED is worse than a partial one, because
        # nothing about it looks wrong: a later stage reading it would measure
        # every mark against the wrong place, which is the single failure
        # `Process: #35` exists to prevent. ! This module already carries
        # `Process: #20` one level up for the refusal path; the same ruling
        # decides this one.
        assert_addresses_held(repo, pulled)
        return pulled
    except BaseException:
        # !! EVERY WAY OUT BUT THE TWO GOOD ONES DISCARDS THE COPY, and only
        # the refusal and `AddressesMoved` paths did until 2026-08-28 -- while
        # this module's docstring asserted, flatly, that *"nothing partial is
        # left on disk"*.
        #
        # ! THE UNGUARDED PATHS WERE REAL, not hypothetical: `shutil.copy2` in
        # the overlay loop above raises on a full disk, a permission, or a
        # locked target, leaving `into` holding SOME of the stage's corrections
        # and not the rest -- verbatim the state the docstring says cannot
        # exist. An exception escaping `proof_setter.run` left the opposite and
        # worse shape: a pristine, complete-looking copy with NONE of them.
        #
        # ! `BaseException`, NOT `Exception`. A `KeyboardInterrupt` between the
        # copy and the gate leaves exactly the same half-set on disk, and the
        # claim being kept here is about what a later stage can find, not about
        # which class of thing went wrong. Re-raised immediately.
        #
        # ! `ignore_errors` STILL, AND `remove_tree` STILL CLEARS THE WRITE BIT
        # FIRST. An exception is already in flight here, so a second one raised
        # while removing would replace the one the caller needs; what
        # `shutil.rmtree(ignore_errors=True)` did instead was skip every
        # read-only `.git` object and leave the copy standing at exit.
        remove_tree(into, ignore_errors=True)
        raise
    finally:
        remove_tree(scratch, ignore_errors=True)


def assert_addresses_held(original: Path, pulled: Pulled) -> None:
    """Raise `AddressesMoved` unless `pulled` addresses the same places `original` did.

    Args:
        original: the checkout the revise was pulled from -- censused at
            revise 0, the original's own number.
        pulled: the revise. `pulled.root` is censused at `pulled.revise`.

    Raises:
        AddressesMoved: naming the addresses that appeared in the revise and
            the ones that disappeared from the original.
    """
    before = known_addresses(_binder_over(Path(original), 0))
    after = known_addresses(_binder_over(Path(pulled.root), pulled.revise))
    appeared = sorted(after - before)
    disappeared = sorted(before - after)
    if appeared or disappeared:
        raise AddressesMoved(
            f"addresses moved between {original} and {pulled.root}: "
            f"{len(appeared)} appeared {appeared}, "
            f"{len(disappeared)} disappeared {disappeared}"
        )


def _binder_over(root: Path, revise: int) -> Binder:
    """Every page under `root`, censused at `revise` -- what the gate compares.

    ! ADDRESSES ONLY. `annotate` and `code_names` resolve CITATIONS, a
    question this gate never asks, so building a page is as far as this goes.

    ! EVERY LANGUAGE THE CENSUS KNOWS, not only Python -- `Process: #35` is a
    claim about code in general, and a Python-only walk would pass a revise
    that renumbered a Rust or Go file clean.

    !! `absent=True`, so an EMPTY place is carried too. `bind`'s default
    drops a place that holds no prose, and appended code with no comment or
    docstring is exactly that -- a new `undocumented` declaration would be
    invisible to this gate without it, which is the one case `Process: #35`
    exists to catch.
    """
    root = Path(root)
    pages = []
    for path in walk_files(root):
        if language_for(path) is None:
            continue
        rel = path.resolve().relative_to(root.resolve()).as_posix()
        page, why = page_of(path, rel=rel)
        if page is not None:
            pages.append(page)
    return bind(pages, read_from={"root": str(root), "revise": revise}, absent=True)


def _set_by(docket: Docket) -> dict[str, str]:
    """Every altered address, mapped to the role that set it.

    ! READS AN OPTIONAL FIELD. `role` is per page and `desk.collator.docket_from`
    is what writes it; see `Pulled.set_by`'s own docstring for why `""` is what
    a docket with no `role` field yields.

    !! IT READ THE RAW DOCKET DICT UNTIL 2026-08-31, and said so: *"straight off
    the raw docket dict"* was in `Schedule`'s own docstring, naming this
    function. `P41`, `decision-log.md Process: #67`. Four `.get` defaults did
    the work of the shape check the boundary now owns -- and each of them would
    have answered `""` for a malformed page rather than refusing it.

    Args:
        docket: the deserialized docket.

    Returns:
        address -> role, one entry per alteration across every page.
    """
    return {
        address_for(page.path, one.cue): page.role
        for page in docket.schedules
        for one in page.alterations
    }
