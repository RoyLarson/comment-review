# There is no mark for LET IT STAND -- a declined proposal is not recorded, so the next run proposes it again

```
Status:   decision-needed
Progress: 1 of 7 tasks done
Owner:    comment-review
Requires-Roy: true
Raised:   2026-08-21 (Roy, 2026-08-21, on leading and matter both being categories
          publishing already had: 'this is twice now that we have realized we were
          categorically wrong about something that the publishing industry already knew
          and uses actively')
Named:    2026-08-21 — Roy: 'There is no stet. - we called this clean we were incorrect'
          -- the finding is not a missing word but clean carrying two facts
```

## Objective

!! **`clean` IS DOING TWO JOBS, AND ONE OF THEM IS `stet`.** Roy, 2026-08-21:
*"There is no stet. -- we called this 'clean' we were incorrect."*

Two different facts are being recorded under one word:

| the fact | what actually happened | what the record says today |
| --- | --- | --- |
| **clean** | a role read this paragraph and had nothing to report | `clean` |
| **stet** | a mark WAS proposed here, and the original stands | `clean` |

! **The second is a decision; the first is the absence of one.** A `stet` presupposes
a finding -- it is the answer to a mark, not a reading of the code. Publishing writes it
in the margin as *stet* ("let it stand") with dots under the text, precisely BECAUSE the
correction is still visible underneath: the page records that the change was considered
and refused, not that nobody looked.

!! **WHY THE CONFLATION COSTS SOMETHING.** A declined proposal recorded as `clean` says
*nothing was found here*, which is false. Nothing downstream can tell the two apart, so:

- a re-run raises the same finding again, and the author declines it again
- **stage 8 REVIEW cannot know a mark was refused** -- it reads the finished page and
  sees text a reviewer would flag, with no record that it was already flagged and kept
- the run's own report undercounts what the roles actually found

! **This is the third instance of the pattern in `CLAUDE.md`'s "it supplies categories,
not only names"** -- after `matter`/`f` and `leading`/`d`. The tell is the same each
time: one category straining to hold a second job, where publishing already has a
separate name for the half that does not fit.

## What it touches

`clean` is stated in twelve files. An eighth verdict is bounded but is not a one-line
edit, and **`record.py:792` carries a comment that counts them** (*"walks all seven
verdicts"*), as does `SKILL.md`'s heading and `CLAUDE.md` twice.

| file | what states `clean` |
| --- | --- |
| `scripts/record.py` | `VERDICTS`, and the count comment at :792 |
| `scripts/verdicts.py`, `scripts/desk.py` | what a report may carry |
| `SKILL.md` | `## The seven verdicts`, and the checkable/necessary matrix |
| the four `agents/*.md` | each role's own `clean`, which asserts something specific |
| `references/reviewer-brief.md`, `references/re-review.md` | the shipped field list |
| `CLAUDE.md` | the count at :179 and the reserved-word rule at :545 |
| `docs/vocabulary.md` | the reserved-word rule under "Rules about the words themselves" |

! **Not this branch.** `fix/folio-placement-is-not-where-the-anchor-is` is the
compositor and the five series; this is the verdict vocabulary. It wants 0.2.4 or its
own branch, after `python-cannot-read-python`.

## Tasks

- [ ] RULING: does a `stet` persist ACROSS RUNS, and if so where does it live --
      in the tree beside the code, or outside it? A stet that dies with the run
      records the decision for nobody
- [x] Name it -- publishing's mark is `stet` ("let it stand"), written in the
      margin with dots under the text, which is why the refused correction stays
      visible underneath
- [ ] Split `clean` in `record.py`'s `VERDICTS`: `clean` = no mark was proposed
      here, `stet` = one was and the original stands
- [ ] Measure the cost before building: run the same page twice and count how many
      identical proposals return
- [ ] Check whether stage 8 REVIEW re-raises what 7a declined -- it reads the
      finished page and cannot know a mark was refused
- [ ] Update the twelve files that state clean -- including the count comment at
      record.py:792 ('walks all seven verdicts'), SKILL.md's '## The seven
      verdicts' heading, CLAUDE.md at :179 and :545, and the reserved-word rule
      in docs/vocabulary.md
- [ ] Say what each ROLE's own stet asserts, in that role's own agent file -- each
      role's clean already asserts something specific, and a stet from ownership-
      context is not a stet from block-context
