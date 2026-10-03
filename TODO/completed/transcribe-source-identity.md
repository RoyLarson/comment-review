# Transcription source identity defects

```
Status:   closed
Progress: 1 of 1 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-02 (review against main)
```

## Objective

Transcription source identity defects.

## Tasks

- [x] T1 | Recorded SHA survives reload and turns; stale destination refuses | b96af9f5bcbfa8f77d449dcc4b7ca9aa2e005ee9 | Record
      ungathered destination SHA before approval; test transcribe.py:210 refuses
      a destination edited after collation
        > 2026-10-02 Repro: .tmp/review_stale_destination.py; newer prose is discarded
