# page.py and addresser.py carry four scans that grow with the file and one CLI that contradicts the gate

```
Status:   in-progress
Progress: 2 of 8 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-22 (C:/Program Files/Git/simplify rounds 1 and 2 and /code-review high
          round 3, 2026-08-22)
RE-VERIFIED: 2026-08-23 -- 2026-08-23. TWO FIXED and ticked: task 1, main() no longer re-
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
reach. The last task is the standard the other four are held to: a before-and-after number from
a run.

**The four scans, as measured 2026-08-22:**

- `addresser.unaddressed` and `addresser._check` both group by path with a full rescan, and
  `_check` is the sum of P squared per file -- **142,103 iterations on this repo, about 8 million
  at 200 files.**
- `page.fill_the_gaps` and `page.tie_leading` are each O(code x paragraphs) with a `str.split`
  per step.
- `page.declarations()` runs TWICE per file -- `page.py:420` and `page.py:726`, re-confirmed by
  grep 2026-08-23. The second call is DEAD for Python: every row comes back `above=False` and is
  then skipped, so a Python file is parsed three times per page, **about 8% of a run.**
- `addresser.for_anchor` reaches into SEVEN census-entry fields and re-derives *the gap above* as
  `at - 1`, inside the module whose own docstring says it knows nothing about a paragraph. The
  addresser's stated rule is `series_of(address)` -- *"an `a` declares, a `c` has a column, a `b`
  has neither. No second field, no inference from kind."*

**The two that are FIXED, kept so the shape stays legible:**

- `main()` re-derived addressability instead of asking `unaddressed()`. MEASURED on a healthy
  census when it was live: `--census` reported *2 entries could not be addressed*, EXIT 1, while
  `--check` on the same file said *17 of 17 addressed*, exit 0 -- two answers from one module
  about one question. Both call sites now ask `unaddressed(paragraphs)`, at `addresser.py:1192`
  and `:1423`.
- `addresser.py:672` typed `documentable` as `dict[int, int]` while the walk unpacked a
  THREE-TUPLE from it, so the doc contradicted the code one screen below. It is now
  `dict[int, tuple[int, int, str]]` at `addresser.py:626`, and the Args block at `:661-663` says
  the body unpacks all three.

## Tasks

- [x] T1 -- FIXED 2026-08-23. Both call sites ask `unaddressed(paragraphs)`. The
      two-answers measurement is in the Objective.
- [ ] T2 -- Make `addresser.unaddressed` and `_check` group by path ONCE, not rescan.
      Verify: the iteration count falls and `--check` reports the same addresses.
- [ ] T3 -- Stop `page.fill_the_gaps` being O(code x paragraphs). Verify: the steps are
      not the product and the fixture census is byte-identical.
- [ ] T4 -- Stop `page.tie_leading` being O(code x paragraphs). Verify: the steps are not
      the product and the fixture census is byte-identical.
- [ ] T5 -- Stop `page.declarations()` running TWICE per file (`page.py:420`, `:726`).
      Verify: `grep -n 'declarations(' page.py` returns ONE call site, census unchanged.
- [ ] T6 -- Stop `addresser.for_anchor` reading census-entry fields its own rule does not
      name. Verify: it reads only what `series_of(address)` names.
- [x] T7 -- FIXED 2026-08-23. `documentable` is annotated as the three-tuple the walk
      unpacks, and the Args block says so. The contradiction as filed is in the Objective.
- [ ] T8 -- Put a before and an after number in this file, from a 200-file run. Verify:
      this file carries both a wall-clock and an iteration count, not a prediction.
