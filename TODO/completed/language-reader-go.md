# Go lexical reader

```
Status:   closed
Progress: 3 of 3 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-25 (decision-log.md Process: #222)
```

## Objective

Read Go source lexically from Go's own language definition, as Python and Rust
are read: its own dated spec, its own definition, its own reader, and no rule
taken from another language.

Worked when it is asked for -- decision-log.md Process: #222.

## Tasks

- [-] T1 | Superseded by #259: its language or reader left the system | e2b34a22ad36b0919b9d01cfd05bb74e80e76db9 | Specify
      the Go lexical reader in its own dated spec
        > 2026-10-25 Check: spec states modes, directive bounds, doc owners, fixtures
- [-] T2 | Superseded by #259: its language or reader left the system | e2b34a22ad36b0919b9d01cfd05bb74e80e76db9 | Implement
      the Go reader from its definition
        > 2026-10-25 Check: uv run pytest -q tests/reading/test_go.py
- [-] T3 | Superseded by #259: its language or reader left the system | e2b34a22ad36b0919b9d01cfd05bb74e80e76db9 | Implement
      Go documentation adjacency
        > 2026-10-25 Moved from doc-does-not-fill-its-a T10
        > 2026-10-25 Check: touching comments use a, separated comments use b
        > 2026-10-25 Check: the reader prose agrees
