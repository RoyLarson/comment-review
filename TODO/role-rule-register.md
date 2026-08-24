# Rule changes proposed for the editorial role files, decided together against a fixed budget

```
Status:   decision-needed
Progress: 0 of 5 tasks done
Owner:    agents
Requires-Roy: true
Raised:   2026-08-18 (Roy, 2026-08-18: keep track of these and have a place to decide on
          them)
Re-measured: 2026-08-23 -- the cost table was measured 2026-08-18 and every row has
          moved; `reviewer-brief.md` is 30,533 bytes against the 22,940 recorded here.
          The file also carried its cost table, its "how an entry earns its place"
          section and its Related list TWICE, and the two copies disagreed: the older
          asked what a candidate REPLACES, which Roy superseded the same day it was
          written. One copy of each is kept.
SPLIT:    2026-08-23 -- each of the four `*` boxes carried the measurement that justifies
          it. The measurements moved into "The four entries" below; the boxes are the
          ruling and how to check it was made. Five boxes stay five.
```

## Objective

**The register of proposed additions and amendments to the four editorial role
files.** Roy, 2026-08-18: *"keep track of these and have a place to specifically
decide on them when we want to review them."*

! **This is where a proposed rule GOES, not where it is decided in passing.** A finding that
implies a role should say something new is filed here and left; the batch is ruled deliberately,
in one sitting, with the others visible.

## !! A RULE PAYS FOR ITS OWN LINES -- IT DOES NOT HAVE TO DISPLACE ONE

Roy, 2026-08-18. There are exactly two currencies, and a candidate needs one. `docs/limitations.md:44`
holds the same rule for the repo at large.

**1. It CATCHES something.** Subjective, and admitted as such -- but what a MISS
costs is not, and it lands twice. A defect a HUMAN finds that this system should
have found is how the tool stops being used, not merely a bad run. And a miss
buys a SECOND and THIRD pass, which racks up tokens fast: one run over two files
and 154 prose blocks measured 870,000 subagent tokens, so a rule that prevents a
single re-run has paid for far more prose than it costs.

**2. It SAVES A SEARCH.** Pure token cost on the FIRST run. A reviewer that
would otherwise scan twenty documents hunting for what a rule could have said
outright is spending the budget on discovery instead of judgement.

! **A rule that answers NEITHER is the one to cut.** That is the test -- not
size, and not a swap. ! The two are not the same question either: a rule can
catch nothing new and still earn its place by making a claim settleable without
opening another file.

! **SUPERSEDED, same day: "what it REPLACES, named" is NOT the test.** An earlier copy of the
section below required every candidate to name a line it displaced, and said an entry that
cannot is not ready to be ruled on. Kept here as the record; the currency test above replaced it.

## What a role costs to load today

MEASURED 2026-08-23 --
`wc -c -l plugins/comment-review/skills/comment-review/references/reviewer-brief.md plugins/comment-review/agents/*.md`.
Every reviewer loads the brief plus its own file, and four run in parallel:

| file | bytes | lines |
| --- | ---: | ---: |
| `reviewer-brief.md` | 30,533 | 477 |
| `comment-review-module-context.md` | 7,986 | 130 |
| `comment-review-function-context.md` | 7,295 | 124 |
| `comment-review-block-context.md` | 7,066 | 117 |
| `comment-review-ownership-context.md` | 6,795 | 111 |
| `comment-review-compact.md` | 1,681 | 30 |
| `comment-review-review.md` | 1,665 | 27 |

! The brief is a FIXED cost paid four times -- **122,132 bytes per run** before a role file is
opened, against the 91,760 measured 2026-08-18. A role file is paid once by its own reviewer.
That asymmetry is why a rule belonging to ONE role must not drift into the brief: there it costs
four times as much for the same work.

## How an entry earns its place

Each candidate should carry three things before it is ruled on:

- **the shape**, in the role's own vocabulary, with the measurement behind it
- **which currency it pays in** -- what it CATCHES, or which search it SAVES
- **what a reviewer DOES with it**: a check runnable without opening another
  file, or it does not go in

## The four entries, and the evidence behind each

**1. `block-context` -- a constraint can be false by ARITHMETIC with no enforcing line.** Its
check is written around finding the line that enforces a bound and comparing value, direction,
units and boundary, so a claim with no code to resolve against cannot be checked at all.
MEASURED 2026-08-23: `comment-review-block-context.md` says nothing about arithmetic -- zero
matches for `arithmetic`. Evidence and siblings in
[`false-by-arithmetic-with-no-enforcing-line`](false-by-arithmetic-with-no-enforcing-line.md).

**2. `module-context` -- what VERDICT a module announcing more than one subject earns.**
MEASURED 2026-08-23: `comment-review-module-context.md:25-29` still lists the three triggers and
names no verdict. At `d3aa065` the role detected the two-subject module, quoted its own trigger,
then emitted a patch WIDENING the docstring to announce both -- the defect the trigger names,
applied as the remedy. The same file already calls a misplaced module constant a CODE CONCERN,
so the pattern exists and was not reached for; the miss is filed as
`module-context-widens-a-two-subject-docstring` in `evals/test-cases.jsonl`.

**3. Every role -- what to do with a paragraph the census marks `doc-kind-unresolved`.** Go and
Ruby attach docs by POSITION, so the census stamps `comment`, annotates the paragraph, and says
it may be governed by FORMAT rather than LENGTH and is not charged to the cap. MEASURED
2026-08-23: the token appears only in `references/compact.md:99` and `:113`, which is stage 6
routing -- no role file says who CONFIRMS the kind or how.

**4. `function-context` and `module-context` -- where they START now the a-series has landed.**
Ordering, never filtering -- Roy, 2026-08-18: they do have to review all `b`s and `c`s but the
focus for them gets a lot easier. ! The dependency is discharged: `cue` emits four series and
`addresser.py --series` accepts `f,a,b,c`, so this is takeable now.

## Related

- [`false-by-arithmetic-with-no-enforcing-line`](false-by-arithmetic-with-no-enforcing-line.md)
  -- the evidence behind the first entry
- [`docstrings-need-their-own-address-series`](docstrings-need-their-own-address-series.md)
  -- the fourth entry waited on that series, which has since landed
- [`doc-is-structural-means-two-things`](doc-is-structural-means-two-things.md)
  -- why `doc-kind-unresolved` exists at all
- [`the-two-lists-were-tuned-to-one-diff`](the-two-lists-were-tuned-to-one-diff.md)
  -- the last time role prose was cut, and what was inside it

## Tasks

- [ ] T1 -- * RULE ON THE `block-context` ENTRY -- a constraint false by ARITHMETIC with
      no enforcing line. Verify: it is in the role file with its currency, or refused.
- [ ] T2 -- * RULE ON THE `module-context` ENTRY -- the VERDICT a module announcing more
      than one subject earns. Verify: the role file names it and the eval case passes.
- [ ] T3 -- * RULE ON THE every-role ENTRY -- what to do with a paragraph marked
      `doc-kind-unresolved`. Verify: it is in the role files or the brief, currency named.
- [ ] T4 -- * RULE where `function-context` and `module-context` START now the a-series
      has landed. Verify: each names its starting series, and says ORDER not filter.
- [ ] T5 -- Record which currency each candidate above pays in -- CATCHES, or the search
      it SAVES. Verify: T1..T4 each carry that line, citing the measured cost table.
