# There is no mark for LET IT STAND -- a declined proposal is not recorded, so the next run proposes it again

```
Status:   decision-needed
Progress: 12 of 16 tasks closed
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

!! **ELEVEN BOXES WERE SUPERSEDED 2026-09-02, AND THE FINDING ABOVE SURVIVES THEM.**
This file was written as though `stet` were an EIGHTH ROLE INSTRUCTION -- added to a
role's verdict set, defined in the four role vocabularies, asserted in each of the four
agent files. It is not. **`stet` is the copy chief's**, and the two sets are closed and
different:

| | the set |
| --- | --- |
| the copy chief | `taken_in`, `stet`, `recast` -- `Vocabulary: #29` |
| a role | `hold`, `withdraw`, `correct`, `patch` -- `Process: #22` |

! **`Process: #9` SAID SO ON 2026-08-24 AND NAMED THESE BOXES BY ID**, then closed with
*"this entry records the correction rather than rewriting its boxes."* They stayed open
nine days. Roy, 2026-09-02: *"It was wrong to make that statement. supersede them."*
`Process: #79`.

!! **AND THE CONFLATION IS SMALLER THAN THIS FILE ARGUES.** Roy, 2026-09-02: *"it only
conflates because we haven't got the wording correct. Query also indicates that a mark
was declined in another way. In both cases it doesn't matter as much as it seems."*
**It is a WORDING problem, not a missing category** -- `clean` reads as two facts because
its sentence has not been written right, and a declined mark already reaches a reader
through `query` by another route. The table below states the two facts correctly and
overstates what follows from them.

! **WHAT SURVIVES IS THE REMEMBERING, NOT THE NAMING.** T1 asks whether a `stet` persists
ACROSS RUNS, T6 measures what re-proposal costs, T7 asks whether stage 8 re-raises what
7a declined, and T11 reserves the word. Where the mark is emitted is settled; whether
anything remembers it is the open half -- and by Roy's reading it is a smaller half than
this file's Objective claims.

! **The second is a decision; the first is the absence of one.** A `stet` presupposes
a finding -- it is the answer to a mark, not a reading of the code. Publishing writes it
in the margin as *stet* ("let it stand") with dots under the text, precisely BECAUSE the
correction is still visible underneath: the page records that the change was considered
and refused, not that nobody looked. **That is the NAME, settled 2026-08-21** -- the finding
was never a missing word, it was `clean` carrying two facts.

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

! **THE THIRTEEN ARE SPLIT INTO ONE BOX EACH BY ARTIFACT**, because a stranger ticks the
count claims, the shipped vocabulary, the reserved-word rule and the field lists at different
times, and `check_vocabulary.py` is the gate for only one of them.

! **AND EACH ROLE'S `stet` IS ITS OWN BOX.** Each role's `clean` already asserts something
specific, so a stet from `ownership-context` is not a stet from `block-context`; one box
covering four agent files would assert they share a definition.

! **Not this branch.** `fix/folio-placement-is-not-where-the-anchor-is` is the compositor and
the five series; this is the verdict vocabulary. It wants 0.2.4 or its own branch, after
`python-cannot-read-python`.

## Tasks

- [?] T1 | T1 -- * RULE whether a `stet` persists ACROSS RUNS, and where it
      lives if it does. Verify: the ruling is recorded in
      `docs/decision-log.md`.
- [x] T2 | FINISHED | unknown | T2 -- NAMED 2026-08-21. Publishing's mark is
      `stet` ("let it stand"), written in the margin with dots under the text.
      In the Objective.
- [-] T3 | SUPERSEDED -- stet is the copy chief's, not a role's. Vocabulary 29 gives the chief taken_in, stet and recast; Process 22 gives a role hold, withdraw, correct and patch. Process 79: Process 9 named this box and was wrong to leave it open | 5369f8a | T3
      -- Add `stet` to `record.py`'s `VERDICTS`: `clean` = no mark was proposed
      here, `stet` = one was and the original stands. Verify: `VERDICTS` holds
      eight.
- [-] T4 | SUPERSEDED -- stet is the copy chief's, not a role's. Vocabulary 29 gives the chief taken_in, stet and recast; Process 22 gives a role hold, withdraw, correct and patch. Process 79: Process 9 named this box and was wrong to leave it open | 5369f8a | T4
      -- Make `desk.py` admit a `stet` record. Verify: a record whose verdict is
      `stet` is admitted rather than refused.
- [-] T5 | SUPERSEDED -- stet is the copy chief's, not a role's. Vocabulary 29 gives the chief taken_in, stet and recast; Process 22 gives a role hold, withdraw, correct and patch. Process 79: Process 9 named this box and was wrong to leave it open | 5369f8a | T5
      -- Make `verdicts.py` admit a `stet` record. Verify: a report carrying
      `stet` joins against the census without exiting nonzero.
- [ ] T6 | T6 -- Measure the cost before building. Verify: the same page is run
      twice and the number of identical proposals returned on the second run is
      written into this file.
- [ ] T7 | T7 -- Check whether stage 8 REVIEW re-raises what 7a declined.
      Verify: a run with a mark declined at 7a is read at stage 8, and the
      answer is written here.
- [-] T8 | SUPERSEDED -- stet is the copy chief's, not a role's. Vocabulary 29 gives the chief taken_in, stet and recast; Process 22 gives a role hold, withdraw, correct and patch. Process 79: Process 9 named this box and was wrong to leave it open | 5369f8a | T8
      -- Update the three COUNT claims: `record.py:805`, `SKILL.md:53`,
      `CLAUDE.md:265`. Verify: no file says "seven verdicts" while `VERDICTS`
      holds eight.
- [-] T9 | SUPERSEDED -- stet is the copy chief's, not a role's. Vocabulary 29 gives the chief taken_in, stet and recast; Process 22 gives a role hold, withdraw, correct and patch. Process 79: Process 9 named this box and was wrong to leave it open | 5369f8a | T9
      -- Resolve `stet` in `SKILL.md`'s checkable/necessary matrix. Verify: the
      matrix names an outcome for `stet` as it does for the other verdicts.
- [-] T10 | SUPERSEDED -- stet is the copy chief's, not a role's. Vocabulary 29 gives the chief taken_in, stet and recast; Process 22 gives a role hold, withdraw, correct and patch. Process 79: Process 9 named this box and was wrong to leave it open | 5369f8a | T10
      -- Define `stet` in `vocabulary.toml` at :43 and add it to the four role
      lists. Verify: `uv run python scripts/check_vocabulary.py` passes.
- [ ] T11 | T11 -- Add `stet` to the reserved-word rule at `CLAUDE.md:780` and
      `docs/vocabulary.md:140`. Verify: both name `stet` beside `clean` as
      reserved.
- [-] T12 | SUPERSEDED -- stet is the copy chief's, not a role's. Vocabulary 29 gives the chief taken_in, stet and recast; Process 22 gives a role hold, withdraw, correct and patch. Process 79: Process 9 named this box and was wrong to leave it open | 5369f8a | T12
      -- Add `stet` to the shipped field lists in `reviewer-brief.md` and
      `re-review.md`. Verify: both list `stet` among the verdicts a report may
      carry.
- [-] T13 | SUPERSEDED -- stet is the copy chief's, not a role's. Vocabulary 29 gives the chief taken_in, stet and recast; Process 22 gives a role hold, withdraw, correct and patch. Process 79: Process 9 named this box and was wrong to leave it open | 5369f8a | T13
      -- Say what `ownership-context`'s own `stet` asserts, in its agent file.
      Verify: `agents/comment-review-ownership-context.md` states its own
      `stet`.
- [-] T14 | SUPERSEDED -- stet is the copy chief's, not a role's. Vocabulary 29 gives the chief taken_in, stet and recast; Process 22 gives a role hold, withdraw, correct and patch. Process 79: Process 9 named this box and was wrong to leave it open | 5369f8a | T14
      -- Say what `block-context`'s own `stet` asserts, in its agent file.
      Verify: `agents/comment-review-block-context.md` states its own `stet`.
- [-] T15 | SUPERSEDED -- stet is the copy chief's, not a role's. Vocabulary 29 gives the chief taken_in, stet and recast; Process 22 gives a role hold, withdraw, correct and patch. Process 79: Process 9 named this box and was wrong to leave it open | 5369f8a | T15
      -- Say what `function-context`'s own `stet` asserts, in its agent file.
      Verify: `agents/comment-review-function-context.md` states its own `stet`.
- [-] T16 | SUPERSEDED -- stet is the copy chief's, not a role's. Vocabulary 29 gives the chief taken_in, stet and recast; Process 22 gives a role hold, withdraw, correct and patch. Process 79: Process 9 named this box and was wrong to leave it open | 5369f8a | T16
      -- Say what `module-context`'s own `stet` asserts, in its agent file.
      Verify: `agents/comment-review-module-context.md` states its own `stet`.
