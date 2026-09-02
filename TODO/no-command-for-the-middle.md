# Reconciliation has no command, so the chain cannot be driven end to end

```
Status:   open
Progress: 5 of 11 tasks closed
Owner:    backend
Requires-Roy: true
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

- [ ] T1 | Implement the step that turns the copy chief's edit_copy into the
      docket `proof --docket` reads. Verify: with the filled edit_copies of a
      stage on disk, the chain census -> seed -> collate -> <this> -> proof runs
      with no Python written by hand. !! SUPERSEDED IN PART 2026-08-30, AND THIS
      IS THE REMAINDER. It read "A command turns one stage's checked edit_copies
      into a docket ... ONE command writes the docket `proof --docket` reads",
      and it was TICKED against that wording when `collate` landed. A review
      read the verify against what shipped and it is false: `collate` writes the
      copy chief's `edit_copy`, which is an ordinary edit_copy -- `{"role",
      "read_from", "sheets"}` -- and `proof --docket` reads `{"pages": [{"path",
      "sha", "alterations": [{"cue", "text"}]}]}`. `commands/proof.py` would
      refuse the one given the other. ! WHAT DID LAND IS THE FOLD, and it is
      real: one stage's checked copies gathered, reconciled, automatically
      resolved where they can be, and folded into one copy with one mark per
      resolved place. The three tasks below it are ticked on their own terms and
      are unaffected. ! WHAT IS OWED HERE IS THE BRIDGE -- transcribing that
      copy into a docket, which is a known piece of work with its own scope
      elsewhere. This box stays open until the chain runs through to `proof`.
- [x] T2 | FINISHED | unknown | It names the ESCALATED and RE-READ places, not
      just what settled. Verify: both appear on stdout -- `docket_from` packages
      only the settled ones, so a run that settles 4 of 10 says which of the
      other 6 escalated and which owe a re-read. ! Narrowed 2026-08-30; the
      unruled remainder is a task below.
- [x] T3 | FINISHED | unknown | Its exit code reaches three different values for
      the three outcomes. Verify: a stage that settles everything, one that
      escalates and one that owes a re-read do not share a code. ! Narrowed
      2026-08-30 from "distinguishable by exit code alone"; see the note.
- [ ] T4 | `tests/gates/test_skill_commands.py` sees it. Verify: the command
      appears in `COMMANDS`, `--help` names it, and the gate that checks
      SKILL.md's commands resolve covers this one.
- [-] T5 | SUPERSEDED by Process #73 -- the task agent sequences the stages from SKILL.md; no command dispatches an agent, so none can drive the horizontal | 7ef790d | A
      command SEQUENCES the stages a topology names. Verify: one invocation runs
      stage 1, pulls revise-1, runs stage 2 against that revise, and stops --
      the topology already expresses the order and `fan_out` already partitions,
      but nothing drives them.
- [ ] T6 | The command compares each returned edit_copy's read_from against the
      binder it was seeded from. Verify: a copy naming a different root or
      revise is reported by name, and one seeded from that binder passes --
      flows/marks.py:136-141 names this gap itself and says the comparison
      belongs wherever the two meet, which is the middle command once one
      exists.
- [x] T7 | FINISHED | unknown | Implement a drift signal that survives an
      escalation or a re-read in the same run. SUPERSEDED 2026-08-30 by
      `decision-log.md Process: #62` -- there is no drift signal to carry,
      because the middle touches no files. Roy: *"the middle doesn't care if the
      pages have changed - it is not reading or writing to the pages at all."*
      The deletion is a task on `collator-defects.md`.
- [x] T8 | commands/collate.py reports Collated.unruled as one routable Problem per place and returns COVERAGE for it, so a role that kept every slot and filled one no longer exits OK with the chief written. tally is still unreported and is its own task. | 3ffe334 | Implement
      the reporting of `Collated.unruled` and `Collated.tally` in
      `commands/collate.py`, so a run names every place carried forward rather
      than counting only the settled ones. Verify: a one-role stage over three
      places where nothing was ruled names all three addresses and does not exit
      0, since exit 0 means every place resolved and nothing carried forward;
      today it prints `0 places resolved` and exits 0.
- [ ] T9 | Implement carrying `Collated.order` out of `commands/collate.py`, so
      whatever applies the chief vacates every `move` origin before it is filled
      instead of re-deriving the order or applying moves unsafely. Verify: `grep
      -rn "\.order\b" src/` returns a consumer outside `flows/collate.py`, and a
      two-move stage's written artifact names the order; today the only readers
      are in `tests/test_collate.py`.
- [?] T10 | Implement the command a reviewer runs to write one mark into its
      edit_copy, so a role does not hand-write JSON
        > 2026-09-01 MEASURED 2026-09-01: no such command has ever existed. The ten in
        > 2026-09-01 COMMANDS hand a copy OUT (distribute --seed) and fold it back
        > 2026-09-01 (collate); none writes a mark. reviewer-brief.md names no command
        > 2026-09-01 at all -- Process 41 emptied that section -- and tells a role to
        > 2026-09-01 FILL a record, which today means hand-writing the JSON.
- [ ] T11 | Implement the one-line round summary from Collated.tally, or delete
      tally if the report does not want it
