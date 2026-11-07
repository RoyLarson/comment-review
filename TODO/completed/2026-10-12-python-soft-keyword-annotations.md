# Read soft-keyword subscript annotations

```
Status:   closed
Progress: 1 of 1 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-12 (review)
```

## Objective

Read soft-keyword subscript annotations.

## Tasks

- [x] T1 | Subscript annotation regressions pass; review approved | 52a61381 | Read
      subscript annotations headed by match
        > 2026-10-12 Check: match[0]: int remains one ordinary module statement.
        > 2026-10-12 Reason: structure.py:348 mistakes a subscript for a match header.
