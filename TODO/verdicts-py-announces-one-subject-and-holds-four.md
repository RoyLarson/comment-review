# verdicts.py announces one subject and holds four, and its own reviewer said so

```
Status:   decision-needed
Progress: 0 of 8 tasks done
Owner:    session * Roy (* 1 ruling -- the module names, which `docs/vocabulary.md`
          constrains)
Raised:   2026-08-18, from the dev review of the file by its own editorial board
```

## Objective

**`verdicts.py` is 2,083 lines and four subjects. Its docstring announces one** -- *"Stage 5's
gate: join four reviewers' reports against the census."*

!! **`module-context` FOUND THIS AND THEN GOT IT WRONG, which is why it is filed rather than
merely fixed.** Reviewing the file at `4fd8384` it quoted its own role file's trigger almost
verbatim -- a summary line describing one half of what the file contains -- and then emitted a
`patch` WIDENING the docstring to announce two subjects. That is the defect the trigger is named
for, applied as the remedy. It filed no `code_concerns` entry, though the same role file says a
misplaced module constant is a code concern, so the pattern exists and was not reached for.

! Recorded as the run's one miss in [`evals/test-cases.jsonl`](../evals/test-cases.jsonl), case
`module-context-widens-a-two-subject-docstring`, pinned at `4fd8384`. **Splitting the file does
not delete that case** -- the fixture is a checkout at a hash, and the hash is an ancestor of
`main`, reachable from `origin/main` and contained in `v0.2.3`.

## The four subjects

| subject | what it answers | lines, at `4fd8384` |
| --- | --- | ---: |
| the verdict table | what each of the seven marks means, and what payload it requires | 95-340, 595-670 |
| the report reader | what a reviewer handed in, read into `Finding`s | 285-340, 670-915 |
| the per-finding checker | is THIS finding usable -- payload, source, address, block, edit | 936-1630 |
| the join | every reviewer against the census and against each other | 1636-2083 |

! The first two overlap in the 285-340 band because the record regexes sit among the verdict
constants. That overlap is the measurement, not an obstacle: it is where the two subjects were
interleaved rather than merely adjacent.

## Why it is scheduled with the census filter and not after it

- **The lookup tool needs a module to live in.** `the-census-is-mostly-intervals-nobody-rules-on`
  builds a tool answering *what is the ADDRESS of this line of code*, and `census.address`
  already owns `path:start-end`. The verdict table is where the address type belongs, and today
  that table is 300 lines inside a 2,000-line file.
- **Two open TODOs are each inside ONE half**, so the split is the cheapest moment to do them:
  [`the-bridge-landed-and-the-rewrite-did-not`](the-bridge-landed-and-the-rewrite-did-not.md)
  is nine `claim_text` call sites in the verdict table, and
  [`the-parser-merges-across-boundaries-it-cannot-read`](the-parser-merges-across-boundaries-it-cannot-read.md)
  is the report reader alone. ! If the bridge is not rewritten during the split it is COPIED into
  a new module and gains a second home.
- **Two findings from the dev review land inside it**, both reproduced and unfixed: `claim_keys`
  reaching two of four sites, and `record.check()` raising `AttributeError` where
  `load_report` guards.

## * The ruling: what the four modules are called

**`docs/vocabulary.md` already binds one of the names.** Its entry reads
*"**the join** | `verdicts.py` -- reads every reviewer's report against the census and against
the others', and refuses what it cannot verify"*, and `mark` is settled as *"editorial. Stage
4's name, and what it emits."* So the term `the join` names the FILE, and any split has to say
which file the term now points at.

Two shapes, and the trade is churn against the register:

| | the join | the verdict table | churn |
| --- | --- | --- | --- |
| **A** minimum churn | `verdicts.py` (unchanged) | a new name | none outside the new files |
| **B** term matches file | `join.py` | `verdicts.py` | `CLAUDE.md`, `SKILL.md`, `docs/vocabulary.md`, tests, and the documented stage-5 command |

! **Recommendation: B.** The vocabulary entry has to be edited under either shape, because under
A the term `the join` would point at a file that no longer holds the join alone. B pays the churn
once and leaves every name meaning what the glossary says. ! Under A the file called
`verdicts.py` would be the one place the verdicts are NOT defined.

! The other two names are not constrained by anything settled: the report reader and the
per-finding checker each need a name that states their one subject.

## Tasks

- [ ] * **Rule the four module names.** A or B above, and the two unconstrained ones. ! This
      comes first because every task below writes an import.

- [ ] **Cut the verdict table out first.** It is the leaf -- the report reader, the checker and
      the join all read it, and it reads none of them. Verify: the new module imports nothing
      from the other three.

- [ ] **Rewrite the bridge while the table is in hand**, rather than copying it.
      `claim_text` renders a typed claim back into the 0.2.x marker string and its own docstring
      calls it a bridge kept *"before anything is rewritten to read the object directly."*
      Verify: no check reads a rendered string where the field is present.

- [ ] **Cut the report reader out**, and fix the merge across boundaries it cannot read while
      it is the only subject in view. Verify: an unrecognised boundary is REPORTED, and the
      diagnostic names the side it could not read.

- [ ] **Cut the per-finding checker out.** Verify: it takes a `Finding` and the tree, and knows
      nothing about reports or reviewers.

- [ ] **Leave the join as the CLI.** Verify: it is the only one of the four with a `main`.

- [ ] **Fix the two dev-review findings inside the split**: `claim_keys` reaching two of four
      sites, and `record.check()` raising `AttributeError` on a non-object report where
      `load_report` guards. Verify: a test reproduces each against the pre-split behaviour.

- [ ] **Prove the split changed no verdict.** The four reports in
      [`evidence/cycle-0.2.3/`](../evidence/cycle-0.2.3/) join to a known result; run them
      before and after and diff the output byte for byte. ! That is the same technique the
      `claim_keys` refactor was verified with 2026-08-18.

## Related

- [`the-census-is-mostly-intervals-nobody-rules-on`](the-census-is-mostly-intervals-nobody-rules-on.md)
  -- depends on this: the lookup tool needs the verdict table to be a module
- [`the-bridge-landed-and-the-rewrite-did-not`](the-bridge-landed-and-the-rewrite-did-not.md)
  -- entirely inside the verdict table
- [`the-parser-merges-across-boundaries-it-cannot-read`](the-parser-merges-across-boundaries-it-cannot-read.md)
  -- entirely inside the report reader
- [`the-harness-cannot-run-the-system-it-grades`](the-harness-cannot-run-the-system-it-grades.md)
  -- holds the case this file's miss became
