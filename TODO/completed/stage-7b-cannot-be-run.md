# Stage 7b has no way to run: approve() has no caller and no flag

```
Status:   closed
Progress: 3 of 3 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-24 (dead_sweep during P8, 2026-08-24)
```

## Objective

Stage 7b has no way to run: approve() has no caller and no flag.

## Tasks

- [x] T1 | The task agent performs the write: SKILL.md:531-535 and references/write.md:69; verified at HEAD | 67184ac1 | Say
      who invokes the write -- a command, a flow, or the task agent through a
      CLI
- [x] T2 | SKILL.md:531-535 plus references/write.md:1-75 state what performs 7b; verified at HEAD | 67184ac1 | Give
      it an entry point, or state in SKILL.md what actually performs 7b
- [-] T3 | Partly done: untouched checkout pinned (test_the_chain.py:160); copy half has no Python to test; verified at HEAD | 67184ac1 | A
      test that the approved bytes reach the real file, and that an abandoned
      run leaves the tree untouched
