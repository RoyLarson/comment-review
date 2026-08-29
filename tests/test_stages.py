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

from comment_review.desk.stages import STAGES, Kind, Stage, pulls_revise


def test_ownership_context_runs_alone_and_first():
    assert STAGES[0].roles == ("ownership-context",)
    assert STAGES[0].kind == Kind.EDITORIAL


def test_the_other_three_share_one_stage():
    # ! THE ORDER AND THE NAME ARE ASSERTED, and only the SET was until
    # 2026-08-28. `Stage.roles` is documented as the roles "in `SKILL.md`'s
    # order" and `Stage.name` as drawn from that file's stage-4 table, so a
    # set comparison passed under any permutation and under any name at all,
    # leaving the table transcribed in this file's own docstring free to go
    # stale with the suite green.
    later = [s for s in STAGES if "block-context" in s.roles][0]
    assert later.name == "4c"
    assert later.roles == ("block-context", "function-context", "module-context")


def test_only_an_editorial_stage_pulls_a_revise():
    # !! THE EXPECTATION IS THE TRANSCRIBED TABLE, NOT THE MODULE'S OWN RULE.
    # This read `all(pulls_revise(s) == (s.kind == EDITORIAL) for s in STAGES)`
    # until 2026-08-28 -- a restatement of `pulls_revise`'s body over the same
    # objects, which is self-consistency and is what this file's docstring
    # forbids. Both rows being EDITORIAL, it also only ever evaluated the True
    # branch.
    assert [s.name for s in STAGES] == ["4a", "4c"]
    assert [s.name for s in STAGES if pulls_revise(s)] == ["4a", "4c"]
    # ! THE FALSE BRANCH NEEDS A `Stage` BUILT HERE, because no row in `STAGES`
    # is ENRICHING -- `annotate` is the named candidate and is stage 3, not in
    # this list. `stages.py` says so rather than implying the enum is exercised.
    assert not pulls_revise(Stage("annotate", Kind.ENRICHING, ()))
