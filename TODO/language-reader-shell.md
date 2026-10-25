# Shell lexical reader

```
Status:   open
Progress: 0 of 3 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-25 (decision-log.md Process: #222)
```

## Objective

Read Shell source lexically from Shell's own language definition, as Python and
Rust are read: its own dated spec, its own definition, its own reader, and no
rule taken from another language.

Worked when it is asked for -- decision-log.md Process: #222.

## Tasks

- [ ] T1 | Specify the Shell lexical reader in its own dated spec
        > 2026-10-25 Check: spec states modes, directive bounds, doc owners, fixtures
- [ ] T2 | Implement the Shell reader from its definition
        > 2026-10-25 Check: uv run pytest -q tests/reading/test_shell.py
- [ ] T3 | Make `#` inert after a dollar-brace in the Shell definition
        > 2026-10-25 Moved from lexer-and-language-findings T4
        > 2026-10-25 Check: `n=${#arr} # count` reads ONE trailing comment at `# count`
        > 2026-10-25 Parameter expansion value=${value#prefix} becomes a comment
