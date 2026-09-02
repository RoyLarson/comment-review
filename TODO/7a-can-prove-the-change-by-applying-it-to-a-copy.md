# 7a can PROVE the change by applying it to a copy and diffing

```
Status:   in-progress
Progress: 3 of 7 tasks closed
Owner:    agents
Requires-Roy: true
Raised:   2026-08-17, while ruling on what CLAIM and CHANGE each carry
TRIAGED:  2026-08-23 — re-verified in place. THREE of five are done: the galley tree
          (`--out`, galley.py:345), the descending splice, and the splice-failure
          question, which the code and SKILL.md now answer in full. TWO remain and they
          are different in kind: T3 is a RULING owed by Roy, T5 is buildable work.
Split:    2026-08-23 -- the derive-the-census box held three jobs (the derivation, the
          `add` that does not derive, and cutting the cycle to one census) and is now
          three; every measurement it carried moved into the Objective
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

! **MEASURED 2026-08-23: 7a still presents the block, not the diff.** `SKILL.md:996-1005`
instructs the task agent to show five parts (`VERDICT / PARAGRAPH / CLAIM / REASON / CHANGE`)
with replacement text inline, and says nothing about a diff. The galley exists and is set at 5b
and 6 (`SKILL.md:918-921`); nothing routes it to the author.

## Why the diff is worth more than the block

A `CHANGE` block is checked for existence and nothing else -- `payload_problem` says so in as
many words, because no checker can judge whether prose is good. A diff is checkable by the
author at a glance, and it answers three questions the block cannot:

| question | the block | the diff |
| --- | --- | --- |
| does it land where the `PARAGRAPH` says | no | yes -- the hunk header names the line |
| did the indentation and comment marker survive | no | yes |
| did an adjacent paragraph get clipped | no | yes -- the hunk shows its neighbours |

! The third is the one that motivated this. `CHANGE` carries *the surrounding paragraph*, so two
findings on adjacent paragraphs each carry overlapping context, and splicing both is where a line
gets eaten. Today that is discovered at 7b, after approval.

! **Roy's rule that *what you show IS what gets written* argues for the diff being primary**: it
is the closer of the two to what lands. ! The ruling finishes the day Roy answers, and until then
`SKILL.md:996-1005` stands as written.

## ! It is NOT a reviewer, and must not become one

The name in Roy's note is *"the reviewer at 7a"*, but stage 8 is the proofreader and this is
not a second one. This renders; it does not rule. ! A stage that both produces the diff and
judges it would be MARK and APPLY in one actor, which is the thing the pipeline separates.

## What the splice already refuses -- the record, moved out of the boxes

MEASURED 2026-08-23: `galley.py` names every refusal rather than guessing, at seven sites --
`galley.py:367` (`--out` overlaps `--repo`), `:389` (`CANNOT USE`, a census carrying no
addresses), `:404` (an address no paragraph in the census holds), `:421` (a write outside
`--out`), `:432` (a read failure, by exception type), `:438` (no language record), `:448`
(anchors moved since the census), `:458` (edits that could not be placed). `SKILL.md:935-944`
states the rule -- *"REFUSES rather than guesses"* -- tells the reader to read the program's
output rather than a list in the prose, and records that `CANNOT USE` exits **2** because
nothing was wrong with the proposal.

! **The splice-failure question was filed 2026-08-17** as *"say what happens when the splice
FAILS"*, when the failure surfaced at 7b as a write that did not go where anyone expected. It now
surfaces at galley time, and `SKILL.md:935-944` separates `CANNOT USE` (exit 2, the census is too
old) from `REFUSED` (the proposal).

## The galley tree and the splice, as they were built

! **The name is the publishing one**: a GALLEY is the trial impression, set but not yet made into
pages, produced so it can be corrected before anything is committed. `proof` was unavailable --
`prove_unchanged.py` already owns it for the CODE CHECK. The run directory already holds the
census; a galley tree mirroring only the files an edit touches is the smallest thing that works,
and it is discarded with the run.

! **`galley.splice` applies every edit in DESCENDING line order**, which is what makes the census
ranges mean anything: a replacement rarely has the line count of what it replaces, so a top-down
splice shifts every range below the one just written. Overlapping edits and stale ranges are
refused before anything is written. `git diff --no-index <original> <galley>` is then the
author's view, and is still to be wired into 7a -- see T3.

!! **It was built for the re-review blocker and this task at once**, because both needed the same
thing: the proposed state rendered as real files. See
[`re-review-is-ordered-everywhere-and-defined-nowhere`](completed/re-review-is-ordered-everywhere-and-defined-nowhere.md).

## Deriving the galley census -- what was measured

MEASURED 2026-08-18 on a controlled cycle -- a docstring grown, a comment shrunk, an empty
interval filled: **88 of 89 paragraphs derive exactly** from the original census plus the
splice's own line deltas. `splice` already applies edits in descending order, so it holds every
number needed.

! **The single miss is the `add`,** and it is the one edit that is not a range replacement: an
empty interval has no lines to replace, so the delta is not `new - old`, and the paragraph
changes KIND from `interval` to `comment`. Derived `(9, 11)`, real `(9, 9)`. The splice knows it
inserted one line of prose there; nothing carries that out.

!! **THE CASE IS CORRECTNESS, NOT COST, and the file should not pretend otherwise.** A census run
is a subprocess: 1,215 ms over 13 files, 224 ms over one, so three extra runs cost seconds and
three tool calls -- not prompt budget. What they cost is a chance to read the WRONG one. Four
artifacts existed in the 0.2.3 cycle (`census`, `pinned-census`, `galley-census`,
`galley6-census`) and stage 8 would make five. ! MEASURED 2026-08-23: `SKILL.md` now names two,
`census.json` and `galley-census.json` (`SKILL.md:918-921, 929`) -- fewer than when this was
filed, and still two.

## Tasks

- [x] T1 | FINISHED | unknown | T1 -- DONE 2026-08-17. `scripts/galley.py --out
      DIR` decides where the copy lives, and the caller names it. VERIFIED
      2026-08-23: `galley.py:345`, `--out` required.
- [x] T2 | FINISHED | unknown | T2 -- DONE 2026-08-17. `galley.splice` applies
      every edit in DESCENDING line order and refuses overlapping edits and
      stale ranges. The reasoning is in the Objective.
- [?] T3 | T3 -- * Rule whether 7a shows the diff INSTEAD OF or ALONGSIDE the
      block. Verify: `SKILL.md`'s stage 7a section names which, and
      `docs/decision-log.md` records it.
- [x] T4 | FINISHED | unknown | T4 -- DONE. The splice-failure case is answered
      in the program and in the prose -- eight named refusals in `galley.py`,
      and `SKILL.md:935-944`.
- [ ] T5 | T5 -- Derive the galley census from the splice's line deltas instead
      of re-running `census.py`. Verify: derived and re-run agree on every
      range-replacement paragraph.
- [ ] T6 | T6 -- Carry the `add` insertion out of the splice so an empty
      interval derives too. Verify: a derived census gives `(9, 9)` not `(9,
      11)`, with kind `comment`.
- [ ] T7 | T7 -- Cut the cycle to ONE census on disk. Verify: `SKILL.md` names
      one census artifact, not both `census.json` and `galley-census.json`.
## Related

- [`the-author-approves-blocks-and-never-sees-the-page`](the-author-approves-blocks-and-never-sees-the-page.md)
  -- the same gap read from the author's side.
