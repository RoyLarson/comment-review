# The census to findings to verdicts path has never been determined against a backend that works

```
Status:   decision-needed
Progress: 3 of 7 tasks done
Owner:    testing
Requires-Roy: true
Raised:   2026-08-22 (Roy, 2026-08-22: that whole system of from census to findings to
          verdicts is something that needs to be determined now that the backend part of
          the system works)
Triaged:  2026-08-23 — three of the seven boxes were a MEASUREMENT, a cross-reference list
          and a filing note; none can be ticked by observation, so they are ticked here
          and restated in the Objective. ! The four that remain are three owed RULINGS
          and one artifact. ! Every TODO this file names was confirmed to exist in
          `TODO/` on 2026-08-23. ! The 19-field census row was RE-MEASURED with
          `census.py --json tests/fixtures/sample.py`: 19 keys, and an `interval` fills
          8 of them, not 7.
```

## Objective

**The census to findings to verdicts path has never been determined against a backend that
works**, and what makes it askable now is that the backend does. Roy, 2026-08-22: *"that whole
system of from census to findings to verdicts is something that needs to be determined now that
the backend part of the system works."*

!! **THE BACKEND NOW WORKS, MEASURED 2026-08-22**: a file to a census and a list of verdicts
back to a new file, byte-identical on 3,015 of 3,020 corpus files across ten languages, 0
collisions -- and all seven verdicts reduce to two operations, set the text at an address or
vacate it. **Every earlier design for the front half was drawn against a back half that could
not set a page**, which is why they are re-asked rather than resumed.

!! **WHAT CROSSES EACH OF THE THREE BOUNDARIES IS WHAT IS UNDETERMINED** -- census to reviewer,
reviewer to record, record to verdict. Each already has a filed defect, and this file is the hub
they resolve against rather than a duplicate of any of them:

| boundary | what is unsettled | filed as |
| --- | --- | --- |
| census -> reviewer | the row a reviewer is handed. MEASURED 2026-08-23: 19 fields, and an `interval` fills 8 | [`census-row-carries-empty-fields`](census-row-carries-empty-fields.md), [`the-census-is-mostly-intervals-nobody-rules-on`](the-census-is-mostly-intervals-nobody-rules-on.md) |
| reviewer -> record | what a finding IS -- `claim` is an object that renders to a marker string for checks written against the old form | [`claim-fallback-is-unreachable`](claim-fallback-is-unreachable.md), DEFERRED on this determination |
| record -> verdict | what the join certifies -- `verdicts.py` refuses a record `record.py` accepts and the reverse; coverage is structural but a gap goes nowhere | [`a-coverage-gap-should-go-back-to-the-reviewer`](a-coverage-gap-should-go-back-to-the-reviewer.md), [`record-and-verdicts-disagree`](record-and-verdicts-disagree.md) |

! **ALSO FILED AND IN SCOPE**:
[`ownership-is-read-first-but-nothing-makes-it-so`](ownership-is-read-first-but-nothing-makes-it-so.md),
[`the-author-approves-blocks-and-never-sees-the-page`](the-author-approves-blocks-and-never-sees-the-page.md),
[`a-malformed-page-drops-its-records`](a-malformed-page-drops-its-records.md).

!! **AND FOUR OF THE RECORD/VERDICTS FINDINGS ARE ONE CLASS**: `record.py --check` refuses a
record `verdicts.py` admits, and **the admitting one is the gate that certifies a review.**
! Which of the two is right is not answerable until this determination settles what a record IS,
which is why they are deferred to an independent session on
[`record-and-verdicts-disagree`](record-and-verdicts-disagree.md) rather than fixed one at a
time.

## Tasks

- [x] T1 -- NOT A TASK, restated in the Objective. THE BACKEND NOW WORKS, which is
      what makes this askable. MEASURED 2026-08-22: a file to a census and a list
      of verdicts back to a new file, byte-identical on 3,015 of 3,020 corpus
      files across ten languages, 0 collisions -- and all seven verdicts reduce to
      two operations, set the text at an address or vacate it. Every earlier design
      for the front half was drawn against a back half that could not set a page.
      A measurement is not a checkpoint.
- [ ] T2 -- * RULE WHAT A REVIEWER IS HANDED. A census row carries 19 fields and an
      empty place fills 8 -- RE-MEASURED 2026-08-23 with `census.py --json --repo .
      tests/fixtures/sample.py`, where an `interval` fills 8 and an `f` fills 6 --
      and what the four roles actually need decides that shape, which is pasted
      into four prompts per page. See
      [`census-row-carries-empty-fields`](census-row-carries-empty-fields.md).
      Finishes the day Roy names the fields.
- [ ] T3 -- * RULE WHAT A FINDING IS. `claim` is an object that renders to a marker
      string for checks written against the old form -- see
      [`claim-fallback-is-unreachable`](claim-fallback-is-unreachable.md), which is
      DEFERRED on this determination and cannot move until it lands.
- [ ] T4 -- * RULE WHAT THE JOIN CERTIFIES. `verdicts.py` refuses a record
      `record.py` accepts and the reverse; coverage is structural but a gap goes
      nowhere -- see
      [`a-coverage-gap-should-go-back-to-the-reviewer`](a-coverage-gap-should-go-back-to-the-reviewer.md).
- [x] T5 -- NOT A TASK, restated in the Objective. RELATED AND ALREADY FILED, so
      this is a hub rather than a duplicate:
      `the-census-is-mostly-intervals-nobody-rules-on`,
      `census-row-carries-empty-fields`, `claim-fallback-is-unreachable`,
      `a-coverage-gap-should-go-back-to-the-reviewer`,
      `ownership-is-read-first-but-nothing-makes-it-so`,
      `the-author-approves-blocks-and-never-sees-the-page`,
      `a-malformed-page-drops-its-records`. ! All seven confirmed present in
      `TODO/` on 2026-08-23. A list of cross-references is not a checkpoint.
- [ ] T6 -- WRITE WHAT *DETERMINED* HAS TO MEAN HERE, or this stays open forever:
      one statement of what crosses each of the three boundaries -- census to
      reviewer, reviewer to record, record to verdict -- with the fields NAMED.
      Verify: the statement exists in this file, every field it names is either a
      key `census.py --json` emits or one this determination adds, and each TODO
      listed in T5 is then either a task under it or ticked as superseded by it.
- [x] T7 -- NOT A TASK, restated in the Objective. THE RECORD/VERDICTS FINDINGS
      ARE FILED SEPARATELY, on `record-and-verdicts-disagree`, deferred to an
      independent session. Four of them are ONE class: `record.py --check` refuses
      a record `verdicts.py` admits, and the admitting one is the gate that
      certifies a review. ! Which of the two is right is not answerable until this
      determination settles what a record IS. A filing note is not a checkpoint.
