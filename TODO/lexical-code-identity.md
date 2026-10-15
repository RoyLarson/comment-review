# Use lexical code identity at both proof boundaries

```
Status:   open
Progress: 2 of 4 tasks closed
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
        > 2026-10-14 Check: both gates accept doc add/drop; proof also requires approval
- [ ] T2 | Preserve literal whitespace in prove_unchanged.py:191-207; verify
      blank-line and trailing-space edits change the fingerprint
- [x] T3 | Selected documentation retains protected directive context; reviewed | 09df3de4 | Retain
      protected directive context when selecting documentation
        > 2026-10-14 Check: selected docs refuse directive spacing or placement changes
        > 2026-10-14 Reason: preservation.py:213 erases protected source context
- [x] T4 | Multiline documentation suffix correspondence passes both directions | 09df3de4 | Match
      retained code after multiline documentation removal
        > 2026-10-14 Check: multiline doc removal retains closing-line code indentation
        > 2026-10-14 Reason: _documentation_span loses the retained suffix context
