# page.py and addresser.py carry four scans that grow with the file and one CLI that contradicts the gate

```
Status:   open
Progress: 2 of 7 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-22 (C:/Program Files/Git/simplify rounds 1 and 2 and /code-review high
          round 3, 2026-08-22)
RE-VERIFIED: 2026-08-23 — 2026-08-23. TWO FIXED and ticked: task 1, main() no longer re-
             derives addressability -- it calls unaddressed(paragraphs) at
             addresser.py:1192 and :1423; task 6, the type contradiction is gone --
             documentable is annotated dict[int, tuple[int, int, str]] at
             addresser.py:626, which is the three-tuple the walk actually unpacks. !
             STILL LIVE: task 4, declarations() still runs twice per file (page.py:420
             and :726). Tasks 2, 3, 5 and 7 are cost claims that need a measurement to
             settle rather than a grep, and task 7 says so itself -- MEASURE BEFORE AND
             AFTER, invisible on a 17-file review and the whole cost on a large one.
```

## Objective

page.py and addresser.py carry four scans that grow with the file and one CLI that contradicts the gate.

## Tasks

- [x] addresser.py:1202 -- main() re-derives addressability instead of asking
      unaddressed(). MEASURED on a healthy census: --census reports *2 entries
      could not be addressed*, EXIT 1, while --check on the same file says *17 of
      17 addressed*, exit 0. Two answers from one module about one question
- [ ] addresser.unaddressed and _check group by path with a full rescan, and _check
      is the sum of P squared per file. MEASURED: 142,103 iterations on this repo,
      about 8 million at 200 files
- [ ] page.fill_the_gaps and tie_leading are both O(code x paragraphs) with a
      str.split per step
- [ ] page.py -- declarations() runs TWICE per file and the second call is DEAD
      for Python: every row comes back above=False and is then skipped. About 8%
      of a run, and a Python file is parsed three times per page
- [ ] addresser.for_anchor reaches into SEVEN census-entry fields and re-derives
      *the gap above* as at - 1, inside the module whose own docstring says it
      knows nothing about a paragraph
- [x] addresser.py:672 types documentable as dict[int, int] and the walk unpacks a
      THREE-TUPLE from it; the doc contradicts the code one screen below
- [ ] ! MEASURE BEFORE AND AFTER. The four scans above are invisible on a 17-file
      review and are the whole cost on a 200-file one, which is the size this is
      meant to reach
