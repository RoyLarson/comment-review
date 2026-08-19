# The galley is the last index-keyed interface, at the write boundary

```
Status:   open
Progress: 0 of 3 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-19 (the seven-agent address review, 2026-08-19)
```

## Objective

!! **`galley.py --edits` TAKES `{"<census index>": ...}` AND NO RECORD CARRIES AN INDEX ANY MORE.**
So between stage 5 and the galley there is now a HAND conversion from address to census position,
with nothing checking it -- at the step that produces the artifact a human approves at 7a.

**An off-by-one there splices the wrong lines into the proof.** That is the one artifact the
author actually rules on, and the galley exists precisely because *"the splice is the first time
anyone sees the two together."*

! **It sits exactly at the round-2 boundary**, where `re-review.md` says *"THE ADDRESS DOES
CARRY, and it is what to quote back."* The one place the rebuild's property matters most is the
one place it is discarded.

! **The bridge already exists and is not wired.** `addresser.resolve(address, blocks)` returns
exactly the 1-based indices `galley` wants, and `record.entry_for` resolves an address to its
entry -- but `galley` imports neither. `SKILL.md` still documents the index form at the 5b/6b step.

## Tasks

- [ ] **Accept an address key through `record.entry_for`; keep `int` for held
      runs.** `addresser.resolve` already returns exactly the 1-based indices
      needed and is called only from inside addresser; galley imports neither
      addresser nor record.
- [ ] **`SKILL.md` still documents the index form** at the 5b/6b galley step.
- [ ] ! It sits exactly at the round-2 boundary, where `re-review.md` says *"THE
      ADDRESS DOES CARRY"* -- so the one place the rebuild's property matters most
      is the one place it is discarded.
