# Align the command smoke with paragraph rewrapping

```
Status:   open
Progress: 0 of 1 tasks closed
Owner:    systems
Requires-Roy: false
Raised:   2026-10-04 (beta.5-check)
```

## Objective

Align the command smoke with paragraph rewrapping.

## Tasks

- [ ] T1 | Update wrapped-drop expected text for paragraph rewrapping and verify
      the full command smoke passes
        > 2026-10-04 Wrapped drop keeps the words but differs from WRAP_RATE_DRAFT
        > 2026-11-06 Wrap stage passes at 8d66c9b4; smoke now stops at one end approved
        > 2026-11-06 transcribe.py refuses one move end; smoke and write.md disagree
        > 2026-11-06 One end refuses per #283 at 39646af8; stops at compacting check
