# A census row carries 19 fields and an empty place fills 7, with three different spellings of absent

```
Status:   open
Progress: 0 of 7 tasks done
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
