# Six mutations to shipped code survive the whole suite

```
Status:   open
Progress: 1 of 6 tasks done
Owner:    testing
Requires-Roy: false
Raised:   2026-08-20 (the branch review of 2026-08-20)
Closed:   2026-08-20 -- 2026-08-20 -- ONE OF THE SIX IS CLOSED. The front-matter ->
          `query` conversion is now gated by two end-to-end tests that run the join and
          read its output: one on a FILLED front-matter run and one on the EMPTY place.
          VERIFIED as a gate by disabling the guard -- both fail, and the suite is green
          with it restored. ! The old class asserted a `VERDICTS` flag and
          `census.FRONT_MATTER == "front-matter"`; the import it needed is now gone,
          which is how the vacuity surfaced.
Re-checked: 2026-08-23 -- the suite is 820 passed, 1 skipped, 734 subtests
          (`uv run pytest -q`), not the 720 each box records. Two of the five open
          boxes name a guard that has since been REWRITTEN, so each mutation is to be
          re-applied before it is called live. Line numbers re-taken below.
```

## Objective

**Five mutations to shipped code are believed to survive the whole suite, and each names the
test that was supposed to stop it.** A test that cannot fail is a green bar over nothing, which
is what `docs/gates.md` says the question is: not *does the check pass*.

! **THE COUNT IN EVERY BOX IS STALE AND THE SHAPE IS NOT.** The runs were taken against 720
tests; `uv run pytest -q` now reports 820 passed, 1 skipped, 734 subtests. Re-measure with the
current suite when each is re-applied.

! **TWO OF THE NAMED GUARDS HAVE MOVED SINCE.** `test_a_cue_is_never_DERIVED_from_another`
(`tests/test_cues.py:1127`) was rewritten on 2026-08-21 and no longer asserts the absence of two
source strings -- it builds a page and reads `cues.places`, which is the property rather than the
punctuation. And `test_no_check_branches_on_a_VERDICT_NAME` (`tests/test_verdicts.py:1273-1291`)
now scans EVERY shipped script with `f\.verdict\s*(==|!=|in)\s*[("']`, which still matches only a
direct comparison. **So the mutation has to be run again to say whether it is live** -- reading
the test is not enough, and this file is the reason: it read one and got it wrong.

! **A closed one stays here checked, with what closed it.** The front-matter to `query`
conversion is gated by two end-to-end tests that run the join and read its output, verified by
disabling the guard.

## Tasks

- [x] T1 -- FINISHED. Deleting `verdicts.py:445-469` entirely -- the 25 lines that
      convert a reviewer's edit on front matter to a `query`, the one path stopping
      an edit landing on a licence header -- left 720 tests OK. Now gated by two
      end-to-end tests that run the join and read its output, one on a FILLED
      front-matter run and one on the EMPTY place; verified by disabling the guard.
- [ ] T2 -- Gate the `c` cue against being DERIVED from the `b` cue.
      `addresser.py:786` reads `beside = c.emit(line, at)`; the prohibition is what
      `tests/test_cues.py:1127` is named for, and that test was rewritten
      2026-08-21 to assert the cue-to-anchor relation instead of two absent source
      strings. Verify: replace `beside` with the `c` cue computed from the `b` cue,
      `uv run pytest -q` FAILS and names the test; restore it and the suite is
      green.
- [ ] T3 -- Gate the retired-word detector against being unable to fire. Forcing
      `hits = 0` at `check_vocabulary.py:355` leaves it dead.
      `tests/test_vocabulary.py:199-205` asserts only that `cv.RETIRED` is truthy,
      and `TestNoRetiredWordSurvivesAnywhere` (`:241-294`) RE-IMPLEMENTS the regex
      in its own `_hits` rather than calling the shipped scanner, so neither one
      runs the code the mutation kills. Verify: a test drives `cv.check_retired()`
      over text holding a retired word and asserts a nonzero count; with `hits = 0`
      forced, `uv run pytest -q` fails.
- [ ] T4 -- Gate `record.slot()` to the address and nothing else. Adding
      `"text": paragraph.get("text","")` contradicts its own docstring -- *"THE
      ADDRESS AND NOTHING ELSE"* -- and the asymmetry the design rests on.
      `tests/test_record.py:103` forbids one key NAME, `original`; `:110` asserts
      `record.SEEDED == ("place", "anchor")`, which is the CONSTANT and not the
      function's output; `:105` checks presence only. Verify: a test asserts the
      exact key set returned by `record.slot(...)`, and fails when a sixth key is
      added.
- [ ] T5 -- Gate the JSON-mode refusal. `census.py:417` and `:437` print the
      refusal to STDERR while the text-mode path prints to stdout, so an assertion
      reading `self._run("--json").stdout` is vacuous and replacing the print with
      `pass` costs nothing. Verify: a test runs `census.py --json` on the input
      that refuses, asserts the refusal text on STDERR and the exit code, and fails
      when the print is removed.
- [ ] T6 -- Close the one-line escape from the verdict-name ban. Adding
      `v = f.verdict` then `if v == "drop"` to `desk.payload_problem` passes
      `tests/test_verdicts.py:1273`, whose regex matches only a direct
      `f.verdict ==`; `record.py:945` and `:1036` already bind
      `verdict = rec.get("verdict")`, so the shape exists in shipped code. Verify:
      the check catches a verdict name compared through a local binding -- add the
      two lines and `uv run pytest -q` fails.
