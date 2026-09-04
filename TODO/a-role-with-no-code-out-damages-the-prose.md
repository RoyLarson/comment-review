# A role that finds a code problem has no out, so it damages the prose instead

```
Status:   decision-needed
Progress: 1 of 10 tasks closed
Owner:    agents
Requires-Roy: true
Raised:   2026-08-23 (2026-08-23, Roy: 'we can't tell the agents to review all of this
          and not give them an out for properly resolving the issues. Several times they
          were overly restricted by what they could do and that caused tension in the
          recommendations.')
TRIAGED:  2026-08-23 -- four of five boxes are tasks and all four are LIVE, re-verified
          today. The fifth was the PASS CRITERION -- a judgement, not a checkpoint --
          and is ticked into the Objective. ! Status stays `decision-needed`: the `*`
          ruling gates this file AND `code-concerns-cannot-carry-a-proposed-change`,
          which records the same block in its own `Status:` line.
SPLIT:    2026-08-23 -- one action per box. The box naming `code_concerns` in three
          reviewer files became three, one per file, on this repo's rule that per-file
          work is its own task. Five boxes became seven. A second pass split the ruling
          from recording it in the backend file it gates, and the module-context trigger
          box into its three triggers -- seven became ten.
Updated:  2026-08-28 — THE DOUBLE-BIND, STATED BY ROY 2026-08-28, AND A CANDIDATE ANSWER
          UNDER CONSIDERATION. NOT A RULING. Verbatim: "The comment-review promises no
          code changes in its run. The code concerns are valid changes that should
          happen to the code at the same time the comments are updated to maximize the
          effectiveness of the program. Identifying and moving code is a long
          refactoring process that this review doesn't have the ability to execute
          safely. So we can give the agents an out for adding code concerns to the
          markers container but that doesn't stop the reduced comment-review output
          because the comments have to reflect now. The best possible answer might be to
          put TODO statements in the appropriate interval/margin prose. If accepted by a
          human." THE THIRD STEP IS WHAT MAKES IT A BIND RATHER THAN A TRADE-OFF. A
          container for code concerns does not rescue the prose, BECAUSE THE COMMENT
          MUST BE TRUE OF THE CODE AS IT STANDS TODAY. Filing a concern elsewhere leaves
          the role still obliged to describe code it believes is wrong, so the output is
          still reduced -- which is what this file's title says. OBSERVATIONS ON THE
          CANDIDATE, MINE AND NOT ROY'S. (a) A TODO WRITTEN INTO AN INTERVAL OR MARGIN
          GETS AN ADDRESS FROM THE CENSUS, which dissolves T7 of `code-concerns-cannot-
          carry-a-proposed-change` rather than answering it: that file's objection is
          that "a code concern has no address, so it cannot be re-run against a later
          tree, deduplicated when two roles raise it, or checked for staleness". As
          prose at a place it gets all three for free. (b) IT NEEDS NO EIGHTH
          INSTRUCTION -- prose that is not there yet is an `add`, so it flows through
          the seven. Roy, 2026-08-26: "the word list we used was the words required else
          they start inventing words." (c) THE HUMAN GATE ALREADY EXISTS: stage 7a
          presents and stops, so "if accepted by a human" needs no new mechanism. (d) IT
          IS SELF-HEALING, and this system already owns the check: once the code is
          fixed the TODO becomes a false claim about the code, which is an obituary --
          exactly what `block-context` is for. A report line has no such property. (e)
          AND IT MAY DELETE THE BACKEND TODO RATHER THAN COMPLETE IT. If a concern is a
          mark at a place, the sheet needs no `code_concerns` field, `T1.6` of the 0.2.4
          plan has nothing to add, and the machinery half of the two-lane sequence has
          no subject. TENSIONS WORTH WEIGHING BEFORE RULING. (i) THE CAP. Stage 6
          COMPACT cuts to a published cap, and a TODO spends budget that true-
          description prose needs; `docs/limitations.md` is budget-constrained by rule.
          (ii) A TODO IS A CLAIM ABOUT THE FUTURE, and this repo's standard is that a
          sentence must be falsifiable by reading the code or re-running a command.
          "This should be split" is not checkable the way a count or a bound is --
          though "the condition that prompted it still holds" IS, which is more than a
          report line offers. (iii) DOUBLE-COUNTING: if a TODO lands in the margin AND a
          concern is reported, one finding exists in two places and they can drift. The
          likely resolution is that the margin TODO is the durable artifact and any
          report line is the run's summary of it, but that is a decision and not an
          inference.
Updated:  2026-08-28 — SECOND INSTANCE OF THE SAME BIND, 2026-08-28, and it is recorded
          in full on `a-scope-declaration-costs-as-much-as-a-finding`. Roy: a `module-
          context` handed a paragraph outside its remit could and often SHOULD return
          `move a.py@b3 to b.py@b10` -- "this whole block indicates that this piece of
          functionality should be in a different module because that is where it fits"
          -- and the blocker is the same one this file names: "that also requires moving
          code which we don't do because it is unsafe." ! THE MARK IS EXPRESSIBLE AND
          THE AFTERMATH IS NOT. A cross-file `move` destination is legal, so the mark
          reaches a docket; executing only its prose half lands a comment in `b.py`
          describing code that is still in `a.py`, which MANUFACTURES the defect `block-
          context` exists to catch. ! So the damage this file names has a second form:
          not only bending a sentence to fit code the role cannot change, but ABANDONING
          A CORRECT STRUCTURAL OBSERVATION because acting on it is unsafe -- the role
          files `outside-my-role` where a real finding was available. ! The TODO-in-the-
          margin candidate reaches both: an `add` at `a.py@b3` saying the subject
          belongs in `b.py` is addressable, human-gated at 7a, and becomes an obituary
          once the code moves. ONE MECHANISM, TWO BINDS.
```

## Objective

`code_concerns` is defined in the shared brief every role reads, and named in only ONE of
the four reviewer files -- `function-context`. It is absent from `module-context`, whose whole
remit is whether a module announces ONE subject, which is the finding that most needs a code
out.

!! **RE-MEASURED 2026-08-23, and every part still holds.** `grep -rn code_concerns
plugins/comment-review/` answers with `reviewer-brief.md:251` and `:255`, the two `held.py`
sites that read the field, `record.py:883` which seeds it empty, and
`comment-review-function-context.md:32` and `:75` -- **and nothing else**. The other three
reviewer files do not contain the string.

!! **MEASURED IN THE HARNESS.** `module-context-widens-a-two-subject-docstring` -- the first
record in `evals/test-cases.jsonl`, `"outcome": "miss"` -- detected that `verdicts.py` holds
four subjects, had no verdict for *split this module*, and emitted a prose `patch` widening the
docstring to announce TWO -- the exact defect its own trigger is named for. `code_concerns` came
back empty. Roy, 2026-08-23: *"we can't tell the agents to review all of this and not give them
an out for properly resolving the issues. Several times they were overly restricted by what they
could do and that caused tension in the recommendations."*

! **AND THE CAUSE THE CASE NAMES IS STILL IN THE FILE.**
`comment-review-module-context.md:25-29` heads a section *"The finding is a module announcing
more than one subject"* and lists three triggers, the third being *"a summary line that
describes one half of what the file contains"*. The section names no verdict, so the role
reached for the only one it had.

! **What T1 decides.** Today a role can only DESCRIBE the problem in `code_concerns`; Roy's
vision is that a code change is SUGGESTED. That is a scope decision, not a wording fix, and it
decides the shape the backend half has to carry.

## !! THIS LANDS SECOND, AND IT IS THE MEASUREMENT

Roy, 2026-08-23: *"it has to be landed in the code, tested that the effectiveness didn't
change, and then change the agents to tell them they can use it. Verify that it improved the
recommendations."*

**This half is the TREATMENT.**
[`code-concerns-cannot-carry-a-proposed-change`](code-concerns-cannot-carry-a-proposed-change.md)
(`backend`) lands first and is proven to change nothing; only then is a role told the channel
exists. Any movement in the recommendations after this change is attributable to the
INSTRUCTION, because the shape was already in place and already shown inert.

! **SHIPPING BOTH AT ONCE DESTROYS THE ATTRIBUTION**, which is why they are two files and not
one. It is a measurement rule, not a filing convention: with one step there is no baseline and
the question *did telling the roles help* cannot be answered at all.

! **AND THE RULING COMES BEFORE EITHER.** What a role may PROPOSE when the right fix is a code
change decides the shape the backend has to carry, so `T1` below gates both files rather than
only this one.

## ! The pass criterion, which is not a checkpoint

**RECOMMENDATIONS IMPROVED, measured against the baseline the backend half established.** Not
*"the field is populated"* -- that is activity. The comparison is whether a role still bends
prose to fit a code problem.

! It carried a box until 2026-08-23 and is not a task: ticking it is a JUDGEMENT about a body of
recommendations, not an observation a stranger can repeat. The harness case is its checkable form
-- it is a `miss` today and either flips or does not. ! And the comparison it asks for cannot be
run yet for a second reason:
[`the-harness-cannot-run-the-system-it-grades`](the-harness-cannot-run-the-system-it-grades.md)
is open, so *"effectiveness unchanged"* has no grader.

## Tasks

- [?] T1 | T1 -- * RULE what a role may propose when the right fix is a CODE
      change -- describe it, or suggest it. Verify: the ruling is recorded in
      the Objective here.
- [ ] T2 | T2 -- Record T1's ruling in
      `code-concerns-cannot-carry-a-proposed-change.md`, the backend file it
      gates. Verify: that file states it.
- [ ] T3 | T3 -- Name `code_concerns` in `comment-review-ownership-context.md`.
      Verify: `grep -l code_concerns plugins/comment-review/agents/*.md` lists
      that file.
- [ ] T4 | T4 -- Name `code_concerns` in `comment-review-block-context.md`.
      Verify: `grep -l code_concerns plugins/comment-review/agents/*.md` lists
      that file.
- [ ] T5 | T5 -- Name `code_concerns` in `comment-review-module-context.md`.
      Verify: the same grep lists four files in total; today it lists one.
- [ ] T6 | T6 -- Say what verdict a docstring enumerating unrelated
      responsibilities earns (`comment-review-module-context.md:27`). Verify:
      that trigger names its verdict.
- [ ] T7 | T7 -- Say what verdict section banners reading as chapter breaks earn
      (`comment-review-module-context.md:28`). Verify: that trigger names its
      verdict.
- [ ] T8 | T8 -- Say what verdict a summary line describing one half of the file
      earns (`comment-review-module-context.md:29`). Verify: that trigger names
      its verdict.
- [ ] T9 | T9 -- Re-run the harness case
      `module-context-widens-a-two-subject-docstring`. Verify:
      `evals/test-cases.jsonl` records an outcome for it other than `miss`.
- [x] T10 | FINISHED | unknown | T10 -- NOT A TASK. The PASS CRITERION --
      *"recommendations improved"* -- is a judgement, not an observation a
      stranger can repeat. Kept in full in the Objective.
