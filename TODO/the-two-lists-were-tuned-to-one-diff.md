# The acquittal and suppression lists are deleted -- five entries need re-deriving

```
Status:   decision-needed
Progress: 3 of 9 tasks done
Owner:    agents
Requires-Roy: true
Raised:   2026-08-16 (Roy: "yes drop both lists / and lets create a todo to clean up
          those entries - because several of them do not follow this own skills rules")
Triaged:  2026-08-23 -- one box held an argument about `states-the-signature` with no state
          in which anyone ticks it; it is ticked and the argument moved to the Objective.
          The register sweep is re-measured: three `acquit` sites survive, at new lines
Split:    2026-08-23 -- the box holding the three CONDITIONAL entries was one ruling per
          entry in one box; it is now three, one per entry, each finishing the day Roy
          answers it
```

## Objective

**Both lists are gone from `reviewer-brief.md`. This file holds what was inside them**, because
several entries carry real checks and one carries a real measurement, and none of that survives
in the tree any more.

Why they went, in order of weight:

1. **The mechanism that decides `clean` already exists and is stated per role.** Each agent file
   says what its own `clean` asserts, and every one is a TRUTH assertion at that role's scope --
   *"EVERY SENTENCE in the block is true of the code beside it"*, *"...belongs to the line it sits
   on"*, *"name, signature, docstring, comments and body agree"*, *"the module docstring accounts
   for the exposed surface"*. The acquittal list matched on a prose SHAPE instead, and claimed to
   be *"the ONLY reasons to pass a block over"* -- so a block that is true of the code beside it
   but matches no label was `clean` by its role's file and a finding by the brief.

2. **The measurement behind it does not support it.** `evidence/ga/brief.md`: ten candidate
   SKILL.md rewrites, each applied to SIX `redacted_pkg` files at base `REDACTED_SHA_H`, scored on F1 against
   *what a later commit actually rewrote there* (`ground_truth.py` builds the answer key from that
   diff; 209 changed prose blocks out of 419). Candidate `1d` used a closed acquittal list and won
   at 0.8184. ! But `brief3.md:31-34` -- 1d and 2a ran the **same closed list** over the **same 419
   blocks** and acquitted 47% versus 14%: *"The acquittal RATE is the trait; the acquittal LIST is
   just vocabulary."*

3. **The oracle is a diff, not a judgement.** A correct finding on a block that commit happened
   not to touch counts as a false positive, so *"precision .783"* measures agreement with one
   burn-down's choices in one project.

4. **The suppression list had no provenance at all** -- it appears nowhere in `evidence/`. It was
   named as a sibling to the acquittal list, and it suppressed nothing: its content is measured
   ANNOTATION precision plus the rule that a low-precision one is a *batch to triage*.

## The three CONDITIONAL entries, verbatim

They were resolution procedures wearing an exemption's name -- each excused a block only *after*
work that could equally have produced a finding. They are checks, and if they are kept they belong
with the checks they duplicate, not in a list of reasons to pass over. Each is now its own ruling,
T1 to T3:

- **re-run the arithmetic.** *"Pure arithmetic over committed values is checkable without
  judgement, so do the sum and report the number. Measured: one worked example was wrong, its
  first correction was ALSO wrong, and all three versions rounded to the same asserted value, so
  nothing downstream ever objected."*
- **verify a guard is really absent.** *"...if a test does fail, one exists."* ! This one is
  already re-derived independently -- the `guard` / `unguarded-invariant` split was settled
  2026-08-16 from Roy's own renderer example, without reference to the GA.
- **an expiry condition already met is not an acquittal.**

## `names-its-line` and `batch to triage`, in full

**`names-its-line`** was a description of a comment doing its ordinary job rather than a rule.
The ruling (T6) is either to name what is lost by its absence, or to record that nothing is.

**`batch to triage`**, with the measured precision rates that went with it (T8): *"An annotation
below roughly 10% precision is a batch, not a finding. Reporting it raw spends the human's
attention on a list they will learn to skip, which is how a real hit gets lost."* Rates were a
date-or-path used as a **command-line argument** (4/4 false), an identifier that is also a
**module stem** (8/8), a **warning glyph** as such (45/0), and a **repo-relative path citation**
resolved only against the repo root (80/84, 18/20, 2/2). ! All measured on ONE repository -- the
same one the GA scored against, so the rates are not transferable and the ruling is whether the
RULE survives without them.

## !! `states-the-signature` MUST NOT BE RESTORED -- and that is a rule, not a task

`states-the-signature` is not merely unearned, it **CONTRADICTS `function-context`**. That role's
absence question is *"what must be true of this function's OUTPUT, or of its CALLER, that the
SIGNATURE CANNOT EXPRESS -- and does the docstring say it?"* A docstring that restates the
signature is the one that has NOT answered it. ! There is no state in which someone ticks *"do
not restore this"*; it is a standing constraint on whoever reopens the list, and it is recorded
here so the next session does not re-derive the entry from the GA scores alone.

## What the ticked boxes recorded

**T4, FINISHED 2026-08-16.** Restored in `clean`'s own section rather than the deleted list's.
Roy: *"Nothing should be 'judged - clean' just because it is ... fits the jurisdiction labels we
added earlier."* `acquitted` became `clean`, and the closing clause now points at the role file:
*"none of those is your role's question unless your role file says it is."* It sits directly under
*"Your role file states what your `clean` asserts"*, which is where the remit question is actually
decided. Brief 261 -> 266 lines.

**T7, FINISHED 2026-08-16. `detector` is DELETED.** It was stated only inside the suppression list
-- *"a census annotation read as a signal, and its PRECISION is how often it is right"* -- and
everything it supported (precision, batch to triage, reasons to distrust) went with that list. The
two `census.py` comments left meant `annotation`, which is settled. Roy: *"drop it - especially
since it currently only survives in code comments where it doesn't belong in the first place."*
! It also failed the REGISTER: a detector is instrumentation.

## Tasks

- [?] T1 | T1 -- * Rule on **re-run the arithmetic** -- keep it as a check
      beside the checks it duplicates, or drop it. Verify: the ruling is written
      in `docs/decision-log.md`.
- [?] T2 | T2 -- * Rule on **verify a guard is really absent**, re-derived as
      the `guard` / `unguarded-invariant` split. Verify: the ruling is in
      `docs/decision-log.md`.
- [?] T3 | T3 -- * Rule on **an expiry condition already met is not an
      acquittal**. Verify: the ruling is written in `docs/decision-log.md`.
- [x] T4 | FINISHED | unknown | T4 -- FINISHED 2026-08-16. The `clean` clause
      was restored in `clean`'s own section of `reviewer-brief.md` and points at
      the role file.
- [x] T5 | FINISHED | unknown | T5 -- SUPERSEDED. This box held the
      `states-the-signature` argument, which cannot be finished; it is stated in
      the Objective above and the record stays.
- [?] T6 | T6 -- * Rule on `names-its-line` -- name what is lost by its absence,
      or record that nothing is. Verify: the ruling is written in
      `docs/decision-log.md`.
- [x] T7 | FINISHED | unknown | T7 -- FINISHED 2026-08-16. `detector` is
      DELETED, along with everything the suppression list supported.
- [?] T8 | T8 -- * Rule on whether **batch to triage** survives without its
      rates, which were measured on one repository. Verify: the ruling is
      written in `docs/decision-log.md`.
- [ ] T9 | T9 -- Sweep the remaining judicial register out of the shipped tree.
      Verify: `grep -rniE "acquit\|suppression\|jurisdiction" plugins/` comes
      back empty.
## Where the three surviving `acquit` sites are

MEASURED 2026-08-23, and the two line numbers this file previously carried are both stale:
`plugins/comment-review/agents/comment-review-block-context.md:37`,
`plugins/comment-review/skills/comment-review/references/reviewer-brief.md:331`, and
`plugins/comment-review/skills/comment-review/SKILL.md:897` -- all `acquit` as a plain verb.
! `jurisdiction` is already done: renamed **`remit`** 2026-08-16, and
`grep -rni "jurisdiction" plugins/` returns nothing as of 2026-08-23.

## ! Why the register is the standard here

**The metaphor is not a new standard; it is the one already in force.** Roy, 2026-08-16: *"I have
been working under this assumption of the metaphor for a while."* Editorial roles, editorial marks
on a manuscript, a proof, a proofreader -- the vocabulary is PUBLISHING, and his PROOFREADER
ruling states the reason out loud: *"it is reading the PROOF and it is determining if the document
deserves more marks. That fits the role of a PROOFREADER in society."*

! **So these words were off-metaphor when they were written, not merely unmeasured.** `acquittal`
and `suppression` arrived with the initial plugin import. **`jurisdiction` did not** -- the
2026-08-16 session proposed it against a metaphor neither party named at the time. It was the one
judicial word that branch ADDED, and it is now **`remit`**; what is left is `acquit` as a plain
verb, which is T9.
