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

from comment_review.flows import proof_setter
from comment_review.reading.addresser import address_for


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
            on, not decoration. ! THE DOCKET CARRIES NO `role` FIELD YET --
            `docket.py`'s schema has three keys per page (`path`, `sha`,
            `alterations`) and none per role. A page dict MAY carry one
            anyway (`read` and `schedules_of` ignore unknown keys), and this
            reads it when present; a docket with none maps every one of its
            addresses to `""`. The producer that tags a docket by role is not
            built yet -- see the TODO above, T1 and T2.
        refusals: every `proof_setter.Refusal`, or `[]` on success. Non-empty
            means `root` was discarded and does not exist.
    """

    root: Path
    revise: int
    set_by: dict[str, str]
    refusals: list[proof_setter.Refusal]


def pull(docket: dict, repo: Path, into: Path, revise: int) -> Pulled:
    """The whole tree, with `docket`'s corrections set -- or nothing at all.

    Args:
        docket: as `docket.read` returned it -- the settled alterations for
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
    # repo it drafts from, so scratch must be disjoint from `repo` too -- a
    # fresh, randomly-named directory beside `into` is disjoint from both by
    # construction, and `into.parent` is guaranteed to exist once `into`
    # itself does.
    scratch = Path(tempfile.mkdtemp(prefix="revise-scratch-", dir=into.parent))
    try:
        drafted, refusals = proof_setter.run(docket, repo, scratch)
        if refusals:
            # !! ONE RULING, CARRIED UP A LEVEL. `proof_setter.run` already
            # discarded every draft IT wrote on this refusal; what is left
            # here is the copy `pull` made before calling it, and
            # `Process: #20` applies to that copy exactly as it applies to
            # the drafts.
            shutil.rmtree(into)
            return Pulled(root=into, revise=revise, set_by={}, refusals=refusals)

        for made in drafted:
            target = into / made.path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(made.draft, target)

        return Pulled(
            root=into, revise=revise, set_by=_set_by(docket), refusals=[]
        )
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def _set_by(docket: dict) -> dict[str, str]:
    """Every altered address, mapped to the role that set it.

    ! READS AN OPTIONAL, NOT-YET-PRODUCED FIELD. See `Pulled.set_by`'s own
    docstring for why `""` is what a docket with no `role` field yields.

    Args:
        docket: as `docket.read` returned it.

    Returns:
        address -> role, one entry per alteration across every page.
    """
    out: dict[str, str] = {}
    for page in docket.get("pages", []):
        path = str(page.get("path", ""))
        role = str(page.get("role", ""))
        for alteration in page.get("alterations", []):
            cue = str(alteration.get("cue", ""))
            out[address_for(path, cue)] = role
    return out
