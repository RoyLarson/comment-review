# `annotate.py` resolves references and sits in `binder/`, not `concordance/`

```
Status:   open
Progress: 0 of 3 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-28 (2026-08-28, Roy: 'File a todo to put this as part of concordance -
          src/comment_review/binder/annotate.py')
```

## Objective

`annotate.py` resolves references and sits in `binder/`, not `concordance/`.

## Tasks

- [ ] Move `src/comment_review/binder/annotate.py` to
      `src/comment_review/concordance/`. Verify: nothing imports it from `binder`,
      the suite passes, and `build_plugin.py --check` is green.
- [ ] Say why each area holds what it holds, where the move makes the boundary
      arguable. `CLAUDE.md` calls `binder/` the pages and their places;
      `concordance/` already holds `referrers.py`, and a concordance is an index
      of where things appear. Verify: the areas' `__init__` docstrings agree with
      where the file now is, and neither claims the other's subject.
- [ ] Update every reference to the old path. Verify: `grep -rn
      'binder/annotate\|binder.annotate'` returns nothing outside `prototype/`,
      `docs/history.md` and a quoted ruling.
