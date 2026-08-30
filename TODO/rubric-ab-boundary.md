# The rubric's A/B boundary is unwritten, so one judge grades identical facts two ways

```
Status:   decision-needed
Progress: 0 of 3 tasks done
Owner:    agents
Requires-Roy: true
Raised:   2026-08-29 (the first keyed T50, 2026-08-29: detection came back B A B A B
          over five readings of one artifact)
```

## Objective

The rubric's A/B boundary is unwritten, so one judge grades identical facts two ways.

## Tasks

- [ ] Rule where the A/B boundary sits for detection, given a run that finds the
      keyed paragraph and files correcting instructions on the exact sentences END
      rewrote. Verify: rubric.md states the condition, and RUBRIC_VERSION is
      bumped
- [ ] Update evals/rubric.md with that condition and bump grader.RUBRIC_VERSION to
      3. Verify: tests/harness/test_grader.py asserts the new version and the
      file's Version line agrees
- [ ] Re-grade evidence/the-threshold-moved-not-the-perception/findings.md under
      the new rubric. Verify: detection returns the same letter across at least
      three readings
