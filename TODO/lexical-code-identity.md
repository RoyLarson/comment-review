# Use lexical code identity at both proof boundaries

```
Status:   open
Progress: 0 of 1 tasks closed
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
