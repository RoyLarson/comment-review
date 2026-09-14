# The agents files name the new CLI and say how to use it

```
Status:   open
Progress: 26 of 33 tasks closed
Owner:    agents
Requires-Roy: false
Raised:   2026-09-04 (Roy, 2026-09-04, superseding the-flow-lives-in-the-command T4)
```

## Objective

The agents files name the new CLI and say how to use it.

## Tasks

- [-] T1 | SUPERSEDED in part by Process 94 -- SKILL.md runs collate --proof-out --batch-out and cap and puts the unsettlable to the author; turn is out for the baseline, its text is T6 | c1b7268a | Update
      SKILL.md to run collate --proof-out --batch-out, turn and cap, and ask the
      human the unsettlable places. Verify: a hand runs from it
        > 2026-09-04 docs/the-turn.md's one NOT built row; stage-5 T13 also asks it
- [-] T2 | SUPERSEDED in part -- the brief runs check over the copy; over answers is the turn's, T7 | 717a35cb | Update
      reviewer-brief.md so a role runs check over its copy and its answers
      before returning. Verify: the brief names both forms
- [-] T3 | SUPERSEDED -- the turn's answer shapes are the turn experiment's brief, T7 | 717a35cb | Update
      the reviewer brief with the turn's two answer shapes, escalation and
      composition, from check --contract. Verify: none hand-typed
- [x] T4 | RULED Process 94 -- the task agent is the copy chief at the cap; SKILL.md says so | c1b7268a | Decide
      who the copy chief is at the cap, the task agent or a role, so SKILL.md
      can say who writes rulings.json
- [x] T5 | FINISHED -- SKILL.md stage 4 and 5: a refused copy goes back to its role with the printed lines, never repaired | c1b7268a | Update
      SKILL.md so the task agent sends every refused copy or answer back to the
      role that owes it, to be fixed. Verify: the brief says so
        > 2026-09-04 Process 92: the errors stack; the task agent reroutes them
        > 2026-09-04 bound on send-backs: a-coverage-gap-should-go-back T2
- [-] T6 | SUPERSEDED by T23: the command is disposition since f2b8f988 | f2b8f988 | Update
      SKILL.md to run turn between collate and cap, for the experiment after the
      baseline. Verify: a hand with a turn runs from it
- [x] T7 | the brief says what a batch slot takes and how to check it | 3b0314e6 | Update
      reviewer-brief.md with check --answers and the two answer shapes from
      check --contract, for the turn experiment
        > 2026-09-11 check --answers now needs --proof, since 0f01d744
        > 2026-09-12 Roy 2026-09-12: joins set 4, the role's side of the turn
- [x] T8 | SKILL.md packet carries BINDER, LISTING, EDIT COPY as paths; the brief reads from them | d0c1e9b1 | Update
      SKILL.md and the brief so the packet names the binder, the listing and the
      copy by absolute path and a role reads from there
        > 2026-09-05 Process 95: told where binder and marks are, roles read there
- [-] T9 | the role body is the reviewer's system prompt, so the role and remit reach it; Roy 2026-09-05 | 3a82256b | Update
      the four role files so the body opens with the remit the description
      states, in the same words. Verify: grep Your remit hits four
        > 2026-09-05 the description reaches the dispatcher, never the reviewer
- [ ] T10 | Decide whether the brief and the vocabulary reach a role by path as
      the binder does, since four verbatim pastes did not fit one message
- [ ] T11 | Update reviewer-brief.md's move text to say a move relocates a whole
      place, never part of a paragraph. Verify: the from and to text says so
- [-] T12 | SUPERSEDED by Process 96: an add needs no include-absent binder once the lookup reads the page | 473afdba | Update
      SKILL.md stage 2 to gather with --include-absent, since an add needs an
      address for a gap. Verify: the gather line has the flag
- [ ] T13 | Update SKILL.md stage 6 to take a paragraph's kind from its binder
      row, not the listing, once the row carries it. Verify: no listing parse
- [ ] T14 | Update SKILL.md and the brief to say absent places are filtered out
      of the binder and are looked up with addresser. Verify: both say so
        > 2026-09-05 waits on binder-defects T22; the text would promise what fails now
        > 2026-09-05 the default filter stays; absent places are noise for a role
        > 2026-09-05 the brief asks by line number, no longer with the line's text
        > 2026-09-05 T22 landed; flag gate red on --anchor: SKILL 367, brief 231
- [x] T15 | FINISHED; the brief says a role may read its own draft with proof --copy | 70965ff4 | Update
      reviewer-brief.md so a role knows it may set its own edit copy with proof
      --copy and read the draft that pulls.
- [ ] T16 | Update SKILL.md 1.9 so the split per role is sized from the binder's
      place count, not fixed at one.
        > 2026-09-07 2026-09-06: 888 places per role over 71 pages exhausted a session.
- [x] T17 | SKILL.md stage 4 lets the roles go out together or one after another, per Process 102 | 23ef6352 | Update
      SKILL.md stage 4 so the roles may be dispatched sequentially: the topology
      and the copies isolate them, not one message.
        > 2026-09-07 decision-log.md Process: #102, Roy 2026-09-07.
- [x] T18 | the packet says the LSP answer is the task agent probe; the brief has a role without the tool grep | 07372c96 | Update
      the packet so the language-server answer says who can call it; three
      reviewers found no LSP tool and fell back to grep
        > 2026-09-07 OneDrive claude-settings/2026-09-07/README.md, Feedback section
- [-] T19 | SUPERSEDED by Addressing: #23 -- the compositor supplies leading, not the role; refiled as T20 | f850c321 | Update
      reviewer-brief.md to teach leading: an existing place's is restored, a
      newly filled place needs its own written
- [x] T20 | the brief asks for no leading blank at either end | 7d2e1834 | Update
      reviewer-brief.md so a role writes no leading blank at either end of a
      change. Verify: the brief asks for none
- [x] T21 | 7a compiles each drafted Python page with py_compile and names pages no compile step reached | 401e36de | Update
      SKILL.md so the task agent runs a compile step on the set page to verify
      it is set correctly
        > 2026-09-11 Addressing 27; Roy: we can have the task-agent run it
- [x] T22 | the collate exit table carries exit 7's row | 49066f15 | Update
      SKILL.md's collate exit table at :664-670 with a row for that code
        > 2026-09-11 Process 112; waits on collate-command-defects for the number
- [x] T23 | SKILL.md runs turn between collate and disposition when told | 25162cb6 | Update
      SKILL.md to run turn between collate and disposition, for the experiment
      after the baseline. Verify: a hand with a turn runs from it
- [x] T24 | Process 136: CLAUDE.md points to limitations.md instead | d3fe7151 | Decide
      which rule governs new skill prose: CLAUDE.md:376-377's replace-at-budget
      or limitations.md:46's earn-its-context
        > 2026-09-12 a brief quoted CLAUDE.md's; limitations.md has Roy, 2026-08-18
- [x] T25 | re-measured as stored blobs, with what set 4's growth bought | c2e64382 | Update
      docs/limitations.md's size table for SKILL.md and reviewer-brief.md as set
      4 left them
        > 2026-09-12 set 4: SKILL.md 60,979 bytes, reviewer-brief.md 38,688 bytes
- [x] T26 | proof --out holds only the drafted pages, per Process 117 | a2fce3ed | Update
      SKILL.md:885, which says proof's --out holds a full copy of --repo; since
      Process 117 it holds only the docket's pages
        > 2026-09-13 seen reading stage 7a for stage-5 T12
- [ ] T27 | Update reviewer-brief.md so <skill> at :126, 271, 580, 592 names a
      path the packet gives a reviewer. Verify: the packet list names it
        > 2026-09-13 from census T14, Process 147
        > 2026-09-13 SKILL.md:610-614 sends a role no path into the plugin
- [ ] T28 | Update reviewer-brief.md:592-593 so ANSWERS, BATCH and PROOF name
      what SKILL.md:712-713 hands a role. Verify: the two agree
        > 2026-09-13 from census T16, Process 147
- [x] T29 | 7a puts a held move to the author as one move; SKILL.md gives the lines disposition prints | dc06c677 | Update
      SKILL.md 7a so the task agent puts a held move's drop and add to the
      author as one move, per Process 155
- [x] T30 | SKILL.md, the brief and compact.md tell no agent to use a kind or annotations; compact keys on the place | fd846264 | Update
      SKILL.md, reviewer-brief.md and compact.md so no agent is told to use a
      paragraph's kind or annotations, per Process 158
- [x] T31 | stage 7b has proof set the approved text in temporary files for the author to diff | 6277bdd8 | Update
      SKILL.md and write.md so stage 7b writes the approved text to temporary
      files for the author to diff, per Process 159
- [x] T32 | SKILL.md, the brief and write.md match the CLI: 16 changes, merged at 626017b7 | 626017b7 | Update
      SKILL.md, reviewer-brief.md and write.md so every command, flag, exit code
      and output they name matches the CLI
- [x] T33 | write.md runs no prove_unchanged at 7b and restores no edit on its result | 6277bdd8 | Update
      write.md so stage 7b runs no prove_unchanged check and restores no edit on
      its result, per Process 160
