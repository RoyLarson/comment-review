# Preserve compact Python header boundaries

```
Status:   closed
Progress: 2 of 2 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-14 (implementation review)
```

## Objective

Preserve compact Python header boundaries.

## Tasks

- [-] T1 | T2 removes the parser dependency instead of extending it | 9690bc3e | Fix
      compact header recognition; nested documentation tests pass
        > 2026-10-14 Check: Python reader tests cover compact headers and lambda colons.
- [x] T2 | Opaque controls preserve nested docs without a statement tree | 64120fb0 | Remove
      control-flow parsing from documentation-position tracking
        > 2026-10-14 Check: opaque code preserves nested docs without control parsing.
