# Shell lexical reader

```
Status:   open
Progress: 2 of 7 tasks closed
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
        > 2026-10-30 Open: `echo ${v% #*}` reads ` #*}` as c0; a drop keeps PROVEN
- [x] T4 | word_breaks row field; bash-checked inputs in tests | 5b0f9fbf | Read
      a shell `#` as a comment only at a word start, at `lexer.py:973`
- [ ] T5 | Read a line opening `#` after a `\` continuation as code
- [ ] T6 | Read a backslash inside a single-quoted string as literal
- [x] T7 | Glued `)` and backtick read as code, checked against bash | 46943d65 | Read
      `#` glued to a closing `)` or backtick as code, at `lexer.py:812`
