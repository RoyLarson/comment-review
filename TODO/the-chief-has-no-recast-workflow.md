# The copy chief has no workflow for recasting the places that never settled

```
Status:   open
Progress: 5 of 10 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-09-08 (Roy 2026-09-08: implementing the recast workflow for the cli the
          copy-chief uses to resolve the final pieces is a good todo, and cap is a bad
          name for it)
```

## Objective

The copy chief has no workflow for recasting the places that never settled.

## Tasks

- [x] T1 | a recast keeps the instruction the roles filed, and _recast_claim shapes the claim to it | 2a5de914 | Update
      cap so a recast keeps the instruction the roles filed rather than writing
      every one as a correct
        > 2026-09-08 It is refused, not repaired -- Process 108; it waits on T2
        > 2026-09-08 The P14 wait was withdrawn 2026-09-08; this is the simple repair
- [ ] T2 | Implement the chief's recast end to end: its own prose at a place,
      reachable when a compose refused
        > 2026-09-08 Held for review after a run, per KISS; not a prerequisite for T1
- [ ] T3 | Verify the docket records the chief as who set a recast, which
      rule_at_cap already sides as CHIEF
- [ ] T4 | Implement the count a run reports: how many recasts were made, and
      how many landed on an empty place
        > 2026-09-08 claude-settings: 2 recasts of 13 carried; one was the lost add
- [x] T5 | RULED Vocabulary: #36 -- disposition; directive collides with topology and dispose reads as release | 6e770324 | Decide
      what the chief's command is called, since cap names the condition that
      triggers it rather than the act
- [ ] T6 | Update the command cap to disposition and rulings.json to
      dispositions.json, across the shipped prose and the gate
        > 2026-09-08 A plugins change needs a version bump, as the role rename does
- [x] T7 | Process 146: a correct from the original to the chief's prose | a4a132be | Decide
      what a recast of a drop should write, since change carries the chief's
      prose whatever the instruction says
        > 2026-09-08 Not new: the hardcoded correct wrote prose for every instruction
- [x] T8 | disposition.py and turn.py say nothing survives max turns without a disposition, per Vocabulary 36 | d1529b62 | Update
      disposition.py:20 and turn.py:621, which still say cap for max turns, per
      Vocabulary 36
        > 2026-09-11 seen in disposition --help while preparing SP7 Task 9
- [ ] T9 | Update the recast so the b9 mark in final.json does not carry the
      source fib.py:21 twice
- [x] T10 | a recast over a drop, and at a move origin, is a correct from the original paragraph to the prose, per Process 146 | e33c3ab0 | Update
      rule_at_max_turns so a recast over a drop is written as a correct from the
      original paragraph to the chief's prose, per Process 146
        > 2026-09-13 includes the recast at a move's origin, 0f9657a0
        > 2026-09-13 test: the claim's true is what lands; false is the original
