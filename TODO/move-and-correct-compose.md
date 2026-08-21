# `move` and `correct` COMPOSE, and the gate calls them a contradiction

```
Status:   open
Progress: 4 of 5 tasks done
Owner:    session * Roy (1 ruling, made)
Raised:   2026-08-17 (the first full run of 0.1.7: 8 blocks flagged as contradictions,
          2 of them genuine)
```

## Objective

! **Group A landed everything but the re-measure**, which needs a live run: the
measured 8 re-reviews should fall to 2 under sentence-keying, and until a run
says so that is a prediction.

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

## Tasks

- [x] Change `contradictions()` so `move` against `correct`/`patch` is not fatal and not a
      re-review. ! Decide what it becomes: silent, or a distinct printed line (`COMPOSES --
      relocation and a truth fix on the same block; apply the move first`). Recommendation: the
      printed line, because the ORDER matters and this is the one place the run can state it
      per block.
      ! **DONE by group A, 2026-08-17.** `move` left the set. ! SILENT rather than a printed
      `COMPOSES` line -- the ordering is stated where the ordering happens, in the synthesis
      order, and a per-block line would restate it 40 times a run.

- [x] Keep `drop` against `correct`/`patch` exactly as it is. It is the real contradiction and
      it is what the check was built for.
      ! **DONE by group A, 2026-08-17.** Kept, and narrowed to the SAME SENTENCE.

- [x] Say in ONE file that a `correct` travelling with a `move` is applied AT THE DESTINATION.
      `SKILL.md` step 3 says *"at the anchor it now sits on"*, which is correct and easy to read
      past. The 2026-08-17 run read past it.
      ! **DONE by group A, 2026-08-17.** `SKILL.md` synthesis step 3.

- [x] State that a `correct` applied after the move may leave a VACUOUS comment, and that this
      is the accepted outcome. Roy ruled it: another pass drops it, and that is cheaper than a
      correction that was true only where the prose used to be. ! Without this the next agent
      re-derives the inversion, because leaving a vacuous comment feels like a defect.
      ! **DONE by group A, 2026-08-17.** Same sentence, `SKILL.md` step 3.

- [ ] Re-measure after the change. The run's 8 re-reviews should fall to 2, and the count
      belongs in [`re-review-is-ordered-everywhere-and-defined-nowhere`](completed/re-review-is-ordered-everywhere-and-defined-nowhere.md)
      as the load that procedure actually carries.
