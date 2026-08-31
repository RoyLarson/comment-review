# The staged chain runs but nothing tests it, and the fan-out topology fits one tree

```
Status:   open
Progress: 0 of 3 tasks done
Owner:    backend
Requires-Roy: false
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
- [ ] T2 | Decide whether a topology may name globs that match nothing on the
      tree it is run against. Verify: either `topology.read` refuses a glob no
      page matches -- at read time, where the file is being validated anyway --
      or `fan` says plainly that an uncovered page is the topology's fault
      rather than the tree's.
- [ ] T3 | Cover the staged chain with a test that survives. Verify: a test
      drives `sequential.toml` over a real tree through distribute, collate,
      docket and pull for every stage, and asserts the edits ACCUMULATE.
      MEASURED: four stages produce four markers in one paragraph -- one per
      stage, each reading the revise the one before it pulled. Fewer means a
      stage read a tree that did not carry the one before it, and nothing in the
      suite would notice today.
