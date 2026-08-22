# A census row carries 19 fields and an empty place fills 7, with three different spellings of absent

```
Status:   open
Progress: 0 of 9 tasks done
Owner:    comment-review
Requires-Roy: true
Raised:   2026-08-22 (Roy, 2026-08-22, reading a census JSON: there are a lot of extra
          fields that have no information in them -- we should trim them to the things
          that are true and are necessary now)
```

## Objective

A census row carries 19 fields and an empty place fills 7, with three different spellings of absent.

## Tasks

- [ ] MEASURED from the row Roy quoted, an empty b place: 19 fields, and 7 carry
      information -- path, kind, anchor, anchor_line, anchor_num, tier, address.
      The other 12 are empty, zero or a sentinel
- [ ] !! THREE SPELLINGS OF ABSENT IN ONE RECORD, and they disagree.
      start/end/lines/original_column say 0; original_start/original_end say null;
      declares says -1. The SAME paragraph therefore states it holds no lines
      three different ways -- and a consumer that tests any one of them is right
      about that field and wrong about the others
- [ ] ! IT IS THE DEFECT FIXED ON anchor_line THE SAME DAY, one field over. Roy
      then: *the end of file getting a 0 is non-functional filling in for a
      missing value*. 0 is a POSITION for a paragraph that has one and a NULL for
      a paragraph that does not, and nothing distinguishes the two readings
- [ ] ! start/end vs original_start/original_end is TWO RANGES on one paragraph,
      and only the second is the paragraph own lines. Check whether start/end
      still has a reader now that the galley sets by ADDRESS and no longer splices
      by line
- [ ] ! tier is a fact about the FILE repeated on every row -- 135 paragraphs of
      repo.py each say tokenized -- and path is the full repo-relative path
      repeated 135 times while address already contains it. record.py already
      solved this with a PAGE ENVELOPE that names the file once; the census
      listing did not follow
- [ ] * RULING: which fields does a reviewer actually need? The answer decides the
      shape, and the shape is what stage 4 pastes into four prompts -- so an
      unused field is paid for four times per page
- [ ] ! MEASURE THE COST BEFORE AND AFTER on a real census, in bytes and in the
      filtered listing, so the trim is reported as a number rather than as
      tidiness
- [ ] MEASURED 2026-08-22 over the 135-row census of repo.py -- 73,429 bytes of
      field data, and roughly HALF is duplication or empty: path 9,450 (12.9%, the
      same string 135 times) plus address 9,727 (13.2%) which CONTAINS that path;
      raw_lines 10,000 (13.6%) plus text 8,247 (11.2%) which is the same prose
      joined; tier 2,565 (3.5%) one value 135 times; annotations, notes, declares
      and symbol 8,944 together (12.2%) and empty on 125 to 130 of 135 rows
- [ ] !! start/end IS A PURE DUPLICATE OF original_start/original_end -- identical
      on 80 of 135 rows, which is EVERY row where both exist. ! But lines matches
      NEITHER derivation: equal to len(raw_lines) on 68 of 135 and to the original
      span on 13 of 135. So it is a THIRD fact whose definition the record does
      not show, and establishing what it means has to come before any trim -- it
      may be right, or it may be a stale field nobody has checked
