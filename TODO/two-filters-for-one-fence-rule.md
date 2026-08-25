# Two filters state one fence rule

```
Status:   open
Progress: 0 of 2 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-25 (shadow-suite mutation run, 2026-08-25)
Updated:  2026-08-25 — NARROWED 2026-08-25. The pair no longer states ONE rule twice:
          since the absent-place ruling, bind() drops fences AND empty places (what an
          agent receives) while carried() drops only fences (what the census LISTING
          numbers). They serve different populations and share just the 'if b.address'
          predicate. ! The other half of the original finding is CLOSED:
          flows.census.emitted_row was deleted -- it was not a second emit but an
          adapter that turned Paragraphs into dicts so the unaddressed gate could read
          them, and the gate now asks the paragraphs it already holds.
```

## Objective

Two filters state one fence rule.

## Tasks

- [ ] Say which of the two owns 'a fence is not carried'
- [ ] The other calls it or is deleted
