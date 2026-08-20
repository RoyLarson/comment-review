# record.py --convert drops every record it was written to migrate

```
Status:   open
Progress: 0 of 3 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-20 (the /code-review high of 2026-08-20)
```

## Objective

record.py --convert drops every record it was written to migrate.

## Tasks

- [ ] !! `held.py:487` `convert`'s guard counts only records whose address is
      EMPTY, but `parse_report` fills `address` from the 0.2.x `BLOCK n |
      path:start-end` line -- non-empty, and matching no census address. Every
      substantive record slips the guard, matches no slot, and is dropped.
- [ ] Reported: `record.py --convert` on `evidence/redacted-corpus-
      full-v0_2/reports/block-context-round2.md` prints `91 findings -> 0 filled
      records` and EXITS 0, writing a file of null verdicts -- the exact failure
      the guard's own comment says it prevents.
- [ ] Its sibling report fails the opposite way: `block-context.md` exits on an
      uncaught `ValueError` traceback from `record.py:1109`.
