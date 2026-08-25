# The addresser command answers three questions wrongly at exit 0

```
Status:   open
Progress: 0 of 4 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-25 (the final whole-branch review of the write-chain branch,
          2026-08-25)
```

## Objective

The addresser command answers three questions wrongly at exit 0.

## Tasks

- [ ] Reproduce all three against a real binder and record the output
- [ ] Point the three reads at original_start and original_end. Verify: --resolve
      prints real line numbers
- [ ] Decide what replaces the declares short-circuit at addresses.py:76 now that
      rows do not carry it
- [ ] A test per flag, over a real binder. Verify: each fails against the current
      code
