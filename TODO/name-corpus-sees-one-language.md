# The name corpus sees one language, and the AST is why

```
Status:   open
Progress: 0 of 5 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-24 (Roy, 2026-08-24: 'If python could parse python code names would be
          useful')
```

## Objective

The name corpus sees one language, and the AST is why.

## Tasks

- [ ] declarations() gains the identifier on the declaring line, per language row
- [ ] code_names harvests from that instead of ast.parse
- [ ] Measure the corpus again: the NO_HARVESTER list holds only languages with an
      empty keyword list
- [ ] Say what C and C++ do, whose keyword lists are empty pending the first-word
      matcher
- [ ] referrers.tokens_for stops parsing Python for top-level defs, or says why it
      still must
