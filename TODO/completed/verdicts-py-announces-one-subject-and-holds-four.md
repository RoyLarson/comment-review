# verdicts.py announces one subject and holds four, and its own reviewer said so

```
Status:   in-progress
Progress: 8 of 8 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-18, from the dev review of the file by its own editorial board
Updated:  2026-08-18 — the module names are ruled -- three modules, verdicts.py keeps
          its name
Updated:  2026-08-23 — Verified in place 2026-08-23. record.check() guards both cases: a
          report whose 'pages' is not a list returns 'not a seeded report'
          (tests/test_record.py:276), and a non-object record reports 'a record is a
          <type>, not an object' (tests/test_verdicts.py:2365). claim_keys is the single
          source -- three call sites, and a grep for hardcoded claim-key names returns
          nothing. ! The split landed as desk.py / record.py / verdicts.py / held.py,
          not the proposed join.py / checks.py: the subjects separated, the filenames
          differed.
```

## Objective

**`verdicts.py` is 2,083 lines and four subjects. Its docstring announces one** -- *"Stage 5's
gate: join four reviewers' reports against the census."*

!! **`module-context` FOUND THIS AND THEN GOT IT WRONG, which is why it is filed rather than
merely fixed.** Reviewing the file at `d3aa065` it quoted its own role file's trigger almost
verbatim -- a summary line describing one half of what the file contains -- and then emitted a
`patch` WIDENING the docstring to announce two subjects. That is the defect the trigger is named
for, applied as the remedy. It filed no `code_concerns` entry, though the same role file says a
misplaced module constant is a code concern, so the pattern exists and was not reached for.

! Recorded as the run's one miss in [`evals/test-cases.jsonl`](../evals/test-cases.jsonl), case
`module-context-widens-a-two-subject-docstring`, pinned at `d3aa065`. **Splitting the file does
not delete that case** -- the fixture is a checkout at a hash, and the hash is an ancestor of
`main`, reachable from `origin/main` and contained in `v0.2.3`.

## The four subjects

| subject | what it answers | lines, at `d3aa065` |
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

- [x] T1 | FINISHED | unknown | * **RULED 2026-08-18: three modules, and
      `verdicts.py` KEEPS ITS NAME.** Neither A nor B: `record.py` already
      announced "what a RECORD is" and derived `allowed()` from the verdict
      table, so the table went there and needed no new name. The checks became
      `desk.py` -- the copy desk, where a submitted mark is checked before
      anyone acts on it, and free in the register where `checks.py` would
      collide with CODE CHECK and PROSE CHECK. `docs/vocabulary.md` needed no
      edit.

- [x] T2 | FINISHED | unknown | **DONE `0bbc3fa`.** 232 lines into `record.py`
      -- `Verdict`, `VERDICTS`, `OUT_OF_ROLE`, `QUERY_SHAPES`, the two claim
      regexes and `claim_keys`. ! It was a true leaf: 190 lines referencing
      nothing but `re.compile`, `@dataclass` and `str.join`, which is why it
      moved in one piece.

- [x] T3 | FINISHED | unknown | **DONE `3645aad`.** `parse_report` types a 0.2.x
      claim through `claim_object` at the seam, and `ruled_text` reads the field
      with the marker scan as fallback. ! It was a local call only because the
      cycle was gone.

- [x] T4 | FINISHED | unknown | **DONE `aa01e61`.** 315 lines to `record.py` --
      reading a record file is the third verb on the noun it already writes and
      checks. ! The boundary-merge fix did NOT ride along; it stays with
      `the-parser-merges-across-boundaries-it-cannot-read`.

- [x] T5 | FINISHED | unknown | **DONE `4fc5974`.** 754 lines to `desk.py`.
      Verified before cutting: the checks call no join function, the reader
      calls no check, and every mention of a moving name outside `verdicts.py`
      is PROSE.

- [x] T6 | FINISHED | unknown | **DONE.** `verdicts.py` 2,084 -> 603 lines and
      is the only one of the three with a `main`. Dependencies run one way:
      verdicts -> desk -> record.

- [x] T7 | FINISHED | unknown | **Fix the two dev-review findings inside the
      split**: `claim_keys` reaching two of four sites, and `record.check()`
      raising `AttributeError` on a non-object report where `load_report`
      guards. Verify: a test reproduces each against the pre-split behaviour.

- [x] T8 | FINISHED | unknown | **DONE, and the method had to be fixed first.**
      With `--repo .` the output moved by one line -- a report citing
      `verdicts.py:1320` in a file the cut shortened -- because SOURCES resolves
      against the working tree. Re-run with BOTH pinned, a worktree at `3e1fedf`
      as subject and `1015469` as the pre-cut tool: BYTE-IDENTICAL, 24 problems.
      ! `evidence/redacted-corpus-full-v0_2/VERSIONS.md` already said "replay
      needs the TREE pinned as well as the census".


## Related

- [`the-census-is-mostly-intervals-nobody-rules-on`](the-census-is-mostly-intervals-nobody-rules-on.md)
  -- depends on this: the lookup tool needs the verdict table to be a module
- [`the-bridge-landed-and-the-rewrite-did-not`](the-bridge-landed-and-the-rewrite-did-not.md)
  -- entirely inside the verdict table
- [`the-parser-merges-across-boundaries-it-cannot-read`](the-parser-merges-across-boundaries-it-cannot-read.md)
  -- entirely inside the report reader
- [`the-harness-cannot-run-the-system-it-grades`](the-harness-cannot-run-the-system-it-grades.md)
  -- holds the case this file's miss became
