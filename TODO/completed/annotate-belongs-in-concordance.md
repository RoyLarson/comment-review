# `annotate.py` resolves references and sits in `binder/`, not `concordance/`

```
Status:   open
Progress: 3 of 3 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-28 (2026-08-28, Roy: 'File a todo to put this as part of concordance -
          src/comment_review/binder/annotate.py')
Measured: 2026-08-28 — 2026-08-28, Roy: *"probably has duplicated logic in both
          `referrers.py` and `code_?.py`"*. MEASURED, and there are TWO overlaps of
          different weight. (1) FIXED THE SAME DAY: `NAMED_DEFS` was defined verbatim in
          BOTH `reading/lexer.py:297` and `concordance/referrers.py:23`, while
          `concordance/code_names.py` IMPORTED it from the lexer -- so two modules in
          one package disagreed about where the tuple came from. Adding a member to the
          lexer's tuple would have carried `code_names` and silently not `referrers`,
          with no error and no type complaint. `referrers` now imports it; `decision-
          log.md Process: #38` is the same argument about an enum member. (2) STILL
          OPEN, and it is the one this file is for: `referrers.tokens_for` and
          `code_names.code_names` each `ast.parse` a Python file inside `except
          exceptions.PARSE_ERRORS`, each seed their result with the file's `stem`, and
          each collect definition names by `isinstance(node, NAMED_DEFS)`. What DIFFERS
          is only the policy on top -- `referrers` walks `tree.body` and keeps PUBLIC
          top-level names, `code_names` walks `ast.walk` and keeps names, attributes,
          args, aliases and constants too. ! SO THE SHARED PART IS *parse a Python file
          and yield its definitions, or say why not*, and the two callers differ in what
          they then keep. `annotate.py` is NOT part of this overlap: it is regex over
          PROSE and parses no Python -- it is the CONSUMER of what these two harvest,
          which is the argument for it moving into the same package rather than for
          merging it with them.
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

- [x] T1 | FINISHED, already done -- annotate.py moved to concordance/ 3c66c56, 2026-08-31 | 3c66c56 | Move
      `src/comment_review/binder/annotate.py` to
      `src/comment_review/concordance/`. Verify: nothing imports it from
      `binder`, the suite passes, and `build_plugin.py --check` is green.
- [x] T2 | FINISHED -- concordance/__init__.py already said why; binder/__init__.py corrected | f9b2ba2 | Say
      why each area holds what it holds, where the move makes the boundary
      arguable. `CLAUDE.md` calls `binder/` the pages and their places;
      `concordance/` already holds `referrers.py`, and a concordance is an index
      of where things appear. Verify: the areas' `__init__` docstrings agree
      with where the file now is, and neither claims the other's subject.
- [x] T3 | FINISHED -- remaining binder/annotate.py mentions in src/tests are historical past tense | f9b2ba2 | Update
      every reference to the old path. Verify: `grep -rn
      'binder/annotate\\|binder.annotate'` returns nothing outside `prototype/`,
      `docs/history.md` and a quoted ruling.
