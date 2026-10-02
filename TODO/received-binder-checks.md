# Check received binder assignments

```
Status:   open
Progress: 3 of 4 tasks closed
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
- [x] T2 | Deleted rulings fail check; paired copies fail admission independently; 166 tests pass | 8b3984ce | Check
      required rulings against received binders; verify missing and unruled
      places refuse admission
- [x] T3 | Withdrawal removes marks without pages or blanks; assigned-place checks require replacement; 76 tests pass | 39e01fc4 | Remove
      withdrawn marks from edit copies; verify binder membership controls
      whether check requires a replacement ruling
- [ ] T4 | Validate role coverage from received shards; verify omissions fail
      and fold and turn preserve input binders
