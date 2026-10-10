# Use lexical code identity at both proof boundaries

```
Status:   open
Progress: 0 of 2 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-10 (live-run)
```

## Objective

Use lexical code identity at both proof boundaries.

## Tasks

- [ ] T1 | Replace Python AST identity checks with lexical comparison; verify
      docstring add and removal agree at both gates
        > 2026-10-10 Roy chose lexical identity at both code-unchanged boundaries
        > 2026-10-10 Use the owned scanner, independent of the runtime Python grammar
        > 2026-10-10 Formatting follows prose-only proof and precedes presentation
        > 2026-10-10 Reader scope: all languages currently listed by gather --languages
        > 2026-10-10 Code-reader scope excludes config, data and document formats
- [ ] T2 | Preserve literal whitespace in prove_unchanged.py:191-207; verify
      blank-line and trailing-space edits change the fingerprint
