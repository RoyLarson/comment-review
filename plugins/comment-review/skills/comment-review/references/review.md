# Stage 8 — REVIEW: the finished page

Loaded by the task agent **after stage 7b has written the approved text**, never before. It is
the last pass and the only one that reads the ARTIFACT rather than the plan.

The last pass, over the **finished file**, reading it as a reader would rather than as a list of
blocks. Everything before this examined prose against code; this examines the **artifact against
itself**, and it is the only stage that can see damage the editing caused.

Read each changed file end to end and look for exactly this:

- **a block that is no longer a proposition** — a sentence ending mid-clause, a hanging clause
  under a deleted line, a contrast marker whose contrast went. Measured repeatedly, and it
  passes every mechanical check there is: it is not stale, not misplaced, not false — it is
  ungrammatical, and nothing upstream asks whether the prose still parses.
- **runs that merged** — an `add` landing next to an existing block across a blank line makes
  one longer run. A compliant edit producing a violation, visible only here.
- **the same sentence now in two places**, because a `move` landed beside one that already said
  it.
- **drift against the style sheet** — dialect, capitalisation, citation form.

⚠ **Fix only what THIS pass created.** A defect you find that predates the run is a finding for
the next one, not a licence to reopen stage 7b. Say which is which.

⚠ **The proof pass is not the residue check.** The residue check is inbound and per-block —
*did this block lose something?* This asks *does the finished page read?* A pass can satisfy the
first everywhere and fail the second, and that is the common case, because each edit was
defensible alone.

## What this pass may NOT do

⚠ **It may not re-open a verdict.** Truth was settled at stage 5, length at 6, and the author
ruled at 7a. Finding a better wording here is not a licence to write it — that is next run's
`patch`, and writing it now puts text on disk the author never saw.

⚠ **It may not run the residue check as a substitute.** That check is inbound and per-block
([`residue-check.md`](residue-check.md)); this one is outbound and per-FILE. A run can pass the
first on every block and still fail this, which is the common case precisely because each edit
was defensible alone.

## Report

Files read end to end, damage found and repaired, and — separately — every defect that predates
this run. The second list is the next run's input and must not be silently folded into the first.
