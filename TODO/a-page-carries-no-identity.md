# A page carries no identity, so staleness is checked by re-parsing and comparing

```
Status:   open
Progress: 4 of 4 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-24 (Roy: the page should record its sha, so the galley and the compositor
          can verify nothing changed without re-parsing)
Updated:  2026-08-25 — OWNERSHIP MOVED, 2026-08-25. T2 and T3 name the GALLEY and the
          COMPOSITOR as the things that verify by sha. Roy ruled otherwise on the write-
          chain branch: the sha-page piece should be part of the chain of command piece.
          One owner answers it once, in flows/proof_setter.py, rather than two owners
          answering it twice. The work is the same work and the file is backend's, so
          this is a restatement rather than a new TODO. T4 is SUPERSEDED OUTRIGHT: it
          asks that the per-paragraph comparison stay honest about what it covers, and
          that comparison was galley.drifted, retired in 0f99805 -- there is no longer a
          comparison to keep honest, and the sha answers the question in one comparison
          before anything is parsed. Per the standing rule a superseded task is checked,
          not deleted, so the error stays legible.
```

## Objective

**A page does not say which bytes it was built from, so every consumer asks the question a
harder way.** Roy, 2026-08-24: *"the page should record its sha. This allows the galley and the
compositor to verify nothing changed without having to reparse and run another less precise
verification scheme."*

!! **WHAT THE GALLEY DOES TODAY, AND WHAT IT HAS ALREADY TRIED.** `galley.py` re-reads the file,
REBUILDS the page, and then compares `raw_lines` per paragraph against the fresh parse. Its own
comment records the two schemes before it:

| scheme | why it went |
| --- | --- |
| compare the ANCHOR per paragraph | a prose edit is not an anchor change, so it could not see one -- MEASURED 2026-08-22: replacing one comment with two unreviewed lines gave exit 0 and overwrote both |
| compare the paragraph's TEXT | *"asked whether the paragraph still READS as it did and needed a case per kind"* |
| compare `raw_lines` per paragraph | today's -- one comparison for every kind, and it still needs the whole re-parse first |

! **THE RULE THEY ARE ALL APPROXIMATING IS ALREADY STATED.** Roy, quoted in `galley.py`: *"if the
file shifted at all it is dead and so are the edits."* **A hash answers exactly that**, in one
comparison, before anything is parsed.

!! **AND THE PER-PARAGRAPH FORM CANNOT ANSWER IT IN PRINCIPLE.** It compares what the census has
rows for. A change in a stretch the census carries no row for, or one that happens to leave a
paragraph's lines identical, is a file that shifted and a check that passes. ! `galley.py:311`
also skips every paragraph with no address, so `leading` and the file's own matter are outside
the comparison entirely.

! **IT IS A PAGE FACT, NOT A ROW FACT**, so it costs one field per page rather than one per row
-- the same envelope `path` moves into.

! **WHAT IT DOES NOT REPLACE.** `raw_lines` still carries the text the compositor sets from, so
the hash retires a JUSTIFICATION for that field and not the field. ! Any ruling on trimming
`raw_lines` has to be made knowing that, which is why this is filed beside the field trim rather
than inside it.

## Tasks

- [x] T1 | FINISHED | unknown | T1 -- Record the source SHA on the page, beside
      `path`. Verify: two censuses of an unchanged file carry the same SHA, and
      one edit changes it.
- [x] T2 | FINISHED | unknown | T2 -- Make the galley refuse a changed file on
      the SHA, before any re-parse. Verify: a one-byte edit is refused and no
      page is built.
- [x] T3 | FINISHED | unknown | T3 -- Make the compositor verify by SHA on the
      same footing. Verify: it refuses a file whose bytes are not the ones its
      page was built from.
- [x] T4 | FINISHED | unknown | T4 -- Keep the per-paragraph comparison honest
      about what it now covers. Verify: its comment names the SHA as what
      answers *did the file shift*.

## Related

- [`galley-and-compositor-write-path`](galley-and-compositor-write-path.md) -- the read paths
  both gates take; this changes what they COMPARE, that changes how they READ
- [`census-row-carries-empty-fields`](census-row-carries-empty-fields.md) -- the field trim this
  adds a field to, deliberately: the minimal set is the FUNCTIONAL one, not the smallest
