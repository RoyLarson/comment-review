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
  checkbox names the file, or the grep that must come back empty.
- **A ruling that is OWED is a task; a ruling already MADE is not.** *"Rule whether `b0` leaves
  the `b` series"* finishes the day Roy answers. *"The trade word is `leading`"* never finishes
  -- it is the Objective's, or a `note`'s. ! Boxing the second is what made
  `leading-owns-the-space-between` read `0 of 10` with nine of them settled; see `CLAUDE.md`,
  *A box is a claim about whether work remains*.
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

### open  (117)

| file | owner | roy? | done | what |
| --- | --- | :-: | ---: | --- |
| [a-comment-inside-a-line-makes-the-file-unprovable](a-comment-inside-a-line-makes-the-file-unprovable.md) | backend | -- | 2/7 | A comment INSIDE a line makes the whole file unprovable |
| [a-role-can-reverse-itself-between-runs](a-role-can-reverse-itself-between-runs.md) | agents | yes | 1/6 | A role can reverse itself between runs, and nothing measures it |
| [a-scope-declaration-costs-as-much-as-a-finding](a-scope-declaration-costs-as-much-as-a-finding.md) | agents | yes | 2/7 | A scope declaration costs as much as a finding |
| [block-comment-markers-survive-into-the-prose](block-comment-markers-survive-into-the-prose.md) | backend | -- | 0/10 | Block-comment markers survive into the prose the reviewers read |
| [move-and-correct-compose](move-and-correct-compose.md) | agents | -- | 4/6 | `move` and `correct` COMPOSE, and the gate calls them a contradiction |
| [only-census-got-out-and-the-skill-instructs-a-redirect](only-census-got-out-and-the-skill-instructs-a-redirect.md) | agents | -- | 3/5 | Only `census.py` got `--out`, and `SKILL.md` instructs the redirect it forbids |
| [referrers-matches-on-any-public-name-and-surfaces-the-whole-repo](referrers-matches-on-any-public-name-and-surfaces-the-whole-repo.md) | backend | -- | 0/6 | `referrers.py` matches on any public name, and surfaced the whole repo |
| [stage-5-is-the-only-stage-with-no-independent-reader](stage-5-is-the-only-stage-with-no-independent-reader.md) | agents | yes | 6/12 | Stage 5 is the only stage whose writer is also its checker |
| [the-code-check-refuses-add-and-drop-on-a-docstring](the-code-check-refuses-add-and-drop-on-a-docstring.md) | backend | yes | 1/5 | The CODE CHECK refuses `add` and `drop` when the prose is a docstring |
| [the-emitted-vocabulary-can-collide-with-the-repo](the-emitted-vocabulary-can-collide-with-the-repo.md) | agents | yes | 1/6 | The emitted vocabulary can collide with the reviewed repo's own terms |
| [doc-is-structural-means-two-things](doc-is-structural-means-two-things.md) | backend | -- | 0/3 | doc_is_structural means two things and its docstring names one |
| [docstrings-need-their-own-address-series](docstrings-need-their-own-address-series.md) | backend | -- | 5/9 | A docstring needs its own address series, and it names what it documents |
| [line-0-places-are-unreachable](line-0-places-are-unreachable.md) | backend | -- | 4/6 | **An empty place sits at line 0 by ruling, and both tools that answer by LINE filter on `start &lt;= line &lt;= end`.** So the places an `add` exists to cite are the ones no line lookup can name -- while the brief forbids the only remaining route, counting. |
| [filtered-measurement-unrecorded](filtered-measurement-unrecorded.md) | testing | -- | 3/5 | The filtered-census measurement exists only in run history |
| [doc-does-not-fill-its-a](doc-does-not-fill-its-a.md) | backend | yes | 5/8 | the a place now exists for Rust/Go/etc but the doc that fills it still sits at b |
| [vocabulary-gate-is-red](vocabulary-gate-is-red.md) | systems | -- | 2/7 | check_vocabulary exits 1 on this branch and no test asserts check_drift |
| [six-mutations-survive-the-suite](six-mutations-survive-the-suite.md) | testing | -- | 1/8 | 720 tests green against six deliberate defects in shipped code |
| [the-anchor-claims-are-inverted](the-anchor-claims-are-inverted.md) | agents | -- | 0/4 | shipped prose says an anchor is often empty; it is never empty |
| [stale-measurements-in-shipped-prose](stale-measurements-in-shipped-prose.md) | testing | yes | 1/6 | every one re-derivable by a command, and every one wrong |
| [assertions-that-gate-a-substring](assertions-that-gate-a-substring.md) | testing | -- | 3/10 | each passes in the buggy state its own comment forbids |
| [move-across-an-uncued-file](move-across-an-uncued-file.md) | backend | -- | 5/6 | the address form spans files; the census does not |
| [closing-line-deletes-code](closing-line-deletes-code.md) | backend | -- | 5/8 | An edit to a comment whose run closes mid-line DELETES the code after the closer |
| [versioning-at-v1](versioning-at-v1.md) | systems | -- | 3/12 | v1.x wants a concrete versioning system on everything that ships |
| [check-passes-a-shared-address](check-passes-a-shared-address.md) | backend | -- | 0/4 | addresser --check prints SHARED and exits 0 |
| [a-series-never-fills-outside-python](a-series-never-fills-outside-python.md) | backend | -- | 17/20 | Outside Python the `a` place is emitted and never filled |
| [bom-is-read-as-source](bom-is-read-as-source.md) | backend | -- | 2/4 | A UTF-8 BOM is censused as a line of code |
| [a-malformed-page-drops-its-records](a-malformed-page-drops-its-records.md) | backend | -- | 1/5 | A page entry that is not an object loses every record under it, silently |
| [unaddressed-is-quadratic](unaddressed-is-quadratic.md) | backend | -- | 0/4 | unaddressed() groups by path for a question that needs one flat pass |
| [stale-claims-after-the-envelope](stale-claims-after-the-envelope.md) | backend | -- | 2/8 | Shipped prose still describes formats and flags this branch deleted |
| [one-stem-four-jobs](one-stem-four-jobs.md) | backend | -- | 7/15 | one stem, four jobs -- and the vocabulary sweep cannot see it |
| [python-cannot-read-python](python-cannot-read-python.md) | backend | -- | 32/39 | the AST cannot read syntax newer than the floor, and two readers hide each other's bugs |
| [claim-fallback-is-unreachable](claim-fallback-is-unreachable.md) | backend | yes | 6/8 | A non-object claim is silently emptied, and 60 lines of fallback say the opposite |
| [census-walks-and-flushes](census-walks-and-flushes.md) | backend | -- | 3/7 | census.py walks the whole repo, runs git twice, and its run-flush never fires |
| [galley-and-compositor-write-path](galley-and-compositor-write-path.md) | backend | -- | 4/11 | The galley can overwrite the file under review, and the compositor reads through a normaliser |
| [record-and-verdicts-disagree](record-and-verdicts-disagree.md) | backend | -- | 4/8 | record.py and verdicts.py disagree about what a valid record is, in four places |
| [exception-hierarchy](exception-hierarchy.md) | backend | -- | 2/10 | Named tuples give us the seam; the hierarchy that catches our own types is not built |
| [language-rows-in-toml](language-rows-in-toml.md) | backend | -- | 6/16 | 18 rows of pure data sit in shipped Python; references/vocabulary.toml is the pattern |
| [computed-and-never-read](computed-and-never-read.md) | backend | -- | 5/10 | The insert line, the matter branch, the paragraph index and two repeated full-file scans -- each needs more than a comment fix |
| [dangling-links-resolve-nowhere](dangling-links-resolve-nowhere.md) | systems | yes | 0/6 | 31 relative links resolve nowhere, and two of them are in a live TODO |
| [fixtures-do-not-test-the-shape](fixtures-do-not-test-the-shape.md) | testing | -- | 1/5 | A per-language fixture can pass without exercising the shape its language is measured on |
| [drop-the-column](drop-the-column.md) | backend | -- | 7/9 | the column is len(anchor)+1 everywhere; the address system answers what it was added for |
| [held-runs-need-a-one-off-migration](held-runs-need-a-one-off-migration.md) | testing | -- | 2/5 | the report cannot name a place, but the recorded hash can -- a script, not a feature |
| [requires-roy-never-goes-back-down](requires-roy-never-goes-back-down.md) | systems | -- | 2/7 | nothing recomputes it or prompts the clearing; 6 cleared, 26 left to read |
| [the-roles-are-named-for-what-they-read](the-roles-are-named-for-what-they-read.md) | agents | -- | 0/5 | block-context etc. become the editorial desks; unlike `block` these ARE on the wire |
| [lookup-parses-whole-census](lookup-parses-whole-census.md) | backend | -- | 4/14 | A lookup is O(project), not O(file) -- 1.1s per lookup extrapolated at 500k lines; sharding or batching fixes it, re-lexing trades away staleness detection |
| [verdicts-is-the-join](verdicts-is-the-join.md) | backend | -- | 8/12 | The VERDICTS table lives in record.py; verdicts.py is the collator and 43 sites say so |
| [census-row-carries-empty-fields](census-row-carries-empty-fields.md) | backend | -- | 11/17 | A census row carries 19 fields and an empty place fills 7, with three different spellings of absent |
| [matter-misses-two-languages](matter-misses-two-languages.md) | backend | yes | 2/5 | C and Python type a licence header as matter; Rust loses the run to the `a` series and TypeScript types it a docstring |
| [nothing-runs-the-whole-chain](nothing-runs-the-whole-chain.md) | backend | -- | 0/7 | Every stage of the backend has its own tests and nothing runs census -> seed -> record -> join -> galley -> compositor -> prove in one pass. So the redesign phase has no measurement to hold constant, and a defect that lives BETWEEN two stages is invisible to every gate this repo has. |
| [nothing-makes-the-fair-copy](nothing-makes-the-fair-copy.md) | backend | yes | 1/13 | Nothing turns the collated marks into the paragraph the galley writes |
| [settle-carries-two-meanings](settle-carries-two-meanings.md) | systems | yes | 0/6 | settle carries two meanings in what an agent is handed, and neither is declared to it |
| [no-stage-agrees-the-terms](no-stage-agrees-the-terms.md) | systems | yes | 0/7 | No stage establishes what the words mean before the roles are asked to use them |
| [listing-hands-the-repo](listing-hands-the-repo.md) | backend | -- | 1/4 | The listing hands every reviewer the whole repo, four times a page |
| [the-cue-legend-and-its-round-trip](the-cue-legend-and-its-round-trip.md) | backend | -- | 0/5 | The cue letter carries what three fields used to say, and nothing gives the agents the legend or checks they followed it |
| [the-flow-lives-in-the-command](the-flow-lives-in-the-command.md) | backend | -- | 1/5 | Lifting main() out showed the orchestration was always inside it: commands/census.py took 446 lines and calls page_for, while flows/census.py kept 261 lines of helpers. A command is meant to EXPOSE a flow, not be one. |
| [two-areas-have-no-tests](two-areas-have-no-tests.md) | backend | -- | 0/4 | tests/ mirrors the package, so an area with no directory is a visible hole. machine/ (repo, constants, exceptions) and commands/ (all ten) have none. repo is exercised only through flows/test_census_names.py, which tests something else. |
| [concordance-gaps-stated-twice](concordance-gaps-stated-twice.md) | backend | -- | 0/4 | Both encode 'a gap is not a pass' and spell it differently: code_names returns unread rows keyed by NO_HARVESTER/WALKED_TREE, referrers collects unreadable and unsearched under NOT CHECKED. Three states, one idea, two vocabularies. The EXTRACTIONS stay separate -- code_names must be structural so a comment mentioning a symbol cannot prove it exists, and referrers must be textual to see mentions in files nothing parses. |
| [name-corpus-sees-one-language](name-corpus-sees-one-language.md) | backend | -- | 0/5 | MEASURED 2026-08-24 on this checkout: 278 of 369 tracked files (75%) contribute NO names, every one NO_HARVESTER, zero read failures. code_names harvests via ast.parse, so it covers Python alone -- and on a checkout with syntax newer than the floor interpreter it goes blind to Python too, turning symbols defined only there into false obituaries. lexer.declarations() already finds every documentable declaration in eleven languages lexically; it returns positions, not identifiers. Harvesting from it instead of the AST makes the corpus polyglot and drops the floor limit in one change. |
| [stage-7b-cannot-be-run](stage-7b-cannot-be-run.md) | backend | -- | 0/3 | SKILL.md stage 7b says the compositor puts the approved draft over the real file wholesale, and compositor.approve(drafted, real) implements exactly that. NOTHING CALLS IT: no shipped code, and the compositor command takes only positional paths -- no --approve, no --draft. The galley command writes a directory and stops. So the one step that puts approved text on disk is documented, implemented, and unreachable. PRE-EXISTING: approve was equally uncalled at b3d79d2, before the package move. dead_sweep has reported it as held-by-prose-only; it always exits 0, so nothing was failing. |
| [a-doc-comment-is-cued-a-and-typed-b](a-doc-comment-is-cued-a-and-typed-b.md) | backend | -- | 0/4 | MEASURED across thirteen languages: go, ruby and lua place a declaration's documentation at an a cue and type it comment -- which is the b series' kind. Rust, Java, C#, Kotlin, Swift, TS and JS all answer docstring, and they are the ones with a DISTINCT doc marker (/// or /** */). The three that break it use an ordinary line-comment marker as their doc form, so the lexer cannot tell the two apart by token and types it comment while the walk still cues it a. One row makes two claims about itself, and every consumer pairing them sees a contradiction: record.prose_paragraphs filters on the KIND while series_of reads the CUE. |
| [two-filters-for-one-fence-rule](two-filters-for-one-fence-rule.md) | backend | -- | 0/2 | binder.bind() filters fences with 'if b.address' and flows.census.carried() filters them with the same predicate. Two statements of one rule: removing either leaves the binder correct, which is how a mutation removing carried() changed nothing an agent receives. One of them owns the rule; the other should call it or go. |
| [the-skill-names-commands-that-moved-to-prototype](the-skill-names-commands-that-moved-to-prototype.md) | agents | -- | 3/4 | Stages 4-7 of the shipped skill cannot be followed as written: SKILL.md invokes record (x2), run_context (x2), verdicts and vocabulary, and all four moved to prototype/ on 2026-08-25. The dispatcher lists six commands now, not ten. This is deliberate rather than an oversight -- the agent-facing design is what is being reconsidered, and rewriting the stages before deciding the new one would be inventing the answer. It is filed so the breakage is a known state and not a discovery. |
| [the-cue-legend-was-never-written](the-cue-legend-was-never-written.md) | agents | yes | 0/4 | Addressing #12 cut kind, declares and symbol on the grounds that 'they are stating something that the cue letter states. So we just give the agents the legend for the cue letters and let them run with it.' The fields went; the legend did not arrive. MEASURED 2026-08-25: nothing in the shipped prose is one. reviewer-brief.md names a, b and c in passing at line 225 -- 'an a is a declaration's documentation, a b is a gap, a c is the room beside a line of code' -- and never f, never the present/absent pairing, and not as the deliberate artefact the ruling named. So agents are handed LESS than the ruling intended rather than differently. Roy, 2026-08-25: it 'is going to change a lot of things in that lane', which is why it is filed here rather than written in passing. |
| [render-page-imports-flat-names](render-page-imports-flat-names.md) | systems | -- | 0/6 | scripts/render_page.py dies at import: ModuleNotFoundError: No module named 'lexer'. It imports lexer, page and addresser as flat top-level modules, which is what src/ looked like before the 2026-08-24 move to src/comment_review/ with sub-packages. Nothing runs it, so nothing noticed. CLAUDE.md documents it as an INPUT to the-census-is-mostly-intervals-nobody-rules-on, where a decision is meant to be made -- so a tool that cannot run is a decision that cannot be informed. Found while updating its page_for call for the sha parameter: the call edit landed, but the file was already dead above it. |
| [coverage-is-not-measured](coverage-is-not-measured.md) | backend | yes | 1/5 | coverage is not a pinned dev dependency and is not installed -- pytest, ruff and ty are. So nothing answers which lines the 789 tests actually execute. Roy, 2026-08-25: cleaning up the tests also allows us to use coverage to verify the tests cover everything and to delete that which we do not need. TWO USES, and the second is the one no other instrument here provides: uncovered code is a DELETION candidate. dead_sweep.py answers a different question -- it finds names nothing POINTS AT, statically. Coverage finds code nothing RUNS. A function called only by another dead function is invisible to the first and obvious to the second. THE ORDER MATTERS AND IS WHY THIS WAS NOT FILED EARLIER: a suite holding tests orphaned by a cut reports coverage on the code those tests touch, so dead code reads as live and the number argues for keeping it. The cleanup has to come first or the instrument lies in the direction of keeping everything. |
| [build-check-reads-the-working-tree](build-check-reads-the-working-tree.md) | systems | -- | 1/6 | MEASURED at commit b39cf4a: src/comment_review/reading/series.py and its plugins/ copy had DIFFERENT git blobs (b59bf2a vs ef4eae2), while diff over the working tree called them identical and build_plugin.py --check printed the plugin matches the source: 37 files and exited 0. Cause: ruff format rewrote src/, the build copied the rewritten source into plugins/, and only the plugins/ side was committed -- so committed plugins/ was AHEAD of committed src/, inverting the one invariant that tree has. A fresh clone gets the committed bytes, and CLAUDE.md states the install reads COMMITTED state, so the same command that exits 0 on the author's machine reports a mismatch there. IT IS NOT A FALSE PASS ON ITS OWN QUESTION -- --check asks whether the built tree matches the source tree, and on that machine it did. Nothing asks whether the committed tree matches itself. NOTE the release rule this defeats: RUN THE BUILD BEFORE TAGGING AND COMMIT WHAT IT WRITES. A run that builds, commits only part, and sees a green --check has followed the letter of that rule and shipped the drift. |
| [no-step-produces-a-page](no-step-produces-a-page.md) | backend | -- | 0/4 | MEASURED 2026-08-25: commands/census.py, commands/galley.py, results/compositor.py lossless, results/compositor.py identity each run the same four calls inline -- read_source, language_for, page_for, carry the sha. Roy: you only have a step that produces a binder but you need a step here that produces a page so you can use it which is one piece of the binder. THE COST IS NOT THE DUPLICATION. With no step that yields a PAGE, a consumer that wants one either rebuilds it or reaches for the BINDER, because the binder is the only thing the tree can hand you. That is what pulled rows_of into desk/notations.py on this branch and had to be undone. The io-and-the-chain spec measured the same thing from the other side -- page_for takes TEXT, so by the time anyone reaches the reading code somebody else has already read the file -- and read it as an I/O ownership problem. It is also a missing step. flows/page.py::page_of lands on the write-chain branch and the write chain uses it; the other four sites are NOT repointed there. |
| [census-should-be-a-chain-of-producers](census-should-be-a-chain-of-producers.md) | backend | yes | 0/4 | Roy, 2026-08-25: This is where flows are useful, you can couple them without coupling how they are done. The read side should be producers plus a chain -- flows/page_for.py, flows/annotations_for.py, and later flows/references_for.py -- chained by flows/gather.py to create the binder. TODAY THE CENSUS IS ONE STEP AND THE ONLY THING THE TREE CAN HAND YOU IS A BINDER. Measured 2026-08-25: five sites rebuild a page from a path inline because no step produces one, and that absence is what pulled binder rows into the write chain and had to be undone. flows/page_for.py lands on the write-chain branch because that chain needs it; annotations_for and gather do not, and were deliberately left out rather than widening a branch mid-flight. NOTE gather is stage 2's own name in SKILL.md, so the module would be named for the stage it performs. |
| [todo-tool-writes-em-dashes](todo-tool-writes-em-dashes.md) | systems | yes | 0/3 | MEASURED 2026-08-25: 51 of the files under TODO/ carry a literal U+2014 em-dash, and the source is scripts/todo_tool.py, not any hand-written prose. Line 53 defines ROY_NO as a literal em-dash for the Requires-Roy column, and a note is rendered as DATE em-dash TEXT. CLAUDE.md states the rule plainly: this tree writes two hyphens for an em-dash because of the ASCII rule, and a reviewer flagged one of these lines as violating a stated global constraint. THE TENSION IS REAL AND NOT OBVIOUSLY THE TOOL'S FAULT. todo_tool.py is VENDORED from another project and re-grabbed rather than maintained here, ruff excludes it, and one local patch already exists for the stdout encoding guard -- which is itself evidence that non-ASCII output has bitten this repo before, on a cp1252 console. DECIDE WHICH IS TRUE rather than patching quietly: either the ASCII rule does not reach tool-written files under TODO/, or the vendored tool needs a second local patch. Nothing here is broken today; the files render and the counts are correct. |
| [galley-refusals-cannot-fire](galley-refusals-cannot-fire.md) | backend | yes | 0/2 | MEASURED 2026-08-25: galley.reset at results/galley.py:178-186 refuses a non-text replacement and an empty string, and NEITHER CAN FIRE ON THE PROOF PATH. desk/notations.py:53-64 rejects both before by_page runs, so both inputs refuse at CANNOT READ THE NOTATIONS and never reach the edit step. They stay reachable only through the deprecated commands/galley.py, which parses its edits with a bare json.loads. NOT A CALL TO DELETE THEM. The galley is a library and may be called by something other than this chain; a guard at the boundary and a guard at the point of use is defensible depth. What is NOT defensible is reset's docstring at :97-100 quoting Roy's None-is-the-delete ruling as though this function enforces it on the live chain, when the enforcement is upstream. Say which guard is load-bearing and which is depth. |
| [into-is-never-resolved](into-is-never-resolved.md) | backend | -- | 2/3 | flows/proof_setter.py resolves TARGET but never resolves INTO, then asks whether target is relative to it. A relative or symlinked into would weaken the containment guard that stops a draft escaping the output directory. NOT REACHABLE TODAY: commands/proof.py resolves out before calling in, and every test hands an absolute tmp_path. This is library hardening, not a live defect. FOUND BY THE IMPLEMENTER OF THE GUARD, WHO REPORTED IT RATHER THAN WIDENING ITS OWN SCOPE. Worth recording because the guard it weakens was itself introduced to close an escape that the previous fix opened -- proof_setter copied the collator half of the galley command's pattern and not the guard half, and wrote a draft onto the original source file at exit 0. Two rounds of path handling on the same function, each fixing the last. |
| [an-empty-place-is-not-citable](an-empty-place-is-not-citable.md) | backend | yes | 1/4 | MEASURED 2026-08-25, twice. A file holding one comment censuses to a binder carrying cues f0 and nothing else. Asking for the empty b place above a line of code -- addresser --census B --anchor 'return n + 1' --series b -- answers no b place for anchor, exit 1. A file with NO prose at all censuses to a binder carrying ZERO rows, and the same question answers carries no paragraphs, exit 2. SO THE add VERDICT IS UNEXPRESSIBLE FOR ANY PLACE THE BINDER DOES NOT CARRY, which is 91 percent of them. AND bind's OWN DOCSTRING ASSERTS THE OPPOSITE, as the justification for the cut: an empty place is still addressed, which is what makes this safe -- the walk emits every place, filled or not, so a reviewer that wants to add ASKS for the one it means, and the place is citable without being carried. That sentence is false as written. CAUSE: for_anchor's fallback in binder/addresses.py resolves an absent place by POSITION, and reads anchor_line, a field the eleven-field row cut removed. Its arithmetic always sees 0, so the fallback is unreachable for every series. The DECLARED short-circuit above it was fixed 2026-08-25 in 521e327; this is the other half and it is not a field rename -- nothing a row now carries answers where a place sits relative to an anchor. NOT A CLAIM THAT THE CUT WAS WRONG. The cut is measured and Roy ruled it. What is wrong is that the mechanism making it safe stopped working in the same change, and the prose still promises it. |
| [empty-edits-fails-a-stage](empty-edits-fails-a-stage.md) | agents | -- | 0/2 | an all-clean run writes {} to --edits, which notations.read refuses at exit 2 |
| [block-text-orphaned](block-text-orphaned.md) | backend | -- | 0/1 | block_text (reading/lexer.py) has had no caller since desk.py moved to prototype |
| [an-alteration-carries-its-own-indentation](an-alteration-carries-its-own-indentation.md) | backend | -- | 1/3 | An alteration carries its own indentation and nothing says so |
| [prove-refuses-a-doc](prove-refuses-a-doc.md) | backend | -- | 0/3 | prove_unchanged refuses a documentation file for having no code |
| [a-reference-needs-its-own-write-chain](a-reference-needs-its-own-write-chain.md) | backend | -- | 0/3 | A reference needs its own write chain, and it is NOT YET |
| [the-fields-do-not-say-a-mark-may-cite-across](the-fields-do-not-say-a-mark-may-cite-across.md) | agents | yes | 5/8 | The mark's fields permit a cross-citation and never say so |
| [a-conflict-has-no-rendering](a-conflict-has-no-rendering.md) | backend | -- | 3/4 | A conflict is detected and nothing renders it |
| [a-revise-answer-has-no-artifact](a-revise-answer-has-no-artifact.md) | backend | -- | 10/24 | A role can be asked to revise and has nothing to answer ON |
| [build-gate-crlf-fragile](build-gate-crlf-fragile.md) | systems | -- | 0/2 | build_plugin.py's raw byte compare fails on a line-ending-only difference introduced by a Windows git checkout |
| [shape-is-three-words](shape-is-three-words.md) | backend | yes | 0/6 | `shape` carries three senses, only one reaches an agent as a field name; and the axis it names is on `query` alone while `clean` has a recorded, unfilled need for the same thing |
| [prototype-move-orphaned-tasks](prototype-move-orphaned-tasks.md) | systems | -- | 0/4 | 25 open TODOs carry an unchecked task naming a module that moved to `prototype/` on 2026-08-25, so the task's site is gone and its verification cannot be run |
| [revise-copies-everything](revise-copies-everything.md) | backend | yes | 0/4 | `pull` copies `.git`, `.venv` and `corpora` into every revise root -- 284MB measured on this repo, per editorial stage, to set a docket over ~4MB of source |
| [sheet-rename-gate-cannot-see-the-source](sheet-rename-gate-cannot-see-the-source.md) | systems | -- | 0/2 | the gate's scope excludes the tree the retired sense actually survived in -- docs/gates.md: a check that could not have failed is not evidence |
| [doc-on-the-declaring-line](doc-on-the-declaring-line.md) | backend | -- | 2/4 | A docstring written on its declaration's own line takes no address, and the round trip invents a blank line |
| [brief-forbids-the-full-address](brief-forbids-the-full-address.md) | agents | -- | 0/3 | reviewer-brief.md:109 instructs the bare cue; the seeder writes the full address and the checker refuses a substantive mark without it |
| [brief-says-prose-is-withheld](brief-says-prose-is-withheld.md) | agents | yes | 0/3 | reviewer-brief.md:113 says the record withholds the prose so a role cannot rule without reading the code; flows/marks.py:81 puts raw_text on every mark and collator.py makes it load-bearing |
| [brief-says-three-series](brief-says-three-series.md) | agents | -- | 0/3 | reviewer-brief.md:69 and :221 say three series; reading/series.py ADDRESSED is ('a','b','c','f') and SKILL.md:378 says four, so a role cannot resolve the @f0 place the same brief tells it to cite |
| [skill-inverts-the-anchor-line](skill-inverts-the-anchor-line.md) | agents | -- | 0/2 | SKILL.md's CANDIDATE paragraph describes the opposite of the line commands/census.py prints, and the reasoning built on it is what the task agent carries into every proposal |
| [external-address-cites-dead-modules](external-address-cites-dead-modules.md) | backend | -- | 0/1 | desk/external_address.py says the address is declared in binder/record.py and resolved in desk/desk.py; record.py left on b50e7a4 and desk.py is in no directory of this tree |
| [no-command-for-the-middle](no-command-for-the-middle.md) | backend | -- | 6/12 | `gather`, `places`, `reconcile` and `docket_from` have no CLI face, so nothing turns checked marks into the docket `proof --docket` requires. Measured 2026-08-29 on a real run: every other step of the chain is a command; this one had to be driven from a hand-written script |
| [query-names-no-sentence](query-names-no-sentence.md) | backend | yes | 0/3 | every other substantive instruction names the sentence it rules on through a `claim` key -- `false` for `correct`, `drop` for `drop`, `from` for `patch` -- and `query` has none, so `_sentence_key` falls back to an identity and two queries at one place read as two different sentences |
| [brief-example-and-scope](brief-example-and-scope.md) | agents | -- | 0/3 | the brief's worked example shows a 40-character `sha` where `bind` writes 16, and the brief says a source resolves against 'the repo' without saying whether that is the scoped tree or the checkout it was cut from |
| [rows-of-derives-no-type](rows-of-derives-no-type.md) | backend | -- | 0/4 | `binder.rows_of` returns `list[dict]` where `docket.schedules_of` returns `list[Schedule]`; the codebase holds one example of each pattern, the typed one is the one that catches things, and `rows_of` has 8 callers and no covering tests |
| [strip-before-review-experiment](strip-before-review-experiment.md) | agents | yes | 0/5 | the `collator.py` prose was deleted whole and rewritten by an agent that could read only the code -- it found three defects the old prose never mentioned and named two things the code cannot say; whether that beats editing in place is untested |
| [collator-defects](collator-defects.md) | backend | yes | 7/29 | four defects in `desk/collator.py`, all found by an agent writing the file's prose from the code alone: a `move` onto its own address becomes a bare delete, a multi-line `verbatim` from a CRLF file can never match, the source cache is keyed without its root, and a malformed cite raises where the half is meant to report |
| [staged-chain-untested](staged-chain-untested.md) | backend | yes | 0/4 | the four-stage chain runs and the edits accumulate, proven 2026-08-30 -- but no test in the suite drives it, and the only committed fan-out topology refuses any tree but this repo's |
| [containers-and-verification-are-unwired](containers-and-verification-are-unwired.md) | backend | yes | 16/44 | The containers and the source-verification half are wired to nothing |
| [mark-holds-spec-and-parse](mark-holds-spec-and-parse.md) | backend | -- | 0/6 | mark.py holds the instruction spec and the boundary parse at one scope |
| [ty-cannot-see-the-tests](ty-cannot-see-the-tests.md) | systems (the gate) - backend (the test fixes) | -- | 1/5 | The type gate is scoped to src and cannot see the tests |
| [null-becomes-the-word-none](null-becomes-the-word-none.md) | backend | -- | 0/6 | A present-but-null key becomes the four characters None |
| [collate-flow-defects](collate-flow-defects.md) | backend | -- | 0/12 | Twelve defects in `flows/collate.py`, from a review of one file |
| [mark-defects](mark-defects.md) | backend | yes | 0/11 | Eleven defects in `desk/mark.py`, found by running its parse against its own prose |
| [binder-defects](binder-defects.md) | backend | yes | 0/18 | Eighteen defects in binder.py, and `read` admits four shapes it exists to refuse |
| [docket-defects](docket-defects.md) | backend | -- | 2/8 | Six defects in docket.py, and one discards an approved page at exit 0 |
| [collate-command-defects](collate-command-defects.md) | backend | -- | 3/19 | Sixteen defects in `commands/collate.py`, measured by running it |
| [differences-defects](differences-defects.md) | backend | -- | 0/10 | Ten defects in `results/differences.py`, none of them in its arithmetic |
| [plans-name-no-todo-tasks](plans-name-no-todo-tasks.md) | systems | yes | 0/4 | Six 0.2.4 plans carry no heading naming the TODO tasks they close |
| [index-and-glossary-for-roles](index-and-glossary-for-roles.md) | agents | yes | 0/1 | Hand a reviewer the name index and the glossary rather than leaving it to grep |
| [local-annotation-false-positive](local-annotation-false-positive.md) | systems | -- | 0/1 | check_shipped_syntax reads a local variable annotation as a forward reference |
| [stage-4b-is-undefined](stage-4b-is-undefined.md) | agents | -- | 1/6 | the 4a/4c split promises a resolved placement that nothing produces |
| [citations-resolve-to-no-object](citations-resolve-to-no-object.md) | systems | -- | 0/1 | Find the four commit citations that resolve to no object |
| [row-was-never-retired](row-was-never-retired.md) | backend | yes | 0/5 | Retire row everywhere -- the type, the wire key and the prose |
| [only-a-flow-reaches-the-machine](only-a-flow-reaches-the-machine.md) | backend | yes | 0/6 | Route every machine read and write through a flow |
| [a-non-code-document-has-no-read-review-resolve-or-write-chain-of-its-own](a-non-code-document-has-no-read-review-resolve-or-write-chain-of-its-own.md) | backend | -- | 0/2 | A non-code document has no read, review, resolve or write chain of its own |
| [re-review-is-retired-for-revise](re-review-is-retired-for-revise.md) | agents | -- | 0/5 | re-review is retired for revise |

### in-progress  (18)

| file | owner | roy? | done | what |
| --- | --- | :-: | ---: | --- |
| [compact-can-buy-lines-with-width](compact-can-buy-lines-with-width.md) | agents | -- | 2/8 | COMPACT can buy lines with width, and nothing stops it |
| [stage-1-is-re-derived-every-run](stage-1-is-re-derived-every-run.md) | agents | yes | 1/15 | Stage 1 is re-derived every run, asks one question twice, and knows one structure source |
| [the-bridge-landed-and-the-rewrite-did-not](the-bridge-landed-and-the-rewrite-did-not.md) | backend | -- | 8/11 | The bridge landed and the rewrite did not |
| [corpora-are-all-python](corpora-are-all-python.md) | testing | -- | 3/10 | The corpora are nine Python projects, so every per-language rule is measured on Python and C alone |
| [7a-can-prove-the-change-by-applying-it-to-a-copy](7a-can-prove-the-change-by-applying-it-to-a-copy.md) | agents | yes | 3/7 | 7a can PROVE the change by applying it to a copy and diffing |
| [a-block-is-a-paragraph-on-a-page](a-block-is-a-paragraph-on-a-page.md) | backend | -- | 3/11 | everything read by a human or an agent says paragraph; 706 internal identifiers remain |
| [b-addresser-uninitialised](b-addresser-uninitialised.md) | backend | yes | 13/18 | The b addresser is never initialised at the module trigger, and computes its cue from line numbers |
| [census-degrades-silently](census-degrades-silently.md) | backend | -- | 5/8 | **Four inputs produce a census that is wrong rather than refused, each exiting 0.** The run reads as complete and the addresses are nonsense. |
| [census-owns-addressing](census-owns-addressing.md) | backend | -- | 4/8 | The census owns addressing, and four modules share one subject between them |
| [page-and-addresser-scans](page-and-addresser-scans.md) | backend | -- | 2/8 | page.py and addresser.py carry four scans that grow with the file and one CLI that contradicts the gate |
| [record-verdict-desk-findings](record-verdict-desk-findings.md) | backend | -- | 9/14 | Round-4 findings in record/verdict/desk, including two that certify a run at exit 0 |
| [the-census-is-mostly-intervals-nobody-rules-on](the-census-is-mostly-intervals-nobody-rules-on.md) | backend | yes | 13/25 | **The census is 67% of what it costs to start a reviewer, and 966 of its 1,120 blocks are intervals nobody rules on.** 131,353 bytes of 195,243, paid four times. Roy ruled the design 2026-08-18: the census stays fully enumerated ON DISK, the agents get a FILTERED view, and a destination outside their set comes from a TOOL answering one question -- what is the ADDRESS of this line of code. ! It does not reverse the 2026-08-17 enumeration; it is a projection of it, and `add` was not expressible before it. ! Rule 4 buys a check as well as bytes: `move`'s `to` is free text nothing resolves, and an index is resolvable exactly as an address already is |
| [the-lexer-reads-no-files](the-lexer-reads-no-files.md) | backend | -- | 8/22 | one decision -- bytes into text -- made in nine places, none of them the lexer |
| [the-parser-merges-across-boundaries-it-cannot-read](the-parser-merges-across-boundaries-it-cannot-read.md) | backend | -- | 2/4 | The collator merges across a boundary it cannot read, and blames the neighbour |
| [the-read-only-contract-is-enforced-by-nothing](the-read-only-contract-is-enforced-by-nothing.md) | agents | yes | 2/8 | The read-only contract is enforced by nothing, and four reviewers wrote files |
| [the-shipped-python-does-not-pass-its-own-review](the-shipped-python-does-not-pass-its-own-review.md) | backend | yes | 7/12 | **Our own scripts spend a sixth of their prose on what the code does NOT do.** ! **Roy's reason, 2026-08-16: *"I don't want the system picking up bad cues from the documentation in the code."*** An agent reads these files and then writes in them. Re-measured after that day's rewrites: **136 of 697 (20%)** comment and docstring lines carry `cannot` / `never` / `does not` / `is not` / `nothing` -- UP from 123/714, because the prose written that day carries the same defect -- `census.py` worst at 52/284. Roy: *"census.py creates the pCST and that is it. Comments about 'cannot answer OWNERSHIP' are not helpful."* ! Not every negative is wrong -- an output (*"reports UNPROVABLE rather than passing"*) and a refusal aimed at a future editor both earn their place -- so the first task is writing the test that tells them apart !! **The hand-pass rule is STRUCK, 2026-08-18.** It told itself not to run `/comment-review` on this repo; Roy: *"By definition the code has to go through the review to state that it has passed."* A hand pass produces a rewrite, and this file's title is a claim about what the review RETURNS -- so it now closes on a run graded from the diff. ! The harness does not gate that: running the skill needs the skill |
| [lexer-and-language-findings](lexer-and-language-findings.md) | backend | -- | 3/29 | Ten findings in lexer.py and language.py, from three review rounds |
| [board-predates-task-ids](board-predates-task-ids.md) | systems | yes | 2/6 | task lines carry no ids, so a plan cannot name one; a trial migration was reverted because it silently cleared 57 `Requires-Roy` flags and refused nine files whose task labels carry a literal pipe |

### decision-needed  (25)

| file | owner | roy? | done | what |
| --- | --- | :-: | ---: | --- |
| [correct-against-patch-is-a-conflict-and-is-not-flagged](correct-against-patch-is-a-conflict-and-is-not-flagged.md) | agents | yes | 0/3 | `correct` against `patch` is a conflict, and the gate does not flag it |
| [role-rule-register](role-rule-register.md) | agents | yes | 0/5 | The register of proposed additions and amendments to the four editorial role files. ! Role prose is BUDGET-FIXED, so a candidate is not judged alone -- it is judged against what it would replace, which is why they collect here instead of landing one at a time. |
| [evidence-still-names-places-by-line](evidence-still-names-places-by-line.md) | testing | yes | 0/14 | **The address reached the record key and a `move`'s destination and stopped.** `SOURCES` -- the field the evidentiary contract rests on -- is 100% line-form, and Roy's `address:lines` ruling is unimplemented. Four other artifacts name a place by nothing at all. |
| [no-mark-for-let-it-stand](no-mark-for-let-it-stand.md) | agents | yes | 12/16 | There is no mark for LET IT STAND -- a declined proposal is not recorded, so the next run proposes it again |
| [front-half-undetermined](front-half-undetermined.md) | testing | yes | 5/11 | The census to findings to verdicts path has never been determined against a backend that works |
| [a-role-with-no-code-out-damages-the-prose](a-role-with-no-code-out-damages-the-prose.md) | agents | yes | 1/10 | `code_concerns` is defined in the shared brief that every role reads, but named in only ONE of the four reviewer files -- `function-context`. It is absent from `module-context`, whose whole remit is whether a module announces ONE subject, which is the finding that most needs a code out. MEASURED in the harness: `module-context-widens-a-two-subject-docstring` detected that `verdicts.py` holds four subjects, had no verdict for 'split this module', and emitted a prose `patch` widening the docstring to announce TWO -- the exact defect its own trigger is named for. `code_concerns` came back empty. |
| [dead-sweep-skips-private](dead-sweep-skips-private.md) | systems | yes | 4/5 | dead_sweep skips every _private name, so a dead module constant is invisible to it and to ruff |
| [lexer-does-not-lex](lexer-does-not-lex.md) | backend | yes | 7/10 | One module, two jobs: one tier reads characters, the other reads CPython's parse |
| [a-comment-run-merges-across-blanks](a-comment-run-merges-across-blanks.md) | backend | yes | 4/6 | A licence header and a doc comment become one paragraph with one address |
| [a-coverage-gap-should-go-back-to-the-reviewer](a-coverage-gap-should-go-back-to-the-reviewer.md) | agents | yes | 2/7 | **A block a reviewer never accounted for is unfinished work, not a finding about the run.** Today `verdicts.py` prints a COVERAGE GAP against the role by name and exits nonzero. Roy, 2026-08-16: *"if comment blocks are missed by a reviewer then they are returned to the reviewer to rule on."* ! Same shape as the two deleted lists one level up -- the reviewer stopped early, and the system files the stopping rather than fixing it. * Unruled: re-dispatch with only the missed indices or the whole census, and what bounds the retry |
| [a-prose-file-has-no-blocks](a-prose-file-has-no-blocks.md) | backend | yes | 4/9 | A prose file has no blocks, so the system cannot review documentation |
| [correcting-one-copy-strands-the-reference-copy](correcting-one-copy-strands-the-reference-copy.md) | agents | yes | 1/9 | Correcting one copy strands the copy in a REFERENCE ONLY file |
| [false-by-arithmetic-with-no-enforcing-line](false-by-arithmetic-with-no-enforcing-line.md) | agents | yes | 1/4 | A claim can be false by arithmetic with no enforcing line to check it against |
| [marketplace-resolves-live](marketplace-resolves-live.md) | systems | yes | 3/5 | A directory marketplace resolves the plugin LIVE, so a version-pinned measurement was never pinned |
| [nothing-checks-that-four-reviewers-were-launched](nothing-checks-that-four-reviewers-were-launched.md) | agents | yes | 1/6 | Nothing checks that four reviewers were LAUNCHED |
| [reference-only-misses-the-documentation](reference-only-misses-the-documentation.md) | agents | yes | 0/4 | REFERENCE ONLY misses the project's own documentation |
| [the-author-approves-blocks-and-never-sees-the-page](the-author-approves-blocks-and-never-sees-the-page.md) | agents | yes | 5/9 | * **Pipeline, not vocabulary.** 7a shows the author a per-block LIST; stage 8 is the only pass that reads the PAGE, and it runs AFTER 7b has written to disk. So every defect `review.md` exists to catch -- a block that is no longer a proposition, two runs merged across a blank line, the same sentence in two places -- is found after approval and after the write. Roy wants a whole-document read BEFORE the person sees it, and floated a temporary branch with the diff so they can accept it in git's own tools. Stage 8 then becomes a verification with two outcomes: good, or raise to human as a new review. ! Already done: the 7b paragraph claiming *"this pass cuts, and it can cut a lot"* is deleted -- self-contradicting since the import |
| [the-harness-cannot-run-the-system-it-grades](the-harness-cannot-run-the-system-it-grades.md) | testing | yes | 10/31 | **Nothing in this repo runs the documented eval format, and no measurement exists that a human did not perform.** `grade_hazards.py` scores worktrees a person built by hand against twelve planted defects, from a base hardcoded to another repository. Ruled 2026-08-18: a reduced role set is supported with `ownership-context` never dropped, and a fixture is a CHECKOUT AT A HASH -- this repo's own history included, since a fix commit is an answer key. ! NOT a release candidate: nothing here is under `plugins/`. * Unruled: the suite layout, which the fixture model narrows to one option |
| [the-strongest-precedence-has-the-weakest-support](the-strongest-precedence-has-the-weakest-support.md) | agents | yes | 2/4 | The role with verdict precedence has the least mechanical support |
| [the-two-lists-were-tuned-to-one-diff](the-two-lists-were-tuned-to-one-diff.md) | agents | yes | 3/9 | **Both lists are DELETED from the brief; this holds what was inside them.** The acquittal list matched a prose SHAPE and claimed to be *"the ONLY reasons to pass a block over"* -- but what decides `clean` is stated per role and is a TRUTH assertion at that role's scope, so the two disagreed outright. Its measurement was `evidence/ga/`: ten candidates over SIX `redacted_pkg` files, scored on F1 against what one later commit rewrote -- and the search itself concluded *"the acquittal RATE is the trait; the acquittal LIST is just vocabulary."* The suppression list had no provenance at all. ! Three entries were CHECKS wearing an exemption's name, one CONTRADICTS `function-context`, and `detector` -- a settled term -- lost its only definition |
| [two-live-runs-proposed-fifteen-changes](two-live-runs-proposed-fifteen-changes.md) | agents | yes | 11/21 | Two live runs proposed fifteen changes |
| [null-is-not-a-decision](null-is-not-a-decision.md) | backend | yes | 0/2 | `null` is the delete signal, and it is also what a failed serialisation writes |
| [strip-and-fill-the-markers](strip-and-fill-the-markers.md) | backend | yes | 0/9 | A role is handed the paragraph with its `#`/`"""` markers and indentation, and must reproduce them exactly in `change`. Measured 2026-08-29: three consecutive attempts by an agent with full context broke the file, and each failure read as a defect in the setter |
| [task-agent-vocabulary-home](task-agent-vocabulary-home.md) | agents (the instructions) - backend (the enum they derive from) | yes | 0/4 | The task agent has no vocabulary home and is never told the command set |
| [move-is-a-composite-mark](move-is-a-composite-mark.md) | backend | yes | 1/22 | A move is a composite mark and the code cannot express one |

### in flight  (0)

| file | owner | roy? | done | what |
| --- | --- | :-: | ---: | --- |

### blocked  (3)

| file | owner | roy? | done | what |
| --- | --- | :-: | ---: | --- |
| [code-concerns-cannot-carry-a-proposed-change](code-concerns-cannot-carry-a-proposed-change.md) | backend | yes | 0/9 | code_concerns is a bare list of strings, so a code problem reaches no gate |
| [docstrings-that-contradict-themselves](docstrings-that-contradict-themselves.md) | backend | -- | 2/12 | each states a rule and then denies it, in the same file |
| [isolate-the-codes-contribution](isolate-the-codes-contribution.md) | testing | -- | 4/10 | Two graded arms, orchestration held constant; the rewording is the confound |
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
| [anchor-was-empty-on-98-percent](completed/anchor-was-empty-on-98-percent.md) | SOLVED and the sweep it asked for found one. MEASURED 2026-08-23: 0 of 687 prose paragraphs carry no anchor, against 98 percent when this was filed. ! The last task -- look for the same shape in the other SEEDED fields -- ran in simplify round 7 and found `Finding.anchor`: filled from the record and read by neither `desk` nor the collator. It was cut |
| [verdicts-py-announces-one-subject-and-holds-four](completed/verdicts-py-announces-one-subject-and-holds-four.md) | The four subjects are separated -- desk.py, record.py, verdicts.py and held.py -- and the two dev-review findings inside the split are fixed and tested. Verified 2026-08-23 rather than assumed: record.check() guards a non-object report and a non-object record, and claim_keys is the one source with no hardcoded key names left. |
| [b-owns-the-blank-lines-SUPERSEDED](completed/b-owns-the-blank-lines-SUPERSEDED.md) | SUPERSEDED 2026-08-23. Roy: 'b doesn't own the blank lines any more.' The blanks went to LEADING, which is its own kind, holds the run the lexer found, and has given up its address -- the census prints it as '@  2-2  leading'. So the premise in the title is no longer true of the system. ! Task 8 WAS fixed on the way and is verified: page.recut takes only the free lines and tests/test_compositor.py:162 pins the cpython/Include/floatobject.h case. Task 7, the galley half, goes with the premise. What leading owes is TODO/leading-owns-the-space-between.md. |
| [the-rename-corrupted-live-prose](completed/the-rename-corrupted-live-prose.md) | All five sites restored 2026-08-23, and the CAUSE is fixed with them. The rename replaced a live sense of 'block' with 'paragraph' in four places the vocabulary gate flagged: the VERB in SKILL.md's verdict table and twice in compact.md, a PYTHON code block in module-context, and a JAVA TEXT BLOCK in prove_unchanged -- a language feature that does not exist under the new name. The agent file also told block-context its own role was PARAGRAPH-CONTEXT. ! Restoring the correct words trips the gate, which is why they were corrupted, so the four live senses are now declared in check_vocabulary.NOT_THE_TERM. Verified the gate still FAILS on a planted retired use. |
| [tier-dispatched-on-name-SUPERSEDED](completed/tier-dispatched-on-name-SUPERSEDED.md) | SUPERSEDED 2026-08-23 by language-rows-in-toml. Roy: "tier-dispatch-on-name actually falls under TODO/language-rows-in-toml.md -- once the languages.toml goes in the Python special case falls." Its measurements are folded into that file: the literal name test at language.py:394, the reader/label split between page.py:694 and :815/825 that can read a file at one tier and label it at the other, and the three further sites deciding is-this-Python their own way. ! Its proposed fix -- tier becomes a FIELD on the row -- is now part of task 7 there, and its re-measure criterion is task 8: no module outside language.py tests lang.name, and no module re-spells a suffix tuple. |
| [a-code-less-file-leaves-lines-unowned](completed/a-code-less-file-leaves-lines-unowned.md) | Both defects are fixed. Every line of a code-less file is owned (`addresser.py:426`) and `splitlines` is out of the reading path (`lexer.py:1160`). The third box said of itself *'Not a defect alone.'* |
| [front-matter-absorbed-by-an-interval](completed/front-matter-absorbed-by-an-interval.md) | Closed by the front/back-matter series. Five of the six boxes were the diagnosis -- an `add` on `b1` silently replaced a licence header at rc=0, caused by `fill_the_gaps` letting one interval span the matter -- and the sixth was a ruling already made. The defect it records was introduced by `4d576d3` and closed by giving matter its own series. |
| [leading-owns-the-space-between](completed/leading-owns-the-space-between.md) | The `d` series shipped. Ten of the eleven boxes were the ruling and its evidence, not work: `leading` is the trade word, it is NOT citable, and the letter is `d`. The eleventh -- leading still reaching a reviewer -- is fixed; `--filtered` emits no bare leading row. MEASURED over 3,082 files: 3,049 byte-identical, 3,075 identical ignoring trailing newline. |
| [not-every-line-has-an-address](completed/not-every-line-has-an-address.md) | The universal claim is gone and both downstream reasons are recorded beside the code. `addresser.py:18-19` now reads *'AN ADDRESS IS NOT A SPAN OF LINES. NO LINE HAS MORE THAN ONE'*, and `owes_address`'s docstring at `:1361-1377` carries Roy's ruling and what stops being determinable without it. Seven of the eight boxes were the measurement and the argument. |
| [retired-word-in-a-quote](completed/retired-word-in-a-quote.md) | The ruling arrived in `8141b7a` (Roy, 2026-08-23): a retired word inside a QUOTATION stays, because a shortened quotation is a different rule. `folio` joined `RETIRED` and `check_vocabulary.py:63-67` enforces it. All five boxes were the collision, the ruling, or the measurement -- none was work. |
| [strip-strings-runs-before-the-opener](completed/strip-strings-runs-before-the-opener.md) | The ordering defect is fixed and the rest was record. `_strip_strings` no longer runs ahead of the opener, and the annotation's reach was re-measured rather than re-argued. `/* don't */` was never a defect -- it is ordinary English inside a comment. |
| [the-xfails-never-reach-the-galley](completed/the-xfails-never-reach-the-galley.md) | All three superseded by the compositor split. `_gap` no longer looks a place up by `(original_start, original_end)`, the class docstring no longer claims an unexpected success, and plan box R7 -- *'no expectedFailure survives this plan'* -- is judgeable again because the galley stopped doing two jobs. |
| [foot-of-file-two-places](completed/foot-of-file-two-places.md) | The closing gap and the back matter both own prose at the foot, separated by a trailing leading -- the head rule in reverse. Roy ruled it 2026-08-26; decision-log.md Addressing: #19. |
| [notations-collides-with-annotations](completed/notations-collides-with-annotations.md) | The name is alteration; the write side has all three containers -- alteration, schedule, docket -- and the docket is its own area carrying each page's path and sha, so the binder no longer reaches the write chain. decision-log.md Vocabulary: #14. |
| [a-closing-quote-with-a-comment](completed/a-closing-quote-with-a-comment.md) | Fixed in paragraphs_stdlib -- a comment on a line a docstring owns is no longer a second paragraph. Both re-measurements verified 2026-08-29; the lexical Python reader was not needed. |
| [mark-is-a-dict-not-a-type](completed/mark-is-a-dict-not-a-type.md) | desk/mark.py now defines Mark and parses one at the boundary -- a dict becomes a Mark or named problems, with no third outcome. The ruling field is 'instruction', typed Instruction. Proved by the defect it ends: the shipped brief's own worked example went from problems_in ([], 0) -- silently discarded and recounted as a coverage gap -- to ([], 1), counted as ruled. |
| [change-is-raw-text-not-lines](completed/change-is-raw-text-not-lines.md) | desk/mark.parse takes `change` as raw text and refuses a list by name; the brief, docs/the-mark.md and the checker now agree, and the superseded line-array claim in the-fields-do-not-say-a-mark-may-cite-across T2 is corrected in place |
| [master-proof-and-edit-copy](completed/master-proof-and-edit-copy.md) | desk/proof.gather builds a master_proof of one stage's edit_copies and refuses a mismatched root; seed nests marks under one sheet per page, each carrying path and sha |
| [topology-is-a-source-edit](completed/topology-is-a-source-edit.md) | a run's stages are read from a TOML topology -- desk/topology.read, with three refusals -- and the STAGES literal and Stage.roles are deleted |
| [move-order-and-cycles-SUPERSEDED](completed/move-order-and-cycles-SUPERSEDED.md) | Filed as its own file in error; the three tasks are collator-defects T12, T13, T14 -- the per-module TODO for desk/collator.py, which already absorbs single-defect files |
| [read-from-never-compared-SUPERSEDED](completed/read-from-never-compared-SUPERSEDED.md) | Filed as its own file in error; the check is a task on no-command-for-the-middle, which is the TODO for the command that performs it |
| [move-change-contract-unenforceable-SUPERSEDED](completed/move-change-contract-unenforceable-SUPERSEDED.md) | Superseded by move-is-a-composite-mark: it names change_all, a classifier removed on 2026-08-29, and the dict-branch question it asks is answered by the composite ruling -- neither branch |
| [move-onto-itself-deletes](completed/move-onto-itself-deletes.md) | SUPERSEDED into collator-defects.md, which carries every task of this file since 9fc9272. Roy, 2026-08-30: the four single-defect files stand until the board migration lands and are superseded in one pass then; it landed at de8efcd |
| [crlf-verbatim-never-matches](completed/crlf-verbatim-never-matches.md) | SUPERSEDED into collator-defects.md, which carries every task of this file since 9fc9272. Roy, 2026-08-30: the four single-defect files stand until the board migration lands and are superseded in one pass then; it landed at de8efcd |
| [cache-keyed-without-root](completed/cache-keyed-without-root.md) | SUPERSEDED into collator-defects.md, which carries every task of this file since 9fc9272. Roy, 2026-08-30: the four single-defect files stand until the board migration lands and are superseded in one pass then; it landed at de8efcd |
| [cite-at-raises-on-a-nondigit](completed/cite-at-raises-on-a-nondigit.md) | SUPERSEDED into collator-defects.md, which carries every task of this file since 9fc9272. Roy, 2026-08-30: the four single-defect files stand until the board migration lands and are superseded in one pass then; it landed at de8efcd |
| [reviewers-are-not-read-only](completed/reviewers-are-not-read-only.md) | SUPERSEDED into the-read-only-contract-is-enforced-by-nothing.md, the same subject filed twice. T2 and T3 had homes there; the measurement was already recorded; the write-tool gate was carried across at da3576a before this file closed |
| [a-block-does-not-say-where-its-text-starts](completed/a-block-does-not-say-where-its-text-starts.md) | FINISHED -- the address carries its own start; the last open box wanted a field Process 69 deleted at d894894 |
| [a-page-carries-no-identity](completed/a-page-carries-no-identity.md) | FINISHED -- a page carries its sha, so staleness is a comparison rather than a re-parse |
| [addresser-answers-wrongly-at-exit-0](completed/addresser-answers-wrongly-at-exit-0.md) | FINISHED -- the addresser command no longer answers its three questions wrongly at exit 0 |
| [brief-change-is-raw-text](completed/brief-change-is-raw-text.md) | SUPERSEDED -- the form was ruled RAW TEXT, Vocabulary 27, and both the brief and desk/mark.py say it; closed 2026-09-02 against b9dce3d |
| [collate-buckets-a-move-at-one-end](completed/collate-buckets-a-move-at-one-end.md) | FINISHED -- collate groups a two-ended mark by every place it touches |
| [plans-unreadable-to-the-tool](completed/plans-unreadable-to-the-tool.md) | FINISHED -- the board reads docs/plans; INTEGRITY ISSUES and EXCLUDED FROM THE BOARD are both 0 |
| [the-flow-assumes-every-role-reads-at-once](completed/the-flow-assumes-every-role-reads-at-once.md) | FINISHED -- the flow no longer assumes one simultaneous read; a stage reads what the stage before it left |
| [the-ported-mark-does-not-fit-the-brief](completed/the-ported-mark-does-not-fit-the-brief.md) | FINISHED -- the mark accepts what the shipped brief tells a role to write |
| [ownership-is-read-first-but-nothing-makes-it-so](completed/ownership-is-read-first-but-nothing-makes-it-so.md) | SUPERSEDED into stage-4b-is-undefined T6 -- Process 75 supplies the mechanism this file proposed a PROPOSED-tag census for: 4b is the task agent running proof and census --revise 1, so 4c is seeded from 4a's revise. The serialisation ruling is kept in the Objective |
| [docket-role-is-per-page-not-per-alteration](completed/docket-role-is-per-page-not-per-alteration.md) | RULED -- role is ONE PER PAGE, answered by which copy was pulled from. Process 81; the per-alteration alternative and the omission-retirement are superseded with it |
| [annotate-belongs-in-concordance](completed/annotate-belongs-in-concordance.md) | moved to concordance/ 3c66c56; stale references corrected f9b2ba2 |
