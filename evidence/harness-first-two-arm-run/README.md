# The first two-arm graded run -- two complete plugin sets, end to end

**2026-08-29. Two complete plugin snapshots, one staged case, both arms dispatched in one turn,
each graded blind, aggregated by the real `skill-creator` tool.** This is the run
`docs/plans/harness-the-first-graded-run.md` was written to make possible, and it is the first
measurement in this repo that no human performed.

!! **THE NUMBER IS SMALL AND THE POINT IS THAT IT EXISTS.** One case, one role, one run per arm --
so `stddev` is 0.0 everywhere because n=1, and nothing here supports a claim about the two
versions in general. What it establishes is that the chain HOLDS: a case can be staged, two sets
can be isolated, both can be run and graded without either seeing the other, and the result comes
back re-derivable.

## What ran

| | |
| --- | --- |
| case | `a-docstring-never-matches-its-own-file`, from `evals/test-cases.jsonl` |
| START | **`1ad4ba72`** -- a commit, never a version number (D2, and `marketplace-resolves-live`) |
| file under review | `plugins/comment-review/skills/comment-review/scripts/galley.py`, 8,425 bytes at that commit |
| role | `block-context`, one role -- a MARK-level case, whose terminus is the role's own findings |
| census | produced by the CURRENT machinery, **identical for both arms** |

| arm | ref | commit | files | result |
| --- | --- | --- | --- | --- |
| `old_skill` | `v0.1.6` | **`52e1d9ef5fadb4ce6680375aa6fcb6a675f033a7`** | 22 | **2 of 5** |
| `with_skill` | `v0.2.2` | **`ccb2404cb25036834505844ee3650cdc0337fd6a`** | 22 | **4 of 5** |

! **ONLY THE PROSE VARIED.** Both arms read the same census from the same machinery, so this is
`decision-log.md Process: #52`'s baseline shape -- the OLD agent workflow on the NEW machinery --
rather than a two-variable comparison whose delta could not be attributed (`Process: #51`).

## What each arm did with the paragraph the case is about

`block_matches` at `galley.py:93-99`. Its docstring asks *"Does the file still read the way the
census recorded this block?"*; the body compares the file's lines against the block's stored
`raw_lines`, which for a Python docstring is the AST value -- no quote delimiters, no first-line
indent -- so a docstring block can never match.

| arm | instruction on that paragraph | what it said |
| --- | --- | --- |
| `v0.1.6` | **`clean`** | *"the question the docstring poses is the comparison the body performs"* |
| `v0.2.2` | **`correct`** | ruled on the word *"one"* in *"the one failure a galley must not produce quietly"* -- an exclusivity claim, not the comparison |

!! **BOTH MISSED THE MECHANISM, AND ONE CERTIFIED IT.** `v0.1.6` inspected the comparison and
declared it sound. `v0.2.2` filed a correcting instruction on the right paragraph for a different
reason -- and separately emitted `clean` on the comparison itself, reasoning that the check
*"compares the file against that stored copy rather than against itself"*. **Neither named the
AST-value form.** E2 failed on both arms, which is the finding worth keeping from a run whose
headline is an improvement.

## The grade

    old_skill    E1 FAIL  E2 FAIL  E3 FAIL  E4 PASS  E5 PASS    2/5   40%
    with_skill   E1 PASS  E2 FAIL  E3 PASS  E4 PASS  E5 PASS    4/5   80%

    tokens       113,315  vs  118,144        time  359.4s  vs  384.3s

!! **THE AGGREGATOR REPORTS `Delta: -0.40`, AND THAT SIGN IS BACKWARDS.** It computes
first-minus-second in sorted config order, and `skill-creator`'s own SKILL.md prescribes
`old_skill` for an improve-mode baseline -- which sorts BEFORE `with_skill`. So the arm that
scored twice as well produces a negative delta. Filed as T47/T48 on
`the-harness-cannot-run-the-system-it-grades`. **Read the pass rates, not the delta, until that
lands.**

## What the run proves about the harness itself

- **B1's isolation held, checked two ways.** Both snapshot manifests verified UNTOUCHED after the
  run, and E5 -- graded from the output side, blind -- confirmed neither arm cited anything
  outside its snapshot, the census and the file under review.
- **Both arms refused rather than reached.** Where `galley.py`'s prose names `verdicts.py`,
  `address_problem` and `edit_problem`, both recorded them unresolved instead of leaving the file
  list to settle them.
- **The workspace layout the aggregator actually walks is the one that was built** -- including
  the `run-N` level `SKILL.md` never mentions.

## What it exposed

| | |
| --- | --- |
| **the staged case has no name corpus** | The staged tree is not a checkout, so the census printed its WALKED_TREE caveat and BOTH arms independently downgraded symbol findings to `query`. A case whose key expects a tombstone scores a miss for the harness's reason. `TODO/staged-case-has-no-name-corpus.md` |
| **the delta sign** | above; T47/T48 |
| **old prose, new census** | Both arms reported the census/brief disagreement rather than guessing past it: the census numbers PARAGRAPHS with cue addresses (`@a0`, `@b33`) while the older briefs rule on BLOCKS with an index and no slot for a cue. This is what `Process: #52` looks like from inside. |
| **212 of 223 paragraphs hold no prose** | `v0.1.6`'s brief demands a record for every numbered block; obeying it would mean ruling on 210 empty places. Measured live -- `the-census-is-mostly-intervals-nobody-rules-on` |

## What is NOT established

- **n=1 per arm.** Every `stddev` in `benchmark.json` is 0.0 because there is one run, not three.
- **The grader model is not recorded, and D2 asks for it.** Both graders were dispatched as
  `general-purpose` subagents with no model pinned, so this package cannot name what graded it.
  That is a gap in the run, not in the plan.
- **One case, one role.** Nothing here says anything about the other three roles, about stage 5,
  or about the write chain.
- **The grade was taken under the WALKED_TREE caveat**, per the first row above, so E-numbers
  touching symbol liveness are depressed by an amount nobody has measured.

## Files

    census.txt              what both arms were handed
    expectations.json       the answer key, written BEFORE either arm returned
    eval_metadata.json      the case, as the workspace records it
    benchmark.json/.md      the real `skill-creator` aggregator's output
    arms/<arm>/findings.md  what that arm filed
    arms/<arm>/grading.json the blind grade, `text`/`passed`/`evidence` per expectation
    arms/<arm>/timing.json  captured from that arm's task notification
    arms/<arm>/snapshot.json the manifest -- ref, commit, and the sha of all 22 files

! `snapshot.json`'s `root` was a run directory under the system temp tree and is not preserved;
the ref and the per-file shas are what make the arm re-derivable.
