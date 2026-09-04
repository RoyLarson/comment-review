# The galley can overwrite the file under review, and the compositor reads through a normaliser

```
Status:   open
Progress: 4 of 11 tasks closed
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
Split:    2026-08-23 -- every box cut to two lines. The read-path box was two call sites
          and the prologue box two changes, so five boxes became seven; a second pass
          took the newline test out of the two read-path boxes, split the prologue
          extraction from its call sites, and split `page_for` recording the fact from
          the refusal that reads it -- seven became ten
```

## Objective

**The galley can overwrite the file under review, and the compositor reads through a
normaliser.** This is the write path -- the one place a defect reaches disk -- so a defect here
lands at stage 7b with every gate green.

!! **THE DESTRUCTIVE CASE IS REFUSED, SINCE 2026-08-23.** `galley.py:365` asks
`out.is_relative_to(repo) or repo.is_relative_to(out)` and prints `REFUSED`. ! The comment above
it states the cause the old test missed: **`is_relative_to` is true of a path and itself**, so a
containment test alone passed on an overlap and `compositor.draft` overwrote the file under
review, printing `1 page(s) set` and exiting 0. VERIFIED at `galley.py:361-368`: both directions
are tested and the run is REFUSED WHOLE.

!! **AND A `c` NO LONGER GIVES UP ITS LEADING.** `galley.py:197-202` reads the cue off the
address and passes `_vacate` a leading of `None` where the cue is a `c` -- `ON = "c"`,
`addresser.py:161`. The reason is at `galley.py:191-196`: **a `c` sits BESIDE code**, so dropping
the trailing comment leaves the statement where it was and the blank below separates that CODE
from what follows. ! `prove_unchanged` cannot tell the two apart, because the AST is identical
either way, which is why it would have landed silently at 7b. ! The hazard is now a comment
recording what was fixed, not the fix that is missing.

! **WHAT IS LEFT IS THE COMPOSITOR'S READ PATH AND ITS TWO GATES**, and none of it needs a
ruling -- the mechanism was measured right and the fix is named in the module that owns it.

### The read path, MEASURED

`compositor.lossless` and `compositor.identity` both call `Path.read_text` -- `compositor.py:304`
and `:335` -- which universal-newline-translates, so `line_endings()` can NEVER answer CRLF from
the gate. MEASURED 2026-08-22: **2,904 of 3,020 corpus files are CRLF on disk and `read_text`
reports zero.** ! Re-measured reading BYTES: 3,015 of 3,020 identical, unchanged -- so the
mechanism is right and what was untested is the newline axis.

! `repo.read_raw` exists for exactly this (`repo.py:25`) and says so; **galley fixed it at its
OWN call site and left the next caller to re-hit it.**

### The shared prologue, and what `main` pays for it

`compositor.lossless` (`:303-313`) and `compositor.identity` (`:334-344`) each read the file,
resolve the language, build the page and set it, and `main` runs the pair twice per file.

### The empty page is inferred from an empty list

`compositor.py:231` reads `if not page.cues.reading and page.text` and raises *"the page has no
places -- its source was never read"* -- an inference from an EMPTY LIST, because `page_for`
throws the fact away instead of recording it. ! The stake is at `:237-246`: MEASURED 2026-08-21
on `sentry/src/sentry/api/paginator.py`, **884 lines in and 0 characters out, silently**, and 4
files in `corpora/` are in that state today.

## Tasks

- [x] T1 | FINISHED | unknown | T1 -- FIXED 2026-08-23. `galley.py` was
      destructive and exited 0; both directions of the overlap are now tested
      and the run is REFUSED WHOLE. Stated in the Objective.
- [x] T2 | FINISHED | unknown | T2 -- FIXED 2026-08-23. `reset` vacated leading
      unconditionally and a `c` sits BESIDE code; `owns_leading` now withholds
      it. Stated in the Objective.
- [x] T3 | FINISHED | unknown | T3 -- **Make `compositor.lossless` read through
      `repo.read_raw`** (`compositor.py:304`). Verify: the `lossless` site calls
      no `read_text`.
- [x] T4 | FINISHED | unknown | T4 -- **Make `compositor.identity` read through
      `repo.read_raw`** (`compositor.py:335`). Verify: `grep -n "read_text"
      compositor.py` returns nothing.
- [ ] T5 | T5 -- **Test the newline axis the gates never saw.** Verify: a CRLF
      fixture makes `line_endings()` answer CRLF, and the test fails on HEAD.
- [ ] T6 | T6 -- **Extract the prologue the two gates share** -- read, resolve
      the language, build the page, set it. Verify: one function does all four.
- [ ] T7 | T7 -- **Make `lossless` and `identity` call that one function.**
      Verify: neither repeats the four steps.
- [ ] T8 | T8 -- **Make `main` read each file once** rather than running the
      pair twice per file. Verify: a run over one file performs one read of it.
- [ ] T9 | T9 -- **Make `page_for` RECORD whether the source was read**, rather
      than throwing the fact away. Verify: a page built from an unread source
      carries that fact.
- [ ] T10 | T10 -- **Make `compositor.py:231` refuse on that fact, not on an
      empty list.** Verify: an empty file with no text still sets back as empty.
- [ ] T11 | Delete results.compositor.approve, or name the caller that will use
      it
        > 2026-08-31 MEASURED 2026-08-31 while landing P45: grep over src/ and tests/
        > 2026-08-31 finds no caller. It is the only remaining write over a REAL file,
        > 2026-08-31 so what it does is a ruling, not a cleanup.
        > 2026-09-03 RULED DELETE by Roy 2026-09-03 -- Process 80
        > 2026-09-03 the or name the caller branch is gone: no piece may write
        > 2026-09-03 the work is only-a-flow-reaches-the-machine T1, and four more
