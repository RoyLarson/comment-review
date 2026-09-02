# The unit of review is the statement, and three files disagree about it

```
Status:   CLOSED 2026-08-17 by group A
Progress: 5 of 5 tasks closed
Owner:    session * Roy (1 ruling)
Raised:   2026-08-16 (Roy, on a proposed sentence saying "why the BLOCK belongs there":
          "A) each sentence/statement is under review not the 'block'. B) some of the
          statements would get deleted or moved -- your comment implies that they only
          are added.")
```

## Objective

**A block is how a finding is ADDRESSED; a statement is what is ruled on.** The payloads already
say so -- `drop` carries *"the sentence, verbatim"*, `correct` carries *"the false clause and the
true one"*, and `split` exists because one block holds two unrelated notes. Nothing states it,
and three files disagree about whether a reviewer may report two statements in one block:

| where | says |
| --- | --- |
| `ref/reviewer-brief.md:92` | *"Every census index must appear **exactly once** across your findings and your clean ranges"* |
| `SKILL.md:44` | *"you will get **several verdicts per role per block** and must synthesise ONE"* |
| `sk-scripts/verdicts.py:266-268` | `by_reviewer[f.reviewer].add(f.block)` -- a **set**. Two findings on one block are accepted, and nothing reports it |

The gate permits it and the task agent expects it, so the brief is the outlier -- and the brief is
what the reviewers actually read. A reviewer obeying *"exactly once"* merges two unrelated defects
into one finding, which is the failure `split` exists to catch.

! **Neither direction of "exactly once" is enforced.** `coverage_gaps` computes
`all_blocks - found - clean`, so it reports only what is MISSING. A block appearing in both a
finding and a `CLEAN` range passes silently too.

! **Not vocabulary, and deliberately off that branch.** The words are settled; this is a rule
three files state differently.

## Tasks

- [x] T1 | FINISHED | unknown | * Rule what *"exactly once"* was protecting. Two
      readings: **coverage** (every index is accounted for somewhere) or
      **exclusivity** (one finding per index). Coverage is what the gate
      computes; exclusivity is what the sentence reads as. Only the ruling
      decides whether the brief's sentence is reworded or the gate gains a
      check. ! **DONE by group A, 2026-08-17.** Resolved as COVERAGE, and by the
      interval work rather than by argument: the brief now reads "at least one
      RECORD for EVERY block that HOLDS PROSE".

- [x] T2 | FINISHED | unknown | State the unit once: a finding is ADDRESSED by
      census index and RULED on a statement, so several findings may carry the
      same `BLOCK`. Say it where the record is defined
      (`ref/reviewer-brief.md:40-68`), not in a second place. ! **DONE by group
      A, 2026-08-17.** In `BLOCK`'s own row: a finding is ADDRESSED by index and
      RULED on a sentence, so several may carry the same `BLOCK`.

- [x] T3 | FINISHED | unknown | Fix `ref/reviewer-brief.md:91-94` to whatever
      the ruling makes it. ! **DONE by group A, 2026-08-17.** The `exactly once`
      text is gone.

- [x] T4 | FINISHED | unknown | Fix `ref/reviewer-brief.md:290`, which tells a
      reviewer to *"say in `FINDING` why the block belongs there"* -- the wrong
      unit, and it covers only arrival, never a statement that is dropped or
      moved out. ! The field table at `:67` already defines `FINDING` as *"what
      is wrong, one clause"*, so the likely fix is deleting the clause rather
      than rewording it. ! **DONE by group A, 2026-08-17.** That sentence is
      gone; `REASON` now says what it carries.

- [x] T5 | FINISHED | unknown | Decide whether the gate should report a block
      that is both found and `CLEAN`. It is silent today, and that is the one
      case where *"exactly once"* is unambiguously right. ! **DONE by group A,
      2026-08-17.** **NO, and the coverage ruling decides it:** a role may
      return `clean` on one sentence and `correct` on another in the same block,
      so reporting the pair would refuse the thing the unit ruling permits.
