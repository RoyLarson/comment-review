# A superseded ruling keeps its own quotation, and the case gate reads that as unfixed

```
Status:   open
Progress: 0 of 3 tasks done
Owner:    testing
Requires-Roy: true
Raised:   2026-08-30 (found promoting prose-only commits to keyed cases, when the
          richest candidate was refused by the gate)
```

## Objective

`tests/harness/test_case_rows.py` keys a site by a sentence that is IN the file at
START and GONE at END. **That is what makes a row a key rather than a claim**, and
it refuses the best-written answer key in the pool.

!! **MEASURED 2026-08-30 on `3b642a0a -> 65b44f5d`**, the richest prose-only
candidate in 1047 commits at 59 insertions. Its most quotable defect --
*"this module supplies the folio and flattens the path, and addresses nothing"* --
**is still present at END**, because END supersedes the 2026-08-20 ruling by
QUOTING it: *"IT IS AN ADDRESSER, AND THE 2026-08-20 RULING AGAINST THAT NAME IS
SUPERSEDED. It read: ..."*. The gate rejects the site, correctly by its own rule
and wrongly about the work.

!! **AND THIS REPO REQUIRES THAT FORM, so it is not a one-off.** `CLAUDE.md`: a
superseded ruling is *"kept beside the one that replaced it rather than rewritten
away"*, and `docs/decision-log.md` is the dated chain of exactly these. **A
file-wide substring test therefore refuses the highest-quality prose fixes and
admits the ones that delete the error instead of recording it** -- the instrument
is biased against the convention it is measuring.

!! **THERE IS NO LATER END. THAT WAS THE FIRST THING CHECKED AND IT IS
EXHAUSTED.** Exactly one commit after `65b44f5d` touches
`plugins/comment-review/skills/comment-review/scripts/foliator.py`, and it is
`c1efd8f` -- **a 1507-line whole-file deletion carried inside a commit titled
"chore: ignore session worktrees"**. The module now lives at
`src/comment_review/reading/addresser.py`. So no commit in this history removes
that sentence from that file in place, and no endpoint exists to substitute.

! **WHICH MAKES THE ADDRESS THE FIX RATHER THAN THE ELEGANT OPTION.** The
question a site should ask is not *does this string appear in the file* but *is
this still ASSERTED at the place it occupied* -- and naming a place is what
`addresser.py` and `path@cue` already exist to do. A sentence quoted inside a
superseding paragraph sits at a different address from the one it was asserted
at.

!! **A SECOND SHAPE IS MISSING, AND THE SAME CASE IS WHERE IT SHOWS.** `sites`
keys a defect by the sentence that WAS there and is GONE. Prose that END **added**
-- the fence reason written into `owes_address`, explaining why a `d` takes no
address -- has no `said` at all, so an `add` finding cannot be recorded as a site
in any form. That is half of what the refused case would have contributed.

! **WHAT THE CASE IS WORTH IF BOTH LAND:** one `correct` on the false universal
*"EVERY LINE HAS EXACTLY ONE ADDRESS"* (false by 595 lines in its own directory,
measured over 8,746 paragraphs), one `correct` on the superseded naming ruling,
and one `add` on `owes_address` -- reaching `module-context` and a keyed
`add`, neither of which the four filed cases carry.

! **NOTHING HERE BLOCKS THE FOUR CASES ALREADY FILED.** They pass the gate as
written, because each of their sites was genuinely removed rather than quoted.
This is about which cases the pool can ADMIT next.

## Tasks

- [ ] Implement address-keyed sites, where gone-at-END means the sentence is no
      longer ASSERTED at the address it occupied rather than absent from the file.
      Verify: 3b642a0a to 65b44f5d files as a case carrying the addresses-nothing
      site, and tests/harness/test_case_rows.py passes over it.
- [ ] Implement a site shape for prose END ADDED where START held none, which
      carries no quoted sentence. Verify: the owes_address fence paragraph files
      as a site of that shape, and the gate asserts it present at END and absent
      at START.
- [ ] When END supersedes a ruling by quoting it, is a run credited for proposing
      the supersession-with-quotation, or only for correcting the claim? Verify:
      the answer is written into this file.
