# There is no mark for LET IT STAND -- a declined proposal is not recorded, so the next run proposes it again

```
Status:   decision-needed
Progress: 1 of 7 tasks done
Owner:    agents
Requires-Roy: true
Raised:   2026-08-21 (Roy, 2026-08-21, on leading and matter both being categories
          publishing already had: 'this is twice now that we have realized we were
          categorically wrong about something that the publishing industry already knew
          and uses actively')
Named:    2026-08-21 — Roy: 'There is no stet. - we called this clean we were incorrect'
          -- the finding is not a missing word but clean carrying two facts
RE-MEASURED: 2026-08-23 — the site list was re-run against the tree and THREE OF ITS
             POINTERS ARE STALE. The count comment is at `record.py:805`, not :792;
             CLAUDE.md states the count at :265 and the reserved-word rule at :780, not
             :179 and :545. ! AND ONE FILE IS MISSING FROM THE TABLE:
             `references/vocabulary.toml` defines `clean` at :43 and lists it in four
             separate role vocabularies (:115, :154, :194, :235) -- it is the file the
             SHIPPED vocabulary gate reads, so an eighth verdict that skips it ships a
             word no role is given. That makes THIRTEEN files, not twelve.
             ! The branch named at the foot is also stale: it is
             `fix/folio-placement-is-not-where-the-anchor-is`.
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

`clean` is stated in THIRTEEN files, re-measured 2026-08-23. An eighth verdict is bounded but
is not a one-line edit, and **`record.py:805` carries a comment that counts them** (*"`allowed()`
walks all seven verdicts"*), as does `SKILL.md`'s heading at :53 and `CLAUDE.md` twice.

| file | what states `clean` | verified |
| --- | --- | --- |
| `scripts/record.py` | `VERDICTS` at :181, and the count comment at :805 | 2026-08-23 |
| `scripts/verdicts.py`, `scripts/desk.py` | what a report may carry | 2026-08-23 |
| `SKILL.md` | `## The seven verdicts` at :53, and the checkable/necessary matrix | 2026-08-23 |
| the four `agents/*.md` | each role's own `clean`, which asserts something specific | 2026-08-23 |
| `references/reviewer-brief.md`, `references/re-review.md` | the shipped field list | 2026-08-23 |
| **`references/vocabulary.toml`** | the DEFINITION at :43 and four role lists at :115, :154, :194, :235 -- **missing from the original table** | 2026-08-23 |
| `CLAUDE.md` | the count at :265 and the reserved-word rule at :780 | 2026-08-23 |
| `docs/vocabulary.md` | the reserved-word rule at :140 | 2026-08-23 |

! **Not this branch.** `fix/folio-placement-is-not-where-the-anchor-is` is the compositor and
the five series; this is the verdict vocabulary. It wants 0.2.4 or its own branch, after
`python-cannot-read-python`.

## Tasks

- [ ] T1 -- * RULING: does a `stet` persist ACROSS RUNS, and if so where does it live
      -- in the tree beside the code, or outside it? A stet that dies with the run
      records the decision for nobody. Verify: the ruling is recorded in
      `docs/decision-log.md`.
- [x] T2 -- Name it -- publishing's mark is `stet` ("let it stand"), written in the
      margin with dots under the text, which is why the refused correction stays
      visible underneath.
- [ ] T3 -- Split `clean` in `record.py`'s `VERDICTS`: `clean` = no mark was proposed
      here, `stet` = one was and the original stands. Verify: `VERDICTS` holds eight
      entries and `desk.py` admits a `stet` record.
- [ ] T4 -- Measure the cost before building. Verify: the same page is run twice and
      the number of identical proposals returned on the second run is written into
      this file.
- [ ] T5 -- Check whether stage 8 REVIEW re-raises what 7a declined. Verify: a run
      where one mark is declined at 7a is read at stage 8, and this file records
      whether stage 8 raised it again.
- [ ] T6 -- Update the THIRTEEN files that state `clean`, per the table above --
      including the count comment at `record.py:805`, `SKILL.md:53`'s
      *"## The seven verdicts"* heading, `CLAUDE.md` at :265 and :780,
      `references/vocabulary.toml` at :43 and its four role lists, and the
      reserved-word rule at `docs/vocabulary.md:140`. Verify:
      `uv run python scripts/check_vocabulary.py` passes, and no file says "seven
      verdicts" while `VERDICTS` holds eight.
- [ ] T7 -- Say what each ROLE's own `stet` asserts, in that role's own agent file --
      each role's `clean` already asserts something specific, and a stet from
      `ownership-context` is not a stet from `block-context`. Verify: each of the four
      files under `plugins/comment-review/agents/` states its own `stet`.
