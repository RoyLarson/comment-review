# The rebuilt middle's final review

```
Status:   open
Progress: 5 of 42 tasks closed
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
- [ ] T3 | Decide whether drift_in goes per Process 62 or 62 is superseded; it
      voids the round today (D3, Broken)
- [ ] T4 | Make the marks row say where a two-place mark's other end is; five
      sites read claim.to and one function is written twice (A1, A2)
- [ ] T5 | Move who owes raw_text from flows/fill.py into the two rows that
      carry it, so check applies it to a hand-written copy (A3)
- [ ] T6 | Fix a taken_in naming copy-chief: disposition exits on a KeyError;
      the row should say which sides it admits (A4)
- [ ] T7 | Fix an end carried forward by its partner: it is sent a slot whose
      answers are stored and ignored (B2)
- [ ] T8 | Fix a held move queried at both ends so the one entry carries both;
      the second never reaches the author (B3)
- [ ] T9 | Decide what two moves onto one place are; Place.partner holds one
      address so the first origin goes unpaired (B4)
- [ ] T10 | Fix collate writing composed and contested text to the chief's copy
      and printing it as resolved (C1)
- [x] T11 | flows/transcribe.py docket_of_proof and proof --proof read the closed proof's decided places (Process 184); dockets byte-identical to --copy on the smoke | 8f6d0fd3 | Make
      docket_of read the proof's decided places, as the design says, not re-fold
      the chief's marks (C2)
- [ ] T12 | Move desk's two binder imports out: collator.py takes a Binder,
      containers.py a private binder name (D1)
- [ ] T13 | Correct 'no handler reads a page' in flows/bus.py and
      docs/the-turn.md; the collate path reads pages under review (D2)
- [ ] T14 | Decide whether coverage and an unruled place void the round; Process
      63, 112 and 133 are reversed with no ruling (D4)
- [ ] T15 | Decide which base the fold composes over; Process 125 says the page
      and the bus hands it the binder's text (D5)
- [ ] T16 | Move the ten rules held in flows and commands into desk, and hold
      check's pre-fold list equal to the bus's (D6)
- [ ] T17 | Delete Row.answers or give it a reader; three docs call it a rule
      and only a test reads it (E1)
- [ ] T18 | Correct docstrings that describe the old design as live:
      master_proof_of, mark.parse, Revisit.unreadable (F1)
- [ ] T19 | Correct disposition --help: it says taken-in and the parse accepts
      taken_in only (G1)
- [ ] T20 | Correct the advisory heading in commands/collate.py so it names no
      row (A5)
- [ ] T21 | Note what the tables gate does not catch: single quotes, instruction
      strings, Shape, Touch, a one-row property (A6)
- [ ] T22 | Move chief_mark out of the gate-exempt table module or narrow the
      exemption; ninety lines of non-row logic (A7)
- [ ] T23 | Define stands once; it means nothing proposed, a lone proposal
      nobody is owed, and closed by the chief (B5)
- [ ] T24 | Decide whether a reader that answered clean becomes a side and is
      then asked an escalation (B6)
- [ ] T25 | Make answers_pass keep the sides on unsettlable as marks_pass does
      (B7)
- [ ] T26 | Correct the design's 'never ruled apart'; Process 139 lets the chief
      rule a move's ends apart (B8)
- [ ] T27 | Give rollback one producer; the bus builds two without a Fold and
      commands/collate.py a third (C3)
- [ ] T28 | Carry the counts and the turn on an event; two commands re-derive
      them from serialized places (C4)
- [ ] T29 | Make one renderer for a refusal line; it is spelled at seven sites
      (C5)
- [ ] T30 | Decide what the chief's copy is on a turn; it is built every turn
      and never saved (C6)
- [ ] T31 | Make MasterProof.places typed, and stop encoding a role into
      reasons, notes and asking as strings (D7)
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
- [ ] T39 | Publish raw_text in the mark's contract for add and move; check
      --contract omits it (G5)
- [ ] T40 | Measure a place the binder does not hold: an add or move there
      passes collate and is first refused at proof (H2)
- [x] T41 | the smoke's main line runs a second turn; store.py plants a contested move its mover withdraws, the sentence landing once | baed3d73 | Add
      a smoke plant of a move answered by its mover across two turns; B1, B2 and
      B4 sat outside the smoke (H3)
- [x] T42 | proof --only (Process 192); compaction is a stage: Stage cap, series and admits, desk/stages.py deals, collate holds marks to the row (Process 193); the compact command removed | eaf52803 | Implement
      compaction onto a closed proof's places and a place filter on proof, per
      Process 191 and 192
