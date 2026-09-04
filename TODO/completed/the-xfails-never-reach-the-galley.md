# Seven of the eight expectedFailures never reach the code they name

```
Status:   in-progress
Progress: 3 of 3 tasks closed
Owner:    testing
Requires-Roy: false
Raised:   2026-08-20 (the branch review of 2026-08-20; threatens plan box R7)
Closed:   2026-08-23 -- all three tasks SUPERSEDED. The eight expectedFailures are gone
          and `_gap` looks a place up by ADDRESS. Ready to move to TODO/completed/
```

## Objective

Seven of the eight `expectedFailure` cases in `tests/test_galley.py` never reached the code they
named. `_gap` looked an interval up by `(original_start, original_end) == (2,1)` / `(1,0)` /
`(4,3)` -- the RETIRED `(n, n-1)` form -- while the census emitted `(None, None)`, so seven
raised `AssertionError: no gap editing ...` INSIDE THE HELPER and the eighth failed comparing
`(None, None)` to itself. `galley.splice_range` and `paragraph_matches` were never reached.

!! **THE WHOLE FILE IS SUPERSEDED, VERIFIED 2026-08-23**, and by the change the 0.2.4 rework
landed rather than by a repair to this suite:

| what this file claimed | what the tree says now |
| --- | --- |
| eight `@unittest.expectedFailure` cases stand | `grep -rn "@unittest.expectedFailure" tests/ --include=*.py` returns **zero decorators**; the one hit in `test_galley.py:175` is PROSE naming the retired ones |
| `_gap` looks up by `(original_start, original_end)` | `test_galley.py:190-194` matches `b.address.split("@")[-1] == cue`. `grep -n original_start tests/test_galley.py` returns **0 lines** |
| the class docstring claims an unexpected-success mechanism that does not exist | it now reads *"EIGHT OF THESE WERE `@unittest.expectedFailure` UNTIL 2026-08-21"* and states why the splice could not do any of them |
| plan box R7 is UNJUDGEABLE | `docs/plans/0.2.4-rework-the-foliator-owns-the-address.md:461` records R7 DONE 2026-08-21, and `:445-450` records this file as no longer threatening it |

! **The cause is the address system, not a test fix.** An empty gap had no lines, so its range was
`n+1 .. n`, and at the file's edges both bounds clamped to 1 -- so the address could not say which
side of line 1 a gap was on. A page has a PLACE for the gap and the compositor sets the places in
order; there is no range, so there is nothing to clamp, and the eight cases pass as ordinary tests
in `TestAnAddIntoAnEmptyGap`.

! **This is a MEASUREMENT the file was right about when it was written.** It is kept checked
rather than deleted so the error stays legible -- a suite can be green, and eight cases can be
red on purpose, while neither of them touches the code they name.

## Tasks

- [x] T1 | FINISHED | unknown | T1 -- SUPERSEDED. `_gap` no longer looks a place
      up by `(original_start, original_end)`. Verified 2026-08-23:
      `tests/test_galley.py:190-194` resolves a cue against `b.address`, and
      `original_start` appears nowhere in the file.

- [x] T2 | FINISHED | unknown | T2 -- SUPERSEDED. The class docstring no longer
      claims *"each reports an UNEXPECTED SUCCESS the moment the galley works
      from addresses"*. `test_galley.py:175-186` states what the eight were and
      why the splice could not do them.

- [x] T3 | FINISHED | unknown | T3 -- SUPERSEDED. Plan box R7 -- *"no
      expectedFailure survives this plan"* -- is judgeable and judged.
      `docs/plans/0.2.4-rework-the-foliator-owns-the-address.md:461` ticks it
      DONE 2026-08-21, verifiable by `grep -rn "@unittest.expectedFailure"
      tests/ --include=*.py`.
