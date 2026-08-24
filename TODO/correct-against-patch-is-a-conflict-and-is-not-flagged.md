# `correct` against `patch` is a conflict, and the gate does not flag it

```
Status:   decision-needed
Progress: 0 of 3 tasks done
Owner:    agents
Requires-Roy: false
Raised:   2026-08-17 (the first end-to-end cycle run; block 1 of galley.py)
Unblocked: 2026-08-19 — Requires-Roy cleared: its own Owner field reads 'the widening is
           a cost decision Roy has already ruled on once'. The flag means a DECISION is
           owed; work still remaining is what the unchecked boxes already say.
TRIAGED:  2026-08-23 — 2026-08-23. ALREADY WELL FORMED: all three boxes are verifiable
          checkpoints -- an owed ruling, a measurement to TAKE, and a change to the
          report. Nothing was ticked, nothing was rewritten; only the T labels were
          added.
RE-VERIFIED: 2026-08-23 — 2026-08-23, read against the tree. STILL LIVE: `contradictions`
             is verdicts.py:225, and the only RE-REVIEW line the join prints is
             verdicts.py:610, *"RE-REVIEW -- drop against correct/patch on:"*. There is
             no `correct` against `patch` case anywhere in the file, so the pair is still
             resolved silently by the ordering rule and the report still names only the
             verdict it applied.
```

## Objective

`contradictions()` (verdicts.py:225) flags a block where one role REMOVES the sentence another
rules on -- `drop` against `correct` or `patch`, printed at verdicts.py:610. It does not flag
`correct` against `patch` on ONE sentence, and that pair is a disagreement about whether the
sentence is TRUE: one role says it is false, the other says it is true and badly worded. The
skill already treats the pair as hazardous -- `correct` is applied before any `patch`, because a
patch to a false claim LAUNDERS it -- so the resolution rule exists and fires silently,
discarding the edit of the patching role without that role or the report ever saying so.

Measured on the first cycle run: block 1 of `galley.py` carried `correct` from block-context
and `patch` from module-context on the same sentence. The join printed **no** `RE-REVIEW`
list. Sent back anyway at stage 5b, **both roles answered `SAME SENTENCE  yes`** -- so the
collision was real and both could see it -- and both answered `HOLD`, module-context reasoning
that the added clause from block-context states the same defect its patch was for, *"so the
finding is carried, not laundered"*.

! **That is one data point and it resolved HOLD**, which is why this is `decision-needed` and
not a fix. Widening the flagged set costs rounds, and Roy ruled the set narrow *"for now"* on
exactly that trade: 51 of 150 blocks had two or more roles converge against 8 flagged as
conflicts.

## Tasks

- [ ] T1 -- * **Rule whether `correct` + `patch` on ONE SENTENCE enters the
      `RE-REVIEW` set.** The three options: flag it (a round per occurrence); flag
      it only where the EDITED SPANS of the two roles coincide, which is what
      `contradictions()` already computes and would be a narrower set than "same
      block"; or leave it and rely on the ordering rule.

- [ ] T2 -- Measure the rate before ruling. `contradictions()` keys on the span
      diff already, so the count is a one-line change to a held report set -- how
      many blocks in the captured runs carry `correct` and `patch` over overlapping
      spans, against the 8 the current rule flags. Verify: the two numbers written
      into this file, naming the run they came from.

- [ ] T3 -- Whatever is ruled, **the report must say when the ordering rule
      discarded an edit.** A role whose `patch` lost to a `correct` is told nothing
      today, and the output of stage 5 names only the verdict it applied. That half
      is not a cost trade -- it is a silent drop, and it is the same shape as the
      `CODE CONCERNS` that vanished in a conversion while every finding total
      matched. Verify: the join prints the discarded edit and its role, with a test
      that fails without it.

## Related

- [`re-review-is-ordered-everywhere-and-defined-nowhere`](completed/re-review-is-ordered-everywhere-and-defined-nowhere.md)
  -- defines what a re-review IS, and carries the ruling that a contested block goes back to
  its FILERS. This file asks what makes a block contested.
- [`the-record-is-a-parsed-template-and-should-be-a-value`](completed/the-record-is-a-parsed-template-and-should-be-a-value.md)
  -- step 7 is the run this was found on.
