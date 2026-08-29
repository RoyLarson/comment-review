"""A run's TOPOLOGY: which stages run, in what order, and what each dispatches.

`desk/stages.py`'s `STAGES` is a literal, so every schedule would otherwise be a
source edit. This module reads a run-scoped TOML file into `Stage` rows instead --
`docs/superpowers/specs/2026-08-29-the-master-proof-and-reconciliation-design.md`
section 2 is the format's own specification; every rule enforced here traces to a
sentence there.

    read    parse a topology file's text into `(stages, "")`, or refuse with
            `([], reason)` -- this repo's binder/docket shape

! **WHICH ROLES EXIST STAYS IN CODE; WHICH ROLE RUNS WHEN MOVES HERE.** `Role`
and `ROLES` are `desk/stages.py`'s closed set -- a dispatch's `role` key is
validated against `ROLES`, never against `Role` itself, because `x in
SomeEnum` raises `TypeError` on Python 3.11, measured at `lexer.py:87`.

! **`Stage` AND `Dispatch` ARE IMPORTED, NOT DEFINED HERE.** The design section
this module implements specifies a `Stage` NamedTuple of its own; `Stage`
already exists in `desk/stages.py`; this module evolves that one in place
instead of declaring a second same-named type in one package.

! **`reads` AND `carries` ARE CAPTURED, NOT YET CROSS-CHECKED.** This module
parses both keys onto the `Stage` it returns -- `reads` defaults to
`"original"`, `carries` to `()` -- but does not yet enforce section 2's
"barrier" (`reads` may only name an earlier, editorial stage's pulled
revise) or refuse a non-empty `carries` (format only, not built). Those
refusals are `TODO/topology-is-a-source-edit.md` T2 and T5, a later change
to this same function.

! **FAN-OUT'S FILE-PARTITION GUARDS ARE NOT THIS MODULE'S.** Section 2
states two guards over how a dispatch's `paths` glob against a binder's
actual pages (no page in two shards of one role's dispatches; every page in
exactly one shard of each role). Those need a binder; `read` takes only
`text` and has none to check against -- a `Dispatch` with no `paths` records
`()`, meaning every page, and leaves the matching to whatever consumes it.
"""

import tomllib

from comment_review.desk.stages import ROLES, Dispatch, Kind, Role, Stage

_KINDS = {"editorial": Kind.EDITORIAL, "enriching": Kind.ENRICHING}


def read(text: str) -> tuple[list[Stage], str]:
    """Parse a run's topology file.

    Returns `(stages, "")` when every stage and every dispatch is well formed;
    `([], reason)` on the first refusal, naming the offending key and the
    stage it was found in.
    """
    try:
        doc = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        return [], f"topology: not valid TOML -- {exc}"

    raw_stages = doc.get("stage")
    if not isinstance(raw_stages, list) or not raw_stages:
        return [], "topology: key 'stage' is missing or empty"

    stages: list[Stage] = []
    for raw in raw_stages:
        if not isinstance(raw, dict):
            return [], "topology: a 'stage' entry is not a table"

        name = raw.get("name")
        if not isinstance(name, str) or not name:
            return [], "topology: a stage is missing key 'name'"

        kind_str = raw.get("kind")
        if kind_str not in _KINDS:
            return [], (
                f"stage {name!r}: key 'kind' is {kind_str!r}, "
                "not 'editorial' or 'enriching'"
            )
        kind = _KINDS[kind_str]

        reads = raw.get("reads", "original")
        if not isinstance(reads, str):
            return [], f"stage {name!r}: key 'reads' must be a string"

        raw_carries = raw.get("carries", [])
        if not isinstance(raw_carries, list) or not all(
            isinstance(c, str) for c in raw_carries
        ):
            return [], f"stage {name!r}: key 'carries' must be a list of strings"

        raw_dispatches = raw.get("dispatch")
        if not isinstance(raw_dispatches, list) or not raw_dispatches:
            return [], f"stage {name!r}: key 'dispatch' is missing or empty"

        dispatches: list[Dispatch] = []
        roles: list[str] = []
        for raw_dispatch in raw_dispatches:
            if not isinstance(raw_dispatch, dict):
                return [], f"stage {name!r}: a 'dispatch' entry is not a table"

            role_str = raw_dispatch.get("role")
            if role_str not in ROLES:
                return [], (
                    f"stage {name!r}: key 'role' is {role_str!r}, "
                    "not a known role"
                )

            paths = raw_dispatch.get("paths", [])
            if not isinstance(paths, list) or not all(
                isinstance(p, str) for p in paths
            ):
                return [], (
                    f"stage {name!r}: key 'paths' for role {role_str!r} "
                    "must be a list of strings"
                )

            dispatches.append(Dispatch(Role(role_str), tuple(paths)))
            if role_str not in roles:
                roles.append(role_str)

        stages.append(
            Stage(
                name=name,
                kind=kind,
                roles=tuple(roles),
                reads=reads,
                carries=tuple(raw_carries),
                dispatches=tuple(dispatches),
            )
        )

    return stages, ""
