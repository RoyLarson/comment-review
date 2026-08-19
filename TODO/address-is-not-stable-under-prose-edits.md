# A line-numbered address is not stable under the edits this tool makes

```
Status:   open
Progress: 0 of 6 tasks done
Owner:    session * Roy (* 1 ruling -- whether the anchor pair becomes THE address)
Requires-Roy: true
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

- [ ] * **Rule whether `anchor`+`side` becomes THE address, or stays a second way
      to name a place.** ! It is already in the record for `add` -- an anchor
      naming a declaration in backticks plus a side -- so the vocabulary exists
      and the question is
      whether `path:start-end` demotes to a cursor into one snapshot.
- [ ] **Measure how many addresses a real run invalidates.** Take the cycle run,
      apply its edits, re-census, and count the blocks whose address moved. ! The
      claim to test is that everything below the FIRST edit shifts, which would
      make the count a function of where the earliest edit lands rather than of
      how many edits there were.
- [ ] **State the invariant where the address is DEFINED.** `census.address` now
      says the format names two different things; it does not say it names them
      only for one file state.
- [ ] **Decide what a re-review cites at 5b and 6b.** Stage 5 and 6 rewrite prose,
      so every address below an edit has moved by the time the filer is asked to
      hold or revise. ! Today the re-review is sent the block index, which
      survives -- confirm that and write it down, or the fix is already in place
      and only the reasoning is missing.
- [ ] **Decide how the harness matches a finding across two versions of a file.**
      A case pinned at one commit and graded against its fix cannot pair findings
      by address. ! This is the blocker under `the-harness-cannot-run-the-system-
      it-grades`'s REGRESSION and KNOWN MISS cases, both of which compare two
      versions.
- [ ] !! **HALF THE ADDRESS SPACE IS NOT ENUMERATED, which is the property the
      whole scheme rests on.** Measured 2026-08-18 on the two files above: every
      gap (`b0`, `b1`, `b2`) is a census entry in BOTH files, empty or not -- that
      is what the 2026-08-17 interval enumeration bought. But an ON-LINE position
      (`c1`, `c2`) is an entry only where a trailing comment already sits, so in
      the bare file it does not exist. ! The consequence is the one intervals were
      enumerated to fix: **an `add` of a trailing comment to a line that has none
      cannot be cited**, exactly as an `add` to an empty gap could not be before.
      Decide whether a code line without a trailing comment gets an entry, and
      what it costs -- one per code line is a bigger table than one per gap.
