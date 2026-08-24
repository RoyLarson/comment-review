# The galley can overwrite the file under review, and the compositor reads through a normaliser

```
Status:   open
Progress: 2 of 5 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-22 (code-review high round 3 and /simplify round 2, 2026-08-22 -- the
          write path, which is the one place a defect reaches disk)
RE-VERIFIED: 2026-08-23 — 2026-08-23. Task 1 is FIXED and ticked -- the destructive case
             is refused: galley.py:365 checks out.is_relative_to(repo) or
             repo.is_relative_to(out) and prints REFUSED, with the comment above it
             recording that is_relative_to is true of a path and itself, which is why
             the old containment test passed on an overlap.
Triaged:  2026-08-23 — TASK 2 IS ALSO FIXED, and the RE-VERIFIED note above read the
          evidence backwards. It called `galley.py:192` "the c-sits-beside-code hazard
          noted", but :186-196 is the RECORD of the hazard and `galley.py:197-202` is the
          guard: `where = cue_of(address).cue`, `owns_leading = not where.startswith(ON)`,
          and `_vacate` is handed `None` for its leading when it is a `c`. `ON = "c"` at
          `addresser.py:161`. ! Tasks 3, 4 and 5 ARE still live, at re-measured line
          numbers: `read_text` at `compositor.py:304` and `:335`, `lossless` at `:290`
          against `identity` at `:327`, and the empty-list inference at `:231`, not :220.
          ! Requires-Roy cleared: the one `*` box carried no ruling -- the mechanism was
          already measured right and the fix is named in the code that owns it.
```

## Objective

**The galley can overwrite the file under review, and the compositor reads through a
normaliser.** This is the write path -- the one place a defect reaches disk -- so a defect here
lands at stage 7b with every gate green.

!! **THE DESTRUCTIVE CASE IS REFUSED, SINCE 2026-08-23.** `galley.py:365` asks
`out.is_relative_to(repo) or repo.is_relative_to(out)` and prints `REFUSED`. ! The comment above
it states the cause the old test missed: **`is_relative_to` is true of a path and itself**, so a
containment test alone passed on an overlap and `compositor.draft` overwrote the file under
review, printing `1 page(s) set` and exiting 0.

!! **AND A `c` NO LONGER GIVES UP ITS LEADING.** `galley.py:197-202` reads the cue off the
address and passes `_vacate` a leading of `None` where the cue is a `c` -- `ON = "c"`,
`addresser.py:161`. The reason is at `galley.py:191-196`: **a `c` sits BESIDE code**, so dropping
the trailing comment leaves the statement where it was and the blank below separates that CODE
from what follows. ! `prove_unchanged` cannot tell the two apart, because the AST is identical
either way, which is why it would have landed silently at 7b.

! **WHAT IS LEFT IS THE COMPOSITOR'S READ PATH AND ITS TWO GATES**, and none of it needs a
ruling -- the mechanism was measured right and the fix is named in the module that owns it.

## Tasks

- [x] T1 -- !! galley.py IS DESTRUCTIVE AND EXITS 0 -- FIXED 2026-08-23. Containment
      asked only whether target `is_relative_to(out)`; NOTHING asked whether
      `--out` is disjoint from `--repo`. On overlap the target IS the source file,
      the guard passed, and `compositor.draft` OVERWROTE the file under review,
      printing `1 page(s) set`. VERIFIED at `galley.py:361-368`: both directions
      are tested and the run is REFUSED WHOLE.
- [x] T2 -- FIXED, and this was reported live on 2026-08-23 by a note that read the
      comment as the defect. `reset` vacated leading unconditionally, but a `c`
      sits BESIDE code, so dropping a trailing comment ate the blank line below
      it -- invisible to `prove_unchanged`, whose AST is identical either way, so
      it landed silently at 7b. VERIFIED 2026-08-23 at `galley.py:197-202`:
      `owns_leading = not where.startswith(ON)` and `_vacate` takes `None` for a
      `c`'s leading. `ON = "c"`, `addresser.py:161`. The hazard is now a comment at
      `galley.py:191-196` recording what was fixed, not the fix that is missing.
- [ ] T3 -- MAKE `compositor.lossless` AND `compositor.identity` READ THROUGH
      `repo.read_raw`. Both call `Path.read_text` -- `compositor.py:304` and
      `:335` -- which universal-newline-translates, so `line_endings()` can NEVER
      answer CRLF from the gate. MEASURED 2026-08-22: 2,904 of 3,020 corpus files
      are CRLF on disk and `read_text` reports zero. ! Re-measured reading BYTES:
      3,015 of 3,020 identical, unchanged -- so the mechanism is right and what
      was untested is the newline axis. `repo.read_raw` exists for exactly this
      (`repo.py:25`) and says so; galley fixed it at its OWN call site and left the
      next caller to re-hit it. Verify: `grep -n "read_text" compositor.py` returns
      nothing, and a CRLF fixture reaches the gate as CRLF.
- [ ] T4 -- COLLAPSE THE SHARED PROLOGUE. `compositor.lossless` (`:303-313`) and
      `compositor.identity` (`:334-344`) each read the file, resolve the language,
      build the page and set it, and `main` runs the pair twice per file. Verify:
      one function reads and sets, both gates call it, and `main` reads each file
      once.
- [ ] T5 -- MAKE `page_for` STATE THAT THE SOURCE WAS NEVER READ, rather than
      leaving it to be inferred. `compositor.py:231` reads `if not
      page.cues.reading and page.text` and raises *"the page has no places -- its
      source was never read"* -- an inference from an EMPTY LIST, because
      `page_for` throws the fact away instead of recording it. ! The stake is at
      `:237-246`: MEASURED 2026-08-21 on `sentry/src/sentry/api/paginator.py`, 884
      lines in and 0 characters out, silently, and 4 files in `corpora/` are in
      that state today. Verify: the refusal is raised on a fact the page carries,
      and an empty file with no text still sets back as empty.
