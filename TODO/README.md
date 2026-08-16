# TODO — open tasks and pending decisions

One file per task. **A TODO is a work order, not an essay** — a header, a short Objective, and
checkboxes. Everything that is not the objective or a task is documentation, and the routing turns
on **whose behavior it describes**:

| the content | home |
| --- | --- |
| how **this system** behaves today, and any survey of it | [`docs/`](../docs/) |
| a prose defect in **someone else's codebase**, which this system is measured against | [`evidence/`](../evidence/) |
| one of the twelve planted hazards | [`evals/discriminators.md`](../evals/discriminators.md) |

⚠ **Those first two read alike and are not.** `evidence/` is the labeled failures the tool is
scored on — probe reports over a real codebase, the triage over them, `ga/ground_truth.py`.
A measurement of **the tool's own** prose is `docs/`, however much it looks like a finding. The
vocabulary survey was filed under `evidence/` once for exactly that reason and moved.

The TODO keeps a one-line link from its Objective and nothing else. If nobody would read it
again, delete it — a TODO is not an archive.

**File names are kebab-case and say the thing, not the category.**
`eight-terms-have-no-definition-and-angle-means-five-things.md`, not `vocabulary-cleanup.md`. The
name is what shows in the table below, so it does the work of a summary.

**The BOXES are the source of truth; `Progress:` is Roy's read-out and is what he assigns work
from.** Tick the box and bump the count **in the same edit, every time** — and the `N/M` cell in
the table below with it. A stale-low count does not look untidy; it manufactures a wrong
instruction, because he asks for work already done and the session burns context discovering that.

⚠ **Nothing checks that arithmetic here.** In `redacted_corpus` a test
(`scripts/tests/test_todo_counts_agree.py`) fails when a file's `Progress:` disagrees with its
boxes or with its row here. This repo has no equivalent, no `todo_tool.py`, and no `completed/`
directory yet — those exist there because that backlog runs to ~120 open files, and one file does
not earn them. Port them at the point where hand-arithmetic starts being wrong, not before.

**`completed/`** will hold finished work when there is any, kept as the record. A file named
`*-SUPERSEDED.md` was **not implemented and is no longer necessary** — the reason goes in the file.

**Status values in use here:**

| value | means |
| --- | --- |
| `open` | nobody has started it |
| `in-progress` | work has genuinely started — some boxes ticked, not blocked, not waiting on a decision |
| `decision-needed` | waiting on Roy; the file names what he has to rule on |
| `blocked` | the task is real, it is not done, and doing it now is wrong because a named change must land first. The `Status:` line names what it waits on |
| `done` | every box ticked; the file moves to `completed/` |

**Owner** is `Roy` or `session`. This repo has no lane split — there is one codebase and one
shipped plugin, so the only distinction that changes what happens next is whether a task needs a
ruling or needs typing. A file may name both.

---

## The TODO file template

There is no `conventions.md` here, so this is the one definition.

````markdown
# {Title — the task, and the one thing that makes it matter}

```
Status:   open | in-progress | decision-needed | blocked (on what) | done
Progress: {done} of {total} tasks done
Owner:    session | Roy | both (say which tasks)
Raised:   YYYY-MM-DD (where it came from)
```

## Objective

{Two to six sentences. What has to become true, and why — the CONCLUSION the evidence
already reached, not the evidence. One link out if a reader needs the working.}

## Tasks

- [ ] {one action, and you can tell by looking whether it is done}
- [x] {done YYYY-MM-DD — `commit`, plus one clause only if the outcome changed the plan}
````

Rules that keep it that shape:

- **The Objective is prose and it is short.** Growing tables or headings means it has become a
  document; split it out to its home in the table above and link it.
- **A task is checkable or it is not a task.** "Clean up the vocabulary" is a project; the
  checkbox names the file, the grep that must come back empty, or the ruling that must exist.
- **The checkboxes ARE the record — no `## Response` section.** Tick with a date; the header's
  status summarizes the boxes.
- **⭐ marks a task that needs Roy before anyone can act on it**, so the ones that gate the rest
  are visible without reading the file.
- Same reason as this repo's own rule against unfalsifiable prose: a task you must re-read the
  evidence document to act on has deferred the decision to the moment of least willpower.

---

## What to do next — re-derived 2026-08-15, third pass

⚠⚠ **SETTLE WHAT A TERM MEANS. DO NOT MOVE IT.** Roy, 2026-08-16: *"once we get the vocabulary
resolved we will fix how to get the vocabulary to the correct places for each of the agents to
use. Please do not propose moving them until this is done else you might take the initiative and
then duplicate the vocabulary issues."* Distribution is its own pass, and it is the ⭐ *"give the
agents a copy of the definitions"* in
[`an-editorial-mark-is-not-an-action-and-reanchor-is-move`](an-editorial-mark-is-not-an-action-and-reanchor-is-move.md).
Until it runs, state a term **in place** — in a sentence that already describes it — and record
a placement problem as an OBSERVATION, never act on it. Moving a definition now either copies it
or lands it somewhere the distribution pass has to undo, which is the defect this branch exists
to remove.

⚠ **Re-derive this after anything lands.** Written fresh each time, not accumulated — a stale
branch status here is the same failure the box/`Progress`/table rule guards against, one level up.

Everything below is on `feat/settle-the-vocabulary`, 29 commits, `main` untouched.

1. **⭐ The record: two rulings, and they are the only thing gating it.** `query` has no
   `SOURCE` by design — where does attempted/would-settle go? And `add` has no block of its own
   yet `BLOCK` is required. The shape itself is ruled and the worked examples are in the file.
2. **The record's real prize is not the cut.** `REASON` is the field the `move` ruling rests
   on and **nothing checks it**; `LOCATION` was checked only for resolvability, never against
   the block it names. Replacing it with a `CLAIM`-against-census cross-check is strictly
   stronger and costs no new machinery.
3. **The vocabulary is down to three polysemy rows** — `residue`, `SUPPRESSED` and `label` —
   then the closing re-sweep. `own`/`owner`/`ownership` is settled (`HOME` retired, the census
   records ANCHORS), `jurisdiction` is the new word for a role's categories of claim, and
   `worktree` is git's word, not this system's.
4. **⚠ The survey is a floor, not a census.** `budget` was used at 18 sites in four senses and
   appeared in NEITHER table of the inventory — Roy found it reading a justification. Assume
   other terms are missing the same way; do not treat "109 terms" as coverage.
5. **The pCST rebuild is follow-up, not this branch.**
   [`an-empty-interval-has-no-census-index`](an-empty-interval-has-no-census-index.md) holds it:
   the block DEFINITION is settled and shipped, but the census still enumerates from prose, so
   an empty interval has no index. That is what `add` is waiting on, and it is a census change,
   not a naming one.
6. **⚠ Two measured gaps are recorded and unowned.** `docs/limitations.md` now records that the
   budget covers 28 KB of the 224 KB shipped and not the two largest files a run loads
   (`reviewer-brief.md` 18 KB, loaded once per reviewer; `SKILL.md` 47 KB). And the level ladder
   was invented during the Aug-14 port — it exists at zero commits in `redacted_corpus`, on
   any branch — with one budget argument as its whole justification. Roy has ruled the ladder is
   **not** a vocabulary question, so it needs a home of its own before it can be acted on.

**Landed 2026-08-15 on `main`:** 0.1.2 (`4a62b93`) — the four reviewer agents renamed for scope,
each stating what its own `clean` asserts, and the placement precedence. Then `8c7d81d`, the
vocabulary survey.

**The rulings on `feat/settle-the-vocabulary`** — 29 commits in all; the table lists the
ones that changed a published name or rule:

| commit | what |
| --- | --- |
| `ef4f33b` | `sweep` retired (7b is APPLY), `angle` retired (editorial role / reviewer), eight facts reconciled |
| `599e20e` | `reanchor` collapsed into `move` — eight verdicts, availability and synthesis order key on the destination |
| `764b1a7` → `da06046` | `budget` settled, then **corrected**: it is what a shipped file costs to load, not the reviewer's runtime |
| `f1a3cc5` | reviewers no longer receive `CAP` or `WIDTH` — the packet gate had been enforcing the opposite of the stated rule |
| `4d3b7a2` → `e9b2ff3` | `DOC CONVENTION` settled — stage 1.3 MEASURES the repo's formats instead of naming a standard |
| `9a84c6f` | `HOME` retired; **owner** is the anchor with the best justification, and `Block.owner` became `Block.anchor` |
| `f40d26b` | a role's categories of claim are its **JURISDICTION**; the anchor sweep finished |
| `f20d376` → `dd4e55a` | absence left `ownership-context` — missing documentation is `module-context`'s or `function-context`'s, by scope |
| `02a51d2` | dropped *"no role may emit another's verdict"* — it contradicted the overlap ruling |
| `ab1bae0` | `worktree` settled: git's word, not a term of art here |

167 tests pass, `ruff check` clean, 5 shipped files parse on 3.9.

---

## Open

### open  (7)

| file | owner | done | what |
| --- | --- | ---: | --- |
| [the-two-lists-were-tuned-to-one-diff](the-two-lists-were-tuned-to-one-diff.md) | session · Roy (2 rulings) | 0/7 | **Both lists are DELETED from the brief; this holds what was inside them.** The acquittal list matched a prose SHAPE and claimed to be *"the ONLY reasons to pass a block over"* — but what decides `clean` is stated per role and is a TRUTH assertion at that role's scope, so the two disagreed outright. Its measurement was `evidence/ga/`: ten candidates over SIX `redacted_pkg` files, scored on F1 against what one later commit rewrote — and the search itself concluded *"the acquittal RATE is the trait; the acquittal LIST is just vocabulary."* The suppression list had no provenance at all. ⚠ Three entries were CHECKS wearing an exemption's name, one CONTRADICTS `function-context`, and `detector` — a settled term — lost its only definition |
| [the-unit-of-review-is-the-statement-not-the-block](the-unit-of-review-is-the-statement-not-the-block.md) | session · Roy (1 ruling) | 0/5 | **A block ADDRESSES a finding; a statement is what is RULED.** Roy, 2026-08-16: *"each sentence/statement is under review not the 'block'"* — and a statement can be dropped or moved out, not only added. Three files disagree on whether two statements in one block are two findings: the brief says *"exactly once"*, `SKILL.md:44` says *"several verdicts per role per block"*, and `verdicts.py:266-268` uses a SET, accepting both silently. ⚠ Neither direction is enforced — `coverage_gaps` reports only what is MISSING, so a block that is both found and `CLEAN` passes too |
| [the-author-approves-blocks-and-never-sees-the-page](the-author-approves-blocks-and-never-sees-the-page.md) | session · Roy (5 rulings) | 1/9 | ⭐ **Pipeline, not vocabulary.** 7a shows the author a per-block LIST; stage 8 is the only pass that reads the PAGE, and it runs AFTER 7b has written to disk. So every defect `review.md` exists to catch — a block that is no longer a proposition, two runs merged across a blank line, the same sentence in two places — is found after approval and after the write. Roy wants a whole-document read BEFORE the person sees it, and floated a temporary branch with the diff so they can accept it in git's own tools. Stage 8 then becomes a verification with two outcomes: good, or raise to human as a new review. ⚠ Already done: the 7b paragraph claiming *"this pass cuts, and it can cut a lot"* is deleted — self-contradicting since the import |
| [the-harness-leaks-into-the-shipped-rules](the-harness-leaks-into-the-shipped-rules.md) | session | 1/5 | **Our eval rig is not the user's environment.** Six shipped sites justified absolute paths with *"a relative one does not resolve from a worktree"* — but a worktree is how `grade_hazards.py` isolates a graded run. ⚠ A right rule with a WRONG reason is worse than one with no reason: a reader who tests it in an ordinary checkout finds it does not fail, drops the rule, and only then do subagents break. Fixed. Open: sweep for the rest, since the same shape has already surfaced twice by other routes (the level ladder's budget argument, and 7b's *"this pass cuts"*) |
| [the-shipped-python-does-not-pass-its-own-review](the-shipped-python-does-not-pass-its-own-review.md) | session | 0/6 | **Our own scripts spend a sixth of their prose on what the code does NOT do.** Measured 2026-08-16 over `plugins/**/*.py`: **123 of 714** comment and docstring lines carry `cannot` / `never` / `does not` / `is not` / `nothing` — `census.py` worst at 52/284. Roy: *"census.py creates the pCST and that is it. Comments about 'cannot answer OWNERSHIP' are not helpful."* ⚠ Not every negative is wrong — an output (*"reports UNPROVABLE rather than passing"*) and a refusal aimed at a future editor both earn their place — so the first task is writing the test that tells them apart |
| [an-empty-interval-has-no-census-index](an-empty-interval-has-no-census-index.md) | session · Roy (1 ruling) | 0/9 | **FOLLOW-UP, deliberately off the vocabulary branch.** A block is the interval between two code lines (settled), but the census still enumerates from PROSE — three adjacent code lines census as **0 blocks**, so an empty interval has no index and `add` has no block to cite. Roy ruled **(a)**: enumerate every interval, empty ones included — *"I don't see a way around this pseudo-concrete syntax tree and I don't think it matters"*. Measured: `census.py` is 59 blocks today against ~606 code lines. ⚠ Not a budget question — run data is not budgeted. ⚠ Check first what a tenfold index count does to the `CLEAN 1-N` fabrication the brief already warns about |
| [the-finding-record-is-eight-fields-and-six-would-do](the-finding-record-is-eight-fields-and-six-would-do.md) | session · Roy (1 ruling) | 0/8 | ⭐ The record shipped with **five** fields and has **eight** — `BLOCK`, `EVIDENCE` and `QUOTE` were all added to serve the GATE, not the reviewer. Six carry it, and the shape is ruled: `BLOCK`, `VERDICT`, `CLAIM`, `SOURCE`, `REASON`, `CHANGE`, opener `--- RECORD` so the record stops sharing a name with its own field. ⚠ **The cut is not the point.** `REASON` is what the `move` ruling rests on and **nothing checks it**; `LOCATION` was checked only for resolvability, never against the block it names — the gate takes only `len(blocks)` from the census. Replacing it with a `CLAIM`-against-census cross-check is strictly stronger. Open: `query` (no `SOURCE` by design) and `add` (no block of its own). Worked examples for every verdict are kept in the file |

### in-progress  (3)

| file | owner | done | what |
| --- | --- | ---: | --- |
| [apply-names-both-stage-5-and-stage-7b](apply-names-both-stage-5-and-stage-7b.md) | session | 5/6 | **DONE 2026-08-15 — Roy ruled B: stage 5 is `APPLY`, stage 7b is `WRITE`, `EDIT` retired.** `apply` had come to name both — applying a MARK to produce text (5) and applying approved text to disk (7b). ⚠ The tell: `SKILL.md:51-52` already said "apply the true/false pair" and "apply the rewrite" for STAGE 5 work, so those sites needed no change at all once 5 took the name. `references/apply.md` → `write.md`, published as a breaking change. One box left: the inventory's Stages table still carries 7a and 7b as one row |
| [an-editorial-mark-is-not-an-action-and-reanchor-is-move](an-editorial-mark-is-not-an-action-and-reanchor-is-move.md) | session · Roy (2 rulings left) | 9/13 | **DONE 2026-08-15: `move` is the one relocation verdict.** Roy ruled the name and the reasoning: the record already carries `LOCATION` and `FINDING`, so `move` says *this comment belongs to that line there* as its reason — and that IS reattachment. `reanchor` was encoding in a second verdict word what the record has fields for. Availability and synthesis order now key on the DESTINATION, which is what removed the measured loss rather than guarding it. Eight verdicts, not nine. **STILL OPEN:** the other half of this file — an edit mark is not an ACTION (it is the preferred action that, *if applied*, would improve the prose; the action happens once, at 7b), plus ⭐ whether `drop`/`patch`/`add`/`split` follow `move`'s reasoning and ⭐ where the agents get their copy of the definitions |
| [eight-terms-have-no-definition-and-angle-means-five-things](eight-terms-have-no-definition-and-angle-means-five-things.md) | session · Roy (2 rulings left) | 14/18 | ⚠ MEASURED 2026-08-15 by twelve agents over the whole live tree: terms used with a fixed sense and defined nowhere (`angle` at ~40 sites in `SKILL.md` alone, plus `prose tree` in both manifests' install-time text, `the join`, `detector`, `banner`, `assessability gate`, `acquittal rate`), and fifteen more carrying two or three senses each. A word may mean several things **if each is clarified up front**, which none are. Also holds the one-edit reconciliations the collection turned up — a "Five fields" docstring against eight declared, "5 of its 7 reviewer reports" against a population fixed at four, four different base refs for one eval tree, two dead paths in `evals.json`. **Settled 2026-08-15 and applied: `sweep` is not a term (stage 7b is APPLY, dead import fixed), and `angle` is retired — prose says `editorial role`, identifiers say `reviewer`.** Survey: [`docs/vocabulary-usage.md`](../docs/vocabulary-usage.md) |

### decision-needed  (0)

_None — the remaining rulings sit inside the two files rather than blocking them entirely; the
other tasks can proceed without them._

### blocked  (0)

_None._

---

## Completed

Kept as the record. **`-SUPERSEDED` means it was never implemented and no longer needs to be** —
the reason is inside the file.

_None yet._
