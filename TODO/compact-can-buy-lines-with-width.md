# COMPACT can buy lines with width, and nothing stops it

```
Status:   open
Progress: 0 of 6 tasks done
Owner:    session * Roy (* 1 ruling)
Raised:   2026-08-17, on stage 6's FIRST exercise -- it returned two blocks at exactly the cap
          by writing lines 20 columns wider than anything in the file
```

## Objective

**A cap counts LINES. Widening a line removes a line and loses nothing, so it is the cheapest
way to satisfy a cap -- and `compact.md` says nothing about width.** Zero occurrences of
`width`, `column` or `character` in the file.

Measured on the first run to reach stage 6: it returned both over-cap blocks at exactly 6 lines,
written at **98-100 columns**, in a file whose 144 comment lines measure **median 76, max 80,
and 0 over 80**. The published limit was wider than the habit, so nothing was violated and the
result does not read like the file.

!! **This is the failure `SKILL.md` 1.2 already names, arriving at the other end of the run:**
*"matching the number while counting differently produces a file that claims to comply and does
not."* Stage 6 matched the number it was given and counted a different thing.

! **It is structural, not a lapse.** Every other route to fewer lines costs information --
cutting a clause, dropping a citation, deleting provenance -- and `compact.md` forbids all of
them, at length and correctly. Widening costs nothing. An agent told to minimise lines and
handed no width will take the free move every time.

! The compact agent FLAGGED it rather than deciding it, which is what its contract asks for.
The defect is that it had to.

## ! The published width is not the observed one, and the style sheet is where that belongs

The run's repo permitted 104 columns and wrote 76-80. `SKILL.md` 1.2 is right to refuse an
invented cap -- *"a number you chose becomes a project fact in the output"* -- so the fix is not
a measured width passed as a flag.

**The STYLE SHEET already holds what the tree DOES**, measured: the documentation templates come
from 1.3 the same way. An observed wrap is that kind of fact, and the style sheet is already in
stage 6's input contract. What is missing is any instruction to read it.

## !! WIDTH is not the only free move -- KIND is the other one

A `#` run has a cap. A docstring does not: *"A `#` comment is governed by LENGTH; a docstring by
FORMAT."* So **converting a comment into a docstring satisfies a cap at zero information cost**,
exactly as widening does. Two escape hatches, same shape, neither named anywhere.

! The line between legitimate and dodging is thin and has to be written down: relocating prose
into a docstring is a real `move` **when a declaration genuinely owns the rule**, and is
cap-dodging when the docstring is the nearest place the cap cannot reach.

! The 2026-08-17 run stayed on the right side of it and shows how: it did NOT propose the
relocation. It reported that no function owns the rule -- three rules stacked at one call site
because clear-on-close has no home -- and named the owner that should exist. That is a code
change, so it went to `CODE CONCERNS` and not to a verdict. `compact.md` had predicted the
diagnosis in those words: *"usually a rule with no owning function, so every site performing
part of it re-explains the whole."*

## Tasks

- [x] * **RULED 2026-08-17: WHICHEVER IS LESS.** Roy's words. Both the published width and the
      observed wrap bind stage 6, and the tighter one wins. ! That is what forbids the measured
      trade: the repo published 104, the tree writes 76-80 over 144 lines, so 80 binds and the
      98-column reflow is refused. ! A block that cannot reach the cap under the tighter bound
      is `compact.md`'s existing answer -- report it, name the owner, do not cut.

      Was: Rule on whether stage 6 is bound by an OBSERVED wrap at all, or only by a published
      one. ! Binding it to the observed wrap means a run can refuse to reach a published cap
      because of a habit nobody wrote down -- which is a real cost, and it is the answer
      `compact.md` already gives for every other conflict: report the block, do not resolve it
      by cutting. The same answer extends here, but it should be ruled rather than assumed.

- [ ] Say in `compact.md` that a block may not change KIND to escape the cap, and state the
      test: a `move` into a docstring is legitimate when the declaration OWNS the rule, and is
      cap-dodging when the docstring is merely where the cap does not reach. ! Stage 6 cannot
      make that call itself -- it holds one block and its kind -- so the rule may have to be
      that stage 6 REPORTS the conflict and never re-kinds anything, which is what it already
      does for every other conflict.

- [ ] Say in `compact.md` that lines may not be widened to buy a line. ! Whatever the ruling
      above, this one holds: reaching a cap by reflowing wider is not compaction, and the file
      currently argues against every alternative while leaving this one unnamed.

- [ ] Add the observed comment wrap to the STYLE SHEET's measured section, beside the templates,
      and state it is measured rather than published. ! It must not become a flag: `census.py`
      takes no width and 1.2 refuses an invented number.

- [ ] Decide what stage 6 reports when in-cap and at-habit conflict. On the measured run the
      block was 7 lines at the file's wrap and 6 at 98 columns, and the operator took the code
      finding -- a rule with no owning function, three rules stacked at one call site. That is
      `compact.md`'s own answer and it worked; it should be written as the rule for this case.

- [ ] ! Record what stage 6 got RIGHT on the same run, so a later pass does not rewrite the
      good part: it refused to cut evidence, it reported the conflict instead of resolving it,
      and the move-then-compact ordering was validated -- block 3040 was 13 lines before a `move`
      split it and 8 after, so a compaction run before the move would have condensed a block
      that was about to become two.
