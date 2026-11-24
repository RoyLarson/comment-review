# A dropped history sentence has no home

```
Status:   open
Progress: 5 of 9 tasks closed
Owner:    agents
Requires-Roy: false
Raised:   2026-11-08 (2026-11-08 run on another repository, plugin 0.2.4-beta.7)
Waiting on: 2026-11-08 -- external addresses (Addressing #21) and the non-code document
            chain, which follow the code section working -- #297
```

## Objective

A role that drops a dated, quoted or ruling sentence has nowhere to send it, so
it is deleted. Where a repo keeps such prose in a home of its own, the run loses
it, and nothing shows the author which sentences the write leaves in no file.

Measured on a 2026-11-08 run over another repository (plugin 0.2.4-beta.7): the
style sheet banned dates and quotations in docstrings, the roles obeyed by
dropping them, and twelve mirror documents had to be written by hand afterwards
from the pre-edit ref. The repo's own fuzzy loss check passed every one.

The tasks land together: a recorded home with no rule to send prose there, or a
rule with no check that the prose arrived, leaves the loss in place.

## Tasks

- [x] T1 | FINISHED -- #297: moved to an external address once that chain lands | 2255e7c9 | Decide
      where a drop of a dated, quoted or ruling sentence sends it, and what a
      run does where the repo names no home
- [x] T2 | Stage 1 records the repo's home for removed history | 4c4be613 | Record
      in stage 1 the repo's home for removed history, or none
        > 2026-11-08 Waits on external addresses, after the code section works (#297)
        > 2026-11-09 #303: ask the author when the repo names no home; none drops
- [x] T3 | The brief: a history drop names its home or queries | 47835332 | Update
      the brief so a drop of history names its destination, or queries the
      author where none is recorded
        > 2026-11-08 Waits on external addresses, after the code section works (#297)
- [x] T4 | #420: lost lists removed sentences no file of the tree as written holds | 0c979445 | Implement
      a 7a list of every removed sentence the write leaves in no file, matched
      exactly
        > 2026-11-08 Waits on external addresses, after the code section works (#297)
- [ ] T5 | Split lost's sentences at line ends as well as at sentence
      punctuation
- [-] T6 | SUPERSEDED -- #426: lost checks a sentence at a named place, not across the tree | 1c3c0e31 | Parse
      in lost only the files the raw-text match could not rule out
- [ ] T7 | Implement in lost a check of each sentence a move removed at the
      move's destination, reading the closed proofs
- [ ] T8 | Add to a history drop a field naming its home, which check reads
        > 2026-11-24 #426: later plan; history drops are listed till then
- [ ] T9 | Implement in lost a check of each sentence a history drop removed in
      the home the drop names
