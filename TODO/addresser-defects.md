# reading/addresser.py answers a miss with a real position

```
Status:   open
Progress: 0 of 2 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-11-08 (comment-review run over src/ since beta.7, 2026-11-08, 8198f716)
```

## Objective

reading/addresser.py answers a miss with a real position.

## Tasks

- [ ] T1 | Make `Cues.anchor_num` answer a miss with a value no cue holds, not 0
- [ ] T2 | Move `LEAD` to `binder/page.py`, its only reader
