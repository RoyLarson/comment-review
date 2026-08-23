# comment-review -- the first 4 -> 5 -> 5b -> 6 -> 6b cycle

The run that cleared **0.2.3's gate**: *"the goal of 0.2.3 is still getting a full reviewer -
rereviewer - cycle functional. We are not releasing until we have that."* (Roy, 2026-08-17.)

**Subject:** `plugins/comment-review/skills/comment-review/scripts/galley.py`, on branch
`feat/0.2.3-cycle-and-record` at `6c863b3`. **110 census blocks, 11 holding prose.**
Four roles, **47 findings**, stage-5 gate **exit 0**.

**Why this file.** It was written the same week by the same session that reviewed it, and it is
the module 5b depends on -- so a defect in it would stop the cycle it was being used to test.
Two did.

---

## !! THREE THINGS THIS RUN DID NOT TEST

!! **The reviewers were NOT the installed plugin agents.** `comment-review:comment-review-*`
resolves, but to **v0.2.2** -- stale against the branch under test. Stage 1.6's sanctioned
fallback was used instead: four general-purpose agents given the REVIEWER FILES paths from the
packet. That exercises the branch's role text and the record contract; it does **not** exercise
namespaced-agent dispatch. Consequently the brief reached them as a PATH rather than pasted
verbatim, which is what the fallback prescribes and what the shipped instruction forbids.

!! **The `/comment-review` skill was never invoked.** The stages were hand-executed by a
session reading `SKILL.md`, not by a task agent meeting it cold. Every stage's TOOLING was
exercised; the skill's own orchestration prose was followed deliberately by someone who had
just edited it, which is the weaker test of the two.

!! **7a, 7b and 8 did not run.** No approval, no WRITE, no `prove_unchanged`, no stage-8
proofread. The galley is the terminus and **nothing this run proposed reached disk.** 0.2.3's
gate is 4 -> 6b, so this is in scope -- but it is not "the whole system".

! **The cap was OPERATOR-SUPPLIED (4 lines).** This repo publishes none, and without a cap
stage 6 is skipped and 6b with it, so the last two legs cannot be exercised here by a run that
invents nothing. `SKILL.md` forbids the skill inventing one; supplying it as the `cap` argument
is the operator's to do.

! **The tree moved under the run.** A REFERENCE ONLY file was edited during MARK, which moved a
cited line from 1320 to 1365 -- the join correctly reported `function-context`'s correct citation
as unresolved. `join.txt` here is taken against a worktree pinned at `6c863b3`, the tree the
roles actually read. Replaying it against any other commit will fail citations that were right.

! **The operating session knew it was testing the skill, and was fixing the code under review
while the run proceeded.** Blocks 25 and 61 are findings about a defect that was repaired
before the run finished, so the galley here edits prose describing code that has since changed.
Nothing below measures a session that only wants its comments reviewed.

---

## What the run found -- and what the run was for

**The cycle's own yield was two defects that made 5b impossible**, either alone sufficient.
Both were in the tree under review; both were found by the roles reading it.

| | measured |
| --- | --- |
| **a docstring never matched its own file** -- `census.py` filled a structural docstring's `raw_lines` from the AST value, and `galley.block_matches` compared that to the file's physical lines | **6 of 6** docstring blocks refused as stale against an **unmodified** file; all 5 comment blocks passed. Filed independently by `block-context` and `function-context` |
| **an `add` would have deleted code** -- an interval's `start`/`end` are the two lines of CODE bounding it, and the galley replaced both | never reached: `block_matches` refused **all 99** intervals first, so the lesser fault hid the worse one |

After the fix all 110 blocks match. Before it, **105 of 110** could not have been spliced.

`tool-findings` for this run live in `TODO/`, not here:
[`correct-against-patch-is-a-conflict-and-is-not-flagged`](../../TODO/correct-against-patch-is-a-conflict-and-is-not-flagged.md)
and a second width measurement on
[`compact-can-buy-lines-with-width`](../../TODO/compact-can-buy-lines-with-width.md).

---

## Stage 5b -- the answers, which exist in no file

`galley.py` sets the joined text; `census.py` gives it an address; the roles are MESSAGED, not
re-dispatched. **Blocks 1, 25 and 61 went back -- the three where stage 5 composed more than one
role's mark.** ! The join printed **no** `RE-REVIEW` list: `contradictions()` flags `drop`
against `correct`/`patch`, and none of these carried a `drop`.

**Six answers over three roles: 5 HOLD, 1 REVISE.** Every reply came back in 12-100 seconds
with 1-3 tool calls.

```text
module-context  BLOCK 1   SAME SENTENCE yes  HOLD
  the tense change survived as "WOULD show" and block-context's added clause states the same
  currency defect my patch was for, so the finding is carried, not laundered

block-context   BLOCK 1   SAME SENTENCE yes  HOLD
  the 7a paragraph carries my finding outright, which is what SKILL.md's stage 7a and the open
  TODO both say

block-context   BLOCK 61  SAME SENTENCE yes  HOLD
  the false clause is gone and the replacement states both halves correctly

function-context BLOCK 61 SAME SENTENCE yes  HOLD
  galley 158-159 carries my true clause with only `and` dropped for width

function-context BLOCK 25 SAME SENTENCE no   HOLD
  my paragraph stands verbatim at galley 106-108 while the other three marks rule on the
  summary line, the staleness paragraph and a new docstring-specific paragraph

block-context   BLOCK 25  SAME SENTENCE yes  REVISE
  both my edits survived and function-context's `add` composes with them, but the count I
  supplied is wrong in the joined block: `main` stops a file on three paths, not two
```

!! **THE `REVISE` IS THE RESULT.** A role read its OWN round-1 correction in the joined block
and found that it miscounted -- it had written *"one of the two failures that stop a file"* where
`main` stops a file on three paths. It filed a full record with four citations **against the
galley census**, not its round-1 index. **Nothing else in the pipeline was positioned to catch
it:** the round-1 gate had already passed that finding, and stage 8 runs after the write.

! **`module-context` answered `SAME SENTENCE yes` on block 1**, where its `patch` and
block-context's `correct` were on one sentence and the gate flagged nothing. That is the
finding behind `correct-against-patch-is-a-conflict-and-is-not-flagged`.

## Stage 6 -- COMPACT, and what a cap costs

One block over the cap. The compact agent returned it at 4 lines.

| | lines | longest line |
| --- | --- | --- |
| after stage 5 | 5 | 79 |
| after COMPACT | 4 | **87** |

! It stayed inside the published width of 88 and **still took the free move**, spending the
whole headroom between what the file writes and what the limit permits. The first run to reach
stage 6 had no width in its input and came back at 98-100 columns; this one had it and came back
at 87. **So the published width is not the missing input** -- that is the second measurement on
`compact-can-buy-lines-with-width`.

## Stage 6b -- is it still correct after shortening?

```text
block-context    BLOCK 61  SAME SENTENCE yes  HOLD
  the clause my `correct` turned on is intact -- "the file's lines for a comment run, the AST
  value for a docstring" still sets the two forms against each other in one breath, and "own"
  was emphasis rather than the distinction itself

function-context BLOCK 61  SAME SENTENCE yes  HOLD
  both halves survive and "own" was emphasis rather than content, so nothing a reader must
  know was cut; the widening to 87 columns costs the block nothing
```

Both measured the compacted widths themselves before answering.

---

## What is in here

```
context.md              the stage-4 packet, as `run_context.py --check` passed it
census.txt              stage 2-3, the reviewers' copy
census.json             the same, as the tools read it
pinned-census.json      re-censused at 6c863b3 AFTER the raw_lines fix -- what the galley used
records/*.json          the four filled record files, as the roles left them
join.txt                the stage-5 gate, exit 0, against a worktree pinned at 6c863b3
edits.json              stage 5's rulings: one replacement per block, 8 blocks
galley/galley.py        the proposal spliced into a copy -- what 5b read
galley-census.json      that copy, censused, so a round-2 record has a real address
galley-compacted/       the same after stage 6, and `galley6-census.json` for 6b
```

! **`census.json` and `pinned-census.json` differ in `raw_lines` and `lines` only** -- the first
was taken before the docstring fix, the second after. Block boundaries are identical, 110 either
way, which is how the fix was shown to be structure-preserving.

! **No `vocabulary` output is kept.** `SKILL.md` requires it be run and pasted, never staged
through a file, so a copy here would be an artifact of exactly the kind that rule forbids.
