"""The MARK sequence, as data: what each stage hands back, and what follows it.

    Kind          the two things a stage can be, closed
    EDITORIAL     hands back marks -- verify -> reconcile -> revise step ->
                  pull a revise
    ENRICHING     hands back facts -- into the next binder. No docket, no
                  revise
    Stage         one row: a name, a kind, the roles it dispatches
    STAGES        the MARK sequence, `SKILL.md:544-583`
    pulls_revise  is this stage's output followed by a revise?

`decision-log.md Process: #34`, Roy, 2026-08-28: *"it bakes in the idea that
all editorial-role agents see everything at the same time and only rule on it
once."* The skill never worked that way -- `SKILL.md` stage 4 already runs
`ownership-context` alone at 4a, settling WHERE each paragraph belongs, and
the other three at 4c, in one message, measuring a claim against the code at
their own scope. `annotate.py` is already an ENRICHING stage in everything
but name, which is why a second kind is a row in this list rather than a new
mechanism -- `TODO/the-flow-assumes-every-role-reads-at-once.md` T1.

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
    """What a stage hands back: EDITORIAL marks, or ENRICHING facts."""

    @staticmethod
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: list[str]
    ) -> str:
        return name.lower()

    EDITORIAL = auto()
    ENRICHING = auto()


EDITORIAL = Kind.EDITORIAL
ENRICHING = Kind.ENRICHING


class Stage(NamedTuple):
    """One stage of MARK.

    Attributes:
        name: the stage's own label, drawn from `SKILL.md`'s stage-4 table
            (`4a`, `4c`).
        kind: EDITORIAL or ENRICHING -- what `pulls_revise` reads. Typed as
            `Kind`, not `str`: annotated `str`, the gate admitted
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
    Stage("4a", EDITORIAL, ("ownership-context",)),
    Stage("4c", EDITORIAL, ("block-context", "function-context", "module-context")),
)


def pulls_revise(stage: Stage) -> bool:
    """Does a revise get pulled after this stage runs?

    Only an EDITORIAL stage does -- `decision-log.md Process: #34`. An
    ENRICHING stage hands facts into the next binder; it seeds no docket and
    pulls nothing.
    """
    return stage.kind == EDITORIAL
