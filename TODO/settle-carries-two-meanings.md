# `settle` carries two meanings in what an agent is handed, and neither is declared to it

```
Status:   open
Progress: 0 of 6 tasks done
Owner:    systems
Requires-Roy: true
Raised:   2026-08-24 (the moment `taken in` was ruled -- Roy: 'now we have a polysemy of
          the word settled and that has to get resolved')
Reassigned: 2026-08-24 — Filed `agents`, reassigned `systems` the same day, with
          `no-stage-agrees-the-terms`. Roy: *"that is a todo list for the systems lane."*
          ! T2-T4 are edits in `agents`-owned files and T5 in `backend`-owned scripts:
          the OWNER ticks the boxes, and the lane owning each file makes the edit. ! The
          vocabulary belongs to NO lane, which is why any lane could have filed this.
```

## Objective

**`settle` means two things in the shipped tree and the ambiguity is inside the prompt.** Roy,
2026-08-24, immediately after ratifying `taken in`: *"now we have a polysemy of the word settled
and that has to get resolved."*

| sense | what it is about | where |
| --- | --- | --- |
| **a CLAIM settled by evidence** | `query` names *what would settle* it; an unsettled claim is an open one | `record.py`'s `needs_settles`, the brief's `settles` key, `SKILL.md:68`'s `unsettled` |
| **a DECISION settled by a ruling** | a term, a definition or a design that is agreed and not reopened | `CLAUDE.md`, `docs/`, and 54 shipped uses |

!! **MEASURED 2026-08-24: 94 uses across 19 shipped files, 35 more in `docs/`.** Of the shipped
uses **40 are the claim sense** -- `settles` 32, `needs_settles` 6, `unsettled` 2.

!! **AND 43 SIT IN WHAT AN AGENT IS HANDED**, which is what makes this different from the
polysemies already allowed: `SKILL.md` 15, `reviewer-brief.md` 16, the four role files 7,
`compact.md`/`write.md`/`re-review.md` 5.

! **`docs/vocabulary.md` allows polysemy WHEN IT IS DECLARED AND THE CONTEXTS DO NOT OVERLAP.**
`leaf` passes that test by confinement -- 10 uses, all in `.py`, **none in `agents/`, `SKILL.md`
or `references/`**, so nothing an agent reads carries the ambiguity. **`settle` fails it on both
counts**: undeclared until today, and 43 of its uses are in the prompt.

! **A THIRD SENSE IS ALREADY RETIRED BY `stet`.** `re-review.md:139` writes *"a paragraph stage 5
settled"* -- that is the copy chief's ruling, and `decision-log.md Vocabulary: #12` gave it its
own word. That use is a rename, not a disambiguation.

!! **AND `settled` WAS PROPOSED AS A TERM OF ART TODAY**, for the mark carried into the text.
Roy's own criterion refused it -- *"not overly generic like set"* -- and the 94 uses are why.
**The proposal is the evidence: a word this saturated cannot take a new load**, and the near miss
is what raised the polysemy.

! **What is NOT yet decided is which sense keeps the word.** The claim sense is a shipped CONTRACT
-- `settles` is a key a reviewer types -- so it is the expensive one to move; the decision sense
is prose and is the frequent one. T1 is that ruling.

## Tasks

- [?] T1 | T1 -- * Rule which sense keeps `settle`, and what the other becomes.
      Verify: the ruling is in `docs/decision-log.md`.
- [ ] T2 | T2 -- Reword the losing sense in `SKILL.md`. Verify: `grep -c settle`
      counts only the kept sense.
- [ ] T3 | T3 -- Reword it in `reviewer-brief.md`. Verify: the same count, and
      the brief still generates from its row.
- [ ] T4 | T4 -- Reword it in the four role files. Verify: each file uses only
      the kept sense.
- [ ] T5 | T5 -- `backend` -- reword it in the scripts if the claim sense loses.
      Verify: `needs_settles` and the `settles` key follow the ruling.
- [ ] T6 | T6 -- Declare the outcome in `docs/vocabulary.md` and confine it.
      Verify: the kept sense is defined and the other appears in no shipped
      file.

## Related

- [`no-stage-agrees-the-terms`](no-stage-agrees-the-terms.md) -- this is one instance of what
  that file is about; it was found by a person in conversation and by no gate
- [`nothing-makes-the-fair-copy`](nothing-makes-the-fair-copy.md) -- where `taken in` and `stet`
  were ruled, and where `settled` was proposed and measured out
