# The task agent emits the vocabulary; nothing restates it

```
Status:   COMPLETE 2026-08-16
Progress: 8 of 8 tasks closed
Owner:    session * Roy (design ruled 2026-08-16)
Raised:   2026-08-16 (Roy: "the task agent runs a command and puts the correct
          vocabulary verbatim into the agents prompt. No summarizing no duplication.
          The task agent already has to run python commands. this is just one more")
```

## Objective

**One source, emitted verbatim, per agent.** A script prints the definitions an agent needs; the
task agent runs it and puts the output in that agent's prompt. Nothing is summarised, nothing is
copied into a second file, and no definition passes through a paraphrasing step.

This is the pass the whole vocabulary branch deferred -- *"once we get the vocabulary resolved we
will fix how to get the vocabulary to the correct places"* -- and it is now designed rather than
open. Four alternatives were considered and rejected: one shared vocabulary file every agent
reads (every agent gets every term, and a shared file inevitably names the surrounding
machinery); the task agent assembling sections by hand (the only option that can reword a
definition); definitions written into each agent file (duplicates every shared term); and placing
each term where its readers already are (better, but leaves definitions spread across files).

! **The vocabulary becomes SHIPPED content for the first time.** Roy: *"vocabulary.md was
always going to have to move. That is the only way to get it into the system anyways."* Done
2026-08-16: `references/vocabulary.toml` holds what agents are given, and the 2,660 lines of
survey it came from are deleted -- `docs/vocabulary.md` keeps the settled state.

## Result, 2026-08-16

All eight done. `check_vocabulary.py` reports **43 definitions across 6 roles, 0 holes,
0 drifted**, and every agent carries the one-line pointer rather than the definitions.

! **Task 7 measured, since Roy put it as a claim to test:** *"it is part of the agents budget -
and I think this pays for itself in tokens removed from the references and agent definition
files."* It does, and the brief being loaded FOUR TIMES is the whole reason:

| a four-reviewer dispatch | lines of loaded context |
| --- | ---: |
| before -- 4 role files + 4 copies of the brief | 1503 |
| after -- the same, plus one emitted VOCABULARY block each | 1384 |
| **saved** | **119** |

`reviewer-brief.md` went 265 -> 199 lines, which is 264 lines out of a run because every
reviewer loads it; 134 lines are emitted back across the four. ! Per FILE it does not pay --
the six agent files net +25 lines, having gained the pointer. The saving is entirely in the
shared file. ! Approximate: other work touched these files in the same window, so this is the
window's net, not the pass's alone.

! **One deviation from the plan.** Task 5 asked for the selector in `run_context.py`. It went
into its own `vocabulary.py` instead: `run_context.py` gates the packet written ONCE per run,
and a vocabulary is per-agent, so the two answer different questions. `--reviewer` uses the
`StrEnum` the task called for.

## Tasks

- [x] T1 | FINISHED | unknown | Move the vocabulary into `plugins/` as
      **`references/vocabulary.toml`**, shaped so a definition is written once
      and the roles list only keys -- Roy, 2026-08-16: *"words are going to be
      common between each role without being used by all roles, so we should
      instead have all of the definitions at the top of the file ... and that is
      now a toml file and that makes it a load and a simple intersection."*

      ```toml
      [definitions]     # term -> the definition, written ONCE
      [roles]           # role -> the terms it gets, KEYS only
      ```

      ! **TOML needs `tomllib`, which is 3.11+**; the floor was raised to 3.11 on 2026-08-16 for
      exactly this, so it is available and stdlib. JSON, a markdown file with a parser, and a
      Python data table were the alternatives if the floor had stayed at 3.9.
      ! It then falls under `scripts/check_vocabulary.py`, whose two checks should extend to it --
      a term with no definition, and a role listing a key that `[definitions]` does not hold.

- [x] T2 | FINISHED | unknown | Measure which terms each agent needs, rather
      than judging it. Roy: *"judge by current terms used in both the agent
      definition files and the `references/*.md` files."* A term used only in
      one agent's readable text goes to that agent; one used across several is
      emitted to each of them. `scripts/vocabulary_sweep.py` already has the
      machinery to answer this.

- [x] T3 | FINISHED | unknown | ! **Remove the in-place statements the emitted
      block replaces.** Roy: *"those statements in the agent files or references
      get removed ... then all of the statements get removed where redundant and
      shortened where the word is used and explained again to just the 'word'."*
      This is the pass's real work and the reason it was deferred: some
      definitions are a CLAUSE inside a working sentence --
      `ref/reviewer-brief.md:71` reads *"quantified claims are block-context's
      REMIT, the categories of claim a role rules on"* -- and the sentence has
      to survive losing it. The prose keeps USING terms and stops DEFINING them.

- [x] T4 | FINISHED | unknown | Give each agent the one-line pointer that
      replaces those statements. Roy's shape: *"at the start of the agent it
      says you are given the vocabulary; if you are uncertain about the meaning
      of a word, refer to it."*

- [x] T5 | FINISHED | unknown | Add the selector to `sk-scripts/run_context.py`
      -- Roy: *"`--editorial-role` or `--reviewer` with a StrEnum defining
      them."*

      ! **UNBLOCKED 2026-08-16**: `StrEnum` is 3.11+ and the floor was raised to 3.11 for this
      reason, so it is available. ! Do NOT copy `LEVELS = ("fact-check", ...)` as the model: that
      tuple is itself slated for removal --
      `the-level-ladder-was-invented-during-the-port`.

- [x] T6 | FINISHED | unknown | Decide the vehicle. The dispatch PACKET is
      written once per run and handed to four agents, so a per-agent block
      belongs in the dispatch PROMPT instead. `run_context.py` has to say which,
      and `SKILL.md`'s stage-4 dispatch has to run the command.

- [x] T7 | FINISHED | unknown | ! **The emitted block is charged to the AGENT'S
      budget.** Roy, 2026-08-16: *"it is part of the agents budget - and I think
      this pays for itself in tokens removed from the references and agent
      definition files, and the quality of the emitted comment marks."* So the
      pass is measured, not asserted: record lines removed from the agent files
      and references against lines emitted. ! The quality half is a REASON, not
      a measurement -- `evals/grade_hazards.py` is the only thing that could put
      a number on it.

- [x] T8 | FINISHED | unknown | ! **It must reach `comment-review-review` and
      `comment-review-compact`, not only the four editorial roles.**
      `ref/reviewer-brief.md` goes to the four and nowhere else, so "put it in
      the brief" does not solve stages 6 and 8. Found 2026-08-16 when stage 8
      needed `truthy`, whose definition is at `ref/reviewer-brief.md:174-181`, a
      file it never loads; it is written in plain words there for now.

! **A constraint on HOW, ruled the same day.** A stage's file describes that stage's inputs and
its job, and must not name the surrounding machinery. Roy: *"I am pretty certain it is going to
go try to read those in the installed plugins the moment you state them."* So this pass gives
each agent the definitions it needs, and never tells it where the other files are.
