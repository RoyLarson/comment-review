# The original range leaves 105 blank lines owned by nothing, and 25 blanks go to an a

```
Status:   open
Progress: 6 of 12 tasks done
Owner:    session
Requires-Roy: true
Raised:   2026-08-20 (Roy, 2026-08-20: 'on the original every line belongs to 1
          paragraph and every paragraph belongs to 1 anchor')
Done:     2026-08-20 — 2026-08-20 -- landed in 5fd5baf. `b` owns every line that is not
          an `a` or a `c`, on BOTH ranges. Measured over the 16 shipped scripts: 105
          lines in no paragraph became 0, and the 25 that were going to a module
          docstring go to the `b` instead. ! Ownership is by PRECEDENCE, not by non-
          overlapping ranges -- a `b`'s span may cross an `a` without owning its lines,
          which is what keeps `(start, end)` sufficient. ! `fill_the_gaps` is now the
          single place that divides a gap. ! The galley half Roy named -- strip empty
          lines at the ends of a `b` on write, then put one back for spacing -- is NOT
          done and stays with the galley work.
```

## Objective

The original range leaves 105 blank lines owned by nothing, and 25 blanks go to an a.

## Tasks

- [x] !! MEASURED over the 16 shipped scripts. On the ADDRESSING range
      (`start`/`end`) the invariant HOLDS: 0 lines in no paragraph, 0 in two. On
      the ORIGINAL range it fails on 105 lines in 16 of 16 files, and every one is
      BLANK -- the blanks at the EDGES of a gap.
- [x] The divergence is deliberate and its reason is now overridden.
      `fill_the_gaps`: *'It moves the ADDRESSING range only ... widening those
      would let a change swallow the blank line that separates a comment run from
      the code beneath it.'* Roy, 2026-08-20: *'we can write a rule on the galley
      that strips empty lines at the ends of bs and then puts one back in to make
      the spacing nice, but the original lines need to be marked as bs because it
      has this flexibility that the others do not.'*
- [x] !! WHY `b` AND NOT NOBODY. Roy: *'else a literal two paragraph comment is
      held by nothing and cannot have its internal paragraphs merged or dropped
      appropriately in the edit process.'* A comment run's INTERNAL blank is
      already inside its paragraph -- measured, `b2` spans '# First para.' / '' /
      '# Second para.'. It is the blanks at the gap's EDGES that are lost.
- [x] !! AND 25 OF THE 105 GO TO AN `a`, NOT A `b`. `fill_the_gaps` extends
      whichever paragraph STARTS the gap, so a module docstring takes the blank
      line beneath it. Under the ruling an `a` must not: it has none of the
      flexibility that makes the widening safe. 80 of 105 go to a `b` correctly.
- [x] ! BOTH ARE ONE FIX. `empty_places` collapses a gap to an insert as soon as
      ANY line in it is filled: `if any(low <= n <= high for n in filled): high =
      low - 1`. Trimming to the UNFILLED REMAINDER instead puts a `b` on the
      blank, which then owns it and leaves the `a` alone.
- [x] Blast radius to check before landing: `raw_lines` must grow with the range
      or `galley.paragraph_matches` refuses a fresh census; `splice_range` reads
      the original range; and `docs/addressing.md` states the current rule.
- [ ] * THE GALLEY HALF, which Roy named and which is not this TODO: strip empty
      lines at the ends of a `b` on write, then put one back for spacing. Deferred
      with the rest of the galley work.
- [ ] !! MINE, 2026-08-21, AND IT SETS PROSE TWICE. `fill_the_gaps` computes a
      `b`'s FREE lines -- excluding every line an `a`, `c` or `f` owns exactly --
      and then `recut` slices `source[start - 1 : end]` over the WHOLE span
      anyway. A `b` whose free lines are not CONTIGUOUS therefore swallows the
      paragraph sitting inside it.
- [ ] MEASURED on `corpora/cpython/Include/floatobject.h`, which opens with a
      BLANK line: `f0` holds line 2 (`/* Float object interface */`) and `b0`
      holds 1-7, so the comment appears in both and the compositor sets it twice.
      9 files of 699, all the same shape -- a file whose front matter is not on
      line 1.
- [ ] ! IT WAS UNREACHABLE BEFORE THE MATTER RULE. Front matter resolved only in
      Python and only above a module docstring, so an `f` place never sat inside a
      gap with a blank above it. The rule going positional is what made the shape
      common.
- [ ] * RULING WANTED: WHO OWNS A BLANK LINE ABOVE FRONT MATTER. Giving it to `f0`
      keeps the tiling total and reads as the file's own head. Leaving it to the
      `b` cannot work -- a `b` is contiguous, and the compositor sets places in
      order, so a `b` owning lines 1 and 3-7 around an `f0` at 2 would set line 1
      AFTER line 2.
- [ ] ! THE INVARIANT AT STAKE is that the page TILES its file: every line belongs
      to exactly one place. That is what makes the compositor total, and this is
      the only measured shape that breaks it.
