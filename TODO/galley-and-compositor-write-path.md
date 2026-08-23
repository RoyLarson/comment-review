# The galley can overwrite the file under review, and the compositor reads through a normaliser

```
Status:   open
Progress: 0 of 5 tasks done
Owner:    comment-review
Requires-Roy: true
Raised:   2026-08-22 (C:/Program Files/Git/code-review high round 3 and /simplify round
          2, 2026-08-22 -- the write path, which is the one place a defect reaches disk)
```

## Objective

The galley can overwrite the file under review, and the compositor reads through a normaliser.

## Tasks

- [ ] !! galley.py:316 IS DESTRUCTIVE AND EXITS 0. Containment asks only whether
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
