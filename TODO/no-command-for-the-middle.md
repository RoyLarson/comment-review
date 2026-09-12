# Reconciliation has no command, so the chain cannot be driven end to end

```
Status:   open
Progress: 20 of 36 tasks closed
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

- [x] T1 | the bridge is flows/revise.docket_of, the proof flow's first step; the chain runs through to proof as four commands, asserted by tests/test_the_chain.py | b80836e | Implement
      the step that turns the copy chief's edit_copy into the docket `proof
      --docket` reads. Verify: with the filled edit_copies of a stage on disk,
      the chain census -> seed -> collate -> <this> -> proof runs with no Python
      written by hand. !! SUPERSEDED IN PART 2026-08-30, AND THIS IS THE
      REMAINDER. It read "A command turns one stage's checked edit_copies into a
      docket ... ONE command writes the docket `proof --docket` reads", and it
      was TICKED against that wording when `collate` landed. A review read the
      verify against what shipped and it is false: `collate` writes the copy
      chief's `edit_copy`, which is an ordinary edit_copy -- `{"role",
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
- [-] T10 | SUPERSEDED against the 2026-08-17 ruling (the-record-is-a-parsed-template T2): no CLI writes a mark; re-filed as T13, the check | 6b673f0 | Implement
      the command a reviewer runs to write one mark into its edit_copy, so a
      role does not hand-write JSON
        > 2026-09-01 MEASURED 2026-09-01: no such command has ever existed. The ten in
        > 2026-09-01 COMMANDS hand a copy OUT (distribute --seed) and fold it back
        > 2026-09-01 (collate); none writes a mark. reviewer-brief.md names no command
        > 2026-09-01 at all -- Process 41 emptied that section -- and tells a role to
        > 2026-09-01 FILL a record, which today means hand-writing the JSON.
        > 2026-09-02 audit: the label opens with Implement -- this is work
        > 2026-09-02 Roy answered it in substance at 3ffe334; no ruling is owed
- [ ] T11 | Implement the one-line round summary from Collated.tally, or delete
      tally if the report does not want it
- [x] T12 | FINISHED; distribute --topology --stage, one copy per dispatch through fan | d6d04d3a | Implement
      distribute taking a stage, so one call seeds one edit_copy per dispatch.
      Verify: fan and topology.read each gain a caller in src/
        > 2026-09-01 Process #74. Both had zero callers in src/ when this was filed
        > 2026-09-01 Fan-out was the one topology shape no command could reach
- [x] T13 | FINISHED -- commands/check.py over EditCopy.deserialize, mark_errors, verify_report, drift_in and parse_answers; tests/test_check_command.py | 6b673f0 | Implement
      the check a role runs over its copy or batch before returning it, on the
      fold's own boundaries. Verify: refusals named
- [ ] T14 | Update reviewer-brief.md so a role runs check over its copy and its
      batch before returning either. Verify: the brief names the command
        > 2026-09-04 agents lane: the brief's wording is theirs; check is 6b673f0
        > 2026-09-04 hand 6: python -m fails at the root; src/comment-review.py runs
- [ ] T15 | Update check.py's header: drop MEASURED, condition the guarantee on
      --binder, name _load_value. Verify: it says so
        > 2026-09-04 hand 6's four-way stet is the text; hands/h6/chief.json
- [x] T16 | FINISHED -- turn (4040acea) and cap (54bde260) are console verbs over flows.turn; the chain gather, distribute, collate, turn, cap runs with no Python written by hand | 54bde260 | Implement
      the turn and cap commands over flows.turn, the master proof as the state
      between them. Verify: game.py's verbs run as commands
        > 2026-09-04 the scratchpad game.py (deal, turn, cap) is the specification
- [x] T17 | FINISHED -- flows/proof_io.py: load_binder, load_copy, load_proof, load_batch, load_value, save_proof, save_copy, save_batch; check._load, _load_value and collate._load deleted; seven commands read through it | 6cc6e742 | Implement
      one loader for the middle's commands; turn and cap import check's private
      _load and collate keeps its own. Verify: one definition
        > 2026-09-04 widen to proof_io: load_binder/copy/batch/value, save_copy
- [x] T18 | FINISHED -- run_turn(proof, binder, root, sent, answers) and refold share _unpacked; MasterProof.turn is the number; grep len(proof.turns) in src returns the container alone | 0611de3e | Update
      run_turn and refold to take the MasterProof, and derive the turn number on
      the container. Verify: no len(proof.turns) in commands/
- [x] T19 | FINISHED -- run_turn returns one Collated with its Revisits folded into revisit; turn.py merges no lists | 0611de3e | Update
      run_turn to fold its Revisits into Collated.revisit and return the
      Collated alone. Verify: turn.py merges no lists
- [ ] T20 | Implement a Turn record container with seed, serialize and
      deserialize, written by the flow. Verify: turn.py composes no record dict
- [ ] T21 | Implement a typed Unsettlable record held by Collated and
      MasterProof. Verify: proof_after strips nothing
- [ ] T22 | Implement a Ruling container and a rulings_at_cap flow that stacks
      refusals. Verify: cap.py parses no ruling by hand; check --rulings
- [x] T23 | FINISHED -- flows.turn.close returns the closed proof and the chief; cap.py calls replace nowhere | 7f59a7f4 | Update
      determined_chief or a close flow to return the closed MasterProof. Verify:
      cap.py calls replace nowhere
- [x] T24 | FINISHED -- Binder.root; the four sites read Path(args.repo) if args.repo else binder.root; the lint delta is the commit after | 231d5cf9 | Implement
      Binder.root and drop the args.repo-or-root-or-dot fallback at four
      commands. Verify: one resolution of the root
- [ ] T25 | Update turn and cap to fold without re-serializing the proof's
      copies, and cap without a refold. Verify: each mark parses once per
      command
- [x] T26 | FINISHED -- the hand driver lives in tests/helpers.py over conftest.run_command; test_turn_command, test_cap_command and test_gather_command drive main() through it | 171bfdb8 | Update
      test_turn_command, test_cap_command and test_gather_command to drive
      main() through run_command, with the hand driver in helpers.py
- [ ] T27 | Update the command tests to deal each distinct hand once per module
      and gather each case once. Verify: 9 collate runs become 2
- [ ] T28 | Implement the outcome once: exit codes, _report, the Revisit
      printer, the refused handler and the batch write, shared by three commands
- [x] T29 | a composition answer at a real place seeds a slot, as fill does | 30071cf1 | Update
      turn so a role answering a composition re-read at an add's empty place is
      not refused for having no slot
        > 2026-09-11 flows/turn.py:323; collate sent the place to all four roles
        > 2026-09-11 smoke run 2026-09-11: 9 answers refused, b8 c3 a2 b15 b17
        > 2026-09-11 stands: Process 49 reaffirmed; the roles need the slot
- [x] T30 | a clean at an add's empty place says nothing further | daa86dc8 | Update
      turn so the adding role's own clean answer on its add is not read as a
      correct missing its clause
        > 2026-09-11 smoke run: block b8, function a2 c3, module b15 b17 refused
        > 2026-09-11 other roles' clean stays clean, not an adopted add; see daa86dc8
- [x] T31 | check --answers applies the answers through turn's own call | 0f01d744 | Update
      check --answers to refuse what turn refuses; it passed the answers turn
      then rejected
        > 2026-09-11 check printed 0 the fold would refuse for all four roles
- [x] T32 | RULED Process: #115 -- against the modified text | 301e685a | Decide
      what a role answers in a turn to propose different text at an add's empty
      place
        > 2026-09-11 composition correct, patch need a base clause: turn.py:294, :306
- [ ] T33 | Implement a test of a move whose other end escalates, to settle
      whether turn.py:337 overwrites claim.to
        > 2026-09-11 unconfirmed; a DiffMark correct or patch writes claim.to
        > 2026-09-11 by reading: the chief's c1 claim keeps the old false clause
        > 2026-09-11 final review probe: confirmed; deserialize at :402 accepts it
- [ ] T34 | Update turn so a correct or patch answer quotes the slot's modified
      text, not the original, per Process 115
        > 2026-09-11 verify: a correct answer at an add's empty place composes
        > 2026-09-11 overlaps stay uncomposed as today; Roy agreed 2026-09-11
        > 2026-09-11 in an escalation: whose modified text a correct quotes, to report
- [?] T35 | Decide whether an add at an empty place settles when every other
      role cleans it; turn.py:320-345 keeps it a re-read
        > 2026-09-11 Process 89 says a lone mark stets when those roles agree
        > 2026-09-11 set in daa86dc8; T30's note records it
        > 2026-09-11 Roy: Process 49 stands; an add to an empty place goes back
- [ ] T36 | Update the history narration in added lines at test_turn.py:854 and
      :878
