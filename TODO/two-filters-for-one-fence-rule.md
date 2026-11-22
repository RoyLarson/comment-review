# Two filters state one fence rule

```
Status:   open
Progress: 3 of 5 tasks closed
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

- [-] T1 | SUPERSEDED by T3: the old pair is gone; Binder.paragraphs with Page.serialize now state the filter | 22c3a0abcbc86509c74296319ce5b719a43338ca | Say
      which of the two owns 'a fence is not carried'
- [-] T2 | SUPERSEDED by T4: 'the other' named a deleted pair; the repeats are in binder/page.py, binder.py | 22c3a0abcbc86509c74296319ce5b719a43338ca | The
      other calls it or is deleted
- [ ] T3 | Name the one owner of the `if b.address` fence filter in binder/
        > 2026-11-22 Check: binder.py:256-262 names the owner, not 'they filter alike'
- [-] T4 | SUPERSEDED by T5: its label cited a reissued task; T1 is now T3 | 22c3a0abcbc86509c74296319ce5b719a43338ca | Route
      each repeat of the `if b.address` fence filter through T1's owner
        > 2026-11-22 Check: Page.serialize, known_addresses call the owner
- [ ] T5 | Route each repeat of the `if b.address` fence filter through T3's
      owner
        > 2026-11-22 Check: Page.serialize, known_addresses call the owner
