# The census to findings to verdicts path has never been determined against a backend that works

```
Status:   decision-needed
Progress: 0 of 6 tasks done
Owner:    comment-review
Requires-Roy: true
Raised:   2026-08-22 (Roy, 2026-08-22: that whole system of from census to findings to
          verdicts is something that needs to be determined now that the backend part of
          the system works)
```

## Objective

The census to findings to verdicts path has never been determined against a backend that works.

## Tasks

- [ ] THE BACKEND NOW WORKS, which is what makes this askable. MEASURED
      2026-08-22: a file to a census and a list of verdicts back to a new file,
      byte-identical on 3,015 of 3,020 corpus files across ten languages, 0
      collisions -- and all seven verdicts reduce to two operations, set the text
      at an address or vacate it. Every earlier design for the front half was
      drawn against a back half that could not set a page
- [ ] * WHAT A REVIEWER IS HANDED IS UNSETTLED. A census row carries 19 fields and
      an empty place fills 7 -- see census-row-carries-empty-fields -- and what
      the four roles actually need decides that shape, which is pasted into four
      prompts per page
- [ ] * WHAT A FINDING IS IS UNSETTLED. claim is an object that renders to a
      marker string for checks written against the old form -- see claim-fallback-
      is-unreachable, which is DEFERRED on this determination
- [ ] * WHAT THE JOIN CERTIFIES IS UNSETTLED. verdicts.py refuses a record
      record.py accepts and the reverse; coverage is structural but a gap goes
      nowhere -- see a-coverage-gap-should-go-back-to-the-reviewer
- [ ] RELATED AND ALREADY FILED, so this is a hub rather than a duplicate: the-
      census-is-mostly-intervals-nobody-rules-on, census-row-carries-empty-fields,
      claim-fallback-is-unreachable, a-coverage-gap-should-go-back-to-the-
      reviewer, ownership-is-read-first-but-nothing-makes-it-so, the-author-
      approves-blocks-and-never-sees-the-page, a-malformed-page-drops-its-records
- [ ] WHAT *DETERMINED* HAS TO MEAN HERE, or this stays open forever: one
      statement of what crosses each of the three boundaries -- census to
      reviewer, reviewer to record, record to verdict -- with the fields NAMED, so
      that each of the TODOs above becomes either a task under it or superseded by
      it
