# The middle folds through three tables, an evaluator and a Unit of Work

```
Status:   closed
Progress: 7 of 7 tasks closed
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
- [x] T2 | desk/evaluate holds Place, the six states and marks_pass, answers_pass, dispositions_pass and evaluate; tests/test_passes.py and tests/test_place.py | 90b80310 | Implement
      the place, its six states and the three passes in desk/evaluate
- [x] T3 | desk/work holds the Fold and its events, flows/bus.py the collate handler; commands/collate.py folds through it; tests/test_bus.py, test_fold.py | b2538cb5 | Implement
      the Unit of Work in desk/work and the bus in flows, and switch collate to
      it
        > 2026-09-14 Fold and events landed at 1ef041f3; bus and collate switch remain
- [x] T4 | flows/bus.py handles AnswersReturned and DispositionsWritten; turn, disposition and check --answers fold through it; the full smoke exits 0 | efad40b3 | Implement
      the turn and disposition handlers and switch both commands to the bus
- [x] T5 | fill, check and docket_of read the rows; text_at deleted; one role's marks at a place compose (#179) | d5455d43 | Update
      fill, check and docket_of to read the tables, and delete text_at
- [x] T6 | the old fold, turn, determined and diff_mark are deleted with their tests; src -3349 lines; the tables gate holds the whole tree; docs/history.md carries the differential | dd81b99e | Delete
      the old fold, turn, determined and diff_mark with their tests
- [x] T7 | the smoke plants every row, shape, effect and side; a row-coverage gate; a second stage over the revise; desk/topology.py seeded_from_problem | 962e3438 | Implement
      a smoke plant for every row of the three tables, and the reader for a
      stage's revise
