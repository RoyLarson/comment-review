# Ten assertions gate a substring or an incidental field, not the property

```
Status:   open
Progress: 3 of 10 tasks done
Owner:    testing
Requires-Roy: false
Raised:   2026-08-20 (the branch review of 2026-08-20)
TRIAGED:  2026-08-23 -- every box was a real task; all ten were RE-VERIFIED against the
          tree today and THREE are gone -- the code they were about was deleted or
          rewritten in between, so they are ticked SUPERSEDED with the measurement that
          retires them. Six stand and are rewritten with the mutation that must make
          each one fail. One (T3) is half retired and rewritten to the half that is
          left.
```

## Objective

Ten assertions gate a substring or an incidental field, not the property. **The test for each is
the same: name the mutation that must turn the test red, apply it, and check that it does.** A
test that stays green under the mutation its own comment forbids is not covering the property it
claims.

## ! What the re-verification of 2026-08-23 retired, and why

- **The splicing galley is gone.** `galley.py` holds no `splice`, `overlaps` or `splice_range`
  -- `tests/test_galley.py:14` and `docs/history.md:62` record their removal, and the module's
  own docstring says *"NO LINE NUMBER APPEARS IN THIS FILE"*. Two boxes were about assertions
  standing in for what that galley did.
- **Front matter is no longer destroyed.** MEASURED 2026-08-23 on the exact fixture the file
  named, `'# Copyright 2024\n# Apache 2.0\n\n"""What this is."""\n\nimport os\n'`: the `matter`
  paragraph comes back `start=1 end=2`, `original=(1,2)`, `raw_lines=['# Copyright 2024',
  '# Apache 2.0']`. The shape three of the boxes described -- `end=0`, `orig=(None,None)`,
  `raw_lines=[]` -- is not produced.
- **The retired report format was deleted, not shimmed** (`2a86573`), and the text-report parser
  one box tested went with it.

## What each retired box measured

**T1.** `test_page.py:294 test_on_both_ranges_every_line_has_exactly_one_owner` was said to pass
only because its `owners()` helper applies a precedence rule no shipped code implements. MEASURED
2026-08-23: the precedence branch is INERT -- counting every paragraph's range with no `exact` set
at all, all 7 shapes on both ranges still give every line exactly one owner, 0 failures. And the
galley it stood in for is deleted; the compositor sets each place from its own `raw_lines`, so no
two places claim a line to begin with.

**T2.** `test_raw_lines_still_matches_the_range_it_covers` does not exist; `test_page.py:337` is
`test_raw_lines_are_the_lines_this_paragraph_OWNS`, rewritten 2026-08-21 because `raw_lines` is
deliberately NOT the whole range. Its `if b.original_column or not held: continue` now skips
EMPTY PLACES, which are a supported state, not the corrupted paragraph the box was about -- and
that paragraph is no longer produced, per the measurement above.

**T4.** `test_an_unterminated_record_is_flagged_not_silently_merged` is not in `tests/`;
`git log -S` finds it removed in `2a86573`, *"the retired report format is DELETED, not shimmed"*,
along with the text-report parser it exercised. Reports are JSON now and the malformed cases are
covered by `held.load_report` at `test_verdicts.py:2356-2451`, which assert on the returned
`malformed` list rather than on a merge.

## The evidence behind each standing box

**T3.** `tests/test_census_blocks.py:937` asserts `self._marked(self.LICENCE) == [1]` and
`_marked` returns `b.start` ALONE (`:929`). ! Half of this box is retired: the front matter is
intact today, measured above. What is left is that the assertion reads one field of a two-line
run, so a paragraph that keeps its start and loses its body passes.

**T5.** `tests/test_run_context.py:99` asserts `str(len(run_context.REQUIRED))` appears in the
module docstring. Its own comment (`:92-98`) says it exists to stop *"quietly re-creating the same
false claim"*, and rewriting the docstring to *"names three sections below, measured over 10
runs"* passes -- the digit is present and says nothing about the count.

**T6.** `tests/test_cues.py:666` asserts `body.count("read_text") == 1` with the message *"only
the census is read"*. Adding a function to `addresser.py` that reads an arbitrary path with
`open()` passes, because the assertion gates the spelling of one call rather than the READS.

**T7.** `tests/test_todo_counts_agree.py:64-66` requires only `^Progress: `, so `Progress: 0 of 99
proposals done` on a file with 16 boxes satisfies BOTH checks: the unit is not matched, so
`PROGRESS` (`:27`, which does require `tasks`) finds nothing and
`test_every_progress_line_matches_its_boxes` skips at `:46`. MEASURED 2026-08-23: all 101
`Progress:` lines in `TODO/` use `tasks`, so no file exercises the hole.

**T8.** `tests/test_declarations.py:313-319`
`test_a_language_with_declares_reaches_the_a_series_and_one_without_does_not` passes `""` to
`lexer.declarations`, so every language returns the module row and the keyword scan runs over ZERO
lines. ! MY test, added 2026-08-20.

**T9.** `TestAStaleCensusIsRefused` (`tests/test_cues.py:300`) is named for a refusal it never
asserts. Its docstring says *"`--check` exits 2 instead"*, and its own third test,
`test_the_addresses_differ_silently_and_neither_errors` (`:337-345`), asserts the opposite -- both
censuses answer, neither errors, `b1` becomes `b0`. ! The other two halves of this box are done:
`TestTheTwoKindSetsAreNotInterchangeable` was rewritten as `TestEverySeriesHasAPositiveAndANegative`
(`test_page.py:466-496`), which derives the absences instead of listing them; and
`test_cues.py:153-157` now reads `test_the_gap_before_it_is_b0_not_b1` /
`test_the_gap_after_it_is_b1`, which assert what they say.

**T10.** `tests/test_verdicts.py:664-668` says the two retired LOCATION tests are replaced by
`TestClaimAgainstTheCensus` and that it *"is a stronger check than the one removed"*.
`grep -rn TestClaimAgainstTheCensus` finds that comment and one plan
(`docs/superpowers/plans/2026-08-17-group-a-unit-of-review.md:862`). The class was never written;
the removed check has no replacement.

## Tasks

- [x] T1 -- SUPERSEDED 2026-08-23. The precedence branch is inert, 0 failures without it,
      and the galley it stood in for is deleted.
- [x] T2 -- SUPERSEDED 2026-08-23. The named test does not exist and the corrupted
      paragraph it was about is no longer produced.
- [ ] T3 -- Assert the EXTENT at `test_census_blocks.py:937` -- `(start, end)` and
      `raw_lines`, not `b.start`. Verify: ending `matter` at its first line goes red.
- [x] T4 -- SUPERSEDED 2026-08-23. The test and the text-report parser it exercised were
      removed in `2a86573`; the malformed cases are covered by `held.load_report`.
- [ ] T5 -- Gate the COUNT, not the digit, at `test_run_context.py:99`. Verify: the
      docstring mutation recorded in the Objective turns the test red.
- [ ] T6 -- Gate the READS, not the spelling of one call, at `test_cues.py:666`. Verify: a
      second `open()` read of an arbitrary path in `addresser.py` turns the test red.
- [ ] T7 -- Match the UNIT in `test_todo_counts_agree.py:64-66`, so a non-`tasks` unit
      cannot skip both checks. Verify: change a `Progress:` unit and a test goes red.
- [ ] T8 -- Run the keyword scan over real lines in `test_declarations.py:313-319`, not
      `""`. Verify: `_declares_here` returning False always turns the class red.
- [ ] T9 -- Make `TestAStaleCensusIsRefused` assert the exit code its docstring claims, or
      stop the docstring claiming it. Verify: `--check` exits 2, or `2` is not named.
- [ ] T10 -- Write `TestClaimAgainstTheCensus`, or stop `test_verdicts.py:664-668` naming
      it. Verify: the class fails on a misattached finding, or the name is gone.
