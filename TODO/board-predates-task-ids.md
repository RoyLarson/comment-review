# The board predates task ids, and migrating it clears the decision queue

```
Status:   blocked
Progress: 0 of 5 tasks done
Owner:    systems
Requires-Roy: false
Raised:   2026-08-29 (2026-08-29, trialling the migration so a plan could name its tasks
          -- reverted the same session. The pipe handling is a fix in the tool rather
          than in this board, and is tracked where that tool is developed)
Updated:  2026-08-29 — waiting on the tool's pipe handling, which is fixed where that
          tool is developed
```

## Objective

The board predates task ids, and migrating it clears the decision queue.

## Tasks

- [ ] Migrate every task line to carry an id. Verify: the migration exits 0 with
      no file refused. It refuses nine today, because their task labels carry a
      literal pipe and the pipe is the column separator -- every one is legitimate
      content (a shell pipe, a regex alternation, a `--series` alternation), so
      the labels are not the thing to change.
- [ ] Restore the decision queue the migration clears. Verify: the requires-Roy
      query names the same files it named before the run. ! MEASURED 2026-08-29 on
      a trial that was reverted the same session: 57 files carried `Requires-Roy:
      true`, the flag is DERIVED from a task mark rather than a header field, and
      the migration creates no such marks -- so every one of them came back false
      and nothing errored.
- [ ] Mark the ruling task in each of those 57 files rather than restoring a
      header field. Verify: each file's flag is true BECAUSE a task carries the
      mark, so the query answers from the boxes and cannot drift from them again.
- [ ] Convert the six legacy plans in `docs/plans/` to the format the board reads.
      Verify: the board reads that directory without erroring -- it stops today at
      `0.2.4-rework-the-binder-hands-the-repo`, which has no `## TODO tasks this
      plan closes` heading. ! `0.2.4-the-commands-for-the-middle` already
      validates, so the format is proven against this repo.
- [ ] Decide whether the board tool is a committed dependency here. Verify: either
      `pyproject.toml` names it WITHOUT a machine-specific absolute path, or it
      does not name it and the tool is invoked from its own checkout. It was left
      uncommitted on 2026-08-29 for exactly that reason.
