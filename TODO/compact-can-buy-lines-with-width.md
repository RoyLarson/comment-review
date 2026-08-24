# COMPACT can buy lines with width, and nothing stops it

```
Status:   in-progress
Progress: 2 of 7 tasks done
Owner:    agents
Requires-Roy: false
Raised:   2026-08-17, on the FIRST exercise of stage 6 -- it returned two blocks at
          exactly the cap by writing lines 20 columns wider than anything in the file
TRIAGED:  2026-08-23 — 2026-08-23. T1 is a RULING ALREADY MADE (2026-08-17, WHICHEVER IS
          LESS) -- it is true the day it was written and every day after, so it stays
          ticked as a record and its content is kept in the Objective. T6 is a RECORD of
          what the run got right, which nobody ticks either; ticked and left in place.
          The four middle boxes are real checkpoints and are untouched but for their
          labels. ! Status stays `in-progress`: a ruling has landed, and CLAUDE.md says a
          file where only a RULING has landed is in-progress, because a ruling is work.
RE-VERIFIED: 2026-08-23 — 2026-08-23. The defect is unchanged in the shipped tree:
             a case-insensitive count of `width`, `column` and `character` over
             `plugins/comment-review/skills/comment-review/references/compact.md` returns
             **0**. So T2, T3 and T5 all still have nothing written against them, and T4
             has nothing in the style sheet to read. The 2026-08-17 ruling has not
             reached the file it rules on.
SPLIT:    2026-08-23 -- the KIND box held a PROHIBITION and the TEST that separates a
          legitimate `move` from cap-dodging; they are two sentences a stranger ticks
          separately, so they are two boxes. Every box cut to two lines. ! The TRIAGED
          and RE-VERIFIED notes above name the PRE-SPLIT labels.
```

## Objective

**A cap counts LINES. Widening a line removes a line and loses nothing, so it is the cheapest
way to satisfy a cap -- and `compact.md` says nothing about width.** Zero occurrences of
`width`, `column` or `character` in the file, re-measured 2026-08-23.

Measured on the first run to reach stage 6: it returned both over-cap blocks at exactly 6 lines,
written at **98-100 columns**, in a file whose 144 comment lines measure **median 76, max 80,
and 0 over 80**. The published limit was wider than the habit, so nothing was violated and the
result does not read like the file.

!! **This is the failure `SKILL.md` 1.2 already names, arriving at the other end of the run:**
*"matching the number while counting differently produces a file that claims to comply and does
not."* Stage 6 matched the number it was given and counted a different thing.

! **It is structural, not a lapse.** Every other route to fewer lines costs information --
cutting a clause, dropping a citation, deleting provenance -- and `compact.md` forbids all of
them, at length and correctly. Widening costs nothing. An agent told to minimise lines and
handed no width will take the free move every time.

! The compact agent FLAGGED it rather than deciding it, which is what its contract asks for.
The defect is that it had to.

## * RULED 2026-08-17: WHICHEVER IS LESS

Roy, verbatim. **Both the published width and the observed wrap bind stage 6, and the tighter
one wins.** ! That is what forbids the measured trade: the repo published 104, the tree writes
76-80 over 144 lines, so 80 binds and the 98-column reflow is refused. ! A block that cannot
reach the cap under the tighter bound has an existing answer in `compact.md` -- report it, name
the owner, do not cut.

! **THE RULING HAS NOT REACHED `compact.md`.** It was made 2026-08-17 and the file still holds
zero occurrences of `width`, `column` or `character` (2026-08-23). T2 through T6 are what would
put it there.

## ! SECOND MEASUREMENT 2026-08-17: giving it the PUBLISHED width bounds the damage, not the move

The end-to-end cycle run put the published width in the style sheet -- 88 columns, from
`line-length` in `pyproject.toml`, enforced by `ruff` in the gate of this repo -- which the
input of the first run did not carry. One block was over a cap of 4.

| | lines | longest line |
| --- | --- | --- |
| after stage 5 | 5 | 79 |
| after COMPACT | 4 | **87** |

**It stayed inside the published width and still took the free move**, spending the whole
headroom between what the file writes and what the limit permits. Nothing was violated: 87 is
legal, `ruff` passes, and the block is at the cap.

! **So the published width is not the missing input** -- it was supplied and the behaviour is
the same, one column short of the limit instead of twenty past it. That is the argument for the
OBSERVED wrap above, measured from the tree the way 1.3 measures the templates, rather than for
passing the published number.

! The agent did not flag it this time, which is consistent: with a width in hand and its output
inside it, there was nothing for its contract to report.

## ! The published width is not the observed one, and the style sheet is where that belongs

The repo of that run permitted 104 columns and wrote 76-80. `SKILL.md` 1.2 is right to refuse an
invented cap -- *"a number you chose becomes a project fact in the output"* -- so the fix is not
a measured width passed as a flag.

**The STYLE SHEET already holds what the tree DOES**, measured: the documentation templates come
from 1.3 the same way. An observed wrap is that kind of fact, and the style sheet is already in
the input contract of stage 6. What is missing is any instruction to read it.

! **AND IT MUST NOT BECOME A FLAG.** `census.py` takes no width, and 1.2 refuses an invented
number.

## !! WIDTH is not the only free move -- KIND is the other one

A `#` run has a cap. A docstring does not: *"A `#` comment is governed by LENGTH; a docstring by
FORMAT."* So **converting a comment into a docstring satisfies a cap at zero information cost**,
exactly as widening does. Two escape hatches, same shape, neither named anywhere.

! The line between legitimate and dodging is thin and has to be written down: relocating prose
into a docstring is a real `move` **when a declaration genuinely owns the rule**, and is
cap-dodging when the docstring is the nearest place the cap cannot reach.

! **STAGE 6 CANNOT MAKE THAT CALL ITSELF** -- it holds one block and its kind -- so the rule may
have to be that stage 6 REPORTS the conflict and never re-kinds anything, which is what it
already does for every other conflict.

## ! What the 2026-08-17 run got RIGHT, so a later pass does not rewrite the good part

It refused to cut evidence, it reported the conflict instead of resolving it, and the
move-then-compact ordering was validated -- block 3040 was 13 lines before a `move` split it and
8 after, so a compaction run before the move would have condensed a block that was about to
become two.

! It also stayed on the right side of the KIND line and shows how: it did NOT propose the
relocation. It reported that no function owns the rule -- three rules stacked at one call site
because clear-on-close has no home -- and named the owner that should exist. That is a code
change, so it went to `CODE CONCERNS` and not to a verdict. `compact.md` had predicted the
diagnosis in those words: *"usually a rule with no owning function, so every site performing
part of it re-explains the whole."*

! **THAT IS ALSO THE ANSWER T6 SHOULD WRITE DOWN.** On the measured run the block was 7 lines at
the wrap of the file and 6 at 98 columns, and the operator took the code finding. `compact.md`
already gives that answer and it worked; what is missing is the sentence saying it is the rule
for this case.

## Tasks

- [x] T1 -- RULING, MADE 2026-08-17: WHICHEVER IS LESS. Both the published width and the
      observed wrap bind stage 6, and the tighter wins. Kept in full in the Objective.
- [ ] T2 -- Say in `compact.md` that a block may not change KIND to escape the cap.
      Verify: the words are there and `scripts/check_vocabulary.py` still passes.
- [ ] T3 -- State in `compact.md` the test that separates a legitimate `move` into a
      docstring from cap-dodging. Verify: the file names both sides of that line.
- [ ] T4 -- Say in `compact.md` that lines may not be widened to buy a line, under T1.
      Verify: `width` occurs in the file and the sentence states WHICHEVER IS LESS.
- [ ] T5 -- Add the observed comment wrap to the measured section of the STYLE SHEET.
      Verify: the style sheet carries the number and says it was measured, not published.
- [ ] T6 -- Write the rule for what stage 6 reports when in-cap and at-habit conflict.
      Verify: `compact.md` names the case and says what stage 6 emits.
- [x] T7 -- RECORD, not a task. What the 2026-08-17 run got RIGHT, kept in the Objective
      so a later pass does not rewrite the good part.
