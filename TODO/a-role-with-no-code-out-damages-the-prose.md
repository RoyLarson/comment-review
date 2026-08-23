# A role that finds a code problem has no out, so it damages the prose instead

```
Status:   decision-needed
Progress: 0 of 5 tasks done
Owner:    agents
Requires-Roy: true
Raised:   2026-08-23 (2026-08-23, Roy: 'we can't tell the agents to review all of this
          and not give them an out for properly resolving the issues. Several times they
          were overly restricted by what they could do and that caused tension in the
          recommendations.')
```

## Objective

`code_concerns` is defined in the shared brief every role reads, and named in only ONE of
the four reviewer files -- `function-context`. It is absent from `module-context`, whose whole
remit is whether a module announces ONE subject, which is the finding that most needs a code
out.

!! **MEASURED IN THE HARNESS.** `module-context-widens-a-two-subject-docstring` detected that
`verdicts.py` holds four subjects, had no verdict for *split this module*, and emitted a prose
`patch` widening the docstring to announce TWO -- the exact defect its own trigger is named
for. `code_concerns` came back empty. Roy, 2026-08-23: *"we can't tell the agents to review all
of this and not give them an out for properly resolving the issues. Several times they were
overly restricted by what they could do and that caused tension in the recommendations."*

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
change decides the shape the backend has to carry, so the `*` task below gates both files
rather than only this one.

## Tasks

- [ ] * RULE what a role may propose when the right fix is a CODE change. Today a
      role can only describe the problem in `code_concerns`; Roy's vision is that
      a code change is SUGGESTED. That is a scope decision, not a wording fix.
- [ ] Name `code_concerns` in the three reviewer files that do not mention it --
      `ownership-context`, `block-context`, `module-context` -- so the out exists
      where the finding is made, not only in the shared brief.
- [ ] Say what verdict a trigger earns. The harness evidence names the cause: the
      role file lists the trigger and 'never says what verdict that finding
      earns', so the role reached for the only one it had.
- [ ] Re-run the harness case `module-context-widens-a-two-subject-docstring` --
      it is a MISS today and is the pass criterion for this TODO.
- [ ] !! PASS CRITERION: RECOMMENDATIONS IMPROVED, measured against the baseline
      the backend half established. Not 'the field is populated' -- that is
      activity. The comparison is whether a role still bends prose to fit a code
      problem.
