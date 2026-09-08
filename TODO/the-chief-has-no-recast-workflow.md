# The copy chief has no workflow for recasting the places that never settled

```
Status:   open
Progress: 0 of 5 tasks closed
Owner:    backend
Requires-Roy: true
Raised:   2026-09-08 (Roy 2026-09-08: implementing the recast workflow for the cli the
          copy-chief uses to resolve the final pieces is a good todo, and cap is a bad
          name for it)
```

## Objective

The copy chief has no workflow for recasting the places that never settled.

## Tasks

- [ ] T1 | Update cap so a recast keeps the instruction the roles filed rather
      than writing every one as a correct
        > 2026-09-08 It is refused, not repaired -- Process 108; it waits on T2
- [ ] T2 | Implement the chief's recast end to end: its own prose at a place,
      reachable when a compose refused
- [ ] T3 | Verify the docket records the chief as who set a recast, which
      rule_at_cap already sides as CHIEF
- [ ] T4 | Implement the count a run reports: how many recasts were made, and
      how many landed on an empty place
        > 2026-09-08 claude-settings: 2 recasts of 13 carried; one was the lost add
- [?] T5 | Decide what the chief's command is called, since cap names the
      condition that triggers it rather than the act
