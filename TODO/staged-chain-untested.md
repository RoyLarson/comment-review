# The staged chain runs but nothing tests it, and the fan-out topology fits one tree

```
Status:   open
Progress: 3 of 6 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-30 (2026-08-30, driving distribute and collate across real stages for
          the first time, on Roy's instruction to get through the full step with a setup
          that actually has the stages)
```

## Objective

The staged chain runs but nothing tests it, and the fan-out topology fits one tree.

## Tasks

- [x] T1 | FINISHED; topology --build writes the fixture's shape for any tree, and the test drives one | 5a99fea8 | Make
      the fan-out fixture runnable against any tree. Verify: `4a-then-4c.toml`
      drives a scratch tree of four files without refusing. MEASURED 2026-08-30:
      it raises `UncoveredPage: block-context: no dispatch covers` because its
      globs name `src/comment_review/reading/*.py` and
      `src/comment_review/binder/*.py` -- this repo's own layout. ! THE REFUSAL
      IS CORRECT; fan-out must cover every page. What is wrong is that the only
      committed fan-out topology can be exercised on exactly one tree.
- [x] T2 | RULED 2026-09-06, decision-log.md Process: #100 -- verify refuses only a page no dispatch covers, or one two shards claim; an empty glob is not a fault | 45742705 | Decide
      whether `topology --verify` refuses a glob matching no page, or only a
      page no dispatch covers. Verify: the answer is in the log.
        > 2026-09-02 REWORDED: the old Verify named two branches that Process 55
        > 2026-09-02 rules out -- topology.read has no tree so it cannot know, and fan
        > 2026-09-02 blaming the tree is the symptom 55 diagnoses, not the fix
        > 2026-09-02 55 settles WHERE the check lives: topology --verify, a command
        > 2026-09-02 with a repo. What it does not settle is whether a REDUNDANT glob
        > 2026-09-02 is illegal -- a topology can hold one and still cover every page
        > 2026-09-02 and those are different conditions. That remainder is this box
        > 2026-09-06 Roy: an empty glob does not matter; the agent reads and modifies.
- [ ] T3 | Cover the staged chain with a test that survives. Verify: a test
      drives `sequential.toml` over a real tree through distribute, collate,
      docket and pull for every stage, and asserts the edits ACCUMULATE.
      MEASURED: four stages produce four markers in one paragraph -- one per
      stage, each reading the revise the one before it pulled. Fewer means a
      stage read a tree that did not carry the one before it, and nothing in the
      suite would notice today.
- [x] T4 | desk/topology.py seeded_from_problem reads Stage.reads; distribute --revise; tests/test_topology.py, test_distribute_command.py | 5e08440f | Implement
      the reader for `Stage.reads`, so a stage seeds from the binder its
      topology names rather than from a path typed by hand
        > 2026-08-31 grep .reads over src/ returns one line: topology.py:140, a WRITE
        > 2026-08-31 topology.py:84-95 refuses a bad value: validated, then unread
- [ ] T5 | Update topology --build to deal a role's pages by place count, not
      round-robin by path, so its dispatches hold near-equal places
        > 2026-09-14 self-run: one role's 3 dispatches held 104, 156 and 75 places
        > 2026-09-14 evidence: OneDrive/comment-review-feedback/2026-09-14-self-run
- [ ] T6 | Make composed topology dispatches match literal page paths containing
      glob characters
        > 2026-09-30 Criteria: docs/reviews/2026-09-30-r6-r7-r8.md, 06:3
