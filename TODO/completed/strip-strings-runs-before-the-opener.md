# A quote inside a block comment blanks the comment's own closer

```
Status:   open
Progress: 4 of 4 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-21 (the /code-review xhigh of 2026-08-21, focused on the file-to-
          census route)
Fixed:    2026-08-22 -- `8170651`, 'a comment closer eaten by an apostrophe, and a gate
          that lied'. The closer is now scanned in the RAW line while the opener is
          still found in the blanked one.
Closed:   2026-08-23 -- re-measured and every task here is settled. Ready for
          `complete`.
```

## Objective

**A quote inside a block comment blanked the comment's own closer, and it is fixed.**

!! **THE DEFECT.** `_strip_strings` runs on the raw line before the comment opener is known, so
`/* the " character */` blanked everything after the quote -- including `*/`. `run_ends`, added
the same day, was fed the blanked text and never saw the closer. Measured: that line followed by
`int a = 1; // note` censused as ONE paragraph spanning both lines, `int a = 1;` left
`code_lines` entirely, and every `b` and `c` boundary below it moved. ! It hit every language
whose `quotes` holds `'` and whose `char_quotes` is empty -- javascript, typescript, sql, lua,
ruby -- so `/* don't */`, ordinary English, was enough.

!! **THE FIX, `8170651`, 2026-08-22.** `lexer.py:1311-1312` cuts `tail` from `raw_line` and
hands that to `run_ends`; `:1297-1301` states the rule and why the two questions differ --
whether a `/*` OPENS a comment depends on whether it is inside a string, so that is asked of the
blanked `code`, and once the comment is open a quote has no meaning at all.

! **RE-MEASURED 2026-08-23**, calling `lexer.paragraphs_lexical` on
`/* the " character */` followed by `int a = 1; // note`: **two paragraphs** -- a `matter`
paragraph on line 1, and a `trailing-comment` on line 2 whose anchor is `int a = 1;`, with the
statement kept as code. The JavaScript apostrophe case answers the same way. `uv run pytest -q`:
820 passed, 1 skipped, 734 subtests.

! **What the annotation was doing meanwhile is worth keeping:**
`unterminated-paragraph-comment` DID fire, so `prove_unchanged` refused the file -- but stages 2
through 5 still handed four reviewers a census saying the file had no code. A refusal at stage 7b
does not protect the reviewers upstream of it.

## Tasks

- [x] T1 | FINISHED | unknown | T1 -- SUPERSEDED. The ordering defect is fixed:
      `_strip_strings` still runs first and still finds the OPENER, but
      `lexer.py:1311-1312` feeds `run_ends` the RAW tail, so the closer is no
      longer blanked.
- [x] T2 | FINISHED | unknown | T2 -- A MEASUREMENT, and it has been re-taken.
      The one-paragraph result is gone: as of 2026-08-23 the same input censuses
      as two paragraphs with `int a = 1;` still in the code.
- [x] T3 | FINISHED | unknown | T3 -- A RECORD of what the annotation caught and
      what it did not. Kept in the Objective: `unterminated-paragraph-comment`
      fired and `prove_unchanged` refused, while stages 2 through 5 had already
      handed out the wrong census.
- [x] T4 | FINISHED | unknown | T4 -- A RECORD, not a task: `/* don't */` is
      ordinary English, so this was never an exotic input. That is why the fix
      carries the language list -- javascript, typescript, sql, lua and ruby,
      every language with `'` in `quotes` and no `char_quotes`.
