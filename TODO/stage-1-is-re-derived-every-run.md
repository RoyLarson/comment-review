# Stage 1 is re-derived every run, asks one question twice, and knows one structure source

```
Status:   in-progress
Progress: 1 of 14 tasks closed
Owner:    agents
Requires-Roy: true
Raised:   2026-08-17 (two full runs in one session, on two repos; stage 1 was established
          from scratch both times and both style sheets were left in a session scratchpad)
Sharpened: 2026-08-17 (Roy: "Figure out why twice / LSP state and name corpus -- twice /
          One pass should have been enough. / Besides lsps there is also codegraph")
Re-checked: 2026-08-23 -- 1.7 (`SKILL.md:286`) and 1.8 (`:319`) are unchanged. CodeGraph
          is no longer absent from the tree: zero occurrences under `plugins/`, three
          files under `docs/`, and THIS repo now carries a `.codegraph/` index, so the
          "ships unexercised" caveat no longer holds here. The ruled sheet home
          `.claude/comment-review/` appears nowhere in the shipped skill.
SPLIT:    2026-08-23 -- one action per box. Eight boxes became twelve: the collapse split
          from re-resolving the citations that name 1.8, the CodeGraph ruling split into
          the probe and the sanctioned use, widening the sheet split from naming its home,
          and the staleness rule split from the ref that makes it computable.
SPLIT:    2026-08-24 -- second pass, twelve boxes to fourteen. The `codegraph_explore`
          ruling was two rulings (anchor, liveness) and the sheet's exclusions were two
          exclusions with two different reasons (a machine fact, a session fact).
```

## Objective

Three defects, and the second explains the first.

### 1. Nothing carries forward

**Every stage-1 answer is discovered again on every run.** Measured across two runs on two
repos: ~25 tool calls each to establish cap, width, whether a guard exists, the documentation
templates, the `move` destination tree, whether the reviewer agents resolve, the structure
available, and the name-corpus source.

`SKILL.md` 1.5 says the STYLE SHEET *"is the only thing in this skill that PERSISTS between
runs"*. Two problems with that as it stands:

- **It has no home.** It reaches a run through the `style` argument (`SKILL.md:157`), so the
  human has to remember a path and type it. Both sheets written on 2026-08-17 went to a session
  scratchpad, which is deleted with the session. ! The location was RULED on 2026-08-17 and the
  shipped skill still does not name it -- measured 2026-08-23, `.claude/comment-review` has zero
  occurrences under `plugins/`.
- **It carries the templates and the rulings, and none of the other stage-1 facts.** The cap,
  the width, whether the guard exists, the destination tree and the marker exemptions are
  re-derived every time and appear only in the run's proposal.

!! **THE HOME IS RULED AND UNIMPLEMENTED.** Roy, 2026-08-17: `.claude/comment-review/` in the
repo under review -- a per-repo location beside the other `.claude` configuration, so the sheet is
found without the human typing a path and travels with the repo it describes. ! It is still
written only after approval, like everything else; this does not make stage 1 a writing stage.

### 2. !! 1.8 IS NOT A QUESTION -- it is 1.7's answer restated

`SKILL.md:286` probes for a language server. `:319` "decides where the name corpus comes from",
and every branch of it is a lookup on 1.7:

| 1.8 says | its only input |
| --- | --- |
| a server answered -> `workspaceSymbol` | 1.7 |
| no server -> the AST corpus, Python only | 1.7, plus a fixed property of `census.py` |
| both -> combine them | 1.7 |

There is no input `1.8` holds that `1.7` does not. A task agent probes once and then performs a
substep whose answer was already fixed -- which is why it reads as being asked twice.

! This TODO reproduced the same error in its own first draft: the persistence table below
listed *"which LSP servers answered"* and *"the name-corpus source (derived from LSP)"* as two
rows, writing **derived from** and still counting it as a separate answer.

### 3. The skill knows ONE structure source, and that is why 1.7 and 1.8 look like two steps

With only LSP in view, *"is a server there?"* and *"so where do names come from?"* read as two
questions. They are one: **what structure is available here, and from where.**

**CodeGraph is a second source and the shipped skill still does not mention it.** MEASURED
2026-08-23: zero occurrences under `plugins/`; three files under `docs/` name it
(`docs/addressing.md:164`, `docs/history.md:56`, and one spec). It answers both halves at once:
symbols for a paragraph's ANCHOR, call paths for liveness. Landing on 1.7 and 1.8 simultaneously
is itself the evidence that they are one substep.

!! **And it breaks the persistence split**, which is the reason it belongs in this file:

| source | availability is a fact about | may persist? |
| --- | --- | --- |
| LSP | the **machine** -- a server someone happens to run | **no** |
| CodeGraph | the **repo** -- a `.codegraph/` directory in the tree | **yes** |

CodeGraph is the first structure source whose presence is discoverable from the checkout alone,
which is the property that makes it recordable at all. ! And it is exercisable here now: this
repo carries a `.codegraph/` directory, which it did not on 2026-08-17.

## !! Persistence has to be SELECTIVE

Some stage-1 answers are facts about the REPO and are the same next month. Others are facts
about the MACHINE or the SESSION and are false the moment they are read back.

| answer | about | persist? |
| --- | --- | --- |
| published cap, published width, and how each counts | the repo | yes |
| whether the guard that enforces them EXISTS | the repo | yes |
| documentation templates measured at 1.3 | the repo | yes -- the sheet already holds these |
| the `move` destination tree, and any per-path split | the repo | yes |
| which markers the repo exempts from the cap | the repo | yes |
| terms of art, dialect, citation form, past rulings | the repo | yes -- already in the sheet |
| **whether a `.codegraph/` index exists** | the repo | yes |
| **which LSP servers answered** | the machine | !! **no** |
| **which reviewer agents resolved** | the session | !! **no** |

!! **Reading a stale LSP answer back is the failure `SKILL.md` 1.7 already forbids**: *"Absence
is reported, never inferred"*, and *"a run that had no server must not read like one that did"*.
A sheet recording "python answered" makes every later run on another machine claim structure it
never had. The same holds for the agents: 1.6's check is about THIS session, and the
2026-08-17 runs are the proof -- the agents did not resolve until the plugin was reloaded
mid-session.

! The name corpus is deliberately absent from that table. Under defect 2 it is not an answer at
all; it is whatever the structure sources say, computed at dispatch.

! **Recommendation for the staleness question**, kept here rather than in a box: the sheet records
the ref it was measured at, and stage 1 re-measures only what the diff since that ref touched.

! **Four things the boxes below no longer carry.** The 1.7/1.8 collapse is Roy's because it
RENUMBERS substeps. Any name proposed for a structure source is checked against the editorial
register BEFORE it is proposed, per `CLAUDE.md`. The three structure states are `answered`, `no
server for this language` and `no tool at all`. And a persisted answer goes wrong the ordinary
ways -- a cap published since the last run, a `docs/` tree deleted since.

## Tasks

- [?] T1 | T1 -- * Collapse 1.7 and 1.8 into ONE substep named for what it does:
      find what structure is available. Verify: `SKILL.md` has one substep
      there, not two.
- [ ] T2 | T2 -- Re-resolve every citation of the old substep numbers once T1
      lands. Verify: `grep -rn "1\.8" plugins/` is empty or points at the new
      number.
- [?] T3 | T3 -- * Rule whether the skill probes for `.codegraph/` alongside the
      LSP probe. Verify: the probe is in `SKILL.md`, or this file records the
      refusal and why.
- [?] T4 | T4 -- * Rule whether `codegraph_explore` is a sanctioned way to
      settle a paragraph's ANCHOR. Verify: the answer is recorded in `SKILL.md`
      or in this file.
- [?] T5 | T5 -- * Rule whether `codegraph_explore` is a sanctioned way to
      settle a LIVENESS claim. Verify: the answer is recorded in `SKILL.md` or
      in this file.
- [ ] T6 | T6 -- State the three structure states PER SOURCE rather than per
      run. Verify: every row of the `SKILL.md` structure table names the source
      it is about.
- [ ] T7 | T7 -- Name `.claude/comment-review/` in `SKILL.md` 1.5 as where a
      sheet is found and written. Verify: `grep -rn "\.claude/comment-review"
      plugins/` returns that line.
- [ ] T8 | T8 -- Widen the sheet's own format to carry the REPO-side rows of the
      table above, marked as repo facts. Verify: the format lists them and says
      which are repo facts.
- [ ] T9 | T9 -- State in the sheet's format that LSP state is NEVER recorded,
      with the reason. Verify: the exclusion and its reason are both in the
      format.
- [ ] T10 | T10 -- State in the sheet's format that agent resolution is NEVER
      recorded, with the reason. Verify: the exclusion and its reason are both
      in the format.
- [ ] T11 | T11 -- Decide what stage 1 does when a persisted answer is now
      WRONG. Verify: `SKILL.md` states what a run does with a stale answer.
- [ ] T12 | T12 -- Record in the sheet the ref it was measured at, so T11's rule
      is computable. Verify: the sheet format carries the ref.
- [ ] T13 | T13 -- Re-measure the stage-1 tool-call cost after the collapse.
      Verify: a dated count in this file, taken from a run made after the
      collapse landed.
- [x] T14 | FINISHED | unknown | T14 -- RULED 2026-08-17, in the Objective:
      `.claude/comment-review/` in the repo under review, Roy's words. The
      ruling is made; implementing it is T7.
