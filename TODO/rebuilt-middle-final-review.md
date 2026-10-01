# The rebuilt middle's final review

```
Status:   open
Progress: 22 of 52 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-09-18 (final whole-branch review of feat/the-middle-rebuilt, 2026-09-18)
```

## Objective

The rebuilt middle's final review.

## Tasks

- [x] T1 | AnswerRow.reaches_partner: a mover's withdrawal reaches its move's other end; refuse_half_moves; Process 188 to 190; tests/test_passes.py, test_bus.py | 9ee20904 | Fix
      a mover's answer at one end of a move so it reaches the other; refuse a
      commit that leaves a move half done (B1, Broken)
- [x] T2 | two patches composed and settled reach the docket through proof --proof; tests/test_revise.py TestDocketOfProof; the chief's copy is no longer an input | af3e115d | Fix
      a chief mark synthesized over patch-only sides so it parses; it is a
      correct with no sources today (H1, Broken)
- [x] T3 | drift_in deleted with its tests per Process 185; every surviving drift statement corrected | ae7a45be | Decide
      whether drift_in goes per Process 62 or 62 is superseded; it voids the
      round today (D3, Broken)
- [x] T4 | Row.places and Row.names_destination are the one statement of which places a mark writes at; touched_by, _touched and the claim.to reads are gone; the gate holds the doc's key to the row | e0a39ccb | Make
      the marks row say where a two-place mark's other end is; five sites read
      claim.to and one function is written twice (A1, A2)
- [ ] T5 | Move who owes raw_text from flows/fill.py into the two rows that
      carry it, so check applies it to a hand-written copy (A3)
- [x] T6 | a taken_in naming copy-chief is refused by name, not a KeyError | 2a5e2730cee1049f22ecf0bc8f2e243c204afb98 | Fix
      a taken_in naming copy-chief: disposition exits on a KeyError; the row
      should say which sides it admits (A4)
- [-] T7 | Place.partner is gone; an end is no longer carried forward by its partner (Process 195) | 0e15fbb1f2f4e3dedf85cde8a26e7a611eecee0c | Fix
      an end carried forward by its partner: it is sent a slot whose answers are
      stored and ignored (B2)
- [-] T8 | A held move is one aggregate and emits one entry; human queries move before the fold (Process 197) | f95537fea2a2f029ea53bdb1712d82837f600a43 | Fix
      a held move queried at both ends so the one entry carries both; the second
      never reaches the author (B3)
- [x] T9 | Process 196: two moves onto one place are two placements; texts compose | 0b17ff17200a4cf901677700087daa5467f7c37c | Decide
      what two moves onto one place are; Place.partner holds one address so the
      first origin goes unpaired (B4)
        > 2026-09-26 Process 195: the move is one aggregate; composite TODO T27
- [x] T10 | the chief copy holds settled places only; composed text stays on the proof | 2a5e2730cee1049f22ecf0bc8f2e243c204afb98 | Fix
      collate writing composed and contested text to the chief's copy and
      printing it as resolved (C1)
- [x] T11 | flows/transcribe.py docket_of_proof and proof --proof read the closed proof's decided places (Process 184); dockets byte-identical to --copy on the smoke | 8f6d0fd3 | Make
      docket_of read the proof's decided places, as the design says, not re-fold
      the chief's marks (C2)
- [ ] T12 | Move desk's two binder imports out: collator.py takes a Binder,
      containers.py a private binder name (D1)
- [ ] T13 | Correct 'no handler reads a page' in flows/bus.py and
      docs/the-turn.md; the collate path reads pages under review (D2)
- [x] T14 | Process 186: the prose says a short shard and an unruled place roll the round back; verify.py and mark_errors.py corrected | b4846ba9 | Decide
      whether coverage and an unruled place void the round; Process 63, 112 and
      133 are reversed with no ruling (D4)
- [x] T15 | the fold's base is the page's text per Process 187; flows/on_the_page.py is the one page reader; mark, check and collate refuse the ungathered move | 2cc1dfed | Decide
      which base the fold composes over; Process 125 says the page and the bus
      hands it the binder's text (D5)
- [ ] T16 | Move the ten rules held in flows and commands into desk, and hold
      check's pre-fold list equal to the bus's (D6)
- [ ] T17 | Delete Row.answers or give it a reader; three docs call it a rule
      and only a test reads it (E1)
        > 2026-09-30 Criteria: docs/reviews/2026-09-30-r6-r7-r8.md, Row.answers
- [ ] T18 | Correct docstrings that describe the old design as live:
      master_proof_of, mark.parse, Revisit.unreadable (F1)
        > 2026-09-25 Revisit.unreadable went with T43; the rest of F1 stands
- [x] T19 | disposition docstring and help say taken_in | 2a5e2730cee1049f22ecf0bc8f2e243c204afb98 | Correct
      disposition --help: it says taken-in and the parse accepts taken_in only
      (G1)
- [ ] T20 | Correct the advisory heading in commands/collate.py so it names no
      row (A5)
- [ ] T21 | Note what the tables gate does not catch: single quotes, instruction
      strings, Shape, Touch, a one-row property (A6)
- [ ] T22 | Move chief_mark out of the gate-exempt table module or narrow the
      exemption; ninety lines of non-row logic (A7)
        > 2026-09-30 Criteria: docs/reviews/2026-09-30-r6-r7-r8.md, item 4
- [ ] T23 | Define stands once; it means nothing proposed, a lone proposal
      nobody is owed, and closed by the chief (B5)
- [ ] T24 | Decide whether a reader that answered clean becomes a side and is
      then asked an escalation (B6)
- [ ] T25 | Make answers_pass keep the sides on unsettlable as marks_pass does
      (B7)
        > 2026-09-30 Process 197 conflicts; see docs/reviews/2026-09-30-r2-r3.md
- [-] T26 | Process 195 narrowed 139: the chief rules words per end; the pair coupling this named is gone | 0e15fbb1f2f4e3dedf85cde8a26e7a611eecee0c | Correct
      the design's 'never ruled apart'; Process 139 lets the chief rule a move's
      ends apart (B8)
        > 2026-09-26 Process 195: apart on words, once on placement
- [ ] T27 | Give rollback one producer; the bus builds two without a Fold and
      commands/collate.py a third (C3)
- [ ] T28 | Carry the counts and the turn on an event; two commands re-derive
      them from serialized places (C4)
- [ ] T29 | Make one renderer for a refusal line; it is spelled at seven sites
      (C5)
- [ ] T30 | Decide what the chief's copy is on a turn; it is built every turn
      and never saved (C6)
        > 2026-09-30 Purpose ruled 184; implementation: collate-flow-defects T17
- [x] T31 | places and moves typed, read once, every bad entry named; tests failed first | cfec876a | Make
      MasterProof.places typed, and stop encoding a role into reasons, notes and
      asking as strings (D7)
- [ ] T32 | Delete what nothing reads: AnswerRow.question, three event fields,
      desk/proof.py, diff3, tally, mark --anchor-line (E2)
- [ ] T33 | Reduce rules stated twice: mismatched roots, the copy-chief string,
      marks by role, a ruling refused twice (E3)
- [ ] T34 | Correct flows.revise.docket_of to flows.transcribe.docket_of on five
      lines of four shipped files and two tests (F2)
- [ ] T35 | Correct scripts/render_brief.py lines 7 and 103: INSTRUCTIONS is in
      desk/marks/table.py (F3, systems lane)
- [ ] T36 | Correct the nine imprecise statements in docs/the-turn.md that the
      final review lists (G2)
- [ ] T37 | Correct docs/the-mark.md line 237: sixteen things is fifteen since
      rereads went (G3)
- [ ] T38 | Delete the-turn.md's 'a run cannot spin'; no code holds a cap, so
      nothing can check it (G4)
- [x] T39 | check --contract names raw_text and the rows that write it | 2a5e2730cee1049f22ecf0bc8f2e243c204afb98 | Publish
      raw_text in the mark's contract for add and move; check --contract omits
      it (G5)
- [ ] T40 | Measure a place the binder does not hold: an add or move there
      passes collate and is first refused at proof (H2)
- [x] T41 | the smoke's main line runs a second turn; store.py plants a contested move its mover withdraws, the sentence landing once | baed3d73 | Add
      a smoke plant of a move answered by its mover across two turns; B1, B2 and
      B4 sat outside the smoke (H3)
- [x] T42 | proof --only (Process 192); compaction is a stage: Stage cap, series and admits, desk/stages.py deals, collate holds marks to the row (Process 193); the compact command removed | eaf52803 | Implement
      compaction onto a closed proof's places and a place filter on proof, per
      Process 191 and 192
- [x] T43 | Revisit.unreadable deleted with its writers; the two claims its tests carried are tested again | b4be6db2 | Delete
      Revisit.unreadable; nothing outside the tests reads it (E2, Roy
      2026-09-25)
- [x] T44 | reading.addresser.folded compares destination to address; cad7f7d1 | cad7f7d1382eb5d7a8988a20b9cd43b3be1688a5 | Fix
      a move to its own paragraph spelled in another path case: it passes and
      the write end deletes the paragraph (code-review 2026-09-25)
- [x] T45 | a move is keyed by its own two addresses; two out of one origin are two moves | 29b3e6931a00471f692374897f4ead9910639c72 | Pair
      a move's two ends on the filing, not the place; two moves out of one
      origin leave the first unpaired (code-review 2026-09-25)
        > 2026-09-26 Process 195: the pair lives on the move aggregate; T27 there
- [ ] T46 | Correct events.py so AsksTheHuman is said to come before the fold,
      not from Fold.run; verify the module docstring says so
        > 2026-09-30 Evidence: docs/reviews/2026-09-30-r2-r3.md, R2-C
- [ ] T47 | Make stage reports own events emitted before and during a fold
        > 2026-09-30 Criteria: docs/reviews/2026-09-30-r2-r3.md, R2-C
- [ ] T48 | Make identical edits compose once while retaining genuine conflicts
        > 2026-09-30 Criteria: docs/reviews/2026-09-30-r2-r3.md, R3-A
- [x] T49 | Same-role equal filings and two-origin moves retain original identities through reload | 7b6ca44a21e1f41ba8b81a69ddbbf85846c806ee | Make
      a role convergent marks and moves compose without discarding their
      identities
        > 2026-09-30 Criteria: docs/reviews/2026-09-30-r2-r3.md, R3-B
- [ ] T50 | Make a composition deferral remove the answering role stale side
        > 2026-09-30 Criteria: docs/reviews/2026-09-30-r2-r3.md, R3-C
- [ ] T51 | Give place and placement answers exhaustive effect contracts with
      explicit deferral
        > 2026-09-30 Criteria: docs/reviews/2026-09-30-r2-r3.md, R3-D
- [ ] T52 | Reject undecided chief-synthesis input before selecting a filed
      clean or query mark
        > 2026-09-30 Criteria: docs/reviews/2026-09-30-r6-r7-r8.md, item 4
