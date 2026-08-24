# unaddressed() groups by path for a question that needs one flat pass

```
Status:   open
Progress: 0 of 4 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-21 (the /code-review xhigh of 2026-08-21, focused on the file-to-
          census route)
Triaged:  2026-08-23 -- three of the four boxes were MEASUREMENTS, not checkpoints; the
          work they describe is now stated as four tasks a stranger can call done
```

## Objective

`unaddressed()` builds a per-path grouping for a question that reads one paragraph at a
time. `addresser.py:1334` calls `sorted(_by_path(paragraphs).items())` and then tests
`owes_address(paragraph) and not stable(paragraph)` per paragraph -- neither predicate
reads the path, so the grouping and the sort buy nothing.

MEASURED 2026-08-21 on this repo's own census -- 24,804 paragraphs over 52 files --
**0.086s against 0.002s for a flat pass**, 43x. ! That measurement predates the
`owes_address` / `stable` split of 2026-08-22, so it has to be re-taken before and after
any change rather than quoted.

! **Three call sites ask this question**, verified 2026-08-23: `census.py:435` on the JSON
path, `census.py:639` on the text path, and `verdicts.py:354` on read. The text path
rebuilds the full `[vars(b) | {"annotations": sorted(b.annotations)} for b in census]`
copy that the JSON path was refactored to build once at `census.py:434`.

! **`_check` repeats the same structure and adds a `resolve()` per paragraph.**
`addresser.py:1427` walks `_by_path(paragraphs).values()` and calls
`resolve(where, mine)` for every paragraph in the group, which is quadratic within a file.

! **A second, separable defect is in the same route.** `census.py --out` leaves an EMPTY
FILE behind when it refuses: `main()` truncates the file before `_report` runs, and the
refusal prints to stderr and returns 1. The exit code is right, so only a caller that
tests for the file is misled.

## Tasks

- [ ] T1 -- Flatten `unaddressed()` in `addresser.py` to one pass over `paragraphs`,
      dropping `_by_path` and the sort from it. ! The `entry N` ordinal in its output
      counts within a file, so the flat pass has to keep a per-path counter or the
      sentences it emits change meaning. Verify: `uv run pytest -q` green, and the
      sentences `unaddressed()` returns for this repo's census are byte-identical before
      and after.

- [ ] T2 -- Re-take the timing on the CURRENT code, before and after T1, and record both
      numbers in this file. ! The 0.086s/0.002s pair above was measured before the
      `owes_address`/`stable` split, so it is not the baseline. Verify: two numbers in
      this file, each with the command that produced it.

- [ ] T3 -- Build the census row list ONCE on the text path. `census.py:639` rebuilds
      `vars(b) | {"annotations": sorted(b.annotations)}` that `census.py:434` already
      builds on the JSON path. Verify: `grep -c "vars(b) | {" census.py` returns 1.

- [ ] T4 -- `census.py --out` must not leave an empty file behind on a refusal. Verify: a
      test that runs `census.py --out <path>` on input the gate refuses, asserts exit 1,
      and asserts `<path>` does not exist -- and that fails on the current code first.
