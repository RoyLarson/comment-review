# Keep Python comment sections at their places

```
Status:   open
Progress: 0 of 2 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-14 (implementation)
```

## Objective

Keep Python comment sections at their places.

## Tasks

- [~] T1 | Separate comment-only sections from trailing comments
        > 2026-10-14 Location: reading/python/projection.py:66 groups B and C together
        > 2026-10-14 Check: galley added-prose reread matrix passes all nine cases
- [ ] T2 | Preserve contiguous header comments after an initial BOM
        > 2026-10-14 Location: reading/python/projection.py:60,70
        > 2026-10-14 Check: BOM then two adjacent header comments stay together in f0
