# Approve moves as indivisible units

```
Status:   closed
Progress: 1 of 1 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-01 (R2-author-review)
```

## Objective

Approve moves as indivisible units.

## Tasks

- [x] T1 | Partial move approvals refuse before docket or revise output | 9e7532b5c641455dd933bd45dce4171584b5b521 | Group
      move ends for selective approval; verify test_revise
        > 2026-10-01 transcribe.py:407-419 selects an agreed move end independently
        > 2026-10-01 Roy: a move is either approved and split or not approved
        > 2026-10-01 Incomplete move selection refuses before transcription
