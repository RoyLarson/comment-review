# A place at line 0 is unreachable by every line-based lookup

```
Status:   open
Progress: 0 of 5 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-19 (the seven-agent address review, 2026-08-19)
```

## Objective

A place at line 0 is unreachable by every line-based lookup.

## Tasks

- [ ] !! **`locator.at` can never return a zero-width gap or an undocumented
      declaration.** Measured on `locator.py`'s own census: 61 of 158 blocks are
      at 0-0. Asked where prose goes above a line, it returns the `margin` BESIDE
      it -- so a compliant reviewer files an above-the-code `add` at a beside
      address.
- [ ] !! **An `add` above an ordinary statement inside a function body has NO
      sanctioned route.** `--anchor --series b` answers only for a DECLARATION's
      gap; the locator cannot reach the place; and `reviewer-brief.md` says *"ASK
      FOR THE ADDRESS. DO NOT COUNT."* This is the most common `add` site in the
      system's own remit.
- [ ] **`--anchor --series b|c` is wrong for a declaration on line 1** --
      `for_anchor` tests `end == at - 1`, which is `end == 0`, and every empty
      place matches. Measured: four answers where one was wanted.
- [ ] **`--anchor --series b|c` silently answers for the FIRST of two same-named
      declarations.** `at = next(...)` takes one. Real in shipped code --
      `census.py` has two nested `flush`. The `a` series is correct; `b`/`c`
      under-report with no signal, and the docstring claims `--check` reports it.
- [ ] **The listing sorts by line, so every line-0 place floats to the top of its
      file** -- measured 9 of 22 rows out of source order, with `@b0` printing
      after `@a4`. `--filtered` then presents scattered gaps as one contiguous run
      (`@b0..b8`) with a `0-0` span.
