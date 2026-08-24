# An above-declaration doc comment is addressed as a b, not as the declaration's a

```
Status:   open
Progress: 2 of 6 tasks done
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
TRIAGED:  2026-08-23 — 2026-08-23. Tasks 1 and 4 are records -- the measurement, and the
          note that Python is unaffected because its docstrings already carry declares
          from the AST. Tasks 2 and 3 state HOW the join must work and what it must not
          break, and are constraints rather than work. ! THE WORK ITSELF WAS NOT WRITTEN
          DOWN, which is why this read 0 of 5 with nothing to do; it is now task 6. Task
          5 stays: check the interaction with doc_is_structural, which today asks a
          reviewer to resolve by hand what the join would answer mechanically.
```

## Objective

An above-declaration doc comment is addressed as a b, not as the declaration's a.

## Tasks

- [x] !! MEASURED on `/// The one doc.` above `fn one() {}`: `a1` exists with
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
- [x] Python is unaffected -- its docstrings already carry `declares` from the
      AST. This is the lexical tier only.
- [ ] Check the interaction with `doc_is_structural`, which today flags such a run
      for a reviewer to resolve BY HAND. If the join lands, that flag is answered
      mechanically for the languages carrying a keyword list, and should say so
      rather than asking twice.
- [ ] JOIN A DOC RUN TO THE DECLARATION BELOW IT. A docstring-kind run ENDING on
      the line immediately above a declaring line documents that declaration, and
      declarations() already reports which lines those are. The doc must LEAVE the
      b series when it joins -- that is what a was introduced for. Verify: on `///
      The one doc.` above `fn one() {}`, a1 reports documented rather than
      undocumented, the /// is no longer a b, and no place is shared.
