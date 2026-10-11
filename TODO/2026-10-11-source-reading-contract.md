# Define shared source reading contracts

```
Status:   open
Progress: 3 of 4 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-11 (2026-10-11 lexical-reader design)
```

## Objective

Define shared source reading contracts.

## Tasks

- [x] T1 | Immutable source representation preserves exact text and classifications; all checks and review pass | 1c455282 | Represent
      source as ordered regions and ownership facts; verify exact reconstruction
      and independently expected classifications
- [ ] T2 | Carry reader compatibility and language settings through saved runs;
      verify incompatible contexts refuse before address use
- [x] T3 | Invalid region kinds raise ValueError; rejection and preservation tests pass review | 1c455282 | Reject
      invalid SourceRegion kinds; verify unknown strings, None and mutable
      values raise ValueError
        > 2026-10-11 Review: source.py:66 accepts mutable and unknown kinds
- [x] T4 | Non-string text raises ValueError before structural validation; focused tests pass review | 1c455282 | Reject
      non-string SourceStructure text; verify lists, bytes and None raise
      ValueError before caching
        > 2026-10-11 Review: source.py:143 accepts mutable text and bytes
