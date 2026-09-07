# A role writes its own tool to fill the edit copy

```
Status:   open
Progress: 0 of 5 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-09-07 (Roy, 2026-09-07, watching two Sonnet roles each write a library
          and a script per file to fill their copy: we should have made a script that
          fills it in for them)
```

## Objective

A role writes its own tool to fill the edit copy.

## Tasks

- [ ] T1 | Implement a mark command that sets one address's instruction, claim,
      reason, sources and change on an edit copy in place
        > 2026-09-07 2026-09-06 run: fc/lib.py, work/apply_marks.py -- the same five ops
- [ ] T2 | Implement appending a second mark at an address already ruled,
      carrying the slot's anchor and raw_text
- [ ] T3 | Implement marking every slot still null on a copy clean in one call
- [ ] T4 | Implement quoting a source verbatim from the slot's own raw_text by
      line, so a role never retypes a citation
- [ ] T5 | Update reviewer-brief.md so a role is told the command and never
      writes a script of its own
        > 2026-09-07 agents lane; a one-for-one naming of a command that exists
