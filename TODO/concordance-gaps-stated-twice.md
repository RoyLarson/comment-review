# The concordance states its gaps twice, in two vocabularies

```
Status:   open
Progress: 0 of 8 tasks closed
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
- [ ] T5 | Print NOT CHECKED gaps with repo-relative paths and a cap, as
      FREEFORM is capped; the list is 50 KB on this repo
- [ ] T6 | Reword gather's NOT CHECKED footer; the symbol notes it qualifies
      never reach the binder
- [ ] T7 | Correct one_row_per_hole's docstring: the WALKED_TREE row is not a
      failed file
- [ ] T8 | Group known holes inside code_names, where path and name are data,
      and test gather's printed output
