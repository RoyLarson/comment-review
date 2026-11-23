# The P5 self-run findings

```
Status:   open
Progress: 4 of 6 tasks closed
Owner:    systems
Requires-Roy: false
Raised:   2026-09-27 (P5 self-run stage 8, 2026-09-27)
```

## Objective

The P5 self-run findings.

## Tasks

- [x] T1 | Stage-8 findings fixed on both pages; differences.py code PROVEN unchanged | d336d460133770c007444b2616dfc3f89d788a95 | Fix
      the stage-8 findings on differences.py and check_vocabulary.py; verify a
      reread finds each section reads as one
- [-] T2 | SUPERSEDED by T6: drop rewraps through Fragment.cut since 568fc4f4/862cb59d; correct does not | 22c3a0abcbc86509c74296319ce5b719a43338ca | Implement
      rewrapping of a paragraph whose correct or drop leaves a ragged line or
      stub; backend
        > 2026-11-08 Outside run, beta.7: a 4-space join gap and a fragment were written
- [x] T3 | FINISHED -- a TODO names its action; the ruling does not restate it | c3a088cd | Update
      the brief so a code-concern TODO names an action and the paragraph ruling
      does not restate it; agents
- [x] T4 | FINISHED -- the chief reads each composed paragraph whole | c3a088cd | Update
      SKILL.md so the chief reads each composed paragraph whole before ruling;
      agents
        > 2026-11-08 Outside run, beta.7: 7 lost referents in composed text got past
- [ ] T5 | Fix referrers matching every file that mentions main when a page
      defines a public main; backend
- [ ] T6 | Rewrap a paragraph whose `correct` leaves a ragged line, as
      Fragment.cut does for a drop
        > 2026-11-22 Check: a longer correct replacement rewraps its run
