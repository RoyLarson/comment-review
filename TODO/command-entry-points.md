# The commands keep entry points of their own beside __main__

```
Status:   open
Progress: 0 of 2 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-11-08 (comment-review run over src/ since beta.7, 2026-11-08, 8198f716)
```

## Objective

The commands keep entry points of their own beside __main__.

## Tasks

- [ ] T1 | Delete the `if __name__ == "__main__"` blocks in check, collate,
      disposition, mark and turn
- [ ] T2 | Delete `commands/topology.py`'s own `utf8_console()` call
