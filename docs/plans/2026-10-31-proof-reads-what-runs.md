# The proof reads what runs

```
Status:   in-progress
Progress: 8 of 9 TODO tasks closed
Plan-tasks: 7 of 9 plan tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-31 (code-review max, 2026-10-31)
```

## Objective

A comment edit that changes what the language runs never reports PROVEN

## TODO tasks this plan closes

### A - [one-line-ending-per-file](../../TODO/one-line-ending-per-file.md)

- [x] T2 | Refuse a file holding a lone CR at the gather

### B - [lexical-code-identity](../../TODO/lexical-code-identity.md)

- [x] T11 | Compare the interpreter line by bytes at `stripped.py:169`
- [x] T13 | Hold a backslash continuation in the stripped comparison,
      `stripped.py:108`
- [x] T10 | Refuse an ordinary string spanning lines at `stripped.py:129`

### C - [language-reader-shell](../../TODO/language-reader-shell.md)

- [x] T6 | Read a backslash inside a single-quoted string as literal

### D - [language-reader-sql](../../TODO/language-reader-sql.md)

- [x] T3 | Read a backslash inside a single-quoted string as literal

### E - [lexer-and-language-findings](../../TODO/lexer-and-language-findings.md)

- [ ] T68 | Refuse the `.rs` draft rustc cannot read at `rust/records.py:350`

### F - [bom-is-read-as-source](../../TODO/bom-is-read-as-source.md)

- [x] T5 | Write the byte-order mark ahead of f0, a0 or b0 when the head is set

### G - [language-reader-javascript](../../TODO/language-reader-javascript.md)

- [x] T5 | Refuse a comment inside JSX text in the stripped proof

## Plan Tasks

- [x] P1 | Lone CR refused at source_of, revision_source_of and _without_comments; tests fail first then pass | d506ea66c3357750b4bcf27375d4716a7d32abca | Refuse
      a lone CR at every read
- [x] P2 | Interpreter line compared with its ending in the stripped, Rust and Python readers; tests fail without the fix | 0033936561c21255827f51a1e592a3cb7912dd0f | Compare
      the interpreter line with its ending
- [x] P3 | verbatim_quotes read backslash as text; scan_strings built; full suite passes | 694f4fed772a4024be3f1199d5925f755dd30000 | Read
      a backslash in a verbatim quote as text
- [x] P4 | A comment inside an open string makes the file unprovable; tests and corpus count verified | 4092d634d1a4f31403fa12a4ef728ba86dc70b58 | Refuse
      a comment standing inside an open string
- [x] P5 | Stripped proof refuses a comment inside a markup element on the JS and .tsx suffixes; covered by test_stripped.py and the row pin test | 57fa9b77c34e7197b1a8ede890cca5d242a01d67 | Refuse
      a comment inside JSX text
- [ ] P6 | Refuse a Rust doc marker with nothing to attach to
- [ ] P7 | State what the stripped comparison holds
- [x] P8 | Stripped comparison holds line_continuations; covered by tests/reading/test_stripped.py and test_language_definitions.py. | a57c7015ed721c3fa4f08758c47da59f56f7c9c8 | Compare
      a backslash continuation in the stripped comparison
- [x] P9 | Compositor sets the byte-order mark at byte 0; tests/test_compositor.py, tests/reading/test_stripped.py, test_rust.py, test_python.py; full suite 6432 passed | dd155ab83501f5ff98b7772a98a79094a1e89929 | Set
      the byte-order mark at byte 0
