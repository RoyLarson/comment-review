# How much of the improvement is the code, and not the orchestration

```
Status:   open
Progress: 0 of 6 tasks done
Owner:    testing
Requires-Roy: true
Raised:   2026-08-22 (Roy, 2026-08-22, after ruling out a history split: the
          orchestration improvements were 0.2.1-0.2.3, so hold them constant and vary
          the code)
```

## Objective

How much of the improvement is the code, and not the orchestration.

## Tasks

- [ ] THE DESIGN: hold ORCHESTRATION constant, vary the CODE. Arm A is v0.2.3 code
      with v0.2.3 agents exactly as tagged. Arm B is 0.2.4 code with those SAME
      agents, reworded to the new dictionary and nothing else. Both graded on the
      twelve planted hazards. The difference is what the code bought. ! Roy,
      2026-08-22: *"I was hoping to be able to measure how much better they are
      just because the code is usable and not orchestration"* -- the orchestration
      improvements landed in 0.2.1, 0.2.2 and 0.2.3, so they are the constant.
- [ ] THE REWORDING IS THE CONFOUND, and controlling it is most of the work.
      v0.2.3's agents say `block` and `pcst`; the 0.2.4 census emits `paragraph`,
      `page` and an ADDRESS. So arm B cannot use them unchanged -- and any wording
      change is a potential orchestration change, which is the thing being held
      constant. ! SO THE SUBSTITUTION MUST BE MECHANICAL AND DIFFABLE: a
      dictionary rename only, no new instruction, no restructured stage, no
      sharpened sentence. The diff of arm B's agents against v0.2.3's should read
      as nothing but the rename. `scripts/check_vocabulary.py` is what says the
      result speaks the shipped language.
- [ ] THERE IS NO BASELINE YET, which is worth knowing before anyone plans around
      one. `evidence/cycle-0.2.3/` is a MECHANICAL run -- census, galley, edits,
      join -- and carries no hazard grade. Both arms have to be run.
- [ ] GRADE FROM THE DIFF, NEVER THE REPORT. `evals/grade_hazards.py <worktree>`
      is the instrument and it reads what was WRITTEN, because self-reported
      confidence has been measured here not to discriminate a real finding from a
      fabricated one. ! `evals/evals.json` and `evals/discriminators.md` hold the
      twelve hazards and what separates a hit from a near miss.
- [ ] THE TAGS ARE ANNOTATED, so `git rev-parse v0.2.3` returns the TAG OBJECT and
      not the commit. Use `v0.2.3^{}` wherever a commit is wanted -- this is the
      trap anyone re-deriving which code produced a measurement hits first.
- [ ] AND SAY WHAT THE ANSWER CANNOT BE. A difference between the arms is the
      code's contribution ON THE TWELVE HAZARDS, over the corpus those hazards
      live in -- not a general claim about the tool. ! The hazards are planted in
      ONE codebase, which is the confound `corpora/` exists to widen and has not
      widened yet: nine of the ten non-Python corpora are manifest rows,
      unfetched.
