# dead_sweep skips every _private name, so a dead module constant is invisible to it and to ruff

```
Status:   open
Progress: 0 of 4 tasks done
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
