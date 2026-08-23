# A comment fenced by code on both sides is censused as prose holding the statement

```
Status:   decision-needed
Progress: 4 of 4 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-19 (the c-series writability ruling, 2026-08-19)
Ruled:    2026-08-19 — Roy, 2026-08-19: 'all intermediate comments are ignored. They can
          be brought up by the agents as code change suggestions.' Not censused at all
          -- the same ruling that keeps a Python type annotation out. original_column no
          longer carries -1, and prove_unchanged got STRONGER: the line is code now, so
          a literal beside the delimiter is caught where the old 'unprovable' refused to
          compare.
```

## Objective

!! **`int x = /* why */ 5;` IS CENSUSED AS A `c` PLACE WHOSE TEXT IS THE STATEMENT.**
Measured 2026-08-19 on a three-line C file:

```
f.c@c1   comment   col=-1   text='int x = /* why */ 5;'
```

The block's `text` is what four reviewers read as prose, and it is executable code. It carries no
annotation saying so. `block-context` measures its claims against the code; there is no claim,
there is a statement.

! **The census stores the whole line ON PURPOSE.** Cutting at the opener loses the `5;`, which
would make `5` and `7` compare EQUAL and `prove_unchanged` report PROVEN on a changed literal --
that condition is written at `census.py` and is correct. What is missing is that the block is then
handed on as prose.

!! **`original_column = -1` IS A SECOND FACT WEARING THE FIRST ONE'S CLOTHES.** Roy, 2026-08-19, on
the column: *"Or does it only apply to address lines - which drops the -1 sense entirely."* The
field says WHERE THE PROSE STARTS. For this block that is a real column -- the `/*`. What makes it
unwritable is that the prose does not run to the END of its last line, which is a fact about the
other end and has nowhere to live. `-1` is the stopgap that keeps `galley.py` from deleting the
`5;`, and it is the only negative value the field takes.

! **The other end already refuses it.** `prove_unchanged._delimiter_shares_the_line` makes such a
file `unprovable`, so nothing written over it reaches stage 8. The gap is stages 4 through 7a,
where a reviewer reads the statement as prose and may rule on it.

**The decision is where the shape is refused, not how the column encodes it:** at census time --
name the block and stop, as a language with no record does -- or as an annotation that filters it
out of what a reviewer reads, the way front matter is filtered.

## Tasks

- [x] !! RULING NEEDED: where is the both-sides shape refused? At census time --
      name the block and stop, the way a language with no record does -- or as an
      annotation that filters it out of what a reviewer reads, the way front
      matter is filtered. Today it is neither: it is handed on as prose.
- [x] The block's `text` is the whole statement and it carries no annotation.
      Measured 2026-08-19: `f.c@c1  comment  col=-1  text='int x = /* why */ 5;'`.
- [x] Whatever is ruled, `original_column` stops carrying `-1` -- the field says where
      the prose STARTS, and this is a fact about where it ENDS.
      `galley.code_on_both_sides` reads it today and is the only reader.
- [x] No test covers the both-sides shape reaching a reviewer.
      `tests/test_census_blocks.py` covers the CUT and
      `tests/test_prove_unchanged.py` the refusal; nothing asks what stages 4-7a
      are handed.
