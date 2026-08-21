# Two prose paragraphs in one gap answer to the SAME address

```
Status:   open
Progress: 0 of 4 tasks done
Owner:    session
Requires-Roy: true
Raised:   2026-08-21 (the /code-review xhigh of 2026-08-21, focused on the file-to-
          census route)
Traced:   2026-08-21 — 2026-08-21 -- IT IS NOT THE FRONT-MATTER AMBIGUITY, and it is not
          one bug with a-series-never-fills-outside-python either. TRACED: attach()
          routes on three facts in order -- declares >= 0 -> the declaration's a; the
          MATTER annotation -> f0; original_column -> that line's c; else above() -> a
          b. Both paragraphs fail the first two and land in the same gap. ! Even a
          perfect mark_matter would only move the licence header out of the way by luck:
          the docstring would still be in a b place and would collide with any ordinary
          comment above the same declaration -- '// helper below' over '/** Adds. */'
          collides with no front matter involved. !! AND WIRING declares DOES NOT CLOSE
          IT FOR C, C++ OR SQL. Those three rows carry an EMPTY declares tuple,
          deliberately -- Roy: a C function opens with its RETURN TYPE, so the keyword
          list could never be complete and a spurious a renumbers every a below it.
          MEASURED: declarations() returns [] for C and [(0,1),(3,3)] for Rust. So in C
          there is no a place for a doc comment to take and it MUST share the gap. * The
          ruling is narrower than first filed: what should an address mean when two
          paragraphs occupy one gap and the language offers no second place?
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
