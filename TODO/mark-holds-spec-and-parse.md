# mark.py holds the instruction spec and the boundary parse at one scope

```
Status:   open
Progress: 0 of 6 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-30 (2026-08-30, Roy ruling on a review finding that mark.py announces
          four subjects at one scope: pull out the leaves out of mark.py)
Updated:  2026-08-30 — Task 6 was the only question owed and Roy answered it 2026-08-30:
          two definitions with different jobs, the whitespace difference deliberate. It
          is now an update box.
```

## Objective

`desk/mark.py` holds the instruction spec and the boundary parse at one scope.

!! **RULED 2026-08-30 -- `decision-log.md Process: #59`.** Roy, asked whether the module's
four subjects warranted a split: *"Yes pull out the leaves out of mark.py"*

! It is the same shape as `Process: #54` -- the mark answers for ITSELF and the collator
answers for the SET -- applied one level down, inside the mark's own file.

## The two subjects

| the SPEC -- what the instructions ARE | the PARSE -- whether one document conforms |
| --- | --- |
| `Instruction`, `Shape`, `QUERY_SHAPES` | `Mark`, `ROLE_FIELDS`, `filled` |
| `Row`, `INSTRUCTIONS`, `allowed()` | `parse`, `untouched` |
| `ANCHOR_NAME`, `ANCHOR_EXAMPLE` | `_claim_problems`, `_source_problems`, `_change_problems`, `_destination_problems` |

! **THE SEAM IS VISIBLE IN WHO IMPORTS WHAT.** `scripts/render_brief.py` wants the table
and nothing else; `tests/gates/test_mark_shape.py` reads the spec's own headings. Both
currently reach into the module that also holds the parse.

! **THE PROPOSED SEAM IS NOT THE RULING.** Roy ruled that the leaves come out; which module
they land in, and what it is called, is this file's work and its review's. The table above
is a starting reading of the file, not a decision.

## The two backtick patterns are TWO DEFINITIONS, and the split is where that gets said

!! **RULED 2026-08-30.** Asked whether `ANCHOR_NAME` and `binder/annotate.py`'s `TICKED`
should be one definition, Roy: *"annotate.py was about finding references in documentation
for the agents. It was about building an index like you would find in the back of a book. I
had to be looser with the answer than other thing because Spaced out words or not could have
been used in doc strings"*

**They answer different questions, so a shared pattern would have been the defect:**

| | asks | lives in |
| --- | --- | --- |
| `TICKED` | what does this documentation REFER to -- the back-of-book index the agents read | `binder/annotate.py` |
| `ANCHOR_NAME` | did this role NAME a declaration when it filed an `add` | `desk/mark.py` |

! **THE PATTERNS DIFFER ON WHITESPACE AND NEITHER IS WRONG.** `ANCHOR_NAME` is
`` `[^`\s][^`]*` `` -- whitespace legal after the first character; `TICKED` is
`` `([^`\s]+)` ``. What is missing is not agreement but **a sentence in each saying which
question it answers**, so the next reader does not find two backtick regexes and assume one
of them drifted.

! **THIS FILE OWNS SAYING IT because `ANCHOR_NAME` moves in the split.** The vocabulary
belongs to no lane, and a lane that notices a split updates the other side in the same
change -- `conventions.md`, *The vocabulary is shared*.

## Tasks

- [ ] Implement the extraction of the instruction SPEC -- `Instruction`, `Shape`,
      `QUERY_SHAPES`, `Row`, `INSTRUCTIONS`, `allowed()`, `ANCHOR_NAME` and
      `ANCHOR_EXAMPLE` -- into its own module under `desk/`, leaving `mark.py`
      holding the `Mark` type and the boundary parse. Verify: `mark.py` imports
      the spec rather than defining it; `uv run ty check src/comment_review/`
      passes and `uv run pytest -q` reports the same counts as before the move.
- [ ] Update `scripts/render_brief.py` to import the classifier table from the
      spec module. Verify: it no longer imports from the module holding the parse,
      and the rendered brief is byte-identical to its pre-split output.
- [ ] Update `tests/gates/test_mark_shape.py` to read the spec at its new home.
      Verify: the gate passes, and goes red when a row is deleted from the table.
- [ ] Update `docs/lanes.md` and `docs/the-mark.md` wherever either names the
      file. Verify: no document names a path that does not exist, checked with `uv
      run python scripts/dead_sweep.py --links`.
- [ ] Delete the inline restatements of `filled()` at their call sites so the
      predicate is called rather than repeated. Verify: the inline form appears
      nowhere in `desk/`, and the suite stays green.
- [ ] Update `ANCHOR_NAME` and `binder/annotate.py`'s `TICKED` so each states
      the question it answers -- the anchor a role NAMED, against the
      back-of-book index of what documentation REFERS to. RULED 2026-08-30:
      two definitions, not one; the whitespace difference is deliberate.
      Verify: neither pattern changes, both carry the sentence, and
      `docs/vocabulary.md` records that two backtick forms exist on purpose.
