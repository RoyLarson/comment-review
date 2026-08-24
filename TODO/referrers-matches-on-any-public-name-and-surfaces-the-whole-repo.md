# `referrers.py` matches on any public name, and surfaced the whole repo

```
Status:   open
Progress: 0 of 6 tasks done
Owner:    backend
Requires-Roy: true
Raised:   2026-08-17 (referrers.py's FIRST real exercise, the redacted_corpus
          builder run on 0.2.0 -- 24 files under review, ~490 files returned)
TRIAGED:  2026-08-23 — 2026-08-23. NOTHING TO RECLASSIFY -- all five boxes are already
          verifiable tasks with their own gates, which is what the rest of this backlog
          is being rewritten towards. Left open as filed. ! Task 5 states the standard
          the others are held to: take the number from a run, not from a prediction,
          because this file exists because the tool first real exercise disagreed with
          how it was expected to behave.
RE-READ:  2026-08-23 -- second triage pass, T labels added and NOTHING ELSE CHANGED. The
          mechanism the Objective describes is unchanged: `tokens_for` is
          referrers.py:36, it still adds the stem, every trailing suffix of the posix
          path and every PUBLIC top-level definition of a `.py` file, and the only guard
          is still the length filter.
SPLIT:    2026-08-23 -- the boxes were cut to two lines each and every one was given the
          Verify clause it had been carrying only as prose. Old T4 held two rules -- a
          sanctioned response AND a recording requirement -- and became T4 and T5, so
          five tasks became six
```

## Objective

**`referrers.py` returned roughly every document in the repo, and the operator hand-picked 28.**
Reported from that run: generic public names -- `run`, `main`, `lift`, `schedule` -- *"pulled in
~490 files, essentially every doc in the repo, so I selected 28 rather than passing its output
through."*

!! **Both 0.2.0 runs hit it independently, on the same day and the same repo.** It is the
tool's normal behaviour, not one unlucky scope:

| run | files under review | returned | handed to reviewers |
| --- | --- | --- | --- |
| builder (`redacted-branch-b`) | 24 | ~490 | 28 |
| todo-tool (`todo-requires-roy`) | 3 | 337 | ~20, via 46 |

! The todo-tool run narrowed in TWO steps (337 -> 46 -> ~20) and only the endpoints were
reported. Neither the rule used at each step nor the files dropped is recoverable.

!! **The hand-selection is the real defect, not the noise.** The tool is stage 3's INBOUND
half, and its output becomes the `REFERENCE ONLY` list in the stage-4 packet. A list narrowed
from 490 to 28 by unrecorded judgement means the reviewers' inputs cannot be reconstructed from
the package, and the next run cannot be compared with this one. A tool whose output must be
hand-filtered has moved the decision out of the tool and into a place nothing records.

## Where it comes from

`tokens_for` (`referrers.py:36`) collects, for each file under review: its stem, its posix path
and every trailing suffix of that path, and **every PUBLIC top-level definition** when the file
is Python. Each token is then grepped across the tree.

The only guard is the last line -- `{t for t in out if len(t) > 2}`. `run`, `main`, `sort` and
`schedule` all clear it, and each is grepped as a bare substring.

! **A length floor cannot fix this and should not be raised.** `sort` is four characters and
`rates` is five; both are real module names in that repo and both are generic English. Length
does not separate a citation from a coincidence.

## !! What must NOT be lost

The same run: `referrers.py` *"surfaced `docs/tests/billing/test_period_wiring.md` and
`docs/tests/billing/test_block_rates_respect_the_tier_grid.md` -- mirror docs for two files
under review, which prior runs never handed the reviewers."*

**That is the tool working, and it is why it exists.** `SKILL.md` names the extracted/mirror
copy as one of the three things `REFERENCE ONLY` is for, and measured that a mirror tree once
held the CORRECT text while the code was backwards. Any narrowing that drops those two files
has made the tool worse than the 490-file version, because the noise was at least filterable
and a missing mirror doc is invisible.

## ! What the boxes carried

! **T1 -- how the threshold is derived.** Compute every token's match count first, then drop the
ones above a threshold -- and derive the threshold from the run (a token matching more than some
fraction of tracked files) rather than hard-coding a number that fits one repo. !! **Never a
stopword list.** `run` is generic in that repo and load-bearing in this one, where the word names
a single invocation of the skill.

! **T2 -- what a citation looks like.** The brief already rules how prose cites: by symbol or
path, in backticks. A `` `run` ``, `run()` or `module.run` match is a reference; the word *run*
in a sentence is not. ! Path tokens keep matching as plain substrings -- a path is already
specific.

! **T3 -- no silent caps.** A tool that quietly narrows reads as "these are all the referrers"
when it is not, so the packet must record the narrowing instead of an operator remembering it.

! **T4 and T5 were ONE box holding two rules.** The rule today is that referrers' output IS the
`REFERENCE ONLY` list; this run shows that can be unusable, and the skill offers no sanctioned
response. ! Whatever it becomes, hand-selection must be RECORDED in the packet -- the current
wording lets a run substitute judgement for the tool with nothing written down.

! **T6 -- the standard the others are held to.** Take the number from a run, not from a
prediction: this whole file exists because the tool's first real exercise disagreed with how it
was expected to behave.

## Tasks

- [ ] T1 -- Drop a token by its MEASURED match count, with the threshold derived from the
      run, not hard-coded. Verify: a token matching several hundred files is dropped.
- [ ] T2 -- Require a bare NAME token to match as a CITATION -- `` `run` ``, `run()` or
      `module.run`, not the word in a sentence. Verify: a prose `run` no longer matches.
- [ ] T3 -- Print what was dropped and why -- one line per dropped token with its count.
      Verify: the packet records the narrowing; no token is dropped silently.
- [ ] T4 -- Say in `SKILL.md` what to do when referrers' output is too large to hand over
      as-is. Verify: `SKILL.md` names a sanctioned response; today it offers none.
- [ ] T5 -- Require hand-selection of the referrers list to be RECORDED in the stage-4
      packet. Verify: `SKILL.md` says so, and the packet has a place for it.
- [ ] T6 -- Re-run referrers against the same 24 files and compare. Verify: the two mirror
      docs still appear and the returned count is workable, taken from the run.
## Related

- [`ownership-is-read-first`](ownership-is-read-first-but-nothing-makes-it-so.md) -- carries the
  four editorial roles written out as editorial desks. `referrers.py` is the INDEX in that
  mapping, and T1 above is the indexer's own rule: **an index whose entries point at
  every page is not an index**, so a term is dropped by how many pages it lands on. The rule was
  written here first and the desk agrees with it; nothing in that mapping is evidence for the
  threshold, which still has to come from a run.
- [`reference-only-misses-the-documentation`](reference-only-misses-the-documentation.md) -- the
  gap `referrers.py` was built to close. ! This file is the cost of closing it.
- [`the-two-lists-were-tuned-to-one-diff`](the-two-lists-were-tuned-to-one-diff.md) -- the same
  two lists, tuned rather than derived.
- [`a-prose-file-has-no-blocks`](a-prose-file-has-no-blocks.md) -- why the `.md` files it finds
  can be handed to reviewers as REFERENCE ONLY but never censused.
