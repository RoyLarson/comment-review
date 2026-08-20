# The census degrades silently on four inputs

```
Status:   open
Progress: 0 of 6 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-19 (the seven-agent address review, 2026-08-19)
Measured: 2026-08-19 — the BOM case is worse than filed: the comment came back with
          address '' -- genuinely unaddressed, not merely misparsed -- with anchor set
          to the BOM character itself.
```

## Objective

!! **FOUR INPUTS PRODUCE A CENSUS THAT IS WRONG RATHER THAN REFUSED, EACH EXITING 0.** The run
reads as complete, the addresses are nonsense, and nothing says so. `census.py` already holds the
opposite rule -- *"Every file handed in is censused, or this errors"* -- and these are the cases
that slip past it by parsing far enough to produce blocks.

**A Python file that fails `ast.parse` collapses every comment onto `@b0`.** Three blocks at one
address, in the REVIEWER'S filtered view, with a code line in no block at all. `census_for` skips
`intervals`, `margins` and `fill_the_gaps` for an unparsed file, so no code lines are established
and `address()` counts 0 for everything. ! Two failure modes for one condition: a `TokenError`
(`def f(:`) is a hard NOT CENSUSED at rc 1, a `SyntaxError` (`x = = 1`) is a soft `unparsed` block
at rc 0.

**A UTF-8 BOM makes any Python file unparseable** -- `census.py` reads with `encoding="utf-8"`
rather than `utf-8-sig`, and the BOM survives into `ast.parse`. Routine on Windows, which is where
this repo is developed.

**A one-line `def f(): pass` has an `a` place that inserts ABOVE the `def`**, because
`_undocumented` uses `body[0].lineno` and for a one-liner that is the `def` line itself. Measured
end to end: the galley wrote a docstring above the declaration and the file raised
`IndentationError`; un-indented it silently becomes the MODULE docstring. Also hits `@overload`
and `class C: pass`.

**An empty file yields zero blocks and has no `a0`**, so an empty `__init__.py` is uncitable --
there is nowhere to say a module docstring is missing. ! It contradicts `intervals`' own
docstring: *"A file with no code at all is therefore one interval."*

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
- [ ] !! A ONE-LINE DECLARATION'S `a` PLACE POINTS OUTSIDE THE DECLARATION, AND NO
      APPLICATION ORDER FIXES IT. `_undocumented` takes `body[0].lineno`, which
      for `def f(): pass` is the `def` line itself -- so the insertion point is
      ABOVE the declaration the docstring documents. ! It is not a collision with
      a0: an address is not an edit range, and the a -> b -> c order settles two
      places that share an insertion point. This is different -- there is no line
      INSIDE the body to insert on, and writing one needs the line SPLIT, which is
      a code change 7b forbids. ! So decide whether the place is UNWRITABLE and an
      `add` on it is refused with a reason, rather than landing above the `def`.
      Same shape for `@overload` and `class C: pass`.
