# Python and Rust only

```
Status:   in-progress
Progress: 0 of 4 TODO tasks closed
Plan-tasks: 1 of 9 plan tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-11-01 (decision-log #259, #260)
```

## Objective

Only Python and Rust are read, addressed, written and proved; other source files
are freeform and answer UNCHECKED

## TODO tasks this plan closes

### A - [python-and-rust-only](../../TODO/python-and-rust-only.md)

- [ ] T1 | Remove every language with no reader from the system

### B - [lexer-and-language-findings](../../TODO/lexer-and-language-findings.md)

- [ ] T40 | Remove `BY_EXT`, which nothing reads
- [ ] T42 | Move `NAMED_DEFS` into `concordance`
- [ ] T44 | Move the comment-form readers out of `lexer.py` to the desk

## Plan Tasks

- [x] P1 | Each general test has a Rust or Python case beside its lexical one; uv run pytest -q gave 6823 passed, 1 skipped, and the uninstall probe left only die-listed functions with no surviving id | e18de103c58dc8277c1099588a1ebd2e256ba16c | Port
      the tests that lean on a lexical language
- [ ] P2 | Move NAMED_DEFS and leading_between to their users
- [ ] P3 | Answer UNCHECKED for a file no reader claims
- [ ] P4 | Add freeform paths to the binder
- [ ] P5 | Uninstall the lexical languages
- [ ] P6 | Delete the lexical reader
- [ ] P7 | Remove the closing docstring branch
- [ ] P8 | Update the prose and the board for Python and Rust only
- [ ] P9 | Route freeform files from gather to reviewers
