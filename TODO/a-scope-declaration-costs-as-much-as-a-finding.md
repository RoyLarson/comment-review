# A scope declaration costs as much as a finding

```
Status:   open
Progress: 1 of 5 tasks done
Owner:    agents
Requires-Roy: true
Raised:   2026-08-17, the day the query contract landed. `module-context`'s report on a
          1,174-block repo is 1.1 MB and most of it is the words "outside my role".
TRIAGED:  2026-08-23 — three of four boxes are tasks; the fourth was a standing
          prohibition and is ticked into the Objective. ! One Objective sentence was
          STALE and is corrected below: the contract no longer asks for `EVIDENCE` and a
          `QUOTE`, it asks for `SOURCES` -- `reviewer-brief.md:419-423`, *"A `query`
          requires `SOURCES`, by construction ... All three shapes carry them, including
          `outside my role`"*.
Updated:  2026-08-28 — TRIAGE 2026-08-28: checked Roy's hedge ("probably not true
          anymore because of the new binder layout and rest of the system") against the
          tree. This file's Objective is about PAYLOAD SIZE -- an outside-my-role query
          costs as many bytes/records as a real finding. decision-log.md Process #33
          (2026-08-27) replaced the three query shapes with outside-my-role/unable-to-
          determine/human-review-necessary and restated that outside-my-role "must never
          block the other roles", citing the same measurement (docket fell from 12
          alterations to 5) that TODO/collate-buckets-a-move-at-one-end.md and plan
          0.2.4 T4.3 track -- that is a BLOCKING/reconciliation concern, not this file's
          payload-size concern, and it is a different TODO's mechanism. Checked whether
          the payload requirement itself changed: reviewer-brief.md:435-447 (current,
          post-#33) still requires full SOURCES plus a REASON naming the remit for
          outside-my-role exactly as before -- "All three shapes carry them, including
          outside-my-role" -- so the bytes-per-query cost this file measures is
          structurally unchanged. None of T1 (bytes), T2 (record count), T3 (rule
          whether it may be lighter) or T4 (document the cost if it stays) has been done
          -- grep confirms no ruling in docs/decision-log.md and no "small-remit" cost
          sentence in reviewer-brief.md. Separately, and worth flagging: the mechanism
          Roy may have had in mind (outside-my-role not blocking reconciliation) is ALSO
          not done in code -- plan 0.2.4-the-mark-and-the-collator.md T4.3 is unchecked,
          and verdicts.py/record.py (the collator) moved to prototype/ and do not run;
          SKILL.md:747-751 states the non-blocking rule as prose for the task agent to
          apply by hand, which is a ruling, not enforcing code. Neither the payload
          question this file actually asks, nor the blocking question Roy's note
          gestures at, has been resolved by the new system. File stays open.
```

## Objective

**`outside my role` now carries the same payload as a real finding, and on most repos it is
most of what one role emits.**

The contract landed 2026-08-17 and is still live: a `query` must NAME its shape in the brief's
own words -- `outside my role`, `outside the checkout`, `outside the code`
(`reviewer-brief.md:406-414`) -- carry `SOURCES` that resolve, and say what WOULD settle it.
Roy ruled it, and the reason holds -- *"Not mine"* is an admission, a showing is a finding, and
the block otherwise leaves the report certified by nobody (`reviewer-brief.md:425-431`).

! The cost was not measured at the time. Measured then, on a 1,174-prose-block repo where
`module-context`'s remit covers 175:

| role | report |
| --- | --- |
| `module-context` | **1.1 MB** |
| `ownership-context` | 660 KB |
| `function-context` | 512 KB |
| `block-context` | 486 KB and still writing |

`module-context` files the fewest substantive findings and writes the largest report, because
roughly a thousand blocks are outside its remit and each one now costs a full record.

! **THE 1.1 MB FIGURE IS A FILE SIZE, and attributing it to out-of-role queries is an inference
this file has not earned** -- which is what the measurement below is for.

!! **It pulls against the change made the same day.** The interval exemption freed budget by
removing records a role did not owe -- measured, `function-context` went from 11 findings to 68
because *"the role spent its budget reading instead of accounting."* The query contract spends
budget by making each remaining out-of-role record heavier. Both are right on their own terms
and they are pulling on the same rope.

## ! What is NOT established

- **That the reports are too large for anything.** Nothing failed. `verdicts.py` parses them
  mechanically and the task agent reads the COLLATOR, not the reports.
- **That the payload is wasted.** An `outside my role` query with its `SOURCES` proves the role
  read the block. That is the fabricated-`clean` defence, and it is the reason the contract
  exists.
- **The token cost specifically.** `block-context` was measured at ~21 minutes and 491k tokens
  as the heaviest role, and its remit is every claim in every block -- that is a different cause
  from this one and must not be folded into it.

## ! The argument on both sides of the owed ruling

**For a lighter payload:** the three shapes already route differently -- the first says which
scope owns the block and asks nothing of the author, the other two are work
(`reviewer-brief.md:407-409` says exactly that). A payload that follows the routing is
consistent with it.

**Against it:** `SOURCES` is what proves the block was read, and dropping it on the shape a
reviewer reaches for when it has nothing to say is dropping it exactly where the fabrication
risk is highest.

! **IF THE RULING IS THAT IT STAYS, THE COST GETS SAID WHERE IT LANDS** -- a paragraph in the
brief's `outside my role` section stating that a role whose remit covers a small fraction of a
repo will write mostly scope declarations, **and that this is the contract working.** Today
nothing there says it.

## ! The one solution that is ruled out, and it carries no box

**Do not solve this by exempting a role from blocks outside its remit.** That is the
forced-record problem in reverse, and `module-context` returning `query` rather than `clean` on
a block it never read is deliberate -- it does not certify what it has not seen.

! It is a standing prohibition, not work: there is no state in which someone ticks *"we did not
do the thing we ruled out"*. It carried a box until 2026-08-23 and is recorded here instead.

## Tasks

- [ ] T1 -- Measure `module-context`'s out-of-role queries by BYTES, before any change.
      Verify: the fraction of the report they occupy is written into this file.
- [ ] T2 -- Measure them by RECORD COUNT on the same report. Verify: the count and the
      total record count are written into this file.
- [ ] T3 -- * RULE whether an `outside my role` query may carry a LIGHTER payload than the
      other two shapes. Verify: the ruling is recorded in `docs/decision-log.md`.
- [ ] T4 -- If T3 rules it stays, say at `reviewer-brief.md:425` that a small-remit role
      writes mostly scope declarations. Verify: that section names the cost.
- [x] T5 -- NOT A TASK. *"Do not solve this by exempting a role from blocks outside its
      remit"* is a standing prohibition. Kept in full in the Objective.
