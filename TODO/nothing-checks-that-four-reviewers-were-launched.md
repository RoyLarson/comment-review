# Nothing checks that four reviewers were LAUNCHED

```
Status:   decision-needed
Progress: 1 of 5 tasks done
Owner:    agents
Requires-Roy: true
Raised:   2026-08-17, on a MISREADING that turned out to sharpen the task -- see below
TRIAGED:  2026-08-23 -- RE-VERIFIED against the shipped tree, and ONE PREMISE MOVED.
          `--reviewers` is still OPTIONAL (verdicts.py:296) and its absence is still only
          ANNOUNCED (verdicts.py:516), so T2 stands. `SKILL.md` still says nothing about
          COUNTING the dispatch: `grep -n 'four were|counted'` over SKILL.md returns no
          stage-4 hit, so T3 stands. ! WHAT MOVED: stage 4 now SEEDS one report file per
          role before dispatch (SKILL.md:658-664, `record.py --seed --reviewer $role
          --out <run-dir>/$role.json`), so a four-named-file artifact in the run directory
          already exists -- which is most of candidate (d) and is stated in T1 rather
          than left for the ruling to rediscover.
```

## Objective

**`!! Every verdict is available on every run, and all four roles run every time`** is stated in
`SKILL.md` and enforced by nothing at the moment it matters.

! The gap is real; the incident that raised it was not. See T5.

What exists today, and where each check sits:

| check | where | when it fires |
| --- | --- | --- |
| the four agents RESOLVE | `SKILL.md` 1.6 | stage 1, before anything is dispatched |
| four report files are SEEDED, one per role | `SKILL.md` 658-664 | stage 4, before dispatch |
| every expected reviewer REPORTED | `verdicts.py --reviewers` | stage 5, after the reports are in |
| a report stem is a published role name | `verdicts.py` | stage 5 |

! **1.6 proves the agents can be dispatched; the seed proves four files were CREATED; nothing
proves four were DISPATCHED.** The gap is the dispatch itself, and it is the one step the skill
cannot inspect: `run_context.py` runs before it and `verdicts.py` runs after.

!! **`--reviewers` catches it LATE, and nothing earlier has an artifact to read.** A three-role
dispatch is detected only once three reviewers have read the census and written their reports --
on a large run that is several hundred thousand tokens and twenty minutes before the run learns it
was invalid. And it is only caught at all if the task agent passes `--reviewers`, which is
optional.

! Why the invariant is not a formality: `SKILL.md` records that **a single-role run ratifies
falsehoods** -- one role reading a false absence claim writes that it is true, where another
refutes it by grep. A three-role run is the same defect, weaker. And the missing role's blocks
are not gaps the join can see: it computes coverage from the reviewers that REPORTED, so three
complete reports read as complete coverage unless `--reviewers` names the fourth.

## Why a stage-4 INSTRUCTION TO OBSERVE is the wrong shape

Kept here rather than in a box, because it is an argument and not work.

!! **The only thing there to observe is a display that LAGS.** On 2026-08-17 the fourth agent
took time to appear; TWO independent readers -- the repo's author, who then waited minutes and
questioned the running session about it, and the session that filed this task -- both concluded
three had launched. An instruction to COUNT WHAT IS DISPLAYED would have raised a false alarm on
a correct run.

!! **DECLARATION beats observation.** Naming four roles in a file cannot lag, it leaves the
artifact the table above says is missing, and it stops `--reviewers` depending on a human
remembering to type it. It is still a self-report and no more trustworthy than the agent making
it -- but a self-report that four were dispatched, against three reports on disk, is a
contradiction the join can print.

!! **And the RELIABLE signal already exists -- it is the dispatch tool's own return, one per
call.** The 2026-08-17 session settled the question exactly that way: four launch confirmations,
and four task-output files, one per id it had been handed. That is a return value, not a
rendering, so it cannot lag. **A declaration is therefore not "invent a record" but "write down
the one you were already given."** Say that in whatever lands, or an agent will reach for the
display again -- it is the thing in front of it.

## Tasks

- [ ] T1 -- * Rule on WHERE the check goes. There is no artifact between the packet and the
      reports that records a DISPATCH, so the candidates are: (a) the task agent states the four
      agent names in the PROPOSAL and the human sees a short list, (b) `--reviewers` stops being
      optional and defaults to the four editorial roles, (c) a stage-4 line in `SKILL.md`
      requiring the dispatch be re-read and the count stated before waiting on results, (d) the
      task agent WRITES the four role names to the run directory at dispatch time, and stage 5
      reads that file rather than a flag the human typed.
      ! Recommendation: **(b) and (d). Not (c)** -- the section above says why.
      ! MEASURED 2026-08-23, and it shortens (d): stage 4 ALREADY writes four files named for
      the four roles, at SKILL.md:658-664, by seeding each reviewer's report before dispatch.
      What those files do not carry is a statement that a dispatch was MADE, so (d) is a field
      on an existing artifact rather than a new one.

- [ ] T2 -- Make `--reviewers` default to the four editorial roles rather than to `""`.
      MEASURED 2026-08-23: it is still optional (verdicts.py:296) and its absence is still only
      announced -- *"whether every expected reviewer reported was NOT checked"* (verdicts.py:516)
      -- and an announcement in a wall of output is not a gate. ! Check what this does to a
      deliberate single-role run; if that is a thing anyone does, it needs an explicit way to say
      so. Verify: `verdicts.py` with no `--reviewers` over three report files exits nonzero and
      names the fourth role.

- [ ] T3 -- Say in `SKILL.md` stage 4 that the dispatch is COUNTED, and that four is the number.
      ! It must name the failure: a short dispatch is not detected until stage 5, after the
      reviewers that did run have spent everything. Verify: the sentence exists under
      `## Stage 4` (SKILL.md:544) and names the count.

- [ ] T4 -- * Rule on whether a missing role is FATAL at stage 5 or a stated degradation. It is
      fatal today via `--reviewers`. ! Fatal is probably right -- the alternative is a proposal
      that reads like a four-role run and is not -- but the ruling should be written down rather
      than inherited from an implementation detail.

- [x] T5 -- NOT A TASK. RECORD, kept because it is the evidence for the section above:
      !! **on 2026-08-17 FOUR were dispatched, and the fourth took time to register in the
      display.** This file was raised on a transcript reading "3 background agents launched",
      which was a UI lag read as an event. No run short-dispatched. ! Left in rather than
      deleted: the only signal available at dispatch time is one that lags, and it misled a
      reader who was looking straight at it.
