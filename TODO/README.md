# TODO -- open tasks and pending decisions

One file per task. **A TODO is a work order, not an essay** -- a header, a short Objective, and
checkboxes. Everything that is not the objective or a task is documentation, and the routing turns
on **whose behavior it describes**:

| the content | home |
| --- | --- |
| how **this system** behaves today, and any survey of it | [`docs/`](../docs/) |
| a prose defect in **someone else's codebase**, which this system is measured against | [`evidence/`](../evidence/) |

! **Those first two read alike and are not.** `evidence/` is the labeled failures the tool is
scored on -- probe reports over a real codebase, the triage over them, `ga/ground_truth.py`.
A measurement of **the tool's own** prose is `docs/`, however much it looks like a finding. The
vocabulary survey was filed under `evidence/` once for exactly that reason and moved.

The TODO keeps a one-line link from its Objective and nothing else. If nobody would read it
again, delete it -- a TODO is not an archive.

**File names are kebab-case and say the thing, not the category.**
`eight-terms-have-no-definition-and-angle-means-five-things.md`, not `vocabulary-cleanup.md`. The
name is what shows in the table below, so it does the work of a summary.

**The BOXES are the source of truth; `Progress:` is Roy's read-out and is what he assigns work
from.** Tick the box and bump the count **in the same edit, every time** -- and the `N/M` cell in
the table below with it. A stale-low count does not look untidy; it manufactures a wrong
instruction, because he asks for work already done and the session burns context discovering that.

! **`scripts/todo_tool.py` checks that arithmetic, which is why the counts are not written by
hand.** Every command recomputes `Progress:` and this table's `N/M` cell from the boxes it just
wrote, and `resync` repairs drift after a merge.

! **It REFUSES rather than guessing when the two disagree.** MEASURED 2026-08-23: a README row
whose file is no longer in `TODO/` stops `resync` with the mismatch named, and it fixes nothing
else in that run. Removing the row by hand and re-running is what recomputes the section count --
`### decision-needed (6) -> (5)`.

**`completed/`** will hold finished work when there is any, kept as the record. A file named
`*-SUPERSEDED.md` was **not implemented and is no longer necessary** -- the reason goes in the file.

**Status values in use here:**

| value | means |
| --- | --- |
| `open` | nobody has started it |
| `in-progress` | work has genuinely started -- some boxes ticked, not blocked, not waiting on a decision |
| `decision-needed` | waiting on Roy; the file names what he has to rule on |
| `blocked` | the task is real, it is not done, and doing it now is wrong because a named change must land first. The `Status:` line names what it waits on |
| `done` | every box ticked; the file moves to `completed/` |

**Owner** is `Roy` or `session`. This repo has no lane split -- there is one codebase and one
shipped plugin, so the only distinction that changes what happens next is whether a task needs a
ruling or needs typing. A file may name both.

---

## The TODO file template

There is no `conventions.md` here, so this is the one definition.

````markdown
# {Title -- the task, and the one thing that makes it matter}

```
Status:   open | in-progress | decision-needed | blocked (on what) | done
Progress: {done} of {total} tasks done
Owner:    session | Roy | both (say which tasks)
Raised:   YYYY-MM-DD (where it came from)
```

## Objective

{Two to six sentences. What has to become true, and why -- the CONCLUSION the evidence
already reached, not the evidence. One link out if a reader needs the working.}

## Tasks

- [ ] {one action, and you can tell by looking whether it is done}
- [x] {done YYYY-MM-DD -- `commit`, plus one clause only if the outcome changed the plan}
````

Rules that keep it that shape:

- **The Objective is prose and it is short.** Growing tables or headings means it has become a
  document; split it out to its home in the table above and link it.
- **A task is checkable or it is not a task.** "Clean up the vocabulary" is a project; the
  checkbox names the file, the grep that must come back empty, or the ruling that must exist.
- **The checkboxes ARE the record -- no `## Response` section.** Tick with a date; the header's
  status summarizes the boxes.
- *** marks a task that needs Roy before anyone can act on it**, so the ones that gate the rest
  are visible without reading the file.
- Same reason as this repo's own rule against unfalsifiable prose: a task you must re-read the
  evidence document to act on has deferred the decision to the moment of least willpower.

---

## What to do next -- re-derived 2026-08-16, fourth pass

!! **SETTLE WHAT A TERM MEANS. DO NOT MOVE IT.** Roy, 2026-08-16: *"once we get the vocabulary
resolved we will fix how to get the vocabulary to the correct places for each of the agents to
use."* Distribution is its own pass and it has NOT run. Until it does, state a term **in place**
-- in a sentence that already describes it -- and record a placement problem as an OBSERVATION.

! **Re-derive this after anything lands.** Written fresh each time, not accumulated -- a stale
branch status here is the same failure the box/`Progress`/table rule guards against, one level up.

Everything below is on `feat/settle-the-vocabulary`, 52 commits, `main` untouched.

**The vocabulary is CLOSED.** `python scripts/check_vocabulary.py` says so as a command rather
than a claim: 185 inventory rows, 0 without a ruling; 1590 citations, 0 broken. Every term is
defined, dropped, or declared as deliberate polysemy.

1. **0.1.3 IS CUT AND THE BRANCH DELIBERATELY DOES NOT LAND.** Roy, 2026-08-16: *"do not land --
   the implications of the changes need to be worked through."* `main` is still 0.1.2. ! The
   version is in `CHANGELOG.md` and nowhere else, and the PATCH number moves whatever the change
   -- *"these will continue to be bugfix versions"* -- so a release carrying breaking renames is
   still `0.1.x`. Do not "correct" the next one to `0.2.0`.
2. *** DISTRIBUTION is the next pass, and it is now DESIGNED rather than open.**
   [`the-task-agent-emits-the-vocabulary`](completed/the-task-agent-emits-the-vocabulary.md) -- a script
   prints the definitions an agent needs and the task agent puts them in that agent's prompt
   verbatim. Four alternatives were considered and rejected; the one that decides it is that
   only this shape has no paraphrasing step. ! Its hardest task is not the script: it is
   REMOVING the in-place statements the emitted block replaces, several of which are a clause
   inside a sentence that has to survive losing it.
3. **The metaphor is now a rule in `CLAUDE.md`, and it earned itself twice.** `walk` and
   `detector` both collided with nothing and both went, because an editor does not walk a page
   and a detector is instrumentation. No collision check would have found either.
4. **! The survey is a floor, not a census -- still true.** `budget` and `own` were missed by
   twelve agents and found by Roy reading. The re-sweep is now a script
   (`scripts/vocabulary_sweep.py`), and its own limits are stated: it sweeps `plugins/` only, and
   it cannot catch a term used consistently in ONE file or one whose two senses are both prose.
   `angle` would not have been caught by it.
5. **! THE LEVEL LADDER HAS NO PROVENANCE and is now filed**, after this status rewrite lost it
   once: [`the-level-ladder-was-invented-during-the-port`](completed/the-level-ladder-was-invented-during-the-port.md).
   `git log -S` puts it at ZERO commits in `redacted_corpus` on any branch.
6. **The rest are filed and none blocks another** -- the pCST rebuild, the finding record, the
   author/page ordering, the shipped Python's own comments, the harness sweep, the two lists'
   entries, the unit-of-review contradiction, and returning a coverage gap to the reviewer.

**Landed 2026-08-15 on `main`:** 0.1.2 (`5975890`) -- the four reviewer agents renamed for scope,
each stating what its own `clean` asserts, and the placement precedence. Then `648bf72`, the
vocabulary survey.

**The rulings on `feat/settle-the-vocabulary`** -- 52 commits in all; the table lists the ones
that changed a published name or rule:

| commit | what |
| --- | --- |
| `e09c53d` | `sweep` retired (7b is APPLY), `angle` retired (editorial role / reviewer), eight facts reconciled |
| `94983c8` | `reanchor` collapsed into `move` -- eight verdicts, availability and synthesis order key on the destination |
| `d36d9f3` -> `f879767` | `budget` settled, then **corrected**: it is what a shipped file costs to load, not the reviewer's runtime |
| `0548daa` | reviewers no longer receive `CAP` or `WIDTH` -- the packet gate had been enforcing the opposite of the stated rule |
| `3c858b0` | stage 5 is APPLY, stage 7b is WRITE |
| `4e8393e` | a block is the interval between two lines of CODE |
| `adf8258` | the census's `marks` are `annotations`; `mark` is editorial |
| `a245b28` -> `7559969` | 7b's gate is the CODE CHECK, and it proves the parser reads the file the same -- not byte identity |
| `7930810` -> `58462fd` | `DOC CONVENTION` settled -- stage 1.3 MEASURES the repo's formats instead of naming a standard |
| `16a95c2` | `HOME` retired; **owner** is the anchor with the best justification, and `Block.owner` became `Block.anchor` |
| `6c19fd5` -> `913fa31` | a role's categories of claim get their own word -- **`remit`**, after `jurisdiction` failed the register |
| `beb5bfb` -> `211bfa7` | absence left `ownership-context` -- missing documentation is `module-context`'s or `function-context`'s, by scope |
| `ec7523a` | `worktree` settled: git's word, not a term of art here |
| `ed7ef8a` | nothing gets suppressed -- `NOISE_FLOOR` deleted from `referrers.py` |
| `7c976cf` | the exemptions-off rule deleted -- a second harness leak |
| `1090e7c` -> `7c5877f` | the acquittal and suppression lists deleted; the no-excuse rule restored in `clean`'s own section |
| `1c66af4` | the CODE CHECK compares a **`stripped`** text; `residue` is the prose check alone |
| `ede42f7` -> `da303c7` | stage 8 REVIEW is all-encompassing, never edits, and names nothing outside itself |
| `b228e8a` | `statement` / `expression` / `declaration` / `assignment` name CODE; `signature` -> `fingerprint` |
| `40398c9` -> `9a5c310` | the re-sweep, and its six ruled -- `walk` retired, a surface gap is an **OMISSION** |
| `9ad9c44` -> `fb7e7f5` | `template` and `original` stated; `detector` dropped -- every inventory row now carries a ruling |
| `1db014a` -> `c347230` | `scripts/check_vocabulary.py` -- every term ruled and every citation live, as a command |

167 tests pass, `ruff check` clean, 5 shipped files parse on 3.9, `check_vocabulary.py` exits 0.

## Open

### open  (84)

| file | owner | roy? | done | what |
| --- | --- | :-: | ---: | --- |
| [the-census-is-mostly-intervals-nobody-rules-on](the-census-is-mostly-intervals-nobody-rules-on.md) | backend · Roy | — | 2/20 | **The census is 67% of what it costs to start a reviewer, and 966 of its 1,120 blocks are intervals nobody rules on.** 131,353 bytes of 195,243, paid four times. Roy ruled the design 2026-08-18: the census stays fully enumerated ON DISK, the agents get a FILTERED view, and a destination outside their set comes from a TOOL answering one question -- what is the ADDRESS of this line of code. ! It does not reverse the 2026-08-17 enumeration; it is a projection of it, and `add` was not expressible before it. ! Rule 4 buys a check as well as bytes: `move`'s `to` is free text nothing resolves, and an index is resolvable exactly as an address already is |
| [the-harness-cannot-run-the-system-it-grades](the-harness-cannot-run-the-system-it-grades.md) | testing | yes | 6/22 | **Nothing in this repo runs the documented eval format, and no measurement exists that a human did not perform.** `grade_hazards.py` scores worktrees a person built by hand against twelve planted defects, from a base hardcoded to another repository. Ruled 2026-08-18: a reduced role set is supported with `ownership-context` never dropped, and a fixture is a CHECKOUT AT A HASH -- this repo's own history included, since a fix commit is an answer key. ! NOT a release candidate: nothing here is under `plugins/`. * Unruled: the suite layout, which the fixture model narrows to one option |
| [a-coverage-gap-should-go-back-to-the-reviewer](a-coverage-gap-should-go-back-to-the-reviewer.md) | agents | yes | 0/6 | **A block a reviewer never accounted for is unfinished work, not a finding about the run.** Today `verdicts.py` prints a COVERAGE GAP against the role by name and exits nonzero. Roy, 2026-08-16: *"if comment blocks are missed by a reviewer then they are returned to the reviewer to rule on."* ! Same shape as the two deleted lists one level up -- the reviewer stopped early, and the system files the stopping rather than fixing it. * Unruled: re-dispatch with only the missed indices or the whole census, and what bounds the retry |
| [the-two-lists-were-tuned-to-one-diff](the-two-lists-were-tuned-to-one-diff.md) | agents | yes | 2/7 | **Both lists are DELETED from the brief; this holds what was inside them.** The acquittal list matched a prose SHAPE and claimed to be *"the ONLY reasons to pass a block over"* -- but what decides `clean` is stated per role and is a TRUTH assertion at that role's scope, so the two disagreed outright. Its measurement was `evidence/ga/`: ten candidates over SIX `redacted_pkg` files, scored on F1 against what one later commit rewrote -- and the search itself concluded *"the acquittal RATE is the trait; the acquittal LIST is just vocabulary."* The suppression list had no provenance at all. ! Three entries were CHECKS wearing an exemption's name, one CONTRADICTS `function-context`, and `detector` -- a settled term -- lost its only definition |
| [the-author-approves-blocks-and-never-sees-the-page](the-author-approves-blocks-and-never-sees-the-page.md) | agents | yes | 1/9 | * **Pipeline, not vocabulary.** 7a shows the author a per-block LIST; stage 8 is the only pass that reads the PAGE, and it runs AFTER 7b has written to disk. So every defect `review.md` exists to catch -- a block that is no longer a proposition, two runs merged across a blank line, the same sentence in two places -- is found after approval and after the write. Roy wants a whole-document read BEFORE the person sees it, and floated a temporary branch with the diff so they can accept it in git's own tools. Stage 8 then becomes a verification with two outcomes: good, or raise to human as a new review. ! Already done: the 7b paragraph claiming *"this pass cuts, and it can cut a lot"* is deleted -- self-contradicting since the import |
| [the-shipped-python-does-not-pass-its-own-review](the-shipped-python-does-not-pass-its-own-review.md) | backend | yes | 7/9 | **Our own scripts spend a sixth of their prose on what the code does NOT do.** ! **Roy's reason, 2026-08-16: *"I don't want the system picking up bad cues from the documentation in the code."*** An agent reads these files and then writes in them. Re-measured after that day's rewrites: **136 of 697 (20%)** comment and docstring lines carry `cannot` / `never` / `does not` / `is not` / `nothing` -- UP from 123/714, because the prose written that day carries the same defect -- `census.py` worst at 52/284. Roy: *"census.py creates the pCST and that is it. Comments about 'cannot answer OWNERSHIP' are not helpful."* ! Not every negative is wrong -- an output (*"reports UNPROVABLE rather than passing"*) and a refusal aimed at a future editor both earn their place -- so the first task is writing the test that tells them apart !! **The hand-pass rule is STRUCK, 2026-08-18.** It told itself not to run `/comment-review` on this repo; Roy: *"By definition the code has to go through the review to state that it has passed."* A hand pass produces a rewrite, and this file's title is a claim about what the review RETURNS -- so it now closes on a run graded from the diff. ! The harness does not gate that: running the skill needs the skill |
| [7a-can-prove-the-change-by-applying-it-to-a-copy](7a-can-prove-the-change-by-applying-it-to-a-copy.md) | agents · Roy | — | 2/5 | 7a can PROVE the change by applying it to a copy and diffing |
| [a-block-does-not-say-where-its-text-starts](a-block-does-not-say-where-its-text-starts.md) | backend | yes | 7/10 | A block does not say where its text starts, so two things infer it |
| [a-comment-inside-a-line-makes-the-file-unprovable](a-comment-inside-a-line-makes-the-file-unprovable.md) | backend · Roy | — | 1/5 | A comment INSIDE a line makes the whole file unprovable |
| [a-prose-file-has-no-blocks](a-prose-file-has-no-blocks.md) | backend | yes | 0/9 | A prose file has no blocks, so the system cannot review documentation |
| [a-role-can-reverse-itself-between-runs](a-role-can-reverse-itself-between-runs.md) | agents | yes | 0/6 | A role can reverse itself between runs, and nothing measures it |
| [a-scope-declaration-costs-as-much-as-a-finding](a-scope-declaration-costs-as-much-as-a-finding.md) | agents | yes | 0/4 | A scope declaration costs as much as a finding |
| [block-comment-markers-survive-into-the-prose](block-comment-markers-survive-into-the-prose.md) | backend | yes | 0/6 | Block-comment markers survive into the prose the reviewers read |
| [correcting-one-copy-strands-the-reference-copy](correcting-one-copy-strands-the-reference-copy.md) | agents | yes | 0/6 | Correcting one copy strands the copy in a REFERENCE ONLY file |
| [move-and-correct-compose](move-and-correct-compose.md) | agents · Roy | — | 4/5 | `move` and `correct` COMPOSE, and the gate calls them a contradiction |
| [nothing-checks-that-four-reviewers-were-launched](nothing-checks-that-four-reviewers-were-launched.md) | agents | yes | 1/5 | Nothing checks that four reviewers were LAUNCHED |
| [only-census-got-out-and-the-skill-instructs-a-redirect](only-census-got-out-and-the-skill-instructs-a-redirect.md) | agents | — | 0/4 | Only `census.py` got `--out`, and `SKILL.md` instructs the redirect it forbids |
| [ownership-is-read-first-but-nothing-makes-it-so](ownership-is-read-first-but-nothing-makes-it-so.md) | agents | — | 3/10 | `ownership-context` is read FIRST, and nothing in the run makes that true |
| [reference-only-misses-the-documentation](reference-only-misses-the-documentation.md) | agents | yes | 0/4 | REFERENCE ONLY misses the project's own documentation |
| [referrers-matches-on-any-public-name-and-surfaces-the-whole-repo](referrers-matches-on-any-public-name-and-surfaces-the-whole-repo.md) | backend | yes | 0/5 | `referrers.py` matches on any public name, and surfaced the whole repo |
| [stage-5-is-the-only-stage-with-no-independent-reader](stage-5-is-the-only-stage-with-no-independent-reader.md) | agents · Roy | — | 1/9 | Stage 5 is the only stage whose writer is also its checker |
| [the-code-check-refuses-add-and-drop-on-a-docstring](the-code-check-refuses-add-and-drop-on-a-docstring.md) | backend | yes | 0/5 | The CODE CHECK refuses `add` and `drop` when the prose is a docstring |
| [the-emitted-vocabulary-can-collide-with-the-repo](the-emitted-vocabulary-can-collide-with-the-repo.md) | agents | yes | 0/4 | The emitted vocabulary can collide with the reviewed repo's own terms |
| [the-parser-merges-across-boundaries-it-cannot-read](the-parser-merges-across-boundaries-it-cannot-read.md) | backend | yes | 0/4 | The join merges across a boundary it cannot read, and blames the neighbour |
| [the-read-only-contract-is-enforced-by-nothing](the-read-only-contract-is-enforced-by-nothing.md) | agents | yes | 0/6 | The read-only contract is enforced by nothing, and four reviewers wrote files |
| [the-strongest-precedence-has-the-weakest-support](the-strongest-precedence-has-the-weakest-support.md) | agents | yes | 0/5 | The role with verdict precedence has the least mechanical support |
| [two-live-runs-proposed-fifteen-changes](two-live-runs-proposed-fifteen-changes.md) | agents | yes | 5/16 | Two live runs proposed fifteen changes |
| [doc-is-structural-means-two-things](doc-is-structural-means-two-things.md) | backend | — | 0/2 | doc_is_structural means two things and its docstring names one |
| [docstrings-need-their-own-address-series](docstrings-need-their-own-address-series.md) | backend · Roy | — | 5/7 | A docstring needs its own address series, and it names what it documents |
| [false-by-arithmetic-with-no-enforcing-line](false-by-arithmetic-with-no-enforcing-line.md) | agents | yes | 0/3 | A claim can be false by arithmetic with no enforcing line to check it against |
| [line-0-places-are-unreachable](line-0-places-are-unreachable.md) | backend | — | 4/5 | **An empty place sits at line 0 by ruling, and both tools that answer by LINE filter on `start &lt;= line &lt;= end`.** So the places an `add` exists to cite are the ones no line lookup can name -- while the brief forbids the only remaining route, counting. |
| [census-degrades-silently](census-degrades-silently.md) | backend | — | 1/8 | **Four inputs produce a census that is wrong rather than refused, each exiting 0.** The run reads as complete and the addresses are nonsense. |
| [b-addresser-uninitialised](b-addresser-uninitialised.md) | backend | — | 9/17 | The b addresser is never initialised at the module trigger, and computes its cue from line numbers |
| [census-owns-addressing](census-owns-addressing.md) | backend | — | 4/5 | The census owns addressing, and four modules share one subject between them |
| [filtered-measurement-unrecorded](filtered-measurement-unrecorded.md) | testing | — | 1/5 | The filtered-census measurement exists only in run history |
| [doc-does-not-fill-its-a](doc-does-not-fill-its-a.md) | backend | — | 0/5 | the a place now exists for Rust/Go/etc but the doc that fills it still sits at b |
| [b-owns-the-blank-lines](b-owns-the-blank-lines.md) | backend | — | 10/12 | b must own a gap's blank lines on the ORIGINAL range, not just the addressing one |
| [front-matter-absorbed-by-an-interval](front-matter-absorbed-by-an-interval.md) | backend | yes | 5/6 | an interval owns the licence header and the module docstring; an add on it destroys them |
| [vocabulary-gate-is-red](vocabulary-gate-is-red.md) | systems | — | 1/4 | check_vocabulary exits 1 on this branch and no test asserts check_drift |
| [stage-4b-is-undefined](stage-4b-is-undefined.md) | agents | yes | 0/5 | the 4a/4c split promises a resolved placement that nothing produces |
| [six-mutations-survive-the-suite](six-mutations-survive-the-suite.md) | testing | — | 1/6 | 720 tests green against six deliberate defects in shipped code |
| [the-xfails-never-reach-the-galley](the-xfails-never-reach-the-galley.md) | testing | — | 0/3 | they fail in the test helper on a retired lookup, not in splice_range |
| [the-rename-corrupted-live-prose](the-rename-corrupted-live-prose.md) | backend | — | 0/5 | a blanket word swap turned verbs and a role name into nonsense |
| [the-anchor-claims-are-inverted](the-anchor-claims-are-inverted.md) | agents | — | 0/2 | shipped prose says an anchor is often empty; it is never empty |
| [docstrings-that-contradict-themselves](docstrings-that-contradict-themselves.md) | backend | — | 0/6 | each states a rule and then denies it, in the same file |
| [stale-measurements-in-shipped-prose](stale-measurements-in-shipped-prose.md) | backend | — | 0/6 | every one re-derivable by a command, and every one wrong |
| [assertions-that-gate-a-substring](assertions-that-gate-a-substring.md) | testing | — | 0/10 | each passes in the buggy state its own comment forbids |
| [a-code-less-file-leaves-lines-unowned](a-code-less-file-leaves-lines-unowned.md) | backend | — | 0/3 | the same one-address-per-line invariant, on a file with no code |
| [move-across-an-uncued-file](move-across-an-uncued-file.md) | backend | — | 4/6 | the address form spans files; the census does not |
| [closing-line-deletes-code](closing-line-deletes-code.md) | backend | — | 0/6 | An edit to a comment whose run closes mid-line DELETES the code after the closer |
| [versioning-at-v1](versioning-at-v1.md) | systems · Roy | — | 0/4 | v1.x wants a concrete versioning system on everything that ships |
| [check-passes-a-shared-address](check-passes-a-shared-address.md) | backend | — | 0/3 | addresser --check prints SHARED and exits 0 |
| [a-series-never-fills-outside-python](a-series-never-fills-outside-python.md) | backend | yes | 0/17 | Outside Python the `a` place is emitted and never filled |
| [bom-is-read-as-source](bom-is-read-as-source.md) | backend | — | 0/3 | A UTF-8 BOM is censused as a line of code |
| [strip-strings-runs-before-the-opener](strip-strings-runs-before-the-opener.md) | backend | — | 0/4 | A quote inside a block comment blanks the comment's own closer |
| [a-comment-run-merges-across-blanks](a-comment-run-merges-across-blanks.md) | backend | — | 0/5 | A licence header and a doc comment become one paragraph with one address |
| [a-malformed-page-drops-its-records](a-malformed-page-drops-its-records.md) | backend | — | 0/3 | A page entry that is not an object loses every record under it, silently |
| [unaddressed-is-quadratic](unaddressed-is-quadratic.md) | backend | — | 0/4 | unaddressed() groups by path for a question that needs one flat pass |
| [stale-claims-after-the-envelope](stale-claims-after-the-envelope.md) | backend | — | 0/4 | Shipped prose still describes formats and flags this branch deleted |
| [one-stem-four-jobs](one-stem-four-jobs.md) | backend | — | 0/11 | one stem, four jobs -- and the vocabulary sweep cannot see it |
| [python-cannot-read-python](python-cannot-read-python.md) | backend | yes | 0/31 | the AST cannot read syntax newer than the floor, and two readers hide each other's bugs |
| [leading-owns-the-space-between](leading-owns-the-space-between.md) | backend | yes | 0/10 | a fifth series for the space between paragraphs -- ruled, designed, two questions open |
| [the-lexer-reads-no-files](the-lexer-reads-no-files.md) | backend | — | 0/8 | one decision -- bytes into text -- made in nine places, none of them the lexer |
| [dead-sweep-skips-private](dead-sweep-skips-private.md) | systems | — | 0/5 | dead_sweep skips every _private name, so a dead module constant is invisible to it and to ruff |
| [marketplace-resolves-live](marketplace-resolves-live.md) | systems | yes | 0/5 | A directory marketplace resolves the plugin LIVE, so a version-pinned measurement was never pinned |
| [census-row-carries-empty-fields](census-row-carries-empty-fields.md) | backend | yes | 0/9 | A census row carries 19 fields and an empty place fills 7, with three different spellings of absent |
| [claim-fallback-is-unreachable](claim-fallback-is-unreachable.md) | backend | yes | 0/7 | A non-object claim is silently emptied, and 60 lines of fallback say the opposite |
| [tier-dispatched-on-name](tier-dispatched-on-name.md) | backend | yes | 0/5 | The tier is dispatched on the language NAME, so a second tokenized language is not a data row |
| [lexer-and-language-findings](lexer-and-language-findings.md) | backend | yes | 1/15 | Ten findings in lexer.py and language.py, from three review rounds |
| [census-walks-and-flushes](census-walks-and-flushes.md) | backend | — | 0/7 | census.py walks the whole repo, runs git twice, and its run-flush never fires |
| [galley-and-compositor-write-path](galley-and-compositor-write-path.md) | backend | yes | 0/5 | The galley can overwrite the file under review, and the compositor reads through a normaliser |
| [page-and-addresser-scans](page-and-addresser-scans.md) | backend | — | 0/7 | page.py and addresser.py carry four scans that grow with the file and one CLI that contradicts the gate |
| [record-and-verdicts-disagree](record-and-verdicts-disagree.md) | backend | yes | 0/8 | record.py and verdicts.py disagree about what a valid record is, in four places |
| [record-verdict-desk-findings](record-verdict-desk-findings.md) | backend | — | 0/9 | Round-4 findings in record/verdict/desk, including two that certify a run at exit 0 |
| [exception-hierarchy](exception-hierarchy.md) | backend | — | 0/5 | Named tuples give us the seam; the hierarchy that catches our own types is not built |
| [language-rows-in-toml](language-rows-in-toml.md) | backend | — | 0/6 | 18 rows of pure data sit in shipped Python; references/vocabulary.toml is the pattern |
| [isolate-the-codes-contribution](isolate-the-codes-contribution.md) | testing | yes | 0/6 | Two graded arms, orchestration held constant; the rewording is the confound |
| [verdicts-is-the-join](verdicts-is-the-join.md) | backend | yes | 4/11 | The VERDICTS table lives in record.py; verdicts.py is the join and 43 sites say so |
| [computed-and-never-read](computed-and-never-read.md) | backend | — | 0/8 | The insert line, the matter branch, the paragraph index and two repeated full-file scans -- each needs more than a comment fix |
| [not-every-line-has-an-address](not-every-line-has-an-address.md) | backend | yes | 0/8 | 595 real lines carry no address, all leading -- and whether that is a false sentence or a missing place is unruled |
| [lookup-parses-whole-census](lookup-parses-whole-census.md) | backend | yes | 0/5 | A lookup is O(project), not O(file) -- 1.1s per lookup extrapolated at 500k lines; sharding or batching fixes it, re-lexing trades away staleness detection |
| [retired-word-in-a-quote](retired-word-in-a-quote.md) | systems | yes | 0/5 | folio cannot join RETIRED without exempting the five core modules whole, because each quotes a ruling made when the word was current |
| [matter-misses-two-languages](matter-misses-two-languages.md) | backend | yes | 0/5 | C and Python type a licence header as matter; Rust loses the run to the `a` series and TypeScript types it a docstring |
| [code-concerns-cannot-carry-a-proposed-change](code-concerns-cannot-carry-a-proposed-change.md) | backend | — | 0/5 | code_concerns is a bare list of strings, so a code problem reaches no gate |

### in-progress  (5)

| file | owner | roy? | done | what |
| --- | --- | :-: | ---: | --- |
| [compact-can-buy-lines-with-width](compact-can-buy-lines-with-width.md) | agents · Roy | — | 1/6 | COMPACT can buy lines with width, and nothing stops it |
| [stage-1-is-re-derived-every-run](stage-1-is-re-derived-every-run.md) | agents | yes | 1/8 | Stage 1 is re-derived every run, asks one question twice, and knows one structure source |
| [verdicts-py-announces-one-subject-and-holds-four](verdicts-py-announces-one-subject-and-holds-four.md) | backend | yes | 7/8 | * **2,083 lines, four subjects, and a docstring announcing one.** The verdict table, a report reader, a per-finding checker and the join. !! `module-context` FOUND IT and then emitted a `patch` widening the docstring to announce TWO subjects -- the defect its own trigger is named for, applied as the remedy, and no `code_concerns` entry. Filed as the one miss in `evals/test-cases.jsonl`, pinned at `d3aa065`. ! Scheduled with the census filter because the lookup tool needs the verdict table to be a module, and because two open TODOs sit entirely inside one half each -- the bridge is COPIED into a new module if it is not rewritten during the cut. * Unruled: the four module names, which `docs/vocabulary.md` constrains by binding `the join` to `verdicts.py` |
| [the-bridge-landed-and-the-rewrite-did-not](the-bridge-landed-and-the-rewrite-did-not.md) | backend | yes | 5/10 | The bridge landed and the rewrite did not |
| [corpora-are-all-python](corpora-are-all-python.md) | testing | — | 2/6 | The corpora are nine Python projects, so every per-language rule is measured on Python and C alone |

### decision-needed  (6)

_None -- the remaining rulings sit inside the two files rather than blocking them entirely; the
other tasks can proceed without them._
| [correct-against-patch-is-a-conflict-and-is-not-flagged](correct-against-patch-is-a-conflict-and-is-not-flagged.md) | agents · Roy | — | 0/3 | `correct` against `patch` is a conflict, and the gate does not flag it |
| [role-rule-register](role-rule-register.md) | agents | yes | 0/5 | The register of proposed additions and amendments to the four editorial role files. ! Role prose is BUDGET-FIXED, so a candidate is not judged alone -- it is judged against what it would replace, which is why they collect here instead of landing one at a time. |
| [evidence-still-names-places-by-line](evidence-still-names-places-by-line.md) | testing | yes | 0/9 | **The address reached the record key and a `move`'s destination and stopped.** `SOURCES` -- the field the evidentiary contract rests on -- is 100% line-form, and Roy's `address:lines` ruling is unimplemented. Four other artifacts name a place by nothing at all. |
| [no-mark-for-let-it-stand](no-mark-for-let-it-stand.md) | agents | yes | 1/7 | There is no mark for LET IT STAND -- a declined proposal is not recorded, so the next run proposes it again |
| [front-half-undetermined](front-half-undetermined.md) | testing | yes | 0/7 | The census to findings to verdicts path has never been determined against a backend that works |
| [a-role-with-no-code-out-damages-the-prose](a-role-with-no-code-out-damages-the-prose.md) | agents | yes | 0/4 | `code_concerns` is defined in the shared brief that every role reads, but named in only ONE of the four reviewer files -- `function-context`. It is absent from `module-context`, whose whole remit is whether a module announces ONE subject, which is the finding that most needs a code out. MEASURED in the harness: `module-context-widens-a-two-subject-docstring` detected that `verdicts.py` holds four subjects, had no verdict for 'split this module', and emitted a prose `patch` widening the docstring to announce TWO -- the exact defect its own trigger is named for. `code_concerns` came back empty. |

### in flight  (0)

| file | owner | roy? | done | what |
| --- | --- | :-: | ---: | --- |

### blocked  (7)

_None._

| [requires-roy-never-goes-back-down](requires-roy-never-goes-back-down.md) | systems | — | 2/5 | nothing recomputes it or prompts the clearing; 6 cleared, 26 left to read |
| [held-runs-need-a-one-off-migration](held-runs-need-a-one-off-migration.md) | testing | — | 0/5 | the report cannot name a place, but the recorded hash can -- a script, not a feature |
| [a-block-is-a-paragraph-on-a-page](a-block-is-a-paragraph-on-a-page.md) | backend | — | 2/5 | everything read by a human or an agent says paragraph; 706 internal identifiers remain |
| [the-roles-are-named-for-what-they-read](the-roles-are-named-for-what-they-read.md) | agents | — | 0/5 | block-context etc. become the editorial desks; unlike `block` these ARE on the wire |
| [drop-the-column](drop-the-column.md) | backend | — | 0/6 | the column is len(anchor)+1 everywhere; the address system answers what it was added for |
| [a-closing-quote-with-a-comment](a-closing-quote-with-a-comment.md) | backend | — | 0/11 | the closing quote and the comment beside it are both stored, so the file gains a line |
| [lexer-does-not-lex](lexer-does-not-lex.md) | backend | yes | 0/7 | One module, two jobs: one tier reads characters, the other reads CPython's parse |
---

## Completed

Kept as the record. **`-SUPERSEDED` means it was never implemented and no longer needs to be** --
the reason is inside the file.

| file | what it settled |
| --- | --- |
| [a-wrapped-trailing-comment-is-split-into-two-blocks](completed/a-wrapped-trailing-comment-is-split-into-two-blocks.md) | **CLOSED 2026-08-17 by group A.** One sentence, two blocks, and the second half is read against the wrong declaration. A trailing comment that wraps was split by the census, so half a claim reached a reviewer with a neighbour's anchor. |
| [apply-names-both-stage-5-and-stage-7b](completed/apply-names-both-stage-5-and-stage-7b.md) | **COMPLETE 2026-08-16.** One word named two stages -- applying a MARK produces replacement text at stage 5; applying the APPROVED text writes it at 7b. Stage 5 is APPLY and 7b is WRITE. |
| [the-harness-leaks-into-the-shipped-rules](completed/the-harness-leaks-into-the-shipped-rules.md) | **COMPLETE 2026-08-16.** This repo's eval harness is not the user's environment, and the shipped rules had stopped distinguishing them -- so a plugin user read instructions about a tree they do not have. |
| [the-level-ladder-was-invented-during-the-port](completed/the-level-ladder-was-invented-during-the-port.md) | **COMPLETE 2026-08-16 -- removed entirely.** `level` gated which verdicts a reviewer may emit and had no provenance: traced with `git log -S`, the ladder exists at ZERO commits in `redacted_corpus`, on any branch. Roy: *"Those weren't in the original format, and I didn't ask for them."* |
| [the-task-agent-emits-the-vocabulary](completed/the-task-agent-emits-the-vocabulary.md) | **COMPLETE 2026-08-16.** One source, emitted verbatim, per agent. A script prints the definitions an agent needs and the task agent pastes the output into that agent's prompt. Roy: *"No summarizing no duplication."* |
| [the-gate-and-the-brief-disagree](completed/the-gate-and-the-brief-disagree.md) | **CLOSED 2026-08-17, 8 of 8.** `verdicts.py` is the gate a report must pass, and in six places it enforced what the brief does not say or accepted what the brief forbids -- so a reviewer could be correct-by-the-brief and rejected, or wrong-by-the-brief and admitted. ! One was a live contradiction: the brief REQUIRED `EVIDENCE` and `QUOTE` on a `query` and the gate exempted both, so a reviewer supplied evidence nothing read |
| [the-unit-of-review-is-the-statement-not-the-block](completed/the-unit-of-review-is-the-statement-not-the-block.md) | **CLOSED 2026-08-17 by group A, 5 of 5.** A block is how a finding is ADDRESSED; a STATEMENT is what is ruled on. Roy: *"each sentence/statement is under review not the 'block'"*. Three files disagreed on whether two statements in one block are two findings -- the brief said *"exactly once"*, `SKILL.md` said *"several verdicts per role per block"*, and the gate used a SET and accepted both silently |
| [an-empty-interval-has-no-census-index](completed/an-empty-interval-has-no-census-index.md) | **CLOSED 2026-08-17, 11 of 11 -- the census change landed and Roy ruled the name.** An `add` is a finding about a GAP, and a gap had no index, so the verdict had to borrow a neighbouring block's. Every interval is now enumerated. ! That enumeration is what [`the-census-is-mostly-intervals-nobody-rules-on`](the-census-is-mostly-intervals-nobody-rules-on.md) later filtered -- a projection of it, never a replacement |
| [the-finding-record-is-eight-fields-and-six-would-do](completed/the-finding-record-is-eight-fields-and-six-would-do.md) | **The record shipped with five fields and grew to eight, every addition serving the GATE rather than the reviewer.** Cut to six, `LOCATION` retired as derivable from `BLOCK`, `EVIDENCE`+`QUOTE` merged into `SOURCE`, `SUMMARY` split into `CLAIM` and `REASON`. ! The cut was never the point: `REASON` is what the `move` ruling rests on and NOTHING checked it, which is the thread that became the typed record. ! Its last task was a budget call on the brief, answered 2026-08-18 by measurement -- the brief is a FIXED cost per reviewer and the record a PER-BLOCK one, so dropping the block text saved 332,828 bytes per run against a brief of 87,284. The prose ships, all seven, and `scripts/render_brief.py` writes it from `VERDICTS` because the hand copy had already drifted to teaching a retired format |
| [the-record-is-a-parsed-template-and-should-be-a-value](completed/the-record-is-a-parsed-template-and-should-be-a-value.md) | **A finding is a JSON object the reviewer FILLS, not a document it composes.** Roy, 2026-08-17: *"we should be using a real class or something that it can paste into and knows that it is receiving strings, not 'can I parse this into the table'."* `record.py --seed` lays down one slot per prose block carrying `block` and `address`; the reviewer sets `verdict`, `claim`, `reason`, `sources`, `change`. !! **The record says WHERE, never WHAT** -- handed the prose a reviewer could rule without opening the file, and no check could tell that from real work, while reading the wrong lines IS caught. ! The regression was byte-identical: four held reports, converted, joined to output `diff` could not separate. ! 83 refusals in one run had been spent on transcription fidelity and not one was about a finding |
| [re-review-is-ordered-everywhere-and-defined-nowhere](completed/re-review-is-ordered-everywhere-and-defined-nowhere.md) | **What a re-review IS**, in the one file that says: `references/re-review.md`. Ten sites ordered a re-review and none defined one. It is the JOINED BLOCK that goes back, never the finding -- Roy, 2026-08-17: *"sending it right back doesn't help"* -- and it answers three questions about the role's own edit. Two slots, 5b after APPLY and 6b after COMPACT, which must not be collapsed: 6b is the only reader of stage 6's output before the author sees it. ! A contested block goes to its FILERS and no others, because all three questions presuppose an edit to answer for; a third role reading it is a FRESH REVIEW travelling 6 -> 4. ! `galley` stays defined inline -- deriving the file into the four reviewers' vocabulary adds exactly one term, `cap`, and those are the four roles the cap is never passed to |
| [eight-terms-have-no-definition-and-angle-means-five-things](completed/eight-terms-have-no-definition-and-angle-means-five-things.md) | **The vocabulary itself.** A twelve-agent survey found nine terms used with a fixed sense and stated nowhere, and fifteen more carrying two or three senses each; every one is now defined, dropped, or declared as deliberate polysemy, and `scripts/check_vocabulary.py` says so as a command. ! Its last * dissolved rather than being ruled: *"5 of its 7 reviewer reports"* had lost two of its four sites already, and the two left sit in prose the shipped-Python cleanup rewrites on grounds that do not need the number |
| [an-editorial-mark-is-not-an-action-and-reanchor-is-move](completed/an-editorial-mark-is-not-an-action-and-reanchor-is-move.md) | **A verdict is a MARK, not an action**, and the relocation verdicts collapsed twice: `reanchor` into `move` (2026-08-15), then `split` into `move` (2026-08-16). ! Both by the same argument -- a relocation is ONE judgment and the destination is payload -- and `split` was additionally the only verdict whose subject was the BLOCK rather than the sentence. Seven verdicts. `drop`, `patch` and `add` were ruled to STAY: Roy, *"everything else we have come up with has had a valid use case."* |
| [address-is-not-stable-under-prose-edits](completed/address-is-not-stable-under-prose-edits.md) | A line-numbered address is valid for one file state only, and `addresser.py` names a place against the CODE instead: `a` a declaration, `b` a gap, `c` an on-line position. Measured: a prose-only edit moved 2 of 3 line addresses and 0 of 3 stable ones. |
| [address-collides-across-dotted-paths](completed/address-collides-across-dotted-paths.md) | Separator changed from '.' to ':', which no path may hold; census refuses a POSIX path that does |
| [c-series-admitted-not-writable](completed/c-series-admitted-not-writable.md) | The galley splices within a line: original_column replaces whole_lines, and an intermediate comment is no longer censused |
| [prose-fenced-by-code-on-both-sides](completed/prose-fenced-by-code-on-both-sides.md) | Ruled the same day it was raised: an intermediate comment is not censused, and its line is code |
| [deprecated-reader-cannot-replay](completed/deprecated-reader-cannot-replay.md) | the old form cannot name a place -- an index is not portable and `LOCATION` is not retained -- so `convert` refuses instead of dropping or fanning out |
| [shipped-prose-lags-the-rulings](completed/shipped-prose-lags-the-rulings.md) | SKILL.md converted, the brief's worked record fixed, ~25 docstrings corrected, and a measurement that had rotted twice re-taken |
| [three-names-two-words](completed/three-names-two-words.md) | One ordered mapping replaces all three; no sorted() survives and the edge case is byte-identical |
| [a-hugs-its-declaration-SUPERSEDED](completed/a-hugs-its-declaration-SUPERSEDED.md) | The a -> b -> c order is universal; the error was reading final position as application order |
| [b-inserts-above-the-shebang-SUPERSEDED](completed/b-inserts-above-the-shebang-SUPERSEDED.md) | No bug: a covered-lines range was read as an insertion point. The field name is the real defect |
| [the-path-is-repeated-in-every-address](completed/the-path-is-repeated-in-every-address.md) | A reviewer is handed one page per file and a record cites the cue alone; held.py reads both shapes |
| [anchor-side-is-dead](completed/anchor-side-is-dead.md) | Deleted, with PATHISH and line_address, in the sweep for shipped names nothing reads |
| [convert-drops-every-record-SUPERSEDED](completed/convert-drops-every-record-SUPERSEDED.md) | Superseded: the converter and the format it read were deleted, not fixed |
| [stage-5-certifies-an-unaddressed-census](completed/stage-5-certifies-an-unaddressed-census.md) | addresser.unaddressed is the one check; census.py refuses on emit and verdicts.py on read |
| [lexer-misreads-ordinary-code](completed/lexer-misreads-ordinary-code.md) | Three misreads fixed and nesting added; the closing-line residue measured at 0 occurrences and accepted, with a test |
| [dead-names-ungated](completed/dead-names-ungated.md) | scripts/dead_sweep.py, an input rather than a gate; 0 dead names in the tree as of 2026-08-21 |
| [complete-breaks-links-SUPERSEDED](completed/complete-breaks-links-SUPERSEDED.md) | Accepted: the orphans are inside completed/, and repairing one means rewriting an archived file |
| [plugin-version-not-bumped](completed/plugin-version-not-bumped.md) | 0.2.4-alpha in all three files; the cache directory can no longer collide with the measured 0.2.3 |
| [two-paragraphs-one-address](completed/two-paragraphs-one-address.md) | Fixed in 28a635d -- a comment's DELIMITERS are not paragraph boundaries, only code is. 157 shared addresses over 699 files became 0. |
| [galley-does-two-jobs](completed/galley-does-two-jobs.md) | Split built and wired: galley.reset places by address, compositor.set_page sets, splice/overlaps/splice_range/paragraph_matches deleted, and the shipped prose now defines both terms |
| [galley-is-still-index-keyed](completed/galley-is-still-index-keyed.md) | Tasks 1-2 done (address-keyed); task 3 was an observation whose mechanism -- splice and its line-ordered sort -- was deleted in the galley rewrite |
| [second-key-stale-on-drop](completed/second-key-stale-on-drop.md) | Ruled and cut the same morning: the second key is DELETED, so it cannot go stale -- Page.leading is dict[str, str], keyed by the place a run of blanks follows |
| [foliation-knows-about-lines](completed/foliation-knows-about-lines.md) | Cues is 3 fields -- addressers, walk, reading. A place records the trigger it was emitted at, so no position is reconstructed; d left SERIES as a symbol; lines and _code were both views of the walk |
| [leaf-means-two-things](completed/leaf-means-two-things.md) | The binder model dissolved it: no leaf in the picture, folio became cue, and the shipped tree holds zero foli* -- the corrections and the rename landed in 3f661d6..8141b7a |
| [front-matter-restamps](completed/front-matter-restamps.md) | SOLVED by the lexer typing matter. The rule is now 'the run starts on line 1', not 'it ends before the module docstring', so it no longer depends on what follows. MEASURED 2026-08-23: a top-of-file comment run is `f0 kind=matter` both before and after an `a0` edit fills the module docstring -- the annotation is stable under this tool's own edits, which is what the file existed to get |
| [back-matter-is-a-gaps-comment](completed/back-matter-is-a-gaps-comment.md) | SOLVED by the `f` series emitting at both ends. MEASURED 2026-08-23: a trailing licence or modeline lands in `f1 kind=matter` -- Python AND Rust -- not in the closing gap. The RECOGNITION half the file said was missing is the lexer's `run[-1] == last line` clause, and `file_places()` returns head and foot |
| [front-matter-protection-is-python-only-SUPERSEDED](completed/front-matter-protection-is-python-only-SUPERSEDED.md) | SUPERSEDED by `matter-misses-two-languages`: the title is false as of 2026-08-23. MEASURED -- an identical licence header types `f0 kind=matter` in C as well as Python, so it is not Python-only. Rust and TypeScript still fail, for two causes neither of which is the positional `mark_matter` this file was written about |
| [census-emits-no-page](completed/census-emits-no-page.md) | SOLVED by the page/census split. `page.py` defines `Page` -- path, text, paragraphs, cues, tier, leading -- and `census.py` imports `page_for` and calls it per file. The census emits pages and no longer builds one |
| [triggers-has-no-caller](completed/triggers-has-no-caller.md) | SOLVED. `addresser.py:685` is `out = Cues(triggers=triggers(list(code)))` -- production, not a test -- and the shape is the one the walk steps through. The docstring's promise that ONE LIST keeps the four series from drifting is now true of the list they actually walk |
| [lexer-owns-a-page-kind](completed/lexer-owns-a-page-kind.md) | SOLVED, and the last task CHECKED rather than assumed: `OCCUPIES_NOTHING` no longer appears in `lexer.py` at all, and `code_lines` appears only in four comment prose references, never as an import. The docstring's one-sibling claim holds |
| [anchor-was-empty-on-98-percent](completed/anchor-was-empty-on-98-percent.md) | SOLVED and the sweep it asked for found one. MEASURED 2026-08-23: 0 of 687 prose paragraphs carry no anchor, against 98 percent when this was filed. ! The last task -- look for the same shape in the other SEEDED fields -- ran in simplify round 7 and found `Finding.anchor`: filled from the record and read by neither `desk` nor the join. It was cut |
