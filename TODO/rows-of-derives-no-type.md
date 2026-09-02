# The binder derives dicts where the docket derives a type

```
Status:   open
Progress: 0 of 4 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-30 (2026-08-30, comparing the containers in the middle against the
          structures at either end before typing them -- Roy: "Just to make certain we
          haven't introduced hidden bugs that could cause problems")
```

## Objective

The binder derives dicts where the docket derives a type.

## Tasks

- [ ] T1 | Measure what a caller of `rows_of` actually reads. Verify: for each
      of the 8 call sites, name which keys it takes off the dict and whether a
      missing or misspelled one would raise, return wrong, or pass silently.
      That list is the finding, and it decides whether this is a defect or a
      style difference.
- [ ] T2 | Compare against the docket's `schedules_of`, which derives a
      `Schedule` NamedTuple. Verify: state in one sentence why the docket needed
      a type and the binder did not, or that it did and nobody noticed --
      `docket.py:190` says the view REFUSES NOTHING because `read` already ruled
      on the shape, and `bind()` has no equivalent guarantee stated.
- [ ] T3 | Give `rows_of` a derived type, or record why it keeps a dict. Verify:
      either it returns a NamedTuple following `Schedule`, or this file records
      why a dict is right here and the reason survives someone asking again.
- [ ] T4 | Cover the call sites. Verify: `rows_of` has a test -- it has NONE
      today across 8 callers in `commands/taken_in.py`, `commands/addresser.py`,
      `commands/census.py` and `desk/collator.py`.
