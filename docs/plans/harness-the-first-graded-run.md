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

- [x] **A1 -- ANSWERED 2026-08-23 by `e31b438`: no second suite. `evals/evals.json` grew the
      fields.** Works `the-harness-cannot-run-the-system-it-grades`. The 2026-08-23 ruling chose
      A SECOND SUITE because `(address, hash, files)` had nowhere to put the hash. **Case 3 put
      it there** -- `start` and `end` beside `prompt`, `hazards` and `evidence` -- so the premise
      is gone and the shipped file holds a hash-pinned case today. ! The ruling is superseded by
      what landed, not by an argument. The question as it was put:

      **Re-decide the suite layout against `skill-creator`'s actual shape.** `skill-creator`
      prescribes `evals/evals.json` plus a sibling `<skill-name>-workspace/`, and `files` is a
      list of PATHS -- so a pre-step can materialise a hash into paths and the hash lives in our
      own sidecar. Both models can now hold.

- [x] **A2 -- SETTLED 2026-08-29 BY MEASUREMENT: the field is `expectations`, and `assertions` is
      read by nothing.** Works `the-harness-cannot-run-the-system-it-grades`. The docs looked like
      they disagreed; they do not. **The split is prose versus schema, not input versus output.**
      Measured over the marketplace copy of `skill-creator`:

      | name | where it is READ | by |
      | --- | --- | --- |
      | `expectations` | `grading.json` | `scripts/aggregate_benchmark.py:157`, again at `:161` and `:252` |
      | `expectations` | `evals.json` -- `evals[].expectations` | `references/schemas.md:20`, `:35` |
      | `expectations` | handed to and emitted by the grader | `agents/grader.md:15`, `:112`, `:188` |
      | `expectations` | the comparator's input | `agents/comparator.md:18` |
      | `assertions` | **nothing** | -- |

      !! **`assertions` SURVIVES ONLY IN SKILL.md's PROSE** -- nine sites, `:145` to `:463` -- plus
      ONE JSON snippet at `SKILL.md:195` showing `"assertions": []` inside `eval_metadata.json`.
      ! **And that file is read for one key.** `aggregate_benchmark.py:87-91` opens
      `eval_metadata.json` and takes `eval_id` from it, falling back to the directory name; it
      never looks at `assertions`. **So a case that spelled the field `assertions` would be
      accepted, graded against nothing, and report zero expectations -- silently.**

      ! **THE EXISTING TASK IS CORRECTED, NOT CONFIRMED.** *"Add `assertions` to
      `evals/evals.json`"* named a key no tool reads. The key is `expectations`, and `evals.json`
      itself was removed 2026-08-23 -- so it lands on whatever B4 hands `skill-creator`, not on a
      file in this tree.

      ! **OUR OWN `expected`/`observed`/`outcome` ARE NOT THIS FIELD AND DO NOT MOVE.** All six
      `evals/test-cases.jsonl` rows carry them; they describe the KNOWN DEFECT a case is built
      from, which is the answer key. `expectations` is the list a grader rules on. ! The same
      survey re-confirms **T15**: every one of the six pins a single `commit`, so no row carries
      the `start`/`end` pair A3 settled.

- [x] **A3 -- DONE 2026-08-23 by `e31b438`, and the shape is `start`/`end`.** Works
      `the-harness-cannot-run-the-system-it-grades`. Case 3 `rename-left-history-in-the-comments`
      carries `start: ff1cab5`, `end: ba5eb32` -- **a nine-commit range**, which is the ruling
      demonstrating itself: one review takes several commits, so a single fix hash could not name
      it. `evals.json`'s own `notes` states the rule.

      ! **The keys were `base`/`fixed` and are now `start`/`end`** (`decision-log.md Vocabulary:
      #10`). `base` already meant two other things here -- the unmodified text of a planted hazard
      in `grade_hazards.py`, and a merge-base in `prove_unchanged.py --base`. Roy, 2026-08-23:
      *"I knew that this collision could happen while writing that case but it needed to be
      written."* ! Nothing reads these keys programmatically yet, so the rename cost nothing --
      **which is exactly why it had to happen before something did.**

### B -- Build the four mechanics

- [x] **B1 -- BUILT 2026-08-29: `evals/snapshot_plugin.py`, six tests in
      `tests/harness/test_snapshot_plugin.py`.**
      Works `the-harness-cannot-run-the-system-it-grades` and `isolate-the-codes-contribution`.
      ! **Proving it is the box, not doing it** -- a run that silently used the installed skill
      scores the wrong tree. Verify: the run records the snapshot path and the ref it came from,
      and a deliberate mismatch is detectable. **Both halves hold:**

      | what | how it is answered |
      | --- | --- |
      | the ref it came from | `Manifest.ref`, and `Manifest.commit` beside it |
      | the snapshot path | `Manifest.root`, stored ABSOLUTE by `write_manifest` |
      | it outlives the run | `snapshot.json`; `read_manifest` round-trips and `verify` works off the reloaded copy |
      | a mismatch | `verify` returns the PATHS, not a boolean |

      !! **THE ANNOTATED-TAG TRAP IS A TEST, NOT A NOTE.** `git rev-parse v0.2.3` returns
      `6acb9e1`, the TAG OBJECT; the commit is `3e1fedf`. `resolve` peels with `^{commit}`, and
      the test asserts against both values so the peeling cannot be dropped silently.

      !! **THREE MISMATCH KINDS, AND ONE OF THEM NEEDS THE SECOND WALK.** A file CHANGED or GONE
      is caught by walking the manifest; a file ADDED is invisible to that walk, because every
      recorded path still matches. ! The added-file test was written first and **observed
      failing** -- `verify` returned `[]` -- which is what says the directory walk is load-bearing
      rather than decorative.

      !! **IT READS THE OBJECT STORE, NOT A WORKTREE, AND THAT IS A CHANGE FROM THIS BOX'S OWN
      SKETCH.** The box said `cp -r` out of a `git worktree`. `git archive` writes the blobs as
      git stores them; **a checkout on this machine applies `core.autocrlf` and hands back CRLF**,
      while B2 verifies a staged file against `git show`, which is the stored blob. Taking both
      from the object store is what lets B2's byte comparison agree -- through a worktree it would
      fail on every text file, on line endings alone. ! It also removes a worktree lifecycle, so
      there is no cleanup step that can leave a stale one behind.

      ! **NO CLI YET, DELIBERATELY.** Nothing calls this from a shell until B3 needs to hand a
      subagent the path, and an interface written before its caller is guessed at.

      ! **ONE DEFECT FOUND AND FIXED IN PASSING**, by the suite rather than by review:
      `tests/harness/` without an `__init__.py` makes pytest import its `conftest.py` under the
      bare name `conftest`, which `tests/conftest.py` already holds -- **15 collection errors**,
      every one an ImportError in a module doing `from conftest import ...`. `tests/gates/`
      carries the same file for the same reason, and now says so.

      !! **THE PROOF REQUIREMENT IS NOT HYPOTHETICAL -- IT HAS ALREADY HAPPENED.** Works
      `marketplace-resolves-live`. A directory marketplace POINTS, it does not copy: re-verified
      2026-08-23, `known_marketplaces.json` has `roy-local` as `source: directory` with both
      `path` and `installLocation` set to `C:\Users\Roy\projects\comment-review` -- **the working
      tree**, which is the shared checkout another session commits to. Roy caught it 2026-08-22
      when the installed plugin traced back to the commit just finished instead of `v0.2.3`, and
      the `d` records gave it away because no cue had a `d` before that branch. **So a run
      believed pinned to a tag was against whatever the tree held at run time.**

      ! **The harness sidesteps it by construction and must not rely on that quietly.** A
      snapshot handed to a subagent as a path never consults the marketplace, so the failure
      cannot recur here -- but B1's *"a deliberate mismatch is detectable"* is exactly the check
      that would have caught it, and it is the box for that reason.

      !! **SNAPSHOT THE WHOLE PLUGIN, NOT JUST `skills/comment-review/`.**
      `isolate-the-codes-contribution` needs arm A to be *"v0.2.3 code with v0.2.3 agents exactly
      as tagged"* -- so the SCRIPTS and the AGENTS have to travel together at one ref, or the two
      things the split exists to separate get mixed at the point of capture. ! And the tags here
      are ANNOTATED: `v0.2.3^{}` for the commit, which that TODO calls *"the trap anyone
      re-deriving which code produced a measurement hits first"*, and which this session hit.

- [ ] **B2 -- STAGE: materialise START into the directory to be graded.** Works
      `the-harness-cannot-run-the-system-it-grades`. Check the START hash out, copy the case's
      paths into the eval workspace, leave everything else behind. Verify: the staged tree matches
      `git show START:<path>` byte for byte for every path in the case.

- [ ] **B3 -- RUN: with-skill and baseline in the SAME turn.** Works
      `the-harness-cannot-run-the-system-it-grades`. SKILL.md is explicit that the baseline is not
      collected afterwards. ! The baseline here is the OLD AGENT WORKFLOW on the NEW machinery
      (`decision-log.md Process: #52`), not "no skill" -- this is an improve-mode comparison, not a
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

      !! **ONE OF THOSE FIVE GATES CANNOT CURRENTLY FAIL, and the plan must say so rather than
      lean on it.** `evidence-still-names-places-by-line` task 1: `_resolve_lines` accepts an
      unbounded range and `source_problem` windows the WHOLE range, so `file:1-868` reduces the
      verbatim check to *"this string occurs somewhere in this file"* -- **a fabricated citation
      to a real file passes today.** ! Until that is fixed, "every citation resolves" is a green
      gate that shares the defect, and C1 must either record it as a KNOWN-WEAK gate or drop it
      from the VOID set. **The fix itself is shipped-tree work and belongs to 0.2.4, not here.**

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

! **CASE 3 IS THE TEMPLATE, AND D1 IS THE SECOND ONE.** `rename-left-history-in-the-comments`
already runs this shape end to end in `evals/evals.json` -- a `start`, an `end`, four paths, three
hazards and an `evidence` package. D1 is not inventing a form; it is filling in one that exists.

- [ ] **D1 -- The 2026-08-16 hand pass: START `3ce610c`, END `8c0cef6`.** Works
      `the-harness-cannot-run-the-system-it-grades` and
      `the-shipped-python-does-not-pass-its-own-review`. Six factual defects verified present at
      START with line numbers, the strongest created BY the START commit -- it moved `READ_ERRORS`
      to `repo.py` and left `run_context.py:87` citing `census.py`. ! **Assert the six, not the
      negative-prose percentage**: register is not in any role's remit, and the six are
      `block-context`'s by definition. Verify: the run is graded from the DIFF, never from its own
      report.

- [ ] **D2 -- Record what the first run actually returned, whatever it was.** Works
      `the-harness-cannot-run-the-system-it-grades` and `marketplace-resolves-live`. ! A first
      number that is bad is the point of having one. Verify: the result lands in `evidence/`,
      names the snapshot ref, the START/END pair and the grader model, and says which of the six
      were caught.

      !! **A COMMIT, NEVER A VERSION NUMBER.** `marketplace-resolves-live` task 5 asks for every
      existing measurement that names a version to be re-checked, *"because the tag did not fix
      that"*. **This plan's job is to not add another one.** ! A version names a tree only if the
      install copies, and this machine's does not -- so a result recorded as *"v0.2.3"* names
      nothing. Its own summary of the failure is the standard to hold to: *"a pin that pins
      nothing and reports as a pin is findings.md section 33"* -- the green gate that shares the
      defect.

### E -- The rate nothing measures

!! **`a-role-can-reverse-itself-between-runs` has been waiting for an instrument, and this is
it.** Raised 2026-08-17, when one role returned opposite verdicts on the same block across two
runs: *"it means the verdict is a SAMPLE, and nothing anywhere states its variance."* Its first
task says *"establish the rate before designing anything"*, and its own caveat is *"two runs give
a number with no error bar."* **`--runs-per-query` defaults to 3 and `aggregate_benchmark` reports
mean +/- stddev** -- the error bar is a default of the instrument, not new work.

- [ ] **E1 -- Measure the reversal RATE, with an error bar.** Works
      `a-role-can-reverse-itself-between-runs` (its task 1). One role, one unchanged census,
      repeated runs, verdicts diffed per paragraph. ! That TODO asks for the COST to be stated
      before starting; run count, tokens and time all come out of `benchmark.json`, so state them
      from the first run rather than estimating. Verify: a rate with a stddev and the run count it
      came from, recorded in `evidence/`.

- [ ] **E2 -- Separate variance from CHANGE SENSITIVITY using the pinned snapshot.** Works
      `a-role-can-reverse-itself-between-runs` (its task 2). That file names the competing
      explanation itself: the second run *"ran against a CHANGED skill"*, so a role told different
      things may reasonably answer differently. **B1's snapshot is exactly that control.** Verify:
      the reversal either reproduces at a fixed skill ref -- variance -- or does not, making this
      change sensitivity, *"a different and more tractable problem"*, and the file says which.

- [ ] **E3 -- Replace the UNMEASURED sentence with the measurement.** Works
      `a-role-can-reverse-itself-between-runs` (its task 5). It asks `docs/limitations.md` to say
      verdict stability across runs is unmeasured -- *"the honest state today"*. E1 makes that
      sentence false. Verify: `docs/limitations.md` carries the measured rate and its conditions,
      or still says UNMEASURED because E1 did not run.

! **This plan does not close that TODO outright, and must not claim to.** It works its tasks 1, 2
and 5, and it UNBLOCKS the two judgements that were waiting on a number -- task 3 (`*` Roy's:
what a measured rate OBLIGES, *"because it decides whether a verdict is a claim or a vote"*) and
task 4 (whether `correct` reversing to `query` is worse than the reverse). ! Task 6 is a standing
prohibition -- **do not add a `confidence` field in response to any of this** -- and no
measurement retires it.

!! **AND THE GRADER INHERITS THE WHOLE PROBLEM.** A grader is a role, so all of the above applies
to it: an A-F letter that moves between runs states less than the letter claims. C3 calibrates it
against a known answer; E1's method is what measures its spread.

## Not in scope

- **`findings.md` Parts I-III.** The commits exist (42 across 2026-08-11 in `redacted_corpus`)
  but no clean repo-level pair does -- `aba2b42a..99f71bde` holds 203 commits against the ~37 the
  burn-down was. Stays on the job board.
- **The Part IV case** (`7850bbc..1a0d41f`). Ready to write and deliberately second: it is 198
  files, and the first case should be one this plan can finish.
- **Promoting `check_citations.py`** anywhere. It is an input that found two real things; where it
  lives is a separate decision.
- **Anything under `plugins/`.** That is 0.2.4's, and this plan must not touch it -- a version
  changes the AGENTS or the MACHINERY, never both (`decision-log.md Process: #51`).

- **`evidence-still-names-places-by-line`, except as a DEPENDENCY.** Eight of its nine tasks are
  shipped-tree addressing work -- `SOURCES` in line form, code concerns carrying no place at all,
  stage 8 with no citation form, stage 6 naming blocks by nothing, two agent files instructing a
  refused `move` destination, `census.py` writing the line form into the census, and
  `residue-check.md` keying by `file:start-end`. **All of it is under `plugins/` and belongs to
  0.2.4.** ! Only its **task 1** touches this plan, and only as a precondition C1 names: the
  citation gate cannot fail while a fabricated citation to a real file passes.

  ! **Its two `*` rulings are not this plan's to ask for** -- what `address:lines` does with a
  code RANGE, and what bounds a FREEFORM source. A case asserting at MARK level does not reach
  either, which is one more reason the first case stops at the record file.

- **`held-runs-need-a-one-off-migration`, and this plan makes the case for it WEAKER.** It is
  already `blocked`/deferred -- Roy, 2026-08-19: *"a one-off script thing and not worth doing
  right now"* -- and its own note says nothing depends on it. ! The harness produces NEW runs in
  the current format, so it never reads a held 0.2.x report; and `isolate-the-codes-contribution`
  already records that the held runs cannot serve as a baseline anyway, because
  `evidence/cycle-0.2.3/` is *"a MECHANICAL run ... and carries no hazard grade"*. **Both arms
  have to be run fresh regardless.** It stays deferred, waiting on someone needing a specific
  held run replayed.

- **FIXING `marketplace-resolves-live`, or auditing what it invalidated.** Its `*` ruling is
  Roy's -- whether the fix is to the INSTALL (a marketplace that copies, or installing from a tag
  rather than a path), to the DOCS (say plainly that `roy-local` is live and no local measurement
  is pinned), or to both. ! **The harness needs neither answer**, because it never installs; it
  hands a subagent a path. And its task 5 -- re-checking every measurement in `docs/` and
  `evidence/` that names a version rather than a commit -- is an audit of the PAST, where this
  plan's D2 is a rule for the FUTURE. Both are wanted; only one is here.

  ! **It also contradicts `CLAUDE.md`'s release section, which is still uncorrected.** That text
  describes the CACHE half only -- *"the plugin cache keys its directory on that version field"*
  -- and never says a directory-source marketplace resolves live. Correcting it is shipped-doc
  work and belongs with the ruling.

- **RUNNING `isolate-the-codes-contribution`'s two arms.** This plan BUILDS what that measurement
  needs -- B1 snapshots a whole plugin at a tag, B3 runs two arms in one turn -- but its own
  question (*"how much of the improvement is the code, and not the orchestration"*, graded on the
  twelve planted hazards via `grade_hazards.py`) is a second measurement with a different
  instrument. ! **It is UNBLOCKED by this plan, not performed by it.**

  !! **AND ITS CENTRAL CONSTRAINT WAS RULED INDEPENDENTLY THE NEXT DAY.** Raised 2026-08-22, it
  says the rewording is the confound and *"the substitution must be MECHANICAL AND DIFFABLE: a
  dictionary rename only, no new instruction, no restructured stage, no sharpened sentence."*
  That is `decision-log.md Process: #51`'s vocabulary carve-out, stated a day early -- and
  measured true 2026-08-23: the six agent files move 29/29 between `v0.2.3` and HEAD, and that is
  a rename plus exactly one orchestration change (four parallel reviewers becoming three at stage
  4c). ! `check_vocabulary.py` is what says the result speaks the shipped language, and it passes
  today at 59 terms, 0 drifted.
