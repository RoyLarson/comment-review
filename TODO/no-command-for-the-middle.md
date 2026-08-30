# Reconciliation has no command, so the chain cannot be driven end to end

```
Status:   open
Progress: 0 of 5 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-29 (2026-08-29, running the chain end to end for the first time with a
          REAL reviewer agent -- census, mark --seed, the block-context agent, mark
          --check and taken_in are all commands; the middle is not)
```

## Objective

Reconciliation has no command, so the chain cannot be driven end to end.

## Tasks

- [ ] A command turns one stage's checked edit_copies into a docket. Verify: with
      the filled edit_copies of a stage on disk, ONE command writes the docket
      `proof --docket` reads, and the chain census -> mark --seed -> mark --check
      -> <this> -> proof runs with no Python written by hand.
- [ ] It reports what reconciliation decided, not just what settled. Verify: the
      command names the escalated and re-read places on stdout -- `docket_from`
      packages only the settled ones, so a run that settles 4 of 10 must say what
      became of the other 6 rather than dropping them silently.
- [ ] Its exit code separates the three outcomes. Verify: a stage that settles
      everything, one that escalates, and one that owes a re-read are
      distinguishable by exit code alone, since the task agent branches on it.
- [ ] `tests/gates/test_skill_commands.py` sees it. Verify: the command appears in
      `COMMANDS`, `--help` names it, and the gate that checks SKILL.md's commands
      resolve covers this one.
- [ ] A command SEQUENCES the stages a topology names. Verify: one invocation runs
      stage 1, pulls revise-1, runs stage 2 against that revise, and stops -- the
      topology already expresses the order and `fan_out` already partitions, but
      nothing drives them.
