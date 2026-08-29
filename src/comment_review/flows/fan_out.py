"""Split a binder by dispatch, so a stage's shards are structural, not counted.

    fan(binder, stage)      one seeded edit_copy per dispatch, in dispatch order
    OverlappingShards       two dispatches of ONE role both claim a page
    UncoveredPage           a role's dispatches, together, miss a page

!! WHY FAN-OUT EXISTS AT ALL, AND IT IS MEASURED: a role handed too many rows
inspects them less carefully, and the effect is largest for the role whose work
is tightest. `decision-log.md Process: #47` holds Roy's own words for it.

! THE RULING IS CITED HERE RATHER THAN QUOTED, and that is deliberate. His
sentence uses a word `docs/vocabulary.md` has since retired, so a shipped file
cannot carry it verbatim -- `scripts/check_vocabulary.py` refuses the retired
word anywhere under `plugins/`. ! AND A BRACKETED SUBSTITUTION WAS TRIED FIRST:
it is honest, but it puts a doctored quotation in the shipped tree while the
verbatim one already lives in the log. **The record keeps his words; this file
keeps the reason.** `CLAUDE.md`: when a ruling is quoted, quote all of it --
which here means quoting it where all of it is allowed.

! THE UNIT IS THE FILE, not the row: *"By file because context should be more
consistent. File thrashing would be bad."* Partitioning by FILE is what makes
non-overlap structural -- an address is `path@cue`, so one role marks a place
at most once, and nothing downstream needs extra identity to tell shards apart.

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
        KeyError: the binder carries no `read_from` -- `flows.marks.seed`'s
            own refusal, reached because the shard below is built with
            `binder["read_from"]` and not with a default.

    !! THE SHARD TAKES `read_from` BY SUBSCRIPT, AND TOOK IT WITH A `{}`
    DEFAULT UNTIL 2026-08-29. `seed` refuses a binder that cannot say which
    tree it read -- the refusal `bind` added on 2026-08-28 and `seed` carried
    one step further the same day -- and this function rebuilt the argument
    with the fallback that refusal exists to remove, so `seed`'s `KeyError`
    could never fire through fan-out. MEASURED: `fan` over a binder with no
    `read_from` returned shards carrying `read_from={}` and raised nothing,
    while `seed(binder, role)` on the same binder raised `KeyError`.

    ! AND EVERY SHARD AGREED ON `{}`, so `desk.proof.gather`'s `MismatchedRoot`
    could not fire either -- the ambiguity surfaced four steps later at
    `mark --check`, blamed on the role, after four agents had read and filled
    the shards.
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
            {"read_from": binder["read_from"], "pages": matched},
            dispatch.role,
        )
        for dispatch, matched in shards
    ]
