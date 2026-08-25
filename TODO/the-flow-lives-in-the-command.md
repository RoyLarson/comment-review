# The flow lives in the command, not in flows/

```
Status:   open
Progress: 0 of 5 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-24 (P2 of refactor/the-boundaries-are-not-real, 2026-08-24)
```

## Objective

The flow lives in the command, not in flows/.

## Tasks

- [ ] Name what census's flow function IS, and what it returns to a command
- [ ] Move the orchestration out of commands/census.py into flows/census.py
- [ ] commands/census.py parses arguments and calls it, and holds no page building
- [ ] tests/binder/test_page.py reads source_of('census') again, not
      command_source
- [ ] Ask the same question of verdicts, galley and record
