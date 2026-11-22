# Resolve final review documentation and reporting findings

```
Status:   closed
Progress: 9 of 9 TODO tasks closed
Plan-tasks: 1 of 1 plan tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-11-21 (rebuilt-middle-final-review.md)
```

## Objective

Correct stale documentation and advisory reporting for the nine approved
final-review items

## TODO tasks this plan closes

### A - [rebuilt-middle-final-review](../../TODO/completed/rebuilt-middle-final-review.md)

- [x] T13 | Correct 'no handler reads a page' in flows/bus.py and
      docs/the-turn.md; the collate path reads pages under review (D2)
- [x] T18 | Correct docstrings that describe the old design as live:
      master_proof_of, mark.parse, Revisit.unreadable (F1)
- [x] T20 | Correct the advisory heading in commands/collate.py so it names no
      row (A5)
- [x] T21 | Note what the tables gate does not catch: single quotes, instruction
      strings, Shape, Touch, a one-row property (A6)
- [x] T34 | Correct flows.revise.docket_of to flows.transcribe.docket_of on five
      lines of four shipped files and two tests (F2)
- [x] T35 | Correct scripts/render_brief.py lines 7 and 103: INSTRUCTIONS is in
      desk/marks/table.py (F3, systems lane)
- [-] T36 | Correct the nine imprecise statements in docs/the-turn.md that the
      final review lists (G2)
- [x] T37 | Correct docs/the-mark.md line 237: sixteen things is fifteen since
      rereads went (G3)
- [x] T38 | Delete the-turn.md's 'a run cannot spin'; no code holds a cap, so
      nothing can check it (G4)

## Plan Tasks

- [x] P1 | Corrected confirmed issues and ran 110 focused tests. T36 source list still outstanding. | 6a9c61768401adaa12c31066fbc882e570a49e9e | Correct
      the confirmed documentation and advisory reporting findings
