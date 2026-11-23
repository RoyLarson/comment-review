# Commands import only flows and the leaves

```
Status:   open
Progress: 0 of 2 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-11-10 (review of the collate command move, 2026-11-10)
```

## Objective

Commands import only flows and the leaves.

## Tasks

- [ ] T1 | Route the desk, binder, results, docket and concordance imports in
      commands/ through flows
- [ ] T2 | Extend tests/test_areas.py to refuse a commands import outside flows
      and the leaves
        > 2026-11-23 comment-review 2026-11-23: gate misses commands/mark.py machine
