# vocabulary_sweep reads a path that moved, so nothing looks for undefined terms

```
Status:   open
Progress: 0 of 3 tasks done
Owner:    systems
Requires-Roy: false
Raised:   2026-08-29 (2026-08-29, checking whether block-context's `State` was a
          declared term)
```

## Objective

vocabulary_sweep reads a path that moved, so nothing looks for undefined terms.

## Tasks

- [ ] T1 -- Point `EMITTED` at the path the build actually writes. Verify: `uv run
      python scripts/vocabulary_sweep.py` exits 0 and prints rows.
- [ ] T2 -- Find every other script reading a pre-move `references/` path. Verify:
      each shipped path named in `scripts/` resolves with `test -f`.
- [ ] T3 -- Decide whether a script that crashes at startup should be caught by a
      gate, given `dead_sweep.py` and this one are INPUTS that always exit 0.
      Verify: the answer is written into this file.
