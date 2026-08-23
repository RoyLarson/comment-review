# comment-review over its own two most load-bearing files

**MARK only.** Four roles read `verdicts.py` and `record.py` and filed records; nothing was
joined, ruled, spliced or written. Kept because the findings are unharvested and re-creating
them costs what they cost: **~870,000 subagent tokens** -- 186k ownership, 184k module, 253k
function, 247k block.

**Subject:** `RoyLarson/comment-review` at **`9a74c5fadb0bd7376e855b9731a133951b7d235e`**, on
`main`. **1,120 census blocks, 154 holding prose.**

```
plugins/comment-review/skills/comment-review/scripts/verdicts.py
plugins/comment-review/skills/comment-review/scripts/record.py
```

! **The commit is pushed**, so a clone plus a checkout reproduces exactly what the roles read.
That is the fixture shape `evals/test-cases.jsonl` uses and the current harness cannot.

!! **WHICH SKILL RAN, precisely: the 0.2.3 tree SEVEN COMMITS BEFORE THE TAG.** Three files
under `plugins/` differ from `v0.2.3`, and two of them are read by a reviewer -- the brief's
verdict table became generated, and `ownership-context` was restated. So this is a 0.2.3
development tree and not the release; a rerun against the tag is not guaranteed to reproduce it.
! Naming which tree produced a measurement is why the version field exists at all.

---

## !! WHAT THE RUN WAS FOR, and the confound is different from the last one

Roy asked for it blind: *"run the system again pointed at these two files specifically in the
current context, not the extracted context -- don't tell the agents anything."* The question was
whether `module-context` would raise a module holding four subjects as a comment problem or a
code problem. **Nothing in any prompt mentioned subjects, imports, or the hypothesis.**

! The operating session knew what it was looking for; the ROLES did not. That is the opposite
of the confound in `cycle-0.2.3/`, where the operator's knowledge shaped the run.

! **The reviewers were the stage-1.6 fallback**, not the installed plugin agents -- the plugin
was v0.2.2 and the branch under test was ahead of it. Same caveat as `cycle-0.2.3/`.

---

## What came back

| role | records | substantive | code concerns |
| --- | --- | --- | --- |
| ownership-context | 155 | 7 -- 6 `drop`, 1 `move` | 0 |
| block-context | 156 | 23 -- 21 `correct`, 1 `patch`, 1 `query` | 4 |
| function-context | 157 | 23 -- 13 `correct`, 4 `patch`, 4 `add` | 2 |
| module-context | 157 | 7 -- 4 `correct`, 3 `patch` | 0 |

! Every file passes `record.py --check`. Three roles ran the join over their own file and
reported every finding admissible. **The four were never joined together** -- the work list
does not exist yet, and that is the harvest still owed.

## The answer to the question it was run for

`module-context` **found it** -- the summary line names one half of what the file holds, and its
reason enumerates `VERDICTS`, `Verdict`, `QUERY_SHAPES`, `ANCHOR_NAME`, `ANCHOR_SIDE`,
`claim_keys` and the fact that `record.py` imports that table -- and then filed a **`patch`
widening the docstring to announce two subjects**, with `code_concerns` empty.

!! **That is the defect its own role file names as the trigger.** The file lists *"a summary
line that describes one half of what the file contains"* under *"The finding is a module
announcing more than one subject"*, and never says what verdict that finding earns. The same
file DOES say a misplaced module constant is a `CODE CONCERN`. The pattern exists and was not
applied. Kept as the one MISS in `evals/test-cases.jsonl`.

## Findings already acted on

Three, all incidental to the question, and all real:

- `record.py main()` printed `0 problem(s)` and exited 1 when the only failure was a missing
  `record_version` -- the count was `len(problems)` and the version sentence is not in that
  list. Fixed 2026-08-18.
- `claim_keys` was added on this branch to make the claim keys one row, and reached **two of
  four sites** -- `record.claim_object` and `verdicts.payload_problem` still hardcode the
  names. Open.
- `record.check()` raises `AttributeError` on a report that is not a JSON object, where
  `verdicts.load_report` guards it. Open.

! **The other ~57 substantive verdicts are unread.** They are prose findings about the two files
the whole system rests on, and they are what this package is kept for.

## What is in here

```
context.md          the stage-4 packet, as `run_context.py --check` passed it
census.txt          stages 2-3, the reviewers' copy
census.json         the same, as the tools read it
records/*.json      the four filled record files, as the roles left them
```

! **No join output**, because there was none. Joining these four is the first thing a harvest
does, and it needs a worktree pinned at the commit above -- the tree has moved since.
