# A place at line 0 is unreachable by every line-based lookup

```
Status:   open
Progress: 4 of 5 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-19 (the seven-agent address review, 2026-08-19)
Measured: 2026-08-19 — tasks 1-4 verified done 2026-08-19: locator.py:96 matches
          start==0 and original_start==line, and for_anchor's direct path answers one place
          per series for a line-1 declaration and BOTH of two same-named ones. Task 5
          stands and is worse than filed -- 63 of 164 places on locator.py's own census
          float to the head of the file as one fabricated run '@b1..b80' spanning 0-0.
RE-MEASURED: 2026-08-23 — 2026-08-23, still live, and the numbers moved. On
             tests/fixtures/sample.py the census now floats 7 of 18 rows to the top of
             the file, every one with a 0-0 span: f0, f1 (front/back matter) then b0,
             b2, b3, b4, b5. The rest print in source order from line 1. ! The recorded
             symptom has INVERTED -- the TODO says '@b0 printing after @a4'; today @b0
             prints BEFORE @a0. The cause is the same (a zero span sorts first) but the
             example no longer reproduces as written, and the front-matter series did
             not exist when this was measured.
```

## Objective

!! **AN EMPTY PLACE SITS AT LINE 0 BY RULING, AND BOTH TOOLS THAT ANSWER BY LINE FILTER ON
`start <= line <= end`.** So the places an `add` exists to cite are exactly the ones no line
lookup can name -- while `reviewer-brief.md` forbids the only route left: *"ASK FOR THE ADDRESS.
DO NOT COUNT."*

Measured 2026-08-19 on `locator.py`'s own census: **61 of 158 blocks are at 0-0**. Asked where
prose goes above a line, the locator returns the `margin` BESIDE it -- so a compliant reviewer,
told *"The SIDE is the address's to say, never yours"*, files an above-the-code `add` at a
beside address.

!! **THE MOST COMMON `add` SITE IN THE SYSTEM'S OWN REMIT HAS NO SANCTIONED ROUTE.** A comment
above an ordinary statement inside a function body: `--anchor --series b` answers only for a
DECLARATION's gap, the locator cannot reach the place, and counting is forbidden.

! Two further defects in `for_anchor` come from the same ruling: a declaration on **line 1**
matches every empty place in the file (`end == at - 1` becomes `end == 0`), and two declarations
sharing a NAME silently answer for the first -- real in shipped code, where `census.py` has two
nested `flush`.

! And the listing sorts by line, so every line-0 place floats to the top of its file -- measured
9 of 22 rows out of source order, with `@b0` printing after `@a4`.

## Tasks

- [x] !! **`locator.at` can never return a zero-width gap or an undocumented
      declaration.** Measured on `locator.py`'s own census: 61 of 158 blocks are
      at 0-0. Asked where prose goes above a line, it returns the `margin` BESIDE
      it -- so a compliant reviewer files an above-the-code `add` at a beside
      address.
- [x] !! **An `add` above an ordinary statement inside a function body has NO
      sanctioned route.** `--anchor --series b` answers only for a DECLARATION's
      gap; the locator cannot reach the place; and `reviewer-brief.md` says *"ASK
      FOR THE ADDRESS. DO NOT COUNT."* This is the most common `add` site in the
      system's own remit.
- [x] **`--anchor --series b|c` is wrong for a declaration on line 1** --
      `for_anchor` tests `end == at - 1`, which is `end == 0`, and every empty
      place matches. Measured: four answers where one was wanted.
- [x] **`--anchor --series b|c` silently answers for the FIRST of two same-named
      declarations.** `at = next(...)` takes one. Real in shipped code --
      `census.py` has two nested `flush`. The `a` series is correct; `b`/`c`
      under-report with no signal, and the docstring claims `--check` reports it.
- [ ] **The listing sorts by line, so every line-0 place floats to the top of its
      file** -- measured 9 of 22 rows out of source order, with `@b0` printing
      after `@a4`. `--filtered` then presents scattered gaps as one contiguous run
      (`@b0..b8`) with a `0-0` span.
