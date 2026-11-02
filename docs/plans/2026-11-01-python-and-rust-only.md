# Python and Rust only

```
Status:   in-progress
Progress: 3 of 4 TODO tasks closed
Plan-tasks: 8 of 9 plan tasks closed
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

- [x] T40 | Remove `BY_EXT`, which nothing reads
- [x] T42 | Move `NAMED_DEFS` into `concordance`
- [x] T44 | Move the comment-form readers out of `lexer.py` to the desk

## Plan Tasks

- [x] P1 | Each general test has a Rust or Python case beside its lexical one; uv run pytest -q gave 6823 passed, 1 skipped, and the uninstall probe left only die-listed functions with no surviving id | e18de103c58dc8277c1099588a1ebd2e256ba16c | Port
      the tests that lean on a lexical language
- [x] P2 | NAMED_DEFS and leading_between moved to their users, two tests moved and run; ruff, ty, gates clean; pytest 6823 passed | 3cdbe205743d9260e7f4cf763519c50f66de7258 | Move
      NAMED_DEFS and leading_between to their users
- [x] P3 | prove_unchanged answers UNCHECKED for a file no reader claims; summary never counts it proven; reader failure still exits 1; tests, ruff, ty, shipped syntax, vocabulary and pytest pass | 3531369c45f58d4b768c0336b76ab060ec994ea6 | Answer
      UNCHECKED for a file no reader claims
- [x] P4 | Binder.freeform and VERSION 4 verified: 9 new tests red then green, full suite 6836 passed, ruff/ty/shipped-syntax/vocabulary pass | 30754af6f0450f69dfa82fa491e99305471bc928 | Add
      freeform paths to the binder
- [x] P5 | Lexical languages uninstalled: READER_METADATA is empty, gather --languages lists language and extensions, every failing lexical test or row is deleted, and no Python or Rust row was lost by the per-function id check. uv run pytest -q: 5881 passed, 1 skipped. | e1bf4bfbf83e71c68589fe2707deb99a7fd5956f | Uninstall
      the lexical languages
- [x] P6 | lexer.py and stripped.py deleted; language.py, readers.py, page.py reduced; pytest, ty, ruff, syntax and vocabulary gates passed; grep for lexical names empty | e2b34a22ad36b0919b9d01cfd05bb74e80e76db9 | Delete
      the lexical reader
- [x] P7 | closing_docstring, a_series, the a at eof, CodeLine.joins and the unit loop are gone; suite 5803 passed; 2088 pages matched BASE, differ 0; probe of 1898 files read no multi-line anchor | d6304b69490e7eb6ada90890d25bb2e37ae8983a | Remove
      the closing docstring branch
- [ ] P8 | Update the prose and the board for Python and Rust only
- [x] P9 | gather lists source files with no reader on the binder, refuses one outside the repo, and passes over other walked files; partition and compose deal freeform paths; a freeform-only run passes topology, distribute, check and collate; full suite 6854 passed, 1 skipped | 27d3262931b68d602e97dcf33039d75c0e3f1b0b | Route
      freeform files from gather to reviewers
