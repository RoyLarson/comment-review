# One line ending per file

```
Status:   open
Progress: 0 of 5 TODO tasks closed
Plan-tasks: 0 of 7 plan tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-25 (one-line-ending-per-file.md)
```

## Objective

A file's line ending is decided once in machine/ at the read, and the flows hand
it to every writer of a line break

## TODO tasks this plan closes

### A - [one-line-ending-per-file](../../TODO/one-line-ending-per-file.md)

- [ ] T1 | Answer each file's line ending from one function in machine/
- [ ] T2 | Refuse a file holding a lone CR at the gather
- [ ] T3 | Write every line break with the ending decided at the read
- [ ] T4 | Check a written file's ending against its own pre-edit read
- [ ] T6 | Delete each line-ending guess made outside machine/

## Plan Tasks

- [ ] P1 | Answer each Source's line ending from one function in machine/repo.py
        > 2026-10-25 Check: tests for one, lone CR, mixed, none fail first
        > 2026-10-25 Mixed: git checkout ending for the path; no conversion refuses
- [ ] P2 | Name a file refused for its line ending as unreadable at the gather
        > 2026-10-25 Check: lone-CR fixture and unconverted mixed one exit nonzero
- [ ] P3 | Pass the decided ending to the Python reader in place of _newline
        > 2026-10-25 Check: CRLF file whose first ending differs sets the passed one
- [ ] P4 | Carry the ending on the page for set_page in place of
      compositor.line_endings
        > 2026-10-25 Check: binder wire carries the ending; set_page writes it
- [ ] P5 | Compare each written file's ending with its own pre-edit read in
      prove_unchanged
        > 2026-10-25 Check: CRLF beside LF sibling: kept proves, LF fails
        > 2026-10-25 dominant_ending and the sibling lookup go
- [ ] P6 | Hand the page's ending to the drop and move rewraps through
      flows/fill
        > 2026-10-25 Check: CRLF page drop and move write CRLF; 3 local rules go
- [ ] P7 | Delete any ending choice left in src/ outside machine/
        > 2026-10-25 Check: search of src/ outside machine/ finds no ending choice
