# An address is not unique across two paths that dot alike

```
Status:   open
Progress: 3 of 3 tasks closed
Owner:    session
Requires-Roy: false
Raised:   2026-08-19 (the seven-agent address review, 2026-08-19)
Flagged:  2026-08-19 — task 2 owes a ruling -- refuse the collision at census time, or
          report SHARED across paths at check time; task 3 corrects the docs with
          whatever is ruled
Ruled:    2026-08-19 — Roy: 'lets use an illegal symbol for the separator then ... that
          makes it trivial.' The separator is ':'. Tasks 1 and 2 are SUPERSEDED -- there
          is no collision for --check to see and none to refuse, because two paths can
          no longer flatten alike.
```

## Objective

!! **`a/b.py` AND `a.b.py` BOTH DOT TO `a.b.py`, SO `a.b.py@a0` NAMES TWO BLOCKS IN TWO FILES --
AND `--check` PASSES IT.** Measured 2026-08-19: `4 of 4 blocks addressed`, rc 0, no SHARED row.
Then `--resolve a.b.py@a0` answers *"no file in this census dots to 'a.b.py'"*. **The gate
certifies what the resolver then refuses.**

**The dotted form was chosen so mixed languages could not collide.** Roy, 2026-08-18: *"we could
have mixed languages in the system with the same names that without that we are back to
collisions."* It solves that and reintroduces the same failure on directory separators, because
`/` and `.` both become `.`.

! **`undot` refuses the ambiguity correctly** -- it returns "" when two real paths dot alike
rather than picking one -- so nothing is silently mis-resolved. What is wrong is that the
collision is ADMITTED at census time and only surfaces later, somewhere else.

! **`_check` cannot see it by construction**: it iterates `for path in sorted({paths})` and
compares only within one path, so a cross-file collision is never in scope. `addresser.py` and
`docs/addressing.md` both claim a complete path cannot collide.

## Tasks

- [x] T1 | FINISHED | unknown | !! **`_check` compares only WITHIN one path.**
      It iterates `for path in sorted({paths})`, so a cross-file collision is
      never seen. Measured: `4 of 4 blocks addressed`, rc=0, no SHARED -- then
      `--resolve a.b.py@a0` answers *"no file in this census dots to ..."*.
      **The gate certifies what the resolver then refuses.**
- [x] T2 | FINISHED | unknown | **`undot` refuses the ambiguity correctly**, so
      the address is admitted and fails somewhere else later. Decide where the
      refusal belongs: at census time (name the collision and stop) or at check
      time (report SHARED across paths).
- [x] T3 | FINISHED | unknown | ! `addresser.py` claims *"a complete path cannot
      collide"* and `docs/addressing.md` repeats it. Correct both with whatever
      is ruled.
