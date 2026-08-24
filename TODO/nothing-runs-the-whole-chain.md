# Nothing runs the whole backend chain, so no stage can be proven not to have moved

```
Status:   open
Progress: 0 of 4 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-24 (scoping the 0.2.4 round trip: every stage has tests and no test
          crosses two)
```

## Objective

**Every stage of the backend has its own tests and nothing runs the chain.** MEASURED
2026-08-24: `tests/` holds `test_page.py`, `test_census_blocks.py`, `test_record.py`,
`test_verdicts.py`, `test_galley.py`, `test_compositor.py` and `test_prove_unchanged.py` -- one
per stage -- and **no test carries an artifact from one stage into the next.** The nearest thing
is `test_fixture_identity.py`, which is read-and-set-back over one file and never touches a
verdict.

!! **SO A DEFECT THAT LIVES BETWEEN TWO STAGES IS INVISIBLE TO EVERY GATE THIS REPO HAS.** That
is not hypothetical here: `record-and-verdicts-disagree` is a whole file about `record.py --check`
refusing a record `verdicts.py` admits, and it was found by READING the two, because nothing runs
one's output into the other.

!! **AND THE REDESIGN HAS NOTHING TO HOLD CONSTANT.** The 0.2.4 plan sequences the round-trip
fixes ahead of the `io.py` and chain-of-custody rebuild, and the second phase's pass criterion is
that the artifacts do not move. **There is no artifact set to compare against**, so that criterion
cannot be stated, let alone met. Building this is what makes the second phase checkable.

! **THE MEASUREMENT IS MACHINERY, NOT EDITORIAL QUALITY.** What this compares is bytes -- the
census, the seeded record, the join's report, the drafted page, `prove_unchanged`'s verdict.
Whether the REVIEW got better needs a grader, which is `testing`'s and is
[`the-harness-cannot-run-the-system-it-grades`](the-harness-cannot-run-the-system-it-grades.md).
The two answer different questions and neither substitutes for the other.

! **T4 IS THE ONE THAT MAKES THE REST WORTH ANYTHING**, on `docs/gates.md`'s rule: *"does the
check pass" is not the question; "could the check fail" is.* A chain run assembled from stages
that already pass will pass on its first run; what it must do is go red when one of them breaks.

## Tasks

- [ ] T1 -- Build a fixture run: census, seed, record, join, galley, compositor, prove.
      Verify: one command produces every artifact and exits nonzero on a stage's refusal.
- [ ] T2 -- Record its artifacts as the baseline a later run is compared against. Verify:
      a re-run over an unchanged tree produces byte-identical artifacts.
- [ ] T3 -- Run it over every language fixture, not Python alone. Verify: one row per
      language in `tests/fixtures/`.
- [ ] T4 -- Prove it can FAIL. Verify: reverting a known defect in any stage turns it red.

## Related

- [`record-and-verdicts-disagree`](record-and-verdicts-disagree.md) -- the between-stages defect
  that was found by reading, because nothing ran one stage's output into the next
- [`the-harness-cannot-run-the-system-it-grades`](the-harness-cannot-run-the-system-it-grades.md)
  -- the same absence one level up: that one scores the REVIEW, this one the MACHINERY
