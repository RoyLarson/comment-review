# A line-numbered address is not stable under the edits this tool makes

```
Status:   CLOSED 2026-08-18
Progress: 6 of 6 tasks done
Owner:    session (the ruling was made 2026-08-18; the addresser is the answer)
Requires-Roy: false
Raised:   2026-08-18 (Roy, 2026-08-18, from two files differing only in comments)
```

## Objective

!! **TWO FILES DIFFERING ONLY IN COMMENTS DO NOT AGREE ON WHERE THE CODE IS.** Roy,
2026-08-18: *"both of the examples should have the same address for the code lines."*
They do not, and the census says so:

```python
# a.py                                          # b.py
my_code_is_awesome ="awesomeness"  # I know     my_code_is_awesome = "awesomeness"
# I like typing but                             my_goals_are_even_better = "Yeah for me!"
# I like things getting done
# more
my_goals_are_even_better = "Yeah for me!"  # Still working
```

```
a.py:1-2  interval             b.py:1-2  interval
a.py:2-2  trailing-comment     b.py:2-3  interval
a.py:3-5  comment  3L          b.py:3-3  interval
a.py:6-6  trailing-comment
a.py:6-6  interval
```

The same two statements sit at lines **2 and 6** in one file and **2 and 3** in the other.

!! **AND THE STRUCTURE CHANGES, not only the numbers.** In `b.py` the gap between the two
statements is one interval, `b.py:2-3`. In `a.py` there is NO interval between them at all --
prose fills it, so the gap is a comment block. Nothing can say the two files name the same
place, because in one of them the place is not the same KIND of thing.

## Why it matters HERE and not in general

**This tool's job is editing prose, and every prose edit moves the line numbers of the code
below it.** So an address is valid only for the exact file state its census was built from.
Four things depend on that and none of them says so:

- **After WRITE**, every address below the first edit is stale. `galley.splice` already
  applies edits in DESCENDING line order for exactly this reason -- the problem is known one
  layer down and unstated one layer up.
- **A re-review at 5b and 6b** is asked to hold or revise after stage 5 and 6 have rewritten
  prose, which has already moved the addresses it was given.
- **A harness comparing two versions** -- a fixture at one commit graded against its fix --
  cannot pair findings by address. That is the REGRESSION and KNOWN MISS case shape in
  [`the-harness-cannot-run-the-system-it-grades`](the-harness-cannot-run-the-system-it-grades.md),
  and both compare two versions by construction.
- **`move`'s destination** names a place that the run's own edits shift while it is being
  applied.

! **THE STABLE FORM IS ALREADY IN THE RECORD.** An `add` carries
`{"anchor": "`send()`", "side": "above"}` -- a declaration and a side, which survive any
number of lines moving above them. What is unruled is whether that pair becomes THE address
and `path:start-end` demotes to a cursor into one snapshot, or whether the two coexist.

! **Not a defect in the census.** Line numbers are the right answer to "where is this in the
file I just read"; they are the wrong answer to "which place is this, across two files".
The census was never asked the second question, and now four callers ask it.

## Tasks

- [x] * **RULED 2026-08-18: the `a`/`b`/`c` scheme in `addresser.py` IS the stable
      address, and `path:start-end` stays as the READER'S CURSOR.** `anchor`+`side`
      was a partial answer -- it existed only for `add`, named only a declaration,
      and had nothing to say about a gap or a trailing comment. The addresser
      covers every place: `a` a declaration, `b` a gap, `c` an on-line position.
      ! Neither replaces the other. A reviewer reads a file and a line number is
      what it has in hand; a RECORD should carry the stable form, because only
      that survives the run's own edits.

- [x] **MEASURED 2026-08-18, and the prediction held.** A prose-only edit -- one
      docstring grown by three lines, no code touched:

      ```
      kind        line addr before   after     stable
      docstring   1-1                1-1       b0 -> b0
      docstring   6-6                6-9       b2 -> b2
      comment     11-11              14-14     b4 -> b4
      ```

      **2 of 3 line addresses moved; 0 of 3 stable addresses did.** ! And the two
      that moved are exactly those at or below the edit, which is the claim: the
      count is a function of where the EARLIEST edit lands, not of how many edits
      there were.

- [x] **STATED where the address is defined.** `census.address` now says it is
      true of ONE FILE STATE ONLY, carries the measurement above, and points at
      the addresser for the other question.

- [x] **ALREADY IN PLACE, and now the reasoning is written down.**
      `references/re-review.md` rules it: *"Cite the galley census, and do not
      carry a round-1 index into round 2."* A re-review is handed a FRESH census
      of the galley, so a stale address never reaches it -- the addresses it cites
      describe the file as 5b and 6b actually find it.

- [x] **ANSWERED by the addresser.** A harness pairs findings across two versions
      by their STABLE address: `b1` is the same place in a file with the prose and
      in the file without it, which is what a REGRESSION case and a KNOWN MISS
      case both need. ! Line addresses cannot do it -- the fix commit moves them
      by construction. See
      [`the-harness-cannot-run-the-system-it-grades`](the-harness-cannot-run-the-system-it-grades.md).

- [x] **MOVED, not dropped: the enumeration gap belongs with the series that
      closes it.** Every gap is enumerated; an ON-LINE position is an entry only
      where a trailing comment already sits, so an `add` of a trailing comment to
      a line that has none still cannot be cited. **Measured 2026-08-18 over 13
      shipped scripts: a full `c` series would add 2,894 entries to 2,987 -- it
      would nearly DOUBLE the census**, where the whole `b` series costs 2,587
      for a much commoner verdict. That is a cost decision, not a stability one,
      and it now sits with
      [`docstrings-need-their-own-address-series`](docstrings-need-their-own-address-series.md),
      which settles the same question for declarations.
