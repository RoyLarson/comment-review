# A role can reverse itself between runs, and nothing measures it

```
Status:   open
Progress: 1 of 6 tasks done
Owner:    agents
Requires-Roy: true
Raised:   2026-08-17 (two runs of the same skill over the same repo at the same ref;
          one role returned opposite verdicts on the same block)
TRIAGED:  2026-08-23 — five of six boxes are tasks; the sixth was a standing
          prohibition and is ticked into the Objective below. ! One Objective claim no
          longer holds: `evals/grade_hazards.py` IS ABSENT -- `evals/` holds
          `generator_split.py` and `test-cases.jsonl`, and `CLAUDE.md:105` states there
          is no end-to-end grade.
          !! IT WAS REMOVED ON 2026-08-23, NOT ABSENT ALL ALONG. `git log --all` is
          empty for that path because this repo's history was REWRITTEN that day; the
          grader was tied to a corpus this repo cannot ship. ! An empty `git log --all`
          after a history rewrite proves nothing about whether a file existed -- it is
          the one measurement a purge silently inverts, and the inference it invites is
          the strongest available evidence pointing the wrong way.
SPLIT:    2026-08-23 -- the boxes were cut to two lines each and every open one now
          carries a Verify clause. The reasoning they held is in the Objective; the
          task count is unchanged at six
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
because this change removed it". ! The first row is unresolved and remains the evidence. A
`correct` that reads confident and a `query` that says nobody can tell are not adjacent verdicts.

!! **This is not the disagreement the system is built for.** Two ROLES disagreeing is designed
in -- remits overlap, the collator prints it, and the re-review resolves it. Two runs of ONE role
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

! **NOTHING IN `evals/` MEASURES ANYTHING TWICE, and there is no grader here at all.**
MEASURED 2026-08-23: `evals/` holds `generator_split.py` and `test-cases.jsonl`, and the
JSONL holds SIX cases -- one role and one outcome each, five `hit` and one `miss`. ! An earlier
version of this file cited `evals/grade_hazards.py` as grading one run against twelve planted
hazards. **That file was REMOVED from this repo and from its history on 2026-08-23**, with the
corpus it graded against; `CLAUDE.md:105` records that there is now no end-to-end grade. The
point the sentence was making survives -- nothing here measures the same run twice -- but it
now rests on a file that exists.

!! **AND `git log --all` CANNOT ANSWER "DID THIS EVER EXIST" IN THIS REPO.** The history was
rewritten on 2026-08-23, so an empty log is what a purged path looks like AND what a path that
never existed looks like -- **the same result for opposite facts.** A triage agent hit exactly
this on the day and concluded the grader *"never has been"* here. ! It is [`gates.md`](../docs/gates.md)'s
rule in its sharpest form: the check ran, came back clean, and was answering a question nobody
had asked it. **Date anything measured from history against the rewrite before believing it.**

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

## ! A "confidence" field is not the answer, and that is settled

**Do NOT add a `confidence` field to the record in response to this.**
[`the-finding-record-is-eight-fields-and-six-would-do`](completed/the-finding-record-is-eight-fields-and-six-would-do.md)
cut the record from eight fields to six for the opposite reason -- every field added since the
import served the GATE and not the reviewer -- and self-reported confidence is the thing this
repo has already measured as worthless. ! That file is DONE; the argument it made is why this
stays a `do NOT`. It carried a box until 2026-08-23 and there is no state in which anyone ticks
it, so it is recorded here instead.

## ! What the boxes carried

! **T1 -- establish the rate before designing anything.** Two runs give a number with no error
bar; decide how many are worth paying for before starting, and state the cost.

! **T2 -- separate the two explanations.** If the reversal does not reproduce against r1's exact
skill version, the cause is the skill change and this file is about CHANGE SENSITIVITY, which is
a different and more tractable problem.

! **T3 -- what a measured reversal rate would OBLIGE.** Candidates: nothing, and it is recorded
as a known bound; a rule that a `clean` from one role never certifies alone; or the collator
reporting agreement across roles as a confidence signal it currently computes and discards.
! Roy's, because it decides whether a verdict is a claim or a vote.

! **T4 -- whether a `correct` reversing to `query` is WORSE than the reverse.** Going from
"here is the true clause" to "nobody can settle this" retracts something already relayed; going
the other way adds.

! **T5.** MEASURED 2026-08-23: `docs/limitations.md`'s two sections are *Notes for Changes* and
*A RULE PAYS FOR ITS OWN LINES* -- it is about what a rule costs, not a list of what is
unmeasured, so whoever writes the sentence is opening a third section rather than adding to a
list. `grep -n "stability" docs/limitations.md` returns nothing today.

## Tasks

- [ ] T1 -- Run one role twice over an unchanged skill and census, and diff the verdicts
      per block. Verify: a per-block diff recorded, with reversals counted over blocks.
- [ ] T2 -- Re-run r1's exact skill version against the same census to see whether the
      reversal reproduces. Verify: both `module-context` verdicts recorded side by side.
- [ ] T3 -- * Rule what a measured reversal rate would OBLIGE: nothing, a bar on a lone
      `clean`, or agreement across roles. Verify: `docs/decision-log.md` records it.
- [ ] T4 -- * Rule whether a `correct` reversing to `query` is WORSE than the reverse. The
      verdict table treats them as peers. Verify: `docs/decision-log.md` records it.
- [ ] T5 -- Say in `docs/limitations.md` that verdict stability across runs is UNMEASURED.
      Verify: `grep -n "stability" docs/limitations.md` returns a line.
- [x] T6 -- NOT A TASK. The standing prohibition on adding a `confidence` field is kept in
      the Objective, under *A "confidence" field is not the answer*.
