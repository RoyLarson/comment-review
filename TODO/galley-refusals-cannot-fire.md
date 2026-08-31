# The galley refuses two shapes the docket reader already rejected

```
Status:   open
Progress: 0 of 2 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-25 (the final whole-branch review of the write-chain branch,
          2026-08-25)
```

## Objective

The galley refuses two shapes the docket reader already rejected.

## Tasks

- [ ] T1 | State in reset's docstring that docket.read is the enforcing check on
      the proof path, and that these guards cover other callers
- [ ] T2 | Decide whether the galley keeps them once commands/galley.py is
      removed. Requires-Roy
