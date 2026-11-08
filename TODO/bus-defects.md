# flows/bus.py carries an unread field and lets a ruling be overwritten

```
Status:   open
Progress: 0 of 2 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-11-08 (comment-review run over src/ since beta.7, 2026-11-08, 8198f716)
```

## Objective

flows/bus.py carries an unread field and lets a ruling be overwritten.

## Tasks

- [ ] T1 | Delete `Result.page_snapshots`, which only tests read
- [ ] T2 | Refuse a second disposition at one address in `_on_dispositions`
