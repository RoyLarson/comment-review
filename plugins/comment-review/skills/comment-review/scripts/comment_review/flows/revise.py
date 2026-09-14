"""Pull a revise: a second proof of the pages one stage's corrections set.

    the docket           the settled alterations for one editorial boundary
        -> proof_setter.run      into a scratch directory, disjoint from both
                                  the checkout and `into`
        -> write each draft      into `into`, at the page path it names
        -> the address gate      the docket's pages, original against revise
        -> the revise root       the docket's pages, drafted, and no other file

The revise root holds each page the docket schedules and no other file: the
write phase copies only the files it modifies, `docs/decision-log.md Process:
#117`. A file the docket does not name is absent from the revise, not copied
into it unchanged.

`TODO/the-flow-assumes-every-role-reads-at-once.md` names the revise as the
trade's word for this -- *"the second proof, pulled after the marked
corrections have been set"* -- and T3 is what this module delivers.

!! A REFUSAL DISCARDS THE WHOLE REVISE, not only the drafts `proof_setter`
already discards. `docs/decision-log.md Process: #20` -- *"a refusal aborts
the run whole"* -- is `proof_setter.run`'s own ruling for ITS directory; this
module carries the same ruling one level up, for the directory `pull` makes at
`into`. A revise root that held some of a stage's corrections and not the rest
would be indistinguishable from one that held all of them, so nothing partial
is left on disk: `Pulled.root` does not exist after a refusal.

`proof_setter.run` proves each draft, and nothing here proves it again. What
`pull` adds is where the drafts land -- `into`, at each page's repo path --
and `Process: #35`'s address gate over those same pages.
"""

import shutil
import tempfile
from pathlib import Path
from typing import NamedTuple

from comment_review.binder.binder import Binder, bind
from comment_review.desk.collator import known_addresses
from comment_review.docket.docket import Docket
from comment_review.flows import proof_setter
from comment_review.flows.page_for import page_of
from comment_review.machine.repo import remove_tree
from comment_review.reading.addresser import address_for


class Pulled(NamedTuple):
    """One revise: where it landed, which number it is, and who set what.

    Attributes:
        root: the revise -- each page the docket schedules, as drafted, at its
            repo path under this directory, and no other file
            (`docs/decision-log.md Process: #117`). Absent when `refusals` is
            non-empty.
        revise: the number this revise was pulled as. Passed through, never
            computed here -- `TODO/the-flow-assumes-every-role-reads-at-once.md`
            T2 is what a binder later reads this against.
        set_by: address -> the role that set it, over every alteration the
            docket named. This is the provenance a later phase (P6) routes
            on, not decoration. `role` is one per page in `docket.py`'s
            schema (`path`, `sha`, `role`, `alterations`) and optional --
            `docket_of` writes it from the source copy's own role; a docket
            with none maps every one of its addresses to `""`.
        refusals: every `proof_setter.Refusal`, or `[]` on success. Non-empty
            means `root` was discarded and does not exist.
    """

    root: Path
    revise: int
    set_by: dict[str, str]
    refusals: list[proof_setter.Refusal]


class AddressesMoved(Exception):
    """A docket page in `pulled.root` does not address the places it did in `original`.

    !! THE WHOLE SAFETY ARGUMENT FOR THE STAGED DESIGN -- `docs/decision-log.md
    Process: #35`. Everything downstream assumes a mark written at a later
    stage against `foo.py@b7` names the place an earlier stage saw, which is
    true only while the executable code is byte-identical. This names the one
    way that stops holding: a revise whose code moved, so a place below the
    change renumbers under it.
    """


def pull(docket: Docket, repo: Path, into: Path, revise: int) -> Pulled:
    """The docket's pages, with its corrections set -- or nothing at all.

    `into` holds each page the docket schedules, drafted by `proof_setter.run`
    and written at its repo path, and no other file: the write phase copies
    only the files it modifies (`docs/decision-log.md Process: #117`).

    Args:
        docket: the deserialized docket -- the settled alterations for
            one editorial boundary.
        repo: the checkout the docket's pages are read from.
        into: where the revise lands. Must not exist yet: `pull` makes it,
            and an `into` that is already there raises `FileExistsError` and
            is left as it was.
        revise: the number this revise is pulled as, carried onto `Pulled`
            unexamined.

    Returns:
        `Pulled(into, revise, set_by, [])` when every page in the docket
        passed, or `Pulled(into, revise, {}, refusals)` with `into` removed
        again when any page refused.

    Nothing partial is left on any path. Once `into` is made, any exception
    -- in the drafting, the writing of the drafts into `into`, or the address
    gate -- removes it before propagating.
    """
    repo = Path(repo)
    into = Path(into)
    # `into` is made outside the protection below, so an `into` that already
    # exists raises `FileExistsError` here and is never removed by it.
    into.mkdir(parents=True)
    scratch = None
    try:
        # The scratch directory is a sibling of `into`. `proof_setter.run`
        # refuses, through `undraftable`, a draft directory that overlaps the
        # repo it drafts from, so scratch must be disjoint from `repo`; a fresh,
        # randomly named directory is disjoint from `into`. That holds while
        # `into.parent` is outside `repo`: an `into` nested inside the checkout
        # puts scratch inside it too, and `undraftable` then refuses every page.
        # The `proof` command asks `undraftable(out, repo)` before it gets here;
        # `pull` as a flow does not, so the caller owns this.
        scratch = Path(tempfile.mkdtemp(prefix="revise-scratch-", dir=into.parent))
        drafted, refusals = proof_setter.run(docket, repo, scratch)
        if refusals:
            # !! ONE RULING, CARRIED UP A LEVEL. `proof_setter.run` already
            # discarded every draft IT wrote on this refusal; what is left
            # here is the directory `pull` made before calling it, and
            # `Process: #20` applies to that directory exactly as it applies
            # to the drafts.
            #
            # Nothing has been written into `into` on this path: the drafts go
            # in only once every page has passed.
            remove_tree(into)
            return Pulled(root=into, revise=revise, set_by={}, refusals=refusals)

        # Each draft is written at the path the docket names for its page, and
        # nothing else is written: the revise holds only the files the write
        # phase modifies, `Process: #117`.
        for made in drafted:
            target = into / made.path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(made.draft, target)

        pulled = Pulled(root=into, revise=revise, set_by=_set_by(docket), refusals=[])
        # The gate runs on every pull, before the success return: it is
        # `Process: #35`'s check, not an opt-in. It compares the docket's
        # pages, which are the only pages the revise holds. `AddressesMoved`
        # propagates through the handler below, which removes `into` first --
        # a revise whose addresses moved looks whole, and a later stage
        # reading it would measure every mark against the wrong place.
        assert_addresses_held(repo, pulled, [s.path for s in docket.schedules])
        return pulled
    except BaseException:
        # Every way out but a return discards `into`: an exception escaping
        # `proof_setter.run`, `shutil.copy2` failing part way through writing
        # the drafts on a full disk, a permission or a locked target, and the
        # gate's `AddressesMoved`. Each would leave a revise root holding some
        # of the stage's pages, or pages whose addresses moved, which a later
        # stage cannot tell from a whole one.
        #
        # `BaseException`, not `Exception`: a `KeyboardInterrupt` leaves the
        # same partial revise on disk, and what is kept here is a claim about
        # what a later stage can find. Re-raised at once.
        #
        # `ignore_errors`, because an exception is already in flight and a
        # second one raised while removing would replace the one the caller
        # needs; `remove_tree` clears the read-only bit before it retries, so
        # a read-only file does not keep the copy standing.
        remove_tree(into, ignore_errors=True)
        raise
    finally:
        if scratch is not None:
            remove_tree(scratch, ignore_errors=True)


def assert_addresses_held(original: Path, pulled: Pulled, pages: list[str]) -> None:
    """Raise `AddressesMoved` unless `pulled` addresses the same places `original` did.

    The comparison runs over `pages` alone -- the docket's pages, which are the
    only files the revise holds (`docs/decision-log.md Process: #117`) --
    gathered from both roots at the same repo paths. Neither tree is walked,
    so a file the docket does not name is never read.

    Args:
        original: the checkout the revise was pulled from -- gathered at
            revise 0, the original's own number.
        pulled: the revise. `pulled.root` is gathered at `pulled.revise`.
        pages: the repo path of each page the docket schedules, posix and
            relative to both roots.

    Raises:
        AddressesMoved: naming the addresses that appeared in the revise and
            the ones that disappeared from the original.
    """
    before = known_addresses(_binder_over(Path(original), 0, pages))
    after = known_addresses(_binder_over(Path(pulled.root), pulled.revise, pages))
    appeared = sorted(after - before)
    disappeared = sorted(before - after)
    if appeared or disappeared:
        raise AddressesMoved(
            f"addresses moved between {original} and {pulled.root}: "
            f"{len(appeared)} appeared {appeared}, "
            f"{len(disappeared)} disappeared {disappeared}"
        )


def _binder_over(root: Path, revise: int, pages: list[str]) -> Binder:
    """The named pages under `root`, gathered at `revise` -- what the gate compares.

    `pages` are repo paths, posix and relative to `root`; nothing else under
    `root` is read.

    ! ADDRESSES ONLY. `annotate` and `code_names` resolve CITATIONS, a
    question this gate never asks, so building a page is as far as this goes.

    !! `absent=True`, so an EMPTY place is carried too. `bind`'s default
    drops a place that holds no prose, and appended code with no comment or
    docstring is exactly that -- a new `undocumented` declaration would be
    invisible to this gate without it, which is the one case `Process: #35`
    exists to catch.
    """
    root = Path(root)
    held = []
    for rel in pages:
        page, why = page_of(root / rel, rel=rel)
        if page is not None:
            held.append(page)
    return bind(held, read_from={"root": str(root), "revise": revise}, absent=True)


def _set_by(docket: Docket) -> dict[str, str]:
    """Every altered address, mapped to the role that set it.

    ! READS AN OPTIONAL FIELD. `role` is per page and `docket_of` above is what
    writes it; see `Pulled.set_by`'s own docstring for why `""` is what a
    docket with no `role` field yields.

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
