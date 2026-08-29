"""Split a binder by dispatch, so a stage's shards are structural, not counted.

    fan(binder, stage)      one seeded edit_copy per dispatch, in dispatch order
    OverlappingShards       two dispatches of ONE role both claim a page
    UncoveredPage           a role's dispatches, together, miss a page

!! WHY FAN-OUT EXISTS AT ALL. Roy, 2026-08-28: *"It makes them more efficient
and we have measured that it makes them more diligent in actually inspecting
the [paragraphs], where they get overloaded on too many records."* (quoted
word retired -- `docs/vocabulary.md`: `block` -> paragraph). And on the unit:
*"By file because context should be more consistent. File thrashing would be
bad."* Partitioning by FILE is what makes non-overlap structural -- an address
is `path@cue`, so one role marks a place at most once, and nothing downstream
needs extra identity to tell shards apart.

! A `Dispatch` WITH NO `paths` GETS EVERY PAGE -- `desk/stages.py`'s own
docstring for the field. Two dispatches for DIFFERENT roles covering the same
page is normal and raises nothing: that is four roles reading one binder.

!! THE MATCHER IS `fnmatch.fnmatch`, stdlib, chosen for the constraint this
package holds everywhere else -- no third-party dependency. `fnmatch`'s `*`
is NOT path-aware: it matches any run of characters, including `/`, because
`fnmatch` treats a path as one flat string rather than a sequence of
segments. MEASURED: `fnmatch.fnmatch("src/reading/sub/lexer.py",
"src/reading/*.py")` is `True` -- a single `*` already crosses a directory
boundary. `**` therefore "works" only in the sense that it matches the same
set `*` already does; there is no recursive-glob semantics to add, because
`fnmatch` never withheld `/` from a plain `*` to begin with.
"""

from fnmatch import fnmatch

from comment_review.desk.stages import Stage
from comment_review.flows.marks import seed


class OverlappingShards(Exception):
    """Two dispatches of the same role, in one stage, both claim a page."""


class UncoveredPage(Exception):
    """A role's dispatches, together, do not reach every page in the binder."""


def _matches(path: str, patterns: tuple[str, ...]) -> bool:
    """Does this page fall under a dispatch carrying these patterns?

    Empty `patterns` means every page -- `desk/stages.py`'s own rule for a
    `Dispatch` with no `paths`.
    """
    return not patterns or any(fnmatch(path, pattern) for pattern in patterns)


def fan(binder: dict, stage: Stage) -> list[dict]:
    """One `edit_copy` per dispatch in `stage`, each seeded from its own pages.

    Args:
        binder: as `binder.read` (or `binder.bind`) returns it.
        stage: the `Stage` whose `dispatches` name the roles and the glob
            patterns selecting each one's pages.

    Returns:
        A list of edit_copies (`flows.marks.seed`'s shape), one per dispatch,
        in `stage.dispatches`' own order.

    Raises:
        OverlappingShards: a page in `binder` matches two dispatches of the
            SAME role -- the address `path@cue` would then be marked twice.
        UncoveredPage: a page in `binder` matches NO dispatch of some role
            that this stage dispatches at all -- that role would never see it.
    """
    pages = binder.get("pages", [])
    all_paths = [str(page.get("path", "")) for page in pages]

    # ! MATCHED ONCE PER DISPATCH, kept alongside it, so the guard pass below
    # and the seeding pass after it read the same computation rather than
    # matching twice and risking the two disagree.
    shards = [
        (
            dispatch,
            [p for p in pages if _matches(str(p.get("path", "")), dispatch.paths)],
        )
        for dispatch in stage.dispatches
    ]

    by_role: dict = {}
    for dispatch, matched in shards:
        by_role.setdefault(dispatch.role, []).append(matched)

    for role, groups in by_role.items():
        counts: dict[str, int] = {}
        for group in groups:
            for page in group:
                path = str(page.get("path", ""))
                counts[path] = counts.get(path, 0) + 1
        overlapping = sorted(path for path, n in counts.items() if n > 1)
        if overlapping:
            raise OverlappingShards(
                f"{role}: reached by two dispatches -- {overlapping}"
            )
        missing = sorted(set(all_paths) - set(counts))
        if missing:
            raise UncoveredPage(f"{role}: no dispatch covers -- {missing}")

    return [
        seed(
            {"read_from": binder.get("read_from", {}), "pages": matched},
            dispatch.role,
        )
        for dispatch, matched in shards
    ]
