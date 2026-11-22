# The concordance states its gaps twice, in two vocabularies

```
Status:   open
Progress: 5 of 12 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-24 (Roy, 2026-08-24: are referrers and code_names one workflow?)
```

## Objective

The concordance states its gaps twice, in two vocabularies.

## Tasks

- [ ] T1 | Name the three gap states once, in concordance/
- [ ] T2 | Both harvesters return that type instead of prose rows
- [ ] T3 | The reporting caller reads the type, not the wording, so a reworded
      gap cannot be reclassified silently
- [ ] T4 | Say whether referrers has a 'did not look here' state, or genuinely
      cannot
- [-] T5 | SUPERSEDED by T10: the list is now 68,285 bytes with 565 rows, not 50 KB | 22c3a0abcbc86509c74296319ce5b719a43338ca | Print
      NOT CHECKED gaps with repo-relative paths and a cap, as FREEFORM is
      capped; the list is 50 KB on this repo
- [-] T6 | Moot: the annotations it improves are removed; Process #320 | f5bb9ab6f78f12d239d415202b9de696b1fff9f1 | Reword
      gather's NOT CHECKED footer; the symbol notes it qualifies never reach the
      binder
- [-] T7 | Revoked with the gather grouping (#271) | a75f0638 | Correct
      one_row_per_hole's docstring: the WALKED_TREE row is not a failed file
- [-] T8 | Revoked: one_row_per_hole is gone (#271) | a75f0638 | Group known
      holes inside code_names, where path and name are data, and test gather's
      printed output
- [ ] T9 | Rename the paragraph annotations when the glossary and index are
      built, per Process #273
- [-] T10 | SUPERSEDED by T11, T12: held two acts; split | 22c3a0abcbc86509c74296319ce5b719a43338ca | Cap
      gather's NOT CHECKED gap rows, printing repo-relative paths, as FREEFORM
      is capped
        > 2026-11-22 Check: a one-file gather prints at most the cap, no absolute path
- [ ] T11 | Bound gather's NOT CHECKED gap rows the way FREEFORM rows are
      bounded
        > 2026-11-22 Check: one gather prints at most the FREEFORM cap of gap rows
- [ ] T12 | Print gather's NOT CHECKED gap paths relative to the repo
        > 2026-11-22 Check: no gap row carries an absolute path
