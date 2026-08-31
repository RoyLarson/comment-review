# A malformed cite aborts the half meant to report rather than raise

```
Status:   open
Progress: 0 of 3 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-30 (2026-08-30, found independently by two reviews on the same day --
          one reading the design, one reading only the code)
```

## Objective

A malformed cite aborts the half meant to report rather than raise.

## Tasks

- [ ] T1 | Reproduce it. Verify: `_cite_at('m.py:\u00b2')` raises `ValueError`
      today, and a test asserts a named problem instead.
- [ ] T2 | Return a problem rather than raising. Verify: `verify_report` over an
      edit_copy holding one malformed cite reports it and still checks every
      other mark -- today one bad cite aborts the whole report.
- [ ] T3 | Audit the other guards for the same shape. Verify: no `isdigit()` in
      `src/` is followed by an `int()` that can still fail.
