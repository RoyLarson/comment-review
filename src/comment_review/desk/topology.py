"""A run's TOPOLOGY: which stages run, in what order, and what each dispatches.

`desk/stages.py` no longer holds a schedule literal -- a run's schedule would
otherwise be a source edit. This module reads a run-scoped TOML file into
`Stage` rows instead --
`docs/superpowers/specs/2026-08-29-the-master-proof-and-reconciliation-design.md`
section 2 is the format's own specification; every rule enforced here traces to a
sentence there.

    read    parse a topology file's text into `(stages, "")`, or refuse with
            `([], reason)` -- this repo's binder/docket shape
    seeded_from_problem
            whether a stage may be seeded from the binder in hand, given the
            revise root the caller named -- the reader for `reads`

! **WHICH ROLES EXIST STAYS IN CODE; WHICH ROLE RUNS WHEN MOVES HERE.** `Role`
and `ROLES` are `desk/stages.py`'s closed set -- a dispatch's `role` key is
validated against `ROLES`, never against `Role` itself, because `x in
SomeEnum` raises `TypeError` on Python 3.11, measured at `lexer.py:87`.

! **`Stage` AND `Dispatch` ARE IMPORTED, NOT DEFINED HERE.** The design section
this module implements specifies a `Stage` NamedTuple of its own; `Stage`
already exists in `desk/stages.py`; this module evolves that one in place
instead of declaring a second same-named type in one package.

! **THREE KEYS SAY WHAT A STAGE DEALS AND WHAT ITS ROLES MAY FILE** --
`cap`, `series` and `admits`, `decision-log.md Process: #193`. Each is
optional and each is checked against the set that defines it rather than
against a list kept here: a series letter against `reading.series`, an
instruction name against the marks table. Absent on every ordinary stage,
which is what makes one behave as it did before the ruling --
`desk.stages.deals` reads the first two and `flows.distribute.seed` narrows
the copy by them.

! **THEY ARE INDEPENDENT OF `reads`, AND NOTHING HERE PAIRS THEM.** A
compacting stage is one use of the three -- the use `#193` ruled, over a
revise -- and a stage reading `"original"` may narrow what it deals in the
same way. Which tree a stage is seeded from and which of that tree's places
it is dealt are two questions, so a row answering one is never required to
answer the other.

! **`reads` ENFORCES SECTION 2'S "BARRIER".** A `"revise:<name>"` value may
only name a stage that appears EARLIER in the file's own `[[stage]]` order
and whose `kind` is `"editorial"` -- a forward reference is refused, and an
`"enriching"` stage named in `reads` is refused BY NAME rather than quietly
resolved to the previous editorial one (`Process: #34`). `carries` parses as
`()`; a non-empty value is refused as format-only, not built
(`Process: #50`). `TODO/topology-is-a-source-edit.md` T2 and T5.

! **FAN-OUT'S FILE-PARTITION GUARDS ARE NOT THIS MODULE'S.** Section 2
states two guards over how a dispatch's `paths` glob against a binder's
actual pages (no page in two shards of one role's dispatches; every page in
exactly one shard of each role). Those need a binder; `read` takes only
`text` and has none to check against -- a `Dispatch` with no `paths` records
`()`, meaning every page, and leaves the matching to whatever consumes it.
"""

import tomllib

from comment_review.desk.marks.table import INSTRUCTIONS
from comment_review.desk.stages import ROLES, Dispatch, Kind, Role, Stage
from comment_review.reading.series import ADDRESSED

_KINDS = {"editorial": Kind.EDITORIAL, "enriching": Kind.ENRICHING}

#: What a `reads` value starts with when it names an earlier stage's revise.
#: Spelled once: `read` refuses a bad one and `seeded_from_problem` decides
#: what a stage is seeded from, and the two cannot disagree about the prefix.
REVISE = "revise:"


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
    kind_by_name: dict[str, Kind] = {}
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

        if reads.startswith(REVISE):
            read_name = reads[len(REVISE) :]
            read_kind = kind_by_name.get(read_name)
            if read_kind is None:
                return [], (
                    f"stage {name!r}: key 'reads' is {reads!r}, naming a "
                    "stage not run earlier in the file -- a stage may only "
                    "read a revise pulled by an earlier stage"
                )
            if read_kind == Kind.ENRICHING:
                return [], (
                    f"stage {name!r}: key 'reads' is {reads!r}, but stage "
                    f"{read_name!r} is 'enriching' and pulls no revise"
                )

        raw_carries = raw.get("carries", [])
        if not isinstance(raw_carries, list) or not all(
            isinstance(c, str) for c in raw_carries
        ):
            return [], f"stage {name!r}: key 'carries' must be a list of strings"
        if raw_carries:
            return [], (
                f"stage {name!r}: key 'carries' is not empty -- 'carries' "
                "is format only, not built (Process: #50)"
            )

        cap, why_cap = _cap(name, raw)
        if why_cap:
            return [], why_cap

        series, why_series = _listed(
            name, raw, "series", ADDRESSED, "a series a place is addressed in"
        )
        if why_series:
            return [], why_series

        admits, why_admits = _listed(
            name, raw, "admits", tuple(INSTRUCTIONS), "one of the instructions"
        )
        if why_admits:
            return [], why_admits

        raw_dispatches = raw.get("dispatch")
        if not isinstance(raw_dispatches, list) or not raw_dispatches:
            return [], f"stage {name!r}: key 'dispatch' is missing or empty"

        dispatches: list[Dispatch] = []
        for raw_dispatch in raw_dispatches:
            if not isinstance(raw_dispatch, dict):
                return [], f"stage {name!r}: a 'dispatch' entry is not a table"

            role_str = raw_dispatch.get("role")
            if role_str not in ROLES:
                return [], (
                    f"stage {name!r}: key 'role' is {role_str!r}, not a known role"
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

        stages.append(
            Stage(
                name=name,
                kind=kind,
                reads=reads,
                carries=tuple(raw_carries),
                cap=cap,
                series=series,
                admits=admits,
                dispatches=tuple(dispatches),
            )
        )
        kind_by_name[name] = kind

    return stages, ""


def _cap(name: str, raw: dict) -> tuple[int, str]:
    """A stage's `cap`, in lines, or the one reason it is not a cap.

    `decision-log.md Process: #193`. Absent is 0, which asks nothing about a
    place's length. ! A TOML BOOLEAN IS AN `int` IN PYTHON, so `cap = true`
    would otherwise read as a cap of one line.
    """
    given = raw.get("cap", 0)
    if isinstance(given, bool) or not isinstance(given, int) or given < 0:
        return 0, f"stage {name!r}: key 'cap' must be a whole number of lines"
    return given, ""


def _listed(
    name: str, raw: dict, key: str, known: tuple[str, ...], what: str
) -> tuple[tuple[str, ...], str]:
    """A stage's `series` or `admits`, checked against the set that defines it.

    Neither key names a rule of this module's own: the series letters are
    `reading.series`'s, and the instruction names are the marks table's, so a
    row naming something outside either is refused by the value it typed
    rather than by a list kept here (`decision-log.md Process: #193`).

    Returns:
        `(the values, "")`, or `((), the reason)`. An absent key is `()`,
        which asks nothing.
    """
    given = raw.get(key, [])
    if not isinstance(given, list) or not all(isinstance(one, str) for one in given):
        return (), f"stage {name!r}: key {key!r} must be a list of strings"
    outside = [one for one in given if one not in known]
    if outside:
        return (), (
            f"stage {name!r}: key {key!r} names {outside[0]!r}, which is not"
            f" {what} -- it holds: {', '.join(known)}"
        )
    return tuple(given), ""


def seeded_from_problem(stage: Stage, revise: str, read_from: dict) -> str:
    """Why this stage may not be seeded from this binder, or `""`.

    `reads` says which tree a stage's copies are cut from, and this is what
    reads it: a stage reading `"original"` is seeded from the gathered binder
    and names no revise root, and a stage reading `"revise:<name>"` is seeded
    from the revise that stage pulled -- so the binder in hand must be the one
    gathered from it.

    A binder says which tree it was gathered from and which revise that tree
    is, so both halves are asked: a binder from another tree answers to
    another address space, and one stamped revise 0 says it read the original,
    whatever directory it was pointed at.

    Args:
        stage: the stage being seeded.
        revise: the revise root the caller named, or `""` where it named
            none. Compared with `read_from["root"]` as given, so a caller
            spelling either of them differently resolves both first.
        read_from: the binder's own `{"root": str, "revise": int}`.

    Returns:
        The one reason, naming the stage, or `""` where the stage may be
        seeded from this binder.
    """
    if not stage.reads.startswith(REVISE):
        if revise:
            return (
                f"stage {stage.name!r} reads {stage.reads!r}, so it is seeded from"
                " the binder it was gathered into and names no revise root"
            )
        return ""
    earlier = stage.reads[len(REVISE) :]
    if not revise:
        return (
            f"stage {stage.name!r} reads the revise stage {earlier!r} pulled,"
            " and no revise root was named"
        )
    root = str(read_from.get("root", ""))
    if root != revise:
        return (
            f"stage {stage.name!r} reads {revise!r} and the binder was gathered"
            f" from {root!r} -- a stage is seeded from the revise it reads"
        )
    if not read_from.get("revise"):
        return (
            f"stage {stage.name!r} reads a revise, and the binder says it"
            f" gathered revise 0 of {root!r}, which is the original"
        )
    return ""
