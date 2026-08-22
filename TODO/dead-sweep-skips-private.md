# dead_sweep skips every _private name, so a dead module constant is invisible to it and to ruff

```
Status:   open
Progress: 0 of 5 tasks done
Owner:    comment-review
Requires-Roy: false
Raised:   2026-08-22 (found while collapsing the Foliation fields 2026-08-22:
          page._SHEBANG and page._CODING are dead and neither gate reports them)
```

## Objective

dead_sweep skips every _private name, so a dead module constant is invisible to it and to ruff.

## Tasks

- [ ] MEASURED 2026-08-22: dead_sweep.py:217 reads if name.startswith("_") or name
      == "main": continue, documented at :194 as deliberate -- so no _private name
      is ever reported
- [ ] page._SHEBANG and page._CODING (page.py:793-794) are defined and read
      nowhere; git show HEAD~1 gives 2 occurrences, both the definitions. Ruff
      does not see a module-level constant either, which is the exact gap
      CLAUDE.md cites the sweep as covering
- [ ] * RULING: is the skip right? A _private name is by definition read only
      inside its own module, which is what makes it CHEAPER to check, not harder
      -- the opposite of the reason given for skipping main
- [ ] Decide whether the two constants are deleted or wanted; they were left in
      place by the change that noticed them
- [ ] MEASURED 2026-08-22, a SECOND blind spot and the same cause: the sweep
      matches a name TEXTUALLY, so a name appearing inside an unrelated identifier
      counts as a use. Foliation.first_code_line and Foliation.last_code_line
      (foliator.py:623, :633) have NO caller in plugins/, scripts/ or tests/ --
      the only hits are the test METHOD NAMES
      test_the_gap_ABOVE_the_first_code_line_inserts_above_it and
      test_the_gap_BELOW_the_last_code_line_appends, which are prose about a gap
      and never call either method. ! The sweep reports them as held by a test. !
      Noticed while collapsing Foliation to three fields and LEFT IN PLACE; they
      were already dead before that change.
