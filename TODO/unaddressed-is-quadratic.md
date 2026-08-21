# unaddressed() groups by path for a question that needs one flat pass

```
Status:   open
Progress: 0 of 4 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-21 (the /code-review xhigh of 2026-08-21, focused on the file-to-
          census route)
```

## Objective

unaddressed() groups by path for a question that needs one flat pass.

## Tasks

- [ ] MEASURED on this repo's own census -- 24,804 paragraphs over 52 files --
      0.086s against 0.002s for a flat pass. 43x, and quadratic in file count.
      `stable(paragraph)` does not depend on the grouping, so it buys nothing.
- [ ] It is called at three sites now: `census.py` on the JSON path, `census.py`
      on the text path, and `verdicts.py` on read. ! The text path additionally
      rebuilds the full `vars(b) | {...}` copy that the JSON path was refactored
      to build once.
- [ ] ! `_check` repeats the same structure and adds a `resolve()` per paragraph.
- [ ] ! `census.py --out` leaves an EMPTY FILE behind when it refuses: `main()`
      truncates the file before `_report` runs, and the refusal prints to stderr
      and returns 1. The exit code is right, so only a caller testing for the file
      is misled.
