# The author approves a list of blocks and never sees the page

```
Status:   decision-needed
Progress: 5 of 9 tasks closed
Owner:    agents
Requires-Roy: true
Raised:   2026-08-15 (Roy, after the 7b cutting paragraph was found and deleted)
Triaged:  2026-08-23 -- four of the nine landed since this was filed. 5b and 6b are
          shipped stages, and stage 8 is already a two-outcome verification that
          edits nothing. What remains is the whole-page read, which is still owed
SPLIT:    2026-08-23 -- the boxes were cut to two lines each. The evidence each
          carried is in the Objective; the task count is unchanged at nine
```

## Objective

**Stage 7a shows the author a LIST, and stage 8 is the only pass that reads the PAGE -- after it
is already on disk.** `SKILL.md:994-999` presents findings *"Grouped by verdict, most
consequential first, in five parts (`VERDICT / PARAGRAPH / CLAIM / REASON / CHANGE`) ...
replacement text inline"*. That is per-paragraph. The author rules on paragraphs and never sees
how the file will read.

`review.md:3` says *"This stage sees the finished page. Every earlier one saw a plan."* What it
looks for -- a paragraph that is no longer a proposition, two runs merged across a blank line,
the same sentence now in two places, drift from the style sheet -- **is none of it visible in a
per-paragraph list, and all of it is found after the author has approved and after 7b has
written.**

Roy: *"We do need something that looks at the whole document(s) as it(they) would be written
with the new comments before bringing it to the attention of the person."*

! **This is a pipeline change, not vocabulary**, and deliberately off that branch.

! **The second-reader half of this file is DONE.** `SKILL.md:905` is stage 5b and `SKILL.md:972`
is stage 6b, both dispatching `references/re-review.md` against a galley that is censused first.
`SKILL.md:979-983` states the argument this file made: *"NOTHING ELSE READS STAGE 6'S OUTPUT
BEFORE THE AUTHOR DOES."* What is still missing is a read of the WHOLE PAGE, which neither 5b nor
6b performs -- both are per-paragraph, like the list they feed.

### What the boxes carried -- the evidence, moved out of the tasks

! **T1.** `write.md` was headed *"Shorten by TRUTH here"* and opened *"This pass cuts, and it
can cut a lot"*, four lines above its own *"Write the APPROVED text verbatim"*. It had been
self-contradicting since the import at `9932c3f`. Roy: *"This has got to go no matter what."*
The section is now "Nothing is judged here" (`write.md:16`).

! **T2 -- where the whole-page read goes.** It has to happen before the author sees anything, on
text that is not yet written. Either stage 8 moves ahead of 7a and reads proposed text rather
than the artifact, or a new pass sits between 6b and 7a and stage 8 keeps its post-write job.
! `review.md:3` and `SKILL.md:1022-1026` both place it after 7b today, and both have to change
under either answer. ! The galley 5b and 6b already set (`SKILL.md:913-922`) is a whole file on
disk, so the material a pre-approval page read needs is already produced twice per run.

! **T3.** `SKILL.md:972-992` -- *"Runs only if stage 6 ran, and over the paragraphs it actually
shortened."* Roy asked for it -- *"There needs to be a 6b that does this procedure before going
to the human"* -- because COMPACT ran the residue check as step 3 of its own per-paragraph loop,
making the agent that cut the text the one checking whether the cut lost something, against
`compact.md`'s own *"the contract only buys anything if the reader is not the writer"*.

! **T4.** `SKILL.md:905-944` sends every paragraph the collator printed as `RE-REVIEW` back to the
roles that ruled on it, against a galley census. Roy: *"potentially a 5b just to double check."*
! `SKILL.md:974-977` states what separates the two so the budget buys two different questions:
*"5b asks whether the synthesis carried the finding, 6b asks whether shortening broke it."*

! **T5 -- the evidence is decisive.** Roy: *"It's too late by the time it got here and if
everything goes right it shouldn't need it... If it is happening after humans have blessed it
that breaks the rule."* `residue-check.md:23` is **"If yes, it is not finished. Put it back and
repeat from 3"** -- rewriting the text is the procedure's ONLY response to a failure, and at 7b
that means rewriting what the author approved, which `write.md:16-20` forbids in its next
section. The check either finds nothing, or finds something and the only legal action is
forbidden.

! **T6 -- the delivery mechanism.** Roy: *"really ought to be a temporary branch with the diff
or something so they can use git's tools to accept it."* That would replace the stage-7a prose
listing with a branch the author reviews in their own tools, and it changes what approval MEANS
-- today it is a sentence in chat, and it would become a merge. ! It also interacts with
`prove_unchanged.py`, which compares against a base ref: a temporary branch gives it an
unambiguous one.

! **T7.** `review.md:50-59`: *"Two outcomes, and say which. Everything answers yes -- the files
are done ... Anything answers no -- bring that section to the human"*, with predating defects
listed separately. Roy asked for *"a final verification with the outcomes good / raise to human
as new review required"*; what shipped is that, with the escalation worded as a section rather
than a round.

! **T8.** `review.md:43`: *"Do not edit. You read and you report; the human decides what happens
next."* `SKILL.md:1032`: *"NOTHING is fixed here."* ! So a second write after approval is now
refused by both files, which is the failure this TODO exists to close -- at stage 8 only. T2 is
the same failure at 7a.

! **T9.** If the author reviews a diff or a rendered page, the five-part per-paragraph listing
at `SKILL.md:996-999` may be redundant, or may still be wanted as the rationale beside it. ! Do
not delete it without deciding which; this cannot be settled before T2.

## Tasks

- [x] T1 | FINISHED | unknown | T1 -- FINISHED 2026-08-15. The claim that 7b
      cuts is deleted; `write.md:16` is now "Nothing is judged here".
- [?] T2 | T2 -- * RULE where the whole-page read goes: stage 8 ahead of 7a on
      proposed text, or a new pass between 6b and 7a. Verify:
      `docs/decision-log.md` records the answer.
        > 2026-09-03 PROVISIONAL leaning: a git branch. Process 85. Not a ruling
- [x] T3 | FINISHED | unknown | T3 -- FINISHED. Stage 6b exists at
      `SKILL.md:972-992`, running the residue check over the paragraphs stage 6
      shortened, with a reader who is not the writer.
- [x] T4 | FINISHED | unknown | T4 -- FINISHED. Stage 5b exists at
      `SKILL.md:905-944`, sending every `RE-REVIEW` paragraph back to the roles
      that ruled on it, against a galley census.
- [ ] T5 | T5 -- Take the residue check OUT of stage 7b. Verify: neither
      `residue-check.md`, `write.md` nor `SKILL.md:834-836` names 7b as a place
      it runs.
- [?] T6 | T6 -- * RULE the delivery mechanism: a temporary branch with the
      diff, or the stage-7a prose listing. Verify: `docs/decision-log.md`
      records which.
        > 2026-09-03 PROVISIONAL leaning: a git branch. Process 85. Not a ruling
- [x] T7 | FINISHED | unknown | T7 -- FINISHED. Stage 8 is a verification with
      two named outcomes -- the files are done, or the section goes to the human
      (`review.md:50-59`).
- [x] T8 | FINISHED | unknown | T8 -- FINISHED. "damage found and REPAIRED" is
      gone; `review.md:43` and `SKILL.md:1032` both refuse a second write after
      approval, at stage 8.
- [ ] T9 | T9 -- Re-check what stage 7a presents once the page is visible;
      blocked on T2. Verify: the five-part listing at `SKILL.md:996-999` is kept
      or cut, with a reason.
        > 2026-09-03 PROVISIONAL leaning noted on T2/T6 -- Process 85, not a ruling
