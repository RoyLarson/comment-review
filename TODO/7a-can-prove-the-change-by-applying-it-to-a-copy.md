# 7a can PROVE the change by applying it to a copy and diffing

```
Status:   open
Progress: 2 of 4 tasks done
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
      [`re-review-is-ordered-everywhere-and-defined-nowhere`](re-review-is-ordered-everywhere-and-defined-nowhere.md).

- [ ] Show the diff at 7a INSTEAD OF or ALONGSIDE the block -- decide which. ! Roy's rule that
      *what you show IS what gets written* argues for the diff being primary: it is the closer
      of the two to what lands.

- [ ] Say what happens when the splice FAILS -- a `BLOCK` whose census range no longer matches
      the file, two `CHANGE`s overlapping. ! This is the case worth having: today it surfaces at
      7b as a write that did not go where anyone expected, and `prove_unchanged.py` catches only
      the executable-code half of it.

## Related

- [`the-author-approves-blocks-and-never-sees-the-page`](the-author-approves-blocks-and-never-sees-the-page.md)
  -- the same gap read from the author's side.
