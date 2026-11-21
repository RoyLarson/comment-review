# Remove desk crossings and duplicate rules

```
Status:   in-progress
Progress: 1 of 2 TODO tasks closed
Plan-tasks: 1 of 2 plan tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-11-21 (rebuilt-middle-final-review.md)
```

## Objective

Remove desk imports of Binder first, then consolidate duplicate validation and
evaluator rules

## TODO tasks this plan closes

### A - [rebuilt-middle-final-review](../../TODO/rebuilt-middle-final-review.md)

- [x] T12 | Move desk's two binder imports out: collator.py takes a Binder,
      containers.py a private binder name (D1)
- [ ] T33 | Reduce rules stated twice: mismatched roots, the copy-chief string,
      marks by role, a ruling refused twice (E3)

## Plan Tasks

- [x] P1 | Architecture gate verifies the desk-to-binder imports are gone. | ef172e66dda3df740e85bfb28e51531076424b18 | Remove
      desk imports of binder implementation
- [ ] P2 | Consolidate duplicate tree and evaluator rules
