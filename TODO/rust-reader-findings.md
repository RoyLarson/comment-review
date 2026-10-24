# Rust reader findings from the pre-merge review

```
Status:   open
Progress: 0 of 8 tasks closed
Owner:    backend
Requires-Roy: true
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

- [ ] T1 | Reset the generic depth at a variant separator in structure.py
        > 2026-10-23 A = 1 << 0, drops every later variant's a (structure.py:221-248)
- [ ] T2 | Detach an inner doc after an inner attribute in a body
        > 2026-10-23 mod m { #![allow(x)] //! late } reads as a1 (documentation.py:262)
- [?] T3 | Record Roy's ruling on the documentable change in page.py
        > 2026-10-23 insert <= line in documentable, page.py:606, not under O1-O5
- [ ] T4 | Remove the quadratic slices in projection and documentation
        > 2026-10-23 4000 items: 5.9 s; tables.rs 132 s (projection.py:469)
- [ ] T5 | Delete the unread contextual entries auto, safe, default
        > 2026-10-23 contextual is read for keywords only (structure.py:356)
- [ ] T6 | Give a spaced outer attribute its owner's a place
        > 2026-10-23 # [derive(Debug)] loses the a; doc becomes f0 (scanner.py:307)
- [ ] T7 | Test that neither reader imports the other's package
        > 2026-10-23 Spec acceptance: neither reader imports the other's package
- [ ] T8 | Correct the Page.warnings docstring in binder/page.py:154
        > 2026-10-23 It says one per noted place; two warnings can share a place
