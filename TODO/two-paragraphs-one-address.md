# Two prose paragraphs in one gap answer to the SAME address

```
Status:   open
Progress: 0 of 4 tasks done
Owner:    session
Requires-Roy: true
Raised:   2026-08-21 (the /code-review xhigh of 2026-08-21, focused on the file-to-
          census route)
```

## Objective

Two prose paragraphs in one gap answer to the SAME address.

## Tasks

- [ ] !! MEASURED 2026-08-21 on a four-line C file. `/* Copyright ... */` then
      `/** Adds. */` then `int add(...)`: both paragraphs go through
      `foliation.above()` into the gap above the declaration and both census as
      `lic.c@b0`. `record.py --seed` emits two records with the same `place` and
      the same `anchor`, and the record format has NO field that tells them apart.
- [ ] !! IT REFUSES CORRECT WORK. `entry_for` returns the FIRST, so a `correct` on
      `/** Adds. */` is checked against the licence header and `verdicts.py` exits
      1 with 'the sentence ruled on is not in lic.c@b0'. Both findings were right.
- [ ] ! IT FALSIFIES TWO SHIPPED CLAIMS: `record.entry_for`'s docstring says 'an
      address identifies exactly one paragraph', and `held.py` cites '0 shared
      over 6,180'. Both were measured on a Python-only tree, where the `a` series
      takes the docstring out of the gap.
- [ ] * RULING WANTED: what makes them distinct. The `a` series solved this for
      Python by giving a docstring its own place -- but see `a-series-never-fills-
      outside-python`, which is why that does not happen here. Fixing that one may
      close this one.
