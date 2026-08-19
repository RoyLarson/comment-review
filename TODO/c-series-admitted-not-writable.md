# The c series is admitted by the gate and cannot be written

```
Status:   decision-needed
Progress: 0 of 5 tasks done
Owner:    session
Requires-Roy: true
Raised:   2026-08-19 (the seven-agent address review, 2026-08-19)
```

## Objective

The c series is admitted by the gate and cannot be written.

## Tasks

- [ ] !! **RULING NEEDED: does the galley learn to splice WITHIN a line, or is the
      `c` series addressable-but-not-writable?** It cannot stay admitted-then-
      refused. `margin` carries `whole_lines=False` and
      `galley.shares_a_line_with_code` refuses exactly that, adding
      `len(file_edits)` to the refusal -- so one `c` edit voids every edit in the
      file.
- [ ] **Same for a `patch`/`correct`/`drop` on an existing trailing comment**,
      which is a real prose block owed a seeded record -- `trailing-comment` is
      not in `HOLDS_NO_PROSE`. Measured: refused identically.
- [ ] **The refusal message points at the census, not at the series**, so a task
      agent reads it as staleness and re-runs the census, which never helps.
- [ ] **No test covers a margin or trailing-comment edit** in
      `tests/test_galley.py`. Whatever is ruled, that is the gap that let this
      ship.
- [ ] ! Its twin at the other end of the pipeline is [`the-code-check-refuses-add-
      and-drop-on-a-docstring`](the-code-check-refuses-add-and-drop-on-a-
      docstring.md) -- an `add` at an `a` place is admitted, galleyed, then
      refused by the CODE CHECK. Rule them together or state why they differ.
