# The galley can overwrite the file under review, and the compositor reads through a normaliser

```
Status:   open
Progress: 1 of 5 tasks done
Owner:    backend
Requires-Roy: true
Raised:   2026-08-22 (C:/Program Files/Git/code-review high round 3 and /simplify round
          2, 2026-08-22 -- the write path, which is the one place a defect reaches disk)
RE-VERIFIED: 2026-08-23 — 2026-08-23. Task 1 is FIXED and ticked -- the destructive case
             is refused: galley.py:365 checks out.is_relative_to(repo) or
             repo.is_relative_to(out) and prints REFUSED, with the comment above it
             recording that is_relative_to is true of a path and itself, which is why
             the old containment test passed on an overlap. ! Tasks 2, 4 and 5 all still
             exist in the code -- _vacate is still there with the c-sits-beside-code
             hazard noted at galley.py:192, lossless and identity are still separate at
             compositor.py:290 and :327, and compositor.py still infers the source was
             never read from an empty list. Task 3 is a measurement that already answers
             itself: reading BYTES, 3,015 of 3,020 corpus files are identical, so the
             mechanism is right and only the read path translates newlines.
```

## Objective

The galley can overwrite the file under review, and the compositor reads through a normaliser.

## Tasks

- [x] !! galley.py:316 IS DESTRUCTIVE AND EXITS 0. Containment asks only whether
      target is_relative_to(out); NOTHING asks whether --out is disjoint from
      --repo. On overlap the target IS the source file, the guard passes, and
      compositor.draft OVERWRITES the file under review, printing 1 page(s) set. !
      The comment at :310-315 records this exact outcome from 2026-08-17 -- the
      absolute-path cause was fixed and the OVERLAP cause was not
- [ ] galley.py:157 -- reset vacates leading unconditionally, but a c sits BESIDE
      code, so dropping a trailing comment eats the blank line below it.
      prove_unchanged cannot see it (the AST is identical) so it lands silently at
      7b, and resets own docstring says a c TAKES ONLY THE PROSE. ! Written
      2026-08-22 by the same change that introduced _vacate
- [ ] * compositor.lossless and identity read via Path.read_text, which universal-
      newline-translates, so line_endings() can NEVER answer CRLF from the gate.
      MEASURED 2026-08-22: 2,904 of 3,020 corpus files are CRLF on disk and
      read_text reports zero. ! Re-measured reading BYTES: 3,015 of 3,020
      identical, unchanged -- so the mechanism is right and what was untested is
      the newline axis. repo.read_raw exists for exactly this and says so; galley
      fixed it at its OWN call site and left the next caller to re-hit it
- [ ] compositor.lossless and identity share a 12-line prologue, and main runs it
      twice per file
- [ ] compositor.py:220 infers *the source was never read* from an EMPTY LIST,
      because page_for throws the fact away rather than stating it
