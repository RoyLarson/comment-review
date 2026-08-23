# A code-less file leaves lines owned by no paragraph

```
Status:   open
Progress: 0 of 3 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-20 (the /code-review high of 2026-08-20)
Corroborated: 2026-08-21 — 2026-08-21 -- the xhigh review reached task 2 independently
              and measured the consequence. splitlines() splits on form feed, \x85 and
              U+2028/2029, so census line numbers disagree with the file's real lines: a
              form-feed page separator yields 5 entries where git and every editor see
              4, and the census reports a statement physically on line 4 as line 5. !
              desk.py checks citations against the SAME skewed list, so it is self-
              consistent -- but the reviewer reads the real file, which means a correct
              citation is refused and an off-by-one passes. ! galley.py splices by index
              into that list and splitlines() discards the form feed, so a rejoin drops
              the character.
```

## Objective

A code-less file leaves lines owned by no paragraph.

## Tasks

- [ ] `addresser.py:426`: on `"""Doc."""\n\n` or a whitespace-only file, lines are
      left owned by no paragraph -- the invariant Roy stated 2026-08-20, *"every
      line belongs to 1 paragraph"*, which the 2026-08-20 fix closed for files
      that HAVE code.
- [ ] `lexer.py:1160`: `splitlines()` splits on form feed where `tokenize` does
      not, yielding empty -- and therefore uncitable -- addresses.
- [ ] `census.py:343` catches bare `Exception` with the comment *"a parse failure
      is REPORTED, as a gap"*. Any bug in `page_for` degrades to a per-file gap
      rather than raising. Not a defect alone; it is WHY the front-matter
      destruction stayed quiet.
