# A licence header is unprotected in Rust and TypeScript

```
Status:   open
Progress: 0 of 5 tasks done
Owner:    comment-review
Requires-Roy: true
Raised:   2026-08-23 (2026-08-23, re-measuring `front-matter-protection-is-python-only`
          during a backlog audit -- its title was false and the surviving defect is a
          different one)
```

## Objective

A licence header is unprotected in Rust and TypeScript.

## Tasks

- [ ] MEASURED 2026-08-23 on four identical licence headers. `lic.py` and `lic.c`
      both type `f0 kind=matter`. `lic.rs` and `lic.ts` type `f0 dark-matter` --
      the file's own matter is not recognised, so the `query` guard that protects
      a licence from being edited never fires for them.
- [ ] !! RUST FAILS BY LOSING THE RUN TO THE `a` SERIES. `// Copyright` above `fn
      main()` is typed `comment` and addressed `a1` -- a declaration's
      documentation -- so the lexer's matter clause never sees it. ! Rust declares
      `doc_line = ('///', '//!')`, and an ordinary `//` run above a declaration is
      still being claimed as that declaration's doc.
- [ ] !! TYPESCRIPT FAILS BY BEING TYPED `docstring`. `/**` is TS's `doc_block`,
      so a file opening with `/** to get started */` is a docstring at `b0` -- and
      the lexer's own rule says a docstring is not matter and is what ENDS matter.
      ! This is the `corpora/sentry/eslint.config.ts` case the superseded file
      measured, still live.
- [ ] ! WHAT IS ALREADY RIGHT, so it is not re-litigated: the rule is POSITIONAL
      and per-language only in what counts as a comment -- a run starting on line
      1 or ending on the last line is matter. C proves the mechanism reaches
      beyond Python.
- [ ] * THE RULING WANTED: whether a doc-shaped opener -- `/**` in TS, `///` in
      Rust -- is matter when it is the FIRST thing in the file. ! The lexer says a
      docstring is never matter, which is right for a module docstring and wrong
      for a licence written in `/** */`. The two cannot both hold on one clause.
