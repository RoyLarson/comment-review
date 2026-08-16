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

## What to do next — re-derived 2026-08-15, second pass (post-0.1.2 merge)

⚠ **Re-derive this after anything lands.** Written fresh each time, not accumulated — a stale
branch status here is the same failure the box/`Progress`/table rule guards against, one level up.

1. **⭐ The remaining half of the collapse file: an edit mark is not an ACTION.** The verdicts
   still name operations — `drop`, `patch`, `add`, `move`, `split` — while a verdict is a mark
   that says what WOULD be done if applied. Two rulings sit here: whether the other four follow
   `move`'s reasoning, and where the agents get their copy of the definitions.
2. **⚠ `mark` carries four senses and blocks that work.** Before "edit mark" can be written as
   a term, check it lands clear of the census's mechanical annotations, stage 4's name, and a
   detector — or give one of those a different word.
3. **Six rulings are open across the two files** and none of them blocks the other's typing
   work. Three in the collapse file — the verdict name, whether `drop`/`patch`/`add`/`split`
   follow, and where the agents get their copy of the definitions. Three in
   `eight-terms-have-no-definition-and-angle-means-five-things` — which of **`HOME`**'s three
   readings is real, whether **`SKILL.md:488`** means reviewers write text, and four
   enforcement gaps where a script accepts what the prose does not.
4. **Tier 0 is done.** `angle` and `sweep` are both retired and applied. What the rename
   turned up and did NOT fix: `REVIEWER FILES`'s hint still holds seven paths (four roles plus
   the brief and two agents) under a name that reads as four, and `--reviewers` is still
   compared to file stems rather than to the four published role names — both now sit in the
   enforcement-gap ruling below.
5. **Settle a name before deciding where definitions live, and settle pointed-at names first.**
   Roy's ordering, 2026-08-15: cleaning the semantics comes before routing them to a home, or
   the routing writes pointers to words that are about to change — which is how `import sweep`
   happened. A term can only dangle if something POINTS at it, so:
   **Tier 0**, names living in identifiers, filenames and flags, where dangling breaks a program
   — `angle` and `sweep` are both done, which empties this tier.
   **Tier 1**, the verdict vocabulary, which appears in reviewer output and the gate.
   **Tier 2**, judgment words inside agent prose — `HOME`, `mark`, `load-bearing`, `obituary`,
   `guard`. **Tier 3**, terms nothing points at and that therefore cannot dangle — `the join`,
   `detector`, `banner`, `assessability gate`, `acquittal rate`, `prose tree`. Safe to do last.

**Landed 2026-08-15:** 0.1.2 merged to `main` (`4a62b93`) — the four reviewer agents renamed for
scope, each stating what its own `clean` asserts, and the placement precedence between
`ownership-context` and `function-context`. Gate green on the merged result. Then `8c7d81d` — the
vocabulary survey both files below work from, written to `docs/` rather than `evidence/`.

**Uncommitted, 2026-08-15 — both Tier 0 rulings applied, one CHANGELOG entry covering them:**

- **`sweep` is not a term.** Stage 7b is **APPLY** at all 12 term sites; the 5 plain-English
  uses kept; `import sweep` → `import census` in `evals/generator_split.py`, so it runs again.
- **`angle` is retired.** Prose says **editorial role**, identifiers say **reviewer** —
  `--angles` → `--reviewers`, `ANGLE FILES` → `REVIEWER FILES`, `angle = path.stem` →
  `reviewer`. Clean break, no alias. ~250 sites across the plugin, both manifests, `tests/`,
  `README.md`, `CLAUDE.md` and `docs/`. The four agent files stayed at their
  `docs/limitations.md` budget (101/101/129/120, re-checked against `wc -l`).

167 tests pass, `ruff check` clean, 5 shipped files parse on 3.9, both CLIs smoke-tested.

⚠ **The file name `eight-terms-…-angle-means-five-things` is now wrong twice over** — it was
nine undefined terms, not eight (two are now settled, leaving seven), and `angle` carried six
senses, not five. Renaming the file is Roy's call; it is linked from `docs/vocabulary-usage.md`
and from this table.

---

## Open

### open  (0)

_None — both files are in progress._

### in-progress  (2)

| file | owner | done | what |
| --- | --- | ---: | --- |
| [an-editorial-mark-is-not-an-action-and-reanchor-is-move](an-editorial-mark-is-not-an-action-and-reanchor-is-move.md) | session · Roy (2 rulings left) | 9/13 | **DONE 2026-08-15: `move` is the one relocation verdict.** Roy ruled the name and the reasoning: the record already carries `LOCATION` and `FINDING`, so `move` says *this comment belongs to that line there* as its reason — and that IS reattachment. `reanchor` was encoding in a second verdict word what the record has fields for. Availability and synthesis order now key on the DESTINATION, which is what removed the measured loss rather than guarding it. Eight verdicts, not nine. **STILL OPEN:** the other half of this file — an edit mark is not an ACTION (it is the preferred action that, *if applied*, would improve the prose; the action happens once, at 7b), plus ⭐ whether `drop`/`patch`/`add`/`split` follow `move`'s reasoning and ⭐ where the agents get their copy of the definitions |
| [eight-terms-have-no-definition-and-angle-means-five-things](eight-terms-have-no-definition-and-angle-means-five-things.md) | session · Roy (4 rulings left) | 9/15 | ⚠ MEASURED 2026-08-15 by twelve agents over the whole live tree: terms used with a fixed sense and defined nowhere (`angle` at ~40 sites in `SKILL.md` alone, plus `prose tree` in both manifests' install-time text, `the join`, `detector`, `banner`, `assessability gate`, `acquittal rate`), and fifteen more carrying two or three senses each. A word may mean several things **if each is clarified up front**, which none are. Also holds the one-edit reconciliations the collection turned up — a "Five fields" docstring against eight declared, "5 of its 7 reviewer reports" against a population fixed at four, four different base refs for one eval tree, two dead paths in `evals.json`. **Settled 2026-08-15 and applied: `sweep` is not a term (stage 7b is APPLY, dead import fixed), and `angle` is retired — prose says `editorial role`, identifiers say `reviewer`.** Survey: [`docs/vocabulary-usage.md`](../docs/vocabulary-usage.md) |

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
