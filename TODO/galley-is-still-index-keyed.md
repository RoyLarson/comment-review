# The galley is the last index-keyed interface, at the write boundary

```
Status:   open
Progress: 2 of 3 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-19 (the seven-agent address review, 2026-08-19)
Superseded: 2026-08-19 — tasks 1-2 done (galley.py:331 resolves by entry_for(address);
            SKILL.md:924 documents the address form). The remaining box is an
            observation, not work. ! The MECHANISM is superseded by write-by-series in
            b-foliator-uninitialised: splice sorts on (start, end, column, replacement)
            and applies descending BY LINE, which is what the a->b->c ruling replaces.
Measured: 2026-08-20 — 2026-08-20 -- THE CALLER CANNOT EXPRESS THE ORDER AT ALL.
          `splice` re-sorts its own `edits` argument, so `[a, b]` and `[b, a]` produce
          byte-identical output. The tie then falls to the ASCII of the replacement
          text: `//` < `///` puts Rust's gap prose outside the doc comment and satisfies
          the a -> b -> c ruling BY ACCIDENT, while `\"\"\"` < `#` applies Python's
          comment first and leaves the docstring ABOVE it, which does not. ! Roy,
          2026-08-20, on why the order is universal: *"a has to be put in first because
          it is the 'inner most' documentation -- the b gets applied in the rows
          outside-beyond it."* Two edits inserting at ONE point are not a conflict; the
          second lands above the first. So the fix is a sort key carrying the SERIES,
          and `overlaps` must stop reading two empty ranges at one line as a clash.
Corrected: 2026-08-20 — 2026-08-20 -- the note above claimed `overlaps` must stop
           reading two empty ranges at one line as a clash. IT ALREADY DOES NOT.
           Measured: `a1 + b3` both inserting at 4, and `a0 + b0 + b1` all inserting at
           1, both return no clash, because an insert's range is `(n, n-1)` and the test
           is `b_start <= a_end`. Two genuinely overlapping paragraph ranges still
           clash. ! So the work here is the SORT KEY alone -- `overlaps` needs nothing.
Measured: 2026-08-20 — 2026-08-20, the ORDER, measured rather than reasoned. ! A REPLACE
          must be applied before an INSERT at the same line, or the insert's own text is
          what gets replaced. Measured on `int b = 2;  /* old */`: applying the `b`
          first then the `c` produced `/* the b:   /* the c */` -- the b's prose
          truncated at the column with an opener welded on -- while `/* old */`, the
          text the c was meant to replace, survived untouched on the next line. An `a`
          fails identically: `\"\"\"wrapper's d  # counts the calls`. !! IT IS NOT ABOUT
          WRAPPED COMMENTS. A single-line `c` corrupts the same way; wrapping only made
          it visible. !! AND HALF THE RULE IS ALREADY STRUCTURAL: `splice` sorts
          `(start, end, ...)` descending, an insert has `end < start` and a replace has
          `end == start`, so a replace already sorts above an insert at one line and is
          applied first. So `c` before `a` and `b` holds today by construction. ! THE
          ONLY UNDECIDED STEP IS `a` vs `b` -- identical tuples, tie falls to the
          replacement text's ASCII. Roy, 2026-08-20: *"the decision on ordering is all
          galley work coming up on how it resets the paragraphs. The decision can be
          made when we have these other pieces setup correctly."* DEFERRED to that work;
          the measurements are here so it does not have to be re-derived.
Updated:  2026-08-20 — ordering deferred to the galley rewrite; the measurements that
          decide it are recorded above
```

## Objective

!! **`galley.py --edits` TAKES `{"<census index>": ...}` AND NO RECORD CARRIES AN INDEX ANY MORE.**
So between stage 5 and the galley there is now a HAND conversion from address to census position,
with nothing checking it -- at the step that produces the artifact a human approves at 7a.

**An off-by-one there splices the wrong lines into the proof.** That is the one artifact the
author actually rules on, and the galley exists precisely because *"the splice is the first time
anyone sees the two together."*

! **It sits exactly at the round-2 boundary**, where `re-review.md` says *"THE ADDRESS DOES
CARRY, and it is what to quote back."* The one place the rebuild's property matters most is the
one place it is discarded.

! **The bridge already exists and is not wired.** `foliator.resolve(address, blocks)` returns
exactly the 1-based indices `galley` wants, and `record.entry_for` resolves an address to its
entry -- but `galley` imports neither. `SKILL.md` still documents the index form at the 5b/6b step.

## Tasks

- [x] **Accept an address key through `record.entry_for`; keep `int` for held
      runs.** `foliator.resolve` already returns exactly the 1-based indices
      needed and is called only from inside foliation; galley imports neither
      foliation nor record.
- [x] **`SKILL.md` still documents the index form** at the 5b/6b galley step.
- [ ] ! It sits exactly at the round-2 boundary, where `re-review.md` says *"THE
      ADDRESS DOES CARRY"* -- so the one place the rebuild's property matters most
      is the one place it is discarded.
