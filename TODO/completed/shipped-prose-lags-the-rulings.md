# The shipped prose lags the rulings, and it is what agents read

```
Status:   open
Progress: 6 of 6 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-19 (the seven-agent address review, 2026-08-19)
Narrowed: 2026-08-19 — B6 closed 2026-08-19: the numbering. Four sites, not the two this
          file named -- the brief plus three passages in addresser.py. Gated by a test
          that measures what the addresser answers and holds the prose to it.
Narrowed: 2026-08-19 — B7 closed 2026-08-19. Nine terms reviewers read had no
          definition, not the one this file named: address (262 uses), margin, interval,
          undocumented, trailing comment, intermediate comment, series, paragraph and
          page. `census` was stale twice over. `block` now reads 'a PARAGRAPH -- the
          older word', per the page/paragraph ruling; the ~1,935-site rename is filed
          separately as a-block-is-a-paragraph-on-a-page.
```

## Objective

!! **THE RULINGS LANDED IN THE CODE AND IN `docs/`; THE FILES AGENTS ACTUALLY READ WERE NOT
BROUGHT ALONG.** Four of seven review agents found this independently on 2026-08-19, each
arriving from a different question.

**The worst of it teaches an off-by-one to four reviewers.** `reviewer-brief.md` still carries
*"The number means a different statement in `b` than in `c`"* -- written while `c` counted from 1.
Since the 0-indexing ruling `bN` and `cN` name the SAME code line, so a reviewer following the
brief cites `c(N+1)` for the line it means. **In the file that costs 5x**, and the brief
contradicts itself 118 lines later where the newer text is right.

**And every role is handed a retired definition.** `vocabulary.toml` ships
`block = "The interval between two lines of CODE"` to all six -- the definition
`docs/vocabulary.md` replaced on 2026-08-19 -- while `address`, the record's primary key, is not
defined at all, and neither is `margin`, which is 30-50% of the rows a reviewer reads.
! `check_vocabulary.py` reports 0 holes because it checks that LISTED terms are defined; it cannot
notice a term of art the brief uses that nobody declared.

! **This is the same shape as the defect the release is named for** -- a fact stated in two places
and updated in one -- applied to prose rather than to code.

## Tasks

- [x] !! **DONE 2026-08-19 -- both files teach `bN` and `cN` name the SAME code line.**
      It said *"The number means a different statement in `b` than in `c`"*, written
      when `c` counted from 1, with the rule *"code line N carries `b(N-1)` above it
      and `cN` beside it"* -- so a reviewer following the brief cited `c(N+1)`, the
      off-by-one the paragraph warns about, inverted, in the file that costs 5x.
      ! **FOUR sites, not two**: the brief, and THREE passages in `addresser.py` --
      its module docstring's example, the rule paragraph, and `stable()`'s example,
      which also still carried the retired dotted path form.
      ! **The ambiguity that hid it is the phrase "code line 3"**, which reads as the
      3rd to one reader and as index 3 to another. One half of the pair stayed wrong
      while the other stayed right, inside one paragraph, for that reason. Both files
      now say *"the code line at index N"*.
      ! **Gated.** `TestTheSHIPPEDPROSETeachesTheNumberingTheCodeUSES` measures what
      the addresser answers and holds both files to it -- prose is not executed, so
      nothing else would notice it drifting back.
- [x] !! **DONE 2026-08-19 -- and it was NINE terms, not one.** `vocabulary.toml` ships the RETIRED definition of a block to all six
      roles** -- `block = "The interval between two lines of CODE"` -- and
      **`address` is not defined at all**, nor `margin`, which is 30-50% of the
      rows a reviewer reads. ! `check_vocabulary.py` reports 0 holes because it
      checks that LISTED terms are defined; it cannot notice a term of art the
      brief uses that nobody declared.
- [x] !! **DONE 2026-08-19.** `SKILL.md` was never converted. Seven passages assert the census
      index as live -- *"that index is what the join resolves"*, *"the record
      needs a `BLOCK` index"*, *"Each slot arrives carrying the census `block`
      index"* -- and the address form appears in it NOWHERE. It also contradicts
      itself on what `contradictions()` keys on.
- [x] **DONE 2026-08-19.** `reviewer-brief.md`'s worked record opened `{ "block": 17,` -- a field
      `--seed` no longer writes.
- [x] **DONE 2026-08-19.** ~25 producer docstrings described removed behaviour. `intervals()`
      contradicts itself inside one docstring; `census.py` says `edit_start` is
      set "nowhere else" and it is set in three places; `splice_range` states a
      fallback its body removed; `stable()` names a function that does not exist
      and the one site `census.py` forbids.
- [x] **DONE 2026-08-19 -- and one had rotted TWICE.** Two measurements rotted in the same two places that recorded them
      rotting.** `SKILL.md` and `verdicts.py` both say *"census.py over itself is
      642 blocks, 76 of them prose"*; measured 2026-08-19 it is **1,504 blocks,
      103 prose**. `verdicts.py` already carries the note *"Re-measure both or
      neither."*
