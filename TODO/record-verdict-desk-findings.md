# Nine findings in the record, verdict and desk system, from review round 4

```
Status:   in-progress
Progress: 9 of 14 tasks closed
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
Fixed:    2026-08-24 — T1, T2 and T9 landed, all three verified by RUNNING them. T1/T2
          resolved toward the BRIEF rather than the gate: the patch row now sets
          owes_sources False, so the shipped sentence and desk.py agree and a sourceless
          patch is ADMITTED while a sourceless correct is still refused. ! T9 was TWO
          sites, not one -- the membership test in record_problems AND a dict lookup in
          claim_problems at :957, which .get hashes the same way; record_problems now
          reports the shape and returns before both. ! NEITHER FIX MOVED THE SUITE: 820
          tests passed before and after, so nothing covered either one. T13 and T14 are
          those tests. SUPERSEDED SAME DAY: that sentence filed them to testing.
Tested:   2026-08-24 — T13 and T14 landed, and both were PROVEN ABLE TO FAIL: each
          defect was put back, the test refused it, and the file was restored and
          compared byte for byte. ! RE-OWNED THE SAME DAY -- Roy ruled a test belongs
          to the lane that owns what it TESTS, so a record.py regression test is
          backend and never was testing's. See decision-log.md Process: 5. ! The
          brief-row check is the GENERAL form rather than a patch special case: no
          payload may waive a source its own row still owes, plus a second case naming
          the row that must match, because a reword would otherwise leave the loop
          running zero times and reporting success.
Fixed2:   2026-08-24 — T4 and T5. census.py refuses a run with no paths
          (exit 2, --languages still exempt); verdicts.py refuses a census holding no
          paragraphs (exit 1) instead of printing "Every finding is admissible. Stage 5
          may rule." ! Both were RE-RUN before and after, and three tests joined the
          class that already covers the unaddressed case at both ends -- the same pair
          of ends, one input short. ! PROVEN ABLE TO FAIL: each guard was disabled in
          turn and the class went red both times, then the files were restored and
          compared byte for byte. 831 tests, up 3.
```

## Objective

Nine findings in the record, verdict and desk system, from review round 4 -- the findings OUTSIDE
the seven reader modules, filed rather than fixed because the reader modules shift under them.

! **Every box here is a task**: each names a specific file and a specific failure, and each
finishes when the failure stops reproducing.

### The evidence, per finding

**The `patch` payload and `owes_sources` disagreed, in the shipped tree.** `record.py`'s `patch`
row says a patch needs no source and that sentence is generated VERBATIM into the shipped
reviewer-brief, but `owes_sources` stayed True -- only `clean` cleared it -- so `desk.py` fatally
refused every `patch` a compliant reviewer filed. ! RE-CONFIRMED BY RUNNING IT, 2026-08-23.
**FIXED 2026-08-24, toward the BRIEF**: the row sets `owes_sources=False`, because a `patch` rules
on wording the paragraph itself settles, so a source would be evidence for a claim nobody made.
Measured after: a sourceless `patch` is ADMITTED, a sourceless `correct` is still REFUSED.

**A non-reviewer role name passes the UNKNOWN-reviewer check.** `published` is built from
`vocabulary.Reviewer` (`verdicts.py:403`), which also holds `compact` and `review`
(`vocabulary.py:46-47`), so a file named `review.json` is accepted. A run where `module-context`
never ran certifies *Every finding is admissible* at exit 0 and never names the absence.
! RE-CONFIRMED 2026-08-23 by reading both files.

**Zero path arguments certified completeness.** `census.py` emitted `[]` at exit 0, and the collator's
emptiness guard was satisfied by an empty list, so `verdicts.py` certified *0 findings over 0 prose
paragraphs* as COMPLETE. Reachable whenever stage 1's merge-base diff yields no paths -- the exact
complete-because-nothing-was-incomplete failure that guard exists to stop, one step out.
! NOT RE-RUN 2026-08-23. **RE-RUN AND FIXED 2026-08-24**, both halves.

! **THE COLLATOR'S HALF IS THE SAME DEFECT ONE INPUT SHORT, and it sat beside its own reasoning.**
`verdicts.py` already refuses a census carrying no ADDRESSES, with a comment saying *"the run then
reads as complete because there was nothing to be incomplete about."* An EMPTY census passes that
check **vacuously** -- `unaddressed([])` is empty because there is nothing that could be
unaddressed -- so the guard was answering a question the input had removed. ! A guard that reads a
collection has to say what an empty one means, or it reports *passed every question it could not
ask* as success.

! **AND `--languages` IS WHY THE CENSUS TAKES `nargs="*"`.** It is the one caller that
legitimately passes no paths, so the refusal is conditioned on it rather than on the argparse
shape -- and a test pins that it still runs, because a refusal that also refused it would be
written to the defect's shape instead of to the defect.

**A blank line inside `desk.py`'s SOURCE window collapses to an empty string** and emits two
spaces where the needle has one, so any honest verbatim quote SPANNING a blank line is fatally
refused. `_resolve_lines` invites function-sized ranges, where blank lines are guaranteed.
! NOT RE-RUN 2026-08-23.

**Any at-sign in a `move`'s `to:` is treated as an address claim** in `desk.py`, but the address
pattern matches only a series letter and digits -- so both a prose destination naming a decorated
accessor and a real front-matter address are rejected as `not an address`. ! NOT RE-RUN
2026-08-23.

**`verdict not in VERDICTS` was asked of unvalidated JSON** in `record.py`, so a verdict written as
a LIST raised `TypeError` and took the pre-flight down. ! RE-CONFIRMED BY RUNNING IT, 2026-08-23:
`record_problems({"verdict": ["patch"]}, None)` gives `TypeError: unhashable type: list`.
**FIXED 2026-08-24, and it was TWO sites rather than one** -- guarding the membership test alone
still raised, from `ALLOWED["claim"].get(verdict)` in `claim_problems`, because `.get` hashes its
argument exactly as `in` does. `record_problems` now reports the shape and returns before both
verdict-keyed helpers. ! A NUMBER never raised: it hashes, so only the two JSON container types
reached it.

**`compositor.draft` writes `set_page(page)` with no losslessness check.** ! The obvious fix does
NOT work and the reason matters: `lossless()` rebuilds the page FROM DISK, so it cannot be asked
of a drafted page -- the whole point of a draft is that lines changed. The guard that would work
is an identity check on the page BEFORE any verdict is applied, so a later difference is
attributable to the edit rather than to the model. ! NOT RE-RUN 2026-08-23.

### The two that arrived already fixed

- **`record.py:1074`** now guards with `isinstance(report.get("pages"), list)` and returns *not a
  seeded report*, where passing a census in place of a report died with `AttributeError` instead
  of the shape diagnostic `held.py` documents guarding for. FIXED, re-confirmed 2026-08-23.
- **`run_context.py`** named three machine-checked sections and subtracted three while FOUR were
  checked; the lookup census was omitted from what the message claimed to have verified.
  `PATH_SECTIONS` now holds four names (`:62`) and the message derives BOTH numbers from it
  (`:344-347`); the comment at `:340-343` records the defect as past. FIXED, found 2026-08-23.

## Tasks

- [x] T1 | FINISHED | unknown | T1 -- `desk.py` -- stop `owes_sources` fatally
      refusing a `patch` filed with no source. Verify: such a `patch` is
      admitted.
- [x] T2 | FINISHED | unknown | T2 -- `record.py` -- make the generated `patch`
      row say what `desk.py`'s gate enforces. Verify: the shipped brief's
      sentence and `owes_sources` agree.
- [ ] T3 | T3 -- `verdicts.py` -- stop `vocabulary.Reviewer` admitting
      non-reviewer role names. Verify: a report named `review.json` is refused
      as an unknown reviewer.
- [x] T4 | FINISHED | unknown | T4 -- `census.py` -- refuse a run given zero
      path arguments instead of emitting `[]`. Verify: a zero-path census run
      exits nonzero.
- [x] T5 | FINISHED | unknown | T5 -- `verdicts.py` -- refuse an empty census
      instead of certifying it COMPLETE. Verify: the collator over an empty
      census exits nonzero and says what was missing.
- [ ] T6 | T6 -- `desk.py` -- keep a blank line inside the SOURCE window from
      collapsing to two spaces. Verify: an honest verbatim quote spanning a
      blank line is admitted.
- [ ] T7 | T7 -- `desk.py` -- stop reading a prose `to:` that names a decorated
      accessor as an address claim. Verify: such a `move` is admitted.
- [ ] T8 | T8 -- `desk.py` -- accept a real front-matter address in a `move`'s
      `to:`. Verify: it passes the address check instead of being rejected.
- [x] T9 | FINISHED | unknown | T9 -- `record.py` -- validate the verdict's
      shape before the `not in VERDICTS` test. Verify:
      `record_problems({"verdict": ["patch"]}, None)` returns a problem.
- [ ] T10 | T10 -- `compositor.draft` -- identity-check the page BEFORE any
      verdict is applied. Verify: `draft` refuses a page that does not set back
      identically.
- [x] T11 | FINISHED | unknown | T11 -- FIXED 2026-08-23, re-confirmed.
      `record.py:1074` guards `report.get('pages')` with `isinstance(...,
      list)`. In the Objective.
- [x] T12 | FINISHED | unknown | T12 -- FIXED, found 2026-08-23.
      `run_context.py` derives both numbers from `PATH_SECTIONS`, which holds
      four. In the Objective.
- [x] T13 | FINISHED | unknown | T13 -- A sourceless `patch` is admitted, and
      the brief's sentence is pinned to its row. Verify: it fails if
      `owes_sources` goes back to True on `patch`.
- [x] T14 | FINISHED | unknown | T14 -- A list, dict or number verdict returns a
      shape diagnostic. Verify: it fails if `record_problems`'s isinstance guard
      is removed.
