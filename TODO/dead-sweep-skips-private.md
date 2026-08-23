# dead_sweep skips every _private name, so a dead module constant is invisible to it and to ruff

```
Status:   decision-needed
Progress: 4 of 5 tasks done
Owner:    systems
Requires-Roy: true
Raised:   2026-08-22 (found while collapsing the Cues fields 2026-08-22:
          page._SHEBANG and page._CODING are dead and neither gate reports them)
RE-CHECKED: 2026-08-23 — 2026-08-23. Tasks 2, 4 and 5 were resolved by other work:
            page._SHEBANG and page._CODING are deleted, and Cues.first_code_line /
            last_code_line are gone from the scripts -- the only surviving hits are the
            two test METHOD NAMES the task itself identified as prose about a gap rather
            than callers. Task 1 is a measurement and still true (dead_sweep.py:217
            skips every _private name); it belongs to the Objective, which already
            states it. ! WHAT IS LEFT IS THE RULING in task 3, and nothing else.
```

## Objective

dead_sweep skips every _private name, so a dead module constant is invisible to it and to ruff.

## Tasks

- [x] MEASURED 2026-08-22: dead_sweep.py:217 reads if name.startswith("_") or name
      == "main": continue, documented at :194 as deliberate -- so no _private name
      is ever reported
- [x] page._SHEBANG and page._CODING (page.py:793-794) are defined and read
      nowhere; git show HEAD~1 gives 2 occurrences, both the definitions. Ruff
      does not see a module-level constant either, which is the exact gap
      CLAUDE.md cites the sweep as covering
- [ ] * RULING: is the skip right? A _private name is by definition read only
      inside its own module, which is what makes it CHEAPER to check, not harder
      -- the opposite of the reason given for skipping main
- [x] Decide whether the two constants are deleted or wanted; they were left in
      place by the change that noticed them
- [x] MEASURED 2026-08-22, a SECOND blind spot and the same cause: the sweep
      matches a name TEXTUALLY, so a name appearing inside an unrelated identifier
      counts as a use. Cues.first_code_line and Cues.last_code_line
      (addresser.py:623, :633) have NO caller in plugins/, scripts/ or tests/ --
      the only hits are the test METHOD NAMES
      test_the_gap_ABOVE_the_first_code_line_inserts_above_it and
      test_the_gap_BELOW_the_last_code_line_appends, which are prose about a gap
      and never call either method. ! The sweep reports them as held by a test. !
      Noticed while collapsing Cues to three fields and LEFT IN PLACE; they
      were already dead before that change.
