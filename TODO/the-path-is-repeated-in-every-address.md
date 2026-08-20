# Every record repeats its page's path, which is 26% of what a reviewer is handed

```
Status:   decision-needed
Progress: 0 of 4 tasks done
Owner:    session
Requires-Roy: true
Raised:   2026-08-19 (Roy relaying an earlier session's finding while closing 0.2.4,
          2026-08-19)
Updated:  2026-08-19 — Not in 0.2.4: it reopens the record shape, and the address is
          correct as it stands. Task 1 is the ruling.
```

## Objective

!! **AN ADDRESS CARRIES ITS PAGE'S PATH, AND EVERY RECORD REPEATS IT.** Roy, 2026-08-19, relaying an earlier session: *"we could significantly reduce the payload if we gave the page its location as an attribute and then just printed out the foliations for the page, as a list of records."*

**Measured 2026-08-19 over this repo's own 15 shipped scripts, one reviewer's seeded record file:**

| | |
| --- | ---: |
| the file | 117,690 bytes, 487 slots |
| the PATH half of every address | **31,006 bytes -- 26%** |
| x4 reviewers | **124,024 bytes** |
| 15 pages stating their path once | 951 bytes |
| **saving per reviewer** | **30,055 bytes** |

! **For scale, every `anchor` in that file together is 20,270 bytes** -- the repeated path costs more than all the anchors combined, and the anchor is the field a reviewer greps.

! **It is a FORMAT change, not a defect.** The address is correct and resolvable as it stands; this is payload. Every consumer reads `record["address"]` as a whole string -- `entry_for`, the galley's `--edits`, `desk.address_problem`, the join -- so grouping by page means each of those learns which page it is reading. ! `addresser.folio_of` already splits the two halves and would be the seam.

! **The census LISTING already does this**: it prints `== path` once as a heading and then rows carrying the folio alone. The record file does not.

## Tasks

- [ ] !! RULE IT FIRST: does a RECORD carry a bare folio with the page named above
      it, or does it keep the whole address and only the LISTING group? The first
      saves the 30KB and makes every consumer page-aware; the second saves nothing
      in the record file.
- [ ] Every consumer reads the address as one string -- `record.entry_for`,
      `galley.py`'s `--edits`, `desk.address_problem`, `verdicts.py`'s join.
      `addresser.folio_of` already splits the halves and is the seam.
- [ ] ! A held report from 0.2.4 carries whole addresses. Whatever is ruled,
      reading one must keep working -- that is the bridge `held.py` exists for.
- [ ] Re-measure after: the figure above is one repo's 15 files, and the saving
      scales with how deep the paths are.
