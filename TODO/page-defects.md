# binder/page.py carries unread names and a branch nothing reaches

```
Status:   open
Progress: 3 of 4 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-11-08 (comment-review run over src/ since beta.7, 2026-11-08, 8198f716)
```

## Objective

binder/page.py carries unread names and a branch nothing reaches.

## Tasks

- [x] T1 | WIRE_FIELDS deleted | 0bd9f597 | Delete `WIRE_FIELDS`, which nothing
      reads
        > 2026-11-23 comment-review 2026-11-23: still unread; _place spells the keys
- [x] T2 | Page.prose deleted; tests read handed() | 0bd9f597 | Delete
      `Page.prose`, which only tests call and `handed` restates
        > 2026-11-23 comment-review 2026-11-23: still test-only; restates handed
- [x] T3 | attach's unreachable MATTER branch deleted | 0bd9f597 | Delete
      `attach`'s `Kind.MATTER` branch, which `page_for` never reaches
- [ ] T4 | Refuse a malformed row cue in binder/page.py:366 _checked_place
      instead of accepting any non-blank cue
        > 2026-11-22 Check (M24): cues 'b0@' and 'zz' are refused at bind
