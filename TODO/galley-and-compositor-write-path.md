# The galley can overwrite the file under review, and the compositor reads through a normaliser

```
Status:   open
Progress: 20 of 33 tasks closed
Owner:    backend
Requires-Roy: true
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
- [ ] T12 | Update the reread step in flows/revise so a drop that empties a
      whole place is not looked up after. Verify: a drop of a whole b place sets
- [ ] T13 | Update revise.pull so the galley copies the tracked files, not the
      checkout wholesale with corpora and the venv
        > 2026-09-07 2026-09-07: 424 MB partial galley, 1,948 path errors
- [ ] T14 | Update revise.pull so a copy that fails part way leaves no partial
      --out behind
        > 2026-09-07 pull's docstring says a stopped run leaves no half-set; it did
- [x] T15 | RULED Process: #110 -- the working tree, since the system runs on uncommitted work | cfe76f33 | Decide
      whether the galley is pulled from the working tree's bytes or from git,
      since this tree mixes CRLF and LF per file
- [-] T16 | SUPERSEDED -- the write path takes a schedule and pages, not a binder; the flow verifies before handing over | 90e1df5a | Update
      proof so an address the binder does not carry is refused rather than
      drafted without
        > 2026-09-07 proof drafted 5 pages with b7's comment on none, exit 0
- [x] T17 | RULED Process: #110 -- the compositor keeps it; the chief removes on review | cfe76f33 | Decide
      whether the compositor keeps a leading blank a change writes at a gap, or
      the brief stops asking for one
        > 2026-09-07 brief says write the blank lines; the setter dropped a leading one
- [-] T18 | SUPERSEDED by Addressing: #23 -- a role writes no leading, so there is none to keep | f850c321 | Update
      the compositor to keep the leading a change writes at a gap. Verify: a
      change given a leading blank is set with it, per Process 110
- [x] T19 | galley._vacate empties raw_lines alone | 4ce9605d | Delete the
      leading half of galley._vacate so a drop empties the b alone. Verify: no d
      is written by the galley, per Addressing 22
- [x] T20 | set_page drops the leading under a vacated place | 4ce9605d | Update
      the compositor to drop a leading whose place is vacated. Verify: an
      unedited round trip stays byte-identical
        > 2026-09-08 Addressing 19's absence rule first fired on unedited composes
- [ ] T21 | Update galley.py's docstring, which claims it sets text as files.
      Verify: it says it alters Paragraphs on a Page and writes none
        > 2026-09-08 The compositor sets the Page into a proof; the galley writes none
- [x] T22 | RULED Addressing: #24 -- unavoidable; matter is a guess by position | aea75e34 | Decide
      whether a drop may leave a comment flush under front matter; after an a0
      drop, # note re-reads into f0
        > 2026-09-11 Set at compositor.py:275; test_compositor.py:280 asserts it
        > 2026-09-11 Not introduced by 4ce9605d: the old galley.reset did the same
- [x] T23 | the pointer names the test that holds the c exclusion | 4326b793 | Update
      compositor.py:215-218 so it stops sending the reader to galley._vacate,
      which no longer says why c is excluded
- [x] T24 | galley.py says kind and held lines; compositor 203-208 already did | 4326b793 | Update
      the comments saying the drop rule keys on kind alone; it keys on kind and
      empty raw_lines
        > 2026-09-11 compositor.py:204-207, :274; galley.py:137, :142, :202
- [x] T25 | quotation replaced by the Addressing 22 cite; test matches vacated | 4326b793 | Update
      compositor.py:268-274 so the quoted ruling is whole and its stated test
      matches the check at :275
- [x] T26 | describes the lookup plus the drop and add checks | 4326b793 | Update
      compositor.py:164-178; its drop half contradicts :248-251 and its add half
      the rule at :277
- [x] T27 | says every site reads .cue | 4326b793 | Update galley.py:97-98,
      which says every site takes [1] where the code reads .cue
- [x] T28 | no bang prefix or caps run left in the nine | 03908eb3 | Update the
      nine paragraphs 4ce9605d opened with a bang prefix and capitalised runs,
      per Process 105 and 106
        > 2026-09-11 compositor.py:203, :210, :215, :268; galley.py:133, :139, :201
        > 2026-09-11 test_galley.py:134, :151
- [x] T29 | deleted; test_only_the_place_changes covers a0 | 4326b793 | Delete
      test_a_drop_leaves_the_leading_alone at test_galley.py:146-159, or name
      what it catches beyond :131
        > 2026-09-11 the :131 test already asserts the leading unchanged on every drop
- [x] T30 | b1 drop test; an a0-only rule passes the old test and fails it | 6fd87377 | Implement
      a second test of the drop rule at compositor.py:275 on a place other than
      a0
        > 2026-09-11 only test_compositor.py:270 catches it, and only at a0
- [x] T31 | the paragraph now says no key changes on a drop | d19de5b8 | Update
      compositor.py:159-162, which says the survivor of a drop takes a new key
      where :175-178 says it needs none
        > 2026-09-11 at 4326b793: new key claimed at :161, no new key at :176
- [ ] T32 | Update proof_setter.py:465-470 so a draft that re-reads with a
      different structure is named as that
        > 2026-09-11 smoke run: an unindented a2 lost every cue; b1 was named
- [?] T33 | Decide whether a docstring's indentation is the role's to write or
      the compositor's to supply
        > 2026-09-11 check, collate, disposition all passed an unindented a2 add
        > 2026-09-11 Addressing 23 moved leading to the compositor the same way
