# Isolate the edit path from comment reading

```
Status:   open
Progress: 0 of 2 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-25 (decision-log.md Process: #227)
```

## Objective

`comment_form` (reading/lexer.py) and the `Comment` / `Fragment` types
(reading/comment.py) do two jobs. Reading: split a paragraph's raw text into
prose and markup, which is what `Paragraph.text` and a role's claim matching
read (decision-log.md Process: #227). Setting: `Fragment.wrap` re-wraps new
prose into the original markers and width, which is compositor work the desk
reaches into `reading` for (desk/marks/rules.py, desk/marks/table.py).

The edit path is isolated when the reading half lives with reading and the
setting half lives with whoever sets a page, and the desk asks each for only the
half it needs. `comment_form` also sits in lexer.py while it dispatches on
language through every reader's comment scanner.

## Tasks

- [ ] T1 | Move Fragment.wrap and its layout fields out of reading
        > 2026-10-25 Check: desk imports no setting code from comment_review.reading
- [ ] T2 | Move comment_form out of lexer.py into its own reading module
        > 2026-10-25 Check: no def comment_form in reading/lexer.py
