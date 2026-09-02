# A move's change_all check never decides the shape gate's outcome

```
Status:   open
Progress: 0 of 2 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-28 (found while rebuilding tests/test_mark.py for the-mark-and-the-
          revise Task 1, fix round 1, 2026-08-28: well_formed('move') needed a literal
          change value that problems() actually accepts, and no dict form does)
```

## Objective

A move's change_all check never decides the shape gate's outcome.

## Tasks

- [ ] T1 | Read problems()'s change handling in desk/mark.py: the general
      owes_change block requires change to be a list before the change_all loop
      (if isinstance(change, dict)) ever runs, so change_all's dict-shaped check
      is never the DECISIVE factor -- a list survives the first block
      unconditionally, and a dict is refused by it before change_all is reached.
      Decide the fix: fold move's to/from requirement into a move-specific
      branch of the primary check, or make the primary check accept a dict for
      instructions that declare change_all.
- [ ] T2 | Add a test: a move whose change is a dict missing 'to' is refused FOR
      THAT REASON (not for being the wrong type), proving change_all can
      actually be the decisive check once fixed.
