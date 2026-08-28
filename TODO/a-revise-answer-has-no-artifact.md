# A role can be asked to revise and has nothing to answer ON

```
Status:   open
Progress: 0 of 8 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-28, filing the work `decision-log.md Process: #21` and `#22` created.
          Both were ruled the same day and neither had a backlog entry, so the plan
          steps that build them cited rulings rather than tasks.
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

- [ ] T1 -- The four answers as a closed set, derived from `rules_on_text` plus the two that are
      not marks. Verify: it cannot drift from `INSTRUCTIONS`, and a fifth answer is refused.
- [ ] T2 -- A revise sheet, seeded per conflict, carrying the rendered diff. Verify: every row
      names the conflict it answers, and a row left unanswered is neither held nor withdrawn.
- [ ] T3 -- The four outcomes. Verify: any new mark relitigates; two holds escalate; hold plus
      withdraw takes the held claim in; two withdraws pick one and re-ask.
- [ ] T4 -- Route a `query` by shape. Verify: `human-review-necessary` never returns to a role,
      and `unable-to-determine` carries the question into the next ask.
- [ ] T5 -- Count queries first raised at revise. Verify: the run reports the number, and it is
      zero on a set of marks where every query was raised in round one.
- [ ] T6 -- A revise sheet is addressed to a ROLE, not to a stage, and carries only the rows that
      role is party to. Verify: a role party to one place in a stage it did not otherwise join
      receives a one-row sheet, and no row names a place it is not party to.
- [ ] T7 -- A reversal is a row, paired with whoever LAST set the statement. Verify: stage 3
      reversing a paragraph stage 2 set pairs with stage 2 and not with stage 1, read from the
      revise's per-place provenance.
- [ ] T8 -- Enforce the two-round cap `Process: #9` already ruled. Verify: a third round cannot
      start, the place reaches the copy chief carrying every round's marks, and the run reports
      the rounds each place took.
