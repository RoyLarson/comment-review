"""TOPOLOGY -- does a topology fit a binder, and write one that does.

    fit(stages, binder)          every way the topology does not fit, or []

! WHY A FLOW AND NOT `desk/topology.py`: `read` takes text and has no binder,
so it cannot ask whether a dispatch reaches a page -- `Process: #55` puts that
question in a command with a repo, and a command exposes a flow (`#12`).

! THE GUARDS ARE `fan_out.partition`'s, NOT A SECOND COPY. `fit` runs the same
partition `fan` will run and turns its two refusals into misfits, so a topology
`fit` passes is one `fan` will not refuse. A glob that matches no page is NOT
a third kind -- `Process: #100`: it either leaves a page uncovered, which the
guard names, or costs nothing, and the agent that wrote it reads the result.
What `fit` adds is the stage's globs on an `uncovered` detail, so that agent
sees which glob missed.
"""

from typing import NamedTuple

from comment_review.binder.binder import Binder
from comment_review.desk.stages import Stage
from comment_review.flows.fan_out import OverlappingShards, UncoveredPage, partition


class Misfit(NamedTuple):
    """One way a topology does not fit a binder.

    Attributes:
        kind: `overlap` (a page in two shards of one role), `uncovered` (a
            page no shard of a role reaches), `reads` (the file's own order
            refuses it -- reported by the command from `read`'s reason, never
            produced here).
        stage: the stage's name.
        detail: what to look at -- the role, the pages, and the stage's globs.
    """

    kind: str
    stage: str
    detail: str


def fit(stages: list[Stage], binder: Binder) -> list[Misfit]:
    """Every misfit between these stages and this binder; `[]` when it fits.

    ! ONE MISFIT PER STAGE AT MOST: `partition` raises on the first role that
    fails, and the caller fixes the topology and runs it again.
    """
    out: list[Misfit] = []
    for stage in stages:
        globs = ", ".join(repr(p) for d in stage.dispatches for p in d.paths) or "none"
        try:
            partition(binder, stage)
        except OverlappingShards as exc:
            out.append(Misfit("overlap", stage.name, str(exc)))
        except UncoveredPage as exc:
            out.append(
                Misfit("uncovered", stage.name, f"{exc} -- the stage's globs: {globs}")
            )
    return out
