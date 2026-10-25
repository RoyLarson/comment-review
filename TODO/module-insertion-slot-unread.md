# Remove the module insertion slot no page reads

```
Status:   open
Progress: 1 of 4 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-23 (final review of the Rust reader plan, R2)
```

## Objective

Every reader record carries a module insertion line as `insertions[0]`, and
`declarations()` hands it to the page as the module entry `(0, line, True)`. The
page's `cue` only checks that the value is not None (`reading/addresser.py`, the
module trigger); the addresser sets `a0` after the front matter whatever the
line says. For Rust the value is always 1, so the records check that the module
insertion may not follow the first declaration (`reading/rust/records.py`,
`_insertions`) cannot fail on a real read. Python carries the slot the same way.

A value that nothing branches on is dead, and a check on it can never fail.
Either the slot goes from both readers' records and `declarations()` writes the
module entry itself, or the slot is kept as the protocol's shape and its check
is removed. Deciding between them changes the `ReaderRecord` contract both
readers satisfy.

## Tasks

- [x] T1 | Ruling recorded as decision-log Process #218 | 0d257f3c | Decide
      whether insertions[0] leaves both reader records
        > 2026-10-24 Roy chose C, NamedTuple included; decision-log Process #218
- [ ] T2 | Remove the slot or its dead check, as decided. Verify: a test fails
      first
        > 2026-10-24 Decided by #218: insertions[0] and its check leave both readers
- [ ] T3 | Replace the bare tuple[int, int, bool] with a named documentation
      place
        > 2026-10-24 Check: grep finds no tuple[int, int, bool] under src
- [ ] T4 | Move the module entry out of declarations() into an a-series answer
        > 2026-10-24 Check: no caller indexes decls[0] or slices decls[1:]
