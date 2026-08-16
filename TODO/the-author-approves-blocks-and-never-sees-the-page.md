# The author approves a list of blocks and never sees the page

```
Status:   open
Progress: 0 of 6 tasks done
Owner:    session · Roy (⭐ 2 rulings)
Raised:   2026-08-15 (Roy, after the 7b cutting paragraph was found and deleted)
```

## Objective

**Stage 7a shows the author a LIST, and stage 8 is the only pass that reads the PAGE — after
it is already on disk.** 7a presents findings "grouped by verdict, most consequential first, in
five parts… replacement text inline". That is per-block. The author rules on blocks and never
sees how the file will read.

`review.md` says stage 8 is *"the only stage that can see damage the editing caused"* and lists
what it looks for: a block that is no longer a proposition, two runs merged across a blank line,
the same sentence now in two places, drift from the style sheet. **None of that is visible in a
per-block list, and all of it is found after the author has approved and after 7b has written.**

Roy: *"We do need something that looks at the whole document(s) as it(they) would be written
with the new comments before bringing it to the attention of the person."*

⚠ **This is a pipeline change, not vocabulary**, and deliberately off that branch.

## Tasks

- [x] Delete the claim that 7b cuts. **Done 2026-08-15 — Roy: "This has got to go no matter
      what."** `write.md` was headed *"Shorten by TRUTH here"* and opened *"This pass cuts, and
      it can cut a lot"*, four lines above its own *"Write the APPROVED text verbatim"*. It had
      been self-contradicting since the import at `7154b92`. Cutting happens at 5, and again at
      6 if it runs; then it is presented and approved and cannot be modified. The section is now
      "Nothing is judged here".

- [ ] ⭐ Decide WHERE the whole-page read goes. It has to happen before the author sees
      anything, on text that is not yet written. Either stage 8 moves ahead of 7a and reads
      proposed text rather than the artifact, or a new pass sits between 6 and 7a and stage 8
      keeps its post-write job. ⚠ `review.md:3-4` currently says it is *"loaded after stage 7b
      has written the approved text, never before"* and *"the only one that reads the ARTIFACT
      rather than the plan"* — both statements have to change under either answer.

- [ ] ⭐ Rule on the delivery mechanism. Roy: *"really ought to be a temporary branch with the
      diff or something so they can use git's tools to accept it."* That would replace the
      stage-7a prose listing with a branch the author reviews in their own tools, and it changes
      what approval MEANS — today it is a sentence in chat, and it would become a merge. ⚠ It
      also interacts with `prove_unchanged.py`, which compares against a base ref: a temporary
      branch gives it an unambiguous one.

- [ ] Restate stage 8 as a VERIFICATION with two outcomes. Roy: *"a final verification with the
      outcomes good / raise to human as new review required."* Today `review.md`'s Report asks
      for "files read end to end, damage found and repaired, and — separately — every defect
      that predates this run" — a narrative, with no stated verdict on the run as a whole. Two
      named outcomes make it checkable.

- [ ] Reconcile "damage found and REPAIRED" with the new shape. If stage 8 verifies rather than
      edits, repairing damage there is a second write after approval — the failure this file
      exists to close. Either the repair is a re-run, or stage 8 keeps a narrow licence that is
      stated as such.

- [ ] Re-check what 7a presents once the page is visible. If the author reviews a diff or a
      rendered page, the five-part per-block listing may be redundant, or may still be wanted as
      the rationale beside it. Do not delete it without deciding which.
