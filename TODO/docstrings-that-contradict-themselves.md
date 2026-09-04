# Four shipped docstrings still contradict themselves or their own bodies

```
Status:   blocked (on the first v0.2.4 dogfood run -- these pairs are its graded finding)
Progress: 2 of 12 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-20 (the branch review of 2026-08-20)
RE-READ:  2026-08-23 -- 2026-08-23. Every line number in the previous version was stale,
          so each pair was re-read in the code as it stands rather than grepped. RESULT:
          four of the six still contradict, two do not. Task 2 is SUPERSEDED -- the
          galley was rewritten and both halves are gone. Task 4 stays FINISHED. Tasks 1,
          3, 5 and 6 SURVIVE at new locations, and task 1 is WORSE than filed: the same
          function now prints the advice its own docstring calls retired. The line
          numbers below were read on 2026-08-23 and will go stale again.
DOGFOOD:  2026-08-23 -- 2026-08-23, Roy: 'if we can finally get to the finish of v0.2.4
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

## The pairs, as read on 2026-08-23

**`addresser._check` (`addresser.py:1389-1465`) contradicts itself twice.** The docstring says at
`:1408` *"SHARED IS NOW A FAULT TOO"*; the `Returns:` section of the SAME docstring says at
`:1417-1419` *"A shared place does not fail the check"*; the code at `:1465` is `return 1 if
missing else 0`. !! AND IT IS WORSE THAN FILED: `:1409-1411` says the old remedy was to *"cite
the census INDEX alongside the address -- a field retired 2026-08-19"*, while the body at
`:1455-1459` still PRINTS *"cite the census index alongside the address for those"*. The
docstring calls the advice retired and the function gives it.

**`lexer.Paragraph` (`lexer.py:212-255`), ONE comment block documenting
`original_start`/`original_end`.** At `:215-217` it says an empty INTERVAL *"reports `(n+1, n)`"*;
at `:247-249`, same block, *"SO THERE IS NO EMPTY-SLICE SENTINEL. `(n, n - 1)` used to say 'holds
nothing' ... `None` cannot be mistaken for a position."* !! MEASURED 2026-08-23 on
`census.py --json` over `exceptions.py`: an empty `interval` emits `start=0, end=0,
original_start=None, original_end=None`. Neither spelling is what the census produces, so the
first half is false about the code it sits in.

**`record.entry_for` (`record.py:743-762`) asserts enforcement and mere reporting at once.** At
`:751-753` it says *"an address identifies exactly one paragraph, held by `addresser.py --check`
on every run"* -- and `--check` does not hold it: `addresser.py:1417-1419` says in its own words
that a shared place does not fail, and `:1465` returns 0 on one. The same docstring then says
*"`--check` is what reports it"*, which is true.

**Its neighbour is the same defect at file scope.** `record.py:37-42` still tells a reviewer
filing an `add` to write *"that interval's index and address"*, and the index was retired
2026-08-19 -- `record.slot()`'s own comment at `:680-681` says a slot *"has carried an ADDRESS and
no index since 2026-08-18"*.

**Retired concepts still named, re-read 2026-08-23 and STILL LIVE:** `desk.py:557` asks *"Does
the record's address name the paragraph the census has at that index?"* while the body resolves
through `entry_for(address)`; `desk.py:246` says `_resolve_lines` is *"Shared by SOURCES and
LOCATION"* when `LOCATION` was dropped -- and `desk.py:567` in the same file says so;
`verdicts.py:120` *"Indices each reviewer left unaccounted for"* over a body that keys
`f.address`; `verdicts.py:194` documents an argument as *"findings by census paragraph index"*
when `by_paragraph` returns a dict keyed by address; `verdicts.py:634` names its loop variable
`index` while iterating addresses. ! RESOLVED: `held.py` no longer says *"two records that share
an index"* -- its one remaining mention, `:126`, says the address IS the key.

## The two that closed on their own

**The galley pair is SUPERSEDED.** It was `galley.py:253-255` against `:269-273`, about falling
back from `original_*` to `start`/`end`. `galley.py` is 477 lines and holds `reset`, `_vacate`
and `drifted`; `paragraph_matches` and `splice` are retired (`lexer.py:202` calls it *"the
retired `paragraph_matches`"*), and the word "fallback" does not occur in the file.

**The `HOLDS_NO_PROSE` pair is FINISHED.** `page.py:102-107` called it *"a DIFFERENT set, and the
two are not interchangeable"* while `set(OCCUPIES_NOTHING) == set(HOLDS_NO_PROSE)` was `True`.
Both module constants are gone; the two questions are now `Kind.holds_no_prose` and
`Kind.occupies_no_lines` (`lexer.py:408`, `:429`), and `page.py:100-101` states why there are two.

## Tasks

- [ ] T1 | T1 -- `addresser._check`: the docstring says a shared place IS a
      fault and also is not, while `:1465` returns 0. Verify: the dogfood run
      reports the pair.
- [ ] T2 | T2 -- `addresser._check` PRINTS the census-index advice its own
      docstring calls retired (`:1409-1411` against `:1455-1459`). Verify: the
      dogfood run reports it.
- [x] T3 | FINISHED | unknown | T3 -- SUPERSEDED. The galley pair's two halves
      are both gone; the module was rewritten. What it said, and what replaced
      it, are in the Objective.
- [ ] T4 | T4 -- `lexer.Paragraph`: one comment block gives two spellings for an
      empty interval, and the census emits neither. Verify: the dogfood run
      reports the pair.
- [x] T5 | FINISHED | unknown | T5 -- FINISHED. `page.py`'s *"a DIFFERENT set"*
      claim is gone with both constants; the two questions are now
      `holds_no_prose` and `occupies_no_lines`.
- [ ] T6 | T6 -- `record.entry_for` asserts that `--check` HOLDS one paragraph
      per address and also that it merely reports. Verify: the dogfood run
      reports the pair.
- [ ] T7 | T7 -- `record.py:37-42` tells a reviewer filing an `add` to write
      *"that interval's index and address"*. Verify: the dogfood run reports it.
- [ ] T8 | T8 -- `desk.py:557` asks whether the address names the paragraph the
      census has at that INDEX, over a body resolving by address. Verify: the
      run reports it.
- [ ] T9 | T9 -- `desk.py:246` calls `_resolve_lines` *"Shared by SOURCES and
      LOCATION"* after `LOCATION` was dropped, which `:567` says. Verify: the
      dogfood run reports the pair.
- [ ] T10 | T10 -- `verdicts.py:120` says *"Indices each reviewer left
      unaccounted for"* over a body that keys `f.address`. Verify: the dogfood
      run reports it.
- [ ] T11 | T11 -- `verdicts.py:194` documents an argument as *"findings by
      census paragraph index"* when `by_paragraph` is keyed by address. Verify:
      the run reports it.
- [ ] T12 | T12 -- `verdicts.py:634` names its loop variable `index` while
      iterating addresses. Verify: the dogfood run reports it.
