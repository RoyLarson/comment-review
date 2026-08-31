# The brief says three series, and the addresser answers four

```
Status:   open
Progress: 0 of 3 tasks done
Owner:    agents
Requires-Roy: false
Raised:   2026-08-29 (found sweeping reviewer-brief.md against its consumers on
          feat/the-mark-and-the-collator, 2026-08-29)
```

## Objective

`reviewer-brief.md:69` says *"The three series are counted by three separate addressers"* and
`:221` offers a `--series` flag naming only `a`, `b` and `c`. `reading/series.py`'s `ADDRESSED`
is `('a', 'b', 'c', 'f')` and `SKILL.md:378` says four -- so a role cannot resolve the `@f0`
place the same brief tells it to cite at `:74`.

## Tasks

- [ ] T1 | Decide what a role is told about the f series, and make
      reviewer-brief.md:69 agree with SKILL.md:378
- [ ] T2 | Fix the --series a\|b\|c example at reviewer-brief.md:221 to the set
      the addresser command actually accepts
- [ ] T3 | Reconcile with reviewer-brief.md:74-79, which calls @f0 the file's
      own matter, filtered out of the census and not a place a role rules on --
      if that still holds, say which of the four a role may cite and which it
      may only read
