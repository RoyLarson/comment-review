# Nothing measures which code the suite actually runs

```
Status:   open
Progress: 1 of 5 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-25 (Roy, 2026-08-25, during the write-chain branch, after the suite
          was cleaned of tests a cut left behind)
Updated:  2026-08-25 — BASELINE, 2026-08-25, coverage 7.15.4 over 789 passed / 3
          xfailed: 43.0 percent of 1864 statements, 1063 unrun. THE ZEROS ARE THE
          FINDING. All six commands/ modules 0.0 percent (537 statements) -- confirms
          two-areas-have-no-tests, and note a smoke run shows all six EXIT 0, so they
          work and nothing watches them. results/prove_unchanged.py 0.0 (89) -- this
          branch's task 11 will exercise it through the flow. binder/annotate.py 0.0
          (58), concordance/code_names.py and referrers.py 0.0 (72),
          desk/external_address.py 0.0 (8). READ THESE AS DELETION CANDIDATES FIRST:
          annotate.py is stage 3 and the chain Roy ruled on does not obviously reach it.
          Covered well: series.py, exceptions.py and binder.py at 100, page.py 94.7,
          addresser.py 93.4, language.py 95.7. machine/repo.py is 40.7 because its git
          half has no tests, not because read_source lacks them.
```

## Objective

Nothing measures which code the suite actually runs.

## Tasks

- [x] T1 | FINISHED | unknown | Ask systems to pin a coverage tool in
      pyproject.toml -- that file is systems-owned, so backend cannot add the
      dependency itself
- [ ] T2 | Record the baseline: which lines of src/comment_review/ the suite
      executes today, per module
- [ ] T3 | Read the uncovered set as a DELETION list, not a test-writing list.
      For each: is this code wanted? Cut what is not, before writing a test for
      it
- [ ] T4 | For code that is wanted and uncovered, write the test -- and say what
      behaviour it pins, not that it raises coverage
- [ ] T5 | Decide whether a coverage floor becomes a gate. Verify: if it does,
      it is systems-owned and it can FAIL -- a floor set at the current number
      can never fail
