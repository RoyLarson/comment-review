# record.ANCHOR_SIDE is written and read by nothing

```
Status:   open
Progress: 2 of 2 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-20 (the branch review of 2026-08-20; an AST sweep found only this)
```

## Objective

record.ANCHOR_SIDE is written and read by nothing.

## Tasks

- [x] `record.py:280` `ANCHOR_SIDE`. `grep -rn ANCHOR_SIDE plugins/ tests/
      scripts/ evals/*.py` returns the definition only. The concept was removed on
      purpose -- `record.claim_keys:322` says *"NO `side`. The ADDRESS carries
      it"*, and `desk.payload_problem:217-220` agrees.
- [x] The comment above it, `record.py:275` -- *"What an `add`'s PAYLOAD must
      carry: the anchor, NAMED"* -- now describes only `ANCHOR_NAME`.
