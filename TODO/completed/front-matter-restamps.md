# Adding a module docstring restamps the comment run above it as front matter

```
Status:   open
Progress: 0 of 7 tasks closed
Owner:    session
Requires-Roy: false
Raised:   2026-08-19 (the python_edge_cases.md run, 2026-08-19)
```

## Objective

!! **THIS TOOL CAN CREATE THE ARRANGEMENT THE RULE WAS MEASURED ON.** `mark_front_matter` asks
one positional question -- is this a comment run ending before the module docstring starts -- and
never asks whether the prose is ABOUT THE FILE. So an `add` that fills `a0` silently restamps the
comment run above it as a licence header.

Measured on `tests/fixtures/python_edge_cases.md`, where the same run does both: the `b1` mark
introduces `N = 0`, the `a0` mark writes the module docstring beneath it, and on the finished
file that comment is `b0`, annotated `front-matter`. It is then dropped from `--filtered`, so no
role ever sees it again, and any edit proposed on it is auto-converted to a `query` by
`verdicts.py`.

! The positional rule was measured over five corpora, where **10 of 12 files with prose above a
module docstring carried the Apache header**, and inside a declaration it never happened at all
-- 0 of 2,579 docstrings. The rule was right about real code. It was never true that this system
could produce the arrangement itself.

!! **AND THE GENERAL CASE IS BIGGER THAN THIS ANNOTATION.** An ADDRESS is stable under a prose
edit -- the `a` series cannot renumber, because only a code change adds a declaration and 7b
proves this tool makes none. **Nothing makes the equivalent promise for an ANNOTATION**, and
`front-matter`, `continues-a-trailing-comment` and `doc-kind-unresolved` are all computed from
prose positions this tool moves. The same run flipped the second one too: a `c` edit put a
trailing comment on the line above a comment run, and the run was stamped as possibly the tail of
that sentence.

! What it reaches: round 2 re-censuses the galley, so a role re-reviews prose whose kind and
annotations changed under it; and stage 8 reads a page whose first comment run is absent from the
filtered view.

## Tasks

- [ ] T1 | !! `mark_front_matter` asks ONE POSITIONAL QUESTION -- is this a
      comment run ending before the module docstring starts -- and never asks
      whether the prose is ABOUT THE FILE. So prose a reviewer placed to
      introduce the first statement becomes a licence header the moment an `add`
      fills `a0`.
- [ ] T2 | Measured end to end: the run's own `a0` edit turned its own `b1` edit
      into front matter. On the finished file that prose is dropped from
      `--filtered`, so no role sees it again, and any edit on it is
      auto-converted to a `query` by `verdicts.py`.
- [ ] T3 | ! The positional rule was MEASURED on real corpora where the only
      prose above a module docstring WAS a licence -- 10 of 12 across five
      corpora. It was never true that this tool could CREATE that arrangement
      itself. It can.
- [ ] T4 | Narrow fix: decide front matter from the PROSE -- shebang, coding
      line, licence-shaped -- which `_SHEBANG` and `_CODING` already half do,
      rather than from position relative to a docstring.
- [ ] T5 | !! BROAD QUESTION, and the reason this is not just a bug: ANNOTATIONS
      ARE NOT STABLE UNDER THIS TOOL'S OWN EDITS. Addresses are -- `a` cannot
      renumber because only a code change adds a declaration, and 7b proves
      none. Nothing makes the equivalent promise for `front-matter`,
      `continues-a-trailing- comment` or `doc-kind-unresolved`, and all three
      are computed from prose positions this tool moves. Same run also flipped
      `continues-a-trailing- comment` onto a run because its own `c` edit landed
      above it.
- [ ] T6 | ! Round 2 re-censuses the galley, so a role re-reviews prose whose
      KIND and ANNOTATIONS changed under it, and stage 8 reads a page whose
      first comment run is invisible in the filtered view.
- [ ] T7 | !! AND THE SHEBANG/CODING BRANCH HAS NO POSITION GUARD AT ALL.
      `page.py:589` promises a rule that is *"POSITIONAL and deliberately
      narrow"*, but the `_SHEBANG`/`_CODING` test runs over EVERY comment in the
      file. Reported 2026-08-20: `# the wire format is coding: utf-8 here` on
      line 5 is stamped FRONT_MATTER, addressed `@b0`, and dropped from
      `Page.prose` -- so no reviewer ever sees it. With a real coding line
      present too, two paragraphs answer to `b0`. Same for a trailing comment.
