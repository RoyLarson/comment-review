# A code-less file leaves lines owned by no paragraph

```
Status:   open
Progress: 0 of 3 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-20 (the /code-review high of 2026-08-20)
```

## Objective

A code-less file leaves lines owned by no paragraph.

## Tasks

- [ ] `foliator.py:426`: on `"""Doc."""\n\n` or a whitespace-only file, lines are
      left owned by no paragraph -- the invariant Roy stated 2026-08-20, *"every
      line belongs to 1 paragraph"*, which the 2026-08-20 fix closed for files
      that HAVE code.
- [ ] `lexer.py:1160`: `splitlines()` splits on form feed where `tokenize` does
      not, yielding empty -- and therefore uncitable -- addresses.
- [ ] `census.py:343` catches bare `Exception` with the comment *"a parse failure
      is REPORTED, as a gap"*. Any bug in `page_for` degrades to a per-file gap
      rather than raising. Not a defect alone; it is WHY the front-matter
      destruction stayed quiet.
