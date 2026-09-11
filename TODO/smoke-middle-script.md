# The middle-chain smoke script carries the findings of its Task 8 review

```
Status:   open
Progress: 32 of 58 tasks closed
Owner:    systems
Requires-Roy: false
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
- [x] T7 | the header and stage note describe the script through diff | 4279b443 | Update
      the header at smoke_middle.ps1:1-3 and the note at :69-70 as stages are
      added past distribute
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
        > 2026-09-11 review 10: rewritten at smoke_middle.ps1:79-83, still overclaims
- [ ] T16 | Update smoke_middle.ps1:36 so a relative -Run from a non-filesystem
      location is refused, not thrown
- [ ] T17 | Update smoke_middle.ps1:36 so a -Run starting with ~ expands to the
      home directory
- [ ] T18 | Update the -Stop refusal at smoke_middle.ps1:150 so an empty value
      reads as empty
- [x] T19 | RULED -- no permanent code changes inside the repo; pycache allowed | e30f48ad | Decide
      whether a run may write gitignored __pycache__ folders inside the repo
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
- [x] T32 | each landing states its outcome, what decides it, its line | 520446ff | Update
      the plant so every planted outcome is written in one place at plant time,
      for Task 10's diff
        > 2026-09-11 texts at :205 :224 :315 :336; sides in smoke_fixture.py:90-128
        > 2026-09-11 review: None means both removed (b14, b1) and kept (a3, a1)
        > 2026-09-11 review: c6 and c1 hold a clause; their old wording is in the ps1
        > 2026-09-11 review: empty places and added blank lines are not in the table
        > 2026-09-11 review 9b: smoke_middle.ps1:311 spells c1's false clause inline
        > 2026-09-11 review 9b: a3, a1, b14, b1 default to route mark
        > 2026-09-11 review 9b: c1, a3 and the adds are decided by disposition too
        > 2026-09-11 review 9b: b0's position and b17's trailing blank are outside it
- [ ] T33 | Implement a test in test_smoke_fixture.py that calls write_texts,
      which no test calls today
- [x] T34 | the docstring says three escalations and six re-reads | d2648ffc | Update
      smoke_fixture.py:12-13, which says DISPOSITIONS rules each place collate
      escalates; six of nine are re-reads
- [x] T35 | the comment counts nine carried places from DISPOSITIONS | d2648ffc | Update
      smoke_middle.ps1:440-443, which counts four carried places where there are
      nine and names LANDINGS as their source
- [x] T36 | the clean comment names a0 and c12's adds | d2648ffc | Update
      smoke_middle.ps1:167-168, which says every unnamed place is clean from all
      four; a0 and c12 now take an add
- [ ] T37 | Update smoke_fixture.py:84-87 and smoke_middle.ps1:164-166, which
      equate the plant with the spec matrix it goes beyond
        > 2026-09-11 review 9b: the matrix names no addresses; the new text says nine
        > 2026-09-11 review 10: still at smoke_middle.ps1:190-191, fixture :137-138
- [x] T38 | the move is described as carrying b1 unchanged | d2648ffc | Update
      smoke_fixture.py:101, which says the move is reworded when b0 carries b1's
      text unchanged
- [x] T39 | c6's comment names the three queries beside the correct | d408ebc0 | Update
      smoke_fixture.py:96, which calls c6's correct the only mark when three
      roles also mark query there
- [x] T40 | the shell-rule comment matches mark.py:11-18 | d408ebc0 | Update
      smoke_fixture.py:222-224, which says every value goes by file;
      mark.py:11-18 sends a clause inline
- [x] T41 | the c12 and a0 reasons name all four roles | d2648ffc | Update the
      c12 and a0 reasons at smoke_fixture.py:203 and :209, which say one role
      alone read a place four read
- [x] T42 | the table comment no longer claims Task 10 exists | d2648ffc | Update
      smoke_fixture.py:92-94, which says in the present tense that Task 10 diffs
      against the table
- [x] T43 | the module docstring names the decisions it holds | d2648ffc | Update
      smoke_fixture.py:7-8, which says a later task plants decisions this module
      now holds
- [x] T44 | the comment names six adds | d2648ffc | Update smoke_middle.ps1:404,
      which calls a2 the add when the plant has six
        > 2026-09-11 the rest of that comment is T26
- [x] T45 | b8 carries the four-space indent of logged's body | 878b55b7 | Update
      the b8 landing text at smoke_fixture.py:121 so it carries the four-space
      indent of logged's body
        > 2026-09-11 probe: lands at column 0 above return wrapper; reviewer-brief :198
- [ ] T46 | Update smoke_fixture.py:110 and test_smoke_fixture.py:88, which cite
      desk.mark.claim_change for derived_change
- [ ] T47 | Update smoke_fixture.py:18-20 and :288-289, which say every route
      mark entry gets a file; kept and removed ones do not
- [ ] T48 | Update smoke_fixture.py:101-104, which says write_texts writes text
      for route mark; for c6 and c1 it writes clauses
        > 2026-09-11 review 10: smoke_fixture.py:103-104 says text goes as --true
- [ ] T49 | Update smoke_fixture.py:13 and :109, which write IS in capitals for
      stress
        > 2026-09-11 review 10: the rewritten docstring keeps IS at :14
- [ ] T50 | Update smoke_fixture.py:156, which calls a2's text the add's
      --change as T44 corrected in the script
- [ ] T51 | Update the agreement test in test_smoke_fixture.py to call
      derived_change rather than str.replace
        > 2026-09-11 replace swaps every occurrence; derived_change refuses a repeat
- [ ] T52 | Update the b17 entry, which cites Addressing 19 for the foot rule
      that only compositor.py:298-305 states
        > 2026-09-11 #19 covers the blank before an added b, not the one after
- [ ] T53 | Update the diff stage to run git with core.autocrlf=false, so a
      line-ending difference fails it
        > 2026-09-11 review 10: a CRLF expectation passed under the system autocrlf
        > 2026-09-11 header :6-7 and :526 claim an exactness the stage lacks
- [ ] T54 | Update the line test at test_smoke_fixture.py:121-138 so a wrong
      line on a b entry fails it
        > 2026-09-11 at_line(n, b) answers one gap for every line down to its code
- [ ] T55 | Update smoke_fixture.py:383 and :387 so write_text is never handed
      str or None
        > 2026-09-11 ty reports both when pointed at scripts/; no None reaches it
- [x] T56 | RULED Process: #114 -- no; scripts are convenience | bd850467 | Decide
      whether ty's scope in pyproject.toml:170-171 takes in scripts/, which it
      skips today
- [ ] T57 | Update smoke_middle.ps1:456 to read the addresser row's line from
      LANDINGS, not a second copy
- [ ] T58 | Update the addresser stage so an address other than the planted one
      fails there, not at mark
        > 2026-09-11 by reading: a wrong address fails at the next @path or disposition
