# TypeScript lexical reader

```
Status:   closed
Progress: 2 of 2 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-25 (decision-log.md Process: #222)
```

## Objective

Read TypeScript source lexically from TypeScript's own language definition, as
Python and Rust are read: its own dated spec, its own definition, its own
reader, and no rule taken from another language.

Worked when it is asked for -- decision-log.md Process: #222.

## Tasks

- [-] T1 | Superseded by #259: its language or reader left the system | e2b34a22ad36b0919b9d01cfd05bb74e80e76db9 | Specify
      the TypeScript lexical reader in its own dated spec
        > 2026-10-25 Check: spec states modes, directive bounds, doc owners, fixtures
- [-] T2 | Superseded by #259: its language or reader left the system | e2b34a22ad36b0919b9d01cfd05bb74e80e76db9 | Implement
      the TypeScript reader from its definition
        > 2026-10-25 Check: uv run pytest -q tests/reading/test_typescript.py
