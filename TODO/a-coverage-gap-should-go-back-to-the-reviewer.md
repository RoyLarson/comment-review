# A coverage gap should go back to the reviewer, not be reported as a result

```
Status:   open
Progress: 0 of 6 tasks done
Owner:    session * Roy (1 ruling)
Requires-Roy: true
Raised:   2026-08-16 (Roy, on the re-sweep's `gap`: "looks like a different form of the
          SUPPRESSED or acquittal list - and should be dropped - if comment blocks are
          missed by a reviewer then they are returned to the reviewer to rule on")
```

## Objective

**A block a reviewer never accounted for is unfinished work, not a finding about the run.**
Today `verdicts.py` computes `all_blocks - found - clean` per reviewer, prints a COVERAGE GAP
naming the role, and exits nonzero. The run stops and a human reads a list of index numbers.

Roy ruled the other way: send those blocks back to the reviewer that skipped them and let it
rule. The gate keeps its job -- nothing passes unaccounted for -- but the outcome is a completed
census instead of a report that one is incomplete.

! **Why it groups with the two deleted lists.** Both of those let a reviewer stop early and have
the stopping recorded as a result: the acquittal list gave named reasons to pass a block over,
the suppression list withheld low-precision hits. A coverage gap is the same shape one level up
-- the reviewer stopped, and the system files the stopping rather than fixing it.

! **Not vocabulary.** The word was found by the 2026-08-16 re-sweep, which is how the ruling
came up, but what changes here is control flow.

## Tasks

- [ ] * Rule how the return happens: re-dispatch the same reviewer with only the missed indices,
      or re-dispatch it with the whole census again. The first is cheap and loses the context
      that produced the miss; the second costs a full pass. Nothing in the tree decides this.

- [ ] Decide what bounds it. A reviewer that returns an incomplete report twice has to stop
      somewhere, and *"send it back"* with no bound is a loop. Say what happens on the second
      failure -- that IS the case the current gate handles, so it must not simply be deleted.

- [ ] Change `sk-scripts/verdicts.py:263-275,524-532` -- `coverage_gaps` and its report -- once
      the two above are ruled. ! The function itself is still needed: computing what is missing
      is how you know what to send back.

- [ ] Update `ref/reviewer-brief.md:91-94`, which tells a reviewer the join *"reports any index
      you did not account for as a COVERAGE GAP against your role by name"*. Under the ruling
      the consequence is different, and naming-and-shaming is no longer what happens.

- [ ] Re-check `SKILL.md:82-84`'s *"coverage is a COMPLETE READ"* rule against the new flow. It
      states the principle correctly and should survive unchanged -- confirm rather than assume.
- [ ] !! **FRONT MATTER IS SEEDED BUT NEVER SHOWN, so every file carrying a
      licence header reports INCOMPLETE forever.** `record.prose_blocks` filters
      on `HOLDS_NO_PROSE` only; `census.py` drops front matter from `--filtered`;
      `verdicts.py` excludes it from coverage. So a slot is written for a block
      the reviewer is never shown, stays `null`, and `record.py --check` calls the
      file INCOMPLETE -- which SKILL.md tells the task agent means a reviewer
      stopped part-way. **One line: `prose_blocks` excludes `FRONT_MATTER`, as
      `verdicts.py` already does.**
