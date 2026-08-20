# Seven of the eight expectedFailures never reach the code they name

```
Status:   open
Progress: 0 of 3 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-20 (the branch review of 2026-08-20; threatens plan box R7)
```

## Objective

Seven of the eight expectedFailures never reach the code they name.

## Tasks

- [ ] !! `tests/test_galley.py` `_gap` looks up an interval by `(original_start,
      original_end) == (2,1)` / `(1,0)` / `(4,3)` -- the RETIRED `(n, n-1)` form.
      The census emits `(None, None)`, so seven raise `AssertionError: no gap
      editing ...` INSIDE THE HELPER and the eighth fails comparing `(None,None)`
      to itself. `galley.splice_range` and `paragraph_matches` are never reached.
- [ ] !! SO THE MECHANISM I WROTE INTO THAT CLASS DOCSTRING DOES NOT EXIST. It
      claims *"each reports an UNEXPECTED SUCCESS the moment the galley works from
      addresses, which is how this suite is meant to announce that work landing."*
      Fixing the galley would flip NONE of them.
- [ ] !! THIS MAKES PLAN BOX R7 UNJUDGEABLE -- *"no expectedFailure survives this
      plan"* -- because the eight cannot pass by fixing what they name. Either the
      helper is repaired to look the place up by ADDRESS, or the tests are
      rewritten against the contract the galley will actually have.
