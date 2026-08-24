# A census row carries 19 fields and an empty place fills 7, with three different spellings of absent

```
Status:   open (T6's ruling deferred to the cleanup; T7 and T9 do not wait on it)
Progress: 6 of 10 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-22 (Roy, 2026-08-22, reading a census JSON: there are a lot of extra
          fields that have no information in them -- we should trim them to the things
          that are true and are necessary now)
TRIAGED:  2026-08-23 — 2026-08-23. T1, T2, T3, T5 and T8 are MEASUREMENTS, not
          checkpoints -- nobody ticks a measurement, so they are ticked as RECORDS and
          left in place. T4 was a real task and is ANSWERED. What is left is T6 (the
          owed ruling), T7 (measure the trim) and T9 (what `lines` means).
RE-TRIAGED: 2026-08-23 — 2026-08-23, every measurement re-run rather than trusted. Ran
            `census.py --repo . --json` over `constants.py` (34 rows): 19 distinct keys,
            exactly the 19 listed below; row 0 carries start/end/lines/original_column =
            0, original_start/original_end = null and declares = -1, so all three
            spellings of absent sit in ONE record; start/end equals original_start/
            original_end on 20 of the 20 rows where both exist; lines equals
            len(raw_lines) on 18 of 34. ! The start/end READERS are still there --
            addresser.py:1046, :1242, :1264, :1339, :1432 and census.py:401, :406, :498,
            :587 -- so T4 stays answered and ticked.
```

## Objective

A census row carries 19 fields and an empty place fills 7, with three different spellings of absent.

The 19 keys, from a run on 2026-08-23: `address`, `anchor`, `anchor_line`, `anchor_num`,
`annotations`, `declares`, `end`, `kind`, `lines`, `notes`, `original_column`,
`original_end`, `original_start`, `path`, `raw_lines`, `start`, `symbol`, `text`, `tier`.

!! **THE RULING IS WHAT THE FILE IS FOR.** Which fields a reviewer actually needs decides
the shape stage 4 pastes into four prompts, so an unused field is paid for four times per
page. ! **AND THE `lines` QUESTION COMES BEFORE THE TRIM**, because `lines` matches neither
derivation: a trim cannot tell a third fact from a stale field, so removing it either way is
a guess.

## The measurements, all re-run 2026-08-23

- **SEVEN OF NINETEEN CARRY INFORMATION.** MEASURED from the row Roy quoted, an empty `b`
  place: 19 fields, and 7 carry information -- `path`, `kind`, `anchor`, `anchor_line`,
  `anchor_num`, `tier`, `address`. The other 12 are empty, zero or a sentinel. Re-measured
  2026-08-23: still 19 keys.
- !! **THREE SPELLINGS OF ABSENT IN ONE RECORD, AND THEY DISAGREE.** `start`/`end`/`lines`/
  `original_column` say 0; `original_start`/`original_end` say null; `declares` says -1. The
  SAME paragraph therefore states it holds no lines three different ways -- and a consumer that
  tests any one of them is right about that field and wrong about the others. Re-measured
  2026-08-23 on row 0 of `constants.py`: all three present in one row.
- ! **IT IS THE DEFECT FIXED ON `anchor_line` THE SAME DAY, one field over.** Roy then: *"the
  end of file getting a 0 is non-functional filling in for a missing value"*. 0 is a POSITION
  for a paragraph that has one and a NULL for a paragraph that does not, and nothing
  distinguishes the two readings.
- ! **`tier` AND `path` ARE FILE FACTS REPEATED ON EVERY ROW** -- 135 paragraphs of `repo.py`
  each say `tokenized`, and `path` is the full repo-relative path repeated 135 times while
  `address` already contains it. `record.py` already solved this with a PAGE ENVELOPE that
  names the file once; the census listing did not follow.
- **HALF THE BYTES ARE DUPLICATION OR EMPTY.** MEASURED 2026-08-22 over the 135-row census of
  `repo.py` -- 73,429 bytes of field data: `path` 9,450 (12.9%, the same string 135 times) plus
  `address` 9,727 (13.2%) which CONTAINS that path; `raw_lines` 10,000 (13.6%) plus `text`
  8,247 (11.2%) which is the same prose joined; `tier` 2,565 (3.5%) one value 135 times;
  `annotations`, `notes`, `declares` and `symbol` 8,944 together (12.2%) and empty on 125 to
  130 of 135 rows.

## `start`/`end` has readers, and is a duplicate rather than dead

ANSWERED 2026-08-23, on the question of whether `start`/`end` still has a reader now that the
galley sets by ADDRESS and no longer splices by line: it does. `addresser.py:1046`, `:1242`,
`:1264`, `:1339` and `:1432` build display spans from it, and `census.py:401`, `:406`, `:498`
and `:587` read it for collision reporting.

!! **SO IT IS A PURE DUPLICATE OF `original_start`/`original_end`** -- identical on 80 of 135
rows of `repo.py` 2026-08-22, and on 20 of the 20 rows of `constants.py` where both exist,
re-measured 2026-08-23. EVERY row where both exist, both times.

! **BUT `lines` MATCHES NEITHER DERIVATION**: equal to `len(raw_lines)` on 68 of 135 and to the
original span on 13 of 135 (`repo.py`, 2026-08-22), and equal to `len(raw_lines)` on 18 of 34
(`constants.py`, 2026-08-23). The field may be a third fact or may be stale, and a trim cannot
tell the two apart -- which is why it is settled before anything is removed.

## !! The ruling is DEFERRED, and it was ASKED AND DECLINED FOR A REASON

Roy, 2026-08-23: *"this is the next actual work to be done so deferring the decision until we get
the current code cleaned up to a point that it isn't fluff we are deciding."*

! **RULING ON TODAY'S FIELD LIST WOULD RULE ON FIELDS THE CLEANUP IS ABOUT TO REMOVE**, so the
answer would be obsolete on arrival and would have to be re-asked -- the same shape as
`CLAUDE.md`'s *a thing whose dependencies are broken is refused, not worked on*.

! **What it waits on**: the binder CLI and the read chain --
[`lookup-parses-whole-census`](lookup-parses-whole-census.md) T6-T9 and
[`the-lexer-reads-no-files`](the-lexer-reads-no-files.md).

! **Deferred is not done**: the box stays unchecked because the ruling is still owed.

## Tasks

- [x] T1 -- RECORD, not a task. Seven of nineteen fields carry information. In the
      Objective.
- [x] T2 -- RECORD, not a task. Three spellings of absent in one record. In the Objective.
- [x] T3 -- RECORD, not a task. The same defect as `anchor_line`, one field over, with
      Roy's 2026-08-23 quotation. In the Objective.
- [x] T4 -- FINISHED. `start`/`end` still has readers, so it is a duplicate and not a dead
      field. The nine call sites are in the Objective.
- [x] T5 -- RECORD, not a task. `tier` and `path` are file facts repeated per row. In the
      Objective.
- [ ] T6 -- * RULE which fields a reviewer actually needs. DEFERRED -- see the Objective.
      Verify: the ruling is recorded in `docs/decision-log.md`.
- [ ] T7 -- Measure the trim in bytes and in the filtered listing, before and after.
      Verify: both numbers from named `--json` and `--filtered` runs are written here.
- [x] T8 -- RECORD, not a task. 73,429 bytes over `repo.py`, roughly half duplication or
      empty, field by field. In the Objective.
- [ ] T9 -- State what `lines` MEANS, in a comment where the record is built. Verify: the
      definition is written at the build site and names its derivation.
- [ ] T10 -- Check every census row against T9's definition. Verify: a named `census.py
      --json` run over a real file has no row that violates it. ! Lands before any trim.
