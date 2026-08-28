# A coverage gap should go back to the reviewer, not be reported as a result

```
Status:   decision-needed
Progress: 1 of 7 tasks done
Owner:    agents
Requires-Roy: true
Raised:   2026-08-16 (Roy, on the re-sweep's `gap`: "looks like a different form of the
          SUPPRESSED or acquittal list - and should be dropped - if comment blocks are
          missed by a reviewer then they are returned to the reviewer to rule on")
TRIAGED:  2026-08-23 -- ONE OF SIX IS ALREADY FIXED: front matter is out of
          `prose_paragraphs`, so a licence header no longer reports INCOMPLETE forever.
          Every remaining citation was STALE and is re-measured below -- the two prose
          sentences this file tells the owner to change do not exist at the lines given,
          and one of them does not exist in any form. The two rulings gate the code
          change, which is why the status is decision-needed and not open.
SPLIT:    2026-08-23 -- one action per box, and the code box became two: sending the
          missed addresses back is one change, and what `verdicts.py` exits on is the
          other. Six boxes became seven; the stale-citation measurements moved up.
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

! **The function itself is still needed.** Computing what is missing is how you know what to send
back; what changes is what happens to the answer.

! **Why it groups with the two deleted lists.** Both of those let a reviewer stop early and have
the stopping recorded as a result: the acquittal list gave named reasons to pass a paragraph over,
the suppression list withheld low-precision hits. A coverage gap is the same shape one level up
-- the reviewer stopped, and the system files the stopping rather than fixing it.

! **Not vocabulary.** The word was found by the 2026-08-16 re-sweep, which is how the ruling
came up, but what changes here is control flow.

### Where the prose actually is -- the cited lines were stale

- **The brief.** `ref/reviewer-brief.md:91-94` does not exist and the file is
  `references/reviewer-brief.md`; its one statement is at **line 137** -- *"`null` means you have
  not ruled yet, and a paragraph left `null` is a coverage gap"*. Under the ruling the consequence
  is different, and naming-and-shaming is no longer what happens.
- **`SKILL.md`.** `SKILL.md:82-84` says nothing about coverage and the phrase *"coverage is a
  COMPLETE READ"* does not occur in the file. What does: `:409` (what is ACCOUNTABLE), `:674`
  (*"the seeded file is why coverage is structural"*) and `:761` (the collator exits nonzero on a
  coverage gap). ! Confirm rather than assume which of the three survive the ruling, and change
  only those that do not.

### One of the six was already fixed

Filed as *"one line: `prose_blocks` excludes `FRONT_MATTER`, as `verdicts.py` already does"*.
VERIFIED 2026-08-23: `record.prose_paragraphs` (`record.py:667-673`) filters `series_of(b) !=
COVERS` with `COVERS = "f"` (`addresser.py:178`), and its docstring at `record.py:653-659` records
the reason -- *"a slot for one is a question nobody can answer -- it stays `null` and reports as a
COVERAGE GAP, on every run, for as long as the file has a licence."*

## Tasks

- [ ] T1 -- * RULE how the return happens: re-dispatch the reviewer with only the missed
      addresses, or with the whole census. Verify: the choice is recorded here.
- [ ] T2 -- * RULE what bounds it -- with no bound, *"send it back"* is a loop, and the
      second failure IS what the gate handles today. Verify: the bound is written here.
- [ ] T3 -- Send missed addresses back to the reviewer that skipped them, once T1/T2 rule.
      Touches `verdicts.py:117-134`, `:520-529`. Verify: a skipped paragraph ends RULED.
- [ ] T4 -- Make `verdicts.py` exit nonzero only on the bound T2 sets. Verify: a run
      inside the bound exits 0; a run past it exits nonzero.
- [ ] T5 -- Correct what the reviewer is TOLD about a gap, at `reviewer-brief.md:137`.
      Verify: that line describes what follows a gap, and no brief line contradicts it.
- [ ] T6 -- Re-check `SKILL.md:409`, `:674` and `:761` against the ruled flow, changing
      only those that do not survive it. Verify: each of the three matches the new flow.
- [x] T7 -- DONE. Front matter is out of the accountable set, so a licence header no
      longer reports INCOMPLETE forever. VERIFIED 2026-08-23 at `record.py:667-673`.
