# Check received binder assignments

```
Status:   closed
Progress: 4 of 4 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-01 (Roy approved received binders and withdrawal removal)
```

## Objective

Check received binder assignments.

## Tasks

- [x] T1 | Paired binders preserve shards, filters and gathered root; 31 focused tests pass | bdef6af1 | Distribute
      paired binders and edit copies; verify shards and stage filters define
      each assigned review set
- [x] T2 | Each copy needs independent coverage and preflight needs its binder; review confirms both bypasses closed | ba48d3b0 | Check
      required rulings against received binders; verify missing and unruled
      places refuse admission
        > 2026-10-01 Review: omitted received binders still allowed combined coverage
- [x] T3 | Withdrawal removes marks without pages or blanks; assigned-place checks require replacement; 76 tests pass | 39e01fc4 | Remove
      withdrawn marks from edit copies; verify binder membership controls
      whether check requires a replacement ruling
- [x] T4 | Role shard omissions refuse admission; full distribution-fold-turn test proves binders unchanged | ba48d3b0 | Validate
      role coverage from received shards; verify omissions fail and fold and
      turn preserve input binders
