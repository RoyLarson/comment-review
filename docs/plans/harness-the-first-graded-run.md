# The harness -- the first graded run

**Branch `test-harness-builder`. The scope is ONE case, run end to end, and the four mechanics it
forces us to build.** Roy, 2026-08-23: *"the important piece is actually figuring out HOW to build
the system."*

!! **THIS IS NOT A RELEASE.** Ruled 2026-08-18 and restated since: harness work is not a release
candidate -- nothing here is under `plugins/`, and it accumulates on `test-harness-builder`.
`0.2.4` is shipped-plugin work only. **So this plan carries no version number**, and closing it
ships nothing; it makes one measurement possible that is not possible today.

! **This is a `docs/plans/` plan, not a `docs/superpowers/plans/` one.** A superpowers plan is
written for an engineer with no context -- exact files, TDD steps, a commit per task. This is a
scope of work: what gets built in one run, and what it must be able to answer at the end.

! **A PLAN IS NOT A TODO.** Anything below that does not get done is filed in `TODO/` before this
plan closes, or it is lost. **Every box names the TODO it works**; the TODO names the work, and
the work is in the tree -- so a ticked box is re-derivable by someone who did none of it.

! No progress count here. `scripts/todo_tool.py` manages `TODO/` and not this file, and a
hand-maintained count is exactly the arithmetic that rots. **The boxes are the state.**

## The four unknowns this plan closes

Roy named them as a sequence, and each is a separate problem:

| # | the unknown | where the answer came from |
| --- | --- | --- |
| 1 | how to isolate the skill and run it separate from the current one | `skill-creator` SKILL.md: **snapshot the directory**, hand the subagent a `Skill path:` |
| 2 | how to copy the files we want graded into the directory | `evals[].files`, plus the prescribed `<skill-name>-workspace/iteration-N/eval-<id>/` layout |
| 3 | how to run the skill to do the review | a with-skill subagent and its baseline **spawned in the same turn** |
| 4 | how to run the grader to verify it caught it | `agents/grader.md` -> `grading.json`, then `aggregate_benchmark`, then an analyst pass |

!! **THE INSTRUMENT IS `skill-creator`, AND THE DECISION IS MADE.** Roy, 2026-08-23, on the
alternative: *"the plugin/agent testing system was much more about testing agents working on their
own for corporations and routing things or making decisions. This is supposed to be an isolated
skill that reviews code bases and stays local."* ! `claude plugin eval` stays refused on FIT, not
on availability -- it is still early-access gated, and that stopped being the question.

## The gate

!! **EVERY BOX BELOW TICKED, and the run produces a grade a stranger can re-derive.** Not "the
tests pass" -- 821 pass today and none of them runs the skill. Not "it looks right" -- that is the
judgement this whole system exists to replace.

## Tasks

### A -- Settle what a case IS, before writing one

- [ ] **A1 -- Re-decide the suite layout against `skill-creator`'s actual shape.**
      Works `the-harness-cannot-run-the-system-it-grades`. The 2026-08-23 ruling chose A SECOND
      SUITE because `(address, hash, files)` had nowhere to put the hash. `skill-creator`
      prescribes `evals/evals.json` plus a sibling `<skill-name>-workspace/`, and `files` is a
      list of PATHS -- so a pre-step can materialise a hash into paths and the hash lives in our
      own sidecar. **Both models can now hold.** Verify: the ruling either stands with its premise
      corrected, or is superseded in the same file, beside what it replaced.

- [ ] **A2 -- Settle the field name before any case is written: `assertions` or
      `expectations`.** Works `the-harness-cannot-run-the-system-it-grades`. Anthropic's own docs
      disagree -- `references/schemas.md` shows `expectations` in `evals.json`, SKILL.md calls it
      *"the `assertions` field"*, `eval_metadata.json` uses `assertions`, and `grading.json` needs
      `expectations` with `text`/`passed`/`evidence`. Verify: read `aggregate_benchmark.py` and
      record which name it consumes; the existing task *"Add `assertions` to `evals/evals.json`"*
      is corrected or confirmed by what that file does.

- [ ] **A3 -- Write the START/END fixture down as a shape.** Works
      `the-harness-cannot-run-the-system-it-grades`. A case pins TWO hashes (Roy, 2026-08-23) and
      `evals.json` has one field for files and none for a ref. Verify: one case file expresses
      `(repo, start, end, paths, role)` and a script materialises `files` from it.

### B -- Build the four mechanics

- [ ] **B1 -- ISOLATE: snapshot the skill at a ref and prove the run used the snapshot.**
      Works `the-harness-cannot-run-the-system-it-grades`. `cp -r` the plugin's skill directory
      out of a `git worktree` at the pinned ref, hand the subagent that path. ! **Proving it is
      the box, not doing it** -- a run that silently used the installed skill scores the wrong
      tree. Verify: the run records the snapshot path and the ref it came from, and a deliberate
      mismatch is detectable.

- [ ] **B2 -- STAGE: materialise START into the directory to be graded.** Works
      `the-harness-cannot-run-the-system-it-grades`. Check the START hash out, copy the case's
      paths into the eval workspace, leave everything else behind. Verify: the staged tree matches
      `git show START:<path>` byte for byte for every path in the case.

- [ ] **B3 -- RUN: with-skill and baseline in the SAME turn.** Works
      `the-harness-cannot-run-the-system-it-grades`. SKILL.md is explicit that the baseline is not
      collected afterwards. ! The baseline here is the OLD AGENT WORKFLOW on the NEW machinery
      (`decision-log.md Process: #6`), not "no skill" -- this is an improve-mode comparison, not a
      does-the-skill-help one. Verify: both arms write outputs under the prescribed layout, and
      `timing.json` is captured from each task notification as it arrives.

- [ ] **B4 -- GRADE: run the grader and aggregate.** Works
      `the-harness-cannot-run-the-system-it-grades`. `agents/grader.md` -> `grading.json` with
      exactly `text`/`passed`/`evidence`, then `python -m scripts.aggregate_benchmark`, then the
      analyst pass. Verify: `benchmark.json` reports mean +/- stddev and a delta over the default
      three runs.

### C -- Make the grade mean something

- [ ] **C1 -- Split every result in two: MACHINERY pass-or-void, EDITORIAL A-F.** Works
      `the-harness-cannot-run-the-system-it-grades`. Roy, 2026-08-23: *"what we need to make
      certain we are not measuring is how good the python machinery under all of this."* Verify:
      a case whose census fails the round trip, holds one address on two paragraphs, drops a
      paragraph, fails `record.py --check`, or leaves a citation unresolved reports **VOID** and
      never reaches the grader.

- [ ] **C2 -- Derive the objective half of the rubric from what the role was HANDED.** Works
      `the-harness-cannot-run-the-system-it-grades`. `vocabulary.py --reviewer <role>` already
      emits it. Verify: every must-pass item cites the emitted term it comes from, and
      `check_vocabulary.py` still passes.

- [ ] **C3 -- Calibrate the grader on the END tree.** Works
      `the-harness-cannot-run-the-system-it-grades`. The END prose is the human answer key, so the
      same grader on the same rubric must score it at the top. Verify: the END tree's letter is
      recorded beside the run it calibrates.

- [ ] **C4 -- * RULING: what does CLOSE TO HERE measure?** Works
      `the-harness-cannot-run-the-system-it-grades`. Roy's own: an identity test fails every real
      run, a bare count passes a run that found different things. **Asked because it is genuinely
      his**, not because the state is unreadable. Verify: the rule names the artifact compared,
      the unit, and a threshold anyone can re-derive.

### D -- The first case, end to end

- [ ] **D1 -- The 2026-08-16 hand pass: START `3ce610c`, END `8c0cef6`.** Works
      `the-harness-cannot-run-the-system-it-grades` and
      `the-shipped-python-does-not-pass-its-own-review`. Six factual defects verified present at
      START with line numbers, the strongest created BY the START commit -- it moved `READ_ERRORS`
      to `repo.py` and left `run_context.py:87` citing `census.py`. ! **Assert the six, not the
      negative-prose percentage**: register is not in any role's remit, and the six are
      `block-context`'s by definition. Verify: the run is graded from the DIFF, never from its own
      report.

- [ ] **D2 -- Record what the first run actually returned, whatever it was.** Works
      `the-harness-cannot-run-the-system-it-grades`. ! A first number that is bad is the point of
      having one. Verify: the result lands in `evidence/`, names the snapshot ref, the START/END
      pair and the grader model, and says which of the six were caught.

## Not in scope

- **`findings.md` Parts I-III.** The commits exist (42 across 2026-08-11 in `redacted_corpus`)
  but no clean repo-level pair does -- `aba2b42a..99f71bde` holds 203 commits against the ~37 the
  burn-down was. Stays on the job board.
- **The Part IV case** (`7850bbc..1a0d41f`). Ready to write and deliberately second: it is 198
  files, and the first case should be one this plan can finish.
- **Promoting `check_citations.py`** anywhere. It is an input that found two real things; where it
  lives is a separate decision.
- **Anything under `plugins/`.** That is 0.2.4's, and this plan must not touch it -- a version
  changes the AGENTS or the MACHINERY, never both (`decision-log.md Process: #5`).
