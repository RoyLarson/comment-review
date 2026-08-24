# A role that finds a code problem has no out, so it damages the prose instead

```
Status:   decision-needed
Progress: 1 of 5 tasks done
Owner:    agents
Requires-Roy: true
Raised:   2026-08-23 (2026-08-23, Roy: 'we can't tell the agents to review all of this
          and not give them an out for properly resolving the issues. Several times they
          were overly restricted by what they could do and that caused tension in the
          recommendations.')
TRIAGED:  2026-08-23 — four of five boxes are tasks and all four are LIVE, re-verified
          today. The fifth was the PASS CRITERION -- a judgement, not a checkpoint --
          and is ticked into the Objective. ! Status stays `decision-needed`: the `*`
          ruling gates this file AND `code-concerns-cannot-carry-a-proposed-change`,
          which records the same block in its own `Status:` line.
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
recommendations, not an observation a stranger can repeat. `T4` is its checkable form -- the
harness case is a `miss` today and either flips or does not. ! And the comparison it asks for
cannot be run yet for a second reason:
[`the-harness-cannot-run-the-system-it-grades`](the-harness-cannot-run-the-system-it-grades.md)
is open, so *"effectiveness unchanged"* has no grader.

## Tasks

- [ ] T1 -- * RULE what a role may propose when the right fix is a CODE change. Today a
      role can only describe the problem in `code_concerns`; Roy's vision is that
      a code change is SUGGESTED. That is a scope decision, not a wording fix.
- [ ] T2 -- Name `code_concerns` in the three reviewer files that do not mention it --
      `ownership-context`, `block-context`, `module-context` -- so the out exists
      where the finding is made, not only in the shared brief. Verify: `grep -l
      code_concerns plugins/comment-review/agents/*.md` lists four files; today it
      lists one.
- [ ] T3 -- Say what verdict a trigger earns. `comment-review-module-context.md:25-29`
      lists three triggers for *a module announcing more than one subject* and names no
      verdict for any of them, so the role reached for the only one it had. Verify:
      each trigger in that section names the verdict it earns.
- [ ] T4 -- Re-run the harness case `module-context-widens-a-two-subject-docstring` --
      it is `"outcome": "miss"` in `evals/test-cases.jsonl` today and is the pass
      criterion for this TODO.

- [x] T5 -- NOT A TASK. The PASS CRITERION -- *"recommendations improved"* -- is a
      judgement about a body of recommendations, not an observation a stranger can
      repeat, and it has no grader today. Kept in full in the Objective, under
      *The pass criterion, which is not a checkpoint*; `T4` is its checkable form.
