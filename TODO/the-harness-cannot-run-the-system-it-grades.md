# The harness cannot run the system it grades, and the cheap fix is the unsafe one

```
Status:   decision-needed
Progress: 10 of 22 tasks done
Owner:    testing
Requires-Roy: true
Raised:   2026-08-18, after a run whose only question needed one role and cost four
Triaged:  2026-08-23 -- the grader, the twelve hazards and the two `todo-tool` evidence
          packages were REMOVED from the tree: they described a corpus this repo cannot
          publish. Four tasks named files that no longer exist and were re-ruled; the
          fixture inventory below is what a `find` returns today
```

## Objective

**Nothing in this repo runs a case against this repo's own system.** `evals/` holds
`test-cases.jsonl` -- six cases, each a repo URL, a commit, a file list, a role, an outcome, a
stated `expected` and the `observed` run that produced it -- and `generator_split.py`. There is no
runner, no assertion mechanism and no score.

!! **AND THE OLD APPARATUS IS GONE, NOT BROKEN.** `evals/evals.json`, `evals/discriminators.md`
and the hazard grader are absent from the tree as of 2026-08-23, and `git log -- evals/` shows the
grader was never at `scripts/grade_hazards.py` in this branch's history. They were tied to a
corpus this repo cannot ship, so they went with it. **What that costs is the only mechanical
scoring this system had**, and rebuilding it by RESTATEMENT on a public corpus is T22.

The fix is per-role cases: one role, one fixture, one assertion, and an answer known in advance.
Ruled 2026-08-18: a reduced set is supported and `ownership-context` is never dropped, so a case
is a legal run rather than a test-only shape. **What remains is that the prose does not say so**
-- `SKILL.md` stage 4 dispatches four by name and stage 5 is written as a negotiation between
them, so a run of two reads as a run missing two.

## ! The confound is ASYMMETRIC, and only half of it was recorded

`a-role-can-reverse-itself-between-runs.md` records that every measurement here was made by an
operator who knew it was a test, and treats that as a flat loss. Roy, 2026-08-18: an agent
running the skill *as a test it may abandon* **drops the whole review the moment the skill is
even marginally worse than reading the file itself**, where an agent that believes it must
apply the skill pushes through.

So the two confounds pull opposite ways, and they measure different things:

| axis | a test-aware operator | a real one |
| --- | --- | --- |
| GATE COMPLIANCE | flatters -- refusing to reword a record to satisfy a parser is cheap when the refusal is the result being sought | the gate stands between them and finishing, so they route around it |
| SKILL ADOPTION | harsher -- abandons a skill that is not clearly worth its cost | carries on, having asked for the review |

! **A finding that survives a test-aware run is therefore STRONGER on skill quality, not
weaker.** What such a run cannot measure is whether the gates hold for someone who needs to
finish.

## !! WHERE DOES A CASE STOP? -- and the second question dissolves the first

Roy, 2026-08-18: *"How to stop the run at the correct level? Or do we if we have built the
system to take 1 or more subagents?"*

**THE ASSERTION PICKS THE STAGE. There is nothing to stop.** A case's terminus is wherever the
artifact its assertion reads is written, and stage 4 already writes one to disk -- the reviewer's
own record file, checked by `record.py --check`. A case asking *"does `module-context` raise
this as a code concern"* reads that file and needs no synthesis, no galley, no approval and no
write. A case asking *"is the final text correct"* needs 5, 6 and 7b, and grades the diff. Two
kinds of case, two artifacts, no stop mechanism.

! That also decides the fixture question: a MARK-level case never writes to the tree, so it needs
no worktree to throw away -- only somewhere to put the record file.

**AND THE JOIN ALREADY TAKES ANY SET.** `verdicts.py:296` takes `--reviewers` as a
comma-separated list matched against report stems; it does not know the number four.
`coverage_gaps` counts against the declared population and `verdicts.py:645` prints a NOT
ACCOUNTED FOR line. ! Verified 2026-08-23 that the absence of `--reviewers` is ANNOUNCED rather
than assumed: `verdicts.py:514-518` prints *"! --reviewers not given: whether every expected
reviewer reported was NOT checked."* So a one-role run is machinery this repo has -- what
hardcodes four is `SKILL.md`'s stage 4, which dispatches by name, and the skill's arguments
(`cap`, `target`, `style`) carry no role set.

## !! STAGE 5 IS WRITTEN FOR FOUR, AND THE ROLES ARE NOT INTERCHANGEABLE

Roy, 2026-08-18: *"SKILL.md also states that step 5 is expected to negotiate the result between
the agents. If one editorial role ran that can create confusion."*

Correct, and the confusion is specific. Verified 2026-08-23, all three still present:

- **The premise is stated as a fact.** `SKILL.md:813`: *"Four reviewers rule on the same
  paragraph, so you hold several recommendations and must emit one replacement."* An agent
  holding one report reads that and has to decide whether it is missing three.
- **A count is used as an argument.** `SKILL.md:847`: *"Any `correct` outranks every `clean`.
  Three roles finding nothing does not soften one role finding a falsehood."*
- **A precedence names a role that may be absent.** `SKILL.md:843-844`: two placement verdicts
  naming different destinations, and *"`ownership-context`'s destination governs."* That role is
  in every legal set, so the rule always points at somebody -- but the sentence does not say why.
- **The re-review it sends a contradiction to becomes SELF-review.** `drop` against `correct` on
  one sentence is ruled a contradiction and goes back -- to its filers, which at N=1 is the role
  that filed both.

!! **AND THE ROLES ARE NOT A SET, THEY ARE A LATTICE.** `SKILL.md` reads `ownership-context`
FIRST because the other three measure a claim against the code at their own scope, and a
misplaced claim gets measured against the wrong code. So a run without `ownership-context` is not
a smaller run -- it is a run whose remaining verdicts rest on an unchecked assumption. Dropping
`module-context` costs coverage; dropping `ownership-context` costs correctness. **"1..N roles"
is not one configuration and must not be ruled on as one.**

! **What SURVIVES N=1 is more than it looks.** The synthesis ORDER -- `query`, then `move`/`drop`,
then `correct`, then `patch`, then `add` -- is about VERDICT KINDS and not about roles
(`SKILL.md:817-829`). One role files several marks on one paragraph routinely: measured
2026-08-18, `block-context` filed two `correct`s on one docstring and stage 5 composed three marks
into one replacement. The residue check, the verification duty and step 6's set-agnostic wording
(*"every reviewer that ran"*) all hold unchanged.

## !! OUR OWN HISTORY IS A FIXTURE SOURCE, and the three kinds of case are not equal

| kind | the question | strength | answer key |
| --- | --- | --- | --- |
| REGRESSION | does the system still catch what it caught at `1ad4ba72`? | strong | a commit we wrote |
| KNOWN MISS | did it stop emitting the two-subject `patch` at `d3aa065`? | strong | the role file's own trigger |
| DISCOVERY | does it find a defect class nobody has shown it? | weak from our history | none -- the point is that there is none |

!! **The KNOWN MISS is the only kind that can prove a fix to the SYSTEM rather than to the
code.** A regression case says the tool still works; a discovery case says nothing yet. Only a
pinned miss, re-run after the role file changes, distinguishes a role that was taught something
from a role that got a different draw.

!! **And DISCOVERY from our own history is the over-fitting risk `corpora.toml` keeps a control
for.** Every defect in this history was found either by this system or by somebody reviewing it,
so a case built from one measures RECALL on a class already known. That is what the
public-history survey at T11 answers, and it stays separate -- not because it is less important,
but because it is not the same measurement.

! The two strong kinds need no network and no planting: the defect is at the parent, the fix is
the key, and both are commits on a branch that is already pushed.

## !! WHAT IS ACTUALLY ON DISK, MEASURED 2026-08-23

| fixture | where | state |
| --- | --- | --- |
| six cases with `expected` and `observed` | `evals/test-cases.jsonl` | present, no runner |
| the self-test commit range, all four roles | `evidence/self-test-commits.md` | present, never run |
| ten public corpora, materialised | `corpora/` and `corpora.toml` | present |
| the two `todo-tool` run packages | `evidence/` | **REMOVED 2026-08-23** |
| `redacted-corpus-full-v0_2/VERSIONS.md`, the pin | `evidence/` | **REMOVED 2026-08-23** |
| the twelve planted hazards and their grader | -- | **REMOVED 2026-08-23** |

!! **WHAT THE REMOVAL COST IS THE THIRD KIND OF CASE.** The `todo-tool` packages were the only
fixture whose SUBJECT was another repository, which is exactly the DISCOVERY axis our own commits
are weak on, and they carried what a synthetic case cannot: 171 prose paragraphs, four roles, and
a stage 8 that rolled a run back. **The replacement has to come from the public corpora, and that
is T22 and T11.**

!! **A HARNESS MUST ASK THE REMOTE, NOT THE CLONE.** This survives the removal and is the most
reusable thing the exercise produced. The first durability reading came from
`git branch -r --contains <sha>`, which searches `refs/remotes` -- and the clone had never FETCHED
those branches, so there was nothing to find and two safe commits read as local-only.
`git ls-remote --heads origin` is the authoritative check. ! The failure is silent in the
direction that matters: a stale tracking ref says a durable fixture is at risk, and would equally
say a lost one is fine.

! **The comment-review pins are annotated tags and still resolve.** Verified 2026-08-23:
`v0.2.0` -> `a0801d49e5c8`, `v0.2.1` -> `bb3281769298`, `v0.2.2` -> `ccb2404cb250`,
`v0.2.3` -> `3e1fedfe20f0`. Use `v0.2.2^{}` wherever a commit is wanted; `git rev-parse v0.2.2`
returns the tag object.

! **Durable does not mean available.** This repository is private, so no commit here is fetchable
without Roy's credentials. A case runs against a local clone or an authenticated fetch, and public
CI is out of scope until a repository is public. **The public corpora are the only fixtures with
no such condition.**

## Tasks

- [x] T1 -- * RULED 2026-08-18 by Roy: a reduced set is SUPPORTED, and `ownership-context` is
      NON-NEGOTIABLE. Every run carries it; the other three flex. So the legal sets are
      `{ownership-context}` plus any subset of `{block-context, function-context, module-context}`.
      !! It is the right role to pin because the truth it rules on is PRIOR to the others', not
      because it rules on none: it settles *"is this statement specifically about this piece of
      code"* and *"is this statement about any specific piece of code or documentation in this
      project"*. What it does NOT rule on is the truth of what the sentence ASSERTS -- the count,
      the bound, the worked example -- which is the other three's. ! The upper bound is left OPEN
      deliberately -- `1..N`, not `1..4`.

- [x] T2 -- FINISHED 2026-08-18, `d3aa065`. The agent file now reads *"the truth of the ANCHORING,
      as against the truth of the ASSERTION -- the count, the bound, the worked example -- which
      belongs to the other three"*, and its frontmatter carries the same sentence. Verified
      2026-08-23 in `agents/comment-review-ownership-context.md`. It replaced *"You do not rule on
      whether the claim is TRUE -- that is outside your remit."* Roy, 2026-08-18: the
      assessability ruling IS a truth ruling.

- [x] T3 -- * RULED 2026-08-18 by Roy: the PROJECT, and it shipped in `d3aa065`. The role file
      asks whether the paragraph is about any specific piece of code or documentation IN THIS
      PROJECT. So prose about nothing in the project is a `drop` and prose about something
      elsewhere in it is a `move`, and the documentation tree stage 1.4 resolves is in scope.

- [ ] T4 -- **State the RESIDUAL cost where the findings are read.** Pinning `ownership-context`
      fixes SCOPE -- a claim measured against the code it belongs to. It does not supply
      CORROBORATION: `SKILL.md` says a single-role run ratifies falsehoods, because one role
      reading a false absence claim writes that it is true where another refutes it by grep. A run
      carrying one truth-ruling role has every truth finding uncorroborated. Verify: the join's
      report, not only this file, says so on a run with fewer than four roles.

- [ ] T5 -- **Rewrite stage 5's synthesis section so it does not state the population as a fact.**
      `SKILL.md:813`, `:847` and `:843-844` each assume four. ! Say what the ORDER is about --
      verdict kinds, not roles -- so it reads correctly whether one role filed three marks or
      three roles filed one each. Verify: the section names no count, and every rule that needs a
      role says what happens when that role did not run.

- [x] T6 -- * RULED 2026-08-18: `ownership-context` is never optional, so the "who governs
      instead" question does not arise. The placement precedence stays as written; what T5 owes is
      saying that it may assume its own presence.

- [ ] T7 -- **Make the join say which roles ran.** A run with fewer than four produces a report
      that reads like any other today: `verdicts.py:505-518` names a MISSING reviewer only when
      `--reviewers` was given, and otherwise prints that it did not check. Verify: the summary
      names the reporting set and, where it is short of four, which role's corroboration is
      absent -- because that is exactly what an absence claim needs.

- [ ] T8 -- **Give a MARK-level case its terminus in writing.** Stage 4's record file is the
      artifact, `record.py --check` is its gate, and nothing downstream runs. Verify: a case
      asserts on a record file and `git status --short` is empty afterwards.

- [x] T9 -- * RULED 2026-08-18 by Roy: a fixture is a CHECKOUT AT A HASH, and THIS REPO'S OWN
      HISTORY is a valid source of them. Give the harness an address and a hash, check it out,
      focus on the files for the test, drop everything after reporting. That answers "how much
      context do we copy" by copying none -- the tree is real and complete. ! The mechanism ships:
      `corpora.toml` supports a `local` corpus as a `git worktree` and a `public` one as a sparse
      clone at a tag, and `scripts/fetch_corpora.py` builds both.

- [ ] T10 -- **Answer "how much context" for the extracted case**, since it is the fallback either
      way. A reviewer is given a census, a packet, a brief and a vocabulary; the packet names
      REFERENCE ONLY files whose whole purpose is settling claims the file under review cannot. A
      fixture that copies only the file under review makes every cross-file claim unsettleable and
      turns `query` into the correct answer for most of them. Verify by re-running a case from
      `evals/test-cases.jsonl` with the reference set removed and comparing the verdict mix.

- [ ] T11 -- **Survey public histories for cases with a known answer.** The property wanted is a
      commit where prose and code disagree and a later commit fixes it -- the fix is the answer
      key. `evals/generator_split.py` already splits a corpus's prose defects by whether the
      introducing commit carries an assistant trailer, so the search tooling half exists.
      !! This is now load-bearing rather than supplementary: it is the only remaining route to a
      DISCOVERY case, the `todo-tool` packages having been removed.

- [ ] T12 -- * **Rule the suite layout, now that only one option survives.** The old question was
      whether role cases live in a SKILL directory's `evals/evals.json` or in a second suite with
      its own layout. `evals/evals.json` is gone and `evals/test-cases.jsonl` is the second suite,
      already carrying `commit` and `role` -- fields the documented schema has nowhere to put. So
      the ruling owed is not the shape but the RUNNER: what executes a `test-cases.jsonl` row, and
      whether it is a script here or `skill-creator`. Verify: one command runs one row by `id` and
      exits nonzero on a miss.

- [x] T13 -- SUPERSEDED. "Add `assertions` to `evals/evals.json`" names a file that is no longer
      in the tree, and the field it wanted already exists under another name: every row of
      `evals/test-cases.jsonl` carries `expected`, `observed` and `outcome`. What is missing is
      something that READS them, which is T12.

- [ ] T14 -- **Run the six cases through `skill-creator`.** The install half is DONE -- verified
      2026-08-23, `skill-creator` is in `~/.claude/plugins/installed_plugins.json` from
      `claude-plugins-official`. It supplies what this repo has none of: a subagent per case with
      clean context, a WITHOUT-SKILL baseline arm, and a blind A/B between two skill versions.
      Verify: a `benchmark.json` exists and reports a delta; `find . -name benchmark.json` returns
      nothing today.

- [x] T15 -- SUPERSEDED. "Keep `grade_hazards.py` as the verification SCRIPT" names a file that is
      not in this tree and is not coming back in that form. ! The GUIDANCE it carried survives and
      belongs to T22: mechanical assertions belong in a script rather than an LLM judge.

- [x] T16 -- FINISHED. The first role case is written and has its answer key:
      `evals/test-cases.jsonl` row `module-context-widens-a-two-subject-docstring`, role
      `module-context`, outcome `miss`, at `d3aa0655b963`. Its `expected` is *"a `code_concerns`
      entry naming the split, and at most a `query` on the summary line"*; its `observed` is the
      `patch` that widened the docstring to announce both subjects -- the defect its own role
      file names as the trigger, applied as the remedy. ! What is still missing is a runner, which
      is T12, not a second case.

- [ ] T17 -- **Make the parent of the 2026-08-16 hand pass a case.**
      `the-shipped-python-does-not-pass-its-own-review.md` records the before and after --
      `census.py` 55 negative-prose lines of 286 down to 2 of 206, and five more files -- so the
      defect is MEASURED at the parent and MEASURED as fixed by the commit. ! It bears most
      directly on the claim that file exists to make, because a human found those by hand and the
      question is whether the system finds them. Verify: a row in `evals/test-cases.jsonl` pins
      that parent commit and names the files.

- [ ] T18 -- * **Decide whether to ask for `claude plugin eval` early access.** Separate, newer,
      CLI-driven -- `evals/**/case.yaml` or `prompt.md` plus `graders/*.md`, `--ablation
      with-without`, `--json`, `--threshold`, built for CI. Verified 2026-08-18: `--help` works
      and lists the full option set; running it prints `plugin eval is currently in early access`
      and exits 1, and `eval init` is gated too. No public documentation and no self-serve request
      route; enablement is an organisation-level environment variable issued by Anthropic. ! Not a
      blocker -- `skill-creator` covers isolation, the baseline and assertions today.

- [x] T19 -- SUPERSEDED. "Parse the two `todo-tool` packages into cases" cannot be done: both
      packages were removed from `evidence/` on 2026-08-23 with the corpus they described, and the
      subject repository is private. ! It is the same removal as T22's, and the discovery
      measurement it would have supplied is what T11 now has to supply instead.

- [x] T20 -- MOOT 2026-08-18: both subject commits were already on `origin`. Filed on a reading of
      `git branch -r --contains`, which searches only the tracking refs this clone had fetched --
      and it had fetched neither branch. ! What the task leaves behind is the RULE in the
      Objective: ask the remote, not the clone.

- [ ] T21 -- **Run `/comment-review` over the self-test commit range.**
      `evidence/self-test-commits.md` pins `d96b10d..7026646` on the branch
      `fix/folio-placement-is-not-where-the-anchor-is`,
      with cases now written up for ALL FOUR roles -- five `module-context`, plus
      `function-context`, `block-context` and `ownership-context` sections. Each is a PROSE defect
      a person found by reading, with the fix commit as its answer key, and **not one broke a
      test**: the suite was green through all of them, 672 to 713 passing. That file's own closing
      section says so: *"None of these was found by `/comment-review`."* ! It also records what is
      NOT a case -- a false plan tick, an `expectedFailure` firing, a hand-written fixture -- which
      are process defects this system has no remit over. Verify: a run exists for at least one row
      and its verdicts are recorded beside the diff that is the answer key.

- [ ] T22 -- !! **REBUILD THE TWELVE HAZARDS BY RESTATEMENT, on a public corpus.** The grader and
      the hazard set are no longer in this tree -- they were tied to a corpus this repo cannot
      ship. Each hazard has to be RESTATED (the failure named precisely enough to score, without
      reproducing the code it was found in) and planted on one of the ten corpora
      `corpora/corpora.toml` already materialises. ! Two of the twelve were positional or left
      true prose standing, so no text probe separated a correct repair from an ignored one; those
      reported NEEDS-EYES, and the replacement owes the same refusal rather than a clean. Verify:
      twelve restated hazards, a script that scores a worktree against them, and a base that is a
      corpus in `corpora.toml` rather than a hardcoded path.

## What this costs today

One run over two files, 154 prose paragraphs, four roles: **~870,000 subagent tokens** -- 186k
ownership, 184k module, 253k function, 247k block. The question being asked needed one role.
! Measured before `--filtered` collapsed the prose-less places; re-take it against
[`the-census-is-mostly-intervals-nobody-rules-on`](the-census-is-mostly-intervals-nobody-rules-on.md),
which owns that measurement.

## Sources

- [Extend Claude with skills](https://code.claude.com/docs/en/skills) -- the skill-creator loop
- [Evaluating skill output quality](https://agentskills.io/skill-creation/evaluating-skills) --
  `grading.json`, `benchmark.json`, and the with/without pattern

## Related

- [`a-role-can-reverse-itself-between-runs`](a-role-can-reverse-itself-between-runs.md) -- holds
  the confound note this file corrects, and the observation that nothing measures one run twice
- [`nothing-checks-that-four-reviewers-were-launched`](nothing-checks-that-four-reviewers-were-launched.md)
  -- the same population question from the gate's side
