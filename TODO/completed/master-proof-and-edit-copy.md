# The middle has no container for one stage's marks, so nothing can reconcile them

```
Status:   open
Progress: 5 of 5 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-29 (2026-08-29, designing P4 with Roy -- `binder` goes out and
          `docket` comes back, and the N marked copies in between had no name, no shape
          and no validator)
```

## Objective

The middle has no container for one stage's marks, so nothing can reconcile them.

## Tasks

- [x] T1 | FINISHED | unknown | Give `seed` the sheets level: an `edit_copy` is
      `{role, read_from, sheets: [{path, sha, marks}]}`, mirroring the binder's
      pages. Verify: an `edit_copy` names every page it was given, and a fan-out
      shard's `edit_copy` names only its own.
- [x] T2 | FINISHED | unknown | Carry the sha on the sheet, so nothing
      downstream reads the binder for it. Verify: a docket can be built from a
      `master_proof` alone, and no module outside `binder/` imports
      `binder.read` to obtain a sha.
- [x] T3 | FINISHED | unknown | Build the `master_proof`: `{stage, read_from,
      edit_copies: [...]}`. Verify: it holds every `edit_copy` of one stage, a
      stage with one role and a stage with seven shards both assemble, and it
      refuses an `edit_copy` whose `read_from` disagrees with the others'.
- [x] T4 | FINISHED | unknown | Move `problems_in` and `verify_report` onto
      sheets. Verify: both walk `sheets` rather than a flat `marks` list, and
      the suite passes with no expectation edited -- only the shape the tests
      read.
- [x] T5 | FINISHED | unknown | Rename the per-role container from `sheet` to
      `edit_copy` in `flows/marks.py`, `SKILL.md` and `reviewer-brief.md`, and
      give `sheet` the page-unit sense. Verify: no agent-facing file calls the
      per-role container a sheet, and `docs/vocabulary.md` carries all four
      containers with `master proof` no longer marked unnamed.
