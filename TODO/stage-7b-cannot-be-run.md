# Stage 7b has no way to run: approve() has no caller and no flag

```
Status:   open
Progress: 0 of 3 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-24 (dead_sweep during P8, 2026-08-24)
```

## Objective

Stage 7b has no way to run: approve() has no caller and no flag.

## Tasks

- [ ] T1 | Say who invokes the write -- a command, a flow, or the task agent
      through a CLI
- [ ] T2 | Give it an entry point, or state in SKILL.md what actually performs
      7b
- [ ] T3 | A test that the approved bytes reach the real file, and that an
      abandoned run leaves the tree untouched
