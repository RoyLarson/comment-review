# The middle-chain smoke script carries the findings of its Task 8 review

```
Status:   open
Progress: 17 of 45 tasks closed
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
- [x] T2 | the printed line starts with & and quotes unsafe arguments | 575054f7 | Update
      smoke_middle.ps1:58 so a failed stage prints a command that runs when
      pasted, and its working directory
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
        > 2026-09-11 review of 4ed781c0: :132-134 still says nothing else changes
- [x] T8 | the launcher prefix is defined once | a40a4a49 | Update
      smoke_middle.ps1 so the launcher prefix at :82, :88, :93 and :99 is
      written once
- [x] T9 | an in-process capture holds only the run path | 6a62edbe | Update
      smoke_middle.ps1:54 so command output goes to the console rather than into
      the script's output
- [x] T10 | distinct default names; a refused -Stop leaves nothing | de603166 | Update
      smoke_middle.ps1:33 so two runs started in the same second get different
      default directories
        > 2026-09-11 review: 4 of 7 simultaneous pairs shared a name
        > 2026-09-11 at 9cf500ae a refused -Stop leaves an empty run dir
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
- [x] T20 | the a2 docstring carries wrapper's eight-space body indent | ce10d1ee | Update
      the a2 add at smoke_middle.ps1:336 so its docstring carries the
      indentation wrapper's body needs
        > 2026-09-11 unindented, the proof's reread loses every altered cue
        > 2026-09-11 waits on the galley-and-compositor indentation ruling
        > 2026-09-11 unblocked: Addressing 27 gives indentation to the role
- [x] T21 | nothing writes recast_prose.txt; the prose rides inline | ce10d1ee | Delete
      recast_prose.txt from write_texts at smoke_fixture.py:146-147, which
      nothing reads
        > 2026-09-11 disposition takes no @path; the prose rides in dispositions.json
- [ ] T22 | Update smoke_middle.ps1:116-124 to find the copies distribute wrote
      rather than spell its file names
        > 2026-09-11 the spec's Coupling section rules out distribute's naming
- [ ] T23 | Update smoke_middle.ps1:164-165, which says the whole matrix is
      planted when the addresser row is not
- [x] T24 | RULED -- the end-to-end bar stands; a middle fault becomes a pytest test | d474bf15 | Decide
      whether the smoke must tell a row that should escalate from one that
      re-reads beside another
        > 2026-09-11 review: c1 turned re-read, a3 and b9 kept collate at 4
        > 2026-09-11 Roy 2026-09-08: no assertions on intermediate artifacts
- [ ] T25 | Update smoke_middle.ps1:166, which says mark refuses a bulk pass
      that mark has no mode for
- [ ] T26 | Update smoke_middle.ps1:329-330, which says wrapper has no slot in
      anyone else's copy when no copy has one
- [x] T27 | no comment cites the brief's table any more | ce10d1ee | Update
      smoke_middle.ps1:366 and smoke_fixture.py:86, :88, :134, which cite a
      table only the brief holds
        > 2026-09-11 the brief is gitignored scratch
- [x] T28 | the docstring names LANDINGS, DISPOSITIONS and write_texts | 03258d76 | Update
      the smoke_fixture.py docstring at :1-9 to account for RECAST_PROSE,
      DISPOSITIONS and write_texts
- [ ] T29 | Update smoke_middle.ps1:341-343, which says check applies the same
      boundary collate does
        > 2026-09-11 by exit code check is stricter: an escalation outranks coverage
- [x] T30 | nine mark calls read their landing text as @path | ce10d1ee | Implement
      one planted mark whose text goes to mark as @path, so the file expansion
      is exercised
- [ ] T31 | Update smoke_middle.ps1 so the role set at :120, :152 and :358-361
      is written once
- [ ] T32 | Update the plant so every planted outcome is written in one place at
      plant time, for Task 10's diff
        > 2026-09-11 texts at :205 :224 :315 :336; sides in smoke_fixture.py:90-128
        > 2026-09-11 review: None means both removed (b14, b1) and kept (a3, a1)
        > 2026-09-11 review: c6 and c1 hold a clause; their old wording is in the ps1
        > 2026-09-11 review: empty places and added blank lines are not in the table
- [ ] T33 | Implement a test in test_smoke_fixture.py that calls write_texts,
      which no test calls today
- [ ] T34 | Update smoke_fixture.py:12-13, which says DISPOSITIONS rules each
      place collate escalates; six of nine are re-reads
- [ ] T35 | Update smoke_middle.ps1:440-443, which counts four carried places
      where there are nine and names LANDINGS as their source
- [ ] T36 | Update smoke_middle.ps1:167-168, which says every unnamed place is
      clean from all four; a0 and c12 now take an add
- [ ] T37 | Update smoke_fixture.py:84-87 and smoke_middle.ps1:164-166, which
      equate the plant with the spec matrix it goes beyond
- [ ] T38 | Update smoke_fixture.py:101, which says the move is reworded when b0
      carries b1's text unchanged
- [ ] T39 | Update smoke_fixture.py:96, which calls c6's correct the only mark
      when three roles also mark query there
- [ ] T40 | Update smoke_fixture.py:222-224, which says every value goes by
      file; mark.py:11-18 sends a clause inline
- [ ] T41 | Update the c12 and a0 reasons at smoke_fixture.py:203 and :209,
      which say one role alone read a place four read
- [ ] T42 | Update smoke_fixture.py:92-94, which says in the present tense that
      Task 10 diffs against the table
- [ ] T43 | Update smoke_fixture.py:7-8, which says a later task plants
      decisions this module now holds
- [ ] T44 | Update smoke_middle.ps1:404, which calls a2 the add when the plant
      has six
        > 2026-09-11 the rest of that comment is T26
- [ ] T45 | Update the b8 landing text at smoke_fixture.py:121 so it carries the
      four-space indent of logged's body
        > 2026-09-11 probe: lands at column 0 above return wrapper; reviewer-brief :198
