# The middle-chain smoke script carries the findings of its Task 8 review

```
Status:   open
Progress: 1 of 12 tasks closed
Owner:    systems
Requires-Roy: false
Raised:   2026-09-11 (review of SP7 Task 8 at 34aea6d4, 2026-09-11)
```

## Objective

The middle-chain smoke script carries the findings of its Task 8 review.

## Tasks

- [ ] T1 | Update smoke_middle.ps1:35 so a relative -Run resolves against the
      caller's location, not the process directory
        > 2026-09-11 probed: -Run scripts from elsewhere named the repo dir
        > 2026-09-11 at 38671d29 an absolute -Run is refused as inside the repo
- [ ] T2 | Update smoke_middle.ps1:58 so a failed stage prints a command that
      runs when pasted, and its working directory
- [ ] T3 | Update smoke_middle.ps1 so a missing executable is reported by the
      stage helper, naming the stage and command
        > 2026-09-11 probed: renamed exe gave not-recognized, no stage line
- [ ] T4 | Update the helper at smoke_middle.ps1:55 so a stage can expect a code
      other than 0, as collate must expect 4
        > 2026-09-11 Task 9 needs it: spec c7ec4932 wants collate at 4
        > 2026-09-11 at dccdbcb5 expecting 4 and getting 0 still exits 0
- [ ] T5 | Update smoke_middle.ps1:53 so a one-element command line does not
      throw under strict mode
- [ ] T6 | Update smoke_middle.ps1 so the stage names at :23 and the stage
      blocks at :71 cannot fall out of step
        > 2026-09-11 at 0c7f3e44 the note at :110 still names $StageOrder
- [ ] T7 | Update the header at smoke_middle.ps1:1-3 and the note at :69-70 as
      stages are added past distribute
- [ ] T8 | Update smoke_middle.ps1 so the launcher prefix at :82, :88, :93 and
      :99 is written once
- [ ] T9 | Update smoke_middle.ps1:54 so command output goes to the console
      rather than into the script's output
- [ ] T10 | Update smoke_middle.ps1:33 so two runs started in the same second
      get different default directories
- [ ] T11 | Update smoke_middle.ps1:25 so an empty -Stop is refused rather than
      running every stage
- [x] T12 | RULED -- flags stay at call sites; spec reworded to names only | 440f4f2e | Decide
      whether flags join the command table, as the spec says at line 187, or
      stay at call sites as the script has them
        > 2026-09-11 the script follows a ruling in the SP7 ledger
