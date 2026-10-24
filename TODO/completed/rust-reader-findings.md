# Rust reader findings from the pre-merge review

```
Status:   closed
Progress: 8 of 8 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-23 (pre-merge code review of feat/lexer-rust, 2026-10-23)
```

## Objective

Findings in the Rust lexical reader (`src/comment_review/reading/rust/`) from
the pre-merge code review of 2026-10-23. The full review, with probes, is in the
run's review file; each task below names the site and the shape.

The reader meets its purpose on the measured input: every `.rs` file in the
local Cargo registry (1,646) sets back byte for byte, every added, dropped or
moved doc proves unchanged, and every code mutation tried is refused. What is
left is a place lost on a valid shape, a rule the spec states that the reader
does not follow in bodies, a cost quadratic in file size, a page.py change with
no recorded approval, and smaller items.

## Tasks

- [x] T1 | FINISHED: angles after a member's own = are operators, the simple rule Roy chose 2026-10-24 | 5d877cab | Reset
      the generic depth at a variant separator in structure.py
        > 2026-10-23 A = 1 << 0, drops every later variant's a (structure.py:221-248)
- [x] T2 | FINISHED: every inner doc in a body is detached at its b place under decision-log.md Addressing: #33 | a8672b0d | Detach
      an inner doc after an inner attribute in a body
        > 2026-10-23 mod m { #![allow(x)] //! late } reads as a1 (documentation.py:262)
- [-] T3 | SUPERSEDED by the revert of the documentable change, decision-log.md Addressing: #33 | a8672b0d | Record
      Roy's ruling on the documentable change in page.py
        > 2026-10-23 insert <= line in documentable, page.py:606, not under O1-O5
- [x] T4 | FINISHED: lookups walk by index and each owner's body is recorded in one pass | 7b219a65 | Remove
      the quadratic slices in projection and documentation
        > 2026-10-23 4000 items: 5.9 s; tables.rs 132 s (projection.py:469)
        > 2026-10-23 Also _body_opener: an inner doc in a field's const block
- [x] T5 | FINISHED: auto, safe and default deleted from contextual | d7fc1385 | Delete
      the unread contextual entries auto, safe, default
        > 2026-10-23 contextual is read for keywords only (structure.py:356)
- [x] T6 | FINISHED: an attribute opener may hold whitespace and comments between its characters | 29e92d04 | Give
      a spaced outer attribute its owner's a place
        > 2026-10-23 # [derive(Debug)] loses the a; doc becomes f0 (scanner.py:307)
- [-] T7 | SUPERSEDED by decision-log.md Process: #217, no test for reader independence | 9e3287a0 | Test
      that neither reader imports the other's package
        > 2026-10-23 Spec acceptance: neither reader imports the other's package
- [x] T8 | FINISHED: the docstring says two warnings can share a place | 787884f5 | Correct
      the Page.warnings docstring in binder/page.py:154
        > 2026-10-23 It says one per noted place; two warnings can share a place
