# Stage 1 is re-derived every run, asks one question twice, and knows one structure source

```
Status:   in-progress
Progress: 1 of 8 tasks done
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

## Tasks

- [ ] T1 -- * Collapse 1.7 and 1.8 into ONE substep, and name it for what it does:
      find what structure is available. The name corpus stops being a decision and
      becomes the output. ! Roy's ruling, because it renumbers a stage's substeps
      and the numbers are cited from `run_context.py`, `census.py` and elsewhere in
      `SKILL.md`. Verify: one substep in `SKILL.md`, and every citation of the old
      numbers re-resolved -- `grep -rn "1\.8" plugins/` comes back empty or points
      at the new number.

- [ ] T2 -- * Rule on CodeGraph: does the skill probe for `.codegraph/` alongside
      the LSP probe, and does `codegraph_explore` become a sanctioned way to settle
      an anchor and a liveness claim? ! Check the register before naming anything
      new. ! This repo now carries a `.codegraph/` index, so whatever is written
      can be exercised here rather than shipping unrun. Verify: the answer is in
      `SKILL.md` with the probe, or this file records the refusal and why.

- [ ] T3 -- State the THREE structure states per SOURCE, not per run, once 1.7/1.8
      collapse. Today 1.7's three-state table (`answered` / `no server for this
      language` / `no LSP tool at all`) is written for LSP alone, and the third
      state -- the tool is absent so no probe is possible -- applies to CodeGraph
      identically. Verify: the table in `SKILL.md` names the source in each row.

- [x] T4 -- * RULED 2026-08-17: `.claude/comment-review/` in the repo under review.
      Roy's words. A per-repo location beside the other `.claude` configuration, so
      the sheet is found without the human typing a path and travels with the repo
      it describes. ! It is still written only after approval, like everything else
      -- this does not make stage 1 a writing stage. ! The ruling is MADE and
      UNIMPLEMENTED: the path is in no shipped file, which is what T5 carries.

- [ ] T5 -- Widen the sheet to carry the REPO-side rows of the table above, and say
      in the sheet itself which rows are repo facts. A sheet that mixes them invites
      the next run to read a machine fact back. Verify: `SKILL.md` 1.5 names
      `.claude/comment-review/` as where a sheet is found and written, and the
      sheet's own format lists the repo rows.

- [ ] T6 -- State explicitly, in the sheet's own format, that LSP state and agent
      resolution are NEVER recorded, ! with the REASON beside each -- or a later
      pass "completes" the sheet by adding them. Verify: the two exclusions and
      their reasons are in the format, not only in this file.

- [ ] T7 -- Decide what happens when a persisted answer is now WRONG -- a cap
      published since the last run, a deleted `docs/` tree. ! Recommendation: the
      sheet records the ref it was measured at, and stage 1 re-measures only what
      the diff since that ref touched. Verify: the sheet format carries the ref,
      and `SKILL.md` says what stage 1 does with it.

- [ ] T8 -- Re-measure the stage-1 cost after the change and record it here. Today:
      ~25 tool calls, measured on both 2026-08-17 runs. ! Record it as a fact, not
      as a budget question. Verify: a dated count in this file taken from a run
      after the collapse.
