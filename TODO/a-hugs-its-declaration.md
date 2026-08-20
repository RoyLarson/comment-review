# The a-then-b tie order is Python's placement, not a universal rule

```
Status:   open
Progress: 0 of 4 tasks done
Owner:    session
Requires-Roy: true
Raised:   2026-08-20 (Roy, 2026-08-20: 'a is correct for python and incorrect for rust
          -- a is the innermost section to the declaration that we can determine to take
          a docstring')
```

## Objective

The a-then-b tie order is Python's placement, not a universal rule.

## Tasks

- [ ] RECORD THE RULE THAT COVERS BOTH: an `a` HUGS ITS DECLARATION and a `b` sits
      OUTSIDE it. Python puts a docstring INSIDE the body, so at a tie `a`
      precedes `b`; Rust's `///` sits ABOVE the `fn`, so at a tie `b` precedes
      `a`. The b0-before-a0 exception is the same rule, not an exception: front
      matter is outside the module, the docstring is the module's own first line.
- [ ] `lexer.declarations` returns `(line, insert)` and nothing states WHICH SIDE
      of the declaration the doc goes on. The tie-break needs it, and only a
      parser knows it -- the same argument that put `insert` in the lexer.
- [ ] The order is written as universal in five places: docs/plans/0.2.5 A4,
      tests/test_galley.py:284, TODO/b-foliator-uninitialised.md (2 places),
      TODO/census-degrades-silently.md:76, TODO/galley-is-still-index-keyed.md:13.
      Each says 'a -> b -> c' with no language attached.
- [ ] * RULING NEEDED before the galley applies by series: is 'a hugs its
      declaration' the rule, or is the order fixed a -> b -> c and an above-doc
      language expresses its doc some other way? Nothing today produces an `a`
      outside Python, so this is not yet observable -- it becomes wrong the moment
      a second tier resolves declarations.
