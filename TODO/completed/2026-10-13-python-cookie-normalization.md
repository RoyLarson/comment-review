# Accept Python UTF-8 source cookie names

```
Status:   closed
Progress: 1 of 1 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-13 (review)
```

## Objective

Accept Python UTF-8 source cookie names.

## Tasks

- [x] T1 | UTF-8 cookie aliases accepted; 1111 reader tests and review pass | 3c62087a | Normalize
      Python encoding cookie names
        > 2026-10-13 Location: reading/python/directives.py:76-79 raw codec lookup.
        > 2026-10-13 Check: utf-8-sig and UTF_8_SIG read; incompatible cookies refuse.
