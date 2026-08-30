# Four defects in collator.py, found by reading only the code

```
Status:   open
Progress: 0 of 11 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-30 (2026-08-30, from the blind rewrite of collator.py -- the prose was
          deleted whole and written back by an agent with no access to the vocabulary,
          the docs, the prototype, git history or the built copy under plugins)
```

## Objective

Four defects in collator.py, found by reading only the code.

## Tasks

- [ ] T1 | Refuse a `move` whose `claim.to` equals its own `address`, by name.
      Verify: `desk.mark.parse` returns a named problem -- today it returns (mark,
      []), measured 2026-08-30.
- [ ] T2 | Prove the docket cannot carry that shape. Verify: a test asserts no
      alteration is a delete with no matching write, and it FAILS against today's
      code, which produces a docket entry of path m.py, cue b1, text None.
- [ ] T3 | Check the neighbouring shapes. Verify: a `move` across files, and one
      whose `to` names a place the binder does not carry, each reach a named
      outcome rather than a silent delete.
- [ ] T4 | Reproduce the CRLF mismatch as a failing test over a real CRLF file.
      Verify: a two-line `verbatim` taken verbatim from that file is reported as
      not found. MEASURED: the window is rejoined with a newline while `_lines`
      preserved the carriage returns.
- [ ] T5 | Decide which side normalises -- the window, the `verbatim`, or both at
      the boundary. Verify: a single-line `verbatim` still matches, and the choice
      is stated where `_lines` says it preserves the endings.
- [ ] T6 | Check the same rejoin elsewhere. Verify: no other comparison in `src/`
      splits on real line endings and rejoins with one spelling.
- [ ] T7 | Reproduce the cache collision: one cache, two roots holding the same
      path with different text. Verify: the second read returns the first root's
      lines, and the test fails today.
- [ ] T8 | Key the cache on the root as well, or refuse a cache handed a second
      root. Verify: the staged design cannot answer from the wrong tree -- a run
      reads an original at one stage and a revise at the next.
- [ ] T9 | Reproduce the cite guard. Verify: `_cite_at` raises `ValueError` on a
      superscript line number today, and a test asserts a named problem instead.
- [ ] T10 | Return a problem rather than raising. Verify: `verify_report` over an
      edit_copy holding one malformed cite reports it and still checks every other
      mark -- today one bad cite aborts the whole report.
- [ ] T11 | Audit the other guards for the same shape. Verify: no `isdigit()` in
      `src/` is followed by an `int()` that can still fail.
