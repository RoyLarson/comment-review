# 7a can PROVE the change by applying it to a copy and diffing

```
Status:   open
Progress: 2 of 5 tasks done
Owner:    session * Roy (raised it, 2026-08-17)
Raised:   2026-08-17, while ruling on what CLAIM and CHANGE each carry
```

## Objective

**Nothing between the reviewer and the author ever renders the proposed text as a FILE.** Stage
7a presents `CHANGE` -- a block of replacement prose -- and the author rules on it as prose. What
lands on disk at 7b is that block spliced into a file, and the splice is the first time anyone
sees the two together.

Roy, 2026-08-17: *"Maybe at the reviewer at 7a where things are temporarily applied"* ... *"Or
applied to a copy and diffed."*

! **The copy is what makes it safe.** 7a's contract is that the run STOPS and writes nothing;
applying to a copy under the scratch tree keeps that contract while producing a real diff.

## Why the diff is worth more than the block

A `CHANGE` block is checked for existence and nothing else -- `payload_problem` says so in as
many words, because no checker can judge whether prose is good. A diff is checkable by the
author at a glance, and it answers three questions the block cannot:

| question | the block | the diff |
| --- | --- | --- |
| does it land where the `BLOCK` says | no | yes -- the hunk header names the line |
| did the indentation and comment marker survive | no | yes |
| did an adjacent block get clipped | no | yes -- the hunk shows its neighbours |

! The third is the one that motivated this. `CHANGE` carries *the surrounding block*, so two
findings on adjacent blocks each carry overlapping context, and splicing both is where a line
gets eaten. Today that is discovered at 7b, after approval.

## ! It is NOT a reviewer, and must not become one

The name in Roy's note is *"the reviewer at 7a"*, but stage 8 is the proofreader and this is
not a second one. This renders; it does not rule. ! A stage that both produces the diff and
judges it would be MARK and APPLY in one actor, which is the thing the pipeline separates.

## Tasks

- [x] **DONE 2026-08-17 -- `scripts/galley.py --out DIR` decides where the copy lives**, and the
      caller names it. The run directory already holds the census; a galley tree mirroring only
      the files an edit touches is the smallest thing that works, and it is discarded with the
      run. ! The name is the publishing one: a GALLEY is the trial impression, set but not yet
      made into pages, produced so it can be corrected before anything is committed. `proof` was
      unavailable -- `prove_unchanged.py` already owns it for the CODE CHECK.

- [x] **DONE 2026-08-17 -- the splice.** `galley.splice` applies every edit in DESCENDING line
      order, which is what makes the census ranges mean anything: a replacement rarely has the
      line count of what it replaces, so a top-down splice shifts every range below the one just
      written. Overlapping edits and stale ranges are refused before anything is written.
      ! `git diff --no-index <original> <galley>` is then the author's view, and is still to be
      wired into 7a -- see the task below.

      !! **It was built for the re-review blocker and this task at once**, because both needed
      the same thing: the proposed state rendered as real files. See
      [`re-review-is-ordered-everywhere-and-defined-nowhere`](completed/re-review-is-ordered-everywhere-and-defined-nowhere.md).

- [ ] Show the diff at 7a INSTEAD OF or ALONGSIDE the block -- decide which. ! Roy's rule that
      *what you show IS what gets written* argues for the diff being primary: it is the closer
      of the two to what lands.

- [ ] Say what happens when the splice FAILS -- a `BLOCK` whose census range no longer matches
      the file, two `CHANGE`s overlapping. ! This is the case worth having: today it surfaces at
      7b as a write that did not go where anyone expected, and `prove_unchanged.py` catches only
      the executable-code half of it.
- [ ] **Derive the galley census from the edits instead of re-running it.**
      MEASURED 2026-08-18 on a controlled cycle -- a docstring grown, a comment
      shrunk, an empty interval filled: **88 of 89 blocks derive exactly** from
      the original census plus the splice's own line deltas. `splice` already
      applies edits in descending order, so it holds every number needed.

      ! **The single miss is the `add`,** and it is the one edit that is not a
      range replacement: an empty interval has no lines to replace, so the delta
      is not `new - old`, and the block changes KIND from `interval` to
      `comment`. Derived `(9, 11)`, real `(9, 9)`. The splice knows it inserted
      one line of prose there; nothing carries that out.

      !! **THE CASE IS CORRECTNESS, NOT COST, and the file should not pretend
      otherwise.** A census run is a subprocess: 1,215 ms over 13 files, 224 ms
      over one, so three extra runs cost seconds and three tool calls -- not
      prompt budget. What they cost is a chance to read the WRONG one. Four
      artifacts existed in the 0.2.3 cycle (`census`, `pinned-census`,
      `galley-census`, `galley6-census`) and stage 8 would make five.

      ! Verify: a derived census and a re-run one agree on every block including
      an `add`, and the cycle keeps ONE census on disk.

## Related

- [`the-author-approves-blocks-and-never-sees-the-page`](the-author-approves-blocks-and-never-sees-the-page.md)
  -- the same gap read from the author's side.
