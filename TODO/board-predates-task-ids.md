# The board predates task ids, and migrating it clears the decision queue

```
Status:   in-progress
Progress: 2 of 6 tasks closed
Owner:    systems
Requires-Roy: true
Raised:   2026-08-29 (2026-08-29, trialling the migration so a plan could name its tasks
          -- reverted the same session. The pipe handling is a fix in the tool rather
          than in this board, and is tracked where that tool is developed)
Updated:  2026-08-29 — waiting on the tool's pipe handling, which is fixed where that
          tool is developed
Measured: 2026-08-30 — the plan's section B cites a-revise-answer-has-no-artifact T4, T5
          and T7 and NONE resolves -- that file writes ids as 'T4 --' where the tool
          reads 'T4 |'. The rollup still shows 0/8, so the count is right while three
          references are dead; only a write-side verb reports it
Cleared:  2026-09-02 — the 2026-08-30 blocker is gone. `de8efcd` migrated the board,
          so the tool no longer refuses a write and `migrate` reports every file
          already current. T1 and T4 close against `de8efcd` and `9876ff9`; what
          remains is T2/T3, the decision queue that migration cleared
```

## Objective

The board predates task ids, and migrating it clears the decision queue.

## Tasks

- [x] T1 | FINISHED -- migrate reports every file is already current, refusing none | de8efcd | Migrate
      every task line to carry an id. Verify: the migration exits 0 with no file
      refused. It refuses nine today, because their task labels carry a literal
      pipe and the pipe is the column separator -- every one is legitimate
      content (a shell pipe, a regex alternation, a `--series` alternation), so
      the labels are not the thing to change.
- [ ] T2 | Restore the decision queue the migration clears. Verify: the
      requires-Roy query names the same files it named before the run. !
      MEASURED 2026-08-29 on a trial that was reverted the same session: 57
      files carried `Requires-Roy: true`, the flag is DERIVED from a task mark
      rather than a header field, and the migration creates no such marks -- so
      every one of them came back false and nothing errored.
- [ ] T3 | Mark the ruling task in each of those 57 files rather than restoring
      a header field. Verify: each file's flag is true BECAUSE a task carries
      the mark, so the query answers from the boxes and cannot drift from them
      again.
- [x] T4 | FINISHED -- the board reads docs/plans; EXCLUDED FROM THE BOARD is 0 | 9876ff9 | Convert
      the six legacy plans in `docs/plans/` to the format the board reads.
      Verify: the board reads that directory without erroring -- it stops today
      at `0.2.4-rework-the-binder-hands-the-repo`, which has no `## TODO tasks
      this plan closes` heading. ! `0.2.4-the-commands-for-the-middle` already
      validates, so the format is proven against this repo.
- [?] T5 | Decide whether the board tool is a committed dependency here. Verify:
      either `pyproject.toml` names it WITHOUT a machine-specific absolute path,
      or it does not name it and the tool is invoked from its own checkout. It
      was left uncommitted on 2026-08-29 for exactly that reason.
- [ ] T6 | Unblock the writes the board tool now refuses. Verify: `job-board
      todo supersede-remaining` completes on this board. MEASURED 2026-08-30: it
      refuses with "56 file(s) state what their own boxes cannot, so a write
      would silently drop it" -- each carrying a hand-set Requires-Roy true with
      no task marked as owing a decision. The flag is DERIVED in that tool, so
      any write would recompute it false and erase 56 decisions from Roy's
      queue. ! THE REFUSAL IS CORRECT and it is the same erasure a trial
      migration caused and had to revert; what it means is that consolidating
      four TODOs into one now waits on this file.
