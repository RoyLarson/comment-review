# Reconciliation has no command, so the chain cannot be driven end to end

```
Status:   open
Progress: 3 of 9 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-29 (2026-08-29, running the chain end to end for the first time with a
          REAL reviewer agent -- census, mark --seed, the block-context agent, mark
          --check and taken_in are all commands; the middle is not)
Narrowed: 2026-08-30 — T2 and T3 narrowed to what shipped. T2 claimed a run says what
          became of ALL the unsettled places; measured 2026-08-30, Collated.unruled and
          Collated.tally are discarded by the command, so a place nobody ruled on is
          still dropped silently. T3 claimed the outcomes are distinguishable by exit
          code ALONE; measured the same day, an unguarded write_text leaves main as a
          traceback so CPython exits 1 and the agent reads a filesystem failure as
          BROKEN, and the DRIFT code is masked by any escalation or re-read. Both boxes
          stay closed on their narrowed claims; the remainders are the three tasks added
          below and the write_text guard on collate-command-defects.
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
- [x] It names the ESCALATED and RE-READ places, not just what settled. Verify:
      both appear on stdout -- `docket_from` packages only the settled ones, so a
      run that settles 4 of 10 says which of the other 6 escalated and which owe a
      re-read. ! Narrowed 2026-08-30; the unruled remainder is a task below.
- [x] Its exit code reaches three different values for the three outcomes.
      Verify: a stage that settles everything, one that escalates and one that
      owes a re-read do not share a code. ! Narrowed 2026-08-30 from
      "distinguishable by exit code alone"; see the note.
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
- [x] Implement a drift signal that survives an escalation or a re-read in the
      same run. SUPERSEDED 2026-08-30 by `decision-log.md Process: #62` -- there
      is no drift signal to carry, because the middle touches no files. Roy: *"the
      middle doesn't care if the pages have changed - it is not reading or writing
      to the pages at all."* The deletion is a task on `collator-defects.md`.
- [ ] Implement the reporting of `Collated.unruled` and `Collated.tally` in
      `commands/collate.py`, so a run names every place carried forward rather
      than counting only the settled ones. Verify: a one-role stage over three
      places where nothing was ruled names all three addresses and does not exit
      0, since exit 0 means every place resolved and nothing carried forward;
      today it prints `0 places resolved` and exits 0.
- [ ] Implement carrying `Collated.order` out of `commands/collate.py`, so
      whatever applies the chief vacates every `move` origin before it is filled
      instead of re-deriving the order or applying moves unsafely. Verify: `grep
      -rn "\.order\b" src/` returns a consumer outside `flows/collate.py`, and a
      two-move stage's written artifact names the order; today the only readers
      are in `tests/test_collate.py`.
