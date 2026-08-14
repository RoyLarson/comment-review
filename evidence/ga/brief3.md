# GA generation 3 — the final round

`brief.md` still defines the task, the six base files at `REDACTED_SHA_H`, the hard
limits (**< 300 lines, no line > 104 chars, generic Python**), and the ban on
reading the answer key. **Read it first.** This file says what two generations
measured and what this one has to beat.

## The finding that decides this generation

Sixteen candidates, plotted by how much they report:

```
 1d  221 findings -> recall 0.828  prec 0.783  F2 0.818
 1i  261 findings -> recall 0.880  prec 0.705  F2 0.839   <- CHAMPION, on the knee
 1e  273 findings -> recall 0.876  prec 0.670  F2 0.825
 1j  279 findings -> recall 0.880  prec 0.659  F2 0.825
 2c  310 findings -> recall 0.885  prec 0.597  F2 0.807
 2a  361 findings -> recall 0.890  prec 0.515  F2 0.777
 2f  364 findings -> recall 0.895  prec 0.514  F2 0.779
```

**Recall saturates.** Going 261 -> 364 findings costs 103 extra findings and
buys **+0.015 recall**. Every generation-2 child scored below its own best
parent, because crossover transmitted each parent's reasons to FLAG and none of
their reasons to STOP. 2h is the worked example: it correctly adopted 1d's
acquittal vocabulary — the exact mechanism behind 1d's 0.783 precision — and
then reported 76 MORE findings than 1d did. It kept the words and dropped the
restraint.

The clearest measurement of it: **1d and 2a swept the same 419 blocks with the
same closed acquittal list.** 1d acquitted **198 (47%)** and reported 221. 2a
acquitted **58 (14%)** and reported 361. Same mechanism, same words, a 33-point
difference in the only number that mattered — and 2a scored 0.777 against 1d's
0.818. **The acquittal RATE is the trait; the acquittal LIST is just vocabulary.**

**So: volume is not the lever, and it has been thoroughly explored.** A child
that reports 350 blocks will score ~0.78 no matter how good its prose is.

## Your target

Beat **F2 0.8387** (1i). There is exactly one way left to do it:

> Report roughly **240–280 findings** and get **recall above 0.88** — i.e.
> choose BETTER, not MORE.

Treat ~260 as a budget you are spending, not a floor. For every block you raise,
you are choosing it over another you did not. The union of all 16 candidates
covers 96.7% of the target set, so almost every block IS findable — the ones
your predecessors missed were missed by choice, not blindness.

⚠ The 7 blocks that no candidate has ever found are **noise in the scoring
set**: a runnable usage line, and two well-argued rationale paragraphs a later
pass merely compressed. A reviewer was RIGHT to leave them. Do not contort the
skill to catch them.

## What is settled — do not re-litigate, do not re-argue in the file

- A **mechanical census before judgement**. All ten of generation 1 invented
  this independently, including the control. Spend no lines defending it.
- The **four angles** (Currency ~45% and Functionality ~30% of yield, then
  Locality, Module coherence). Merging them measurably lost recall (1c, rank 9).
- **Reachability folded into Functionality**, not a fifth angle. **Provenance
  not adopted** — probes showed it would revert correct fixes.
- Scope with `git merge-base`. Corpus excludes `.md`/`.txt` and never harvests
  string constants from tests. `TODO/FIXME/HACK/XXX/BUG` are free.
- A docstring carrying a date, ruling, quotation or rationale paragraph is a
  finding **at any length** — a FORMAT failure, not a length one.
- A fifth verdict **`correct`**, for a block that must be fixed rather than cut.

Your lines are better spent on **which blocks are worth a reviewer's attention**
than on restating any of the above.

## Parents

Your prompt names three, drawn from all 19 skills (generation 1, generation 2,
and the incumbent committed skill). Read all three plus `docs/skills/`. Where
they disagree, prefer the one whose measured column supports it — and say which
in your report.

## Output — unchanged

`cand_<ID>_SKILL.md` and `cand_<ID>_findings.json` in the shared `ga/`
directory, findings as `[{"file": "...", "line": N}, ...]` in BASE line numbers.

Return ONLY: your ID, line count, longest line, finding count, and — the part
that matters this round — **what you deliberately chose NOT to report, and the
rule you used to decide.**
