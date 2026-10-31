# Swift lexical reader

```
Status:   open
Progress: 1 of 4 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-25 (decision-log.md Process: #222)
```

## Objective

Read Swift source lexically from Swift's own language definition, as Python and
Rust are read: its own dated spec, its own definition, its own reader, and no
rule taken from another language.

Worked when it is asked for -- decision-log.md Process: #222.

## Tasks

- [ ] T1 | Specify the Swift lexical reader in its own dated spec
        > 2026-10-25 Check: spec states modes, directive bounds, doc owners, fixtures
- [ ] T2 | Implement the Swift reader from its definition
        > 2026-10-25 Check: uv run pytest -q tests/reading/test_swift.py
- [ ] T3 | Give Swift its own soft-keyword rule for `convenience`, `required`
        > 2026-10-25 Moved from lexer-and-language-findings T15
        > 2026-10-25 Check: `required = f()` in a .swift mints no a; a real init does
- [x] T4 | Row names shebang; refusal tested, Swift not run | 6e48bc46 | Name
      `shebang` on the Swift row from its own grammar
