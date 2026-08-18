# A block does not say where its text starts, so two things infer it

```
Status:   open
Progress: 0 of 4 tasks done
Owner:    session
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
literal, and **it has to**: store the file slice there and `physical == stored`, the suffix
test stops firing, and the real line of code the literal sits inside drops out of the code set,
moving every interval boundary below it. That is the failure the same comment block already
records twice.

So one string comparison carries two unrelated facts -- what text this block holds, and whether
code precedes it -- and they are now pulling in opposite directions.

! The information exists at both producers and is thrown away: `ast.Constant` carries
`col_offset`, and `blocks_lexical` already computes `opens_at` and discards it.

## Tasks

- [ ] **Give `Block` the column its text starts at**, set by every producer. Verify: a
      `Doc()` block and a trailing comment both report a nonzero column, a comment run on its
      own line reports zero.

- [ ] **`code_lines` tests that field instead of the suffix.** Verify: `census.py` over
      `repo.py` emits the same blocks before and after -- the measurement that caught the last
      regression here was eight spurious `interval` blocks overlapping real docstrings.

- [ ] **Then `_annotated_docs` stores the file's slice**, like every other producer. Verify:
      `galley.block_matches` answers True for a `Doc()` block against an unmodified file, and
      `Block.widest` reports the real column width rather than the AST value's.

- [ ] **`prove_unchanged._without_comments` reads the same field** rather than re-deriving the
      suffix rule. Verify: its CLI tests pass unchanged, and the two implementations of one
      rule become one.

## Related

- [`the-record-is-a-parsed-template-and-should-be-a-value`](completed/the-record-is-a-parsed-template-and-should-be-a-value.md)
  -- step 7's run is where the docstring half was found, by two roles independently.
