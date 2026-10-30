# One reader builder from each language's definition

```
Status:   open
Progress: 0 of 7 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-27 (Roy, 2026-10-27, decision-log #244)
```

## Objective

**One reader builder puts a language's reader together from its definition**
(decision-log #244).

Definitions stay per language; the machinery is shared. Today three readers each
carry their own: the lexical reader (`reading/lexer.py`), `reading/python/` and
`reading/rust/`. Shared already: the matter rule (`reading/matter.py`),
`Paragraph`, the page, the addresser and the compositor. Written once or three
times instead of once for all:

- cut by place, one paragraph per `a`/`c`/`f` (#242, #243): lexer only
- annotations as one unit (#238): lexer only (lexer-and-language-findings T51)
- which run documents which declaration: lexer `document_declarations`, Python `owner_at`,
  Rust records
- the unchanged-code proof: `stripped.py`, `python/preservation.py`, `rust/preservation.py`

Done when a rule of that kind is stated in one module and every installed
language reads through it, and Python and Rust are definitions plus the parts
only they need.

## Tasks

- [ ] T1 | Move the cut by place out of lexer.py into one step every reader
      passes
        > 2026-10-30 A3: take _partner with the cut; A6: lexer.py is 1763 lines
        > 2026-10-30 file_matter runs twice while docs are decided after the cut
- [ ] T2 | Write the design for the reader builder and its shared parts
- [ ] T3 | Build the lexical reader through the builder
- [ ] T4 | Rebuild the Python reader as a definition plus its own parts
- [ ] T5 | Rebuild the Rust reader as a definition plus its own parts
- [ ] T6 | Replace the three unchanged-code proofs with one
- [ ] T7 | Remove the reader's anchor text once the page places paragraphs
        > 2026-10-30 Page overwrites it at page.py:780; only use is the EOF flag :763
