# COMPACT can buy lines with width, and nothing stops it

```
Status:   open
Progress: 0 of 5 tasks done
Owner:    session · Roy (⭐ 1 ruling)
Raised:   2026-08-17, on stage 6's FIRST exercise -- it returned two blocks at exactly the cap
          by writing lines 20 columns wider than anything in the file
```

## Objective

**A cap counts LINES. Widening a line removes a line and loses nothing, so it is the cheapest
way to satisfy a cap — and `compact.md` says nothing about width.** Zero occurrences of
`width`, `column` or `character` in the file.

Measured on the first run to reach stage 6: it returned both over-cap blocks at exactly 6 lines,
written at **98-100 columns**, in a file whose 144 comment lines measure **median 76, max 80,
and 0 over 80**. The published limit was wider than the habit, so nothing was violated and the
result does not read like the file.

⚠⚠ **This is the failure `SKILL.md` 1.2 already names, arriving at the other end of the run:**
*"matching the number while counting differently produces a file that claims to comply and does
not."* Stage 6 matched the number it was given and counted a different thing.

⚠ **It is structural, not a lapse.** Every other route to fewer lines costs information —
cutting a clause, dropping a citation, deleting provenance — and `compact.md` forbids all of
them, at length and correctly. Widening costs nothing. An agent told to minimise lines and
handed no width will take the free move every time.

⚠ The compact agent FLAGGED it rather than deciding it, which is what its contract asks for.
The defect is that it had to.

## ⚠ The published width is not the observed one, and the style sheet is where that belongs

The run's repo permitted 104 columns and wrote 76-80. `SKILL.md` 1.2 is right to refuse an
invented cap — *"a number you chose becomes a project fact in the output"* — so the fix is not
a measured width passed as a flag.

**The STYLE SHEET already holds what the tree DOES**, measured: the documentation templates come
from 1.3 the same way. An observed wrap is that kind of fact, and the style sheet is already in
stage 6's input contract. What is missing is any instruction to read it.

## Tasks

- [ ] ⭐ Rule on whether stage 6 is bound by an OBSERVED wrap at all, or only by a published
      one. ⚠ Binding it to the observed wrap means a run can refuse to reach a published cap
      because of a habit nobody wrote down — which is a real cost, and it is the answer
      `compact.md` already gives for every other conflict: report the block, do not resolve it
      by cutting. The same answer extends here, but it should be ruled rather than assumed.

- [ ] Say in `compact.md` that lines may not be widened to buy a line. ⚠ Whatever the ruling
      above, this one holds: reaching a cap by reflowing wider is not compaction, and the file
      currently argues against every alternative while leaving this one unnamed.

- [ ] Add the observed comment wrap to the STYLE SHEET's measured section, beside the templates,
      and state it is measured rather than published. ⚠ It must not become a flag: `census.py`
      takes no width and 1.2 refuses an invented number.

- [ ] Decide what stage 6 reports when in-cap and at-habit conflict. On the measured run the
      block was 7 lines at the file's wrap and 6 at 98 columns, and the operator took the code
      finding — a rule with no owning function, three rules stacked at one call site. That is
      `compact.md`'s own answer and it worked; it should be written as the rule for this case.

- [ ] ⚠ Record what stage 6 got RIGHT on the same run, so a later pass does not rewrite the
      good part: it refused to cut evidence, it reported the conflict instead of resolving it,
      and the move-then-compact ordering was validated — block 3040 was 13 lines before a `move`
      split it and 8 after, so a compaction run before the move would have condensed a block
      that was about to become two.
