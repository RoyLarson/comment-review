# flows/bus.py carries an unread field and lets a ruling be overwritten

```
Status:   closed
Progress: 2 of 2 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-11-08 (comment-review run over src/ since beta.7, 2026-11-08, 8198f716)
```

## Objective

flows/bus.py carries an unread field and lets a ruling be overwritten.

## Tasks

- [x] T1 | Deleted; tests read the proof instead | 6f071f96 | Delete
      `Result.page_snapshots`, which only tests read
- [-] T2 | SUPERSEDED by collate-flow-defects T20: filed twice in error | 4db8b52f | Refuse
      a second disposition at one address in `_on_dispositions`
