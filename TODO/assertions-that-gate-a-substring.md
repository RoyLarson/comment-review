# Ten assertions gate a substring or an incidental field, not the property

```
Status:   open
Progress: 0 of 10 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-20 (the branch review of 2026-08-20)
```

## Objective

Ten assertions gate a substring or an incidental field, not the property.

## Tasks

- [ ] `test_page.py` `test_on_both_ranges_every_line_has_exactly_one_owner` PASSES
      on the fixture that destroys front matter, because `owners()` applies a
      precedence rule NO SHIPPED CODE IMPLEMENTS: it puts `a`/`c` lines in `exact`
      first. `galley.splice_range` returns the raw range and `splice` replaces
      every line in it. The invariant lives in the test's interpretation, not in
      the data the galley consumes.
- [ ] `test_raw_lines_still_matches_the_range_it_covers` skips the corrupted
      paragraph outright: `if b.original_column or not held: continue` -- `held`
      is empty exactly when `original_start is None`, which is the broken case.
- [ ] `test_census_blocks.py:531` asserts `_marked(LICENCE) == [1]`, and `_marked`
      returns `b.start` ONLY. On that fixture `start` is still 1 while `end=0`,
      `orig=(None,None)`, `raw_lines=[]`, and the neighbouring interval holds the
      licence text.
- [ ] `test_verdicts.py:124-151`
      `test_an_unterminated_record_is_flagged_not_silently_merged` PASSES ON THE
      MERGE IT FORBIDS: run on its own fixture the merge happens, and the
      assertion whose message reads *"a malformed record must not enter the
      findings at all"* is True in the buggy state and vacuously True in the fixed
      one.
- [ ] `test_run_context.py:99` asserts `str(len(REQUIRED))` appears in a docstring
      -- rewriting it to *"names three sections below, measured over 10 runs"*
      passes. Its comment says it exists to stop *"quietly re-creating the same
      false claim"*.
- [ ] `test_foliation.py:619` asserts `body.count("read_text") == 1` with the
      message *"only the census is read"* -- adding a function that reads an
      arbitrary path with `open()` passes.
- [ ] `test_todo_counts_agree.py:64-66` requires only `^Progress: `, so `Progress:
      0 of 99 proposals done` against 16 boxes passes both checks. `:58` names
      *"one of the two units"*; all 56 `Progress:` lines use `tasks`.
- [ ] `test_declarations.py:197-203` passes `""`, so every language returns the
      module row and the keyword scan runs over ZERO lines -- making
      `_declares_here` `return False` unconditionally leaves the class green. MY
      test, added 2026-08-20.
- [ ] `TestTheTwoKindSetsAreNotInterchangeable` never tests non-
      interchangeability; it would pass if the two names were aliased.
      `test_foliation.py:152-156` has two method names asserting the opposite of
      what they say. `TestAStaleCensusIsRefused` says `--check` exits 2 --
      falsified by a passing sibling in the same file.
- [ ] `test_verdicts.py:774-778` says `TestClaimAgainstTheCensus` *"is what
      replaces"* the two retired LOCATION tests and *"is a stronger check"*. `grep
      -rn TestClaimAgainstTheCensus` finds that comment and a plan. The class was
      never written; the removed check has no replacement.
