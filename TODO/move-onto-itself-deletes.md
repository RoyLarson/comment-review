# A move onto its own address reaches the docket as a bare delete

```
Status:   open
Progress: 0 of 3 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-30 (2026-08-30, by an agent writing collator.py's prose from the code
          alone, with no access to the vocabulary, the docs or the prototype)
```

## Objective

A move onto its own address reaches the docket as a bare delete.

## Tasks

- [ ] Refuse `claim.to == address` on a `move`, by name. Verify: `desk.mark.parse`
      returns a named problem for it -- today it returns `(mark, [])`, measured.
- [ ] Prove the docket cannot carry the shape. Verify: a test asserts no
      alteration is a delete with no matching write, and it FAILS against today's
      code, which produces `[('m.py', 'b1', None)]`.
- [ ] Check the neighbouring shapes. Verify: a `move` across files, and one whose
      `to` names a place the binder does not carry, each reach a named outcome
      rather than a silent delete.
