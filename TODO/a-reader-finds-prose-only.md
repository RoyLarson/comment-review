# A reader finds prose and rebuilds nothing after it

```
Status:   open
Progress: 0 of 3 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-25 (decision-log.md Process: #224)
```

## Objective

A reader supplies what only parsing can find -- each paragraph's span, its raw
lines, its kind and its anchor. Everything that follows from those is derived
once for every language: `Paragraph` derives its own fields, the page places it,
and the addresser addresses it, as they did for Python before the lexical
readers. decision-log.md Process: #224.

Measured 2026-10-25: the lexer (`_join`), the Python reader
(`reading/python/projection.py`) and the Rust reader
(`reading/rust/projection.py`) each build `Paragraph.text` their own way, and
the Python and Rust readers stamp `address` themselves. `lines` was the same
defect and is repaired (lexer-and-language-findings T12, b30cc510).

## Tasks

- [ ] T1 | Derive Paragraph.text in one place for every reader
        > 2026-10-25 Check: one comment in .py, .rs and .go reads the same text
        > 2026-10-25 Check: no reader passes text to Paragraph
- [ ] T2 | Assign each paragraph's address in the page instead of in a reader
        > 2026-10-25 Check: git grep finds no address= in reading/python or reading/rust
- [ ] T3 | List each Paragraph, Page or Addresser duty a reader still performs
        > 2026-10-25 Check: each duty is a task on this file naming its file:line
