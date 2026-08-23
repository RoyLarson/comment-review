# todo_tool complete breaks a file's relative links when it moves it

```
Status:   open
Progress: 4 of 4 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-21 (the link sweep prompted by the /code-review xhigh of 2026-08-21)
Accepted: 2026-08-21 — 2026-08-21 -- ACCEPTED, not fixed. Roy: 'complete-breaks-links is
          fine. As you stated it orphans the references but only down to the completed
          folder, and if the plan and the todo are completed then it is unlikely that it
          matters except back checking. It also seems like it would require files to be
          rewritten for history, which has been denied several times.' !! THAT LAST
          CLAUSE IS THE DECIDING ONE: repairing a link inside an archived TODO means
          editing a file that records what happened, and this repo keeps a superseded
          thing legible rather than rewriting it. The four that were in LIVE documents
          are fixed. ! The sweep half IS built -- scripts/dead_sweep.py --links reports
          them, so they are read rather than repaired.
```

## Objective

todo_tool complete breaks a file's relative links when it moves it.

## Tasks

- [x] !! MEASURED 2026-08-21: 13 of 274 relative links under docs/ and TODO/ are
      broken, and every one is a TODO that moved to `completed/`. A file at
      `TODO/a.md` linking a sibling as `b.md` still says `b.md` after the move,
      where the sibling is now a directory up.
- [x] `complete_todo` moves the file and rewrites the README row. It does not
      touch the file's own body, so a `[x](sibling.md)` link goes dead at exactly
      the moment the work is archived -- when nobody is looking at it again.
- [x] ! Four MORE were in live documents and are fixed: the 0.2.5 plan's R0 (four
      links, all TODOs this branch completed) and `TODO/move-and-correct-
      compose.md`. Those mattered because CLAUDE.md's release gate is that anyone
      can check a box 'including someone who did none of the work'.
- [x] ! THE SWEEP IS THE OTHER HALF. Nothing checks a relative link, which is why
      16 accumulated unseen. A checker belongs beside `check_vocabulary.py`; it is
      the same shape as `dead-names-ungated` and could ship in the same gate.
