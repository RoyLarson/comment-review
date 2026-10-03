# Transcription source identity defects

```
Status:   open
Progress: 0 of 1 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-02 (review against main)
```

## Objective

Transcription source identity defects.

## Tasks

- [ ] T1 | Record ungathered destination SHA before approval; test
      transcribe.py:210 refuses a destination edited after collation
        > 2026-10-02 Repro: .tmp/review_stale_destination.py; newer prose is discarded
