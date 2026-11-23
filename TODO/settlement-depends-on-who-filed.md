# Settlement depends on who filed, not on what was read

```
Status:   open
Progress: 0 of 3 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-11-23 (broken review, 2026-11-23)
```

## Objective

From the broken review of comment-review at 6a81c7b0
(feat/0.2.4-what-a-reviewer-is-handed), 2026-11-23. Evidence codes cite the
review's perspective outputs (W workflow, A architecture, D domain, I
implementation, N names, V vocabulary). The solution phase has not run; nothing
below is a recommendation.

Problem 4. Settlement depends on who filed, not on what was read [W-F3, W-F4,
W-F8, N-N5; V17, V19, V22]

- A lone proposal becomes `State.STANDS` (`desk/evaluate/passes.py:500,513`), so in a
  one-reader stage (4a) every move or drop settles at exit 0 unread and prints `stet`. The
  chief's `taken_in original` is refused as "not an open move"; undoing takes two recasts (W).
  This run's stage 8 measured the cost (defects on 35 of 62 pages; board:
  stage-5-is-the-only-stage-with-no-independent-reader T18).
- Two disjoint sentence edits compose when one role files them and contest when two do:
  within a role the fold matches by clause (`passes.py:76-79`), across roles it merges by line
  (`:521`); the docstring at `:55-58` claims they are the same, and the T36 fix (4e67fa3d)
  changed only the within-role site (W-F4).
- The console prints `stet` for every settled place including changed text
  (`commands/report.py:93-99`); `StetAnswer` is a role refusing a move; the docs say only the
  chief may stet (W-F8, N-N5).

## Tasks

- [ ] T1 | Determine what settles a place apart from who filed its marks
        > 2026-11-23 Solution phase running; recommendation to follow (broken review)
        > 2026-11-23 Symptom: stage-5-is-the-only-stage-with-no-independent-reader T18
- [ ] T2 | Make two disjoint sentence edits settle alike from one role or from
      two
- [ ] T3 | Make the console name a settled place by what settled it
        > 2026-11-23 Related: no-mark-for-let-it-stand.md
