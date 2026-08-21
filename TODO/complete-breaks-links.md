# todo_tool complete breaks a file's relative links when it moves it

```
Status:   open
Progress: 0 of 4 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-21 (the link sweep prompted by the /code-review xhigh of 2026-08-21)
```

## Objective

todo_tool complete breaks a file's relative links when it moves it.

## Tasks

- [ ] !! MEASURED 2026-08-21: 13 of 274 relative links under docs/ and TODO/ are
      broken, and every one is a TODO that moved to `completed/`. A file at
      `TODO/a.md` linking a sibling as `b.md` still says `b.md` after the move,
      where the sibling is now a directory up.
- [ ] `complete_todo` moves the file and rewrites the README row. It does not
      touch the file's own body, so a `[x](sibling.md)` link goes dead at exactly
      the moment the work is archived -- when nobody is looking at it again.
- [ ] ! Four MORE were in live documents and are fixed: the 0.2.5 plan's R0 (four
      links, all TODOs this branch completed) and `TODO/move-and-correct-
      compose.md`. Those mattered because CLAUDE.md's release gate is that anyone
      can check a box 'including someone who did none of the work'.
- [ ] ! THE SWEEP IS THE OTHER HALF. Nothing checks a relative link, which is why
      16 accumulated unseen. A checker belongs beside `check_vocabulary.py`; it is
      the same shape as `dead-names-ungated` and could ship in the same gate.
