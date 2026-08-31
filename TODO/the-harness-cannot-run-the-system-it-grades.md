# The harness cannot run the system it grades, and the cheap fix is the unsafe one

```
Status:   decision-needed
Progress: 10 of 31 tasks done
Owner:    testing
Requires-Roy: true
Raised:   2026-08-18, after a run whose only question needed one role and cost four
Triaged:  2026-08-23 -- the grader, the twelve hazards and the two `todo-tool` evidence
          packages were REMOVED from the tree: they described a corpus this repo cannot
          publish. Four tasks named files that no longer exist and were re-ruled; the
          fixture inventory below is what a `find` returns today
Split:    2026-08-23 -- 22 boxes became 29. The rulings and measurements that carried a
          box are stated below and their boxes now say only what was settled
Absorbed: 2026-08-24 — P5 of the 0.2.4 foliator plan came here as T30 and T31. Roy:
          supersede P5 to that todo because it is testing work anyways. Both halves were
          missing an instrument this file owns -- the recall figure that justifies the
          filtered view is in run history and nowhere a reader can find it, and the
          scorer that would settle the dominance claim is T28. ! The plan closed at 25
          of 25 on that supersession, not on the work: what P5 asked for is unbuilt and
          now waits here, which is what a backlog is for.
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
scoring this system had**, and rebuilding it by RESTATEMENT on a public corpus is T26 to T29.

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

**AND THE COLLATOR ALREADY TAKES ANY SET.** `verdicts.py:296` takes `--reviewers` as a
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
public-history survey at T14 answers, and it stays separate -- not because it is less important,
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
is T14 and T26 to T29.**

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

## What the settled boxes recorded

!! **THE LEGAL SETS, RULED 2026-08-18 by Roy** (T1). A reduced set is SUPPORTED and
`ownership-context` is NON-NEGOTIABLE: every run carries it, the other three flex, so the legal
sets are `{ownership-context}` plus any subset of
`{block-context, function-context, module-context}`. ! It is the right role to pin because the
truth it rules on is PRIOR to the others', not because it rules on none: it settles *"is this
statement specifically about this piece of code"* and *"is this statement about any specific
piece of code or documentation in this project"*. What it does NOT rule on is the truth of what
the sentence ASSERTS -- the count, the bound, the worked example -- which is the other three's.
! The upper bound is left OPEN deliberately -- `1..N`, not `1..4`.

! **WHAT SHIPPED FOR IT, 2026-08-18 in `d3aa065`** (T2). The agent file now reads *"the truth of
the ANCHORING, as against the truth of the ASSERTION -- the count, the bound, the worked example
-- which belongs to the other three"*, and its frontmatter carries the same sentence. Verified
2026-08-23 in `agents/comment-review-ownership-context.md`. It replaced *"You do not rule on
whether the claim is TRUE -- that is outside your remit."* Roy, 2026-08-18: the assessability
ruling IS a truth ruling.

! **THE SCOPE IS THE PROJECT, RULED 2026-08-18 by Roy** (T3), shipped in `d3aa065`. The role file
asks whether the paragraph is about any specific piece of code or documentation IN THIS PROJECT.
So prose about nothing in the project is a `drop` and prose about something elsewhere in it is a
`move`, and the documentation tree stage 1.4 resolves is in scope.

! **AND BECAUSE `ownership-context` IS NEVER OPTIONAL** (T8), the "who governs instead" question
does not arise. The placement precedence stays as written; what T5 to T7 owe is saying that it
may assume its own presence.

! **A FIXTURE IS A CHECKOUT AT A HASH, RULED 2026-08-18 by Roy** (T12), and THIS REPO'S OWN
HISTORY is a valid source of them. Give the harness an address and a hash, check it out, focus on
the files for the test, drop everything after reporting. That answers "how much context do we
copy" by copying none -- the tree is real and complete. ! The mechanism ships: `corpora.toml`
supports a `local` corpus as a `git worktree` and a `public` one as a sparse clone at a tag, and
`scripts/fetch_corpora.py` builds both.

! **WHAT THE REMOVALS SUPERSEDED.** (T17) "Add `assertions` to `evals/evals.json`" names a file
no longer in the tree, and the field it wanted exists under another name: every row of
`evals/test-cases.jsonl` carries `expected`, `observed` and `outcome`; what is missing is
something that READS them, which is T15 and T16. (T19) "Keep `grade_hazards.py` as the
verification SCRIPT" names a file that is not in this tree and is not coming back in that form --
the GUIDANCE it carried survives and belongs to T26 to T29: mechanical assertions belong in a
script rather than an LLM judge. (T23) "Parse the two `todo-tool` packages into cases" cannot be
done: both were removed from `evidence/` on 2026-08-23 with the corpus they described, and the
subject repository is private, so the discovery measurement falls to T14.

! **THE FIRST ROLE CASE IS WRITTEN AND HAS ITS ANSWER KEY** (T20): `evals/test-cases.jsonl` row
`module-context-widens-a-two-subject-docstring`, role `module-context`, outcome `miss`, at
`d3aa0655b963`. Its `expected` is *"a `code_concerns` entry naming the split, and at most a
`query` on the summary line"*; its `observed` is the `patch` that widened the docstring to
announce both subjects -- the defect its own role file names as the trigger, applied as the
remedy. ! What is still missing is a runner, which is T15 and T16, not a second case.

! **THE DURABILITY SCARE WAS MOOT, 2026-08-18** (T24): both subject commits were already on
`origin`. It was filed on a reading of `git branch -r --contains`, which searches only the
tracking refs this clone had fetched -- and it had fetched neither branch. What it leaves behind
is the rule stated above: ask the remote, not the clone.

! **WHAT `skill-creator` SUPPLIES, verified 2026-08-23**: it is installed, from
`claude-plugins-official` in `~/.claude/plugins/installed_plugins.json`, and gives this repo what
it has none of -- a subagent per case with clean context, a WITHOUT-SKILL baseline arm, and a
blind A/B between two skill versions.

! **WHAT `claude plugin eval` IS, verified 2026-08-18.** Separate, newer, CLI-driven --
`evals/**/case.yaml` or `prompt.md` plus `graders/*.md`, `--ablation with-without`, `--json`,
`--threshold`, built for CI. `--help` works and lists the full option set; running it prints
`plugin eval is currently in early access` and exits 1, and `eval init` is gated too. No public
documentation and no self-serve request route; enablement is an organisation-level environment
variable issued by Anthropic. ! Not a blocker -- `skill-creator` covers isolation, the baseline
and assertions today.

! **WHAT THE 2026-08-16 HAND PASS MEASURED.**
`the-shipped-python-does-not-pass-its-own-review.md` records the before and after -- `census.py`
55 negative-prose lines of 286 down to 2 of 206, and five more files -- so the defect is MEASURED
at the parent and MEASURED as fixed by the commit. ! It bears most directly on the claim that
file exists to make, because a human found those by hand and the question is whether the system
finds them.

! **WHAT THE SELF-TEST RANGE HOLDS.** `evidence/self-test-commits.md` pins `d96b10d..7026646` on
the branch `fix/folio-placement-is-not-where-the-anchor-is`, with cases written up for ALL FOUR
roles -- five `module-context`, plus `function-context`, `block-context` and `ownership-context`
sections. Each is a PROSE defect a person found by reading, with the fix commit as its answer
key, and **not one broke a test**: the suite was green through all of them, 672 to 713 passing.
That file's own closing section says so: *"None of these was found by `/comment-review`."* ! It
also records what is NOT a case -- a false plan tick, an `expectedFailure` firing, a
hand-written fixture -- which are process defects this system has no remit over.

! **WHY TWO OF THE TWELVE HAZARDS NEED A REFUSAL RATHER THAN A CLEAN.** Two were positional or
left true prose standing, so no text probe separated a correct repair from an ignored one; those
reported NEEDS-EYES, and the replacement owes the same refusal.

## !! P5 CAME HERE 2026-08-24, AND IT IS THE PAGE'S OWN PASS CRITERION

Roy, 2026-08-24: *"supersede P5 to that todo because it is testing's work anyways."* It was the
last open box on the `0.2.4-rework-the-foliator-owns-the-address` plan, and it could not be
worked there: **both of its halves are missing an instrument, and both instruments are this
file's.** T30 and T31 carry it.

! **NAMED, NOT LINKED, AND THAT IS THE RULE.** A `T` takes no dependency on a `P` -- see
`docs/conventions.md`, *T, P and SP*. What arrived here is the WORK; the plan that used to hold
it can be deleted tomorrow and T30 and T31 stay answerable, which is the test.

!! **THE PAGE CLAIMS TO DOMINATE BOTH PRIOR FORMATS, WHICH IS NOT A PREFERENCE.** Roy,
2026-08-20: the page is *"partially to get the best of both worlds."* It fails if either half
fails:

| | information | tokens | recall |
| --- | --- | --- | --- |
| unfiltered, v0.1.0 | all | high | **worse** |
| filtered, v0.2.0 | less | low | baseline |
| the page | MORE than filtered | LESS than unfiltered | AT LEAST filtered |

!! **AND THE PRIOR IS ALREADY MEASURED AND WRITTEN DOWN NOWHERE.** Roy, 2026-08-20, on the
v0.1.0 -> v0.2.0 split: going unfiltered, *"the agents got a lot more tokens and used a lot more
tokens on effectively the same level of output. They did miss a lot in the difference."*
! Nothing in `evidence/` records it and the shipped tree carries only the byte figures -- 39% of
the listing was repeated paths, `--filtered` saved 61%. **The measurement that justifies the
single most consequential thing about what a reviewer sees exists in run history and nowhere a
reader can find it**, which is T30.

! **T31 IS DOWNSTREAM OF THE SCORER**, T28: a hand-run comparison is the thing this file exists
to end, so the dominance claim waits on something that can disagree with it.

## Tasks

- [x] T1 -- RULED 2026-08-18 by Roy: a reduced set is SUPPORTED and `ownership-context` is
      NON-NEGOTIABLE; the legal sets are in the Objective.
- [x] T2 -- FINISHED 2026-08-18, `d3aa065`: the ANCHORING-against-ASSERTION sentence ships
      in `agents/comment-review-ownership-context.md`, verified 2026-08-23.
- [x] T3 -- RULED 2026-08-18 by Roy: the scope is the PROJECT, and it shipped in
      `d3aa065`.
- [ ] T4 -- State the residual cost of a reduced run -- every truth finding
      uncorroborated. Verify: the collator's report says so, not only this file.
- [ ] T5 -- Rewrite stage 5's synthesis so it states no population count; `SKILL.md:813`,
      `:847` and `:843-844` each assume four. Verify: the section names no count.
- [ ] T6 -- Say in stage 5 that the synthesis ORDER is about verdict kinds, not roles.
      Verify: it reads correctly for one role filing three marks.
- [ ] T7 -- Make every stage-5 rule that names a role say what happens when that role did
      not run. Verify: no rule naming a role is silent on its absence.
- [x] T8 -- RULED 2026-08-18: `ownership-context` is never optional, so "who governs
      instead" does not arise and the placement precedence stays as written.
- [ ] T9 -- Make the collator name the reporting set even with no `--reviewers`. Verify: a run
      without it prints which roles reported.
- [ ] T10 -- Where the set is short of four, make the collator name whose corroboration is
      absent. Verify: a three-role report names it.
- [ ] T11 -- Give a MARK-level case its terminus in writing: stage 4's record file.
      Verify: a case asserts on one and `git status --short` is empty.
- [x] T12 -- RULED 2026-08-18 by Roy: a fixture is a CHECKOUT AT A HASH and this repo's
      own history is a source; the mechanism ships.
- [ ] T13 -- Answer how much context an extracted case copies, given the packet's
      REFERENCE ONLY files. Verify: re-run a case without them, compare verdicts.
- [ ] T14 -- Survey public histories for a commit whose prose and code disagree, and its
      later fix. Verify: one such pair is a row in `evals/test-cases.jsonl`.
- [?] T15 -- * Rule what executes a `test-cases.jsonl` row: a script in this repo or
      `skill-creator`. Verify: the answer is written into this file.
- [ ] T16 -- Build that runner. Verify: one command runs one row by `id` and exits nonzero
      on a miss.
- [x] T17 -- SUPERSEDED: `evals/evals.json` is gone and the `assertions` field it wanted
      exists as `expected`, `observed` and `outcome` on every `test-cases.jsonl` row.
- [ ] T18 -- Run the six `evals/test-cases.jsonl` cases through `skill-creator`. Verify: a
      `benchmark.json` exists and reports a delta; today none does.
- [x] T19 -- SUPERSEDED: `grade_hazards.py` is not in this tree and is not returning in
      that form; the guidance it carried is in the Objective and belongs to T26 to T29.
- [x] T20 -- FINISHED: the first role case and its answer key are written, at
      `evals/test-cases.jsonl` row `module-context-widens-a-two-subject-docstring`.
- [ ] T21 -- Make the parent of the 2026-08-16 hand pass a case. Verify: a row in
      `evals/test-cases.jsonl` pins that parent commit and names the files.
- [?] T22 -- * Decide whether to ask for `claude plugin eval` early access. Verify: the
      decision and its reason are written into this file.
- [x] T23 -- SUPERSEDED: both `todo-tool` packages were removed 2026-08-23 and the subject
      repo is private, so the DISCOVERY measurement they would have supplied falls to T14.
- [x] T24 -- MOOT 2026-08-18: both subject commits were already on `origin`; the rule it
      leaves -- ask the remote, not the clone -- is in the Objective.
- [ ] T25 -- Run `/comment-review` over the self-test range `d96b10d..7026646`. Verify:
      one row has a run, with its verdicts beside the answer-key diff.
- [ ] T26 -- Restate the twelve hazards, each named precisely enough to score without the
      code it was found in. Verify: twelve restatements, none quoting.
- [ ] T27 -- Plant the restated set on a corpus `corpora/corpora.toml` materialises.
      Verify: the base is a manifest row rather than a hardcoded path.
- [ ] T28 -- Write the scorer for the restated set. Verify: one script scores a worktree
      against the twelve and exits nonzero on a miss.
- [ ] T29 -- Make the two hazards no text probe separates report NEEDS-EYES rather than a
      pass. Verify: scoring a worktree that ignored either returns NEEDS-EYES.
- [ ] T30 -- Recover the v0.1.0-vs-v0.2.0 recall figure into `evidence/`, or record it
      lost. Verify: a reader finds it without reading a run transcript.
- [ ] T31 -- Score the page against BOTH prior formats, on the dominance criterion.
      Verify: more info than filtered, fewer tokens than unfiltered, recall >= filtered.

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
