# An above-declaration doc comment is addressed as a b, not as the declaration's a

```
Status:   open
Progress: 0 of 5 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-20 (found while adding the per-language declares keyword list,
          2026-08-20)
```

## Objective

An above-declaration doc comment is addressed as a b, not as the declaration's a.

## Tasks

- [ ] !! MEASURED on `/// The one doc.` above `fn one() {}`: `a1` exists with
      anchor `fn one() {}` and reports `undocumented`, while the `///` is a
      `docstring` paragraph at `b1` with `declares=-1`. The prose IS there and the
      place IS there; nothing joins them.
- [ ] The keyword list makes the join computable: a `docstring`-kind run ENDING on
      the line immediately above a declaring line documents that declaration.
      `declarations()` already reports which lines those are.
- [ ] !! THE DOC MUST LEAVE THE `b` SERIES when it joins, which is what `a` was
      introduced for -- `foliator.py`: *'with `a` the docstring leaves the `b`
      series: re-measured over 10,744 paragraphs, 0 shared places.'* Today a Rust
      `///` is counted as a `b`, so a declaration's doc and the gap above it are
      the same address, the exact shape the `a` series ended for Python.
- [ ] Python is unaffected -- its docstrings already carry `declares` from the
      AST. This is the lexical tier only.
- [ ] Check the interaction with `doc_is_structural`, which today flags such a run
      for a reviewer to resolve BY HAND. If the join lands, that flag is answered
      mechanically for the languages carrying a keyword list, and should say so
      rather than asking twice.
