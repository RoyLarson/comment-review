# A block does not say where its text starts, so two things infer it

```
Status:   in-progress
Progress: 9 of 10 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-17, by /simplify over the 0.2.3 branch
Narrowed: 2026-08-19 — the staleness symptom was the ADDRESSER's sweep, now removed --
          what remains is the galley's comparison, where checking the file is right and
          the stored text is wrong
Narrowed: 2026-08-19 — B3 closed 2026-08-19: one raw_lines rule for both tiers, the
          block's own characters cut at original_column. Four of six comment shapes were
          unwritable, not one. Two boxes ticked and one SUPERSEDED -- it prescribed
          storing the whole physical line in both tiers, which would have put the code
          in two fields.
TRIAGED:  2026-08-23 — ONE TASK LEFT, and Requires-Roy is cleared: both questions this
          file was holding open are answered by work already in the tree.
          `_annotated_docs` no longer exists and a PEP 727 `Doc()` is not censused at
          all; `Paragraph.widest` was DELETED in fa25924. What remains is
          prove_unchanged, which still re-derives the suffix rule at
          `prove_unchanged.py:156`.
```

## Objective

A census paragraph records WHICH LINES it spans, and `original_column` now records WHERE ON THE
FIRST LINE its text begins. **One reader still infers that fact instead of reading it.**
`prove_unchanged._without_comments` reconstructs the surviving PREFIX of a line by testing
whether the stored text is a proper SUFFIX of the physical one --
`elif stored and actual.endswith(stored)`, `prove_unchanged.py:156` -- which is the same rule the
producers already state.

! **SUPERSEDED 2026-08-18: the reason once given for leaving the inference alone -- that storing
the file slice would stop the suffix test firing and drop the declaration line out of the code
set -- no longer holds.** `code_lines` has no suffix test; the producer states what it needs.

!! **AND `whole_lines` WAS NOT THE END OF IT, which is the case that produced the column.** A
boolean answers one question -- does code share this paragraph's first line -- and
`_without_comments` needs a different one: it must rebuild the surviving prefix TEXT, and a
boolean cannot give it one. `whole_lines` is gone and `original_column` replaced it
(`lexer.py:285-289`); the last reader that never moved is the one this file now tracks.

! The information exists at the producers and reaches the census: `lexer.py:1148` and
`lexer.py:1743` set `original_column` on both tiers, and `page.py:276, 287, 334` already read it.

## Two questions this file held open, and how each was answered

**1. `_annotated_docs` -- CLOSED, the other way.** The function is gone from the tree (measured
2026-08-23: no `_annotated_docs` in `scripts/*.py`; the only hits are stale `__pycache__`). A PEP
727 `Doc()` is not censused as prose at all, on the same ground as any other type annotation --
Roy, 2026-08-18: *"Type annotations are not comments or docstrings ... we are not building a type
checker"* -- and `tests/test_cues.py:479 test_a_type_annotation_is_NOT_a_docstring` pins it. So
there is no field to rule on and no producer to change.

**2. `Paragraph.widest` -- CLOSED, it went.** The file asked *"does a width rule ever read it, or
does it go?"*. Answered by deletion in `fa25924`, 2026-08-21: *"`Paragraph.widest` WAS DEAD -- a
property read by no code, no test and no prose."* Measured 2026-08-23: no `widest` member exists
in `plugins/`, `tests/` or `docs/`.

## Tasks

- [x] **T1 -- DONE 2026-08-19 -- `original_column`, set by every producer, and `whole_lines` is gone.**
      The START column is a field; the END column was RULED AWAY rather than built. Roy,
      2026-08-19: an INTERMEDIATE comment -- `/* note */ x = 1`, code on both sides -- *"is not a
      comment that can be systemically and completely verified across code bases"* and is not
      censused at all, on the same grounds as a Python type annotation. So there is no second
      edge to state: a paragraph either owns its lines, or starts at a column and runs to the end of
      the line. ! The shape that motivated the span is now handled by not being prose.

- [x] **T2 -- DONE 2026-08-18 -- `code_lines` tests a field instead of the suffix.** It reads what
      the producer states rather than comparing text. ! The field was a BOOLEAN and this file
      argued for a span; T1 is what the span bought over it.

- [x] **T3 -- SUPERSEDED 2026-08-23. There is no `_annotated_docs` to rule on.** Filed as
      *"rule whether `_annotated_docs` should store the file's slice at all"*. The producer was
      removed and a `Doc()` literal is not prose -- see the objective above. ! The measurement
      that made it a question -- `Block.widest` reporting the AST value's width -- went with
      `widest` itself, so nothing reads an AST value for these blocks today.

- [ ] **T4 -- `prove_unchanged._without_comments` reads `original_column`** rather than re-deriving
      the suffix rule at `prove_unchanged.py:156`. MEASURED 2026-08-23: still
      `elif stored and actual.endswith(stored)`, so one rule has two implementations, exactly as
      this file found them. Verify: `uv run pytest -q tests/test_prove_unchanged.py` passes
      unchanged, and `endswith` no longer decides where a line is cut.

- [x] **T5 -- DONE 2026-08-19 -- ONE ADDRESS NAMED TWO BLOCKS on a mid-line comment, and this was
      the cause.** Measured on `let b = 2; /* opens` / `and closes */`: the comment and an empty
      interval were both `@b1`, and lines 2-3 each carried two addresses. `record.entry_for`
      returned the interval, so every text check on the comment read `""`.
      ! **Two computations of one fact inside one module** -- `address()` read
      `kind in SHARES_ITS_LINE`, `code_lines_of` read `whole_lines`. A mid-line `comment` is
      `whole_lines=False` and in neither list. **`address()` now reads the producer's field and
      `SHARES_ITS_LINE` is deleted.** Two further sites were asking a second way and now read the
      same fact: `margins()` (a line already carrying prose that shares it has no room left) and
      `blocks_in()` (a paragraph OVERLAPS a gap; it does not have to START in one -- a start test
      emitted an interval over the comment's own second line).
      ! **Re-measured over 18 files in four languages: 7,436 lines, each with exactly one address,
      0 shared.** The prior figure was Python-only.

- [x] **T6 -- DONE 2026-08-19 -- ONE RULE, BOTH TIERS: `raw_lines` is the paragraph's OWN
      CHARACTERS**, its lines whole where it owns them and cut at `original_column` where code comes
      first, so `anchor + raw_lines[0]` rebuilds the physical line. ! **It was FOUR of six comment
      shapes, not the indented block alone** -- every block comment off column 0 and every
      trailing comment in the ten lexical languages. Re-measured: 6 of 6 match a fresh census, 0
      refused across the fixtures, and a `c` edit writes in Go end to end keeping the statement
      and its tab. ! It also stopped feeding CODE to the annotators: `prose_numbers` reads this
      field, so `TIMEOUT = 30  # the note says nothing` reported 30 as a claim the prose makes.
      **The original text, for the record:** the lexical tier cut `raw_lines[0]` at the comment opener
      where the stdlib tier stored the whole line, so `galley.block_matches` compared `/* block`
      against `    /* block` and refused the splice:
      `REFUSED sample.rs: 1 range(s) no longer match the census: 6-7`.
      ! **SCOPE CORRECTED 2026-08-19.** This was filed as *"a FRESH census reads as STALE"*, which
      it no longer does: it reached `--check`, `--resolve` and `--anchor` only through a staleness
      sweep the cues had no business running, and that sweep is gone (T7). **What remains is the
      galley**, where comparing stored text against the file is exactly right and the stored text
      was wrong. ! It also masked the mid-line collision, which is why that one survived the first
      measurement.

- [x] **T7 -- DONE 2026-08-19 -- THE ADDRESSER NO LONGER SWEEPS FOR STALENESS, and it
      un-blocked the rest of this file.** Roy: *"not necessary for foliation to do
      the staleness sweep as long as the original census is still an available
      document ... In a small way it is the foliation stating the line numbers
      matter still."* ! Every question it takes is census-internal, so it reads no
      file and takes no `--repo`. **`--check` now reports the mid-line collision
      it was written to catch** -- `SHARED s.js@b1 <- 0-0 interval | 2-3 comment`
      -- which the sweep had masked on every non-Python file.

- [x] **T8 -- SUPERSEDED 2026-08-19 by T7, which carries the DONE record.** This was filed as a
      SECOND task recording the same fix -- `ONE fact decides "shares its line"` -- while the task
      that STATES the work sat unchecked, so one file both claimed the work remained and recorded
      it complete. ! **It was briefly DELETED, and that was wrong.** Roy, 2026-08-19:
      *"todos don't get deleted they get SUPERSEDED and checked."* A deleted box
      leaves no trace that it was ever there or why it went; a superseded one
      keeps the error legible. Restored here rather than left out.

- [x] **T9 -- SUPERSEDED 2026-08-19 -- THIS PRESCRIBED THE WRONG FIX**, and is kept so the error
      stays legible. It said BOTH TIERS STORE THE WHOLE PHYSICAL LINE. That satisfies the
      staleness check and puts the code in TWO fields -- `anchor` and `raw_lines` -- which is the
      conflation the anchor was added to end, and Roy named it the same day: *"won't this kill the
      anchor?"* The rule shipped is the opposite: `raw_lines` holds the paragraph's own characters
      only, and the anchor holds the code. ! Its MEASUREMENT was right and is what found the
      defect -- a lexical trailing comment storing `['// note']` against `int b = 2; // note`.

- [x] **T10 -- DONE. `Paragraph.widest` WENT, which is the answer this box asked for.** Filed
      2026-08-19 as *"decide: does a width rule ever read it, or does it go?"* after measuring it
      had no caller across `plugins/`, `tests/` and `docs/`. Deleted in `fa25924`, 2026-08-21, as
      part of the sweep for dead METHODS; re-measured 2026-08-23, no member of that name exists.

## Related

- [`the-record-is-a-parsed-template-and-should-be-a-value`](completed/the-record-is-a-parsed-template-and-should-be-a-value.md)
  -- step 7's run is where the docstring half was found, by two roles independently.
