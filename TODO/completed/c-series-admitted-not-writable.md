# The c series is admitted by the gate and cannot be written

```
Status:   decision-needed
Progress: 5 of 5 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-19 (the seven-agent address review, 2026-08-19)
Ruled:    2026-08-19 — Roy, 2026-08-19: 'c needs to be writeable. It is the reason c is
          not an extension of b.' The census states original_column, one past the last
          character of CODE on the line; galley.splice keeps line[:original_column-1].
          whole_lines is gone -- it was the same fact, weaker. Task 5's twin is NOT the
          same shape and stays open: the code check refuses an add/drop on a docstring
          because the AST changes, which no column can express.
```

## Objective

!! **THE JOIN SAYS `Every finding is admissible. Stage 5 may rule.` ON AN `add` AT `@c0`, AND THE
GALLEY THEN REFUSES THE SPLICE -- discarding every other edit in that file with it.** The pipeline
says yes at stage 5 and no at 5b, which `verdicts.py` itself calls the most expensive kind of
diagnostic there is: it sends the reader to fix something that is not broken.

**The `c` series exists for exactly this and nothing else.** Roy, 2026-08-19: *"without the cs
being there you can't specify that the comment belongs at the end of the code line."* A `margin`
carries `whole_lines=False`; `galley.shares_a_line_with_code` is exactly `not whole_lines` and
refuses -- correctly, because a splice replaces WHOLE LINES and writing over that line would
delete the statement sharing it.

! **It is not only the empty case.** Any `correct`, `patch` or `drop` on an existing
`trailing-comment` is refused the same way, and a trailing comment is a real prose block owed a
seeded record -- it is not in `HOLDS_NO_PROSE`.

!! **The refusal message names the CENSUS, not the series**, so a task agent reads it as staleness
and re-runs the census, which never helps. And no test in `tests/test_galley.py` covers a margin
or trailing-comment edit, which is how it shipped.

## Tasks

- [x] !! **RULING NEEDED: does the galley learn to splice WITHIN a line, or is the
      `c` series addressable-but-not-writable?** It cannot stay admitted-then-
      refused. `margin` carries `whole_lines=False` and
      `galley.shares_a_line_with_code` refuses exactly that, adding
      `len(file_edits)` to the refusal -- so one `c` edit voids every edit in the
      file.
- [x] **Same for a `patch`/`correct`/`drop` on an existing trailing comment**,
      which is a real prose block owed a seeded record -- `trailing-comment` is
      not in `HOLDS_NO_PROSE`. Measured: refused identically.
- [x] **The refusal message points at the census, not at the series**, so a task
      agent reads it as staleness and re-runs the census, which never helps.
- [x] **No test covers a margin or trailing-comment edit** in
      `tests/test_galley.py`. Whatever is ruled, that is the gap that let this
      ship.
- [x] ! Its twin at the other end of the pipeline is [`the-code-check-refuses-add-
      and-drop-on-a-docstring`](the-code-check-refuses-add-and-drop-on-a-
      docstring.md) -- an `add` at an `a` place is admitted, galleyed, then
      refused by the CODE CHECK. Rule them together or state why they differ.
