# The addressed unit of prose is a passage, not a paragraph

```
Status:   open
Progress: 0 of 9 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-18 (roy)
```

## Objective

The unit of prose a page is made of -- a comment run, a docstring, or the empty
place either could go, answering to exactly one address -- is a `passage`.
Everywhere the system uses `paragraph` for that unit, it says `passage`.

`paragraph` keeps its ordinary English meaning: a paragraph of prose inside a
comment or docstring. A passage can hold several paragraphs, and only the
term-of-art uses change.

Before: `class Paragraph`, `reading/paragraph.py`, a binder's `"paragraphs"`
key, and "one paragraph per address" in the agent prose.

After: `class Passage`, `reading/passage.py`, `"passages"`, and "one passage per
address". A comment saying "this paragraph explains the cap" in plain English
stays as it is.

Measured 2026-10-18 with `git grep -i -c -w -E 'paragraphs?'`, counting both
senses: 736 uses in 57 files under `src/comment_review`, 88 in 8 under
`src/plugin`, 439 in 53 under `tests`, 531 in 60 under `docs`, 114 in 7 under
`scripts`. Dated records -- `docs/history.md`, `docs/decision-log.md`,
`docs/plans/`, `docs/superpowers/` -- stay as written.

## Tasks

- [ ] T1 | Rename the `paragraph` term to `passage` in `vocabulary.toml`
- [ ] T2 | Move `paragraph` to the retired terms in `docs/vocabulary.md`
- [ ] T3 | Rename `reading/paragraph.py` to `reading/passage.py`
- [ ] T4 | Rename `Paragraph` and each identifier naming the unit to `passage`
- [ ] T5 | Rename the binder's `paragraphs` wire key to `passages`
- [ ] T6 | Rename the term in the agent prose under `src/plugin`
- [ ] T7 | Rename the term in the tests
        > 2026-10-18 Also: a retired-noun `block` in tests becomes `passage` too
        > 2026-10-18 Keep live senses: verb, code block, block comment, BLOCK marker
- [ ] T8 | Rename the term in the live docs
        > 2026-10-18 Also: retired `block` in addressing/parsing.md becomes passage
        > 2026-10-18 limitations.md is agents-lane: name the lane and ask first
- [ ] T9 | Retire `paragraph` as a term in the vocabulary gate, keeping its
      English sense
