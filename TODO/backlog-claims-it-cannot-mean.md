# The backlog claims things it cannot mean, and nothing was checking

```
Status:   open
Progress: 0 of 6 tasks done
Owner:    systems
Requires-Roy: true
Raised:   2026-08-24 (2026-08-24, sweeping TODO/ after two merges each turned up the
          same shape by hand)
```

## Objective

**The backlog claims things it cannot mean, and nothing was checking.** MEASURED 2026-08-24 by
`scripts/todo_sweep.py`, which was written from these findings and re-runs every one of them:

| what | how many |
| --- | --- |
| files in `completed/` carrying an unchecked box | **8** -- four with EVERY box open |
| files owing a ruling that `list --requires-roy` does not show | **10** |
| files flagged for Roy with no `*` box naming a ruling | **6** |
| TODO links resolving nowhere | **19** |
| cited commit hashes that no longer resolve | **6** |

!! **EVERY CHECK WAS FOUND BY HAND, ONCE, AND WAS THEN EVERYWHERE.** None was looked for.
`requires-roy-never-goes-back-down` was in `completed/` with FIVE unchecked boxes and
`Status: deferred`, and surfaced only because `todo_tool.py resync` REFUSED to reconcile the
README around it. Sweeping for the same shape found seven more. ! **That is the argument for
the script rather than for more care**: a defect that reaches eight files is not an attention
problem.

!! **THE FLAG MISMATCH IS THE ONE THAT COSTS ROY DIRECTLY.** `.claude/skills/todo-tool/SKILL.md`
says `--requires-roy` is *"how Roy pulls his own queue: everything waiting on"* him. Ten files
hold an unchecked `*` box -- an owed ruling -- with the flag down and no `deferred` or `blocked`
status to explain it, so **the queue is silently short by ten**. ! Seven MORE have the flag down
with an owed ruling and ARE deferred or blocked; those are correct, because what stops them is
work rather than an answer, and the sweep lists them separately so the distinction survives.

! **IT IS THE SAME FIELD `requires-roy-never-goes-back-down` IS ABOUT, FAILING THE OTHER WAY.**
That file records a flag that never comes DOWN; these are flags that never went UP. One tool
recompute would answer both, which is why T6 asks whether any of this earns a gate.

!! **AND A STALE HASH READS EXACTLY LIKE A GOOD ONE.** The 2026-08-23 history rewrite killed six
commits this backlog cites. Three are `evidence/self-test-commits.md`'s and are tracked in
[`the-harness-cannot-run-the-system-it-grades`](the-harness-cannot-run-the-system-it-grades.md)
T42; the other three are cited in TODO prose and are T5 here. ! **`git log` cannot answer this
question** -- an empty result is what a purged path and a path that never existed both look like
-- so `git cat-file --batch-check` is the check, and absence is settled on disk.

! **The sweep REPORTS and decides nothing**, on the ruling `dead_sweep.py` already carries. Roy,
2026-08-21: *"I don't think it deserves a gating. I do think it is a genuinely good idea to run
every now and then."* A closed file with an open box may need the box ticked or the file
reopened; a dead link may need repointing or deleting. Both are judgements about what the work
IS.

## Tasks

- [ ] T1 -- Tick or reopen the 8 files in `completed/` that carry unchecked boxes.
      Verify: `todo_sweep.py --closed` reports 0.
- [ ] T2 -- Raise `Requires-Roy` on the 10 files that owe a ruling with the flag
      down. Verify: `todo_sweep.py --flags` shows 0 in the first section.
- [ ] T3 -- Clear the flag, or write the `*` box, on the 6 flagged files that name
      no ruling. Verify: the second section of `todo_sweep.py --flags` reports 0.
- [ ] T4 -- Repoint or drop the 19 TODO links that resolve nowhere. Verify:
      `todo_sweep.py --links` reports 0.
- [ ] T5 -- Re-locate the 3 TODO-cited hashes the rewrite killed, named in the
      Objective. Verify: `todo_sweep.py --hashes` names only `evidence/`'s three.
- [ ] T6 -- * Rule whether any of these five checks earns a gate, or all stay
      inputs. Verify: the ruling is in `docs/decision-log.md`.
