# Nine findings in the record, verdict and desk system, from review round 4

```
Status:   in-progress
Progress: 2 of 12 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-22 (/code-review high round 4, 2026-08-22 -- the findings OUTSIDE the
          seven reader modules, filed rather than fixed because this system is due an
          independent review session and the reader modules shift under it)
RE-VERIFIED: 2026-08-23 -- Task 6 is FIXED and ticked: record.py:1074 now
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
SPLIT:    2026-08-23 -- one failure per box, with the evidence moved to the Objective. The
          zero-path box held a `census.py` failure and a `verdicts.py` failure and is now
          two, so 9 findings sit in 10 boxes. A second pass split the `patch` box into the
          gate and the generated instruction, and the at-sign box into its two rejected
          cases -- 10 boxes became 12. Nothing was re-measured.
```

## Objective

Nine findings in the record, verdict and desk system, from review round 4 -- the findings OUTSIDE
the seven reader modules, filed rather than fixed because the reader modules shift under them.

! **Every box here is a task**: each names a specific file and a specific failure, and each
finishes when the failure stops reproducing.

### The evidence, per finding

**The `patch` payload and `owes_sources` disagree, in the shipped tree.** `record.py`'s `patch`
row says a patch needs no source and that sentence is generated VERBATIM into the shipped
reviewer-brief, but `owes_sources` stays True -- only `clean` clears it -- so `desk.py` fatally
refuses every `patch` a compliant reviewer files. ! RE-CONFIRMED BY RUNNING IT, 2026-08-23.

**A non-reviewer role name passes the UNKNOWN-reviewer check.** `published` is built from
`vocabulary.Reviewer` (`verdicts.py:403`), which also holds `compact` and `review`
(`vocabulary.py:46-47`), so a file named `review.json` is accepted. A run where `module-context`
never ran certifies *Every finding is admissible* at exit 0 and never names the absence.
! RE-CONFIRMED 2026-08-23 by reading both files.

**Zero path arguments certify completeness.** `census.py` emits `[]` at exit 0, and the join's
emptiness guard is satisfied by an empty list, so `verdicts.py` certifies *0 findings over 0 prose
paragraphs* as COMPLETE. Reachable whenever stage 1's merge-base diff yields no paths -- the exact
complete-because-nothing-was-incomplete failure that guard exists to stop, one step out.
! NOT RE-RUN 2026-08-23.

**A blank line inside `desk.py`'s SOURCE window collapses to an empty string** and emits two
spaces where the needle has one, so any honest verbatim quote SPANNING a blank line is fatally
refused. `_resolve_lines` invites function-sized ranges, where blank lines are guaranteed.
! NOT RE-RUN 2026-08-23.

**Any at-sign in a `move`'s `to:` is treated as an address claim** in `desk.py`, but the address
pattern matches only a series letter and digits -- so both a prose destination naming a decorated
accessor and a real front-matter address are rejected as `not an address`. ! NOT RE-RUN
2026-08-23.

**`verdict not in VERDICTS` is asked of unvalidated JSON** in `record.py`, so a verdict written as
a LIST raises `TypeError` and takes the pre-flight down. ! RE-CONFIRMED BY RUNNING IT, 2026-08-23:
`record_problems({"verdict": ["patch"]}, None)` gives `TypeError: unhashable type: list`.

**`compositor.draft` writes `set_page(page)` with no losslessness check.** ! The obvious fix does
NOT work and the reason matters: `lossless()` rebuilds the page FROM DISK, so it cannot be asked
of a drafted page -- the whole point of a draft is that lines changed. The guard that would work
is an identity check on the page BEFORE any verdict is applied, so a later difference is
attributable to the edit rather than to the model. ! NOT RE-RUN 2026-08-23.

### The two that are fixed

- **`record.py:1074`** now guards with `isinstance(report.get("pages"), list)` and returns *not a
  seeded report*, where passing a census in place of a report died with `AttributeError` instead
  of the shape diagnostic `held.py` documents guarding for. FIXED, re-confirmed 2026-08-23.
- **`run_context.py`** named three machine-checked sections and subtracted three while FOUR were
  checked; the lookup census was omitted from what the message claimed to have verified.
  `PATH_SECTIONS` now holds four names (`:62`) and the message derives BOTH numbers from it
  (`:344-347`); the comment at `:340-343` records the defect as past. FIXED, found 2026-08-23.

## Tasks

- [ ] T1 -- `desk.py` -- stop `owes_sources` fatally refusing a `patch` filed with no
      source. Verify: such a `patch` is admitted.
- [ ] T2 -- `record.py` -- make the generated `patch` row say what `desk.py`'s gate
      enforces. Verify: the shipped brief's sentence and `owes_sources` agree.
- [ ] T3 -- `verdicts.py` -- stop `vocabulary.Reviewer` admitting non-reviewer role names.
      Verify: a report named `review.json` is refused as an unknown reviewer.
- [ ] T4 -- `census.py` -- refuse a run given zero path arguments instead of emitting
      `[]`. Verify: a zero-path census run exits nonzero.
- [ ] T5 -- `verdicts.py` -- refuse an empty census instead of certifying it COMPLETE.
      Verify: the join over an empty census exits nonzero and says what was missing.
- [ ] T6 -- `desk.py` -- keep a blank line inside the SOURCE window from collapsing to two
      spaces. Verify: an honest verbatim quote spanning a blank line is admitted.
- [ ] T7 -- `desk.py` -- stop reading a prose `to:` that names a decorated accessor as an
      address claim. Verify: such a `move` is admitted.
- [ ] T8 -- `desk.py` -- accept a real front-matter address in a `move`'s `to:`. Verify:
      it passes the address check instead of being rejected.
- [ ] T9 -- `record.py` -- validate the verdict's shape before the `not in VERDICTS` test.
      Verify: `record_problems({"verdict": ["patch"]}, None)` returns a problem.
- [ ] T10 -- `compositor.draft` -- identity-check the page BEFORE any verdict is applied.
      Verify: `draft` refuses a page that does not set back identically.
- [x] T11 -- FIXED 2026-08-23, re-confirmed. `record.py:1074` guards `report.get('pages')`
      with `isinstance(..., list)`. In the Objective.
- [x] T12 -- FIXED, found 2026-08-23. `run_context.py` derives both numbers from
      `PATH_SECTIONS`, which holds four. In the Objective.
