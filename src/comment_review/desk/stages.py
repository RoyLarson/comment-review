"""The MARK sequence, as data: what each stage hands back, and what follows it.

    Kind            what a stage can be, closed
    Kind.EDITORIAL  hands back marks -- verify -> reconcile -> revise step ->
                    pull a revise
    Kind.ENRICHING  hands back facts -- into the next binder. No docket, no
                    revise, and no producer yet
    Role            the four editorial roles, closed, independent of any
                    run's topology
    ROLES           the companion to `Role` -- membership is asked of THIS
    Stage           one row: a name, a kind, the roles it dispatches
    STAGES          the MARK sequence, `SKILL.md:544-583`
    pulls_revise    is this stage's output followed by a revise?

!! NO MODULE-LEVEL ALIAS OF A MEMBER, AND THERE WERE TWO UNTIL 2026-08-28:
`EDITORIAL = Kind.EDITORIAL` beside `ENRICHING = Kind.ENRICHING`. Roy:
*"aliasing like that is lazy and bad ... It allows for drift without the drift
being apparent because of shadowing. That is a horrible practice."*

! THE DRIFT IS THE ARGUMENT, NOT THE READABILITY. An alias is a SECOND name for
a value, bound once at import; nothing afterwards holds the two together. A
member renamed, a member's value changed, a second binding further down the
module, or an import that shadows the bare name -- each leaves the alias
pointing at what the member USED to be, and every call site reading the alias
goes with it. Nothing announces that: the name still resolves, the module still
imports, and `ty` still passes, because both sides are the same type.

! IT ALSO MADE A CAPITALISED NAME UNREADABLE AS A MEMBER, which is how this
surfaced -- a bare `ENRICHING` shown to Roy read as a module constant, and it
WAS one. That is the symptom; the drift is the defect.

Every site names `Kind.EDITORIAL` in full.

`decision-log.md Process: #34`, Roy, 2026-08-28: *"it bakes in the idea that
all editorial-role agents see everything at the same time and only rule on it
once."* The skill never worked that way -- `SKILL.md` stage 4 already runs
`ownership-context` alone at 4a, settling WHERE each paragraph belongs, and
the other three at 4c, in one message, measuring a claim against the code at
their own scope.

!! `Kind.ENRICHING` HAS NO PRODUCER, AND IS KEPT ANYWAY. It was dropped on
2026-08-28 and restored the same day. Roy: *"Put it back on the Kind because it
might have uses in `annotate.py` once `annotate.py` goes to `concordance.py`
which it is part of."*

! WHAT IT MEANS: a stage that hands back FACTS rather than marks -- resolutions
fed into the next stage's binder. It seeds no docket and pulls no revise, which
is what `pulls_revise` reads it for. `annotate` is stage 3 and resolves exactly
that kind of fact; it is not in this stage-4 list today, so nothing in `src/`
constructs an ENRICHING `Stage` yet.

! WHY THAT IS NOT SPECULATIVE MACHINERY: the candidate is NAMED and the move is
already filed -- `TODO/annotate-belongs-in-concordance.md`. ! WHAT IS NOT
CLAIMED is that anything exercises it: no `STAGES` row is ENRICHING, so
`pulls_revise`'s False branch is unreachable from this module's own data.

!! AND THE DROP IS RECORDED BECAUSE OF HOW IT HAPPENED. A session showed Roy a
bare `ENRICHING` -- which was then ALSO a module-level alias -- while asking
whether it earned its place; he read it as a constant, which it was, and said to
drop it. The session removed the MEMBER, a wider change than the answer covered.
`decision-log.md Process: #38` holds that, and the alias it came from is gone.

!! ADDING A STAGE IS A ROW, NOT A BRANCH. Nothing in this module or in
`pulls_revise` asks a stage's or a role's NAME; `pulls_revise` reads only
`stage.kind`. `CLAUDE.md` records what the other shape costs: `language.py`
decided a tier as `"tokenized" if lang.name == "python" else "lexical"`, and a
second tokenized language became three edits in two modules.

! `Kind`'s values are DERIVED from the member names via `_generate_next_value_`,
never hand-typed, following `T1.15` of `docs/plans/0.2.4-the-mark-and-the-
collator.md`. No site in this module asks membership of `Kind` itself --
`x in SomeEnum` raises `TypeError` on Python 3.11, measured at `lexer.py:87`
-- so there is no companion frozenset here; nothing in this file needs one.
"""

from enum import StrEnum, auto
from typing import NamedTuple


class Kind(StrEnum):
    """What a stage hands back. EDITORIAL -- marks -- is the only one.

    !! DECLARED POLYSEMY, and it went undeclared until 2026-08-28. This is the
    SECOND `Kind` in this package: `reading.series.Kind` has nine members
    (DOCSTRING, INTERVAL, MARGIN, MATTER, LEADING, ...) and answers *what kind
    of PLACE is this*, and it is imported by `binder/binder.py`, `binder/page.py`,
    `commands/census.py` and `reading/lexer.py`. This one answers
    *what does a STAGE hand back*. ! A reader meeting `stage.kind` after
    `paragraph.kind` has nothing telling them the word changed subject, and a
    module needing both must alias one -- `docs/vocabulary.md` is where this
    repo records a word carrying several meanings, and the undeclared one is
    the defect.
    """

    @staticmethod
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: list[str]
    ) -> str:
        return name.lower()

    EDITORIAL = auto()
    ENRICHING = auto()


class Role(StrEnum):
    """The four editorial roles -- a closed set, independent of any topology.

    !! A RUN'S TOPOLOGY MUST NOT DECIDE WHICH ROLE NAMES ARE VALID --
    `TODO/topology-is-a-source-edit.md`. `STAGES` below names which roles run
    together and in what order; `Role` names which roles EXIST at all, and
    that question does not move when the schedule does.

    ! No site in this module asks membership of `Role` itself -- `x in
    SomeEnum` raises `TypeError` on Python 3.11, measured at `lexer.py:87` --
    `ROLES = tuple(Role)` below is the companion asked instead.
    """

    @staticmethod
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: list[str]
    ) -> str:
        return name.lower().replace("_", "-")

    OWNERSHIP_CONTEXT = auto()
    BLOCK_CONTEXT = auto()
    FUNCTION_CONTEXT = auto()
    MODULE_CONTEXT = auto()


#: The companion to `Role` -- membership is asked of THIS, never of the
#: class. `SKILL.md`'s stage-4 table order: `ownership-context` alone at 4a,
#: then `block-context`, `function-context`, `module-context` at 4c.
ROLES = tuple(Role)


class Stage(NamedTuple):
    """One stage of MARK.

    Attributes:
        name: the stage's own label, drawn from `SKILL.md`'s stage-4 table
            (`4a`, `4c`).
        kind: a `Kind` -- what `pulls_revise` reads. Typed as `Kind` and not
            `str`: annotated `str`, the type gate admitted
            `Stage("x", "banana", ())`, measured 2026-08-28.
        roles: the role names this stage dispatches, in `SKILL.md`'s order.
    """

    name: str
    kind: Kind
    roles: tuple[str, ...]


#: The MARK sequence -- `SKILL.md:544-583`. 4a runs `ownership-context` alone
#: and first; 4c runs the other three in one message, blind to each other,
#: against 4a's resolved placement.
STAGES: tuple[Stage, ...] = (
    Stage("4a", Kind.EDITORIAL, ("ownership-context",)),
    Stage(
        "4c",
        Kind.EDITORIAL,
        ("block-context", "function-context", "module-context"),
    ),
)


def pulls_revise(stage: Stage) -> bool:
    """Does a revise get pulled after this stage runs?

    Only a `Kind.EDITORIAL` stage does -- `decision-log.md Process: #34`. A
    `Kind.ENRICHING` stage hands facts into the next binder; it seeds no docket
    and pulls nothing.

    ! TRUE FOR EVERY ROW IN `STAGES`, because both are EDITORIAL and nothing
    constructs an ENRICHING `Stage` yet. The False branch is reachable only
    from a `Stage` a caller builds itself.
    """
    return stage.kind == Kind.EDITORIAL
