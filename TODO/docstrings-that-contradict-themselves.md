# Four shipped docstrings still contradict themselves or their own bodies

```
Status:   blocked (on the first v0.2.4 dogfood run -- these pairs are its graded finding)
Progress: 2 of 6 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-20 (the branch review of 2026-08-20)
RE-READ:  2026-08-23 — 2026-08-23. Every line number in the previous version was stale,
          so each pair was re-read in the code as it stands rather than grepped. RESULT:
          four of the six still contradict, two do not. Task 2 is SUPERSEDED -- the
          galley was rewritten and both halves are gone. Task 4 stays FINISHED. Tasks 1,
          3, 5 and 6 SURVIVE at new locations, and task 1 is WORSE than filed: the same
          function now prints the advice its own docstring calls retired. The line
          numbers below were read on 2026-08-23 and will go stale again.
DOGFOOD:  2026-08-23 — 2026-08-23, Roy: 'if we can finally get to the finish of v0.2.4
          we have the tool to get this correct.' This file is the tool's own remit --
          block-context asks whether every claim in a paragraph is true of the code it
          sits with, and function-context asks whether name, signature, docstring and
          body disagree. ! So do NOT hand-fix these pairs: they are the subject of the
          first real dogfood run, and hand-fixing them destroys the finding the run
          would be graded on. Each task below is CLOSED BY THE RUN REPORTING IT, not by
          an editor rewriting it.
```

## Objective

Shipped docstrings that contradict themselves or their own bodies. **Six at filing; four survive
at 2026-08-23.** They are held, not fixed, because they are the graded input to the first
dogfood run of this tool on its own scripts.

! Two closed on their own, which is why the file is re-read rather than trusted: the galley was
rewritten out from under one pair, and the set-comparison that justified another was deleted.

## Tasks

- [ ] T1 -- `addresser._check` (`addresser.py:1389-1465`). The docstring says at `:1408` *"SHARED
      IS NOW A FAULT TOO"*; the `Returns:` section of the SAME docstring says at `:1417-1419`
      *"A shared place does not fail the check"*; the code at `:1465` is `return 1 if missing
      else 0`. !! AND IT IS WORSE THAN FILED: `:1409-1411` says the old remedy was to *"cite the
      census INDEX alongside the address -- a field retired 2026-08-19"*, while the body at
      `:1455-1459` still PRINTS *"cite the census index alongside the address for those"*. The
      docstring calls the advice retired and the function gives it. Closed by the run reporting
      the pair.

- [x] T2 -- SUPERSEDED. The contradiction was `galley.py:253-255` against `:269-273`, about
      falling back from `original_*` to `start`/`end`. `galley.py` is 477 lines and holds
      `reset`, `_vacate` and `drifted`; `paragraph_matches` and `splice` are retired
      (`lexer.py:202` calls it *"the retired `paragraph_matches`"*), and the word "fallback" does
      not occur in the file. Both halves are gone.

- [ ] T3 -- `lexer.Paragraph` (`lexer.py:212-255`), ONE comment block documenting
      `original_start`/`original_end`. At `:215-217` it says an empty INTERVAL *"reports `(n+1,
      n)`"*; at `:247-249`, same block, *"SO THERE IS NO EMPTY-SLICE SENTINEL. `(n, n - 1)` used
      to say 'holds nothing' ... `None` cannot be mistaken for a position."* !! MEASURED
      2026-08-23 on `census.py --json` over `exceptions.py`: an empty `interval` emits
      `start=0, end=0, original_start=None, original_end=None`. Neither spelling is what the
      census produces, so the first half is false about the code it sits in. Closed by the run
      reporting it.

- [x] T4 -- FINISHED. `page.py:102-107` called `HOLDS_NO_PROSE` *"a DIFFERENT set, and the two
      are not interchangeable"* while `set(OCCUPIES_NOTHING) == set(HOLDS_NO_PROSE)` was `True`.
      Both module constants are gone; the two questions are now `Kind.holds_no_prose` and
      `Kind.occupies_no_lines` (`lexer.py:408`, `:429`), and `page.py:100-101` states why there
      are two.

- [ ] T5 -- `record.entry_for` (`record.py:743-762`). At `:751-753` it says *"an address
      identifies exactly one paragraph, held by `addresser.py --check` on every run"* -- and
      `--check` does not hold it: `addresser.py:1417-1419` says in its own words that a shared
      place does not fail, and `:1465` returns 0 on one. The same docstring then says *"`--check`
      is what reports it"*, which is true, so the paragraph asserts both enforcement and mere
      reporting. ! Its neighbour is the same defect at file scope: `record.py:37-42` still tells
      a reviewer filing an `add` to write *"that interval's index and address"*, and the index
      was retired 2026-08-19 -- `record.slot()`'s own comment at `:680-681` says a slot *"has
      carried an ADDRESS and no index since 2026-08-18"*.

- [ ] T6 -- Retired concepts still named, re-read 2026-08-23. STILL LIVE: `desk.py:557` asks
      *"Does the record's address name the paragraph the census has at that index?"* while the
      body resolves through `entry_for(address)`; `desk.py:246` says `_resolve_lines` is *"Shared
      by SOURCES and LOCATION"* when `LOCATION` was dropped -- and `desk.py:567` in the same file
      says so; `verdicts.py:120` *"Indices each reviewer left unaccounted for"* over a body that
      keys `f.address`; `verdicts.py:194` documents an argument as *"findings by census paragraph
      index"* when `by_paragraph` returns a dict keyed by address; `verdicts.py:634` names its
      loop variable `index` while iterating addresses. RESOLVED: `held.py` no longer says *"two
      records that share an index"* -- its one remaining mention, `:126`, says the address IS the
      key.
