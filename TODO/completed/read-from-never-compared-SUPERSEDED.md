# Nothing compares a returned edit_copy's read_from against the binder it was seeded from

```
Status:   open
Progress: 0 of 2 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-30 (found 2026-08-30 while specifying SP-1; flows/marks.py:136-141
          names the gap itself and says the comparison belongs wherever the two meet --
          which is collate, once one exists)
```

## Objective

Nothing compares a returned edit_copy's read_from against the binder it was seeded from.

## Tasks

- [ ] Implement the comparison where the binder and the returned copies first
      meet. Verify: a copy whose read_from names a different root or revise than
      the binder is reported by name, and one seeded from that binder passes.
- [ ] Update the note at flows/marks.py:136-141 to name the function that makes
      the comparison. Verify: the comment no longer says only that it belongs
      wherever the two meet.
