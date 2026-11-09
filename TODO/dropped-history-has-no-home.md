# A dropped history sentence has no home

```
Status:   open
Progress: 0 of 4 tasks closed
Owner:    agents
Requires-Roy: true
Raised:   2026-11-08 (2026-11-08 run on another repository, plugin 0.2.4-beta.7)
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

- [?] T1 | Decide where a drop of a dated, quoted or ruling sentence sends it,
      and what a run does where the repo names no home
- [ ] T2 | Record in stage 1 the repo's home for removed history, or none
- [ ] T3 | Update the brief so a drop of history names its destination, or
      queries the author where none is recorded
- [ ] T4 | Implement a 7a list of every removed sentence the write leaves in no
      file, matched exactly
