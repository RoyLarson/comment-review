# `move` and `correct` COMPOSE, and the gate calls them a contradiction

```
Status:   open
Progress: 4 of 6 tasks done
Owner:    agents
Raised:   2026-08-17 (the first full run of 0.1.7: 8 blocks flagged as contradictions,
          2 of them genuine)
VERIFIED: 2026-08-23 -- all four landed changes re-read in the tree and all four hold.
          `verdicts.py:250-252` states *"`move` is absent by ruling"*;
          `verdicts.py:234-238` keys the check on the TEXT, not the paragraph index;
          `verdicts.py:240-245` takes the text from the BLOCK/CHANGE diff rather than
          `CLAIM`; and `SKILL.md:825` carries both the destination rule and the vacuous
          -comment rule in one sentence. ! Nothing prints a per-block COMPOSES line,
          which is what task 1 chose; the word survives only as prose at SKILL.md:854.
          ! ONE TASK LEFT and it needs a live run.
SPLIT:    2026-08-23 -- one action per box. The last open box held a live run AND writing
          its number into another file, and is now two. Five boxes became six; what the
          four landed changes did moved to *What landed* below.
```

## Objective

! **Group A landed everything but the re-measure**, which needs a live run: the
measured 8 re-reviews should fall to 2 under sentence-keying, and until a run
says so that is a prediction. ! The count belongs in
[`re-review-is-ordered-everywhere-and-defined-nowhere`](completed/re-review-is-ordered-everywhere-and-defined-nowhere.md),
as the load that procedure actually carries.

**`contradictions()` flags `drop`/`move` against `correct`/`patch` as a collision. On a `move`
it is not one.** Prose can belong somewhere else AND be false; those are two findings about one
sentence and both get applied. Measured on the 2026-08-17 run:

| shape | blocks | a contradiction? |
| --- | --- | --- |
| `move` + `correct` | 126, 166, 645, 1041, 1226 | **no** -- a sequence |
| different sentences in one block | 981 | **no** -- see [`the-unit-of-review-is-the-statement-not-the-block`](completed/the-unit-of-review-is-the-statement-not-the-block.md) |
| `drop` vs `correct`, same sentence | 728, 1575 | **yes** |

**Two genuine contradictions out of eight flagged.** The other six sent both roles a re-review
asking them to resolve something the skill already knows how to do -- `SKILL.md`'s synthesis
order applies every `move` at step 2 and every `correct` at step 3, which composes them
correctly without anyone being asked anything.

! `drop` against `correct` on the SAME sentence stays a real contradiction: one role says the
sentence should not exist, the other says it should exist and be fixed. Nothing composes those.

## !! The ORDER is settled: MOVE FIRST, and it was re-stated wrong during the run

Roy, 2026-08-17: *"I disagree that correct comes before move. Everything in all of the documents
state the reverse because until a statement has moved to the correct anchor any 'correct'
adjustment may be wrong. It may take another comment-review to get it dropped completely if
correct leaves it as a vacuous comment but that is better than correcting something to read for
where it is at now then moving it to a different anchor where it would no longer be correct."*

`SKILL.md` step 2 already says it: *"! **Placement comes first because a claim is measured
against the code it sits with** -- correct it where it does not belong and you have corrected it
against the wrong code."*

! **A reviewer asserted the reverse in a re-review answer and the task agent relayed it as
"load-bearing, not incidental."** On block 1226 the claim was that the `correct` must be applied
BEFORE the move, or the move launders a falsehood into `docs/`. That inverts step 2. The
laundering worry is real but it is answered by a later pass, not by re-ordering: a correction
written for the site the prose is LEAVING can be false at the site it arrives at, and that error
is silent.

## What landed -- group A, 2026-08-17, all four re-verified 2026-08-23

- **`move` against `correct`/`patch` is no longer fatal and no longer a re-review.** `move` left
  the set. ! SILENT rather than a printed `COMPOSES` line -- the ordering is stated where the
  ordering happens, in the synthesis order, and a per-block line would restate it 40 times a run.
  VERIFIED: `verdicts.py:250-252` states the ruling, and `contradictions()` emits nothing at all
  for a `move`/`correct` pair; the word COMPOSES appears only as prose at `SKILL.md:854`.
- **`drop` against `correct`/`patch` is kept exactly as it was**, and narrowed to the SAME
  SENTENCE. It is the real contradiction and it is what the check was built for. VERIFIED:
  `verdicts.py:234-245` keys on the BLOCK/CHANGE diff text, not the paragraph index and not
  `CLAIM`.
- **ONE file says a `correct` travelling with a `move` is applied AT THE DESTINATION.** Step 3
  said *"at the anchor it now sits on"*, which is correct and easy to read past; the 2026-08-17
  run read past it. VERIFIED at `SKILL.md:825`.
- **A `correct` applied after the move may leave a VACUOUS comment, and that is the accepted
  outcome.** Roy ruled it: another pass drops it, and that is cheaper than a correction that was
  true only where the prose used to be. ! Without this the next agent re-derives the inversion,
  because leaving a vacuous comment feels like a defect. VERIFIED: same sentence, `SKILL.md:825`.

## Tasks

- [ ] T1 -- Re-measure on a live `/comment-review` run over blocks holding both `move` and
      `correct`. Verify: it reports 2 re-reviews where the 2026-08-17 run reported 8.
- [ ] T2 -- Write T1's count into the re-review TODO linked in the Objective, as the load
      that procedure carries. Verify: that file names the count and the date it was taken.
- [x] T3 -- DONE by group A, 2026-08-17, re-verified 2026-08-23. `move` against
      `correct`/`patch` is not fatal and not a re-review. In the Objective.
- [x] T4 -- DONE by group A, 2026-08-17, re-verified 2026-08-23. `drop` against
      `correct`/`patch` kept, narrowed to the same sentence. In the Objective.
- [x] T5 -- DONE by group A, 2026-08-17, re-verified 2026-08-23. `SKILL.md:825` says a
      `correct` travelling with a `move` is applied at the destination.
- [x] T6 -- DONE by group A, 2026-08-17, re-verified 2026-08-23. `SKILL.md:825` states
      that a vacuous comment is the accepted outcome, and why.
