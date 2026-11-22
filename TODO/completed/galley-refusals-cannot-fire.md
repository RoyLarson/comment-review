# The galley refuses two shapes the docket reader already rejected

```
Status:   closed
Progress: 2 of 2 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-25 (the final whole-branch review of the write-chain branch,
          2026-08-25)
```

## Objective

The galley refuses two shapes the docket reader already rejected.

## Tasks

- [-] T1 | Prescribed sentence would be false: on proof --proof the galley is the enforcing check; verified at HEAD | 67184ac1 | State
      in reset's docstring that docket.read is the enforcing check on the proof
      path, and that these guards cover other callers
- [-] T2 | Moot: galley command and alias gone (1119cb32, 5ad6d47d); guards are the only check on proof --proof | 5ad6d47d | Decide
      whether the galley keeps them once commands/galley.py is removed.
      Requires-Roy
