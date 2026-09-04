# A role can be asked to revise and has nothing to answer ON

```
Status:   open
Progress: 35 of 35 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-28, filing the work `decision-log.md Process: #21` and `#22` created.
          Both were ruled the same day and neither had a backlog entry, so the plan
          steps that build them cited rulings rather than tasks.
Superseded: 2026-08-29 — 2026-08-29, `decision-log.md Process: #49`: a COMPOSITION of
            edits must be re-read, so the revise step now asks TWO questions -- *which
            of these?* on a conflict, and *does this still read?* on a composition --
            and five tasks here assumed only the first. !! T1 (the four answers) is the
            sharpest: **a role cannot `hold` or `withdraw` a claim it never made**,
            which is exactly what a composition re-read asks it to judge. T2 seeds a
            sheet PER CONFLICT; T3's four outcomes are all conflict outcomes; T6's
            *party to* was defined by disagreement and is now three routes -- disagreed,
            co-edited, or holds a page that took an `add`; T8's two-round cap counted
            rounds of DISAGREEMENT and no longer says what it counts. ! CHECKED AS
            SUPERSEDED, NOT DONE -- `CLAUDE.md`'s table, so the record of what they said
            stays legible. ! T4, T5 and T7 STAND: query routing, query counting and the
            cross-stage reversal are untouched by within-stage composition. ! THE
            REPLACEMENT WORK IS `T6.7`-`T6.11` of `docs/plans/0.2.4-the-mark-and-the-
            collator.md`, and the answer set itself waits on `no-mark-for-let-it-stand`
            T1, an open `agents` ruling -- publishing's `stet` is the candidate.
Reopened: 2026-08-30 — T8 unticked 2026-08-30: it claimed the two-round cap was enforced
          and no round or cap logic exists anywhere in src/comment_review. The re-read
          loop is the design's ONLY cycle, so this box was the sole thing standing
          between it and being unbounded
```

## Objective

**The revise round is fully specified and has no artifact.** A role is handed a conflict and
answers one of four; nothing carries the question and nothing carries the answer.

    hold        my mark stands
    withdraw    I retract it
    correct     a revised claim -- relitigates
    patch       revised wording -- relitigates

!! **THE FOUR ARE A CLOSED SET AND ALL FOUR ARE WRITTEN DOWN.** Roy, 2026-08-27: *"I would prefer
the explicit hold/withdrawn/patch/correct marks. Inferring the decision from lack of decision
means that the agents get to do the human failure of the anti-decision decision. Where we allow
undecided things to continue effectively making the decision to keep the status quo."*

! **AN INFERRED WITHDRAWAL IS INDISTINGUISHABLE FROM A ROLE THAT NEVER ANSWERED**, so the status
quo wins by default and nobody is on record as having chosen it. ! Same rule as an unchecked box
meaning work remains, and as `clean` being mandatory.

!! **AND THEY ARE NOT AN ADDITION TO THE SEVEN.** A diff-mark is a different artifact answering a
different question -- *does your finding still stand* rather than *what is wrong with this page* --
so it carries its own closed set. `correct` and `patch` appear in both because they are the two
that `rules_on_text`, which is a property of the row rather than a list.

### The four outcomes

| role A | role B | outcome |
| --- | --- | --- |
| a new mark | anything | **another round**, always -- an answer given against a state is stale once the state moves |
| holds | holds | the **copy chief**; both have declared they disagree |
| holds | withdraws | the held claim, mechanically `taken in` |
| withdraws | withdraws | pick one, revise double-check, mechanically `taken in` |

### What a `query` does here

| shape | what happens |
| --- | --- |
| `human-review-necessary` | raised to the HUMAN before the write flow sets any text |
| `unable-to-determine`, another role holding a mark | revise with the context of the question |

! **AND IT MEASURES SOMETHING.** Roy: *"The text has become ambiguous and probably should have had
the query mark from the first round."* **Queries first raised at revise count round-one
OVER-CLAIMING** -- the failure direction opposite to the one coverage measures.

! **THE OTHER ROLES' REASONING IS SHARED FROM ROUND TWO ON**, reversing the earlier design. Roy:
*"Besides the first round I don't think isolation buys accuracy over group-think. No new ideas in
no new concepts out."* ! Checkable rather than hoped: a role that re-read the code carries new
`sources` or a `ran`; one that agreed with the argument carries only prose.

### A REVERSAL IS THE SAME ARTIFACT, added 2026-08-28

**A later stage correcting a paragraph an earlier stage set is a disagreement between two roles
over one statement**, so it is a row on this sheet and not a re-run of anything. Roy, 2026-08-28:
*"The return to stage 1 only goes between the agents that disagree over the statement. It doesn't
restart the whole flow. Same as the other revise and in the same revise step."*

| row | its base | its sides |
| --- | --- | --- |
| a **conflict** -- two roles, one stage, one sentence | that stage's paragraph | the two proposed texts |
| a **reversal** -- a later stage undid an earlier one | the paragraph as the earlier stage left it | the later stage's text |

! **THE PAIRING IS WITH WHOEVER LAST SET THE STATEMENT**, which need not be the first stage: if
stage 2 already corrected a place and stage 3 reverses it, the two parties are stage 3 and stage
2. So the revise carries per-place PROVENANCE, and that provenance ROUTES the row rather than
merely counting it.

!! **THE CAP WAS ALREADY RULED AT TWO AND IS NOT NEW HERE.** `decision-log.md Process: #9`,
2026-08-24: *"the goal is revise ... gives the editorial roles two chances to figure out the
compromise with reasons"*, and `references/re-review.md:128` already states *"AT MOST TWO
re-review rounds."* What terminates the second round is the copy chief's `stet`.

## Tasks

- [-] T1 | SUPERSEDED 2026-08-29, Process 49 -- assumed only the conflict question; re-filed as T10 | 1a900d1 | T1
      -- The four answers as a closed set, derived from `rules_on_text` plus the
      two that are not marks. Verify: it cannot drift from `INSTRUCTIONS`, and a
      fifth answer is refused.
- [-] T2 | SUPERSEDED 2026-08-29, Process 49 -- seeded a sheet per conflict only; re-filed as T11 | 1a900d1 | T2
      -- A revise sheet, seeded per conflict, carrying the rendered diff.
      Verify: every row names the conflict it answers, and a row left unanswered
      is neither held nor withdrawn.
- [-] T3 | SUPERSEDED 2026-08-29, Process 49 -- four conflict outcomes only; re-filed as T15 | 1a900d1 | T3
      -- The four outcomes. Verify: any new mark relitigates; two holds
      escalate; hold plus withdraw takes the held claim in; two withdraws pick
      one and re-ask.
- [-] T4 | SUPERSEDED in part: human-review-necessary never returns to a role (99c7620); unable-to-determine ABSTAINS under Process 90 rather than carrying the question on | 99c7620 | T4
      -- Route a `query` by shape. Verify: `human-review-necessary` never
      returns to a role, and `unable-to-determine` carries the question into the
      next ask.
- [-] T5 | SUPERSEDED as filed in error -- Process #78. Roy: a random requirement a session added and was never asked for | eb49e56 | T5
      -- Count queries first raised at revise. Verify: the run reports the
      number, and it is zero on a set of marks where every query was raised in
      round one.
- [-] T6 | SUPERSEDED 2026-08-29, Process 49 -- party-to was disagreement alone; re-filed as T11 | 1a900d1 | T6
      -- A revise sheet is addressed to a ROLE, not to a stage, and carries only
      the rows that role is party to. Verify: a role party to one place in a
      stage it did not otherwise join receives a one-row sheet, and no row names
      a place it is not party to.
- [-] T7 | SUPERSEDED into a-role-can-reverse-itself-between-runs T3 -- it is agent-output variance across two runs, not a claim about the process, so it is agents' and not a code gate | f196ef9 | T7
      -- A reversal is a row, paired with whoever LAST set the statement.
      Verify: stage 3 reversing a paragraph stage 2 set pairs with stage 2 and
      not with stage 1, read from the revise's per-place provenance.
- [-] T8 | SUPERSEDED by Process #78 -- the round bound is what the task agent is told, not what the code enforces, and the Process 9 citation resolved nowhere | eb49e56 | T8
      -- Enforce the two-round cap `Process: #9` already ruled. Verify: a third
      round cannot start, the place reaches the copy chief carrying every
      round's marks, and the run reports the rounds each place took.
- [x] T9 | RULED Process 87: a chief-only Determined per resolved place, on the master proof with the turn record | 77fccea | Decide
      what records HOW the copy chief ruled, since an edit_copy cannot. Verify:
      the artifact exists, or the question is answered in the log
        > 2026-09-02 Roy 2026-09-02: that needs something besides the edit-copy
- [x] T10 | FINISHED as a prototype -- desk/diff_mark.py; a fifth and Mark's seven refused by name, test_diff_mark.py | bc62ea5 | Implement
      the DiffMark a role answers a disagreement on, four answers closed.
      Verify: a fifth, or any of Mark's seven, is refused by name
        > 2026-09-03 prototype at desk/diff_mark.py, 5574f0a -- P20; replaces T1
- [x] T11 | FINISHED -- flows.turn.batch_for attaches every slot's diff3 at the flow; one send per role | 28981c8d | Implement
      the batch: one payload per role per round, each slot carrying its diff3.
      Verify: one send per role whatever the place count
        > 2026-09-03 prototype batch_of 9406b3b -- P21; the FLOW attaches diff3
        > 2026-09-03 replaces T2 and T6
- [x] T12 | FINISHED as a prototype -- parse_batch and flows/turn.parse_answers; unanswered refused by name, test_turn.py | bc62ea5 | Implement
      the return: a role's answered batch parses at the boundary. Verify: an
      unanswered slot is refused by name, never read as withdraw
        > 2026-09-03 prototype parse_batch 37fbbb8 -- P16
- [x] T13 | FINISHED -- a lone add is its own composition; every role's clean lands it; test_turn.py TestALoneOwingMark | 45d3e61 | Implement
      the recollate so a round's resolutions join the chief's copy. Verify: a
      lone surviving add, all others holding, lands
        > 2026-09-03 P17. Measured hand 3: a lone add re-reads forever today
        > 2026-09-04 Process 86: composed text goes into every copy, then recollate
        > 2026-09-04 bc62ea5: a clean from the adder withdraws the add -- open
- [x] T14 | RULED Process 86: an escalation answers with a DiffMark, a composition re-read with a fresh Mark | 38bc37b | Decide
      whether a composition re-read is answered with a DiffMark or a fresh Mark,
      given clean and query are its only passes
        > 2026-09-03 P1/P6. the-turn.md: clean and query are a composition's passes
        > 2026-09-03 the prototype takes no side -- desk/diff_mark.py docstring
- [x] T15 | FINISHED -- hold/hold another turn, hold/withdraw takes the held in after the read, withdraw/withdraw a stet of the original, how withdrawn; test_turn.py | d4d7cd8 | Implement
      the conflict outcomes: hold/hold next round, hold/withdraw takes the held
      in, withdraw/withdraw re-asks. Verify: each lands
        > 2026-09-03 P5; replaces T3's conflict half -- the Objective's outcomes table
        > 2026-09-04 Process 86: withdraw reverts to base; correct/patch write change
        > 2026-09-04 bc62ea5: withdraw/withdraw drops the place with no Determined
- [-] T16 | SUPERSEDED, reworded -- the word is turn, Vocabulary 33; re-filed as the turn counter | efd9221 | Implement
      the round counter, rounds named by kind, no maximum enforced. Verify: a
      run reports each place's rounds
        > 2026-09-03 P18. Process 78: the cap is the agent's, never the code's
- [x] T17 | FINISHED -- determined_chief refuses while a carried place is unruled, naming it and its roles; unsettlable excepted; test_turn.py | d1ddbd8 | Implement
      the copy chief's ruling at the cap on whatever is still unresolved.
      Verify: no place survives the last round unruled
        > 2026-09-03 P19. the-turn.md: the chief's ruling is the terminator
        > 2026-09-04 bc62ea5: rule_at_cap exists; nothing enforces every place ruled
- [x] T18 | FINISHED -- parse_answers, apply and run_turn return Revisits; check prints them as collate does; test_turn.py | f4e746b | Implement
      routing of a refused or unanswered DiffMark to its role as a revisit.
      Verify: it appears in revisit naming role and address
        > 2026-09-03 Roy 2026-09-03: unanswered or malformed is refused, not a withdraw
        > 2026-09-04 bc62ea5: a refused answer is a problem string, not a Revisit
- [x] T19 | FINISHED -- diff_mark.allowed and turn.contracts generate the three shapes; check --contract prints them; the brief's publishing is T14 (agents) | 28981c8d | Generate
      the DiffMark contract a role is handed from the code, as allowed() does
      for Mark. Verify: no agent file hand-types its fields
        > 2026-09-03 the game's brief hand-typed the contract and got query wrong
        > 2026-09-03 publishing it in the brief is agents lane; the generator is backend
        > 2026-09-04 hand 4: a role answered a DiffMark patch meaning keep my patch
- [x] T20 | FINISHED as a prototype -- Determined.turn on every place, MasterProof.turns; no maximum in code | bc62ea5 | Implement
      the turn counter, turns named by kind, no maximum enforced. Verify: a run
      reports each place's turns
        > 2026-09-04 P18. Process 78: the cap is the agent's, never the code's
- [x] T21 | FINISHED as a prototype -- batch_of seeds a Mark slot for a reread, a DiffMark slot for an escalation | bc62ea5 | Update
      batch_of so a reread seeds a Mark slot over the composed text, an
      escalation a DiffMark. Verify: no DiffMark field on a reread
        > 2026-09-04 Process 86; a lone add must compose without a re-read -- T13
- [x] T22 | FINISHED as a prototype -- desk/determined.py; Mark's seven and DiffMark's four refused by name | bc62ea5 | Implement
      Determined, the chief's per-place record: stet, taken_in, recast. Verify:
      Mark's seven and DiffMark's four are refused
        > 2026-09-04 Process 87; Roy's name, taken until a trade word turns up
- [x] T23 | FINISHED as a prototype -- MasterProof.turns and .determined round-trip, test_determined.py | bc62ea5 | Update
      MasterProof to carry the turn record and one Determined per resolved
      place. Verify: a serialized proof round-trips both
        > 2026-09-04 Process 87: the master proof is the state between turns
- [x] T24 | FINISHED as a prototype -- _chief_copy derives from the Determineds; original taken in writes no entry | bc62ea5 | Update
      _chief_copy so the chief's edit copy is derived from the Determineds.
      Verify: every place in it names its Determined
        > 2026-09-04 Process 87: Process 30's shape holds, one mark per place
- [-] T25 | SUPERSEDED by T35 under Process 91: once stet, a place leaves every later batch and keeps its turn | 7e2c6b4 | Update
      run_turn so a Determined keeps the turn the place first agreed on. Verify:
      agreed on turn 1, it reads turn 1 after turn 2's fold
        > 2026-09-04 game hand 1: function's t2 answer refused for a dropped key
        > 2026-09-04 the note above is T27's, misfiled; T25's: b19 read t1 then t2
- [x] T26 | RULED Process 90: a human-review query rides with the set and is asked last; the other shapes abstain | 7e2c6b4 | Decide
      what a query at a place other roles are contesting records, since it takes
      no part in the fold. Verify: it is on the master proof
        > 2026-09-04 game hand 1: b19 read turn 1 after t1 and turn 2 after t2
        > 2026-09-04 the note above is T25's, misfiled; module's query at b74 vanished
        > 2026-09-04 hand 4: a lone query against cleans is in no output at all
- [x] T27 | FINISHED -- parse_answers pairs to the sent slot by address; a stripped slot parses, a stray address is refused; test_turn.py | 2c04181 | Update
      run_turn to pair an answer with the sent slot by address, not by an echoed
      question key. Verify: a slot returned without it parses
        > 2026-09-04 game hand 1: function's t2 answer refused for a dropped key
- [x] T28 | RULED Process 88: agreement is the text alone | 7e2c6b4 | Decide
      whether byte-identical change texts agree when the instructions or quoted
      sentences differ. Verify: the ruling is on the log
        > 2026-09-04 game hand 2: 3 roles, one text, patch/correct/patch -- never agreed
- [x] T29 | RULED Process 89: a lone owing mark goes back to every role that marked anything but a query | 7e2c6b4 | Decide
      whether a lone owing mark against cleans is a stet at turn 0 or goes back
      to the other roles as a re-read. Verify: ruling on the log
        > 2026-09-04 hand 3: module's patch at b93 landed at t0, cleans unread
- [x] T30 | RULED Process 88: it takes every owing mark; unanimity stays | 7e2c6b4 | Decide
      whether a place agrees when every owing mark is byte-identical or when a
      majority is, the rest holding. Verify: ruling on the log
        > 2026-09-04 hand 3: two of three held one text; the third held; no stet
- [x] T31 | FINISHED -- a null mark only for ORIGINAL, a recast's side is CHIEF, a side outside known roles refused; test_determined.py | 6ef4db8 | Update
      Determined.deserialize to refuse a null mark unless side is ORIGINAL, and
      an unknown side. Verify: both refused by name
        > 2026-09-04 game hand 4: function-context's query on the class docstring
- [x] T32 | FINISHED -- _identical compares change alone; _outcome escalates one text before the sentence test; test_collate.py | 388952c | Update
      the fold so byte-identical change texts agree whatever the instruction or
      sentence quoted. Verify: patch + correct, one text -> stet
        > 2026-09-04 Process 88; hand 2: one text as patch/correct/patch, never agreed
- [x] T33 | FINISHED -- a lone mark is a re-read to every role that marked but a query, carrying its text; stands when the author is alone | 45d3e61 | Update
      the fold so a lone owing mark is a re-read to every role that marked the
      place but a query. Verify: one mark, three cleans -> re-read
        > 2026-09-04 Process 89; hand 3: b93 landed at t0 with three cleans unread
- [x] T34 | FINISHED -- a human-review query holds its place as Collated.unsettlable, on the master proof, refused at the cap; the other shapes take the role out of the place | 99c7620 | Implement
      the human-review query riding on the master proof, unsettlable and asked
      last; other shapes abstain. Verify: it is on the proof
        > 2026-09-04 Process 90; hands 1 and 4: queries vanished from the record
- [x] T35 | FINISHED -- run_turn keeps every earlier Determined, turn included; a stet place leaves later batches; test_turn.py TestOnceStetAlwaysStet | aefefdd | Update
      the recollate so a place once stet leaves every later batch and keeps its
      turn. Verify: stet at turn 1 reads turn 1 after turn 2
        > 2026-09-04 Process 91; T25's turn stamp folded in
