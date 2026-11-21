# Share rollback report construction

```
Status:   closed
Progress: 1 of 1 TODO tasks closed
Plan-tasks: 1 of 1 plan tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-11-21 (rebuilt-middle-final-review.md)
```

## Objective

Build rollback events in one place while preserving reasons and exit codes

## TODO tasks this plan closes

### A - [rebuilt-middle-final-review](../../TODO/rebuilt-middle-final-review.md)

- [x] T27 | Give rollback one producer; the bus builds two without a Fold and
      commands/collate.py a third (C3)

## Plan Tasks

- [x] P1 | One RolledBack constructor in production and 274 focused tests passed. | 7326755ae0dc31e83d42cabad89df80cbfadd529 | Move
      rollback report construction into the shared event module
