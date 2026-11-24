"""Pull a revise: a second proof of the pages one stage's corrections set.

    the docket           the decided alterations for one editorial boundary
        -> proof_setter.run      into a scratch directory, disjoint from both
                                  the checkout and `into`
        -> write each draft      into `into`, at the page path it names
        -> the address gate      the docket's pages, original against revise
        -> the revise root       the docket's pages, drafted, and no other file

The revise root holds each page the docket schedules and no other file: the
write phase copies only the files it modifies. A file the docket does not name
is absent from the revise, not copied into it unchanged.

A revise is the trade's word for the second proof, pulled after the marked
corrections have been set.

!! A refusal discards the whole revise, not only the drafts `proof_setter` already
discards. A revise root that held some of a stage's corrections and not the rest
would be indistinguishable from one that held all of them, so nothing partial is
left on disk: `Pulled.root` does not exist after a refusal.

`proof_setter.run` proves each draft, and nothing here proves it again. What
`pull` adds is where the drafts land -- `into`, at each page's repo path --
and the address gate over those same pages.
"""

import contextlib
import itertools
import shutil
import tempfile
from collections.abc import Mapping
from pathlib import Path
from typing import NamedTuple

from comment_review.binder.binder import Binder, bind, known_addresses
from comment_review.docket.docket import Docket
from comment_review.flows import proof_setter
from comment_review.flows.page_for import page_of
from comment_review.flows.read_diagnostics import format_failure
from comment_review.flows.reading_context import admit_pages, context_for
from comment_review.machine.repo import remove_tree
from comment_review.reading.addresser import address_for
from comment_review.reading.context import Imprint, ReadingContext
from comment_review.reading.diagnostics import ReadFailure


class Pulled(NamedTuple):
    """One revise: where it landed and who set what.

    Attributes:
        root: the revise -- each page the docket schedules, as drafted, at its
            repo path under this directory, and no other file. Absent when
            `refusals` is non-empty.
        set_by: address -> the role that set it, over every alteration the
            docket named. `role` is one per page of the docket and optional
            -- `flows.transcribe.docket_of` writes the source copy's own
            role and `docket_of_proof` writes the copy chief's; a page with
            none maps every one of its addresses to `""`.
        refusals: every `proof_setter.Refusal`, or `[]` on success. Non-empty
            means `root` was discarded and does not exist.
    """

    root: Path
    set_by: dict[str, str]
    refusals: list[proof_setter.Refusal]


class AddressesMoved(Exception):
    """A docket page in `pulled.root` no longer addresses its places in `original`.

    A page's places follow from its code, so a revise that keeps the code
    byte-identical keeps them. An address holds for one reading and text may
    read back at another place, which this leaves alone: it compares the sets
    of places, not where any text reads. This names the one way those sets
    change: a revise whose code moved, so a place below the change renumbers
    under it. It is also raised before any comparison, for a page whose saved
    reading context is missing, or that will not read.
    """


def pull(docket: Docket, repo: Path, into: Path) -> Pulled:
    """The docket's pages, with its corrections set -- or nothing at all.

    Args:
        docket: the deserialized docket -- the decided alterations for
            one editorial boundary.
        repo: the checkout the docket's pages are read from.
        into: where the revise lands. Must not exist yet: `pull` makes it, and
            an `into` that is already there raises `FileExistsError` and is left
            as it was. `into.parent` must be outside `repo`: the scratch
            directory the drafts are set in is made beside `into`, so an
            `into` nested inside the checkout puts that directory inside it
            too, and `undraftable` then refuses the whole run before any page
            is read. The `proof` command asks `undraftable(out, repo)` before
            it gets here; `pull` as a flow does not, so the caller owns this.

    Returns:
        `Pulled(into, set_by, [])` when every page in the docket passed, or
        `Pulled(into, {}, refusals)` with `into` removed again when any page
        refused.

    Nothing partial is left on any path. Once `into` is made, any exception
    -- in the drafting, the writing of the drafts into `into`, or the address
    gate -- removes it before propagating. A refusal or an exception also
    removes each directory above `into` that `pull` made, while it is empty.
    """
    repo = Path(repo)
    into = Path(into)
    imprints, problems = admit_pages(("docket", docket.schedules))
    if problems:
        return Pulled(
            into,
            {},
            [proof_setter.Refusal("read", "", p.text) for p in problems],
        )
    # The ancestors `mkdir` makes, nearest first, so a pull that does not
    # return a revise removes them with `into`.
    ancestors = list(itertools.takewhile(lambda p: not p.exists(), into.parents))
    # `into` is made outside the protection below, so an `into` that already
    # exists raises `FileExistsError` here and is never removed by it.
    into.mkdir(parents=True)
    scratch = None
    whole = False
    try:
        # The scratch directory is a sibling of `into`. `proof_setter.run`
        # refuses, through `undraftable`, a draft directory that overlaps the
        # repo it drafts from, so scratch must be disjoint from `repo`; a fresh,
        # randomly named directory is disjoint from `into`.
        scratch = Path(tempfile.mkdtemp(prefix="revise-scratch-", dir=into.parent))
        drafted, refusals = proof_setter.run(docket, repo, scratch)
        if refusals:
            # !! One rule, carried up a level. `proof_setter.run` already
            # discarded every draft it wrote on this refusal; what is left
            # here is the directory `pull` made before calling it, and a
            # refusal discards that directory exactly as it discards the
            # drafts.
            #
            # Nothing has been written into `into` on this path: the drafts go
            # in only once every page has passed.
            remove_tree(into)
            return Pulled(root=into, set_by={}, refusals=refusals)

        # Each draft is written at the path the docket names for its page, and
        # nothing else is written: the revise holds only the files the write
        # phase modifies.
        for made in drafted:
            target = into / made.path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(made.draft, target)

        pulled = Pulled(root=into, set_by=_set_by(docket), refusals=[])
        # The gate runs on every pull, before the success return: it is not an
        # opt-in. `AddressesMoved` propagates through the handler below, which
        # removes `into` first -- a revise whose addresses moved looks whole,
        # and a later stage reading it would measure every mark against the
        # wrong place.
        assert_addresses_held(
            repo, pulled, [s.path for s in docket.schedules], imprints=imprints
        )
        whole = True
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
        # needs.
        remove_tree(into, ignore_errors=True)
        raise
    finally:
        if scratch is not None:
            remove_tree(scratch, ignore_errors=True)
        # After the scratch directory, which sits in `into.parent`. `rmdir`
        # removes only an empty directory, so one another writer filled stays.
        if not whole:
            for ancestor in ancestors:
                with contextlib.suppress(OSError):
                    ancestor.rmdir()


def assert_addresses_held(
    original: Path,
    pulled: Pulled,
    pages: list[str],
    *,
    imprints: Mapping[str, Imprint] | None = None,
) -> None:
    """Raise `AddressesMoved` unless `pulled` addresses the same places `original` did.

    The comparison runs over `pages` alone -- the docket's pages, which are the
    only files the revise holds -- gathered from both roots at the same repo
    paths. Neither tree is walked, so a file the docket does not name is never
    read.

    Args:
        original: the checkout the revise was pulled from.
        pulled: the revise.
        pages: the repo path of each page the docket schedules, posix and
            relative to both roots.
        imprints: the docket's identity table, as `pull` admitted it. Omit
            for a fresh comparison that selects one context per file for both
            roots.

    Raises:
        AddressesMoved: naming the addresses that appeared in the revise and
            the ones that disappeared from the original -- or, before any
            comparison, a page the table lacks, or that will not read.
    """
    contexts: dict[str, ReadingContext] = {}
    if imprints is not None:
        contexts = {path: imprint.reading for path, imprint in imprints.items()}
    for rel in pages:
        if rel not in contexts:
            if imprints is not None:
                raise AddressesMoved(f"{rel}: missing saved reading context; regather")
            selected = context_for(Path(original) / rel)
            if isinstance(selected, ReadFailure):
                raise AddressesMoved(format_failure(selected, path=rel))
            contexts[rel] = selected
    before = known_addresses(_binder_over(Path(original), pages, contexts))
    after = known_addresses(_binder_over(Path(pulled.root), pages, contexts))
    appeared = sorted(after - before)
    disappeared = sorted(before - after)
    if appeared or disappeared:
        raise AddressesMoved(
            f"addresses moved between {original} and {pulled.root}: "
            f"{len(appeared)} appeared {appeared}, "
            f"{len(disappeared)} disappeared {disappeared}"
        )


def _binder_over(
    root: Path, pages: list[str], contexts: Mapping[str, ReadingContext]
) -> Binder:
    """The named pages under `root`, bound -- what the gate compares.

    `pages` are repo paths, posix and relative to `root`; nothing else under
    `root` is read.

    ! Addresses only. `annotate` and `code_names` resolve citations, a
    question this gate never asks, so building a page is as far as this goes.

    !! `absent=True`, so an empty place is carried too. `bind`'s default
    drops a place that holds no prose, and appended code with no comment or
    docstring is exactly that -- a new `undocumented` declaration would be
    invisible to this gate without it, which is the one case the gate exists
    to catch.
    """
    root = Path(root)
    held = []
    for rel in pages:
        page = page_of(root / rel, rel=rel, reading_context=contexts[rel])
        if isinstance(page, ReadFailure):
            raise AddressesMoved(format_failure(page, path=rel))
        held.append(page)
    return bind(held, read_from={"root": str(root)}, absent=True)


def _set_by(docket: Docket) -> dict[str, str]:
    """Every altered address, mapped to the role that set it.

    ! Reads an optional field. `role` is per page and `flows.transcribe` writes
    it; a page with no `role` yields `""` for each of its addresses, as
    `Pulled.set_by` states.

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
