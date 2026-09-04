# mark.py validates dicts instead of defining the Mark the-mark.md specifies

```
Status:   open
Progress: 7 of 7 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-29 (2026-08-29, Roy, on the max-effort sweep: "mark.py should define a
          Mark that follows 'the_mark.md' that is not negotiable. I expected that
          'the_mark.md' is the definition of the structure not an unsanctioned
          adapter/facade that is neither")
```

## Objective

mark.py validates dicts instead of defining the Mark the-mark.md specifies.

## Tasks

- [x] T1 | FINISHED | unknown | Define `Mark` in `desk/mark.py` with exactly the
      fields `docs/the-mark.md` names. Verify: every field in that file's table
      is an attribute of `Mark`, and a test reads the table rather than
      restating it, so adding a row there fails until the type follows.
- [x] T2 | FINISHED | unknown | Parse ONCE, at the boundary. Verify: one
      function turns a dict into a `Mark` or into named problems, and there is
      no third outcome -- no half-valid mark reaches a consumer, which is what
      `problems(where, mark: dict)` allows today.
- [x] T3 | FINISHED | unknown | The ruling field is `instruction`, typed
      `Instruction`. Verify: `INSTRUCTIONS[m.instruction]` resolves with no
      str-to-enum cast, and `uv run ty check src/comment_review/` reports zero
      'str is not assignable to Instruction' errors -- there are 10 in
      `desk/collator.py` today.
- [x] T4 | FINISHED | unknown | Every consumer takes a `Mark`, not a dict.
      Verify: no `.get("mark")` and no ["mark"] subscript remains anywhere under
      `src/comment_review/` -- 15 sites on 2026-08-29.
- [x] T5 | FINISHED | unknown | `flows/marks.py`'s silent skip is gone. Verify:
      a mark whose instruction is missing is REFUSED BY NAME. Today `if
      mark.get("mark") is None: continue` drops it before `desk.mark.problems`
      ever sees it, and it is recounted as a place nobody looked at.
- [x] T6 | FINISHED | unknown | Correct `docs/the-mark.md`'s field table: the
      row reading `mark` becomes `instruction`. Verify: the file and the code
      name the same seven fields, and no field is spelled two ways.
- [x] T7 | FINISHED | unknown | A mark written from `reviewer-brief.md` VERBATIM
      is accepted. Verify: saving the brief's own worked example and running
      `mark --check` on it exits 0 -- it exits 1 today, on every field.
