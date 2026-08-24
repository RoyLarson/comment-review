# A place at line 0 is unreachable by every line-based lookup

```
Status:   open
Progress: 4 of 6 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-19 (the seven-agent address review, 2026-08-19)
Measured: 2026-08-19 -- tasks 1-4 verified done 2026-08-19: locator.py:96 matches
          start==0 and original_start==line, and for_anchor's direct path answers one place
          per series for a line-1 declaration and BOTH of two same-named ones. Task 5
          stands and is worse than filed -- 63 of 164 places on locator.py's own census
          float to the head of the file as one fabricated run '@b1..b80' spanning 0-0.
RE-MEASURED: 2026-08-23 -- 2026-08-23, still live, and the numbers moved. On
             tests/fixtures/sample.py the census now floats 7 of 18 rows to the top of
             the file, every one with a 0-0 span: f0, f1 (front/back matter) then b0,
             b2, b3, b4, b5. The rest print in source order from line 1. ! The recorded
             symptom has INVERTED -- the TODO says '@b0 printing after @a4'; today @b0
             prints BEFORE @a0. The cause is the same (a zero span sorts first) but the
             example no longer reproduces as written, and the front-matter series did
             not exist when this was measured.
TRIAGED:  2026-08-23 -- `locator.py` NO LONGER EXISTS. Tasks 1-4 name it and are already
          ticked, so they stand as the record of a module that is gone;
          `docs/plans/0.2.4-rework-the-foliator-owns-the-address.md:66` states why --
          *"`locator.py` answered where do I insert text, the question the address
          system removed"*. ! WHAT SURVIVES IT IS TASK 5, and it is not about the
          locator at all: it is the ORDER the census prints its own rows in, which is
          still live and was re-measured today with a second symptom the file never
          recorded.
```

## Objective

!! **AN EMPTY PLACE SITS AT LINE 0 BY RULING, AND THE LISTING SORTS BY LINE.** So every place
an `add` exists to cite floats above the file it belongs to, in a listing whose job is to let a
reviewer find where prose goes.

MEASURED 2026-08-23, `census.py --repo . tests/fixtures/sample.py`: **7 of 18 rows print before
line 1**, each with a `0-0` span -- `f0`, `f1`, then `b0`, `b2`, `b3`, `b4`, `b5`. The remaining
eleven print in source order. ! The symptom recorded in 2026-08-19 has INVERTED: this file says
*"`@b0` printing after `@a4`"*; today `@b0` prints BEFORE `@a0`. The cause is unchanged -- a
zero span sorts first -- and the `f` series did not exist when the original example was written.

!! **AND `--filtered` MAKES A RUN THAT DOES NOT EXIST.** Same file, same day:
`census.py --filtered` prints one row reading `3-7  @b0..b5  0-0  no-prose  0L  5-intervals`.
Five separate places are presented as one contiguous run, **and `b1` is named by the range while
being excluded from it** -- `b1` is a real 2-line comment at lines 4-7, printed on its own row
below. A reviewer reading `@b0..b5` as a span reads a place into it that is not there.

! **The locator half of this file is history.** `locator.py` was the second tool that answered
by line and it no longer exists; tasks 1-4 record what it did wrong and stay ticked so the
error remains legible.

## What the ticked boxes recorded

**T1.** !! **`locator.at` can never return a zero-width gap or an undocumented declaration.**
Measured on `locator.py`'s own census: 61 of 158 blocks are at 0-0. Asked where prose goes above a
line, it returns the `margin` BESIDE it -- so a compliant reviewer files an above-the-code `add`
at a beside address. ! `locator.py` no longer exists; kept as the record.

**T2.** !! **An `add` above an ordinary statement inside a function body has NO sanctioned route.**
`--anchor --series b` answers only for a DECLARATION's gap; the locator cannot reach the place; and
`reviewer-brief.md` says *"ASK FOR THE ADDRESS. DO NOT COUNT."* This is the most common `add` site
in the system's own remit.

**T3.** **`--anchor --series b|c` is wrong for a declaration on line 1** -- `for_anchor` tests
`end == at - 1`, which is `end == 0`, and every empty place matches. Measured: four answers where
one was wanted.

**T4.** **`--anchor --series b|c` silently answers for the FIRST of two same-named declarations.**
`at = next(...)` takes one. Real in shipped code -- `census.py` has two nested `flush`. The `a`
series is correct; `b`/`c` under-report with no signal, and the docstring claims `--check` reports
it.

## Tasks

- [x] T1 -- `locator.at` could never return a zero-width gap or an undocumented
      declaration; it answered with the `margin` beside the line. Kept as the record.
- [x] T2 -- An `add` above an ordinary statement inside a function body had NO sanctioned
      route, and it is the most common `add` site in the system's own remit.
- [x] T3 -- `--anchor --series b|c` was wrong for a declaration on line 1: every empty
      place matched `end == at - 1`, giving four answers where one was wanted.
- [x] T4 -- `--anchor --series b|c` silently answered for the FIRST of two same-named
      declarations, with no signal that a second existed.
- [ ] T5 -- Print each place where it belongs, not where its span sorts. Verify: on
      `sample.py` `@b0` prints above `@a0`'s anchor, and no `0-0` row sorts first.
- [ ] T6 -- Stop `--filtered` collapsing scattered places into a range naming a place it
      excludes. Verify: it lists the addresses, or names a range holding only those.
