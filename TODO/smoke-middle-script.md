# The middle-chain smoke script carries the findings of its Task 8 review

```
Status:   open
Progress: 9 of 19 tasks closed
Owner:    systems
Requires-Roy: true
Raised:   2026-09-11 (review of SP7 Task 8 at 34aea6d4, 2026-09-11)
```

## Objective

The middle-chain smoke script carries the findings of its Task 8 review.

## Tasks

- [x] T1 | absolute and relative -Run resolve; inside the repo refused | 441af97a | Update
      smoke_middle.ps1:35 so a relative -Run resolves against the caller's
      location, not the process directory
        > 2026-09-11 probed: -Run scripts from elsewhere named the repo dir
        > 2026-09-11 at 38671d29 an absolute -Run is refused as inside the repo
- [ ] T2 | Update smoke_middle.ps1:58 so a failed stage prints a command that
      runs when pasted, and its working directory
        > 2026-09-11 review: a quoted exe and args with $ ; ( ) do not paste
- [x] T3 | a missing executable prints the stage line, exits 1 | b680577e | Update
      smoke_middle.ps1 so a missing executable is reported by the stage helper,
      naming the stage and command
        > 2026-09-11 probed: renamed exe gave not-recognized, no stage line
- [x] T4 | every expected-code mismatch exits non-zero | f5ad90f0 | Update the
      helper at smoke_middle.ps1:55 so a stage can expect a code other than 0,
      as collate must expect 4
        > 2026-09-11 Task 9 needs it: spec c7ec4932 wants collate at 4
        > 2026-09-11 at dccdbcb5 expecting 4 and getting 0 still exits 0
- [x] T5 | a bare one-element command runs under strict mode | 4a9ed92a | Update
      smoke_middle.ps1:53 so a one-element command line does not throw under
      strict mode
- [x] T6 | one ordered stages table drives order and -Stop | 4df10f7d | Update
      smoke_middle.ps1 so the stage names at :23 and the stage blocks at :71
      cannot fall out of step
        > 2026-09-11 at 0c7f3e44 the note at :110 still names $StageOrder
- [ ] T7 | Update the header at smoke_middle.ps1:1-3 and the note at :69-70 as
      stages are added past distribute
        > 2026-09-11 review: a new stage also needs a path variable near :107
- [x] T8 | the launcher prefix is defined once | a40a4a49 | Update
      smoke_middle.ps1 so the launcher prefix at :82, :88, :93 and :99 is
      written once
- [x] T9 | an in-process capture holds only the run path | 6a62edbe | Update
      smoke_middle.ps1:54 so command output goes to the console rather than into
      the script's output
- [ ] T10 | Update smoke_middle.ps1:33 so two runs started in the same second
      get different default directories
        > 2026-09-11 review: 4 of 7 simultaneous pairs shared a name
- [x] T11 | an empty -Stop is refused | 75febc65 | Update smoke_middle.ps1:25 so
      an empty -Stop is refused rather than running every stage
- [x] T12 | RULED -- flags stay at call sites; spec reworded to names only | 440f4f2e | Decide
      whether flags join the command table, as the spec says at line 187, or
      stay at call sites as the script has them
        > 2026-09-11 the script follows a ruling in the SP7 ledger
- [ ] T13 | Update smoke_middle.ps1:165 so an in-process caller's $LASTEXITCODE
      is 0 after a run that succeeded
- [ ] T14 | Update the note at smoke_middle.ps1:113 to say each stage block runs
      in its own scope
- [ ] T15 | Update the helper comment at smoke_middle.ps1:68-76, which claims
      more than a failure prints
        > 2026-09-11 missing-exe path prints no codes; pwsh -File puts output on stdout
- [ ] T16 | Update smoke_middle.ps1:36 so a relative -Run from a non-filesystem
      location is refused, not thrown
- [ ] T17 | Update smoke_middle.ps1:36 so a -Run starting with ~ expands to the
      home directory
- [ ] T18 | Update the -Stop refusal at smoke_middle.ps1:150 so an empty value
      reads as empty
- [?] T19 | Decide whether a run may write gitignored __pycache__ folders inside
      the repo
        > 2026-09-11 review: predates Task 8a; .gitignore:18 covers them
