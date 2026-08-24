# How much of the improvement is the code, and not the orchestration

```
Status:   blocked (on the-harness-cannot-run-the-system-it-grades -- neither the twelve
          hazards nor their grader is in this tree, so neither arm can be scored)
Progress: 4 of 6 tasks done
Owner:    testing
Requires-Roy: false
Raised:   2026-08-22 (Roy, 2026-08-22, after ruling out a history split: the
          orchestration improvements were 0.2.1-0.2.3, so hold them constant and vary
          the code)
Triaged:  2026-08-23 — THE INSTRUMENT THIS FILE NAMES IS NOT IN THE TREE. `ls evals/`
          returns `generator_split.py` and `test-cases.jsonl` and nothing else --
          `evals/grade_hazards.py`, `evals/evals.json` and `evals/discriminators.md` do
          not exist, which `CLAUDE.md` states independently: *"the twelve planted hazards
          and their grader are NOT here -- there is no end-to-end grade."* So the design
          is sound and unrunnable, and the file is blocked rather than open. ! One
          measurement in it also went stale the other way: all ten corpora ARE fetched --
          `corpora/` holds `cpython`, `django`, `fastapi`, `flask`,
          `meta-package-manager`, `neovim`, `numpy`, `photo_organizer`, `pymc` and
          `sentry`, each non-empty. ! Requires-Roy cleared: no box asks him to decide
          anything; what is missing is an artifact.
```

## Objective

**How much of the improvement is the code, and not the orchestration.** Roy, 2026-08-22: *"I was
hoping to be able to measure how much better they are just because the code is usable and not
orchestration."* The orchestration improvements landed in 0.2.1, 0.2.2 and 0.2.3, so they are the
constant and the code is the variable.

!! **IT CANNOT BE RUN TODAY, AND THAT IS THE ONE THING TO KNOW BEFORE PLANNING AROUND IT.**
MEASURED 2026-08-23: `evals/` holds `generator_split.py` and `test-cases.jsonl`. The grader
(`grade_hazards.py`), the twelve hazards (`evals.json`) and what separates a hit from a near miss
(`discriminators.md`) are none of them here. `CLAUDE.md` says why -- they were tied to a corpus
this repo cannot ship -- and rebuilding them is
[`the-harness-cannot-run-the-system-it-grades`](the-harness-cannot-run-the-system-it-grades.md).
**Both arms of this experiment are scored by that instrument, so both wait on it.**

! **THE RULE THE GRADER ENFORCED STANDS AND HAS NOWHERE TO RUN: GRADE FROM THE DIFF, NEVER FROM
THE RUN'S OWN REPORT.** Self-reported confidence has been measured here not to discriminate a real
finding from a fabricated one. Whatever replaces `grade_hazards.py` reads what was WRITTEN.

!! **THERE IS NO BASELINE EITHER.** `evidence/cycle-0.2.3/` is a MECHANICAL run -- census, galley,
edits, join, and four role reports -- and carries no hazard grade. Both arms have to be run; there
is nothing to compare a single new arm against.

! **THE TAGS ARE ANNOTATED**, so `git rev-parse v0.2.3` returns the TAG OBJECT and not the commit.
Use `v0.2.3^{}` wherever a commit is wanted -- this is the trap anyone re-deriving which code
produced a measurement hits first.

!! **AND WHAT THE ANSWER CANNOT BE.** A difference between the arms is the code's contribution ON
THE TWELVE HAZARDS, over the codebase those hazards are planted in -- not a general claim about
the tool. ! The hazards live in ONE codebase, which is the confound `corpora/` exists to widen.
**That confound has narrowed since this was filed**: all ten corpora are materialised on disk as
of 2026-08-23, where this file said nine of ten were unfetched manifest rows. Widening the
hazard set across them is still work nobody has done.

## Tasks

- [ ] T1 -- RUN BOTH ARMS. Arm A is v0.2.3 code with v0.2.3 agents exactly as
      tagged. Arm B is 0.2.4 code with those SAME agents, reworded to the new
      dictionary and nothing else. Both graded on the twelve planted hazards; the
      difference is what the code bought. ! BLOCKED: the grader and the hazards are
      not in this tree -- see the Objective and
      `the-harness-cannot-run-the-system-it-grades`. Verify: two graded runs sit
      under `evidence/`, each naming the commit it was produced at, and a reader
      who ran neither can say which arm scored higher and by how much.
- [ ] T2 -- BUILD ARM B'S AGENTS AS A MECHANICAL RENAME, and nothing else.
      v0.2.3's agents say `block` and `pcst`; the 0.2.4 census emits `paragraph`,
      `page` and an ADDRESS, so arm B cannot use them unchanged -- and any wording
      change is a potential ORCHESTRATION change, which is the variable being held
      constant. Verify: `git diff v0.2.3^{} -- plugins/comment-review/agents/`
      against arm B's tree reads as a dictionary substitution only -- no new
      instruction, no restructured stage, no sharpened sentence -- and
      `uv run python scripts/check_vocabulary.py` passes over the result.
- [x] T3 -- NOT A TASK, restated in the Objective. THERE IS NO BASELINE YET, which
      is worth knowing before anyone plans around one. `evidence/cycle-0.2.3/` is a
      MECHANICAL run -- census, galley, edits, join -- and carries no hazard grade.
      Both arms have to be run. A measurement is not a checkpoint.
- [x] T4 -- SUPERSEDED AS WRITTEN, and the rule it carried is in the Objective. It
      said *"`evals/grade_hazards.py <worktree>` is the instrument"* and that
      `evals/evals.json` and `evals/discriminators.md` hold the twelve hazards.
      MEASURED 2026-08-23: none of the three files exists; `evals/` holds
      `generator_split.py` and `test-cases.jsonl`. ! GRADE FROM THE DIFF, NEVER THE
      REPORT still holds and is what the replacement must do -- self-reported
      confidence has been measured here not to discriminate a real finding from a
      fabricated one. Rebuilding the instrument is
      `the-harness-cannot-run-the-system-it-grades`, which this file is blocked on.
- [x] T5 -- NOT A TASK, restated in the Objective. THE TAGS ARE ANNOTATED, so
      `git rev-parse v0.2.3` returns the TAG OBJECT and not the commit. Use
      `v0.2.3^{}` wherever a commit is wanted. A trap worth writing down is not a
      checkpoint anyone ticks.
- [x] T6 -- NOT A TASK, restated in the Objective, and one of its numbers is now
      wrong. It said the answer is the code's contribution ON THE TWELVE HAZARDS,
      over the codebase they live in -- not a general claim about the tool -- and
      that *"nine of the ten non-Python corpora are manifest rows, unfetched."*
      MEASURED 2026-08-23: all ten `corpora/` directories are materialised and
      non-empty. The scoping statement stands; the count does not.
