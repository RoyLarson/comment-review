# Complete R3 placement deferral for movers

```
Status:   closed
Progress: 1 of 1 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-09-30 (review)
```

## Objective

Complete R3 placement deferral for movers.

## Tasks

- [x] T1 | Both deferral shapes stop asking the mover again while preserving its filing and the other reader contest | a97bb5ded04e28d5372eecac87ea28ddaf3965b5 | Remove
      deferring movers from contested placement questions
        > 2026-09-30 At evaluate/move.py:158, owed still includes deferring movers
