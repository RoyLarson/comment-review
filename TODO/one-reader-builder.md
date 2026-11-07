# One reader builder from each language's definition

```
Status:   open
Progress: 4 of 12 tasks closed
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
- [-] T3 | Superseded by #259: its language or reader left the system | e2b34a22ad36b0919b9d01cfd05bb74e80e76db9 | Build
      the lexical reader through the builder
- [ ] T4 | Rebuild the Python reader as a definition plus its own parts
- [ ] T5 | Rebuild the Rust reader as a definition plus its own parts
- [ ] T6 | Replace the three unchanged-code proofs with one
- [ ] T7 | Remove the reader's anchor text once the page places paragraphs
        > 2026-10-30 Page overwrites it at page.py:780; only use is the EOF flag :763
- [x] T8 | CodeLine.joins removed; T51 derives a unit from DocPlace.at | e0da1c3a2a39e797c69ae351e76d296d5156ad5f | Remove
      CodeLine.joins once a unit has one statement
        > 2026-10-30 Derive it from DocPlace.at; Rust units land then (T51)
- [-] T9 | Widened by #285 into T11 | 5ca5f8f1 | Mark an empty `b` inside a unit
      unassignable (#257)
- [-] T10 | Widened by #285 into T12 | 5ca5f8f1 | Resolve an unassignable `b` to
      its unit's assignable `b` (#257)
- [ ] T11 | Map every place on Cues to the address it is written at (#285)
        > 2026-11-07 Unit b -> unit's b; string b -> b above; string c -> closing c
        > 2026-11-07 Most map to themselves; built at read, held on Cues (#285)
- [ ] T12 | Resolve the lookup to the mapped address (#285)
        > 2026-11-07 Check: find at b2 inside a decorator unit answers the unit's b
        > 2026-11-07 Check: b and c inside a multi-line string answer per T11
