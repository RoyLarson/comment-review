# The galley is the last index-keyed interface, at the write boundary

```
Status:   open
Progress: 0 of 3 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-19 (the seven-agent address review, 2026-08-19)
```

## Objective

The galley is the last index-keyed interface, at the write boundary.

## Tasks

- [ ] **Accept an address key through `record.entry_for`; keep `int` for held
      runs.** `addresser.resolve` already returns exactly the 1-based indices
      needed and is called only from inside addresser; galley imports neither
      addresser nor record.
- [ ] **`SKILL.md` still documents the index form** at the 5b/6b galley step.
- [ ] ! It sits exactly at the round-2 boundary, where `re-review.md` says *"THE
      ADDRESS DOES CARRY"* -- so the one place the rebuild's property matters most
      is the one place it is discarded.
