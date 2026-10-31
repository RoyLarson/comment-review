# C# lexical reader

```
Status:   open
Progress: 1 of 3 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-25 (decision-log.md Process: #222)
```

## Objective

Read C# source lexically from C#'s own language definition, as Python and Rust
are read: its own dated spec, its own definition, its own reader, and no rule
taken from another language.

Worked when it is asked for -- decision-log.md Process: #222.

## Tasks

- [ ] T1 | Specify the C# lexical reader in its own dated spec
        > 2026-10-25 Check: spec states modes, directive bounds, doc owners, fixtures
- [ ] T2 | Implement the C# reader from its definition
        > 2026-10-25 Check: uv run pytest -q tests/reading/test_csharp.py
- [x] T3 | Ruled #252; the row change is in the repair commit | 207d733bcd76762e6fe72d77618c45e68c11ad42 | Decide
      whether C# holds `#!` as an interpreter line
        > 2026-10-30 Outcome: C# names `#!` on its row (#252)
