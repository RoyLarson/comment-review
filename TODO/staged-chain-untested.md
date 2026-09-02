# The staged chain runs but nothing tests it, and the fan-out topology fits one tree

```
Status:   open
Progress: 0 of 4 tasks closed
Owner:    backend
Requires-Roy: true
Raised:   2026-08-30 (2026-08-30, driving distribute and collate across real stages for
          the first time, on Roy's instruction to get through the full step with a setup
          that actually has the stages)
```

## Objective

The staged chain runs but nothing tests it, and the fan-out topology fits one tree.

## Tasks

- [ ] T1 | Make the fan-out fixture runnable against any tree. Verify:
      `4a-then-4c.toml` drives a scratch tree of four files without refusing.
      MEASURED 2026-08-30: it raises `UncoveredPage: block-context: no dispatch
      covers` because its globs name `src/comment_review/reading/*.py` and
      `src/comment_review/binder/*.py` -- this repo's own layout. ! THE REFUSAL
      IS CORRECT; fan-out must cover every page. What is wrong is that the only
      committed fan-out topology can be exercised on exactly one tree.
- [?] T2 | Decide whether `topology --verify` refuses a glob that matches no
      page, or only a page no dispatch covers. Verify: the answer is in
      `docs/decision-log.md`, and `topology --verify` implements it.
        > 2026-09-02 REWORDED: the old Verify named two branches that Process 55
        > 2026-09-02 rules out -- topology.read has no tree so it cannot know, and fan
        > 2026-09-02 blaming the tree is the symptom 55 diagnoses, not the fix
        > 2026-09-02 55 settles WHERE the check lives: topology --verify, a command
        > 2026-09-02 with a repo. What it does not settle is whether a REDUNDANT glob
        > 2026-09-02 is illegal -- a topology can hold one and still cover every page
        > 2026-09-02 and those are different conditions. That remainder is this box
- [ ] T3 | Cover the staged chain with a test that survives. Verify: a test
      drives `sequential.toml` over a real tree through distribute, collate,
      docket and pull for every stage, and asserts the edits ACCUMULATE.
      MEASURED: four stages produce four markers in one paragraph -- one per
      stage, each reading the revise the one before it pulled. Fewer means a
      stage read a tree that did not carry the one before it, and nothing in the
      suite would notice today.
- [ ] T4 | Implement the reader for `Stage.reads`, so a stage seeds from the
      binder its topology names rather than from a path typed by hand
        > 2026-08-31 grep .reads over src/ returns one line: topology.py:140, a WRITE
        > 2026-08-31 topology.py:84-95 refuses a bad value: validated, then unread
