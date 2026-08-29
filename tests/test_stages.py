"""The MARK sequence, checked against SKILL.md's own stage table.

! EXPECTATIONS HERE COME FROM `SKILL.md:544-583`, THE SHIPPED PROSE -- NEVER
FROM THE MODULE UNDER TEST. `decision-log.md Vocabulary: #23` forbids a test
whose expectation is derived from `stages.py` itself; the table below is the
same one two agent files (`SKILL.md`'s stage-4 table, `reviewer-brief.md`)
already state, transcribed by hand.

    4a   ownership-context, ALONE                    settles WHERE a
                                                       paragraph belongs
    4c   block-context, function-context,             measure a claim
         module-context, in ONE message               against the code
"""

from comment_review.desk.stages import (
    EDITORIAL,
    ENRICHING,
    STAGES,
    Stage,
    pulls_revise,
)


def test_ownership_context_runs_alone_and_first():
    assert STAGES[0].roles == ("ownership-context",)
    assert STAGES[0].kind == EDITORIAL


def test_the_other_three_share_one_stage():
    later = [s for s in STAGES if "block-context" in s.roles][0]
    assert set(later.roles) == {"block-context", "function-context", "module-context"}


def test_only_an_editorial_stage_pulls_a_revise():
    assert all(pulls_revise(s) == (s.kind == EDITORIAL) for s in STAGES)
    assert not pulls_revise(Stage("annotate", ENRICHING, ()))
