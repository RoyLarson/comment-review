# `collate` buckets a two-ended mark at one end

```
Status:   open
Progress: 3 of 3 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-27, splitting the residue out of Roy's correction on relational
          findings ("It is disjoint but both parts are fully cite-able and stated in
          the current findings") -- two of the three forms need no new shape; this
          one is a bucketing defect and not a shape defect at all
Updated:  2026-08-29 — T2's *decided once* half landed only now, in desk/collator.py's
          _join_moves. The grouping half (T1) had been delivered, but reconcile sorted
          each of a move's two places INDEPENDENTLY, so the origin could settle while
          the destination went back for a re-read -- and docket_from packages settled
          alone, so the docket deleted the origin and never wrote the destination.
          _join_moves lifts every move to the strongest outcome either end was given, to
          a fixed point, before any bucket is read. Tested both directions in
          tests/test_reconcile.py, and no-docket-carries-one-end in
          tests/test_docket.py; all four go red when _join_moves is replaced with a no-
          op.
```

## Objective

**`collate` groups marks by a single `mark["address"]`, and `move` names two places.** A `move`
out of `a0` into `a8` lands in the `a0` bucket. Another role's mark on `a8` lands in the `a8`
bucket. **The two never meet**, so the table that decides merge-from-fight never sees that they
touch the same text.

! **`move` IS THE EXISTING PROOF THAT TWO-ENDEDNESS IS EXPRESSIBLE.** Its `claim` carries `from:`
and `to:`, and its `change` shows BOTH -- so the shape has always been two-ended and only the
grouping is one-ended. That is why this is one line of bucketing rather than a new field.

! **THE FAILURE IS SILENT AND IT IS THE DANGEROUS DIRECTION.** Both marks are well-formed, both
settle as `ONE substantive mark -> TAKE IN`, and both are applied. Nothing escalates, so the
`move`'s destination is written by two decisions that never saw each other -- which is exactly
the *"applying a `move` without seeing the other duplicates the rule"* case.

### What the collation is keyed on today

    at = defaultdict(list)
    for mark in marks:
        at[normalise(mark["address"])].append(mark)

One key per mark. ! The fix is that a mark contributes to **every place it touches** -- its own
address, plus a `move`'s destination -- while still being DECIDED once. A destination-side entry
is a claim on that place's text, not a second copy of the mark.

! **AND THE SENTENCE RULE STILL GOVERNS.** Two marks meeting at one place are only in conflict if
they rule on the same sentence; different sentences compose. Widening the bucketing must not
turn every `move` into an escalation -- that would repeat the measured cost of treating a scope
declaration as a question, where one role vetoed three others and the docket fell from 12
alterations to 5.

### Not in scope

! **A contradiction between two places needs NOTHING here.** Roy, 2026-08-27: *"one or both sides
get a correct or query with a reason / The reason says this contradicts that / Along with the
sources pointing at the 'that'."* MEASURED: `module-context` produced that shape unprompted in
rounds 2 and 3. The instruction gap is
[`the-fields-do-not-say-a-mark-may-cite-across`](the-fields-do-not-say-a-mark-may-cite-across.md),
an `agents` file.

## Tasks

- [x] T1 | FINISHED | unknown | T1 -- Write the failing case FIRST: a `move`
      from `a0` to `a8` and another role's `correct` on `a8`, over one base.
      Verify: it asserts an escalation, and FAILS on today's bucketing by taking
      both in silently.
- [x] T2 | FINISHED | unknown | T2 -- Make a mark contribute to every place it
      touches while being decided once. Verify: T1 passes, and a `move` whose
      destination carries no other mark still settles without escalating.
- [x] T3 | FINISHED | unknown | T3 -- Prove the widening did not make `move`
      escalate by default. Verify: a run of the round-2 marks settles 11 of 16
      places, escalates 0 and re-reads 5. ! **THIS SAID "THE SAME 13 OF 16" AND
      THAT FIGURE IS SUPERSEDED**, corrected 2026-08-29. It was measured under
      SILENT-MERGE semantics, which `decision-log.md Process: #49` replaced: 3
      places carrying 2+ marks on different sentences and 2 `add` places move to
      re-read, and the 3 that previously escalated now settle -- `13 - 5 + 3 =
      11`. The 16 is places carrying at least one mark that owes a change, out
      of 76 addresses round 2 marked at all. Re-derived twice: through
      `desk.collator.reconcile`, and separately straight from
      `evidence/the-loop-measured-2026-08-27/marks.jsonl`, so the check is not
      the code agreeing with itself. ! **A CHECKED BOX ASSERTING A SUPERSEDED
      FACT READS AS SETTLED**, which is why the wording is corrected rather than
      left beside the new number.
