# The filtered-census measurement exists only in run history

```
Status:   open
Progress: 0 of 5 tasks done
Owner:    session * Roy (the runs are his)
Requires-Roy: true
Raised:   2026-08-20 (Roy, 2026-08-20, correcting a claim that only size had been
          measured)
```

## Objective

The filtered-census measurement exists only in run history.

## Tasks

- [ ] !! RECOVER THE v0.1.0 -> v0.2.0 COMPARISON. Roy: going unfiltered, 'the
      agents got a lot more tokens and used a lot more tokens on effectively the
      same level of output. They did miss a lot in the difference.' Nothing in
      `evidence/` records it; the shipped tree carries only the byte figures.
- [ ] ! It is the justification for `--filtered`, which is the single most
      consequential thing about what a reviewer sees -- it REMOVES information
      from the census a role reads. The only numbers written down measure how much
      SMALLER it made the prompt: 39% of the listing was repeated paths,
      `--filtered` saved 61%. Those are the cost, not the benefit.
- [ ] State what was compared, over what, and what 'missed a lot' counts --
      findings, hazards, or something else. A recall claim with no denominator is
      the shape this repo already retired once, as `acquittal rate`.
- [ ] ! It is the baseline the PAGE has to beat, and the page claims to beat BOTH
      formats at once -- more information than filtered, fewer tokens than
      unfiltered. Without the prior recorded there is nothing to hold it to.
- [ ] * RULING WANTED from Roy: where the runs are, or whether the comparison must
      be re-run. Only he has the history.
