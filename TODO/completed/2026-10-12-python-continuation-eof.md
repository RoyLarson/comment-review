# Read Python continuation before final whitespace

```
Status:   closed
Progress: 1 of 1 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-12 (Logical-line review: reading/python/structure.py:89)
```

## Objective

Read Python continuation before final whitespace.

## Tasks

- [x] T1 | 36 logical-line and 769 reader tests pass; review clean | cd5635f0 | Accept
      joined final whitespace at EOF; logical_lines tests still refuse an
      immediately unfinished continuation.
