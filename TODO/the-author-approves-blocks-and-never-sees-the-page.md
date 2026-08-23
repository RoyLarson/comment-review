# The author approves a list of blocks and never sees the page

```
Status:   open
Progress: 1 of 9 tasks done
Owner:    agents
Requires-Roy: true
Raised:   2026-08-15 (Roy, after the 7b cutting paragraph was found and deleted)
```

## Objective

**Stage 7a shows the author a LIST, and stage 8 is the only pass that reads the PAGE -- after
it is already on disk.** 7a presents findings "grouped by verdict, most consequential first, in
five parts... replacement text inline". That is per-block. The author rules on blocks and never
sees how the file will read.

`review.md` says stage 8 is *"the only stage that can see damage the editing caused"* and lists
what it looks for: a block that is no longer a proposition, two runs merged across a blank line,
the same sentence now in two places, drift from the style sheet. **None of that is visible in a
per-block list, and all of it is found after the author has approved and after 7b has written.**

Roy: *"We do need something that looks at the whole document(s) as it(they) would be written
with the new comments before bringing it to the attention of the person."*

! **This is a pipeline change, not vocabulary**, and deliberately off that branch.

## Tasks

- [x] Delete the claim that 7b cuts. **Done 2026-08-15 -- Roy: "This has got to go no matter
      what."** `write.md` was headed *"Shorten by TRUTH here"* and opened *"This pass cuts, and
      it can cut a lot"*, four lines above its own *"Write the APPROVED text verbatim"*. It had
      been self-contradicting since the import at `9932c3f`. Cutting happens at 5, and again at
      6 if it runs; then it is presented and approved and cannot be modified. The section is now
      "Nothing is judged here".

- [ ] * Decide WHERE the whole-page read goes. It has to happen before the author sees
      anything, on text that is not yet written. Either stage 8 moves ahead of 7a and reads
      proposed text rather than the artifact, or a new pass sits between 6 and 7a and stage 8
      keeps its post-write job. ! `review.md:3-4` currently says it is *"loaded after stage 7b
      has written the approved text, never before"* and *"the only one that reads the ARTIFACT
      rather than the plan"* -- both statements have to change under either answer.

- [ ] * Add a **6b**: the residue check as a GATE after compaction, before the human. Roy:
      *"There needs to be a 6b that does this procedure before going to the human."* Today
      COMPACT runs it as step 3 of its own per-block loop -- **the agent that cut the text is the
      one checking whether the cut lost something**, which violates the principle COMPACT itself
      is built on (`compact.md:101`: *"the contract only buys anything if the reader is not the
      writer"*). A 6b is a second reader, the same argument one level down.

- [ ] * Decide whether a **5b** follows. Roy: *"potentially a 5b just to double check."* Same
      shape after APPLY: the agent that wrote the replacement text is the one asking whether it
      lost anything. ! Weigh it against the budget -- a fifth and sixth dispatch per run is real
      cost, and 5 and 6 are the same actor today.

- [ ] Take the residue check OUT of 7b. Roy: *"It's too late by the time it got here and if
      everything goes right it shouldn't need it... If it is happening after humans have blessed
      it that breaks the rule."* ! The evidence is decisive: `residue-check.md`'s step 4 is
      **"If yes, it is not finished. Put it back and repeat from 3"** -- rewriting the text is the
      procedure's ONLY response to a failure, and at 7b that means rewriting what the author
      approved, which `write.md` forbids in its next section. The check either finds nothing, or
      finds something and the only legal action is forbidden. Update `residue-check.md:16-18`
      ("Stage 6 re-runs it... and stage 7b runs it on what it applies") and `write.md:10-14`.

- [ ] * Rule on the delivery mechanism. Roy: *"really ought to be a temporary branch with the
      diff or something so they can use git's tools to accept it."* That would replace the
      stage-7a prose listing with a branch the author reviews in their own tools, and it changes
      what approval MEANS -- today it is a sentence in chat, and it would become a merge. ! It
      also interacts with `prove_unchanged.py`, which compares against a base ref: a temporary
      branch gives it an unambiguous one.

- [ ] Restate stage 8 as a VERIFICATION with two outcomes. Roy: *"a final verification with the
      outcomes good / raise to human as new review required."* Today `review.md`'s Report asks
      for "files read end to end, damage found and repaired, and -- separately -- every defect
      that predates this run" -- a narrative, with no stated verdict on the run as a whole. Two
      named outcomes make it checkable.

- [ ] Reconcile "damage found and REPAIRED" with the new shape. If stage 8 verifies rather than
      edits, repairing damage there is a second write after approval -- the failure this file
      exists to close. Either the repair is a re-run, or stage 8 keeps a narrow licence that is
      stated as such.

- [ ] Re-check what 7a presents once the page is visible. If the author reviews a diff or a
      rendered page, the five-part per-block listing may be redundant, or may still be wanted as
      the rationale beside it. Do not delete it without deciding which.
