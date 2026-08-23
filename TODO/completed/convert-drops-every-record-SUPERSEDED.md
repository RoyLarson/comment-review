# record.py --convert drops every record it was written to migrate

```
Status:   open
Progress: 3 of 3 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-20 (the /code-review high of 2026-08-20)
Superseded: 2026-08-20 — 2026-08-20 -- all three tasks name code that no longer exists.
            held.convert, held.parse_report and record.py --convert were DELETED in
            2a86573, with the 0.2.x TEXT format they read. Roy: 'we are not carrying a
            backwards compatible shim right now, particularly on a format that was a
            proof-of-concept format.' ! The defect was real and is kept legible here:
            the guard tested whether an address was EMPTY when it needed to test whether
            it was a CENSUS address, so every finding slipped it and was dropped at exit
            0. Nothing replaces the converter; docs/history.md says where the reader is
            in the history.
```

## Objective

record.py --convert drops every record it was written to migrate.

## Tasks

- [x] !! `held.py:487` `convert`'s guard counts only records whose address is
      EMPTY, but `parse_report` fills `address` from the 0.2.x `BLOCK n |
      path:start-end` line -- non-empty, and matching no census address. Every
      substantive record slips the guard, matches no slot, and is dropped.
- [x] Reported: `record.py --convert` on `evidence/redacted-corpus-
      full-v0_2/reports/block-context-round2.md` prints `91 findings -> 0 filled
      records` and EXITS 0, writing a file of null verdicts -- the exact failure
      the guard's own comment says it prevents.
- [x] Its sibling report fails the opposite way: `block-context.md` exits on an
      uncaught `ValueError` traceback from `record.py:1109`.
