# A role writes its own tool to fill the edit copy

```
Status:   closed
Progress: 5 of 5 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-09-07 (Roy, 2026-09-07, watching two Sonnet roles each write a library
          and a script per file to fill their copy: we should have made a script that
          fills it in for them)
```

## Objective

A role writes its own tool to fill the edit copy.

## Tasks

- [x] T1 | FINISHED -- mark places one ruling on a copy, one flag per field, @path for text | 7cfaeb81 | Implement
      a mark command that sets one address's instruction, claim, reason, sources
      and change on an edit copy in place
        > 2026-09-07 2026-09-06 run: fc/lib.py, work/apply_marks.py -- the same five ops
        > 2026-09-07 claude-settings run: all four roles wrote a helper as well
- [x] T2 | FINISHED -- a ruled address gets a second entry beside it carrying anchor and raw_text | 7cfaeb81 | Implement
      appending a second mark at an address already ruled, carrying the slot's
      anchor and raw_text
- [-] T3 | SUPERSEDED, Roy 2026-09-07: a bulk clean invites skipping paragraphs; each role certifies each paragraph under its remit | 08b4f8d3 | Implement
      marking every slot still null on a copy clean in one call
- [x] T4 | FINISHED -- a bare --cite has its line read from the checkout into verbatim | 7cfaeb81 | Implement
      quoting a source verbatim from the slot's own raw_text by line, so a role
      never retypes a citation
- [x] T5 | FINISHED -- the brief names the command and forbids a script of the role's own | 6b1a6171 | Update
      reviewer-brief.md so a role is told the command and never writes a script
      of its own
        > 2026-09-07 agents lane; a one-for-one naming of a command that exists
