# A coverage gap should go back to the reviewer, not be reported as a result

```
Status:   decision-needed
Progress: 1 of 6 tasks done
Owner:    agents
Requires-Roy: true
Raised:   2026-08-16 (Roy, on the re-sweep's `gap`: "looks like a different form of the
          SUPPRESSED or acquittal list - and should be dropped - if comment blocks are
          missed by a reviewer then they are returned to the reviewer to rule on")
TRIAGED:  2026-08-23 — ONE OF SIX IS ALREADY FIXED: front matter is out of
          `prose_paragraphs`, so a licence header no longer reports INCOMPLETE forever.
          Every remaining citation was STALE and is re-measured below -- the two prose
          sentences this file tells the owner to change do not exist at the lines given,
          and one of them does not exist in any form. The two rulings gate the code
          change, which is why the status is decision-needed and not open.
```

## Objective

**A paragraph a reviewer never accounted for is unfinished work, not a finding about the run.**
Today `verdicts.py` computes the addresses no reviewer accounted for, prints a COVERAGE GAP
naming the role, and counts each one fatal. The run stops and a human reads a list of addresses.

RE-MEASURED 2026-08-23: `coverage_gaps` is `verdicts.py:117-134`, and its report is
`verdicts.py:520-529` -- *"COVERAGE GAPS - addresses no reviewer accounted for"*, one `fatal += 1`
per reviewer.

Roy ruled the other way: send those paragraphs back to the reviewer that skipped them and let it
rule. The gate keeps its job -- nothing passes unaccounted for -- but the outcome is a completed
census instead of a report that one is incomplete.

! **Why it groups with the two deleted lists.** Both of those let a reviewer stop early and have
the stopping recorded as a result: the acquittal list gave named reasons to pass a paragraph over,
the suppression list withheld low-precision hits. A coverage gap is the same shape one level up
-- the reviewer stopped, and the system files the stopping rather than fixing it.

! **Not vocabulary.** The word was found by the 2026-08-16 re-sweep, which is how the ruling
came up, but what changes here is control flow.

## Tasks

- [ ] * **T1 -- RULE how the return happens**: re-dispatch the same reviewer with only the missed
      addresses, or re-dispatch it with the whole census again. The first is cheap and loses the
      context that produced the miss; the second costs a full pass. Nothing in the tree decides
      this, and T3 cannot be written until it does.

- [ ] * **T2 -- RULE what bounds it.** A reviewer that returns an incomplete report twice has to
      stop somewhere, and *"send it back"* with no bound is a loop. Say what happens on the second
      failure -- that IS the case the current gate handles, so it must not simply be deleted.

- [ ] **T3 -- Change `verdicts.py:117-134` and `:520-529` once T1 and T2 are ruled.** ! The
      function itself is still needed: computing what is missing is how you know what to send
      back. Verify: a run whose reviewer skipped a paragraph ends with that paragraph RULED, and
      `verdicts.py` exits nonzero only on the bound T2 sets.

- [ ] **T4 -- Correct what the reviewer is TOLD about a gap.** ! THE CITED SENTENCE IS GONE:
      measured 2026-08-23, `ref/reviewer-brief.md:91-94` does not exist and the file is
      `references/reviewer-brief.md`; its one statement is at **line 137** -- *"`null` means you
      have not ruled yet, and a paragraph left `null` is a coverage gap"*. Under the ruling the
      consequence is different, and naming-and-shaming is no longer what happens. Verify: that
      line describes what actually follows a gap, and no other line in the brief contradicts it.

- [ ] **T5 -- Re-check `SKILL.md` against the new flow.** ! THE CITED RULE IS NOT THERE EITHER:
      measured 2026-08-23, `SKILL.md:82-84` says nothing about coverage and the phrase *"coverage
      is a COMPLETE READ"* does not occur in the file. What does: `SKILL.md:409` (what is
      ACCOUNTABLE), `:674` (*"the seeded file is why coverage is structural"*) and `:761` (the
      join exits nonzero on a coverage gap). Confirm rather than assume which of the three survive
      the ruling, and change only those that do not.

- [x] **T6 -- DONE. Front matter is out of the accountable set, so a licence header no longer
      reports INCOMPLETE forever.** Filed as *"one line: `prose_blocks` excludes `FRONT_MATTER`,
      as `verdicts.py` already does"*. VERIFIED 2026-08-23: `record.prose_paragraphs`
      (`record.py:667-673`) filters `series_of(b) != COVERS` with `COVERS = "f"`
      (`addresser.py:178`), and its docstring at `record.py:653-659` records the reason --
      *"a slot for one is a question nobody can answer -- it stays `null` and reports as a
      COVERAGE GAP, on every run, for as long as the file has a licence."*
