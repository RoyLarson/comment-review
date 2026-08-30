# Reconciliation has no command, so the chain cannot be driven end to end

```
Status:   open
Progress: 2 of 6 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-29 (2026-08-29, running the chain end to end for the first time with a
          REAL reviewer agent -- census, mark --seed, the block-context agent, mark
          --check and taken_in are all commands; the middle is not)
```

## Objective

Reconciliation has no command, so the chain cannot be driven end to end.

## Tasks

- [ ] Implement the step that turns the copy chief's edit_copy into the docket
      `proof --docket` reads. Verify: with the filled edit_copies of a stage on
      disk, the chain census -> seed -> collate -> <this> -> proof runs with no
      Python written by hand.
      !! SUPERSEDED IN PART 2026-08-30, AND THIS IS THE REMAINDER. It read "A
      command turns one stage's checked edit_copies into a docket ... ONE command
      writes the docket `proof --docket` reads", and it was TICKED against that
      wording when `collate` landed. A review read the verify against what
      shipped and it is false: `collate` writes the copy chief's `edit_copy`,
      which is an ordinary edit_copy -- `{"role", "read_from", "sheets"}` -- and
      `proof --docket` reads `{"pages": [{"path", "sha", "alterations": [{"cue",
      "text"}]}]}`. `commands/proof.py` would refuse the one given the other.
      ! WHAT DID LAND IS THE FOLD, and it is real: one stage's checked copies
      gathered, reconciled, automatically resolved where they can be, and folded
      into one copy with one mark per resolved place. The three tasks below it
      are ticked on their own terms and are unaffected.
      ! WHAT IS OWED HERE IS THE BRIDGE -- transcribing that copy into a docket,
      which is a known piece of work with its own scope elsewhere. This box stays
      open until the chain runs through to `proof`.
- [x] It reports what reconciliation decided, not just what settled. Verify: the
      command names the escalated and re-read places on stdout -- `docket_from`
      packages only the settled ones, so a run that settles 4 of 10 must say what
      became of the other 6 rather than dropping them silently.
- [x] Its exit code separates the three outcomes. Verify: a stage that settles
      everything, one that escalates, and one that owes a re-read are
      distinguishable by exit code alone, since the task agent branches on it.
- [ ] `tests/gates/test_skill_commands.py` sees it. Verify: the command appears in
      `COMMANDS`, `--help` names it, and the gate that checks SKILL.md's commands
      resolve covers this one.
- [ ] A command SEQUENCES the stages a topology names. Verify: one invocation runs
      stage 1, pulls revise-1, runs stage 2 against that revise, and stops -- the
      topology already expresses the order and `fan_out` already partitions, but
      nothing drives them.
- [ ] The command compares each returned edit_copy's read_from against the binder
      it was seeded from. Verify: a copy naming a different root or revise is
      reported by name, and one seeded from that binder passes --
      flows/marks.py:136-141 names this gap itself and says the comparison belongs
      wherever the two meet, which is the middle command once one exists.
