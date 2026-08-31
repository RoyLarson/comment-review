# The census to findings to verdicts path has never been determined against a backend that works

```
Status:   decision-needed
Progress: 3 of 11 tasks done
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
Split:    2026-08-23 -- every box cut to two lines. The one artifact box held three
          boundary statements and a reconciliation of seven TODOs, so it became four.
          Second pass: the collator box held two rulings, so 10 boxes became 11
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
| record -> verdict | what the collator certifies -- `verdicts.py` refuses a record `record.py` accepts and the reverse; coverage is structural but a gap goes nowhere | [`a-coverage-gap-should-go-back-to-the-reviewer`](a-coverage-gap-should-go-back-to-the-reviewer.md), [`record-and-verdicts-disagree`](record-and-verdicts-disagree.md) |

! **THE ROW WAS RE-MEASURED 2026-08-23** with `census.py --json --repo .
tests/fixtures/sample.py`: 19 keys, an `interval` fills 8 of them and an `f` fills 6. **What the
four roles actually need decides that shape**, and it is pasted into four prompts per page.

! **ALSO FILED AND IN SCOPE**:
[`ownership-is-read-first-but-nothing-makes-it-so`](ownership-is-read-first-but-nothing-makes-it-so.md),
[`the-author-approves-blocks-and-never-sees-the-page`](the-author-approves-blocks-and-never-sees-the-page.md),
[`a-malformed-page-drops-its-records`](a-malformed-page-drops-its-records.md).

! **THE SEVEN THIS FILE IS THE HUB FOR**, all confirmed present in `TODO/` on 2026-08-23:
`the-census-is-mostly-intervals-nobody-rules-on`, `census-row-carries-empty-fields`,
`claim-fallback-is-unreachable`, `a-coverage-gap-should-go-back-to-the-reviewer`,
`ownership-is-read-first-but-nothing-makes-it-so`,
`the-author-approves-blocks-and-never-sees-the-page`, `a-malformed-page-drops-its-records`.

!! **AND FOUR OF THE RECORD/VERDICTS FINDINGS ARE ONE CLASS**: `record.py --check` refuses a
record `verdicts.py` admits, and **the admitting one is the gate that certifies a review.**
! Which of the two is right is not answerable until this determination settles what a record IS,
which is why they are deferred to an independent session on
[`record-and-verdicts-disagree`](record-and-verdicts-disagree.md) rather than fixed one at a
time.

!! **WITHOUT A WRITTEN STATEMENT OF WHAT *DETERMINED* MEANS, THIS FILE STAYS OPEN FOREVER.** The
statement is one per boundary, with the fields NAMED, and every named field is either a key
`census.py --json` already emits or one this determination adds.

## Tasks

- [x] T1 -- NOT A TASK, restated in the Objective: THE BACKEND NOW WORKS, measured
      2026-08-22, which is what makes this askable. A measurement is not a checkpoint.
- [x] T2 -- NOT A TASK: the seven related TODOs are already filed, so this is a hub rather
      than a duplicate. Restated in the Objective.
- [x] T3 -- NOT A TASK: the record/verdicts findings are filed on
      `record-and-verdicts-disagree` and deferred there. Restated in the Objective.
- [?] T4 -- * **RULE WHAT A REVIEWER IS HANDED** -- which of the census row's 19 fields
      the four roles need. Verify: the ruling names them and is recorded in this file.
- [?] T5 -- * **RULE WHAT A FINDING IS**, `claim` included. Verify: the ruling is recorded
      in this file and `claim-fallback-is-unreachable` can move on it.
- [?] T6 -- * **RULE WHAT THE COLLATOR CERTIFIES**, and where a coverage gap goes. Verify: the
      ruling is recorded in this file.
- [?] T7 -- * Rule which of `record.py --check` and `verdicts.py` is right where they
      disagree. Verify: the ruling is recorded in this file.
- [?] T8 -- **State what crosses CENSUS -> REVIEWER, with the fields named.** Verify: each
      field is a key `census.py --json` emits or one this determination adds.
- [?] T9 -- **State what crosses REVIEWER -> RECORD, with the fields named.** Verify:
      every field it names is a key a record slot carries or one this determination adds.
- [?] T10 -- **State what crosses RECORD -> VERDICT, with the fields named.** Verify:
      every field it names is one `verdicts.py` reads or one this determination adds.
- [?] T11 -- **Reconcile the seven filed TODOs against those three statements.** Verify:
      each is a task under a statement or ticked as superseded by it.
