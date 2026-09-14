# Reconciliation has no command, so the chain cannot be driven end to end

```
Status:   open
Progress: 77 of 92 tasks closed
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
- [x] T33 | a real two-turn run shows claim.to overwritten; T38 fixes it | 6b256ef5 | Implement
      a test of a move whose other end escalates, to settle whether turn.py:337
      overwrites claim.to
        > 2026-09-11 unconfirmed; a DiffMark correct or patch writes claim.to
        > 2026-09-11 by reading: the chief's c1 claim keeps the old false clause
        > 2026-09-11 final review probe: confirmed; deserialize at :402 accepts it
        > 2026-09-11 the probe called _answered directly; no real fold reaches it
        > 2026-09-12 waits on T41, left open by Process 120
        > 2026-09-12 Process 128: done now, from a real two-turn run
- [-] T34 | SUPERSEDED by T47 and T48: split | 60e477e2 | Update turn so a
      correct or patch answer quotes the slot's modified text, not the original,
      per Process 115
        > 2026-09-11 verify: a correct answer at an add's empty place composes
        > 2026-09-11 overlaps stay uncomposed as today; Roy agreed 2026-09-11
        > 2026-09-11 in an escalation: whose modified text a correct quotes, to report
        > 2026-09-11 waits on T39: the fold refuses a quote of the modified text
        > 2026-09-12 waits on T44, the quote check Process 119 rules
- [x] T35 | RULED Process: #116 -- goes back; their clean settles it | c0659be2 | Decide
      whether an add at an empty place settles when every other role cleans it;
      turn.py:320-345 keeps it a re-read
        > 2026-09-11 Process 89 says a lone mark stets when those roles agree
        > 2026-09-11 set in daa86dc8; T30's note records it
        > 2026-09-11 Roy: Process 49 stands; an add to an empty place goes back
- [ ] T36 | Update the history narration in added lines at test_turn.py:854 and
      :878
- [x] T37 | another role's clean adopts the add; all holding it is a stet | d4e98476 | Update
      turn so every other role answering clean at an add at an empty place
      settles it, per Process 116
        > 2026-09-11 undoes the plain clean daa86dc8 keeps; smoke drops 5 dispositions
- [x] T38 | a correct at a move's escalation keeps its destination | 685a16d0 | Update
      turn so no answer overwrites a move claim.to with paragraph text; T33
      confirmed it at turn.py:337
        > 2026-09-12 waits on T41, left open by Process 120
        > 2026-09-12 Process 128: done now, after T33's test
- [x] T39 | the page at the mark's address; for the turn, the text sent; P119 | 8894c9d3 | Decide
      how the fold verifies a turn-written correct or patch whose claim quotes
      the modified text, per Process 115
        > 2026-09-11 desk/collator.py:150-182 checks every quote against the binder
        > 2026-09-11 probe: claim.false is not in the paragraph this row seeded
        > 2026-09-12 Process 119: a check against the binder alone is faulty
        > 2026-09-12 collator.py:451 checks a place the binder lacks against empty text
- [x] T40 | an escalation's correct or patch claim quotes the role's proposal | 5ff707be | Update
      turn so a correct answer's claim derives its change: claim.false quotes
      what the answer replaces
        > 2026-09-11 T33's note: the chief's c1 claim keeps the old false clause
        > 2026-09-11 waits on T39, how the fold verifies it
        > 2026-09-12 waits on T44, the quote check Process 119 rules
- [x] T41 | Process 128: T33's test runs a real two-turn collate, now | c4eaeeee | Decide
      whether T33's test calls _answered directly, since collator.py:720-743
      never sends a move end an escalation
        > 2026-09-11 set 2's real collate: both move ends came back as re-reads
        > 2026-09-12 Process 120: open until we have experimented enough to know
        > 2026-09-12 by reading, 18e757ad escalates a move whose ends disagree
        > 2026-09-12 so Process 120's premise may no longer hold
- [x] T42 | Process 121: kept; a deferring query lets the add settle | 30b376ce | Decide
      whether a deferring query at an add's empty place settles the add, as
      d4e98476 does; Process 116 names only clean
        > 2026-09-11 test_a_role_with_no_slot_there_is_seeded_one_from_the_page
- [x] T43 | the test shows the defect; xfail strict until the fix lands | 5224085a | Implement
      a test of a mover's own clean at its move's origin, to settle whether
      _answered withdraws the move or makes it a correct
        > 2026-09-11 found by reading in set 2: _answered's filled-text branch
- [x] T44 | the quote check reads the page and the text a turn sent | f91722df | Update
      the quote check so it reads the page at the mark's address and, for a mark
      the turn wrote, the text collate sent there
        > 2026-09-12 Process 119; desk/collator.py:431-451 reads base_texts(binder)
        > 2026-09-12 Process 119: where no page can be read, the quote is refused
- [x] T45 | Process 122: it reports a page it cannot read; T46 does it | 1f9ba90d | Decide
      whether _resolution_problems at flows/collate.py:824-867 reports a page it
      cannot read, now the quote check refuses one
        > 2026-09-12 its docstring skips that case, citing Process 97
        > 2026-09-12 Process 111: an address is verified against its page, everywhere
- [x] T46 | an address whose page cannot be read is reported | fe13d10f | Update
      _resolution_problems at flows/collate.py:824-867 so a page it cannot read
      is reported, per Process 122
        > 2026-09-12 Process 122; its docstring skips that case, citing Process 97
- [x] T47 | a composition correct or patch quotes the text it was sent | 60e477e2 | Update
      turn so a composition correct or patch quotes the text collate sent, not
      the original, per Process 115
- [x] T48 | Process 123: carried forward; no change, the chief rules | c5b695de | Decide
      whether a composition correct or patch at an add's empty place composes
      with the add, or stays carried forward
        > 2026-09-12 T34's verify said composes; Process 115 leaves overlaps open
        > 2026-09-12 smoke b8, c3: the add and the answer both stand; chief takes in
- [x] T49 | Process 124: an escalation; T52 makes it so | c5b695de | Decide
      whether a composition correct beside another role's clean adoption folds
      as an escalation or a re-read
        > 2026-09-12 60e477e2 loosened test_turn.py:341 and :369 to accept either
        > 2026-09-12 before 60e477e2 it folded as an escalation
- [x] T50 | a mover's own clean at its origin keeps the move | 1b249d0d | Update
      _answered so a mover's own clean at its move's origin keeps the move;
      T43's xfail test pins it
        > 2026-09-12 T43 at 5224085a: clean when unchanged, correct when reworded
- [x] T51 | Process 125: the base reads the page, drift does not; T53 | c5b695de | Decide
      whether the composition base and the drift check read the page, not the
      binder, per Process 119
        > 2026-09-12 flows/collate.py:948 and commands/check.py:96 read base_texts
        > 2026-09-12 by reading: differs only for a file outside the binder
- [x] T52 | a contested re-read with two texts escalates, in the turn | 18e757ad | Update
      the fold so a composition correct beside another role's clean adoption
      folds as an escalation, per Process 124
        > 2026-09-12 test_turn.py:341 and :369 assert the escalation again
        > 2026-09-12 Process 127: decided in the turn, not the collator
- [x] T53 | a composition composes over the page's text | 7855a05b | Update the
      composition base to read the page's text at the mark's address, not the
      binder's, per Process 125
        > 2026-09-12 flows/collate.py:948 via base_texts; drift is left for T27
- [x] T54 | hold versus correct stays an escalation after the turn | 18e757ad | Update
      the fold so an escalation where one role answers correct and another holds
      stays an escalation after the turn
        > 2026-09-12 5ff707be: the answer quotes its proposal, the hold the original
        > 2026-09-12 found by probe in set 2; it now folds as a re-read
        > 2026-09-12 Process 127: the same step in the turn as T52
- [x] T55 | refold escalates what the last turn escalated | 52b32fc8 | Update
      refold so it applies the in-turn escalation step as run_turn does, per
      Process 127
        > 2026-09-12 refold misses _disagreeing; disposition sees b8, c3 as re-reads
        > 2026-09-12 no outcome moves today: rule_at_max_turns reads both lists
- [x] T56 | deleted; it rebuilt other claims unchanged, so nothing moved | f5c27575 | Delete
      the escalation fallback in _answered that rewrites a claim's true and to
      keys; no instruction reaches it since 685a16d0
        > 2026-09-12 correct, patch and move carry those keys; each is handled above it
- [x] T57 | the answer does not reach the move; xfail strict, T61 fixes it | 6ed51da4 | Implement
      a test of a mover's answer at its move's destination end, to settle
      whether it reaches the move
        > 2026-09-12 set 2: it lands on the mover's own seeded clean at that address
- [x] T58 | a move's claim.to is resolved against its page | d2114b38 | Update
      the resolution check so a move's claim.to resolves against its page, per
      Process 111
        > 2026-09-12 the overwritten claim.to in T33's run passed with no problem
        > 2026-09-12 _destination_problems says it does not ask this
- [x] T59 | Process 129: it reaches the move; T61 does it | 336b7a4c | Decide
      what a mover's answer at its move's destination end does: reach the move,
      or be refused there
        > 2026-09-12 T57 6ed51da4: it lands on the mover's clean; the move is unchanged
- [x] T60 | a clean carrying a filled change is refused | f5248790 | Update
      Mark.parse so a clean carrying a filled change is refused
        > 2026-09-12 T57's run: a turn wrote one and nothing refused it
        > 2026-09-12 Process 129: before set 2 merges
- [x] T61 | a mover's answer at the destination end reaches the move | e260438d | Update
      the turn so a mover's answer at its move's destination end applies to its
      move, per Process 129
        > 2026-09-12 T57's xfail test at 6ed51da4 pins it; remove the marker
- [x] T62 | Process 137: a move is two sided; both ends resolve together | 2a34928c | Decide
      whether a mover's answer to a composition re-read at its move's
      destination end reaches the move
        > 2026-09-12 outside Process 129, which covers escalation answers
- [x] T63 | a movers answer at a destination holding its own mark lands on that mark; xfail strict, question for Roy | 822ee987 | Implement
      a test of a role holding its own mark at a move's destination and a move
      there, to settle where its answer lands
        > 2026-09-12 e260438d routes to the move only past a clean or no slot
- [x] T64 | a movers answer where two of its moves land reaches neither and lands on a seeded slot; xfail strict, question for Roy | b5ef0bf9 | Implement
      a test of a role holding two moves to one destination, to settle where its
      answer lands
        > 2026-09-12 _move_to returns None for two; the answer stays on its slot
- [ ] T65 | Update T33's test in test_turn.py to use the two-turn helper T57's
      test and the withdraw test share
        > 2026-09-12 e260438d added the helper; T33's test repeats its setup
        > 2026-09-12 f2a2d47b's both-ends test repeats the same turn-1 setup
- [x] T66 | turn exits 7 as collate does | f85ea724 | Update turn so it exits 7
      when its fold carries places forward and a role left a place unruled, per
      Process 133
        > 2026-09-12 collate exits 7 since 685f2ecb
        > 2026-09-12 collate exits 7 since 685f2ecb
- [x] T67 | renamed for the exit 7 it asserts | 84601860 | Update the name of
      test_an_unanswered_slot_is_COVERAGE_and_the_place_stays in
      tests/test_turn_command.py, which asserts exit 7
        > 2026-09-12 f85ea724 moved its expected code to CARRIED_AND_UNRULED
- [x] T68 | a settled move is written once in the chief's copy after the wire | c7ca8be5 | Update
      the chief copy so a place determined at turn 0 appears once;
      chief-final.json carries fib.py@b1's move twice
        > 2026-09-12 smoke 2026-09-12 18:27: chief.json has it once, chief-final twice
        > 2026-09-12 the docket lists b1 and b0 twice; --from-docket would refuse it
        > 2026-09-12 Roy 2026-09-12: fixed in set 4
- [-] T69 | SUPERSEDED by T70, T71 and T72: Process 138 | c7930fb2 | Update the
      turn so a mover's composition answer at its move's destination end reaches
      the move, per Process 137
        > 2026-09-12 T61 reroutes escalation answers only; e260438d
- [x] T70 | correct and patch set the move's text; both ends tested together | c7930fb2 | Update
      the turn so a mover's composition correct or patch at its move's
      destination end reaches the move, per Process 137
- [x] T71 | a mover's clean at the destination keeps the move | 162c8b43 | Update
      the turn so a mover's clean at its move's destination end keeps the move,
      per Process 138
        > 2026-09-12 the composition table would read it as a withdrawal
- [x] T72 | a mover's query at the destination holds both ends | 84d7641d | Update
      the turn so a mover's query at its move's destination end holds both ends
      of the move, per Process 138
        > 2026-09-12 written over the move entry today it would remove the move
- [x] T73 | the move is lost at the origin; xfail strict, a fix is filed | 935b6bed | Implement
      a test of a mover's composition correct or patch at its move's origin, to
      settle whether the move is lost
        > 2026-09-12 by reading: _as_answered makes the move a correct or a patch
- [x] T74 | an unchanged move never settles; xfail strict, a fix is filed | 09c9b6e0 | Implement
      a test of every role cleaning a move whose text is unchanged, to settle
      why neither end settles
        > 2026-09-12 T69's probe: both ends went back as re-reads again
- [x] T75 | the ends split across the carried lists; xfail strict, fix filed | 1f867373 | Implement
      a test of a move whose ends disagree after a turn, to settle whether
      _disagreeing splits them across the carried lists
        > 2026-09-12 by reading in T69; the fold's own pairing keeps them together
- [x] T76 | a mover's correct or patch at the origin keeps the move | c6ee610d | Update
      the turn so a mover's composition correct or patch at its move's origin
      keeps the move, per Process 137
        > 2026-09-12 T73's xfail at 935b6bed: the move becomes a correct or a patch
        > 2026-09-13 Roy 2026-09-13: fixed before the move branch merges
- [x] T77 | every role cleaning an unchanged move settles both ends | 7fd6a549 | Update
      the fold so every role cleaning a move whose text is unchanged settles it,
      per Process 89
        > 2026-09-12 T74's xfail at 09c9b6e0: both ends go back as re-reads each turn
        > 2026-09-12 fixing it breaks test_it_follows_the_movers_clean_there's turn 2
        > 2026-09-13 Roy 2026-09-13: fixed before the move branch merges
- [x] T78 | both ends of a move escalate together | b09692ab | Update
      _disagreeing so a move's two ends land in the same carried list, per
      Process 137
        > 2026-09-12 T75's xfail at 1f867373: the destination escalates, the origin not
        > 2026-09-13 Roy 2026-09-13: fixed before the move branch merges
- [x] T79 | a reworded move is lost over two all-clean turns; xfail, fix filed | 17d0491d | Implement
      a test of a reworded move over two all-clean turns, to settle whether the
      move is lost
        > 2026-09-12 round 2's probe: both ends ended as withdrawn stets
- [x] T80 | a mover's query at the origin loses the move; xfail, fix filed | 7b728ca0 | Implement
      a test of a mover's query at its move's origin, to settle whether the move
      is lost
        > 2026-09-12 by reading: the query is written over the move entry
- [x] T81 | the clean-slot half of apply's routing is tested and holds | efb89e43 | Implement
      a test of apply routing to a move where the mover's slot at the
      destination is a clean
        > 2026-09-12 by reading: after 162c8b43 no test reaches that half
- [x] T82 | a place with no roles is carried to the chief, nothing lost | 3f1d2550 | Implement
      a test of a place carried forward with no roles left, to settle whether
      any turn is sent it
        > 2026-09-12 round 2: a deferring query leaves the destination with no roles
- [x] T83 | a mover's clean at the origin keeps the move | 12990b28 | Update the
      turn so a mover's clean at its move's origin keeps the move, per Process
      137 and 138
        > 2026-09-13 T79's xfail at 17d0491d: turn 2's origin clean withdraws it
- [x] T84 | a mover's query at the origin holds both ends | f10de03b | Update
      the turn so a mover's query at its move's origin holds both ends, per
      Process 137 and 138
        > 2026-09-13 T80's xfail at 7b728ca0: the query is written over the move
- [-] T85 | SUPERSEDED by T86: Process 139, the chief rules each end | 80e15c4b | Update
      disposition to refuse a ruling that treats a move's two ends differently,
      per Process 137
        > 2026-09-13 round 3: origin original, destination the move; the origin is lost
- [x] T86 | each end of a split move is written as its own drop or add | 0f9657a0 | Update
      disposition so the chief's ruling at each end of a move takes effect on
      its own section, per Process 139
        > 2026-09-13 round 3: a split ruling lost the origin's ruling
- [x] T87 | a reworded move never settles; xfail strict, a fix is filed | 2fb8c079 | Implement
      a test of a reworded move every role cleans over two turns, to settle
      whether it settles
        > 2026-09-13 round 4, by reading: turn 2's clean withdraws its adoption
- [x] T88 | a reworded move every role cleans settles at turn 1 | cb42539e | Update
      the turn so a reworded move every role cleans settles, per Process 89
        > 2026-09-13 T87's xfail at 2fb8c079; after turn 1 no agreement was read
        > 2026-09-13 it reaches the chief at max turns, so nothing is lost
        > 2026-09-13 Roy 2026-09-13: the last round before the move branch merges
- [x] T89 | the add lands; the held origin's drop misses 7a; xfail, fix filed | ed8afe94 | Implement
      a test of a move whose origin is held for the human while the chief rules
      its destination, to settle what lands
        > 2026-09-13 round 5, by reading: only the destination's add is written
        > 2026-09-13 Roy 2026-09-13: the last round before the move branch merges
- [x] T90 | a held move origin carries the moves drop on the proof and in disposition output | a67fba8a | Update
      the unsettlable entry for a move's held origin so the move's drop rides
      with it to the human at 7a, per Process 90 and 139
        > 2026-09-13 T89's xfail at ed8afe94: text at both ends until 7a
- [x] T91 | a reworded move settles with the movers origin unanswered and one as it stands does not; xfail strict, question for Roy | c6c28bc5 | Implement
      a test of a mover that leaves its origin slot unanswered while every role
      holds one text, to settle whether it settles
        > 2026-09-13 by reading: cb42539e reads copies, not the turn's answers
- [ ] T92 | Delete T79's test in tests/test_turn.py, which since cb42539e runs
      T87's route with weaker assertions
        > 2026-09-13 round 6: T79's turn-1 assertion went with the fix
