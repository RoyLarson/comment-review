# A human question is asked before the fold

```
Status:   open
Progress: 0 of 5 tasks closed
Owner:    backend
Requires-Roy: true
Raised:   2026-09-26 (Process 197)
```

## Objective

A human question is asked before the fold.

## Tasks

- [?] T1 | Decide what records the human answer and carries it back to the
      roles, per Process 197
- [ ] T2 | Implement a check that lists every human-review query in the returned
      copies or answers before collate or turn folds
- [ ] T3 | Implement the record of the human answer and its hand-back to the
      role that asked, so it can revise its mark or answer
- [ ] T4 | Update SKILL.md so the task agent asks each human-review query with
      the question tool before collate and turn; agents lane
- [ ] T5 | Delete the write-end refusal of a move open at an unruled end once no
      human-review query reaches the fold
