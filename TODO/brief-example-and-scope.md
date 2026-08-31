# The brief's example and its resolution scope disagree with a real run

```
Status:   open
Progress: 0 of 3 tasks done
Owner:    agents
Requires-Roy: false
Raised:   2026-08-29 (2026-08-29, the first end-to-end run with a real block-context
          agent over two files: it returned 8 `query` and 0 `clean`, and named both
          causes itself)
```

## Objective

The brief's example and its resolution scope disagree with a real run.

## Tasks

- [ ] T1 | The brief's `sha` matches what `bind` writes. Verify: the example's
      sha is the length `binder.bind` produces -- 16 hex characters on
      2026-08-29, where the example shows 40.
- [ ] T2 | The brief says what a `source` may resolve against. Verify: it states
      whether a cite is resolved against the scoped tree or the checkout, and a
      role reviewing two files of a larger repo can tell which without guessing.
- [ ] T3 | A narrow scope is distinguishable from a broken one. Verify: a run
      whose citations all fall outside the scoped tree says so, rather than
      returning `query` for every place and reading as a reviewer that could not
      do its job.
