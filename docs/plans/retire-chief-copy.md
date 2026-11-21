# Retire the chief copy artifact

```
Status:   closed
Progress: 2 of 2 TODO tasks closed
Plan-tasks: 2 of 2 plan tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-11-21 (rebuilt-middle-final-review.md)
```

## Objective

Commit decided places to the proof and remove chief-copy synthesis and CLI
output

## TODO tasks this plan closes

### A - [rebuilt-middle-final-review](../../TODO/rebuilt-middle-final-review.md)

- [x] T56 | Decide whether Fold._unwritable refuses a place through the chief
      copy or the docket
- [x] T30 | Decide what the chief's copy is on a turn; it is built every turn
      and never saved (C6)

## Plan Tasks

- [x] P1 | Fold and bus no longer synthesize chief marks. Full suite passed. | 4d43e9fef2460f704c2084d2a189a100eef7b115 | Remove
      chief-copy synthesis from the fold and bus
- [x] P2 | Commands and skill use proof output. End-to-end smoke passed. | 4d43e9fef2460f704c2084d2a189a100eef7b115 | Remove
      chief-copy output from the CLI workflow
