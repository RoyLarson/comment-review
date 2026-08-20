# The lexer emits a page kind, and its own docstring says it does not

```
Status:   open
Progress: 0 of 5 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-20 (the ownership-context sweep, 2026-08-20)
```

## Objective

The lexer emits a page kind, and its own docstring says it does not.

## Tasks

- [ ] !! `lexer.py` emits `kind="undocumented"` at line 990 -- a PAGE kind --
      twenty-two lines after its own docstring says 'a reader emits comment,
      docstring, trailing-comment and unparsed; interval, margin and undocumented
      are the page's, because only a page knows where prose is MISSING'.
- [ ] ! It is BOTH findings at once: `ownership-context` (`_undocumented` belongs
      to the page, which emits every other empty place in `empty_places`) and
      `block-context` (the docstring's claim is false of the code beneath it).
- [ ] The fix is the cut already identified when `empty_places` was written: the
      LEXER reports which lines declare something documentable AND where its
      docstring would go, and the PAGE emits the `a` places from that. Today
      `documentable` is a `set[int]` of code-line indices, which cannot carry the
      insert line -- and a wrapped signature means `def_line + 1` is wrong.
- [ ] ! Verify with the one-line `def f(): pass` case from `census-degrades-
      silently`: `body[0].lineno` is the `def` line, so the insert point is
      OUTSIDE the declaration. Both are the same missing fact.
- [ ] ! `lexer.py` also names `code_lines` and `OCCUPIES_NOTHING`, both defined in
      `page.py`, while its docstring says it imports no sibling. Those are cross-
      references and may be fine; check them once the kind is moved.
