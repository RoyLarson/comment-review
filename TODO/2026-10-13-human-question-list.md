# Expose human questions across edit copies

```
Status:   open
Progress: 1 of 4 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-13 (user)
```

## Objective

Expose human questions across edit copies.

## Tasks

- [x] T1 | Collate lists every question from every edit copy and exits 5; Process #368 | 718944e14524f963b93cc5c8fcca2e7948fb0a67 | List
      human questions from multiple edit copies
        > 2026-10-13 Check: list questions with copy, role and address for task agents.
        > 2026-10-13 Reason: task agents need one list from returned edit copies.
- [ ] T2 | Make flows/human.py match a code concern's answer by place, not by
      role, per Process #269
- [ ] T3 | Ask desk.marks.table Row.places where a mark writes in flows/human.py
        > 2026-11-23 corrections_to_matter reads mark.address, MoveMark.to itself
- [ ] T4 | Match approval of a matter correction to the text the author saw in
      flows/human.py
        > 2026-11-23 corrections_to_matter keys on mark reason; new text inherits OK
