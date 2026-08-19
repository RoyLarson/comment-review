# A block does not say where its text starts, so two things infer it

```
Status:   open
Progress: 7 of 9 tasks done
Owner:    session
Requires-Roy: true
Raised:   2026-08-17, by /simplify over the 0.2.3 branch
Narrowed: 2026-08-19 — the staleness symptom was the ADDRESSER's sweep, now removed --
          what remains is the galley's comparison, where checking the file is right and
          the stored text is wrong
Narrowed: 2026-08-19 — B3 closed 2026-08-19: one raw_lines rule for both tiers, the
          block's own characters cut at edit_column. Four of six comment shapes were
          unwritable, not one. Two boxes ticked and one SUPERSEDED -- it prescribed
          storing the whole physical line in both tiers, which would have put the code
          in two fields.
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

- [x] **DONE 2026-08-19 -- `edit_column`, set by every producer, and `whole_lines` is gone.**
      The START column is a field; the END column was RULED AWAY rather than built. Roy,
      2026-08-19: an INTERMEDIATE comment -- `/* note */ x = 1`, code on both sides -- *"is not a
      comment that can be systemically and completely verified across code bases"* and is not
      censused at all, on the same grounds as a Python type annotation. So there is no second
      edge to state: a block either owns its lines, or starts at a column and runs to the end of
      the line. ! The shape that motivated the span is now handled by not being prose.

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

- [x] !! **DONE 2026-08-19 -- ONE RULE, BOTH TIERS: `raw_lines` is the block's OWN
      CHARACTERS**, its lines whole where it owns them and cut at `edit_column` where code comes
      first, so `anchor + raw_lines[0]` rebuilds the physical line. ! **It was FOUR of six comment
      shapes, not the indented block alone** -- every block comment off column 0 and every
      trailing comment in the ten lexical languages. Re-measured: 6 of 6 match a fresh census, 0
      refused across the fixtures, and a `c` edit writes in Go end to end keeping the statement
      and its tab. ! It also stopped feeding CODE to the annotators: `prose_numbers` reads this
      field, so `TIMEOUT = 30  # the note says nothing` reported 30 as a claim the prose makes.
      **The original text, for the record:** `blocks_lexical` cuts `raw_lines[0]` at the comment opener
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
- [x] !! **SUPERSEDED 2026-08-19 by the task above, which carries the DONE
      record.** This was filed as a SECOND task recording the same fix -- `ONE
      fact decides "shares its life"` -- while the task that STATES the work sat
      unchecked, so one file both claimed the work remained and recorded it
      complete. ! **It was briefly DELETED, and that was wrong.** Roy, 2026-08-19:
      *"todos don't get deleted they get SUPERSEDED and checked."* A deleted box
      leaves no trace that it was ever there or why it went; a superseded one
      keeps the error legible. Restored here rather than left out.
- [x] !! **SUPERSEDED 2026-08-19 -- THIS PRESCRIBED THE WRONG FIX**, and is kept so the error
      stays legible. It said BOTH TIERS STORE THE WHOLE PHYSICAL LINE. That satisfies the
      staleness check and puts the code in TWO fields -- `anchor` and `raw_lines` -- which is the
      conflation the anchor was added to end, and Roy named it the same day: *"won't this kill the
      anchor?"* The rule shipped is the opposite: `raw_lines` holds the block's own characters
      only, and the anchor holds the code. ! Its MEASUREMENT was right and is what found the
      defect -- a lexical trailing comment storing `['// note']` against `int b = 2; // note`.
- [`the-record-is-a-parsed-template-and-should-be-a-value`](completed/the-record-is-a-parsed-template-and-should-be-a-value.md)
  -- step 7's run is where the docstring half was found, by two roles independently.
