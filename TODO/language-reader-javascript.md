# JavaScript lexical reader

```
Status:   open
Progress: 2 of 5 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-25 (decision-log.md Process: #222)
```

## Objective

Read JavaScript source lexically from JavaScript's own language definition, as
Python and Rust are read: its own dated spec, its own definition, its own
reader, and no rule taken from another language.

Worked when it is asked for -- decision-log.md Process: #222.

## Tasks

- [ ] T1 | Specify the JavaScript lexical reader in its own dated spec
        > 2026-10-25 Check: spec states modes, directive bounds, doc owners, fixtures
- [ ] T2 | Implement the JavaScript reader from its definition
        > 2026-10-25 Check: uv run pytest -q tests/reading/test_javascript.py
- [ ] T3 | Implement JavaScript regex-literal recognition
        > 2026-10-25 Moved from lexer-and-language-findings T33
        > 2026-10-25 Check: `/[//]/` yields no comment paragraph
- [-] T4 | Refused at the proof, not read: #258; reissued as a new task | 3e2a87a0799543c84093b6811f382313885c8852 | Read
      JSX text as code, not a line comment
- [x] T5 | A comment between the tags of a JSX element makes the stripped proof unprovable; JS states element_suffixes for all its suffixes and TS for .tsx only; tests fail on the prior code; corpus 17 JS/TS files, none newly refused | 57fa9b77c34e7197b1a8ede890cca5d242a01d67 | Refuse
      a comment inside JSX text in the stripped proof
