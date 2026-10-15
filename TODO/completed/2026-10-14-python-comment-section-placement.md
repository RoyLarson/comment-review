# Keep Python comment sections at their places

```
Status:   closed
Progress: 2 of 2 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-14 (implementation)
```

## Objective

Keep Python comment sections at their places.

## Tasks

- [x] T1 | C and B retain distinct places through writing and rereading | HEAD | Separate
      comment-only sections from trailing comments
        > 2026-10-14 Location: reading/python/projection.py:66 groups B and C together
        > 2026-10-14 Check: galley added-prose reread matrix passes all nine cases
- [x] T2 | BOM header matrix preserves one F and exact writer bytes | HEAD | Preserve
      contiguous header comments after an initial BOM
        > 2026-10-14 Location: reading/python/projection.py:60,70
        > 2026-10-14 Check: BOM then two adjacent header comments stay together in f0
