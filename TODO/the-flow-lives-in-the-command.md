# The flow lives in the command, not in flows/

```
Status:   open
Progress: 4 of 5 tasks closed
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

- [x] T1 | FINISHED -- flows.gather.gather(repo, targets, revise) returns a Gathering: binder, pages, paragraphs, files, unreadable, no_record, unread | 68bfc548 | Name
      what census's flow function IS, and what it returns to a command
- [x] T2 | FINISHED -- the walk, the pages, the annotations and the bind moved into flows/gather.py as STEPS | 68bfc548 | Move
      the orchestration out of commands/census.py into flows/census.py
- [x] T3 | FINISHED -- commands/gather.py (census renamed, Vocabulary 34) parses, prints and exits; it builds no page | 68bfc548 | commands/census.py
      parses arguments and calls it, and holds no page building
- [ ] T4 | tests/binder/test_page.py reads source_of('census') again, not
      command_source
        > 2026-09-04 tests/binder/test_page.py and command_source both no longer exist
- [-] T5 | SUPERSEDED -- verdicts, galley and record all left src/ for prototype/original/ and none of them runs | b50e7a4 | Ask
      the same question of verdicts, galley and record
