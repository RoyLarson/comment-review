# A block does not say where its text starts, so two things infer it

```
Status:   open
Progress: 3 of 7 tasks done
Owner:    session
Requires-Roy: true
Raised:   2026-08-17, by /simplify over the 0.2.3 branch
```

## Objective

A census block records WHICH LINES it spans and never WHERE ON THE FIRST LINE its text begins.
Two places need that fact and both infer it by comparing the stored text against the file:
`census.code_lines` decides whether a line is code by testing whether the block's first stored
line is a proper SUFFIX of the physical one, and `prove_unchanged._without_comments` re-derives
the same rule independently to decide whether a line keeps a code prefix.

**The inference is why one producer could not be fixed with the other.** A structural
docstring's `raw_lines` became the file's own slice on the 0.2.3 branch, which fixed
`galley.block_matches` -- it had answered False for every docstring against an unmodified file.
`_annotated_docs`, twelve lines below it, still stores the AST value for a PEP 727 `Doc()`
literal.

! **SUPERSEDED 2026-08-18: the reason given here for that -- that storing the file slice would
stop the suffix test firing and drop the declaration line out of the code set -- no longer
holds.** `code_lines` has no suffix test: it reads `Block.whole_lines`, which the producer
states, so what `raw_lines` holds does not affect it. The remaining readers of the AST value
are `Block.widest` and `annotate.prose_numbers`, and both want the literal's text rather than
the line it sits in -- which is a reason to KEEP the AST value there, and a better one than the
superseded one. **The task below is cheaper than this paragraph says.**

!! **AND `whole_lines` IS NOT THE END OF IT, which is the case for the column.** It answers
one question -- does code share this block's first line -- and the two readers wanted different
things. `prove_unchanged._without_comments` still cannot use it: it must reconstruct the
surviving PREFIX TEXT of a line, and a boolean cannot give it one, so that file still re-derives
the suffix rule independently. Two implementations of one rule, as this file found them.

So ONE FACT is still inferred where a producer knows it: not "does code share this line",
which `whole_lines` now answers, but WHERE the block's text sits on that line -- which is what
`prove_unchanged` needs and a boolean cannot carry.

! The information exists at both producers and is thrown away: `ast.Constant` carries
`col_offset`, and `blocks_lexical` already computes `opens_at` and discards it.

## Tasks

- [ ] **Give `Block` the column its text starts at -- and the column it ends at**, set by
      every producer. ! The SPAN, not one edge: `whole_lines` was derived from the start alone
      and missed `/* note */ x = 1`, where the code is after the closer, so the galley was
      willing to write over the statement. Both edges are already in hand at the producer.
      Verify: a `Doc()` block, a trailing comment and a `/* note */ x = 1` all report a partial
      span; a comment run on its own line reports the whole line.

- [x] **DONE 2026-08-18 -- `code_lines` tests a field instead of the suffix.** It reads
      `Block.whole_lines`. ! The field is a BOOLEAN and this file argues for a span; the
      remaining tasks are what the span buys over it.

- [ ] **Rule whether `_annotated_docs` should store the file's slice at all.** It was
      going to be forced; it is now a genuine question, and the answer may be no. The slice for
      a `Doc()` carries the `Annotated[...]` wrapper, which is CODE, and the two remaining
      readers of that field -- `Block.widest` and `annotate.prose_numbers` -- want the literal's
      text rather than the line it sits in. ! Whichever way it goes, `Block.widest` reports the
      AST value's width for these blocks today and that is a measurement, so say which it
      should be.

- [ ] **`prove_unchanged._without_comments` reads the same field** rather than re-deriving the
      suffix rule. Verify: its CLI tests pass unchanged, and the two implementations of one
      rule become one.
- [x] !! **DONE 2026-08-19 -- ONE ADDRESS NAMED TWO BLOCKS on a mid-line comment, and this was
      the cause.** Measured on `let b = 2; /* opens` / `and closes */`: the comment and an empty
      interval were both `@b1`, and lines 2-3 each carried two addresses. `record.entry_for`
      returned the interval, so every text check on the comment read `""`.
      ! **Two computations of one fact inside one module** -- `address()` read
      `kind in SHARES_ITS_LINE`, `code_lines_of` read `whole_lines`. A mid-line `comment` is
      `whole_lines=False` and in neither list. **`address()` now reads `whole_lines` and
      `SHARES_ITS_LINE` is deleted.** Two further sites were asking a second way and now read the
      same fact: `margins()` (a line already carrying prose that shares it has no room left) and
      `blocks_in()` (a block OVERLAPS a gap; it does not have to START in one -- a start test
      emitted an interval over the comment's own second line).
      ! **Re-measured over 18 files in four languages: 7,436 lines, each with exactly one address,
      0 shared.** The prior figure was Python-only.

- [ ] !! **THE TWO TIERS STORE `raw_lines` DIFFERENTLY, so an INDENTED BLOCK COMMENT CANNOT BE
      EDITED.** `blocks_lexical` cuts `raw_lines[0]` at the comment opener
      (`census.py:541,561`) where `blocks_stdlib` stores the whole line, so
      `galley.block_matches` compares `/* block` against `    /* block` and refuses the splice:
      `REFUSED sample.rs: 1 range(s) no longer match the census: 6-7`.
      ! **SCOPE CORRECTED 2026-08-19.** This was filed as *"a FRESH census reads as STALE"*, which
      it no longer does: it reached `--check`, `--resolve` and `--anchor` only through a staleness
      sweep the addresser had no business running, and that sweep is gone (task above). **What
      remains is the galley**, where comparing stored text against the file is exactly right and
      the stored text is wrong. ! It also masked the mid-line collision, which is why that one
      survived the first measurement.
- [x] !! **THE ADDRESSER NO LONGER SWEEPS FOR STALENESS -- done 2026-08-19, and it
      un-blocked the rest of this file.** Roy: *"not necessary for addresser to do
      the staleness sweep as long as the original census is still an available
      document ... In a small way it is the addresser stating the line numbers
      matter still."* ! Every question it takes is census-internal, so it reads no
      file and takes no `--repo`. **`--check` now reports the mid-line collision
      it was written to catch** -- `SHARED s.js@b1 <- 0-0 interval | 2-3 comment`
      -- which the sweep had masked on every non-Python file.
- [`the-record-is-a-parsed-template-and-should-be-a-value`](completed/the-record-is-a-parsed-template-and-should-be-a-value.md)
  -- step 7's run is where the docstring half was found, by two roles independently.
