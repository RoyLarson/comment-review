# Preserve compact Python header boundaries

```
Status:   open
Progress: 0 of 2 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-14 (implementation review)
```

## Objective

Preserve compact Python header boundaries.

## Tasks

- [ ] T1 | Fix compact header recognition; nested documentation tests pass
        > 2026-10-14 Check: Python reader tests cover compact headers and lambda colons.
- [ ] T2 | Remove control-flow parsing from documentation-position tracking
        > 2026-10-14 Check: opaque code preserves nested docs without control parsing.
