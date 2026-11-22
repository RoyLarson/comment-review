# Retire unused review code

```
Status:   closed
Progress: 1 of 1 TODO tasks closed
Plan-tasks: 2 of 2 plan tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-11-21 (rebuilt-middle-final-review.md)
```

## Objective

Remove verified dead functions, event fields and the no-op anchor-line flag

## TODO tasks this plan closes

### A - [rebuilt-middle-final-review](../../TODO/rebuilt-middle-final-review.md)

- [x] T32 | Delete what nothing reads: AnswerRow.question, three event fields,
      desk/proof.py, diff3, tally, mark --anchor-line (E2)

## Plan Tasks

- [x] P1 | Removed tally and unused payloads. Proof and rollback behavior verified. | 1bd897f077a06dc469bfec75390cca32317a8553 | Remove
      unused functions and event fields
- [x] P2 | Removed anchor-line from CLI, reviewer brief and scripts. Middle-chain smoke passed. | 1bd897f077a06dc469bfec75390cca32317a8553 | Remove
      the no-op anchor-line flag from the CLI workflow
