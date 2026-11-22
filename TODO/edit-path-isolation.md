# Isolate the edit path from comment reading

```
Status:   open
Progress: 2 of 7 tasks closed
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

- [-] T1 | SUPERSEDED by T3: Fragment.wrap was deleted in 862cb59d; Fragment.cut/_set_run now re-set lines | 22c3a0abcbc86509c74296319ce5b719a43338ca | Move
      Fragment.wrap and its layout fields out of reading
        > 2026-10-25 Check: desk imports no setting code from comment_review.reading
- [x] T2 | comment_form lives in reading/comment.py | e2b34a22ad36b0919b9d01cfd05bb74e80e76db9 | Move
      comment_form out of lexer.py into its own reading module
        > 2026-10-25 Check: no def comment_form in reading/lexer.py
- [ ] T3 | Move Fragment.cut's line re-setting out of reading/comment.py
        > 2026-11-22 Check: desk imports no setting code from comment_review.reading
- [ ] T4 | Re-read the text Fragment cut/_set_run set at reading/comment.py:211,
      refusing prose fused to a marker
        > 2026-11-22 Check (M14): Rust '//x /y' drop 'x' is refused, not '///y'
- [ ] T5 | Fix reading/comment.py:129 Fragment.cut refusing a drop of a
      docstring's last paragraph after a blank line
        > 2026-11-22 Check (M77): drop 'Drop me.' from a 2-paragraph docstring is set
- [ ] T6 | Make reading/comment.py:336 _set_run rebuild a touched line with its
      original space characters
        > 2026-11-22 Check (M79): a derived drop keeps a no-break space
- [ ] T7 | Split comment lines on line breaks only, not str.splitlines(), in
      reading/comment.py:475 _comment_fragment
        > 2026-11-22 Check (M80): drop 'note here' after a form feed writes no '#' alone
