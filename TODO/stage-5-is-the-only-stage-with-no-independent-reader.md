# Stage 5 is the only stage whose writer is also its checker

```
Status:   open
Progress: 6 of 11 tasks done
Owner:    agents
Requires-Roy: false
Raised:   2026-08-17, by the session that ran all eight stages and rolled its own work back.
          Its words: "the synthesis -- where four verdicts become one sentence -- is written
          by the same agent that then decides it's correct."
Unblocked: 2026-08-19 -- Requires-Roy cleared: its own Owner field read '* 3 rulings, 2
           made'; the remaining one is named in the file and is not what the flag is
           for. The flag means a DECISION is owed; work still remaining is what the
           unchecked boxes already say.
Delivered: 2026-08-23 -- 5b and 6b SHIP. `SKILL.md:905` and `:972` define them and
           `references/re-review.md` (161 lines) carries the payload, the three
           questions, the return shape, the channel and the stop rule.
           `re-review-is-ordered-everywhere-and-defined-nowhere` is in `completed/`.
           Owner was `agents / Roy`; set to the lane, since `Requires-Roy` carries the
           other half and `docs/lanes.md` says an Owner is one of the four lanes.
Split:    2026-08-23 -- 9 boxes became 11; the pre-write read and the `write.md` rail each
           held two artifacts, and the two RECORD boxes are stated in the Objective
```

## !! INDEPENDENT is not FRESH, and only two readers are fresh

Roy, 2026-08-17: *"The only 'fresh' reader is the human and stage 8."*

Two different properties, and this file conflated them until he separated them:

| | means | who has it |
| --- | --- | --- |
| **independent** | did not write the text it is reading | the collator, the compact agent, the filers at 5b/6b, stage 8, the human |
| **FRESH** | formed no prior view of this paragraph | **stage 8 and the human, and nobody else** |

A filer confirming at 5b already read the paragraph and already ruled on it. That is worth having
-- it is the only participant who knows what its finding meant -- but it is **not a fresh read**,
and a design that leans on it must not claim one. Stage 8 reads the finished page and never sees
a report; the human sees the proposal and nothing before it.

## Objective

**Every stage but one was read by somebody who did not write it, and the exception now has two
readers.**

| stage | who checks it |
| --- | --- |
| 4 MARK | `verdicts.py` -- the collator, mechanically |
| **5 APPLY** | **5b RE-REVIEW** -- the roles that ruled, asked *is this what you meant?* |
| 6 COMPACT | **6b RE-REVIEW** -- `re-review.md:59` calls it stage 6's only reader before the author |
| 7b WRITE | the CODE CHECK, against the pre-edit ref |
| 8 REVIEW | a separate agent, reading the finished page |

!! `compact.md` already made the argument, for its own stage: *"An agent that never saw the
argument cannot keep a sentence because it remembers writing it -- which is what makes this pass
safe... **The contract only buys anything if the reader is not the writer.**"* That reasoning
applied to stage 5 verbatim and was not applied there: stage 5 wrote the replacement text and
then ran the residue check on its own output.

! **What shipped is (e), the recommendation below.** `SKILL.md:39`: *"5b and 6b are the same
mechanism asking DIFFERENT questions"*; `:101-104` says they are what make every stage's output
read by somebody who did not write it, and records that APPLY still runs the residue check on
its own output as well. ! `re-review.md:145`: **nothing has yet reached a second round**, so
none of it is measured in a live run.

! **THE ALTERNATIVES ARE KEPT FOR THE RECORD**, since the ruling that chose (e) arrived
2026-08-17 and the losers explain the shape: (a) stage 8 alone, (b) a residue-check agent, (c) a
re-derivation agent, (d) stage 8 before the write -- which stays live as T5 and T6.

## ! Measured: the self-administered rails were read and not run

A run reached stage 8 with `ruff` clean, the formatter clean, the AST **PROVEN**, and 1103 tests
green -- and stage 8 returned twelve findings, enough that the operator rolled the whole pass
back to `REDACTED_SHA_D`. Three of the twelve were the same rail failing:

- **`write.md` requires re-deriving a claim before touching its paragraph.** Three findings were
  a reviewer's `correct` applied without re-derivation. The operator: *"I read that rail and
  didn't run it."*
- **The residue check's four refusals** were answered once instead of four times, which is how
  the `_salvage_row` laundering passed. Filed separately and since fixed in shape --
  `references/residue-check.md:39` now heads them *"The four refusals"* and requires all four.
- **A `drop` was applied whose own `FINDING` named an owner** -- `move`'s payload wearing
  `drop`'s label.

!! **Two of the twelve are the system making prose WORSE than it found it**, which no other
finding today reaches:

- An unfalsifiable claim was replaced with a **checkably false** one -- *"every site reads the
  groups BY NAME"* -- in the comment whose entire subject is positional renumbering, while
  `_stale_row_scan` reads `m.group(2)` positionally and is called with a pattern that has no
  named groups at all.
- A reviewer's `correct` dropped a qualifier that was carrying a true sentence, and the result
  is falsified by the test it annotates.

!! **AND THE MECHANICAL STAGES HELD, WHICH IS THE OTHER HALF OF THAT MEASUREMENT.** The collator
gated correctly, the interval exemption removed the 65-refusal class, `compact` respected the
docstring exemption and flagged its own width trade rather than hiding it, and the CODE CHECK
stopped the run on a real AST change. **The failure is specific to the stage that had no second
reader.**

!! **AND THE ROLLBACK IS THE SYSTEM WORKING.** Twelve findings, tree returned to
`REDACTED_SHA_D`, 0 modified files. A pass that makes the page worse and says so is the outcome
stage 8 exists for.

## ! What is NOT established

- **That a second reader would have caught them.** Stage 8 did, which is the design working
  one stage later than it could have.
- **Whether the cost is payable.** A per-paragraph second reader on 43 paragraphs would be 43
  dispatches; what shipped is four messages instead, one per role.
- **That the mechanism works in a run.** `re-review.md:145` records that nothing has reached a
  second round yet.

## * (e) -- send the patch back to the reviewers

Roy, 2026-08-17: *"instead of step 5 just asking step 4 to relitigate the editors answers, it
should create the patch for the answer and send it back to the reviewers since that is what it
needs. Basically stating - is this what you mean?"*

**It is not relitigation, and that is the whole of it.** *"Reconsider your verdict"* is
unanswerable -- nothing changed. *"Is this the text your finding asked for?"* is a narrow
question with a hold/revise answer, and **the filer is the only participant who knows.** Stage 5
turns four verdicts into one sentence; when it misreads one, no other reader can tell.

!! **RULED 2026-08-17, and sharpened.** Roy: *"Sending the joined resolved block back to the
reviewers that had comments does help because each can say yes my edits made it and are correct
and the other edits do not negate that or cause mine to be wrong."* Not *"is this what you
mean"* -- which a reviewer can answer from memory -- but three questions about the JOINED
paragraph: did my edit survive, is it still correct there, and do the other edits break it.
`re-review.md:22-32` carries exactly those three.

**WHERE IT SITS -- * RULED 2026-08-17: BOTH, and they ask DIFFERENT questions.** Roy: *"I think
it can run before and after stage 6. Stage 5 - is this what you meant. Stage 6 - is this still
correct after my edits. The 4 editor roles i think are well verified roles at this point."*

| | asked after | question | catches |
| --- | --- | --- | --- |
| **5b** | APPLY | *is this what you meant?* | a synthesis that misread a finding |
| **6b** | COMPACT | *is this still correct after my edits?* | compaction that cut what the finding rested on |

### * RULED: a paragraph stage 6 must edit that NO ROLE ruled on goes to all four

Roy: *"If stage 6 has to edit a block not in the specific review results it sends it back to all
of them for a response/verdict."* Shipped at `re-review.md:67`. It is the only path by which
stage 6 originates work, and it inverts the usual direction: every other finding travels 4 -> 5,
this one travels 6 -> 4.

## ! The case for and against (d), a pre-write whole-page read

Stage 8 already exists, already reads fresh, and already caught all of this; what it cannot do
today is stop the write. ! Against it, `review.md` reads a FINISHED PAGE and a proposal is not a
page.

!! **AND A PRE-WRITE READ IS ONLY VALID UNDER BLANKET APPROVAL.** Roy, on the measured run:
*"all of the changes should be read before the proposal to the human -- that was an artifact of
my blanket yes statement. If I had stated apply this one not that one would nullify that
effort."* Approve 30 of 43 and it read a page that never exists. ! Not fatal: the
absentee-author principle already assumes the blanket case. MEASURED 2026-08-23: `SKILL.md` says
neither half -- zero matches for `blanket` or for `pre-write`.

## ! The `write.md` rail is prose where the residue check's is a refusal

MEASURED 2026-08-23: `write.md:113` states *"Touching a paragraph obliges re-deriving its
claim"* as prose, while `residue-check.md:39` heads its four as refusals that must each be
answered. A rail read and not run is a shape problem, and it was measured twice in one day.

## Tasks

- [x] T1 | FINISHED | unknown | T1 -- FINISHED. * The ruling on whether stage 5
      gains an independent reader arrived 2026-08-17 and it is (e): send the
      patch back to the reviewers that filed.
- [x] T2 | FINISHED | unknown | T2 -- FINISHED. * RULED: (e) runs BEFORE and
      AFTER stage 6, asking a different question each time; the stage-6 case is
      in the Objective.
- [x] T3 | FINISHED | unknown | T3 -- FINISHED. The two questions are written as
      input contracts at `references/re-review.md:52-53`, with `:56` stating why
      one prompt answers neither.
- [x] T4 | FINISHED | unknown | T4 -- FINISHED. `SKILL.md:905` is stage 5b and
      `:972` is stage 6b, both deferring to `references/re-review.md` rather
      than restating it.
- [ ] T5 | T5 -- Decide (d): does a whole-page read run before the write?
      Verify: `SKILL.md` states whether it runs; there are zero matches for
      `pre-write` today.
- [ ] T6 | T6 -- If it runs, state that a SELECTIVE approval invalidates it and
      needs a re-read. Verify: `SKILL.md` says so; there are zero matches for
      `blanket` today.
- [ ] T7 | T7 -- Count how many of stage 8's twelve findings a pre-write reader
      could have caught. Verify: the number is in this file with its artifact.
- [ ] T8 | T8 -- Make the `write.md` re-derivation rail a question the writer
      answers per paragraph, as `residue-check.md:39` does. Verify: the rail is
      answerable, not prose.
- [ ] T9 | T9 -- Give the stage-7b report somewhere to put that per-paragraph
      answer. Verify: the report has a field for it and an unanswered paragraph
      shows.
- [x] T10 | FINISHED | unknown | T10 -- A RECORD, not a task: the mechanical
      stages held; the failure is specific to the stage that had no second
      reader. Stated in the Objective.
- [x] T11 | FINISHED | unknown | T11 -- A RECORD, not a task: the rollback is
      the system working -- twelve findings, tree returned to `REDACTED_SHA_D`,
      0 modified files. Stated in the Objective.
