# mark_matter cannot fire outside Python, so a licence header is editable work

```
Status:   open
Progress: 0 of 7 tasks closed
Owner:    session
Requires-Roy: false
Raised:   2026-08-21 (the /code-review xhigh of 2026-08-21, focused on the file-to-
          census route)
Ruled:    2026-08-21 — the matter rule is POSITIONAL -- the comment run at the top (and
          at the foot) of a file, terminated by a blank line or a docstring. No module
          docstring need exist, so it resolves in every language.
```

## Objective

mark_matter cannot fire outside Python, so a licence header is editable work.

## Tasks

- [ ] T1 | MEASURED: `lic.c` and `lic.rs` census with `annotations=[]` and `f0
      kind=dark-matter`; an identical `lic.py` gets `annotations=['matter']`.
      The `doc` lookup in `mark_matter` requires `declares == 0`, never true at
      the lexical tier.
- [ ] T2 | !! SO THE `query` GUARD NEVER FIRES. `verdicts.py`'s rule 'ANY EDIT
      PROPOSED ON FRONT MATTER BECOMES A query' keys on `series_of(held) ==
      FRONT`, so a `correct` on licence text in C, Rust, Java, JS or Go is
      admitted as ordinary work. Roy's reason for that guard was that the cost
      is asymmetric and sits OUTSIDE this system -- a licence is a legal
      instrument.
- [ ] T3 | MEASURED 2026-08-21, a live instance:
      `corpora/sentry/eslint.config.ts` holds two `/** */` blocks above its
      first code line -- a 'to get started, read the docs' header at 1-11 and an
      'Import Linting Strategy' note at 12-26 -- and BOTH census as `@b0`. The
      first code line is `import e18e from ...`, and `import` is not in
      TypeScript's `declares`, so no `a` place exists for either. ! THIS
      COLLISION IS CLOSED BY THIS TODO ALONE: `mark_matter` firing would put the
      header on `f0` and leave 12-26 on `b0`. It needs no gap- splitting ruling
      and is NOT an instance of `two-paragraphs-one-address`, which is where it
      was first attributed.
- [ ] T4 | !! RULED 2026-08-21, AND IT IS POSITIONAL RATHER THAN PER-LANGUAGE.
      Roy: *"Any normal comment section at the top of the file becomes f0 until
      there is either a docstring or a blank line."* And, asked whether back
      matter differs: *"same answer for the back matter because of the same
      reason"* -- so the run at the FOOT of the file, read upward, terminated by
      a blank line or a docstring, is the back matter. ! No module docstring
      need EXIST for either, which is what made the old rule Python-only.
- [ ] T5 | ! THE OVER-INCLUSION IS ACCEPTED AND HAS A ROUTE BACK. A top-of-file
      comment that is not a licence still becomes `f0`. Roy: *"The agents can
      always ask for the record for the f0 to move it which ultimately doesn't
      effect the final pageset because the f0 would get a None and be skipped
      and the b0 would be then put at the top again. it is a little cluggy but
      it will be consistent."* ! CONSISTENT beats correct-by-inference here: a
      rule that guesses which header is a licence is a rule that guesses
      differently per language.
- [ ] T6 | !! IT MOVES A PARAGRAPH BOUNDARY, NOT JUST AN ANNOTATION, and that is
      the work. Today only CODE ends a run, so a Rust file opening `//
      Copyright` / `// MIT` / blank / `/// Returns the name.` censuses as ONE
      paragraph over lines 1-4. MEASURED 2026-08-21. Under the ruling it must
      split: `f0` = 1-2, and line 4 is the declaration's own documentation.
      `text` is the run with its comment markers stripped, so the split has to
      go through the lexer's own construction rather than re-deriving it.
- [ ] T7 | THE COMPOSITOR THEN WRITES IT POSITIONALLY. Roy: *"back-matter gets a
      write if it is not None at the end of the file. front-matter gets a write
      at the front of the file if it is not None."* ! VERIFIED 2026-08-21 that
      this needs no step over the shebang: the shebang is INSIDE `f0` --
      `raw=['#!/usr/bin/env bash', '# Copyright 2001.']` with `ann=['matter']`
      -- in shell, Python and Ruby alike, because that route is a regex on line
      1 rather than a language rule. Roy: *"the shebang is front-matter"*,
      *"always"*.
