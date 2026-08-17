# A role can reverse itself between runs, and nothing measures it

```
Status:   open
Progress: 0 of 6 tasks done
Owner:    session * Roy (* 1 ruling)
Raised:   2026-08-17 (two runs of the same skill over the same repo at the same ref;
          one role returned opposite verdicts on the same block)
```

## Objective

**The same editorial role, given the same census, returned opposite verdicts on the same block
across two runs.** Observed on `todo_tool`, r1 against r2:

| block | r1 | r2 |
| --- | --- | --- |
| the *"Six call sites"* claim | `module-context` **cleared** it | `module-context` **corrected** it -- four functions, and both test modules read the groups |
| `_OWNER_SPLIT`'s *"five real fields"* | `module-context` **corrected** it -- *"actually three"* | `module-context` **`query` -- outside the code**, on the grounds that the fix erased the state that would settle it |

!! **The second row RESOLVED, 2026-08-17, and both runs were right about different things.**
The operator settled it from `git` rather than from the checkout: of the five fields, three used
the separators the code parses and two used an em dash and a `!` continuation it cannot see. So
r1's *"five is three"* was correct, and r2 was correct that **the checkout alone could not prove
it** -- the state that would settle it had been erased by the very fix under review.

! That downgrades this row from a contradiction to a scope difference, and it sharpens the
question rather than retiring it: a role that can settle a claim only from history, not from the
tree, has no verdict for that. `query -- outside the checkout` is the nearest, and it says
"generated, gitignored, remote" -- not "the checkout no longer holds what would settle this,
because this change removed it". ! The first row is unresolved and remains the evidence. A `correct` that reads confident and a
`query` that says nobody can tell are not adjacent verdicts.

!! **This is not the disagreement the system is built for.** Two ROLES disagreeing is designed
in -- remits overlap, the join prints it, and the re-review resolves it. Two runs of ONE role
disagreeing is different: it means the verdict is a sample, and nothing anywhere states its
variance.

**What rests on that, in this repo's own words:**

- each role's `clean` *"asserts something specific"* -- but an assertion that flips between runs
  asserts less than the wording claims
- a `correct` must carry *"the line that settles it"* -- and r1's did, and r2 says the claim was
  not settleable
- the whole grading rule is *"grade a run from its DIFF, never from its own report"*, because
  self-reported confidence was measured not to discriminate real findings from fabricated ones.
  ! **Run-to-run reversal is the same defect one level up**, and the same remedy is not
  available: there is no diff to grade a `clean` against.

! `evals/grade_hazards.py` grades ONE run against twelve planted hazards. Nothing in
`evals/` measures the same run twice.

## !! Every measurement here was made by an operator who KNEW it was a test

Roy, 2026-08-17, watching a session report a gate refusal instead of routing around it:
*"it knows that this is testing the comment-review skill and is acting appropriately."*

That is the right behaviour and it is also a confound on the whole evidence base. Refusing to
reword evidence to satisfy a parser is cheap when the refusal IS the result being sought. For a
session that only wants its comments reviewed, the gate is what stands between it and finishing,
and the cheapest route past 22 `EVIDENCE` refusals is to edit the reports.

! That produces exit 0 and a laundered review, and nothing downstream separates it from a real
one -- the same asymmetry this repo already records about a fabricated `clean`. **What is
measured today is the system operated in GOOD FAITH**, and no run has been observed under the
other condition.

## ! What is NOT established

- **Which answer was right.** Neither run's `Six call sites` verdict has been checked here.
- **Whether the input was truly identical.** Both runs are the same repo at the same ref, but
  the second ran against a CHANGED skill -- the interval exemption, the query-shape requirement
  and the withheld packet section all landed between them. A role told different things may
  reasonably answer differently, and that is a competing explanation this file must not skip.
- **The rate.** Two reversals in one pair of runs is an anecdote, not a variance.

## Tasks

- [ ] Establish the rate before designing anything. Run one role twice over an UNCHANGED skill
      and an unchanged census, and diff the verdicts per block. ! Two runs give a number with no
      error bar; decide how many are worth paying for before starting, and state the cost.

- [ ] Separate the two explanations. Re-run r1's exact skill version against the same census and
      see whether the reversal reproduces. If it does not, the cause is the skill change and
      this file is about CHANGE SENSITIVITY, which is a different and more tractable problem.

- [ ] * Rule on what a measured reversal rate would OBLIGE. Candidates: nothing, and it is
      recorded as a known bound; a rule that a `clean` from one role never certifies alone; or
      the join reporting agreement across roles as a confidence signal it currently computes
      and discards. ! Roy's, because it decides whether a verdict is a claim or a vote.

- [ ] Decide whether a `correct` reversing to `query` is WORSE than the reverse. Going from
      "here is the true clause" to "nobody can settle this" retracts something already relayed;
      going the other way adds. The verdict table treats them as peers.

- [ ] Say in `docs/limitations.md` that verdict stability across runs is UNMEASURED. ! It is
      the honest state today and the file already exists to hold exactly this kind of statement.

- [ ] ! Do NOT add a "confidence" field to the record in response to this.
      `the-finding-record-is-eight-fields-and-six-would-do` is open for the opposite reason, and
      self-reported confidence is the thing this repo has already measured as worthless.
