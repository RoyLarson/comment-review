# The addresser command answers three questions wrongly at exit 0

```
Status:   open
Progress: 4 of 4 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-25 (the final whole-branch review of the write-chain branch,
          2026-08-25)
```

## Objective

The addresser command answers three questions wrongly at exit 0.

## Tasks

- [x] T1 | FINISHED | unknown | Reproduce all three against a real binder and
      record the output
- [x] T2 | FINISHED | unknown | Point the three reads at original_start and
      original_end. Verify: --resolve prints real line numbers
- [x] T3 | FINISHED | unknown | Decide what replaces the declares short-circuit
      at addresses.py:76 now that rows do not carry it
- [x] T4 | FINISHED | unknown | A test per flag, over a real binder. Verify:
      each fails against the current code
