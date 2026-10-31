# Lua lexical reader

```
Status:   open
Progress: 1 of 8 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-25 (decision-log.md Process: #222)
```

## Objective

Read Lua source lexically from Lua's own language definition, as Python and Rust
are read: its own dated spec, its own definition, its own reader, and no rule
taken from another language.

Worked when it is asked for -- decision-log.md Process: #222.

## Tasks

- [ ] T1 | Specify the Lua lexical reader in its own dated spec
        > 2026-10-25 Check: spec states modes, directive bounds, doc owners, fixtures
- [ ] T2 | Implement the Lua reader from its definition
        > 2026-10-25 Check: uv run pytest -q tests/reading/test_lua.py
- [ ] T3 | Read a Lua long bracket of any level
        > 2026-10-25 Moved from lexer-and-language-findings T18
        > 2026-10-25 Check: a fixture with `--[===[` fails before the fix
- [ ] T4 | Make Lua doc typing consult placement, not only the opener
        > 2026-10-25 Moved from lexer-and-language-findings T25
        > 2026-10-25 Check: `---` above `local function f()` types docstring
        > 2026-10-25 Check: `---` above nothing types comment
- [ ] T5 | Add `---` to Lua's `doc_line`
        > 2026-10-25 Moved from lexer-and-language-findings T28
        > 2026-10-25 Check: `--- x` above `local function f()` is a docstring on it
        > 2026-10-25 Authorised by the lexer-and-language-findings T20 ruling
- [ ] T6 | Select the earliest block opener on a Lua line
        > 2026-10-25 Moved from lexer-and-language-findings T35
        > 2026-10-25 Check: mixed delimiters in a long comment keep its full body
- [ ] T7 | Decide whether a Lua `--[[ ]]` block has its markers stripped
        > 2026-10-25 Moved from block-comment-markers-survive-into-the-prose T10
        > 2026-10-25 Check: answer and measurement written here, from Lua's grammar
- [x] T8 | Row names shebang; refusal tested, Lua not run | 6e48bc46 | Name
      `shebang` on the Lua row from its own grammar
