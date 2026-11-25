# unaddressed() groups by path for a question that needs one flat pass

```
Status:   open
Progress: 4 of 6 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-21 (the /code-review xhigh of 2026-08-21, focused on the file-to-
          census route)
Triaged:  2026-08-23 -- three of the four boxes were MEASUREMENTS, not checkpoints; the
          work they describe is now stated as four tasks a stranger can call done
Split:    2026-08-23 -- boxes cut to two lines each; the `entry N` ordinal caveat moved
          into the Objective
```

## Objective

`unaddressed()` builds a per-path grouping for a question that reads one
paragraph at a time. `addresser.py:1334` calls
`sorted(_by_path(paragraphs).items())` and then tests `owes_address(paragraph)
and not stable(paragraph)` per paragraph -- neither predicate reads the path, so
the grouping and the sort buy nothing.

MEASURED 2026-08-21 on this repo's own census -- 24,804 paragraphs over 52 files
-- **0.086s against 0.002s for a flat pass**, 43x. ! That measurement predates
the `owes_address` / `stable` split of 2026-08-22, so it has to be re-taken
before and after any change rather than quoted.

!! **THE FLAT PASS STILL OWES A PER-PATH COUNTER.** The `entry N` ordinal in
`unaddressed()`'s output counts WITHIN a file, so dropping `_by_path` without
keeping a per-path counter changes what every sentence it emits means -- which
is why the check on that change is byte-identity of the sentences, not merely a
green suite.

! **Three call sites ask this question**, verified 2026-08-23: `census.py:435`
on the JSON path, `census.py:639` on the text path, and `verdicts.py:354` on
read. The text path rebuilds the full `[vars(b) | {"annotations":
sorted(b.annotations)} for b in census]` copy that the JSON path was refactored
to build once at `census.py:434`.

! **`_check` repeats the same structure and adds a `resolve()` per paragraph.**
`addresser.py:1427` walks `_by_path(paragraphs).values()` and calls
`resolve(where, mine)` for every paragraph in the group, which is quadratic
within a file.

! **A second, separable defect is in the same route.** `census.py --out` leaves
an EMPTY FILE behind when it refuses: `main()` truncates the file before
`_report` runs, and the refusal prints to stderr and returns 1. The exit code is
right, so only a caller that tests for the file is misled.

## Tasks

- [-] T1 | SUPERSEDED by T5: unaddressed() now lives in binder/addresses.py; census sentences are gone | 22c3a0abcbc86509c74296319ce5b719a43338ca | T1
      -- Flatten `unaddressed()` to one pass, dropping `_by_path` and the sort.
      Verify: `uv run pytest -q` green and its census sentences byte-identical
      before and after.
- [ ] T2 | T2 -- Re-take the `unaddressed()` timing on the current code, before
      and after T1. Verify: two numbers in this file, each with the command that
      produced it.
- [-] T3 | 36f1e404 removed gather's text listing; no `vars(b) / {` row copy remains in src/ | 36f1e404 | T3
      -- Build the census row list ONCE on the text path, reusing what
      `census.py:434` already builds. Verify: `grep -c "vars(b) \| {" census.py`
      returns 1.
- [-] T4 | SUPERSEDED by T6: census.py became commands/gather.py, which opens --out before _report refuses | 22c3a0abcbc86509c74296319ce5b719a43338ca | T4
      -- Stop `census.py --out` leaving an empty file behind on a refusal.
      Verify: a test asserting exit 1 and no `<path>` fails today and passes
      after.
- [ ] T5 | Flatten binder/addresses.unaddressed() to one pass without the
      _by_path sort
        > 2026-11-22 Check: suite green; gather's unaddressed lines byte-identical
- [x] T6 | A refused gather leaves no --out file | bf44bb44 | Stop `gather
      --out` leaving an empty file behind when the gather refuses
        > 2026-11-22 Check: a refused gather --out X exits 1 with no file at X
