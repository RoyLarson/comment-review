# A move onto its own address reaches the docket as a bare delete

```
Status:   open
Progress: 1 of 3 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-30 (2026-08-30, by an agent writing collator.py's prose from the code
          alone, with no access to the vocabulary, the docs or the prototype)
Landed:   2026-08-30 — T1 landed in f17b712 -- desk/mark.py _destination_problems
          refuses a move whose claim.to equals its address, by name. T2 and T3 remain
          and are both reshaped by the composite ruling (decision-log Process: 56,
          TODO/move-is-a-composite-mark.md); T3 second half -- a destination the binder
          does not carry -- is that file task 9, a question owed by Roy.
```

## Objective

A move onto its own address reaches the docket as a bare delete.

## Tasks

- [x] T1 | FINISHED | unknown | Refuse `claim.to == address` on a `move`, by
      name. Verify: `desk.mark.parse` returns a named problem for it -- today it
      returns `(mark, [])`, measured.
- [ ] T2 | Prove the docket cannot carry the shape. Verify: a test asserts no
      alteration is a delete with no matching write, and it FAILS against
      today's code, which produces `[('m.py', 'b1', None)]`.
- [ ] T3 | Check the neighbouring shapes. Verify: a `move` across files, and one
      whose `to` names a place the binder does not carry, each reach a named
      outcome rather than a silent delete.
