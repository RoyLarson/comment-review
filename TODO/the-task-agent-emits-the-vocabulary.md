# The task agent emits the vocabulary; nothing restates it

```
Status:   open
Progress: 0 of 8 tasks done
Owner:    session · Roy (design ruled 2026-08-16)
Raised:   2026-08-16 (Roy: "the task agent runs a command and puts the correct
          vocabulary verbatim into the agents prompt. No summarizing no duplication.
          The task agent already has to run python commands. this is just one more")
```

## Objective

**One source, emitted verbatim, per agent.** A script prints the definitions an agent needs; the
task agent runs it and puts the output in that agent's prompt. Nothing is summarised, nothing is
copied into a second file, and no definition passes through a paraphrasing step.

This is the pass the whole vocabulary branch deferred — *"once we get the vocabulary resolved we
will fix how to get the vocabulary to the correct places"* — and it is now designed rather than
open. Four alternatives were considered and rejected: one shared vocabulary file every agent
reads (every agent gets every term, and a shared file inevitably names the surrounding
machinery); the task agent assembling sections by hand (the only option that can reword a
definition); definitions written into each agent file (duplicates every shared term); and placing
each term where its readers already are (better, but leaves definitions spread across files).

⚠ **The vocabulary becomes SHIPPED content for the first time.** `docs/vocabulary-usage.md` is
2100 lines of survey and does not ship. Roy: *"vocabulary.md was always going to have to move.
That is the only way to get it into the system anyways."*

## Tasks

- [ ] Move the vocabulary into `plugins/` as a compact record — term, definition, and which
      agents need it — separate from the survey and the rulings, which stay in `docs/`. ⚠ It then
      falls under `scripts/check_vocabulary.py`, whose two checks should extend to it.

- [ ] Measure which terms each agent needs, rather than judging it. Roy: *"judge by current terms
      used in both the agent definition files and the `references/*.md` files."* A term used only
      in one agent's readable text goes to that agent; one used across several is emitted to each
      of them. `scripts/vocabulary_sweep.py` already has the machinery to answer this.

- [ ] ⚠ **Remove the in-place statements the emitted block replaces.** Roy: *"those statements in
      the agent files or references get removed … then all of the statements get removed where
      redundant and shortened where the word is used and explained again to just the 'word'."*
      This is the pass's real work and the reason it was deferred: some definitions are a CLAUSE
      inside a working sentence — `ref/reviewer-brief.md:71` reads *"quantified claims are
      block-context's REMIT, the categories of claim a role rules on"* — and the sentence has to
      survive losing it. The prose keeps USING terms and stops DEFINING them.

- [ ] Give each agent the one-line pointer that replaces those statements. Roy's shape: *"at the
      start of the agent it says you are given the vocabulary; if you are uncertain about the
      meaning of a word, refer to it."*

- [ ] Add the selector to `sk-scripts/run_context.py` — Roy: *"`--editorial-role` or `--reviewer`
      with a StrEnum defining them."*

      ⚠ **`StrEnum` is Python 3.11+ and the shipped floor is 3.9.** `from enum import StrEnum`
      PARSES at the floor and fails at import, so `scripts/check_shipped_syntax.py` cannot catch
      it — its own docstring says *"`ast.parse(feature_version=...)` validates syntax and nothing
      else."* It would break on a user's machine and never on ours. Use `class Reviewer(str,
      Enum)`, or match the idiom already in that file: `LEVELS = ("fact-check", "line", "full",
      "proof")`, used with argparse `choices=`.

- [ ] Decide the vehicle. The dispatch PACKET is written once per run and handed to four agents,
      so a per-agent block belongs in the dispatch PROMPT instead. `run_context.py` has to say
      which, and `SKILL.md`'s stage-4 dispatch has to run the command.

- [ ] ⚠ **The emitted block is charged to the AGENT'S budget.** Roy, 2026-08-16: *"it is part of
      the agents budget - and I think this pays for itself in tokens removed from the references
      and agent definition files, and the quality of the emitted comment marks."* So the pass is
      measured, not asserted: record lines removed from the agent files and references against
      lines emitted. ⚠ The quality half is a REASON, not a measurement — `evals/grade_hazards.py`
      is the only thing that could put a number on it.

- [ ] ⚠ **It must reach `comment-review-review` and `comment-review-compact`, not only the four
      editorial roles.** `ref/reviewer-brief.md` goes to the four and nowhere else, so "put it in
      the brief" does not solve stages 6 and 8. Found 2026-08-16 when stage 8 needed `truthy`,
      whose definition is at `ref/reviewer-brief.md:174-181`, a file it never loads; it is
      written in plain words there for now.

⚠ **A constraint on HOW, ruled the same day.** A stage's file describes that stage's inputs and
its job, and must not name the surrounding machinery. Roy: *"I am pretty certain it is going to
go try to read those in the installed plugins the moment you state them."* So this pass gives
each agent the definitions it needs, and never tells it where the other files are.
