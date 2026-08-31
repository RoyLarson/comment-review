# The a-then-b tie order is Python's placement, not a universal rule

```
Status:   open
Progress: 4 of 4 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-20 (Roy, 2026-08-20: 'a is correct for python and incorrect for rust
          -- a is the innermost section to the declaration that we can determine to take
          a docstring')
Superseded: 2026-08-20 — SUPERSEDED by Roy, 2026-08-20: *"still correct. a has to be put
            in first because it is the 'inner most' documentation -- the b gets applied
            in the rows outside-beyond it."* The a -> b -> c order IS universal and
            needs no language attached. ! The error was comparing FINAL LINE POSITIONS
            instead of APPLICATION order: two edits inserting at one point, the second
            lands ABOVE the first, so applying `a` first puts `b` outside it in an
            above-doc language and a below-doc one alike. Nothing needs to state which
            side a doc goes on.
```

## Objective

The a-then-b tie order is Python's placement, not a universal rule.

## Tasks

- [x] T1 | FINISHED | unknown | RECORD THE RULE THAT COVERS BOTH: an `a` HUGS
      ITS DECLARATION and a `b` sits OUTSIDE it. Python puts a docstring INSIDE
      the body, so at a tie `a` precedes `b`; Rust's `///` sits ABOVE the `fn`,
      so at a tie `b` precedes `a`. The b0-before-a0 exception is the same rule,
      not an exception: front matter is outside the module, the docstring is the
      module's own first line.
- [x] T2 | FINISHED | unknown | `lexer.declarations` returns `(line, insert)`
      and nothing states WHICH SIDE of the declaration the doc goes on. The
      tie-break needs it, and only a parser knows it -- the same argument that
      put `insert` in the lexer.
- [x] T3 | FINISHED | unknown | The order is written as universal in five
      places: docs/plans/0.2.5 A4, tests/test_galley.py:284,
      TODO/b-foliator-uninitialised.md (2 places),
      TODO/census-degrades-silently.md:76,
      TODO/galley-is-still-index-keyed.md:13. Each says 'a -> b -> c' with no
      language attached.
- [x] T4 | FINISHED | unknown | * RULING NEEDED before the galley applies by
      series: is 'a hugs its declaration' the rule, or is the order fixed a -> b
      -> c and an above-doc language expresses its doc some other way? Nothing
      today produces an `a` outside Python, so this is not yet observable -- it
      becomes wrong the moment a second tier resolves declarations.
