# The measurement harness leaks into the shipped rules

```
Status:   open
Progress: 1 of 6 tasks done
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

- [ ] Sweep the shipped tree for other harness assumptions. Candidates to grep: `corpora`,
      `eval`, `hazard`, `D1`–`D12`, `redacted_pkg`, `workout`, `grade`, `probe`, `base ref`,
      `REDACTED_SHA_A`, `--base`, and any measurement quoted as a rule rather than as evidence.
      **Done when every shipped statement is true in a fresh checkout of an unrelated repo.**

- [ ] Check the direction of every MEASURED claim in `plugins/`. The rules cite measurements
      constantly and that is the house style — but a measurement taken on `redacted_corpus`
      is evidence FOR a rule, not the rule's justification to a stranger. Where a site reads
      *"because X was measured here"*, the rule needs a reason that holds in a repo the reader
      owns.

- [ ] Decide what a shipped rule may assume about its environment, and write it once. Today
      nothing states the floor — whether a git repo exists, whether it is a worktree, whether
      `--base` resolves, whether the cwd is the repo root. Several rules quietly assume answers.

- [ ] Add the check to `docs/limitations.md`'s three questions. It asks "Would it fire in a repo
      about something else?" — which catches a rule fitted to a project, but not a REASON fitted
      to a harness. A fourth question would: *is the reason true in a fresh checkout?*
