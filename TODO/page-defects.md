# binder/page.py carries unread names and a branch nothing reaches

```
Status:   open
Progress: 0 of 3 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-11-08 (comment-review run over src/ since beta.7, 2026-11-08, 8198f716)
```

## Objective

binder/page.py carries unread names and a branch nothing reaches.

## Tasks

- [ ] T1 | Delete `WIRE_FIELDS`, which nothing reads
- [ ] T2 | Delete `Page.prose`, which only tests call and `handed` restates
- [ ] T3 | Delete `attach`'s `Kind.MATTER` branch, which `page_for` never
      reaches
