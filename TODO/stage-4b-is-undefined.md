# Stage 4b is referenced everywhere and defined nowhere

```
Status:   decision-needed
Progress: 0 of 5 tasks done
Owner:    agents
Requires-Roy: true
Raised:   2026-08-20 (the /code-review high of 2026-08-20)
Re-measured: 2026-08-23 -- `4b` appears NOWHERE under `plugins/`; in `docs/plans/` it
          appears twice, one of them a link to this file. `SKILL.md` now defines 4a at
          :550 and 4c at :551. One of the four boxes is fixed: `reviewer-brief.md` no
          longer says remits overlap by design -- zero matches for `overlap`.
Split:    2026-08-23 -- the box about the two configuration sentences held two separate
          artifacts: a run's own artifacts naming their configuration, and `SKILL.md:3`
          framing the parallel form as the BASELINE. They are now two boxes.
```

## Objective

**Stage 4 is split into 4a and 4c, and 4b is defined nowhere.** MEASURED 2026-08-23:

- `SKILL.md:550-551` names `4a` (`ownership-context`, ALONE) and `4c` (the other three, in one
  message). `:30` and `:161-163` say the same. **`4b` has zero occurrences under `plugins/`.**
  It survives in `docs/plans/0.2.4-what-a-reviewer-is-handed.md:471` and in a link to this file.
- ! The letter is not free for something else to mean: `SKILL.md` now defines **5b** (`:905`)
  and **6b** (`:972`) as RE-REVIEW steps, so a reader meets `Nb` elsewhere as a real stage.

!! **AND NOTHING PRODUCES A RESOLVED PLACEMENT.** `SKILL.md:663` seeds all four roles from the
same `census.json` BEFORE dispatch, and `:608` hands all four the same stage-2 `dispatch.txt`.
So the serialisation only DELAYS the three: `block-context` still verifies a misfiled note
against the passage it was misfiled into, which is the precise failure `SKILL.md:555-558` says
the ordering prevents. **The boxes below cannot be checked until the stage exists or the claim
goes.** ! Nothing else in this file can be closed before T1: T2 is whichever answer T1 gives.

! **One half of the advertising is already corrected.** `reviewer-brief.md` no longer tells all
four that *"remits overlap by design ... two roles can reach different placement decisions"* --
zero matches for `overlap` in that file, 2026-08-23. What is left is `SKILL.md:3`, whose
description still advertises *"parallel read-only subagents"* while `:30` says stage 4 is
`4 reviewers, SERIAL`.

!! **THOSE TWO SENTENCES ARE NOT A CONTRADICTION TO RESOLVE BY DELETION.** Roy, 2026-08-23:
*"That was the original setup and I want to be able to figure out how well that setup does
compared to any other expansion of the process because the expansion has to pay for itself in
tokens."* The parallel form is the BASELINE, and correcting `:3` to match `:30` destroys the only
written record of what the comparison is against. So the work is to say WHICH CONFIGURATION a run
used (T3) and to frame `:3` as a configuration rather than as current behaviour (T4) -- not to
make the two sentences agree.

! **A third drift sits in the same stage's gate.** `run_context.py:62` holds four
`PATH_SECTIONS` -- `REPO ROOT`, `CENSUS`, `LOOKUP CENSUS`, `REVIEWER FILES` -- so `--check`
refuses a packet without `LOOKUP CENSUS`. `SKILL.md:624` still says it refuses *"the three
answers a machine can settle"* and never mentions the section at all. A run following `SKILL.md`
fails its own stage-4 gate.

## Tasks

- [?] T1 -- * RULING WANTED: what 4b IS -- a real step between 4a and 4c, or a wrong prose
      split. Verify: `SKILL.md` defines 4b, or the split reads 4a/4b and `4b` is nowhere.
- [ ] T2 -- Make 4c's input differ from 4a's, or drop the RESOLVED PLACEMENT claim.
      Verify: 4c gets an artifact 4a produced, or `SKILL.md:555-558` stops claiming it.
- [ ] T3 -- Make a run's own artifacts name the configuration that produced them. Verify:
      the artifacts of one run say whether stage 4 was serial or parallel.
- [ ] T4 -- Reword `SKILL.md:3` so the parallel form reads as the BASELINE, not as current
      behaviour. Verify: `grep -n "parallel"` finds it named as a configuration.
- [ ] T5 -- Make `SKILL.md` name every section `run_context.py --check` refuses. Verify:
      `LOOKUP CENSUS` appears in `SKILL.md` and its count equals `len(PATH_SECTIONS)`.
