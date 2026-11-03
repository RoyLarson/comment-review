# The name corpus sees one language, and the AST is why

```
Status:   open
Progress: 4 of 7 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-24 (Roy, 2026-08-24: 'If python could parse python code names would be
          useful')
```

## Objective

The name corpus sees one language, and the AST is why.

## Tasks

- [-] T1 | Superseded by #259: its language or reader left the system | e2b34a22ad36b0919b9d01cfd05bb74e80e76db9 | declarations()
      gains the identifier on the declaring line, per language row
- [ ] T2 | code_names harvests from that instead of ast.parse
- [-] T3 | Superseded by #259: its language or reader left the system | e2b34a22ad36b0919b9d01cfd05bb74e80e76db9 | Measure
      the corpus again: the NO_HARVESTER list holds only languages with an empty
      keyword list
- [-] T4 | Superseded by #259: its language or reader left the system | e2b34a22ad36b0919b9d01cfd05bb74e80e76db9 | Say
      what C and C++ do, whose keyword lists are empty pending the first-word
      matcher
- [-] T5 | SUPERSEDED by T6: concordance is shelved from the lexical plan | c0b5b211 | referrers.tokens_for
      stops parsing Python for top-level defs, or says why it still must
- [ ] T6 | Make referrers.tokens_for stop parsing Python for top-level defs, or
      say why it still must
- [ ] T7 | Add Python and Rust declaration facts to referrer discovery. Verify:
      path terms remain; unharvested Rust is reported
