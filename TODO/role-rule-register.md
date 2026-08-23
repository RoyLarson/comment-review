# Rule changes proposed for the editorial role files, decided together against a fixed budget

```
Status:   decision-needed
Progress: 0 of 5 tasks done
Owner:    agents
Requires-Roy: true
Raised:   2026-08-18 (Roy, 2026-08-18: keep track of these and have a place to decide on
          them)
```

## Objective

**The register of proposed additions and amendments to the four editorial role
files.** Roy, 2026-08-18: *"keep track of these and have a place to specifically
decide on them when we want to review them."*

## !! A RULE PAYS FOR ITS OWN LINES -- IT DOES NOT HAVE TO DISPLACE ONE

Roy, 2026-08-18. There are exactly two currencies, and a candidate needs one:

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

## What a role costs to load today

Measured 2026-08-18. Every reviewer loads the brief plus its own file, and four
run in parallel:

| file | bytes | lines |
| --- | ---: | ---: |
| `reviewer-brief.md` | 22,940 | 364 |
| `comment-review-module-context.md` | 8,039 | 130 |
| `comment-review-function-context.md` | 7,238 | 124 |
| `comment-review-block-context.md` | 7,102 | 117 |
| `comment-review-ownership-context.md` | 6,751 | 111 |
| `comment-review-compact.md` | 1,637 | 30 |
| `comment-review-review.md` | 1,661 | 27 |

! The brief is a FIXED cost paid four times -- 91,760 bytes per run before a
role file is opened. A role file is paid once by its own reviewer. That
asymmetry is why a rule belonging to ONE role must not drift into the brief:
there it costs four times as much for the same work.

## How an entry earns its place

Each candidate should carry three things before it is ruled on:

- **the shape**, in the role's own vocabulary, with the measurement behind it
- **which currency it pays in** -- what it CATCHES, or which search it SAVES
- **what a reviewer DOES with it**: a check runnable without opening another
  file, or it does not go in

! **This is where a proposed rule GOES, not where it is decided in passing.** A
finding that implies a role should say something new is filed here and left; the
batch is ruled deliberately, in one sitting, with the others visible.

## Related

- [`false-by-arithmetic-with-no-enforcing-line`](false-by-arithmetic-with-no-enforcing-line.md)
  -- the evidence behind the first entry
- [`docstrings-need-their-own-address-series`](docstrings-need-their-own-address-series.md)
  -- the fourth entry depends on that series landing
- [`doc-is-structural-means-two-things`](doc-is-structural-means-two-things.md)
  -- why `doc-kind-unresolved` exists at all
- [`the-two-lists-were-tuned-to-one-diff`](the-two-lists-were-tuned-to-one-diff.md)
  -- the last time role prose was cut, and what was inside it

## What a role costs to load today

Measured 2026-08-18. Every reviewer loads the brief plus its own file, and four
run in parallel:

| file | bytes | lines |
| --- | ---: | ---: |
| `reviewer-brief.md` | 22,940 | 364 |
| `comment-review-module-context.md` | 8,039 | 130 |
| `comment-review-function-context.md` | 7,238 | 124 |
| `comment-review-block-context.md` | 7,102 | 117 |
| `comment-review-ownership-context.md` | 6,751 | 111 |
| `comment-review-compact.md` | 1,637 | 30 |
| `comment-review-review.md` | 1,661 | 27 |

! The brief is a FIXED cost paid four times -- 91,760 bytes per run before a
role file is opened. A role file is paid once by its own reviewer. That asymmetry
is why a rule belonging to ONE role must not drift into the brief.

## How an entry earns its place

Each candidate below should end up carrying three things before it is ruled on:

- **the shape**, in the role's own vocabulary, with the measurement behind it
- **what it REPLACES**, named -- or the argument that the file is under budget
- **what a reviewer DOES with it**: a check runnable without opening another
  file, or it does not go in

! An entry that cannot name what it displaces is not ready to be ruled on, and
saying so is more use than ruling it in.

## Related

- [`false-by-arithmetic-with-no-enforcing-line`](false-by-arithmetic-with-no-enforcing-line.md)
  -- the evidence behind the first entry
- [`docstrings-need-their-own-address-series`](docstrings-need-their-own-address-series.md)
  -- the fourth entry depends on that series landing
- [`doc-is-structural-means-two-things`](doc-is-structural-means-two-things.md)
  -- why `doc-kind-unresolved` exists at all
- [`the-two-lists-were-tuned-to-one-diff`](the-two-lists-were-tuned-to-one-diff.md)
  -- the last time role prose was cut at budget, and what was inside it

## Tasks

- [ ] block-context: a constraint can be false by ARITHMETIC with no enforcing
      line. Its check is written around finding the line that enforces a bound and
      comparing value, direction, units and boundary -- so a claim with no code to
      resolve against cannot be checked at all. Evidence and siblings in false-by-
      arithmetic-with-no-enforcing-line.
- [ ] module-context: its role file lists three triggers for a module announcing
      more than one subject and never says what VERDICT one earns. Measured at
      d3aa065: it detected the two-subject module, quoted its own trigger, then
      emitted a patch WIDENING the docstring to announce both -- the defect the
      trigger names, applied as the remedy. The same file already says a misplaced
      module constant is a CODE CONCERN, so the pattern exists and was not reached
      for. Filed as the one miss in evals/test-cases.jsonl.
- [ ] every role: what to do with a block the census marks doc-kind-unresolved. Go
      and Ruby attach docs by POSITION, so the census stamps comment, annotates
      the block, and says it may be governed by FORMAT rather than LENGTH and is
      not charged to the cap. No role file says who confirms the kind or how.
- [ ] function-context and module-context: where they START once the a-series
      lands. Ordering, never filtering -- Roy, 2026-08-18: they do have to review
      all bs and cs but the focus for them gets a lot easier. See docstrings-need-
      their-own-address-series.
- [ ] State the BUDGET in this file, measured, and hold every entry to it.
      docs/limitations.md rules that a rule PAYS FOR ITS OWN LINES, in one of
      two currencies: what it CATCHES, or the search it SAVES. Record which
      currency each candidate above pays in, so the batch is decided on value
      rather than on size.
