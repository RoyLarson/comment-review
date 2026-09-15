# The middle folds through three tables, an evaluator and a Unit of Work

```
Status:   open
Progress: 1 of 7 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-09-14 (docs/superpowers/specs/2026-09-14-the-middle-rebuilt-design.md)
```

## Objective

The middle folds through three tables, an evaluator and a Unit of Work.

## Tasks

- [x] T1 | FINISHED -- the three tables under desk/, and the gate with its shrinking list | 3a379014 | Implement
      the marks, answers and dispositions tables under desk/, with the gate that
      nothing else names a row
- [ ] T2 | Implement the place, its six states and the three passes in
      desk/evaluate
- [ ] T3 | Implement the Unit of Work in desk/work and the bus in flows, and
      switch collate to it
- [ ] T4 | Implement the turn and disposition handlers and switch both commands
      to the bus
- [ ] T5 | Update fill, check and docket_of to read the tables, and delete
      text_at
- [ ] T6 | Delete the old fold, turn, determined and diff_mark with their tests
- [ ] T7 | Implement a smoke plant for every row of the three tables, and the
      reader for a stage's revise
