# What the first live freeform run showed

```
Status:   open
Progress: 4 of 17 tasks closed
Owner:    agents
Requires-Roy: false
Raised:   2026-11-02 (freeform plan Task 4 live run and stage walk, 2026-11-02)
```

## Objective

What the first live freeform run showed.

## Tasks

- [ ] T1 | Collapse one concern raised by several roles before asking the author
      (reviewer-brief.md:320-327, SKILL.md:287); three roles cost three resumes
        > 2026-11-02 Ruled #269: chief composes; backend change after merge
- [ ] T2 | Stop pasting 613 lines into every role prompt (SKILL.md:206-217);
      four reviewers read about 600 lines for 90 lines of code
        > 2026-11-02 Ruled by decision-log #266; wording still needs Roy's approval
        > 2026-11-02 Extended by #270: the edited copy is the finding
- [ ] T3 | Limit stage 5 step 3 to human-review-necessary queries, and state the
      fate of outside-my-role queries on pages (SKILL.md:344, 272, 488)
- [x] T4 | A stop holds the run at its stage; SKILL.md says so, #267 | ca1c53bce0246b727b0beade267b54acc0a8e81c | Say
      how a run resumes after stage 7a stops; a formatter fix moves the pre-edit
      ref (SKILL.md:429-431, 411)
- [-] T5 | SUPERSEDED by #268: the audit stays a reading | ca1c53bce0246b727b0beade267b54acc0a8e81c | Mechanise
      the freeform audit; hunks were matched to findings by eye, and check has
      no freeform mode (SKILL.md:429)
- [ ] T6 | State that an empty stage 6 skips the condenser (SKILL.md:358,
      381-388)
- [ ] T7 | Give stage 8 and stage 6 the vocabulary their role files claim
      (SKILL.md:464-466, 384-386)
- [-] T8 | SUPERSEDED by #268: the author owns their edit | ca1c53bce0246b727b0beade267b54acc0a8e81c | Decide
      what checks an author edit that changes code; it skips formatter and
      audit, and prove_unchanged answers UNCHECKED (write.md:29-30)
- [ ] T9 | Let a reviewer read its own draft at exit 5, or stop offering proof
      for that (reviewer-brief.md:59-65)
        > 2026-11-02 Ruled: one line in the brief; preview once queries answered
- [-] T10 | SUPERSEDED: a real run has the tool; only a test subagent lacked it | ca1c53bce0246b727b0beade267b54acc0a8e81c | Name
      a fallback when AskUserQuestion is missing (SKILL.md:146, 273)
- [ ] T11 | Decide who consumes the reviewer's copy, and reconcile the
      later-stage draft with 7a step 1 re-copying (SKILL.md:219, 235-238, 404)
        > 2026-11-02 Ruled #270: the copy is the finding; 7a re-copy still open
        > 2026-11-02 Open: drop 7a setter? #270 before or after merge? See log
        > 2026-11-02 #270 lands before merge (Roy). 7a setter still open.
        > 2026-11-02 Ruled #270: the setter retires; plan the 7a change
- [ ] T12 | Clear stale page-only text: write.md:5,72; SKILL.md:45-46,52-68;
      role files :12 and Return; comment-review-review.md:8,19
- [ ] T13 | Fix current and at for an add and a string line
      (reviewer-brief.md:386-392; freeform.md:24,27)
        > 2026-11-02 Goes away with #270: current leaves the findings
- [ ] T14 | Report the line-endings UNCHECKED beside the freeform one
      (write.md:59-62) and limit stage 5 send-backs (SKILL.md:341-342)
- [ ] T15 | Work the smaller ambiguities listed in the Task 4 report: withdraw
      scope, correct or drop, add at a held place, role value on a composed
      entry, module-less JS, review.md template departures, NOT CHECKED noise
- [ ] T16 | Exercise what Task 4 left out: stage 6 on real over-cap text, turns,
      partial acceptance, no formatter, a failing check
- [ ] T17 | Plant an audit stop and a failing check in the T16 runs
