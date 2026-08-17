# The measurement harness leaks into the shipped rules

```
Status:   open
Progress: 3 of 6 tasks done
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

- [ ] Check the direction of every MEASURED claim in `plugins/`. ⚠ **The Python half is done
      2026-08-16**, under a ruling of Roy's given on `annotate.py`'s *"Measured on a scientific
      library: 4 hits, 4 false"*: *"Unnecessary and potentially harmful quoting of hits that
      could no longer be true."* Applied across all eight scripts — the MECHANISM stays and the
      quantity goes. Removed: `5 of 8 blocks`, a dated `asanyarray` observation, `5 of 7
      reviewer reports FABRICATED` (Roy, on that one: *"only needs the first line"*), `3 of 3
      verification runs`, `14 en-GB spellings`, `80/84, 18/20 and 2/2 false dangling reports`,
      `6 of 20 dangling reports were gitignored state`, `Measured four times`, `Measured on all
      three runs`.

      ⚠ **STILL OPEN FOR THE MARKDOWN, and it needs a ruling, because the two rules collide.**
      `docs/limitations.md` REQUIRES a number — *"Is the evidence a number or ratio rather than
      a story?"* — and this task says a number measured on one repo is not a justification to a
      stranger. Seven sites are affected: `SKILL.md:222` (*"6, 19 and 8 rotted citations"*),
      `:266` (*"templates measured at 1.3"*), `:270` and `:507` (*"14 en-GB spellings"*, twice),
      `write.md:83` (*"14 dialect changes"*) and `:95` (*"2 of 28 authored docstrings"*), and
      `module-context.md:110` (*"548 blocks"*). ⭐ Roy rules which of the two gives way.

- [ ] Decide what a shipped rule may assume about its environment, and write it once. Today
      nothing states the floor — whether a git repo exists, whether it is a worktree, whether
      `--base` resolves, whether the cwd is the repo root. Several rules quietly assume answers.

- [x] Add the check to `docs/limitations.md`'s three questions. **Done 2026-08-16** — there are
      four now, and the fourth is *"is the REASON true in a fresh checkout?"*, with the failure
      it catches named: a reader who tests the reason, finds it false, and drops the rule.
