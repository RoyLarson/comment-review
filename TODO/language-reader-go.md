# Go lexical reader

```
Status:   open
Progress: 0 of 3 tasks closed
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

- [ ] T1 | Specify the Go lexical reader in its own dated spec
        > 2026-10-25 Check: spec states modes, directive bounds, doc owners, fixtures
- [ ] T2 | Implement the Go reader from its definition
        > 2026-10-25 Check: uv run pytest -q tests/reading/test_go.py
- [ ] T3 | Implement Go documentation adjacency
        > 2026-10-25 Moved from doc-does-not-fill-its-a T10
        > 2026-10-25 Check: touching comments use a, separated comments use b
        > 2026-10-25 Check: the reader prose agrees
