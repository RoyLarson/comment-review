# The original range leaves 105 blank lines owned by nothing, and 25 blanks go to an a

```
Status:   open
Progress: 0 of 7 tasks done
Owner:    session
Requires-Roy: true
Raised:   2026-08-20 (Roy, 2026-08-20: 'on the original every line belongs to 1
          paragraph and every paragraph belongs to 1 anchor')
```

## Objective

The original range leaves 105 blank lines owned by nothing, and 25 blanks go to an a.

## Tasks

- [ ] !! MEASURED over the 16 shipped scripts. On the ADDRESSING range
      (`start`/`end`) the invariant HOLDS: 0 lines in no paragraph, 0 in two. On
      the ORIGINAL range it fails on 105 lines in 16 of 16 files, and every one is
      BLANK -- the blanks at the EDGES of a gap.
- [ ] The divergence is deliberate and its reason is now overridden.
      `fill_the_gaps`: *'It moves the ADDRESSING range only ... widening those
      would let a change swallow the blank line that separates a comment run from
      the code beneath it.'* Roy, 2026-08-20: *'we can write a rule on the galley
      that strips empty lines at the ends of bs and then puts one back in to make
      the spacing nice, but the original lines need to be marked as bs because it
      has this flexibility that the others do not.'*
- [ ] !! WHY `b` AND NOT NOBODY. Roy: *'else a literal two paragraph comment is
      held by nothing and cannot have its internal paragraphs merged or dropped
      appropriately in the edit process.'* A comment run's INTERNAL blank is
      already inside its paragraph -- measured, `b2` spans '# First para.' / '' /
      '# Second para.'. It is the blanks at the gap's EDGES that are lost.
- [ ] !! AND 25 OF THE 105 GO TO AN `a`, NOT A `b`. `fill_the_gaps` extends
      whichever paragraph STARTS the gap, so a module docstring takes the blank
      line beneath it. Under the ruling an `a` must not: it has none of the
      flexibility that makes the widening safe. 80 of 105 go to a `b` correctly.
- [ ] ! BOTH ARE ONE FIX. `empty_places` collapses a gap to an insert as soon as
      ANY line in it is filled: `if any(low <= n <= high for n in filled): high =
      low - 1`. Trimming to the UNFILLED REMAINDER instead puts a `b` on the
      blank, which then owns it and leaves the `a` alone.
- [ ] Blast radius to check before landing: `raw_lines` must grow with the range
      or `galley.paragraph_matches` refuses a fresh census; `splice_range` reads
      the original range; and `docs/addressing.md` states the current rule.
- [ ] * THE GALLEY HALF, which Roy named and which is not this TODO: strip empty
      lines at the ends of a `b` on write, then put one back for spacing. Deferred
      with the rest of the galley work.
