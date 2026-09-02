# A malformed cite aborts the half meant to report rather than raise

```
Status:   open
Progress: 3 of 3 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-30 (2026-08-30, found independently by two reviews on the same day --
          one reading the design, one reading only the code)
```

## Objective

A malformed cite aborts the half meant to report rather than raise.

## Tasks

- [-] T1 | SUPERSEDED into collator-defects T9, which carries this task verbatim since 9fc9272 | 9fc9272 | Reproduce
      it. Verify: `_cite_at('m.py:\u00b2')` raises `ValueError` today, and a
      test asserts a named problem instead.
- [-] T2 | SUPERSEDED into collator-defects T10, which carries this task verbatim since 9fc9272 | 9fc9272 | Return
      a problem rather than raising. Verify: `verify_report` over an edit_copy
      holding one malformed cite reports it and still checks every other mark --
      today one bad cite aborts the whole report.
- [-] T3 | SUPERSEDED into collator-defects T11, which carries this task verbatim since 9fc9272 | 9fc9272 | Audit
      the other guards for the same shape. Verify: no `isdigit()` in `src/` is
      followed by an `int()` that can still fail.
