# An above-declaration doc comment is addressed as a b, not as the declaration's a

```
Status:   open
Progress: 0 of 5 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-20 (found while adding the per-language declares keyword list,
          2026-08-20)
Measured: 2026-08-20 — 2026-08-20 -- WHAT THE LEXER ALREADY SETTLES, per language. Roy
          asked whether the lexer states that the paragraph is a docstring and not a
          comment. It does, for 7 of 10: rust, java, csharp, swift, kotlin, javascript
          and typescript all carry a doc MARKER (`///`, `/**`), so syntax alone decides
          the kind. go, ruby and lua have no marker -- a doc comment there IS an
          ordinary comment in the right POSITION, which is exactly what
          `doc_is_structural` means. Python is already `a1` via the AST. !! AND
          `declares` IS -1 IN EVERY NON-PYTHON CASE. The lexer answers 'is this a doc?'
          and never 'a doc for what?'. ! SO THE JOIN IS THE PAGE'S -- Roy: *"this is
          something the page needs to resolve probably."* The page is the only thing
          holding the paragraphs AND the places. ! It follows that the join needs TWO
          rules, not one: where a marker exists, a `docstring` run ending immediately
          above a declaring line fills that `a`; where none exists (go, ruby), the same
          must be read off a `comment` run, and position is the only evidence there is.
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
      introduced for -- `addresser.py`: *'with `a` the docstring leaves the `b`
      series: re-measured over 10,744 paragraphs, 0 shared places.'* Today a Rust
      `///` is counted as a `b`, so a declaration's doc and the gap above it are
      the same address, the exact shape the `a` series ended for Python.
- [ ] Python is unaffected -- its docstrings already carry `declares` from the
      AST. This is the lexical tier only.
- [ ] Check the interaction with `doc_is_structural`, which today flags such a run
      for a reviewer to resolve BY HAND. If the join lands, that flag is answered
      mechanically for the languages carrying a keyword list, and should say so
      rather than asking twice.
