# The flow lives in the command, not in flows/

```
Status:   open
Progress: 0 of 5 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-24 (P2 of refactor/the-boundaries-are-not-real, 2026-08-24)
Narrowed: 2026-08-25 — commands/proof.py exposes flows/proof_setter.py, the galley half
          of task 5: the command parses arguments, reads two files and calls the flow
          once, holding no orchestration. census, verdicts and record remain untouched
          -- task 5 is not closed.
```

## Objective

The flow lives in the command, not in flows/.

## Tasks

- [ ] T1 | Name what census's flow function IS, and what it returns to a command
- [ ] T2 | Move the orchestration out of commands/census.py into flows/census.py
- [ ] T3 | commands/census.py parses arguments and calls it, and holds no page
      building
- [ ] T4 | tests/binder/test_page.py reads source_of('census') again, not
      command_source
- [ ] T5 | Ask the same question of verdicts, galley and record
