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

**`annotate.py` is stage 3 -- FIND REFERENCES.** `CLAUDE.md` names it *"the resolution a reviewer
would otherwise do by hand"*: every reference each node makes, resolved -- paths, symbols, counts.

**That is the concordance's subject.** A concordance is an index of where things appear, and
`src/comment_review/concordance/` already holds `referrers.py`, which answers the inbound half of
the same question: which tracked files NAME the files under review.

! **`binder/` is where it sits today, and the binder is a different subject.** `CLAUDE.md`:
*"ONE FILE -- its paragraphs tied to the places on it"*, and the binder is what the gatherer hands
over -- pages and the places on them. **Resolving what a paragraph POINTS AT is not a fact about
where the paragraph SITS.**

! **The areas each announce ONE subject, which is what `module-context` asks of any module.** A
file whose subject belongs to a neighbouring area is the defect that role is named for, in this
system's own source.

## Not a rename, and not urgent

This is a MOVE with no behaviour change: nothing about what `annotate.py` computes is in question,
only which area declares it. ! The boundary is worth stating as the move lands -- `binder/` and
`concordance/` both touch a page's references, and a reader who cannot say why the split falls
where it does will put the next file on the wrong side.

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
