# The census degrades silently on four inputs

```
Status:   open
Progress: 0 of 5 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-19 (the seven-agent address review, 2026-08-19)
```

## Objective

The census degrades silently on four inputs.

## Tasks

- [ ] !! **A Python file that fails `ast.parse` collapses every comment onto
      `@b0`, rc=0.** Three blocks at one address, in the REVIEWER'S filtered view,
      and a code line in no block at all. `census_for` skips
      `intervals`/`margins`/`fill_the_gaps` for an unparsed file, so no code lines
      are established and `address()` counts 0 for everything. ! Two failure modes
      for one condition: a `TokenError` is a hard NOT CENSUSED rc=1, a
      `SyntaxError` is a soft `unparsed` block rc=0.
- [ ] **A UTF-8 BOM makes any Python file unparseable**, rc=0. `census.py` reads
      with `encoding="utf-8"`, not `utf-8-sig`; the BOM survives into `ast.parse`.
      Routine on Windows.
- [ ] **A one-line `def f(): pass` has an `a` place that inserts ABOVE the
      `def`.** `_undocumented` uses `body[0].lineno`, which for a one-liner is the
      `def` line. Measured end to end: the galley wrote a docstring above the
      declaration and the file raised `IndentationError`; un-indented it silently
      becomes the MODULE docstring. Also hits `@overload` and `class C: pass`.
- [ ] **An empty file yields zero blocks and has no `a0`**, so an empty
      `__init__.py` is uncitable -- there is nowhere to say a module docstring is
      missing. ! Contradicts `intervals`' own docstring: *"A file with no code at
      all is therefore one interval."* The weaker form hits any file with no
      statements.
- [ ] **`references/compact.md` says of `unparsed` "the file did not parse, so
      nothing was censused"** -- false. The comment blocks ARE censused and handed
      to reviewers.
