# A census row carries 19 fields and an empty place fills 7, with three different spellings of absent

```
Status:   open (T6's ruling deferred to the cleanup; T7 and T9 do not wait on it)
Progress: 6 of 9 tasks done
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
page. ! **AND T9 COMES BEFORE THE TRIM**, because `lines` matches neither derivation: a
trim cannot tell a third fact from a stale field, so removing it either way is a guess.

## Tasks

- [x] T1 -- RECORD, not a task. MEASURED from the row Roy quoted, an empty b
      place: 19 fields, and 7 carry information -- path, kind, anchor, anchor_line,
      anchor_num, tier, address. The other 12 are empty, zero or a sentinel.
      Re-measured 2026-08-23: still 19 keys.
- [x] T2 -- RECORD, not a task. !! THREE SPELLINGS OF ABSENT IN ONE RECORD, and
      they disagree. start/end/lines/original_column say 0; original_start/
      original_end say null; declares says -1. The SAME paragraph therefore states
      it holds no lines three different ways -- and a consumer that tests any one
      of them is right about that field and wrong about the others. Re-measured
      2026-08-23 on row 0 of constants.py: all three present in one row.
- [x] T3 -- RECORD, not a task. ! IT IS THE DEFECT FIXED ON anchor_line THE SAME
      DAY, one field over. Roy then: *"the end of file getting a 0 is
      non-functional filling in for a missing value"*. 0 is a POSITION for a
      paragraph that has one and a NULL for a paragraph that does not, and nothing
      distinguishes the two readings.
- [x] T4 -- FINISHED. The question was whether start/end still has a reader now
      that the galley sets by ADDRESS and no longer splices by line. ANSWERED
      2026-08-23: it does -- addresser.py:1046, :1242, :1264, :1339 and :1432 build
      display spans from it, and census.py:401, :406, :498 and :587 read it for
      collision reporting. So it is a DUPLICATE (see T9), not a dead field, and
      what to do about it is T6.
- [x] T5 -- RECORD, not a task. ! tier is a fact about the FILE repeated on every
      row -- 135 paragraphs of repo.py each say tokenized -- and path is the full
      repo-relative path repeated 135 times while address already contains it.
      record.py already solved this with a PAGE ENVELOPE that names the file once;
      the census listing did not follow.
- [ ] T6 -- * RULING: which fields does a reviewer actually need? The answer
      decides the shape, and the shape is what stage 4 pastes into four prompts --
      so an unused field is paid for four times per page.
      !! **DEFERRED 2026-08-23, ASKED AND DECLINED FOR A REASON.** Roy: *"this is
      the next actual work to be done so deferring the decision until we get the
      current code cleaned up to a point that it isn't fluff we are deciding."*
      ! **RULING ON TODAY'S FIELD LIST WOULD RULE ON FIELDS THE CLEANUP IS ABOUT TO
      REMOVE**, so the answer would be obsolete on arrival and would have to be
      re-asked -- the same shape as `CLAUDE.md`'s *a thing whose dependencies are
      broken is refused, not worked on*. ! Waits on the binder CLI and the read
      chain -- [`lookup-parses-whole-census`](lookup-parses-whole-census.md) T6-T9
      and [`the-lexer-reads-no-files`](the-lexer-reads-no-files.md). ! Deferred is
      not done: the box stays unchecked because the ruling is still owed.
- [ ] T7 -- MEASURE THE COST BEFORE AND AFTER on a real census, in bytes and in
      the filtered listing, so the trim is reported as a number rather than as
      tidiness. Verify: both numbers written into this file, from a named
      `census.py --json` and `census.py --filtered` run.
- [x] T8 -- RECORD, not a task. MEASURED 2026-08-22 over the 135-row census of
      repo.py -- 73,429 bytes of field data, and roughly HALF is duplication or
      empty: path 9,450 (12.9%, the same string 135 times) plus address 9,727
      (13.2%) which CONTAINS that path; raw_lines 10,000 (13.6%) plus text 8,247
      (11.2%) which is the same prose joined; tier 2,565 (3.5%) one value 135
      times; annotations, notes, declares and symbol 8,944 together (12.2%) and
      empty on 125 to 130 of 135 rows.
- [ ] T9 -- ESTABLISH WHAT `lines` MEANS and write the definition where the record
      is built. !! start/end is a PURE DUPLICATE of original_start/original_end --
      identical on 80 of 135 rows of repo.py 2026-08-22, and on 20 of the 20 rows
      of constants.py where both exist, re-measured 2026-08-23; EVERY row where
      both exist, both times. ! But `lines` matches NEITHER derivation: equal to
      len(raw_lines) on 68 of 135 and to the original span on 13 of 135 (repo.py,
      2026-08-22), and equal to len(raw_lines) on 18 of 34 (constants.py,
      2026-08-23). Verify: a stated definition, plus a check that every row
      satisfies it. ! This lands BEFORE any trim -- the field may be a third fact
      or may be stale, and a trim cannot tell the two apart.
