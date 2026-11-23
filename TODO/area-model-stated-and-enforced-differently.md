# The area architecture is stated in one model and enforced against another

```
Status:   open
Progress: 0 of 5 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-11-23 (broken review, 2026-11-23)
```

## Objective

From the broken review of comment-review at 6a81c7b0
(feat/0.2.4-what-a-reviewer-is-handed), 2026-11-23. Evidence codes cite the
review's perspective outputs (W workflow, A architecture, D domain, I
implementation, N names, V vocabulary). The solution phase has not run; nothing
below is a recommendation.

Problem 6. The area architecture is stated in one model and enforced against
another [A-F2, A-F4, A-F6, A-F7, I-F9; V25]

- `tests/test_areas.py` treats machine and concordance as leaves and never checks commands or
  machine importers; crossings it cannot see include commands->desk (21), desk->machine,
  results->machine (A-F6). Missing rows filed (commands-reach-past-flows T2, T11); the model
  disagreement is not.
- The middle is split across `desk` and `flows` with no rule: `flows/bus.py` holds chief-ruling,
  admits, dealt-stage and turn-slot policy; `human.py`, `mark_errors.py`, `answers.py` read only
  desk types; `flows` (6,122 lines) exceeds `desk` (4,838) (A-F2). #383/#384 rule the commands
  side and the flow helpers; nothing rules which middle rules belong to `desk`.
- No component owns writing inter-stage files: `proof_io` saves only proof, batch and a mid-fill
  copy; raw `Path` I/O in commands never imports `machine`, so it is invisible to the
  "only a flow reaches the machine" rule (#80, #207) (A-F4).
- `desk` holds non-middle things: topology parser read only by commands, the unexecuted
  `stages` model, the `external_address` sketch, collator file reads, console events (A-F7).
- No shared command skeleton: `__main__` rewrites `sys.argv`, 13 of 15 `main()` read it
  implicitly; root resolution differs per command (I-F9).

## Tasks

- [ ] T1 | Make the area gate enforce the area table docs/conventions.md states
        > 2026-11-23 Symptom: commands-reach-past-flows.md T2
        > 2026-11-23 Symptom: only-a-flow-reaches-the-machine.md T11
- [ ] T2 | Determine which middle rules belong to desk rather than flows
        > 2026-11-23 Related: flow-helpers-placement.md (#384)
- [ ] T3 | Determine which component owns writing inter-stage files
        > 2026-11-23 Related: only-a-flow-reaches-the-machine.md; one-obvious-way.md T38
- [ ] T4 | Determine where the non-middle modules in desk belong
- [ ] T5 | Determine the entry skeleton every command shares
        > 2026-11-23 Related: command-entry-points.md; one-obvious-way.md T14
