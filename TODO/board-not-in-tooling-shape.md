# The board is not in the shape the backlog tooling now reads

```
Status:   deferred
Progress: 0 of 1 tasks closed
Owner:    systems
Requires-Roy: false
Raised:   2026-08-30 (checking this repo's board against the tooling that now owns it,
          2026-08-29)
```

## Objective

`TODO/` was written under a two-mark model -- `[ ]` and `[x]`, with `Requires-Roy`
a header field set by hand. The tooling that now owns the board uses more marks,
gives every task an id, and **derives `Requires-Roy` from a decision mark rather
than storing it**. No file here carries that mark.

!! **SO A FULL RESYNC EMPTIES ROY'S QUEUE. MEASURED 2026-08-29: 218 files
changed and the queue went from 60 rows to 0**, because the flag is derived from
a mark no file has and the derivation correctly found none. It was reverted.
**`scripts/todo_tool.py resync` is what to run in the meantime** -- it still
reads the header field, and this repo's own docs name it.

! **READS AND SINGLE-FILE WRITES ARE FINE**, and were used after that: filing,
noting and rewriting one file each leave the rest of the board alone.

!! **NOTHING HERE IS WORTH DOING UNTIL THE TOOLING SETTLES, WHICH IS WHY THIS
FILE HOLDS ONE DEFERRED BOX AND NOT A PLAN.** `CLAUDE.md`: *a thing whose
dependencies are broken is not worked on, it is refused* -- name the dependency
and leave the box unchecked. ! An earlier version of this file listed five
actionable tasks against that moving dependency and was withdrawn; **four of
them were not this project's work at all.** The label and heading rules are the
tooling's to settle, and one supposed defect here -- a `Progress:` line
disagreeing with its boxes -- is not one: the tool this repo uses reports *all
numbers already agree* on the same file, so the two simply count different
things.

! **WHEN IT IS READY, THIS IS ONE COMMAND, NOT A MIGRATION PROJECT** -- a trial
run over a copy of `TODO/`, then the same over the real one. The trial is the
gate: it must migrate every file and refuse none.

## Tasks

- [ ] T1 | Migrate the board to the task format the tooling reads, once that
      tooling settles. Verify: a trial run over a COPY of TODO/ migrates every
      file and refuses none, and the decision queue holds the same rows before and
      after
