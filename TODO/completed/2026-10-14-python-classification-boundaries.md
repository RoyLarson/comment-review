# Preserve Python classification boundaries

```
Status:   closed
Progress: 2 of 2 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-14 (review)
```

## Objective

Preserve Python classification boundaries.

## Tasks

- [x] T1 | Unicode boundary regressions and 1333 reader checks pass | 64120fb0 | Distinguish
      lambda keywords from Unicode name spelling
        > 2026-10-14 Location: reading/python/structure.py:201 keyword boundary
        > 2026-10-14 Check: Unicode lambda names retain declarations and documentation
- [-] T2 | Whole-code source context meets the protection contract | b404f360 | Attach
      inline type comments to their assignment source
        > 2026-10-14 Location: reading/python/directives.py:167-178 inline attachment
        > 2026-10-14 Check: def and opaque header tails attach to x=1 only
        > 2026-10-14 Review withdrew: retained code prefix preserves source attachment.
