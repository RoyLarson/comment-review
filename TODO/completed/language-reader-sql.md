# SQL lexical reader

```
Status:   closed
Progress: 3 of 3 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-25 (decision-log.md Process: #222)
```

## Objective

Read SQL source lexically from SQL's own language definition, as Python and Rust
are read: its own dated spec, its own definition, its own reader, and no rule
taken from another language.

Worked when it is asked for -- decision-log.md Process: #222.

## Tasks

- [-] T1 | Superseded by #259: its language or reader left the system | e2b34a22ad36b0919b9d01cfd05bb74e80e76db9 | Specify
      the SQL lexical reader in its own dated spec
        > 2026-10-25 Check: spec states modes, directive bounds, doc owners, fixtures
- [-] T2 | Superseded by #259: its language or reader left the system | e2b34a22ad36b0919b9d01cfd05bb74e80e76db9 | Implement
      the SQL reader from its definition
        > 2026-10-25 Check: uv run pytest -q tests/reading/test_sql.py
- [x] T3 | SQL backslash-quote and backslash-double-quote files refused as unprovable; full suite passes | 694f4fed772a4024be3f1199d5925f755dd30000 | Read
      a backslash inside a single-quoted string as literal
