# page.py and addresser.py carry four scans that grow with the file and one CLI that contradicts the gate

```
Status:   in-progress
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
TRIAGED:  2026-08-23 -- second pass. BOTH RE-VERIFICATIONS ABOVE RE-RUN AND BOTH HOLD:
          `unaddressed(paragraphs)` at addresser.py:1192 and :1423 (T1 stays ticked);
          `documentable: dict[int, tuple[int, int, str]]` at addresser.py:626, and the
          docstring at :661-663 now says the body unpacks all three (T6 stays ticked);
          `declarations(text, lang, code)` at page.py:420 and again at page.py:726 inside
          `document_declarations` (T4 STILL LIVE, re-confirmed by grep, not by reading a
          note). ! FIVE BOXES WERE MEASUREMENTS WITH THE WORK LEFT IMPLICIT and are
          rewritten as tasks with the measurement kept as the reason; none is ticked,
          because none of the work has been done.
```

## Objective

`page.py` and `addresser.py` carry four scans that grow with the file, and the two modules were
reviewed together because the scans cross them.

!! **THE MEASUREMENTS ARE THE REASON, NOT THE WORK.** Each task below states what was measured on
this repo and what the same shape costs at 200 files, which is the size the tool is meant to
reach. T7 is the standard the other four are held to: a before-and-after number from a run.

## Tasks

- [x] T1 -- FIXED 2026-08-23. addresser.py:1202 -- main() re-derived addressability instead of
      asking unaddressed(). MEASURED on a healthy census when it was live: --census reported
      *2 entries could not be addressed*, EXIT 1, while --check on the same file said *17 of
      17 addressed*, exit 0 -- two answers from one module about one question. Now both call
      sites ask `unaddressed(paragraphs)`, at addresser.py:1192 and :1423.

- [ ] T2 -- Make `addresser.unaddressed` and `_check` group by path ONCE instead of rescanning.
      MEASURED: both group by path with a full rescan, and `_check` is the sum of P squared per
      file -- 142,103 iterations on this repo, about 8 million at 200 files. Verify: the
      iteration count on this repo falls, and `--check` reports the same addresses it does
      today on the same census.

- [ ] T3 -- Make `page.fill_the_gaps` and `page.tie_leading` stop being O(code x paragraphs)
      with a `str.split` per step. Verify: the census is byte-identical before and after on the
      fixture corpus, and the step count is no longer the product.

- [ ] T4 -- Stop `page.declarations()` running TWICE per file. STILL LIVE, re-confirmed
      2026-08-23: page.py:420 and page.py:726. The second call is DEAD for Python -- every row
      comes back `above=False` and is then skipped -- so a Python file is parsed three times per
      page, about 8% of a run. Verify: `grep -n 'declarations(' page.py` returns ONE call site,
      and the census is unchanged on the fixture corpus.

- [ ] T5 -- Stop `addresser.for_anchor` reaching into SEVEN census-entry fields and re-deriving
      *the gap above* as `at - 1`, inside the module whose own docstring says it knows nothing
      about a paragraph. Verify: `for_anchor` reads no census-entry field the addresser's stated
      rule does not name (`series_of(address)` -- *"an `a` declares, a `c` has a column, a `b`
      has neither. No second field, no inference from kind."*).

- [x] T6 -- FIXED 2026-08-23. addresser.py:672 typed `documentable` as `dict[int, int]` while the
      walk unpacked a THREE-TUPLE from it, so the doc contradicted the code one screen below. It
      is now `dict[int, tuple[int, int, str]]` at addresser.py:626, and the Args block at
      :661-663 says the body unpacks all three.

- [ ] T7 -- MEASURE BEFORE AND AFTER, and put both numbers in this file. The four scans above are
      invisible on a 17-file review and are the whole cost on a 200-file one, which is the size
      this is meant to reach. Verify: this file carries a before and an after wall-clock and
      iteration count from a 200-file run, not a prediction.
