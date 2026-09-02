# original_column is redundant and can be dropped entirely

```
Status:   open
Progress: 6 of 9 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-20 (Roy, 2026-08-20: 'the edit_column is an idea that can be dropped
          entirely. It was there because we did not have a way to identify the above
          line-of-code comments from the beside line-of-code comment. That is now
          resolved fully by the address system')
Updated:  2026-08-20 — waiting on the galley rewrite: dropping the field changes
          splice's tuple
UNBLOCKED: 2026-08-23 — 2026-08-23. THE GALLEY REWRITE LANDED AND THE BLOCKER IS GONE.
           `galley.py` is 477 lines holding `reset`, `_vacate` and `drifted`; there is
           no `splice`, no `paragraph_matches` and no `unanswerable`, and the word
           `original_column` does not occur in the file. Tasks 3, 4, 5 and 6 all named
           code that no longer exists and are SUPERSEDED. ! Five of six boxes were a
           measurement or an argument; the WORK -- delete the field -- was never
           written down, and is now the one open task.
Split:    2026-08-23 -- the one open box held three jobs (the reads, the writes and the
           docs) and is now three; the site citations and the standing checks moved
           into the Objective
```

## Objective

`original_column` is redundant with `anchor` and can be dropped entirely.

!! **MEASURED, and RE-MEASURED 2026-08-23.** `original_column == len(anchor) + 1` for every
paragraph carrying one:

```
this repo's python (plugins/ + scripts/ + tests/)   12,601 of 12,601, 0 disagreeing
tests/fixtures/sample.* -- all 18 languages            107 of 107,    0 disagreeing
```

The field carries nothing the anchor does not. `lexer.py:195-198` already says so: *"With
`anchor` holding the code, the two RECONSTRUCT that line: `anchor + raw_lines[0]` is what is on
disk."*

!! **AND KIND NOW ANSWERS WHAT IT WAS FOR.** A `c` is exactly `{trailing-comment, margin}` and an
`a` is `{docstring, undocumented}`; everything else is a `b`. Verified with zero exceptions after
the 2026-08-20 kind fix, so every remaining use of the column as a BOOLEAN becomes a membership
test.

**MEASURED 2026-08-23, every use in the shipped scripts** -- 14 mentions, of which 8 are code:

| site | what it does |
| --- | --- |
| `lexer.py:289` | the field declaration |
| `lexer.py:1148`, `:1743`, `page.py:524` | WRITE it, as `len(code) + 1` |
| `lexer.py:1583`, `page.py:276`, `:287`, `:334` | READ it -- **all four as a BOOLEAN** |

! **The whole-tree count is 64 occurrences today, 14 of them in `plugins/`.** That is what the
three boxes below have to drive to zero, across the code and then the docs.

! **THERE IS NO NUMERIC READ LEFT IN THE SHIPPED SCRIPTS.** The two the original filing named --
`galley.paragraph_matches` splitting the stored halves at `column - 1`, and `splice` keeping
`line[: column - 1]` as the head -- went with the galley rewrite. Roy, 2026-08-20: *"I think the
galley work becomes simpler because of this."* It already is.

! The reasoning this file filed against has also already been corrected in place.
`addresser._series_of` argued *"NOT from the kind, which would need a case per kind"*; that
function is gone, and `series_of` (`addresser.py:1059-1073`) now reads the series off the address
and says so: *"Inferring was meant to avoid a case per KIND, and reading the address avoids that
too."*

! **The docs did not follow the galley.** `docs/addressing.md:179` still says *"`galley.splice`
keeps `line[:original_column - 1]` and replaces the rest"* about a function that no longer
exists, and `:114` is the same shape.

! **THE DEFERRAL THAT IS NOW SPENT.** It was on the galley rewrite -- Roy, 2026-08-20: *"the
decision on ordering is all galley work coming up on how it resets the paragraphs ... it can
wait"*. It landed.

! **Every box below also carries this repo's standing check**: `uv run pytest -q` green.

## Tasks

- [x] T1 | FINISHED | unknown | T1 -- MEASURED, moved to the Objective:
      `original_column == len(anchor) + 1` for every paragraph carrying one,
      12,601 of 12,601 and 107 of 107, 0 disagreeing.
- [x] T2 | FINISHED | unknown | T2 -- MEASURED, moved to the Objective: kind
      answers what the column was for, so all four surviving reads in the
      shipped scripts are boolean.
- [x] T3 | FINISHED | unknown | T3 -- SUPERSEDED. `addresser._series_of` no
      longer exists, and the stale reasoning it carried has already been
      corrected in `series_of` (`addresser.py:1069-1071`).
- [x] T4 | FINISHED | unknown | T4 -- SUPERSEDED. Both numeric uses were
      `galley.paragraph_matches` and `splice`; neither exists. No numeric read
      of the column survives in `plugins/`.
- [x] T5 | FINISHED | unknown | T5 -- SUPERSEDED. `galley.unanswerable` does not
      exist; nothing requires the field to be present.
- [x] T6 | FINISHED | unknown | T6 -- SUPERSEDED. The deferral was on the galley
      rewrite, quoted in the Objective. It landed.
- [ ] T7 | T7 -- Replace the four boolean reads with a kind or series membership
      test. Verify: `addresser.py --check` reports UNADDRESSED and SHARED counts
      unchanged.
- [ ] T8 | T8 -- Remove the three writes of `original_column` and its field
      declaration. Verify: `grep -rn original_column plugins/ scripts/ tests/`
      comes back empty.
- [ ] T9 | T9 -- Correct `docs/addressing.md:114` and `:178-179`, which still
      describe `galley.splice` and `original_column`. Verify: neither name
      occurs in `docs/`.
