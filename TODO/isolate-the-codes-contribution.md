# How much of the improvement is the code, and not the orchestration

```
Status:   blocked (on the-harness-cannot-run-the-system-it-grades -- neither the twelve
          hazards nor their grader is in this tree, so neither arm can be scored)
Progress: 4 of 10 tasks closed
Owner:    testing
Requires-Roy: false
Raised:   2026-08-22 (Roy, 2026-08-22, after ruling out a history split: the
          orchestration improvements were 0.2.1-0.2.3, so hold them constant and vary
          the code)
Triaged:  2026-08-23 -- THE INSTRUMENT THIS FILE NAMES IS NOT IN THE TREE. `ls evals/`
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
SPLIT:    2026-08-23 -- one action per box. The run box held BOTH arms and became two,
          and building arm B's agents split from the vocabulary gate that checks them.
          Six boxes became eight; the arm definitions moved to the Objective.
SPLIT:    2026-08-24 -- second pass, eight boxes to ten. RUN and GRADE were one box per arm
          and are now two: an arm can be run long before there is a grader to score it, and
          the Status line says that is exactly where this file sits.
```

## Objective

**How much of the improvement is the code, and not the orchestration.** Roy, 2026-08-22: *"I was
hoping to be able to measure how much better they are just because the code is usable and not
orchestration."* The orchestration improvements landed in 0.2.1, 0.2.2 and 0.2.3, so they are the
constant and the code is the variable.

**The two arms.** Arm A is v0.2.3 code with v0.2.3 agents exactly as tagged. Arm B is 0.2.4 code
with those SAME agents, reworded to the new dictionary and nothing else. Both are graded on the
twelve planted hazards; the difference is what the code bought.

! **Arm B's agents cannot be v0.2.3's unchanged.** v0.2.3's agents say `block` and `pcst`; the
0.2.4 census emits `paragraph`, `page` and an ADDRESS. And any wording change beyond that
substitution is a potential ORCHESTRATION change, which is the variable being held constant.

!! **IT CANNOT BE RUN TODAY, AND THAT IS THE ONE THING TO KNOW BEFORE PLANNING AROUND IT.**
MEASURED 2026-08-23: `evals/` holds `generator_split.py` and `test-cases.jsonl`. The grader
(`grade_hazards.py`), the twelve hazards (`evals.json`) and what separates a hit from a near miss
(`discriminators.md`) are none of them here. `CLAUDE.md` says why -- they were tied to a corpus
this repo cannot ship -- and rebuilding them is
[`the-harness-cannot-run-the-system-it-grades`](the-harness-cannot-run-the-system-it-grades.md).
**Both arms of this experiment are scored by that instrument, so both wait on it.**

! **SUPERSEDED AS WRITTEN**: this file used to say *"`evals/grade_hazards.py <worktree>` is the
instrument"* and that `evals/evals.json` and `evals/discriminators.md` hold the twelve hazards.
None of the three files exists.

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
of 2026-08-23, where this file said nine of ten were unfetched manifest rows. The scoping
statement stands; the count does not. Widening the hazard set across them is still work nobody
has done.

## Tasks

- [ ] T1 | T1 -- Run ARM A -- v0.2.3 code with v0.2.3 agents as tagged. Verify:
      the run's output is under `evidence/`, naming the commit it was produced
      at.
- [ ] T2 | T2 -- Grade arm A on the twelve planted hazards. Verify: the grade is
      recorded under `evidence/` beside arm A's run.
- [ ] T3 | T3 -- Run ARM B -- 0.2.4 code with the arm B agents T5 builds.
      Verify: the run's output is under `evidence/`, naming the commit it was
      produced at.
- [ ] T4 | T4 -- Grade arm B on the same twelve hazards as arm A. Verify: both
      grades are recorded so a reader who ran neither can compare them.
- [ ] T5 | T5 -- Build arm B's agents as a mechanical rename to the 0.2.4
      dictionary. Verify: `git diff v0.2.3^{} -- agents/` against arm B reads as
      substitution only.
- [ ] T6 | T6 -- Keep the shipped vocabulary green over arm B's agents. Verify:
      `uv run python scripts/check_vocabulary.py` exits 0 on arm B's tree.
- [x] T7 | FINISHED | unknown | T7 -- NOT A TASK, in the Objective: THERE IS NO
      BASELINE YET -- `evidence/cycle-0.2.3/` is a MECHANICAL run and carries no
      hazard grade.
- [x] T8 | FINISHED | unknown | T8 -- SUPERSEDED AS WRITTEN; the rule it carried
      is in the Objective, and the three named `evals/` files do not exist.
- [x] T9 | FINISHED | unknown | T9 -- NOT A TASK, in the Objective: THE TAGS ARE
      ANNOTATED -- use `v0.2.3^{}` wherever a commit is wanted.
- [x] T10 | FINISHED | unknown | T10 -- NOT A TASK, in the Objective, and one of
      its numbers was wrong. The scoping statement stands; all ten `corpora/`
      directories are materialised as of 2026-08-23.
