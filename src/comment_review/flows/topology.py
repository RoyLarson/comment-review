"""TOPOLOGY -- does a topology fit a binder, and write one that does.

    fit(stages, binder)          every way the topology does not fit, or []
    compose(directives, binder)  a topology's TEXT that fits by construction

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

import json
from typing import NamedTuple

from comment_review.binder.binder import Binder
from comment_review.desk.stages import ROLES, Stage
from comment_review.flows.fan_out import OverlappingShards, UncoveredPage, partition

#: A stage's name and, in order, `(role, ways)` -- how many shards the role is
#: split into. `ways == 1` is one dispatch over every page.
Directive = tuple[str, list[tuple[str, int]]]


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


def _toml_string(s: str) -> str:
    # ! JSON's string escaping is a subset of TOML's basic-string escaping for
    # every character a path may carry, and the stdlib has a JSON encoder and
    # no TOML one. A test round-trips a quote through `read`.
    return json.dumps(s)


def compose(directives: list[Directive], binder: Binder) -> str:
    """A topology, as text, that `read` accepts and `fit` passes for `binder`.

    Every stage is `editorial`; the first reads `original` and each later one
    reads the revise of the stage before it. A role split `ways` > 1 gets
    `ways` dispatches, each carrying explicit page paths -- the binder's pages
    sorted and dealt round-robin -- so it fits by construction rather than by
    a glob that happens to match.

    Raises:
        ValueError: a role outside the closed set, or a split the binder's
            page count cannot honour.
    """
    pages = sorted(page.path for page in binder.pages)
    lines: list[str] = []
    previous: str | None = None
    for name, roles in directives:
        lines += ["[[stage]]", f"name = {_toml_string(name)}", 'kind = "editorial"']
        lines.append(
            f'reads = "revise:{previous}"' if previous else 'reads = "original"'
        )
        for role, ways in roles:
            if role not in ROLES:
                raise ValueError(f"stage {name!r}: {role!r} is not a known role")
            if ways < 1 or ways > len(pages):
                where = f"stage {name!r}: {role!r}"
                raise ValueError(f"{where} split {ways} ways over {len(pages)} pages")
            for i in range(ways):
                lines += ["  [[stage.dispatch]]", f"  role = {_toml_string(role)}"]
                if ways > 1:
                    shard = ", ".join(_toml_string(p) for p in pages[i::ways])
                    lines.append(f"  paths = [{shard}]")
        lines.append("")
        previous = name
    return "\n".join(lines)
