"""Split a binder by dispatch, so a stage's shards are structural, not counted.

    partition(binder, stage)  each dispatch with its files, after the two guards
    dealt(binder, stage)      each dispatch's received binder with its seeded
                              edit_copy, in dispatch order
    write_dealt(binder, stage, out_dir)
                              those copies and binders, written to disk
    received_binder_of(copy)  where `write_dealt` writes a copy's binder
    Shard                     a dispatch, with the pages and freeform paths it
                              matched
    OverlappingShards         two dispatches of one role both claim a file
    UncoveredPage             a role's dispatches, together, miss a file

!! Why fan-out exists at all, and it is measured: a role handed too many rows
inspects them less carefully, and the effect is largest for the role whose work
is tightest.

! The unit is the file, not the row: a role's context stays consistent within a
file, and no file is split between dispatches. Partitioning by file is what
makes non-overlap structural -- an address is `path@cue`, so one role marks a
place at most once, and nothing downstream needs extra identity to tell shards
apart.
"""

import json
from dataclasses import replace
from fnmatch import fnmatch
from pathlib import Path

from comment_review.binder.binder import Binder
from comment_review.binder.page import Page, RedactedPage
from comment_review.desk.stages import Dispatch, Stage
from comment_review.flows.distribute import admit_binder, assigned_binder, seed
from comment_review.machine.repo import write_raw


class OverlappingShards(Exception):
    """Two dispatches of the same role, in one stage, both claim a file."""


class UncoveredPage(Exception):
    """A role's dispatches, together, do not reach every file in the binder."""


def _matches(path: str, patterns: tuple[str, ...]) -> bool:
    """Whether this file falls under a dispatch carrying these patterns.

    Empty `patterns` means every file -- `desk/stages.py`'s own rule for a
    `Dispatch` with no `paths`.

    !! The matcher is `fnmatch.fnmatch`, stdlib, chosen for the constraint this
    package holds everywhere else -- no third-party dependency. `fnmatch`'s `*`
    is not path-aware: it matches any run of characters, including `/`, because
    `fnmatch` treats a path as one flat string rather than a sequence of
    segments. Measured: `fnmatch.fnmatch("src/reading/sub/other.py",
    "src/reading/*.py")` is `True` -- a single `*` already crosses a directory
    boundary. `**` therefore "works" only in the sense that it matches the same
    set `*` already does; there is no recursive-glob semantics to add, because
    `fnmatch` never withholds `/` from a plain `*`.
    """
    return not patterns or any(fnmatch(path, pattern) for pattern in patterns)


def dealt(binder: Binder, stage: Stage) -> list[tuple[Binder, dict]]:
    """Pair each dispatch's received binder with its seeded edit copy.

    The shard carries the binder's own `read_from` and `version`: it is the binder
    with fewer pages, built by `dataclasses.replace`, so neither is restated.
    `distribute.admit_binder` runs first and raises `distribute.IncompatibleBinder`
    for a binder whose saved reading metadata is incompatible.
    """
    admit_binder(binder)
    out = []
    for dispatch, matched, freeform in partition(binder, stage):
        shard = replace(binder, pages=tuple(matched), freeform=tuple(freeform))
        received = assigned_binder(shard, stage)
        out.append((received, seed(received, dispatch.role, stage)))
    return out


def write_dealt(binder: Binder, stage: Stage, out_dir: Path) -> list[tuple[Path, str]]:
    """Write `dealt`'s copies into `out_dir`, each received binder under `binders/`.

    A copy is `<stage>_<role>_<n>.json`, `n` counting that role's dispatches,
    and its binder has the same name. `dealt` refuses the whole stage before
    anything is written.

    Returns:
        Each copy's path with the line that reports it, in dispatch order.
    """
    packets = dealt(binder, stage)
    seen: dict[str, int] = {}
    written = []
    for dispatch, (received, copy) in zip(stage.dispatches, packets, strict=True):
        n = seen[dispatch.role] = seen.get(dispatch.role, 0) + 1
        where = out_dir / f"{stage.name}_{dispatch.role}_{n}.json"
        write_raw(where, json.dumps(copy, indent=2))
        binder_path = received_binder_of(where)
        write_raw(binder_path, json.dumps(received.serialize(), indent=2))
        places = sum(len(sheet["marks"]) for sheet in copy["sheets"])
        written.append(
            (
                where,
                f"{where}: {places} places for {dispatch.role} to rule on; "
                f"{len(received.freeform)} freeform; binder {binder_path}",
            )
        )
    return written


def received_binder_of(copy: Path) -> Path:
    """The received binder `write_dealt` writes beside the copy at `copy`."""
    return copy.parent / "binders" / copy.name


#: A dispatch, the pages it matched and the freeform paths it matched.
Shard = tuple[Dispatch, list[Page | RedactedPage], list[str]]


def partition(binder: Binder, stage: Stage) -> list[Shard]:
    """Each dispatch with the files its globs select, after the two guards.

    A freeform path is dealt as a page is: the guards count both alike. A
    stage whose row sets a `cap` deals no freeform path: it compacts the
    places the reader addressed, and stage 5 holds a freeform comment to the
    cap itself.

    ! One computation, two readers. `dealt` seeds from this, and
    `flows.topology.fit` asks it whether a topology fits before any page is
    read -- so a topology `fit` passes is one `dealt` will not refuse.

    Raises:
        OverlappingShards: a file matches two dispatches of the same role.
        UncoveredPage: a file matches no dispatch of a role this stage
            dispatches at all.
    """
    freeform_dealt = () if stage.cap else binder.freeform
    all_paths = [*(page.path for page in binder.pages), *freeform_dealt]

    # ! MATCHED ONCE PER DISPATCH, kept alongside it, so the guard pass below
    # and the seeding pass after it read the same computation rather than
    # matching twice and risking the two disagree.
    shards = [
        (
            dispatch,
            [p for p in binder.pages if _matches(p.path, dispatch.paths)],
            [f for f in freeform_dealt if _matches(f, dispatch.paths)],
        )
        for dispatch in stage.dispatches
    ]

    by_role: dict = {}
    for dispatch, matched, freeform in shards:
        by_role.setdefault(dispatch.role, []).append(
            [*(page.path for page in matched), *freeform]
        )

    for role, groups in by_role.items():
        counts: dict[str, int] = {}
        for group in groups:
            for path in group:
                counts[path] = counts.get(path, 0) + 1
        overlapping = sorted(path for path, n in counts.items() if n > 1)
        if overlapping:
            raise OverlappingShards(
                f"{role}: reached by two dispatches -- {overlapping}"
            )
        missing = sorted(set(all_paths) - set(counts))
        if missing:
            raise UncoveredPage(f"{role}: no dispatch covers -- {missing}")

    return shards
