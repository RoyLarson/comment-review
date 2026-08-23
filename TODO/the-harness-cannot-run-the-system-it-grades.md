# The harness cannot run the system it grades, and the cheap fix is the unsafe one

```
Status:   open
Progress: 6 of 22 tasks done
Owner:    testing
Requires-Roy: true
Raised:   2026-08-18, after a run whose only question needed one role and cost four
Corrected: 2026-08-20 — the fixtures in evidence/self-test-commits.md are FIVE module-
           context cases, not the twenty-one commits first recorded. Roy, 2026-08-20: a
           false plan tick, an expectedFailure firing and a hand-written fixture are
           'specifically not useful test cases for comment-review' -- they are process
           defects, and this system reads comments and docstrings against the code they
           sit with. The useful ones are the modules whose docstring announced one
           subject while the module held several.
```

## Objective

`evals/evals.json` is the documented skill-eval format and nothing in this repo runs it.
`grade_hazards.py` scores worktrees a person produced by hand, from a base hardcoded to
another repository, against twelve planted defects -- so a new question cannot be asked
without planting it there, and no measurement exists that a human did not perform.

The fix is per-role cases: one role, one fixture, one assertion, and an answer known in
advance. Ruled 2026-08-18: a reduced set is supported and `ownership-context` is never
dropped, so a case is a legal run rather than a test-only shape. **What remains is that the
prose does not say so** -- stage 4 dispatches four by name and stage 5 is written as a
negotiation between them, so a run of two reads as a run missing two.

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
finish. The existing note should be corrected rather than deleted.

## !! WHERE DOES A CASE STOP? -- and the second question dissolves the first

Roy, 2026-08-18: *"How to stop the run at the correct level? Or do we if we have built the
system to take 1 or more subagents?"*

**THE ASSERTION PICKS THE STAGE. There is nothing to stop.** A case's terminus is wherever the
artifact its assertion reads is written, and stage 4 already writes one to disk -- the reviewer's
own record file, checked by `record.py --check`. A case asking *"does `module-context` raise
this as a code concern"* reads that file and needs no synthesis, no galley, no approval and no
write. A case asking *"is the final text correct"* needs 5, 6 and 7b, and grades the diff. Two
kinds of case, two artifacts, no stop mechanism.

! That also decides the fixture question one row down: a MARK-level case never writes to the
tree, so it needs no worktree to throw away -- only somewhere to put the record file.

**AND THE JOIN ALREADY TAKES ANY SET.** `verdicts.py --reviewers` is a comma-separated list
matched against report stems; it does not know the number four. `coverage_gaps` counts against
the declared population and the summary already carries a NOT ACCOUNTED FOR line. So a one-role
run is machinery this repo has -- what hardcodes four is `SKILL.md`'s stage 4, which dispatches
by name, and the skill's arguments (`cap`, `target`, `style`) carry no role set.

! **So the reduced-set question is smaller than it looks: a ruling, an argument, and a line of
report.** It is not a re-architecture, and if N roles is a supported configuration then role
CASES stop being a test-only hack -- they are the same thing a user gets by asking for one.

## !! STAGE 5 IS WRITTEN FOR FOUR, AND THE ROLES ARE NOT INTERCHANGEABLE

Roy, 2026-08-18: *"SKILL.md also states that step 5 is expected to negotiate the result between
the agents. If one editorial role ran that can create confusion."*

Correct, and the confusion is specific. What breaks at N=1:

- **The premise is stated as a fact.** *"Four reviewers rule on the same block, so you hold
  several recommendations and must emit ONE replacement."* An agent holding one report reads
  that and has to decide whether it is missing three.
- **A count is used as an argument.** *"Any `correct` outranks every `clean`. THREE ROLES
  finding nothing does not soften one role finding a falsehood."*
- **A precedence names a role that may be absent.** *"Two placement verdicts on one block,
  naming different destinations: `ownership-context`'s destination governs."* If
  `ownership-context` is not in the set, that rule points at nobody and nothing says who
  governs instead.
- **The re-review it sends a contradiction to becomes SELF-review.** `drop` against `correct`
  on one sentence is ruled a contradiction and goes back -- to its filers, which at N=1 is the
  role that filed both.

!! **AND THE ROLES ARE NOT A SET, THEY ARE A LATTICE.** `SKILL.md` reads
`ownership-context` FIRST because the other three measure a claim against the code at their own
scope, and a misplaced claim gets measured against the wrong code. So a run without
`ownership-context` is not a smaller run -- it is a run whose remaining verdicts rest on an
unchecked assumption. Dropping `module-context` costs coverage; dropping `ownership-context`
costs correctness. **"1..N roles" is not one configuration and must not be ruled on as one.**

! **What SURVIVES N=1 is more than it looks, and worth saying so the ruling is not overbroad.**
The synthesis ORDER -- `query`, then `move`/`drop`, then `correct`, then `patch`, then `add` --
is about VERDICT KINDS and not about roles. One role files several marks on one block routinely:
measured 2026-08-18, `block-context` filed two `correct`s on one docstring and stage 5 composed
three marks into one replacement. The residue check, the verification duty and step 6's already
set-agnostic wording (*"every reviewer that ran"*) all hold unchanged.

! So stage 5 at N=1 is not empty -- it is MIS-DESCRIBED, and the hazard is an agent reading a
negotiation it does not have and inferring that a single uncorroborated finding needs less
scrutiny, in the one stage whose own text says a single-role run ratifies falsehoods.

## !! OUR OWN HISTORY IS A FIXTURE SOURCE, and the three kinds of case are not equal

Roy, 2026-08-18: previous commits on this repo's history are valid test cases. They are, and
saying WHAT EACH IS EVIDENCE OF decides which cases go where -- two of the three are enough for
the work in hand and the third is a different question wearing the same shape.

| kind | the question | strength | answer key |
| --- | --- | --- | --- |
| REGRESSION | does the system still catch what it caught at `882635ba`? | strong | a commit we wrote |
| KNOWN MISS | did it stop emitting the two-subject `patch` at `4fd8384`? | strong | the role file's own trigger |
| DISCOVERY | does it find a defect class nobody has shown it? | weak from our history | none -- the point is that there is none |

!! **The KNOWN MISS is the only kind that can prove a fix to the SYSTEM rather than to the
code.** A regression case says the tool still works; a discovery case says nothing yet. Only a
pinned miss, re-run after the role file changes, distinguishes a role that was taught something
from a role that got a different draw.

!! **And DISCOVERY from our own history is the over-fitting risk `corpora.toml` already keeps
two personal projects as a control for.** Every defect in this history was found either by this
system or by somebody reviewing it, so a case built from one measures RECALL on a class already
known. That is what the public-history survey one task down answers, and it stays separate --
not because it is less important, but because it is not the same measurement and must not be
reported as though it were.

! The two strong kinds need no network, no third-party tree, and no planting: the defect is at
the parent, the fix is the key, and both are commits on a branch that is already pushed.

## !! THE RICHEST FIXTURE IS ALREADY ON DISK, PINNED, AND EXTERNAL

Roy, 2026-08-18: the `todo_tool` runs were made against
`REDACTED_SHA_D`, so `evidence/` already holds what a case needs.

**Two complete packages, same subject, same hash** -- `redacted_corpus` branch
`todo-requires-roy` at `REDACTED_SHA_D`, three files, 3,333 census blocks, **171 holding prose** (88
docstring, 75 comment, 8 trailing):

| package | what it holds |
| --- | --- |
| [`evidence/todo-tool-full-run/`](../evidence/todo-tool-full-run/) | the first run -- one blocked, one complete, plus `tool-findings.md` |
| [`evidence/todo-tool-full-v0_2/`](../evidence/todo-tool-full-v0_2/) | the second: census, all four reviewer reports, four joins, stage 5, 6, 7a and 8 artifacts, `applied.patch`, and two miss analyses |

! Its own README already says what this file wants: *"kept as a documented test case for the
next iteration of the tool."*

!! **THIS IS THE THIRD KIND OF CASE, and the one our own history cannot supply.** The subject is
ANOTHER REPOSITORY, so a finding here is not a defect this system already knew about -- which is
exactly the DISCOVERY axis the taxonomy above marks weak for our own commits. It also carries
what a synthetic case cannot: 171 prose blocks, four roles, and a stage 8 that ROLLED A RUN BACK.

!! **A CASE MUST CHECK OUT `REDACTED_SHA_D`; IT MUST NOT READ `scripts/todo_tool.py`.** The vendored
copy in this repo is no longer the fixture -- it carries a local stdout-encoding patch and is
1,646 lines against the fixture's 1,638. Reading the convenient copy would grade the system
against a file the run never saw.

! **One number in the evidence is off and is NOT corrected here**, because a captured run is a
record: `todo-tool-full-v0_2/README.md` states `todo_tool.py` at 1640 lines where `REDACTED_SHA_D` has
1638. The run edited these files and restored them, so the count was most likely taken after its
own edits. ! Anything keying on a line number in that package should re-derive it from the hash.

## !! A CASE IS TWO PINS, AND HALF OF THEM LIVE ON ONE DISK

**A run is only reproducible if BOTH the tool version and the subject tree are pinned.** Roy
supplied both halves 2026-08-18; verified the same day:

| pin | commit | where | durable |
| --- | --- | --- | --- |
| comment-review `v0.2.0` | `4621569cf370` | `origin/main`, annotated tag | yes |
| comment-review `v0.2.1` | `7a0945ad3f40` | `origin/main`, annotated tag | yes |
| comment-review `v0.2.2` | `5e0b0f75105b` | `origin/main`, annotated tag | yes |
| redacted_corpus BASE | `REDACTED_SHA_E` | `origin/master` | yes |
| redacted_corpus RUN | `REDACTED_SHA_F` | `origin/redacted-branch-b` (tip) | yes |
| redacted_corpus todo-tool | `REDACTED_SHA_D` | `origin/todo-requires-roy`, 1 behind tip | yes |

!! **CORRECTED 2026-08-18: ALL SIX ARE ON A REMOTE. The durability problem does not exist,
and the way it was mis-measured is worth more than the scare.**

The first reading said the two SUBJECT commits were local-only. It came from
`git branch -r --contains <sha>`, which searches `refs/remotes` -- and this clone had never
FETCHED those two branches, so there was nothing there to find. The commits were on `origin` the
whole time. `git ls-remote --heads origin` is the authoritative check and disagreed immediately.

!! **A HARNESS MUST ASK THE REMOTE, NOT THE CLONE.** Every fixture claim of the form *"this
commit is safe"* has to come from `git ls-remote` or an explicit fetch. A stale or absent
tracking ref reads exactly like a commit that was never pushed, and the failure is silent in
the direction that matters -- it says a durable fixture is at risk, and it would equally say a
lost one is fine if a tracking ref were stale the other way.

- **DURABILITY -- not a problem.** All six are reachable from a branch on `origin`. `REDACTED_SHA_D`
  sits one commit behind `origin/todo-requires-roy`'s tip `REDACTED_SHA_G` and is still an ancestor
  of it.
- **ACCESS -- not fixable, and not a defect.** Roy, 2026-08-18: *"None because they are
  private."* Both repositories are private, so no commit here is fetchable without his
  credentials, INCLUDING the four that are durable. **A case runs against a local clone or an
  authenticated fetch, and public CI is out of scope until a repository is public.**

! **Durable does not mean available.** Durable means it survives a deleted branch or a lost
disk; a runner still cannot get it. A case should say which of the two it needs.

! **The comment-review self-history cases differ on ONE axis only.** Their commits are ancestors
of `main` and contained in `v0.2.3`, so they are durable -- and that repository is private too,
so they are no more publicly fetchable than these. Durability is the whole difference.

! **The tags are ANNOTATED**, so `git rev-parse v0.2.2` returns the tag object. Use `v0.2.2^{}`
wherever a commit is wanted. The two whose tag object could be mistaken for the commit are
recorded in that package's `VERSIONS.md`.

! `evidence/redacted-corpus-full-v0_2/VERSIONS.md` is already the authoritative pin for that
package and states all of this except reachability. It is not restated there; this table adds
only which side of the network each commit is on.

## Tasks

- [x] * **RULED 2026-08-18 by Roy: a reduced set is SUPPORTED, and
      `ownership-context` is NON-NEGOTIABLE.** Every run carries it; the other three flex. So
      the legal sets are `{ownership-context}` plus any subset of `{block-context,
      function-context, module-context}`.

      !! **It is the right role to pin because the truth it rules on is PRIOR to the others',
      not because it rules on none.** Roy, 2026-08-18: it settles *"is this statement
      specifically about this piece of code"* and *"is this statement about any specific piece
      of code or documentation in this project"*. Both are propositions that can be false and
      are settled by evidence. What it does NOT rule on is the truth of what the sentence
      ASSERTS -- the count, the bound, the worked example -- which is the other three's.

      !! **Every other role's verdict PRESUPPOSES that ruling.** A claim attached to the wrong
      scope is checked against the wrong code: a comment about `parse()` sitting above
      `render()` is read against `render()`, found false, and CORRECTED into a falsehood. So
      dropping `ownership-context` does not remove a check, it leaves the remaining checks
      resting on an assumption nobody made. Dropping any other removes a remit and nothing
      else.

      ! **`ownership-context` ALONE is therefore a coherent run**: it answers whether the prose
      is about this code, or about anything in the project, and emits no findings about what
      the prose asserts.

      ! **The upper bound is left OPEN deliberately** -- `1..N`, not `1..4`. Roy, 2026-08-18: a
      fifth editorial role might be found, *"though the fact the editorial roles mimic
      real-world roles makes me think it is unlikely."* The four are a copy desk; `compact` and
      `review` are stages rather than members of the board.

- [x] **Corrected 2026-08-18, `4fd8384`.** The agent file now reads *"the truth of the
      ANCHORING, as against the truth of the ASSERTION -- the count, the bound, the worked
      example -- which belongs to the other three"*, and its frontmatter carries the same
      sentence. The text it replaced:
      *"You do not rule on whether the claim is TRUE -- that is outside your remit. You rule on
      whether truth is assessable here at all."* Roy, 2026-08-18: the assessability ruling IS a
      truth ruling -- it settles a proposition about the statement's relation to the code, and
      that proposition can be false. The distinction the sentence wants is between the truth of
      the ANCHORING and the truth of the ASSERTION, and it should say that. ! It matters beyond
      wording: the role that is never dropped should state its remit at full width, or a reader
      deciding a set will under-rate it.

- [x] * **RULED 2026-08-18 by Roy: the PROJECT, and it shipped in `4fd8384`.** The role file
      now asks whether the block is about any specific piece of code or documentation IN THIS
      PROJECT, and says so twice -- the second question itself, and *"the right place is
      anywhere in the PROJECT, not only this file -- another module, or the documentation tree
      the run named"*. So prose about nothing in the project is a `drop` and prose about
      something elsewhere in it is a `move`, and the documentation tree stage 1.4 resolves is
      in scope for that ruling. The question as it was put:
      whether a block would be truthy where it sits, and whether it would be truthy *"in the
      right place"* -- with the surrounding text file-scoped (*"equally useful anywhere in the
      FILE"*). Roy states it wider: *"about any specific piece of code or documentation in this
      project"*. The difference decides a verdict -- prose about nothing in the project is a
      `drop`, prose about something elsewhere in it is a `move` -- and the wider reading pulls
      in the documentation tree stage 1.4 resolves.

- [ ] **State the RESIDUAL cost, which this ruling does not remove.** Pinning
      `ownership-context` fixes SCOPE -- a claim measured against the code it belongs to. It
      does not supply CORROBORATION, and those are different: `SKILL.md` says a single-role run
      ratifies falsehoods because one role reading a false absence claim writes that it is
      true where another refutes it by grep. A run carrying one truth-ruling role has every
      truth finding uncorroborated. ! Say it where the findings are read, not only in the
      arguments.

- [ ] **Rewrite stage 5's synthesis section so it does not state the population as a fact.**
      The premise sentence, the "three roles finding nothing" argument and the
      `ownership-context` placement precedence each assume four. ! Say what the ORDER is about
      -- verdict kinds, not roles -- so it reads correctly whether one role filed three marks
      or three roles filed one each. Verify: the section names no count, and every rule that
      needs a role says what happens when that role did not run.

- [x] * **RULED 2026-08-18: it is never optional, so the question does not arise.**
      `ownership-context`'s destination governs two placement verdicts, and that role is in
      every legal set. ! The rule stays as written; what needs saying is that it may now
      assume its own presence.

- [ ] **Then make the tool say which it was.** A run with fewer than four roles produces a
      report that reads like any other today. Whatever is ruled above, the join's output has to
      carry it, because the report is what a reader grades from -- and the corroboration a
      missing role would have supplied is exactly what an absence claim needs.

- [ ] **Give a MARK-level case its terminus in writing.** Stage 4's record file is the artifact,
      `record.py --check` is its gate, and nothing downstream runs. Verify: a case asserts on a
      record file and the tree is unmodified afterwards.

- [x] * **RULED 2026-08-18 by Roy: a checkout at a hash, and THIS REPO'S OWN HISTORY is a
      valid source of them.** Give the harness an address and a hash, check it out, focus on
      the files for the test, drop everything after reporting. That answers "how much context
      do we copy" by copying none -- the tree is real and complete.

      !! **The second half is what settled it.** Roy, 2026-08-18: previous commits on this
      repo's own history are valid test cases. `evals/test-cases.jsonl` is already built that
      way, and the two commits it pins were verified 2026-08-18 as ancestors of `main`,
      reachable from `origin/main`, and contained in `v0.2.3` -- so the fixtures cannot be
      collected and cannot drift. The network dependency this task was weighing does not
      arise for them.

      ! **The mechanism ships already.** `corpora.toml` supports a `local` corpus as a
      `git worktree` of a repo on the machine and a `public` one as a sparse clone at a tag;
      `scripts/fetch_corpora.py` builds both. Nothing new is needed to check out a fixture.

- [ ] **Answer "how much context" for the extracted case, since it is the fallback either way.**
      A reviewer is given a census, a packet, a brief and a vocabulary; the packet names
      REFERENCE ONLY files whose whole purpose is settling claims that the file under review
      cannot. A fixture that copies only the file under review makes every cross-file claim
      unsettleable and turns `query` into the correct answer for most of them. Verify by
      re-running a known case with the reference set removed and comparing the verdict mix.

- [ ] **Survey public histories for cases with a known answer.** The property wanted is a commit
      where prose and code disagree and a later commit fixes it -- the fix is the answer key.
      `evals/generator_split.py` already splits a corpus's prose defects by whether the
      introducing commit carries an assistant trailer, so the search tooling half exists.

- [ ] * **Rule the suite layout, because roles are not skills.** The documented format is
      `evals/evals.json` inside a SKILL directory, and the four reviewers are AGENTS. Either
      role cases live in the skill's suite with a prompt that dispatches one role, or they are
      a second suite with its own layout and the shipped runner covers only whole-skill cases.
      This decides whether the corpus is one file or five, so it comes before writing cases.

      ! **The fixture ruling above narrows this to one option, and the ruling should say so
      rather than arrive at it twice.** The documented schema takes `files: [...]` -- a list
      copied INTO the case -- and neither it nor `claude plugin eval` pins a repository state.
      A case whose fixture is `(address, hash, files)` has nowhere to put the hash in that
      format. So the choice is not between two shapes of equal cost: it is a second suite, or
      it is abandoning hash fixtures.

- [ ] **Add `assertions` to `evals/evals.json`.** The documented schema is `id`, `prompt`,
      `expected_output`, `files`, `assertions`; this repo's three cases carry every field but
      that one, plus a local `hazards`. `assertions` is the field that states a known result,
      which is the whole point of the upgrade.

- [ ] **Install `skill-creator` and run the existing three cases through it.** It is generally
      available -- `/plugin marketplace add anthropics/claude-plugins-official` then
      `/plugin install skill-creator@claude-plugins-official` -- and it supplies what this repo
      has none of: a subagent per case with clean context, a WITHOUT-SKILL baseline arm, and a
      blind A/B between two skill versions. Verify: `benchmark.json` reports a delta.

- [ ] **Keep `grade_hazards.py` as the verification SCRIPT, not the harness.** The guidance is
      explicit that mechanical assertions belong in a script rather than an LLM judge. Its base
      is hardcoded to another repository, which the fixture ruling above will move.

- [ ] **Write the first role case, which already has a known answer.** Given `verdicts.py`,
      `module-context` should raise the two-subject finding as a `code_concerns` entry and at
      most `query` the summary line. Measured 2026-08-18: it emitted a `patch` widening the
      docstring to announce both subjects -- the defect its own role file names as the trigger,
      applied as the remedy. ! Its role file lists three triggers for "a module announcing more
      than one subject" and never says what verdict one earns; the same file does say a
      misplaced module constant is a CODE CONCERN, so the pattern exists and was not applied
      here.

- [ ] **Locate the 2026-08-16 hand pass over the shipped Python, and make its parent a case.**
      `the-shipped-python-does-not-pass-its-own-review.md` records the before and after --
      `census.py` 55 negative-prose lines of 286 down to 2 of 206, and five more files -- so the
      defect is MEASURED at the parent and MEASURED as fixed by the commit. ! It is the case
      that bears most directly on the claim that file exists to make, because a human found
      those by hand and the question is whether the system finds them.

- [ ] * **Decide whether to ask for `claude plugin eval` early access.** Separate, newer,
      CLI-driven -- `evals/**/case.yaml` or `prompt.md` plus `graders/*.md`, `--ablation
      with-without`, `--json`, `--threshold`, built for CI. Verified 2026-08-18: `--help`
      works and lists the full option set; running it prints `plugin eval is currently in early
      access` and exits 1, and `eval init` is gated too. No public documentation was found and
      no self-serve request route; enablement is an organisation-level environment variable
      issued by Anthropic. ! Not a blocker -- `skill-creator` covers isolation, the baseline
      and assertions today.
- [ ] **Parse the two `todo-tool` packages into cases.** Subject
      `redacted_corpus@REDACTED_SHA_D`, three files, 171 prose blocks, four reviewer
      reports and stage 5-8 artifacts per run. ! Check the hash out; do NOT read
      this repo's vendored `scripts/todo_tool.py`, which carries a local patch and
      is eight lines longer than the fixture.
- [x] **MOOT 2026-08-18: both were already on `origin`.** Filed on a reading of
      `git branch -r --contains`, which searches only the tracking refs this clone
      had fetched -- and it had fetched neither branch. `git push` reported
      *"Everything up-to-date"* and `git ls-remote` confirmed both. ! What the task
      leaves behind is the RULE above: ask the remote, not the clone.
- [ ] !! TWENTY-ONE COMMITS ARE RECORDED AS FIXTURES -- `evidence/self-test-
      commits.md`, range `3af9752..93cc4b0`. Each is a PROSE defect a person found
      by reading, with the fix commit as its answer key, and NOT ONE broke a test:
      the suite was green through all of them, 672 to 713 passing. ! Roy,
      2026-08-20: 'put the commit range in the evidence files or wherever we can
      remember that these specific commits are good test cases for the system to
      test itself against.' ! Running `/comment-review` over them is the
      measurement this file exists to make possible, and it has not been done.
- [ ] !! REBUILD THE TWELVE HAZARDS BY RESTATEMENT. The grader and the hazard set
      are no longer in this tree -- they were tied to a corpus this repo cannot
      ship. Each hazard has to be RESTATED (the failure named precisely enough to
      score, without reproducing the code it was found in) and planted on one of
      the public corpora. ! Two of the twelve were positional or left true prose
      standing, so no text probe separated a correct repair from an ignored one;
      those reported NEEDS-EYES, and the replacement owes the same refusal rather
      than a clean.

## What this costs today

One run over two files, 154 prose blocks, four roles: **~870,000 subagent tokens** -- 186k
ownership, 184k module, 253k function, 247k block. The question being asked needed one role.

## Sources

- [Extend Claude with skills](https://code.claude.com/docs/en/skills) -- the skill-creator loop
- [Evaluating skill output quality](https://agentskills.io/skill-creation/evaluating-skills) --
  the `evals.json` schema, `grading.json`, `benchmark.json`, and the with/without pattern

## Related

- [`a-role-can-reverse-itself-between-runs`](a-role-can-reverse-itself-between-runs.md) -- holds
  the confound note this file corrects, and the observation that nothing measures one run twice
- [`nothing-checks-that-four-reviewers-were-launched`](nothing-checks-that-four-reviewers-were-launched.md)
  -- the same population question from the gate's side
