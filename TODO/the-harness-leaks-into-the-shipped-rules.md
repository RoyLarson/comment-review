# The measurement harness leaks into the shipped rules

```
Status:   open
Progress: 4 of 6 tasks done
Owner:    session
Raised:   2026-08-16 (Roy, on finding `worktree` in the shipped plugin: "that is
          indicating a wrong idea in the workflow requirements")
```

## Objective

**This repo's eval harness is not the user's environment, and the shipped rules had stopped
telling them apart.** Six sites justified taking absolute paths with *"a relative one does not
resolve from a worktree"* — but a worktree is how `evals/grade_hazards.py` isolates a graded
run. A user invoking `/comment-review` in their own checkout is not in one.

⚠ **A right rule with a wrong reason is worse than a right rule with none.** Absolute paths are
correct — a subagent's working directory is not guaranteed to be the dispatcher's — but a reader
who tests *"does a relative path fail here?"* in an ordinary checkout finds it does not, drops
the rule, and only then do subagents break.

The same shape has already been found twice by other routes: `SKILL.md`'s level ladder,
justified by one budget measurement from a 4,000-line module and invented during the Aug-14
port; and `write.md`'s *"this pass cuts, and it can cut a lot"*, which described stage 5's work
from inside stage 7b's file. **If the harness leaked once it is worth sweeping for the rest**,
rather than finding them one at a time when someone happens to look.

## Tasks

- [x] Give the absolute-path rule its real reason. **Done 2026-08-16** — six sites: the four
      agent files (line-neutral, all at budget), `SKILL.md:344`, and `census.py:768`, whose
      *"the review usually runs from a worktree"* was a plain empirical claim true only of our
      eval runs. ⚠ `reviewer-brief.md:198` is deliberately untouched: *"an archive absent from
      every worktree"* is a measurement about one repository in git's ordinary sense — a
      finding, not a requirement.

- [x] **A SECOND leak, found 2026-08-16 and removed.** `function-context.md:45-50` told
      reviewers to *"Run the guard with its EXEMPTIONS OFF, and read its EXCLUSION list"*, on
      two measurements that `evidence/findings.md` files under **"More of my own errors"**
      (§22 at `:613-617`, and the scope-widening no-op at `:670-684`) — a session mis-invoking
      ruff on this repo's own config while doing documentation cleanup. Roy: *"It would only be
      applicable here if there was a method of intentionally bypassing the reviewers and there
      isn't. If the reviewers fail then they get rerun."* Deleted with its two dependants
      (`function-context.md:3`, `SKILL.md:430`); function-context 129 → 122 lines. ⚠ The rule
      the section exists for is untouched: does the guard exist, and would it FAIL if the claim
      were false.

- [x] Sweep the shipped tree for other harness assumptions. **Run 2026-08-16** over the listed
      candidates. ⚠ **The word list found NOTHING.** Every hit was ordinary English (`degrade`,
      `grade a run from its DIFF`, `git-decoding hazard`) or a false positive on a substring.
      `redacted_pkg/billing/rates.py` in `reviewer-brief.md:50` reads like a corpus path and is NOT
      one — no `redacted_pkg` in `corpora.toml`; it is an invented example, which is what the brief
      is required to use. ⚠ **The remaining leaks are not findable by word**, which is the
      finding: they are QUANTITIES, and the next task holds them.

- [x] Check the direction of every MEASURED claim in `plugins/`. ⚠ **The Python half was done
      2026-08-16**, under a ruling of Roy's given on `annotate.py`'s *"Measured on a scientific
      library: 4 hits, 4 false"*: *"Unnecessary and potentially harmful quoting of hits that
      could no longer be true."* Applied across all eight scripts — the MECHANISM stays and the
      quantity goes. Removed: `5 of 8 blocks`, a dated `asanyarray` observation, `5 of 7
      reviewer reports FABRICATED` (Roy, on that one: *"only needs the first line"*), `3 of 3
      verification runs`, `14 en-GB spellings`, `80/84, 18/20 and 2/2 false dangling reports`,
      `6 of 20 dangling reports were gitignored state`, `Measured four times`, `Measured on all
      three runs`.

      ⚠ **THE MARKDOWN HALF, ruled by Roy 2026-08-16.** The two rules never collided; the
      number question in `docs/limitations.md` was being read as licence to paste run
      statistics into instructions. Roy's discriminator: **does the number teach a reviewer to
      CHECK a number, or does it merely report what happened here?**

      | cut, and why | site |
      | --- | --- |
      | *"6, 19 and 8 rotted citations"* — helps no one discriminate | `SKILL.md` |
      | *"14 en-GB spellings"*, twice — the session talking about its own mistakes | `SKILL.md` |
      | *"14 dialect changes"* — same | `write.md` |
      | *"2 of 28 authored docstrings"* — same | `write.md` |
      | *"548 blocks"* — an unidentifiable source; an agent may go looking for that many | `module-context.md` |
      | *"27 of 48 remaining runs"*, *"3 of 3 known inversions"* — not shown to Roy, same shape | `compact.md`, `SKILL.md` |

      ⚠ **`2 of 7 passes` in `module-context.md:51` STAYS.** It is inside an INVENTED example —
      a loudness guarantee — and it teaches that a number in prose is a checkable claim. Roy:
      *"the better answers are in `reviewer-brief.md`"*, where *"The retry budget is 40"* is
      truthy and false if the budget is 100, and *"this is robust"* is not truthy at all.
      `block-context` carries the same shape.

      ⚠ **One FALSE POSITIVE of mine, caught by Roy.** I listed *"templates measured at 1.3"* as
      a statistic and cut it. **1.3 is a STAGE** — `SKILL.md:232`, *"MEASURE the repo's
      documentation formats"* — so it was a cross-reference like *"(1.4)"* and *"see 1.5"* in the
      same file. Restored. ⚠ It read as a quantity to me and would to an agent, so it is now
      bolded as a reference rather than run into the phrase.

- [ ] Decide what a shipped rule may assume about its environment, and write it once. Today
      nothing states the floor — whether a git repo exists, whether it is a worktree, whether
      `--base` resolves, whether the cwd is the repo root. Several rules quietly assume answers.

- [x] Add the check to `docs/limitations.md`'s three questions. **Done 2026-08-16** — there are
      four now, and the fourth is *"is the REASON true in a fresh checkout?"*, with the failure
      it catches named: a reader who tests the reason, finds it false, and drops the rule.
