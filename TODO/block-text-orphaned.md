# block_text (reading/lexer.py) has had no caller since desk.py moved to prototype

```
Status:   open
Progress: 0 of 1 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-26 (the final simplify pass on feat/the-write-chain-of-command,
          2026-08-26)
```

## Objective

`block_text` (`src/comment_review/reading/lexer.py:457`) has no caller anywhere
under `src/`, `plugins/` or `tests/` -- MEASURED: `grep -rn block_text` over
those trees matches only the definition itself and its own docstring.
`prototype/original/desk.py` still calls it, but `prototype/` is reference
only and nothing imports it.

Its last real caller was `desk.as_block`, which existed continuously from the
function's introduction until commit `b50e7a4` ("the middle moves to
prototype/, and the new suite replaces the old one", 2026-08-25) deleted
`src/comment_review/desk/desk.py` wholesale -- `git log --follow -p --
src/comment_review/desk/desk.py` shows the import
`from comment_review.reading.lexer import block_text, language_for` removed in
that same diff.

Not this branch's to cut: it is orphaned code, and a cut needs its own
consideration rather than riding in on an unrelated pass.

## Tasks

- [ ] Decide whether to delete block_text or give it a caller, on its own
      consideration
