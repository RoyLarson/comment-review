# The harness cannot run the system it grades, and the cheap fix is the unsafe one

```
Status:   decision-needed
Progress: 16 of 48 tasks done
Owner:    testing
Requires-Roy: true
Raised:   2026-08-18, after a run whose only question needed one role and cost four
Triaged:  2026-08-23 -- the grader, the twelve hazards and the two `todo-tool` evidence
          packages were REMOVED from the tree: they described a corpus this repo cannot
          publish. Four tasks named files that no longer exist and were re-ruled; the
          fixture inventory below is what a `find` returns today
Split:    2026-08-23 -- 22 boxes became 29. The rulings and measurements that carried a
          box are stated below and their boxes now say only what was settled
Merged:   2026-08-24 -- two divergent copies of this file reconciled. From the 0.2.4
          branch: the header fields, the two-line task shape, and every box the
          2026-08-23 history purge superseded -- that side is NEWER on what is on disk.
          From the harness branch: the START/END amendment, the A-F versus pass-or-void
          rubric split, the `claude plugin eval` decision, the Part IV case, the one
          variable per release ruling and the baseline patch -- that side is NEWER on
          what was ruled after the fork. Where the two disagreed on a file, `ls` decided
Absorbed: 2026-08-24 — P5 of the 0.2.4 foliator plan came here as T43 and T44. Roy:
          supersede P5 to that todo because it is testing work anyways. Both halves were
          missing an instrument this file owns -- the recall figure that justifies the
          filtered view is in run history and nowhere a reader can find it, and the
          scorer that would settle the dominance claim is T40. ! The plan closed at 25
          of 25 on that supersession, not on the work: what P5 asked for is unbuilt and
          now waits here, which is what a backlog is for.
          ! RENUMBERED ON MERGE, 2026-08-29 -- the pair is T43/T44 and the scorer is T40.
          T30, T31 and T28 were the 0.2.4 file's numbers, and this file's own task list
          already used all three
```

## Objective

**Nothing in this repo runs a case against this repo's own system.** `evals/` holds
`test-cases.jsonl` -- six cases, each a repo URL, a commit, a file list, a role, an outcome, a
stated `expected` and the `observed` run that produced it -- and `generator_split.py`. There is no
runner, no assertion mechanism and no score.

!! **AND THE OLD APPARATUS IS GONE, NOT BROKEN.** `evals/evals.json`, `evals/discriminators.md`
and the hazard grader are absent from the tree as of 2026-08-23. They were tied to a corpus this
repo cannot ship, so they went with it. **What that costs is the only mechanical scoring this
system had**, and rebuilding it by RESTATEMENT on a public corpus is T38 to T41.

! **AN EMPTY `git log` PROVES NOTHING HERE, AND NEITHER DOES A HASH.** The history was rewritten
on 2026-08-23, so absence is settled by looking on disk and by nothing else. The same rewrite
retired the hashes: of the commits the harness branch cites, `d96b10d`, `d3aa065` and `1ad4ba72`
resolve in this checkout and the rest do not. **Every pre-rewrite hash in a task has to be
re-located before its Verify can be run.**

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
finish. **The existing note should be corrected rather than deleted.**

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

! **So the reduced-set question is smaller than it looks: a ruling, an argument, and a line of
report.** It is not a re-architecture, and if N roles is a supported configuration then role
CASES stop being a test-only hack -- they are the same thing a user gets by asking for one.

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

! **So stage 5 at N=1 is not empty -- it is MIS-DESCRIBED**, and the hazard is an agent reading a
negotiation it does not have and inferring that a single uncorroborated finding needs less
scrutiny, in the one stage whose own text says a single-role run ratifies falsehoods.

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
public-history survey at T17 answers, and it stays separate -- not because it is less important,
but because it is not the same measurement and must not be reported as though it were.

! The two strong kinds need no network and no planting: the defect is at the parent, the fix is
the key, and both are commits on a branch that is already pushed.

## !! A CASE PINS TWO HASHES -- A START AND AN END

Amended 2026-08-23 by Roy: *"the evals need to have the start/end commits the intermediate
commits are not necessarily useful because each set of recommendations can take many commits to
implement properly. The goal would be to have this was the starting point and after the work is
done the comment-reviewers would have got it close to here."*

! **A single hash cannot name the answer key, because a fix is not a commit.** Measured
2026-08-23 on the 2026-08-16 hand pass: the fix is FOUR commits, so under the one-hash reading
there is no commit to point at -- picking any one of the four names a tree where some files are
corrected and others are not. A START and an END name it exactly, and the commits between them
stop mattering.

! **The two keys are `start` and `end`, not `base` and `fixed`** -- `decision-log.md
Vocabulary: #29`, because `base` already meant a planted hazard's unmodified text in
`grade_hazards.py` and a merge-base in `prove_unchanged.py`. ! The harness branch cited that
ruling as `Vocabulary: #10`, which on the current tree is *"Stage 2 is GATHER"*; the numbering
moved with the purge and the citation was re-derived.

!! **THE RULING SURVIVED ITS VEHICLE.** It landed by extending `evals/evals.json`, whose case 3
carried `start` and `end` beside `prompt`, `hazards` and `evidence`, with the file's own `notes`
stating *"a fixture is a checkout at a hash, and a fix commit is an answer key. A case that
carries `start`/`end` is graded over that RANGE."* **That file was removed on 2026-08-23**, and
the surviving row format, `evals/test-cases.jsonl`, pins a single `commit` -- so the shape the
amendment requires is on no row today. That is T15.

! **The superseded argument is kept so the error stays legible.** Before `evals.json` was
extended, a SECOND SUITE was ruled -- role cases and hash-pinned fixtures in their own layout,
because a case of `(address, hash, files, role)` had *"nowhere to put"* the hash in the
documented schema. Two new keys is where. The premise expired the same day the ruling was made.

! **And the assertion the amendment implies is APPROXIMATE, not identity.** *"got it close to
here"* -- the END tree is a target the run is scored against, not an output it must reproduce.
What counts as close is unruled, and is T31.

## !! THE RESULT IS TWO HALVES, AND ONLY ONE OF THEM IS A LETTER

Ruled 2026-08-23 by Roy: there is never going to be an oracle that can be exact, so an AGENT
grades the run A-F, the way an english language teacher rules that this was well done prose and
that was not. ! **Two halves and only one is subjective** -- the rules we HAND the reviewers are
objective and must pass; whether the prose reads well is a letter.

!! **AND THE CONFOUND IS NAMED**: what must NOT be measured is how good the python machinery
under all of this is. So a machinery defect VOIDS a case rather than grading the reviewer for it
-- T32.

! **Five things are checkable before the grader reads anything, and ALL FIVE HAVE ALREADY BEEN
WRONG IN THIS TREE** -- T33:

1. the round trip sets the START page back byte-identical
2. no address is held by two paragraphs (157 were)
3. every prose paragraph is censused exactly once
4. `record.py --check` passes
5. every citation resolves in the join

! **The objective floor is DERIVED, not written by hand** -- T34. Roy, 2026-08-23: we do know a
bunch of the rules that must pass because we tell the reviewers those. `vocabulary.py --reviewer
<role>` already emits the 42 to 46 terms one role is given, and several are rules with a
checkable failure: `laundering` forbids a `patch` on a claim that is false, `move` carries a
DESTINATION or it is not a `move`, and `clean` is wrong where the role did not READ the
paragraph and should be `query`.

! **The grader itself is a role, so it can reverse itself.** The END tree is the human answer
key, so the same grader on the same rubric must score it at the top; a grader that hands the
answer key a middling letter is what is broken, not the tree. That is `docs/gates.md` applied to
the grader -- could the check FAIL, not does it pass -- and it is T35.

## !! ONE VARIABLE PER RELEASE, AND THE BASELINE HAS TO BE RETAKEN

Ruled 2026-08-23 by Roy, recorded as `decision-log.md Process: #51` and `Process: #52`: a version
changes the AGENTS or the MACHINERY, never both, so a test can say whether the python tools got
better or the agent reviews did. ! **It does NOT hold retroactively** -- the current work changed
both -- so every score taken before it is uncomparable and the baseline has to be retaken.

!! **PREDICTION, not a ruling, and dated so it can be checked**: Roy expects the python side to
mostly resolve itself by being implemented and tested correctly, with the split becoming
usability rather than correctness AFTER 0.2.4 lands. If correctness defects are still the
majority after that, the prediction was wrong and the split needs re-arguing.

! **VOCABULARY TERMS CROSS THE SPLIT IN BOTH DIRECTIONS**, amended 2026-08-23 by Roy completing
Process #5: those items have to be kept in sync else vocabulary drift is a problem that several
pieces have missed and caused problems. So the `block` to `paragraph` rename arriving with a
machinery release was CORRECT, not a violation. `check_vocabulary.py` is the gate: 59 definitions
across 6 roles, 0 holes, 0 drifted, verified 2026-08-23.

!! **THE OLD AGENT WORKFLOW IS NOT A CHECKOUT OF THE OLD AGENT FILES.** Measured 2026-08-23,
`v0.2.3` to HEAD: the six agent files change by 29 insertions and 29 deletions, and that is TWO
things -- `block` renamed to `paragraph` (a declared synonym, harmless) and four PARALLEL
reviewers becoming three dispatched at stage 4c after `ownership-context` settles placement at
4a. Only the second is agent workflow. ! The real drift is elsewhere: `SKILL.md` and
`reviewer-brief.md` carry 626 insertions and 292 deletions between them, and `vocabulary.toml`
131. **So the patch has to be SELECTIVE** -- restore the old dispatch shape, keep the new
vocabulary -- or the baseline mixes the two variables the split exists to separate. That is T36
and T37, and Roy, 2026-08-23: the old results are conflated by the machinery more than how well
the agents did, so patch the agent workflow from the old into the new just to get the baseline.

## !! WHAT IS ACTUALLY ON DISK, MEASURED 2026-08-23

| fixture | where | state |
| --- | --- | --- |
| six cases with `expected` and `observed` | `evals/test-cases.jsonl` | present, no runner |
| the self-test commit range, all four roles | `evidence/self-test-commits.md` | present, never run |
| ten public corpora, materialised | `corpora/` and `corpora.toml` | present |
| the two `todo-tool` run packages | `evidence/` | **REMOVED 2026-08-23** |
| `redacted-corpus-full-v0_2/VERSIONS.md`, the pin | `evidence/` | **REMOVED 2026-08-23** |
| `findings.md`, Parts I-IV | `evidence/` | **REMOVED 2026-08-23** |
| `evals.json`, `discriminators.md` | `evals/` | **REMOVED 2026-08-23** |
| the twelve planted hazards and their grader | -- | **REMOVED 2026-08-23** |

!! **WHAT THE REMOVAL COST IS THE THIRD KIND OF CASE.** The `todo-tool` packages were the only
fixture whose SUBJECT was another repository, which is exactly the DISCOVERY axis our own commits
are weak on, and they carried what a synthetic case cannot: 171 prose paragraphs, four roles, and
a stage 8 that rolled a run back. **The replacement has to come from the public corpora, and that
is T17 and T38 to T41.**

! **WHAT THE `findings.md` PARTS I-III MEASUREMENT LEFT BEHIND.** Measured 2026-08-23 before the
removal: the Parts I-III commits did exist in the redacted corpus -- 42 subjects carrying
comment-review across 2026-08-11, found by searching the corrected TEXT rather than the messages
-- but **no clean repo-level pair exists.** The range that spans the burn-down holds 203 commits,
71 on first-parent and 109 touching `tests/`, against a burn-down of roughly 37, so around 160
commits of unrelated work sit inside it and an END tree scored against START would credit or
blame the reviewers for refactors they never saw. ! The candidate remedy was a PER-FILE pair,
since every entry cited a file. ! Part IV did not have this problem, which is what Roy meant by
almost every commit belongs in there. **The pins themselves are not restated here: they name a
private repository and went with the purge.** That is T30, and the discovery measurement falls
to T17.

! **PART IV IS ALREADY A START/END PAIR and needs no commit hunt** -- the branch
`fix/folio-placement-is-not-where-the-anchor-is`, 235 commits over five days, 198 files,
+56k/-5.4k. Roy, 2026-08-22: this branch is the manual review version of what it takes to get
this correct. ! Its recorded hashes are pre-rewrite and do not resolve in this checkout, so the
pair has to be re-derived from the branch. That is T29.

!! **A HARNESS MUST ASK THE REMOTE, NOT THE CLONE.** This survives the removal and is the most
reusable thing the exercise produced. The first durability reading came from
`git branch -r --contains <sha>`, which searches `refs/remotes` -- and the clone had never FETCHED
those branches, so there was nothing to find and two safe commits read as local-only.
`git ls-remote --heads origin` is the authoritative check. ! The failure is silent in the
direction that matters: a stale tracking ref says a durable fixture is at risk, and would equally
say a lost one is fine.

! **AND A CASE GRADES THE TREE AT THE HASH, NEVER A CONVENIENT LOCAL COPY.** The rule was
measured on the vendored `scripts/todo_tool.py`, which carries a local stdout-encoding patch and
was eight lines longer than the fixture it was mistaken for. ! A captured run's own line counts
are a record and are not corrected; anything keying on one re-derives it from the hash.

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
! Every other role's verdict PRESUPPOSES that ruling: a comment about `parse()` sitting above
`render()` is read against `render()`, found false, and CORRECTED into a falsehood -- so dropping
`ownership-context` leaves the remaining checks resting on an assumption nobody made, where
dropping any other removes a remit and nothing else. ! **`ownership-context` ALONE is therefore a
coherent run.** ! The upper bound is left OPEN deliberately -- `1..N`, not `1..4`. Roy,
2026-08-18: a fifth editorial role might be found, *"though the fact the editorial roles mimic
real-world roles makes me think it is unlikely."* The four are a copy desk; `compact` and
`review` are stages rather than members of the board.

! **WHAT SHIPPED FOR IT, 2026-08-18 in `d3aa065`** (T2). The agent file now reads *"the truth of
the ANCHORING, as against the truth of the ASSERTION -- the count, the bound, the worked example
-- which belongs to the other three"*, and its frontmatter carries the same sentence. Verified
2026-08-23 in `agents/comment-review-ownership-context.md`. It replaced *"You do not rule on
whether the claim is TRUE -- that is outside your remit. You rule on whether truth is assessable
here at all."* Roy, 2026-08-18: the assessability ruling IS a truth ruling -- it settles a
proposition about the statement's relation to the code, and that proposition can be false. ! It
matters beyond wording: the role that is never dropped should state its remit at full width, or a
reader deciding a set will under-rate it.

! **THE SCOPE IS THE PROJECT, RULED 2026-08-18 by Roy** (T3), shipped in `d3aa065`. The role file
asks whether the paragraph is about any specific piece of code or documentation IN THIS PROJECT,
and says so twice -- the second question itself, and *"the right place is anywhere in the
PROJECT, not only this file -- another module, or the documentation tree the run named"*. So
prose about nothing in the project is a `drop` and prose about something elsewhere in it is a
`move`, and the documentation tree stage 1.4 resolves is in scope. ! The question as it was put
was file-scoped (*"equally useful anywhere in the FILE"*); Roy states it wider, and the
difference decides a verdict.

! **AND BECAUSE `ownership-context` IS NEVER OPTIONAL** (T8), the "who governs instead" question
does not arise. The placement precedence stays as written; what T5 to T7 owe is saying that it
may assume its own presence.

! **A FIXTURE IS A CHECKOUT AT A HASH, RULED 2026-08-18 by Roy** (T12), and THIS REPO'S OWN
HISTORY is a valid source of them. Give the harness an address and a hash, check it out, focus on
the files for the test, drop everything after reporting. That answers "how much context do we
copy" by copying none -- the tree is real and complete. ! The mechanism ships: `corpora.toml`
supports a `local` corpus as a `git worktree` and a `public` one as a sparse clone at a tag, and
`scripts/fetch_corpora.py` builds both. ! The amendment that pins TWO hashes rather than one is
T13, and its own section is above.

! **WHAT THE REMOVALS SUPERSEDED.** (T20) "Add `assertions` to `evals/evals.json`" names a file
no longer in the tree, and the field it wanted exists under another name: every row of
`evals/test-cases.jsonl` carries `expected`, `observed` and `outcome`; what is missing is
something that READS them, which is T18 and T19. (T22) "Keep `grade_hazards.py` as the
verification SCRIPT" names a file that is not in this tree and is not coming back in that form --
the GUIDANCE it carried survives and belongs to T38 to T41: mechanical assertions belong in a
script rather than an LLM judge. (T26) "Parse the two `todo-tool` packages into cases" cannot be
done: both were removed from `evidence/` on 2026-08-23 with the corpus they described, and the
subject repository is private, so the discovery measurement falls to T17. (T14) "No second suite"
and (T30) "Tie `findings.md` Parts I-III to a pair" name files removed the same day.

! **THE FIRST ROLE CASE IS WRITTEN AND HAS ITS ANSWER KEY** (T23): `evals/test-cases.jsonl` row
`module-context-widens-a-two-subject-docstring`, role `module-context`, outcome `miss`, at
`d3aa0655b963`. Its `expected` is *"a `code_concerns` entry naming the split, and at most a
`query` on the summary line"*; its `observed` is the `patch` that widened the docstring to
announce both subjects -- the defect its own role file names as the trigger, applied as the
remedy. ! Its role file lists three triggers for a module announcing more than one subject and
never says what verdict one earns, while the same file does say a misplaced module constant is a
CODE CONCERN -- so the pattern exists and was not applied here. ! What is still missing is a
runner, which is T18 and T19, not a second case.

! **THE DURABILITY SCARE WAS MOOT, 2026-08-18** (T27): both subject commits were already on
`origin`. It was filed on a reading of `git branch -r --contains`, which searches only the
tracking refs this clone had fetched -- and it had fetched neither branch. What it leaves behind
is the rule stated above: ask the remote, not the clone.

! **`claude plugin eval` IS DECIDED, AND IT IS A FIT JUDGEMENT RATHER THAN AN AVAILABILITY ONE**
(T25). Decided 2026-08-23 by Roy: NO. *"the plugin/agent testing system was much more about
testing agents working on their own for corporations and routing things or making decisions.
This is supposed to be an isolated skill that reviews code bases and stays local -- which is much
closer to the skill tester setup requirements and doesn't cost money."* ! What it is, verified
2026-08-18 and re-verified 2026-08-23: separate, newer, CLI-driven -- `evals/**/case.yaml` or
`prompt.md` plus `graders/*.md`, `--ablation with-without`, `--json`, `--threshold`, built for
CI. `--help` works and lists the full option set; `plugin eval` and `eval init` both exit 1 with
*"currently in early access"*. No public documentation and no self-serve request route;
enablement is an organisation-level environment variable issued by Anthropic. **Availability
stopped being the question.**

! **WHAT `skill-creator` SUPPLIES, verified 2026-08-23**: it is installed, from
`claude-plugins-official` in `~/.claude/plugins/installed_plugins.json`, and gives this repo what
it has none of -- a subagent per case with clean context, a WITHOUT-SKILL baseline arm, and a
blind A/B between two skill versions. ! It ships `scripts/run_eval.py`,
`scripts/aggregate_benchmark.py`, `agents/grader.md`, `agents/analyzer.md`,
`agents/comparator.md` and `references/schemas.md` under its cache dir, and its SKILL.md section
*"Running and evaluating test cases"* is a five-step procedure that answers all four unknowns.

! **WHAT THE 2026-08-16 HAND PASS MEASURED.**
`the-shipped-python-does-not-pass-its-own-review.md` records the before and after -- `census.py`
55 negative-prose lines of 286 down to 2 of 206, and five more files -- so the defect is MEASURED
at the parent and MEASURED as fixed by the commit. ! It bears most directly on the claim that
file exists to make, because a human found those by hand and the question is whether the system
finds them. ! The pass is a RUN of four commits, not one, which is why a single `--grep` or `-S`
search kept landing on a fragment of it -- and the hashes recorded for it are pre-rewrite and no
longer resolve, so T24 has to re-locate them.

!! **AND THREE OF THAT FILE'S OWN HASHES NO LONGER RESOLVE.** MEASURED 2026-08-24 over every
hash in `evidence/self-test-commits.md`: `4286833`, `9293806` and **`7026646`** are gone, while
`d96b10d`, `4cb63f5`, `64ed7a4`, `7cbfa96`, `afeba7b` and `d09b0c1` still answer. `7026646` is
the END of the range below, so **the range as written cannot be checked out** and every Verify
resting on it is unrunnable until the end is re-located. ! They died in the 2026-08-23 history
rewrite, not in any edit to the file -- which is why nothing flagged them: a stale hash reads
exactly like a good one until someone runs it. T42 tracks the repair.

! **WHAT THE SELF-TEST RANGE HOLDS.** `evidence/self-test-commits.md` pins `d96b10d..7026646` on
the branch `fix/folio-placement-is-not-where-the-anchor-is`, with cases written up for ALL FOUR
roles -- five `module-context`, plus `function-context`, `block-context` and `ownership-context`
sections. Each is a PROSE defect a person found by reading, with the fix commit as its answer
key, and **not one broke a test**: the suite was green through all of them, 672 to 713 passing.
That file's own closing section says so: *"None of these was found by `/comment-review`."*
! Roy, 2026-08-20: *"put the commit range in the evidence files or wherever we can remember that
these specific commits are good test cases for the system to test itself against."* ! The range
was once recorded as twenty-one commits; corrected 2026-08-20, the useful ones are the modules
whose docstring announced one subject while the module held several, and the file on disk names
the range above. ! It also records what is NOT a case -- a false plan tick, an `expectedFailure`
firing, a hand-written fixture, which Roy, 2026-08-20, called *"specifically not useful test
cases for comment-review"* because they are process defects this system has no remit over.

! **WHY TWO OF THE TWELVE HAZARDS NEED A REFUSAL RATHER THAN A CLEAN.** Two were positional or
left true prose standing, so no text probe separated a correct repair from an ignored one; those
reported NEEDS-EYES, and the replacement owes the same refusal.

## !! P5 CAME HERE 2026-08-24, AND IT IS THE PAGE'S OWN PASS CRITERION

Roy, 2026-08-24: *"supersede P5 to that todo because it is testing's work anyways."* It was the
last open box on the `0.2.4-rework-the-foliator-owns-the-address` plan, and it could not be
worked there: **both of its halves are missing an instrument, and both instruments are this
file's.** T43 and T44 carry it.

! **NAMED, NOT LINKED, AND THAT IS THE RULE.** A `T` takes no dependency on a `P` -- see
`docs/conventions.md`, *T, P and SP*. What arrived here is the WORK; the plan that used to hold
it can be deleted tomorrow and T43 and T44 stay answerable, which is the test.

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
reader can find it**, which is T43.

! **T44 IS DOWNSTREAM OF THE SCORER**, T40: a hand-run comparison is the thing this file exists
to end, so the dominance claim waits on something that can disagree with it.

## !! THE GRADED FIELD IS `expectations`, AND `assertions` IS READ BY NOTHING

**MEASURED 2026-08-29 over the marketplace copy of `skill-creator`**, which is what P-A2 asked
for. The two names looked like a disagreement between Anthropic's own docs. They are not a
disagreement, and they do not split input from output: **every SCHEMA says `expectations` and
only the PROSE says `assertions`.**

| name | read from | by |
| --- | --- | --- |
| `expectations` | `grading.json` | `scripts/aggregate_benchmark.py:157`, `:161`, `:252` |
| `expectations` | `evals.json`, as `evals[].expectations` | `references/schemas.md:20`, `:35` |
| `expectations` | the grader's input, and its output | `agents/grader.md:15`, `:112`, `:188` |
| `expectations` | the comparator's input | `agents/comparator.md:18` |
| `assertions` | **nothing** | -- |

!! **AND THE ONE PLACE `assertions` LOOKS MACHINE-FACING IS NOT.** `SKILL.md:195` shows
`"assertions": []` inside an `eval_metadata.json`. The only script that opens that file is
`aggregate_benchmark.py:87-91`, which takes `eval_id` and falls back to the directory name when
it is missing. **Nothing else is read out of it.**

! **SO THE FAILURE MODE IS SILENT, WHICH IS WHY THE BOX CAME BEFORE ANY CASE WAS WRITTEN.** A
case spelling the field `assertions` is accepted, graded against an empty list, and reports zero
expectations -- a green run that asked nothing. That is `docs/gates.md`'s question exactly:
not *does the check pass* but *could the check fail*.

! **`expected`, `observed` and `outcome` ARE OURS AND DO NOT MOVE.** All six
`evals/test-cases.jsonl` rows carry them, and they describe the KNOWN DEFECT -- the answer key a
case is built from. `expectations` is the list a grader rules on. Two artifacts, two owners; the
earlier reading of T20 conflated them.

## Tasks

- [x] T1 -- RULED 2026-08-18 by Roy: a reduced set is SUPPORTED and `ownership-context` is
      NON-NEGOTIABLE. Verify: the legal sets are stated in the Objective.
- [x] T2 -- FINISHED 2026-08-18 in `d3aa065`: the ANCHORING-against-ASSERTION sentence
      ships. Verify: it is in `agents/comment-review-ownership-context.md`.
- [x] T3 -- RULED 2026-08-18 by Roy: the scope is the PROJECT, shipped in `d3aa065`.
      Verify: the role file asks about code or documentation in this project.
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
      own history is a source. Verify: `scripts/fetch_corpora.py` builds both kinds.
- [x] T13 -- AMENDED 2026-08-23 by Roy: a case pins a START and an END hash, not one, and
      the commits between them do not matter. Verify: the ruling is in the Objective.
- [x] T14 -- SUPERSEDED: the NO-SECOND-SUITE resolution landed in `evals/evals.json`,
      removed 2026-08-23; the `start`/`end` naming survives it. Verify: `ls evals/`.
- [ ] T15 -- Carry `start` and `end` onto `evals/test-cases.jsonl` rows, which today pin
      one `commit`. Verify: every row naming a range carries both keys.
- [ ] T16 -- Answer how much context an extracted case copies, given the packet's
      REFERENCE ONLY files. Verify: re-run a case without them, compare verdicts.
- [ ] T17 -- Survey public histories for a commit whose prose and code disagree, and its
      later fix. Verify: one such pair is a row in `evals/test-cases.jsonl`.
- [ ] T18 -- * Rule what executes a `test-cases.jsonl` row: a script in this repo or
      `skill-creator`. Verify: the answer is written into this file.
- [ ] T19 -- Build that runner. Verify: one command runs one row by `id` and exits nonzero
      on a miss.
- [x] T20 -- SUPERSEDED: `evals/evals.json` is gone, so a field cannot be added to it.
      ! Its second clause was WRONG and is corrected 2026-08-29 -- see the note below.
- [ ] T21 -- Run the six `evals/test-cases.jsonl` cases through `skill-creator`. Verify: a
      `benchmark.json` exists and reports a delta; today none does.
- [x] T22 -- SUPERSEDED: `grade_hazards.py` is not in this tree and is not returning in
      that form; the guidance it carried belongs to T38 to T41. Verify: `ls evals/`.
- [x] T23 -- FINISHED: the first role case is `evals/test-cases.jsonl` row
      `module-context-widens-a-two-subject-docstring`. Verify: the row carries `expected`.
- [ ] T24 -- Make the parent of the 2026-08-16 hand pass a case; its recorded hashes are
      pre-rewrite. Verify: a row pins a parent commit `git rev-parse` resolves.
- [x] T25 -- DECIDED 2026-08-23 by Roy: NO, we do not want `claude plugin eval`, and its
      access is not worth asking for. Verify: the reason is in the Objective.
- [x] T26 -- SUPERSEDED: both `todo-tool` packages were removed 2026-08-23 and the subject
      repo is private, so the DISCOVERY measurement falls to T17. Verify: `ls evidence/`.
- [x] T27 -- MOOT 2026-08-18: both subject commits were already on `origin`. Verify: the
      rule it leaves -- ask the remote, not the clone -- is in the Objective.
- [ ] T28 -- Run `/comment-review` over the self-test range `d96b10d..7026646`. Verify:
      one row has a run, with its verdicts beside the answer-key diff.
- [ ] T29 -- Write the Part IV case, on the branch named in the Objective, from its START
      hash to its END hash. Verify: the case pins two hashes `git rev-parse` resolves.
- [x] T30 -- SUPERSEDED: `evidence/findings.md` was removed with the corpus it described,
      so Parts I-III cannot become cases and that falls to T17. Verify: `ls evidence/`.
- [ ] T31 -- * Rule what CLOSE TO HERE measures, since a START/END case scores against a
      target tree. Verify: the rule names an artifact, a unit and a threshold.
- [ ] T32 -- Split every case result in two -- MACHINERY pass-or-void and EDITORIAL A-F.
      Verify: a machinery defect reports VOID and never reaches the grader.
- [ ] T33 -- Make the five machinery checks in the Objective the void gate, run before the
      grader. Verify: failing any one reports VOID and files a machinery defect.
- [ ] T34 -- Derive the rubric's must-pass floor from `vocabulary.py --reviewer <role>`.
      Verify: every item cites an emitted term and `check_vocabulary.py` still passes.
- [ ] T35 -- Calibrate the grader against the END tree, which is the human answer key.
      Verify: the END tree scores at the top and its letter is recorded beside each run.
- [ ] T36 -- Patch the `v0.2.3` dispatch shape onto HEAD's machinery, keeping the new
      vocabulary. Verify: the diff touches dispatch only and `check_vocabulary.py` passes.
- [ ] T37 -- Run that patched set and record its score as the baseline. Verify: the record
      names which agent files came from which ref, and that the machinery is HEAD.
- [ ] T38 -- Restate the twelve hazards, each named precisely enough to score without the
      code it was found in. Verify: twelve restatements, none quoting.
- [ ] T39 -- Plant the restated set on a corpus `corpora/corpora.toml` materialises.
      Verify: the base is a manifest row rather than a hardcoded path.
- [ ] T40 -- Write the scorer for the restated set. Verify: one script scores a worktree
      against the twelve and exits nonzero on a miss.
- [ ] T41 -- Make the two hazards no text probe separates report NEEDS-EYES rather than a
      pass. Verify: scoring a worktree that ignored either returns NEEDS-EYES.
- [ ] T42 -- Re-locate the three hashes in `evidence/self-test-commits.md` the 2026-08-23
      rewrite killed. Verify: every hash in that file resolves with `git cat-file -e`.
- [ ] T43 -- Recover the v0.1.0-vs-v0.2.0 recall figure into `evidence/`, or record it
      lost. Verify: a reader finds it without reading a run transcript.
- [ ] T44 -- Score the page against BOTH prior formats, on the dominance criterion.
      Verify: more info than filtered, fewer tokens than unfiltered, recall >= filtered.
- [x] T45 -- Lay a DECLARED `variant` over a snapshot, so a run names the theory
      it scored. Verify: `verify` returns [] for the declared path and still names
      an undeclared change beside it.
- [x] T46 -- `reset` returns the rig to its ref between theories. Verify: a file
      the variant ADDED is gone, and the reset manifest equals the base.
- [ ] T47 -- The aggregator's delta reads BACKWARDS for an improve-mode run. It is
      first-minus-second in sorted config order, and `skill-creator` prescribes
      `old_skill` for the baseline, which sorts BEFORE `with_skill`. Measured
      2026-08-29: 40% vs 80% reported as `Delta: -0.40`. Verify: a run where the
      newer arm scores higher reports a POSITIVE pass_rate delta.
- [ ] T48 -- Say in the harness's own notes which arm name goes on which side,
      whatever T47 lands on. Verify: the rule is written where a run is set up,
      not only in a result.

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
