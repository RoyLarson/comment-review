# GA generation 2 -- breed the winners

Everything in `brief.md` still applies: the same two halves, the same six base
files at `REDACTED_SHA_H`, the same hard limits (**< 300 lines, no line > 104 chars,
any Python generic**), the same ban on reading the answer key.

**Read `brief.md` first.** This file only says what changed.

## What generation 1 established

Ten candidates, all legal, F2 from 0.777 to 0.839. Ranking is now **F2** --
recall weighted 4x precision -- because the goal is "as many of the real changes
as possible in ONE pass".

```
1i 0.8387  recall .880  prec .705  261 findings   census + portable sweep
1e 0.8251  recall .876  prec .670  273            31-class checklist
1j 0.8251  recall .880  prec .660  279            CONTROL: evidence-only edits
1b 0.8205  recall .866  prec .678  267            four angles, sharpened prose
1d 0.8184  recall .828  prec .783  221            named acquittals  <- best F1
```

Three results shape this generation:

1. **All ten independently added a mechanical census/sweep before judgement** --
   including the control, which was told to change only what the evidence
   supports. Sampling, not the angles, was capping recall. This mechanism is
   settled; do not spend lines re-arguing it.
2. **No individual beat 0.881 recall, but the UNION of ten covers 96.7%.** The
   ceiling is complementarity. The 7 blocks nobody found are noise in the
   scoring set (a runnable usage line; two well-argued rationale paragraphs) --
   a reviewer was RIGHT to leave them, so treat ~0.96 as the real ceiling.
3. **Precision and recall are separable.** 1d reported 40 fewer findings than
   1i and won on precision by 0.08, because every block gets either a finding
   **or a named acquittal from a closed list** (`label`, `states-the-signature`,
   `derivation`, `only-guard`, `names-its-expiry`). Silence is a gap in the
   review, not a pass.

## The hypothesis this generation tests

**Census x acquittal.** 1i guarantees every block is SEEN; 1d guarantees every
block is RULED ON with a named reason. They are independent mechanisms and the
metrics say they are complementary. A candidate that carries both should beat
0.84 without paying 1d's recall cost.

You are given three parent SKILL.md files in the shared `ga/` directory. Read
all three, then write one child. Take the parts that the numbers justify -- not
the parts that read best. Where two parents disagree, prefer the one whose
measured column supports it, and say which in your report.

## Other material worth folding in, all measured in generation 1

- A **fifth verdict `correct`** -- a real pass corrected 82 blocks under a
  four-verdict vocabulary with nowhere to file them (1a).
- A docstring carrying a date, ruling, quotation or rationale paragraph is a
  finding **at any length** -- a FORMAT failure, not a length one. The old
  wording let reviewers `keep` every rationale docstring, which is exactly
  where an evicted `#` block relocates (1b).
- The ghost-symbol corpus must exclude `.md`/`.txt`: a doc discussing a deleted
  symbol otherwise vouches for it. Measured to suppress three real obituaries
  (1j). Likewise never harvest string constants from tests -- a negative
  assertion (`assert "x" not in y`) makes a dead name read as alive.
- Scope with `git merge-base`, never `A...B` between two tips.
- Do NOT adopt the refuted recommendations (`Provenance` as a diff-against-
  history angle; `Reachability` as a fifth angle). Probes showed Provenance
  would revert correct fixes; fold reachability into Functionality instead.

## Output -- same as before

`cand_<ID>_SKILL.md` and `cand_<ID>_findings.json` in the shared `ga/`
directory. Your `<ID>` is in your prompt.

Return ONLY: your ID, line count and longest line, finding count, which parent
each major decision came from, and the one thing you took from a LOWER-ranked
parent over the best one -- with the reason.
