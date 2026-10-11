# Define shared source reading contracts

```
Status:   open
Progress: 6 of 8 tasks closed
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
- [x] T5 | Immutable outcomes and invalid-state checks verified | 42752127 | Define
      immutable read diagnostics and failures; verify location units, field
      validation and successful empty input
- [~] T6 | Reject failed readings at page and proof admission; verify
      either-side failures, empty success and cleanup
- [x] T7 | Unsupported-syntax fixture runs only on affected interpreter | 2b50b752 | Make
      unsupported-syntax fixtures interpreter-aware; verify valid newer Python
      syntax is not required to fail
        > 2026-10-11 Review: test_reading_diagnostics.py:21 assumes Python 3.11 syntax
- [x] T8 | Normal script imports and page outcomes verified by regression | a8b18c66 | Repair
      render_page package imports and page outcomes; verify its normal command
      on successful and refused source
        > 2026-10-11 Found during migration: render_page imports retired flat modules
