# Define shared source reading contracts

```
Status:   open
Progress: 0 of 4 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-11 (2026-10-11 lexical-reader design)
```

## Objective

Define shared source reading contracts.

## Tasks

- [~] T1 | Represent source as ordered regions and ownership facts; verify exact
      reconstruction and independently expected classifications
- [ ] T2 | Carry reader compatibility and language settings through saved runs;
      verify incompatible contexts refuse before address use
- [ ] T3 | Reject invalid SourceRegion kinds; verify unknown strings, None and
      mutable values raise ValueError
        > 2026-10-11 Review: source.py:66 accepts mutable and unknown kinds
- [ ] T4 | Reject non-string SourceStructure text; verify lists, bytes and None
      raise ValueError before caching
        > 2026-10-11 Review: source.py:143 accepts mutable text and bytes
