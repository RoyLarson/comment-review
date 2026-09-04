# A role can be asked to revise and has nothing to answer ON

```
Status:   open
Progress: 7 of 19 tasks closed
Owner:    backend
Requires-Roy: true
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

- [x] T1 | FINISHED | unknown | T1 -- The four answers as a closed set, derived
      from `rules_on_text` plus the two that are not marks. Verify: it cannot
      drift from `INSTRUCTIONS`, and a fifth answer is refused.
- [x] T2 | FINISHED | unknown | T2 -- A revise sheet, seeded per conflict,
      carrying the rendered diff. Verify: every row names the conflict it
      answers, and a row left unanswered is neither held nor withdrawn.
- [x] T3 | FINISHED | unknown | T3 -- The four outcomes. Verify: any new mark
      relitigates; two holds escalate; hold plus withdraw takes the held claim
      in; two withdraws pick one and re-ask.
- [ ] T4 | T4 -- Route a `query` by shape. Verify: `human-review-necessary`
      never returns to a role, and `unable-to-determine` carries the question
      into the next ask.
- [-] T5 | SUPERSEDED as filed in error -- Process #78. Roy: a random requirement a session added and was never asked for | eb49e56 | T5
      -- Count queries first raised at revise. Verify: the run reports the
      number, and it is zero on a set of marks where every query was raised in
      round one.
- [x] T6 | FINISHED | unknown | T6 -- A revise sheet is addressed to a ROLE, not
      to a stage, and carries only the rows that role is party to. Verify: a
      role party to one place in a stage it did not otherwise join receives a
      one-row sheet, and no row names a place it is not party to.
- [-] T7 | SUPERSEDED into a-role-can-reverse-itself-between-runs T3 -- it is agent-output variance across two runs, not a claim about the process, so it is agents' and not a code gate | f196ef9 | T7
      -- A reversal is a row, paired with whoever LAST set the statement.
      Verify: stage 3 reversing a paragraph stage 2 set pairs with stage 2 and
      not with stage 1, read from the revise's per-place provenance.
- [-] T8 | SUPERSEDED by Process #78 -- the round bound is what the task agent is told, not what the code enforces, and the Process 9 citation resolved nowhere | eb49e56 | T8
      -- Enforce the two-round cap `Process: #9` already ruled. Verify: a third
      round cannot start, the place reaches the copy chief carrying every
      round's marks, and the run reports the rounds each place took.
- [?] T9 | Decide what records HOW the copy chief ruled, since an edit_copy
      cannot. Verify: the artifact exists, or the question is answered in the
      log
        > 2026-09-02 Roy 2026-09-02: that needs something besides the edit-copy
- [ ] T10 | Implement the DiffMark a role answers a disagreement on, four
      answers closed. Verify: a fifth, or any of Mark's seven, is refused by
      name
        > 2026-09-03 prototype at desk/diff_mark.py, 5574f0a -- P20; replaces T1
- [ ] T11 | Implement the batch: one payload per role per round, each slot
      carrying its diff3. Verify: one send per role whatever the place count
        > 2026-09-03 prototype batch_of 9406b3b -- P21; the FLOW attaches diff3
        > 2026-09-03 replaces T2 and T6
- [ ] T12 | Implement the return: a role's answered batch parses at the
      boundary. Verify: an unanswered slot is refused by name, never read as
      withdraw
        > 2026-09-03 prototype parse_batch 37fbbb8 -- P16
- [ ] T13 | Implement the recollate so a round's resolutions join the chief's
      copy. Verify: a lone surviving add, all others holding, lands
        > 2026-09-03 P17. Measured hand 3: a lone add re-reads forever today
- [?] T14 | Decide whether a composition re-read is answered with a DiffMark or
      a fresh Mark, given clean and query are its only passes
        > 2026-09-03 P1/P6. the-revise.md: clean and query are a composition's passes
        > 2026-09-03 the prototype takes no side -- desk/diff_mark.py docstring
- [ ] T15 | Implement the conflict outcomes: hold/hold next round, hold/withdraw
      takes the held in, withdraw/withdraw re-asks. Verify: each lands
        > 2026-09-03 P5; replaces T3's conflict half -- the Objective's outcomes table
- [ ] T16 | Implement the round counter, rounds named by kind, no maximum
      enforced. Verify: a run reports each place's rounds
        > 2026-09-03 P18. Process 78: the cap is the agent's, never the code's
- [ ] T17 | Implement the copy chief's ruling at the cap on whatever is still
      unresolved. Verify: no place survives the last round unruled
        > 2026-09-03 P19. the-revise.md: the chief's ruling is the terminator
- [ ] T18 | Implement routing of a refused or unanswered DiffMark to its role as
      a revisit. Verify: it appears in revisit naming role and address
        > 2026-09-03 Roy 2026-09-03: unanswered or malformed is refused, not a withdraw
- [ ] T19 | Generate the DiffMark contract a role is handed from the code, as
      allowed() does for Mark. Verify: no agent file hand-types its fields
        > 2026-09-03 the game's brief hand-typed the contract and got query wrong
        > 2026-09-03 publishing it in the brief is agents lane; the generator is backend
