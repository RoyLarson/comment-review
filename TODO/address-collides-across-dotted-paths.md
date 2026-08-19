# An address is not unique across two paths that dot alike

```
Status:   open
Progress: 0 of 3 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-19 (the seven-agent address review, 2026-08-19)
```

## Objective

An address is not unique across two paths that dot alike.

## Tasks

- [ ] !! **`_check` compares only WITHIN one path.** It iterates `for path in
      sorted({paths})`, so a cross-file collision is never seen. Measured: `4 of 4
      blocks addressed`, rc=0, no SHARED -- then `--resolve a.b.py@a0` answers
      *"no file in this census dots to ..."*. **The gate certifies what the
      resolver then refuses.**
- [ ] **`undot` refuses the ambiguity correctly**, so the address is admitted and
      fails somewhere else later. Decide where the refusal belongs: at census time
      (name the collision and stop) or at check time (report SHARED across paths).
- [ ] ! `addresser.py` claims *"a complete path cannot collide"* and
      `docs/addressing.md` repeats it. Correct both with whatever is ruled.
