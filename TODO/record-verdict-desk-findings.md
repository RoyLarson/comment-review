# Nine findings in the record, verdict and desk system, from review round 4

```
Status:   in-progress
Progress: 2 of 9 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-22 (/code-review high round 4, 2026-08-22 -- the findings OUTSIDE the
          seven reader modules, filed rather than fixed because this system is due an
          independent review session and the reader modules shift under it)
RE-VERIFIED: 2026-08-23 — 2026-08-23. Task 6 is FIXED and ticked: record.py:1074 now
             guards with isinstance(report.get("pages"), list) and returns "not a seeded
             report" instead of dying with AttributeError. ! TWO RE-CONFIRMED BY RUNNING
             THEM, not by reading: task 7 still raises -- record_problems({"verdict":
             ["patch"]}, None) gives TypeError: unhashable type: list, because the
             membership test is asked of unvalidated JSON; and task 1 still contradicts
             itself -- the patch row payload generates "A patch needs no source"
             verbatim into the shipped brief while owes_sources stays True by default,
             so desk.py fatally refuses every compliant patch. The shipped instruction
             and the shipped gate still disagree. Tasks 2, 3, 4, 5, 8 and 9 were not re-
             run.
TRIAGED:  2026-08-23 -- second pass, and ONE MORE OF THE SIX UNRE-RUN BOXES TURNED OVER.
          T6 re-confirmed FIXED at record.py:1074. **T8 IS ALSO FIXED and is now ticked**:
          `PATH_SECTIONS` holds FOUR names (run_context.py:62 -- `REPO ROOT`, `CENSUS`,
          `LOOKUP CENSUS`, `REVIEWER FILES`) and the success message derives BOTH numbers
          from it (run_context.py:344-347), with the comment at :340-343 recording the
          three-for-four defect as past. T2 re-confirmed STILL LIVE: `published = {r.value
          for r in Reviewer}` (verdicts.py:403) and `Reviewer` still holds `COMPACT` and
          `REVIEW` (vocabulary.py:46-47). ! T3, T4, T5 and T9 were NOT re-run and are left
          open on their original measurement -- say so rather than imply a check that did
          not happen.
```

## Objective

Nine findings in the record, verdict and desk system, from review round 4 -- the findings OUTSIDE
the seven reader modules, filed rather than fixed because the reader modules shift under them.

! **Every box here is a task**: each names a specific file and a specific failure, and each
finishes when the failure stops reproducing.

## Tasks

- [ ] T1 -- `record.py` -- the `patch` row's payload says a patch needs no source and that
      sentence is generated VERBATIM into the shipped reviewer-brief, but `owes_sources` stays
      True (only `clean` clears it), so `desk.py` fatally refuses every `patch` a compliant
      reviewer files. The shipped instruction and the shipped gate contradict each other.
      ! RE-CONFIRMED BY RUNNING IT, 2026-08-23. Verify: a `patch` record filed with no source is
      admitted, and the brief and the gate say the same thing.

- [ ] T2 -- `verdicts.py` -- `published` is built from `vocabulary.Reviewer`
      (verdicts.py:403), which also holds `compact` and `review` (vocabulary.py:46-47), so a
      file named `review.json` passes the UNKNOWN-reviewer check. A run where `module-context`
      never ran certifies `Every finding is admissible` at exit 0 and never names the absence.
      ! RE-CONFIRMED 2026-08-23 by reading both files. Verify: a report named `review.json` is
      refused as an unknown reviewer.

- [ ] T3 -- `census.py` + `verdicts.py` -- zero path arguments emit `[]` at exit 0, and the
      join's emptiness guard is satisfied by an empty list, so it certifies `0 findings over 0
      prose paragraphs` as COMPLETE. Reachable whenever stage 1's merge-base diff yields no
      paths -- the exact complete-because-nothing-was-incomplete failure that guard exists to
      stop, one step out. ! NOT RE-RUN 2026-08-23. Verify: a zero-path run exits nonzero.

- [ ] T4 -- `desk.py` -- a blank line inside the SOURCE window collapses to an empty string and
      emits two spaces where the needle has one, so any honest verbatim quote SPANNING a blank
      line is fatally refused. `_resolve_lines` invites function-sized ranges, where blank lines
      are guaranteed. ! NOT RE-RUN 2026-08-23. Verify: a verbatim quote spanning a blank line is
      admitted.

- [ ] T5 -- `desk.py` -- any at-sign in a `move`'s `to:` is treated as an address claim, but the
      address pattern matches only a series letter and digits, so both a prose destination naming
      a decorated accessor and a real front-matter address are rejected as `not an address`.
      ! NOT RE-RUN 2026-08-23. Verify: both shapes are accepted.

- [x] T6 -- FIXED 2026-08-23, re-confirmed. `record.py` -- `report.get('pages')` had no type
      guard, so passing a census where a report was expected died with `AttributeError` instead
      of the shape diagnostic `held.py` documents guarding for. record.py:1074 now guards with
      `isinstance(report.get("pages"), list)` and returns *not a seeded report*.

- [ ] T7 -- `record.py` -- `verdict not in VERDICTS` is asked of unvalidated JSON, so a verdict
      written as a LIST raises `TypeError` and takes the pre-flight down. ! RE-CONFIRMED BY
      RUNNING IT, 2026-08-23: `record_problems({"verdict": ["patch"]}, None)` gives
      `TypeError: unhashable type: list`. Verify: the same call returns a problem instead of
      raising.

- [x] T8 -- FIXED, found 2026-08-23. `run_context.py` -- the success message named three
      machine-checked sections and subtracted three while FOUR were checked; the lookup census
      was omitted from what the message claimed to have verified. `PATH_SECTIONS` now holds four
      names (run_context.py:62) and the message derives BOTH numbers from it
      (run_context.py:344-347); the comment at :340-343 records the defect as past.

- [ ] T9 -- `compositor.draft` writes `set_page(page)` with no losslessness check. ! The obvious
      fix does NOT work and the reason matters: `lossless()` rebuilds the page FROM DISK, so it
      cannot be asked of a drafted page -- the whole point of a draft is that lines changed. The
      guard that would work is an identity check on the page BEFORE any verdict is applied, so a
      later difference is attributable to the edit rather than to the model. ! NOT RE-RUN
      2026-08-23. Verify: `draft` refuses a page that does not set back identically before any
      verdict is applied.
