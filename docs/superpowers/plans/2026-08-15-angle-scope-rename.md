# Angle Scope Rename Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

!! **THIS PLAN IS FINISHED. Audited 2026-09-02; every box was open and 41 of 43 had
landed.** It shipped as release **0.1.2** on 2026-08-15 -- branch
`feat/angle-scope-rename`, merged at `a3c200a`, recorded in `CHANGELOG.md` at
`c76f238`. Each task below carries the commit that delivered it. Nothing was ticked at the time, which is the failure
`CLAUDE.md` names: superpowers authors the boxes and never closes them.

! **Its VOCABULARY has since been overtaken and its boxes are not re-openable by that.**
`angle` is retired (`e09c53d`), `verdict` is struck for `instruction` (`3e47286`), the
level ladder Task 7 edited was removed entirely (`f1b20d7`), and `reanchor` and `split`
collapsed into `move` (`94983c8`, `8dacb0a`). The work landed; the artifacts moved on.

**Goal:** Rename the four reviewer angles to name the scope each one checks, and close the
gaps between what `README.md` says each angle checks and what its agent file actually does.

**Architecture:** The four angles become a scope series with one dispatcher.
**Ownership-context** decides where a claim belongs; **Block-context**, **Function-context**
and **Module-context** each check a claim against the code at their scope. That ordering is a
dependency, not a preference -- a claim measured against the wrong scope produces a confident
wrong verdict, so placement resolves first. The rename is mechanical and provable by grep; the
content additions come from `README.md`'s own criteria, which the agent files never
implemented.

**Tech Stack:** Markdown agent definitions, `SKILL.md` and `references/*.md` prose, plus
`verdicts.py`'s `--angles` handling and `tests/test_verdicts.py`. Stdlib `unittest`.

**Spec:** `README.md`'s "## What" section -- the four criteria and their sub-bullets -- is the
specification this plan implements. It currently states checks no agent performs; that gap is
the reason for tasks 3-6.

## Global Constraints

- **The four new names, used everywhere with no survivors of the old:**
  `ownership-context`, `block-context`, `function-context`, `module-context`.
  Agent files become `comment-review-ownership-context.md` and so on; the namespaced IDs
  become `comment-review:comment-review-ownership-context` etc.
- **The rename must land atomically.** `SKILL.md` stage 1.6 probes the agent IDs, `verdicts.py
  --angles` matches report-file stems against them, and `run_context.py`'s packet lists the
  angle files. A half-rename breaks dispatch.
- **`docs/limitations.md` caps prose PER FILE.** Current agent sizes: ownership 81, block 79,
  function 114, module 96 lines. **At budget a new rule REPLACES one**, and if two rules are
  instances of one generalization, write the generalization and delete both. Every addition in
  tasks 3-6 must answer: would it fire in a repo about something else; is its evidence a number
  or ratio rather than a story; does it change what a reviewer does.
- **When paying the budget, cut the OVERFIT before the general.** The four agent files carry
  eleven `Measured:` instances. A short ratio is what `docs/limitations.md` asks for and stays
  -- *"a constraint restated in six places"*, *"548 blocks"*, *"ten mentions... missed an
  eleventh"*. What goes is the instance that carries a ratio **and** a narrative of one
  incident in one repository: `README.md` already records that the mechanical detectors "were
  fitted to the codebase the tool grew up in", firing ~70 times across seven corpora for about
  two real findings, so a rule illustrated by that codebase's specifics is the least
  transferable line in the file. Task 5 does this to the `abs()` material and gives the exact
  replacement; apply the same test in tasks 3, 4 and 6 rather than trimming whatever is
  nearest.
- **A rule belongs in exactly one file.** The duplication rule is being split between two
  angles in Task 2; that split must be written down in both places or they drift.
- **Do not restate a reference document in an agent file.** Agent files point; `reviewer-brief.md`
  and the `references/` docs hold shared contract.
- **No subjective statements about the project.** State what is checked, not that a check is
  good. `clean` is a reserved verdict word and must not be used as an adjective.
- Suite must stay green: `python -m unittest discover -s tests -v` (167 tests at plan time).
  Gate: `ruff check . && ruff format . && python scripts/check_shipped_syntax.py`.

---

## Task 1: Rename the four angles

**Landed:** `753d0bc` -- the four agent files renamed with `git mv` (rename detection
confirms history followed), each frontmatter `name:` and body opener changed, 16 files
updated including `verdicts.py`, `census.py`, `run_context.py`, `plugin.json`,
`docs/parsing.md` and the two test files. `git grep -i` for the four old names at that
commit returns nothing outside `corpora/`, `evidence/` and `docs/superpowers/plans/`.
`3e68b44` carried the pre-flight defects. ! `evals/discriminators.md` is named in the
file list and exists at no commit in this repo's history.

**Why:** The names describe the classification's origin rather than what each angle checks.
The new names state the scope, which makes the series and its ordering visible.

**Files:**
- Rename: `plugins/comment-review/agents/comment-review-locality.md` -> `comment-review-ownership-context.md`
- Rename: `comment-review-currency.md` -> `comment-review-block-context.md`
- Rename: `comment-review-functionality.md` -> `comment-review-function-context.md`
- Rename: `comment-review-module-coherence.md` -> `comment-review-module-context.md`
- Modify: `plugins/comment-review/skills/comment-review/SKILL.md`
- Modify: `plugins/comment-review/skills/comment-review/references/reviewer-brief.md`
- Modify: `plugins/comment-review/skills/comment-review/references/apply.md`
- Modify: `plugins/comment-review/skills/comment-review/scripts/verdicts.py`
- Modify: `plugins/comment-review/.claude-plugin/plugin.json`
- Modify: `tests/test_verdicts.py`
- Modify: `README.md`, `CLAUDE.md`, `evals/discriminators.md`
- Modify: `docs/parsing.md` -- carries `LOCALITY` at the "never improvise a parse" section

! **`docs/parsing.md` is easy to miss** -- it is the only file outside `plugins/` and the
top-level docs that names an angle, and it names it in caps mid-sentence.

**Interfaces:**
- Produces: agent IDs `comment-review:comment-review-{ownership,block,function,module}-context`.
  Task 7 wires the level table to these; Task 8 documents them.

- [x] **Step 1: Rename the files with git so history follows**

```bash
cd plugins/comment-review/agents
git mv comment-review-locality.md comment-review-ownership-context.md
git mv comment-review-currency.md comment-review-block-context.md
git mv comment-review-functionality.md comment-review-function-context.md
git mv comment-review-module-coherence.md comment-review-module-context.md
```

- [x] **Step 2: Update each agent's frontmatter `name:` to match its filename stem**

The `name:` must equal the filename stem or the agent will not resolve. In each file set:

```yaml
name: comment-review-ownership-context
name: comment-review-block-context
name: comment-review-function-context
name: comment-review-module-context
```

- [x] **Step 3: Update the first line of each agent body**

Each begins `You are the LOCALITY reviewer for a comment review.` and so on. Change to:

```markdown
You are the OWNERSHIP-CONTEXT reviewer for a comment review. You are READ-ONLY.
You are the BLOCK-CONTEXT reviewer for a comment review. You are READ-ONLY.
You are the FUNCTION-CONTEXT reviewer for a comment review. You are READ-ONLY.
You are the MODULE-CONTEXT reviewer for a comment review. You are READ-ONLY.
```

- [x] **Step 4: Replace every remaining reference across the repo**

Locate by content, not line number. The old words appear ~101 times across 13 files. Work
file by file and read each hit in context -- several are English rather than the angle name
(for example `README.md`'s "currency" in prose about corpora, if any). Do not blind-replace.

Run this to enumerate before and after:

```bash
grep -rn -io "currency\|functionality\|module-coherence\|module coherence\|modularity\|locality" \
  --include="*.md" --include="*.py" --include="*.json" . \
  | grep -v "^./corpora\|^./evidence\|__pycache__\|superpowers/plans" | wc -l
```

!! **`docs/superpowers/plans/` is excluded and must stay excluded.** Both plan files there
contain the old names throughout, in the "Why" sections that explain what is being renamed and
in this very step. They are a historical record of a decision, not live rules -- editing them
would rewrite the reasoning to match its own outcome. Measured now, before the rename: **193
occurrences repo-wide, 127 once the plans are excluded** -- so 66 of them are plan text you
must not touch. Work only on the 127.

- [x] **Step 5: Verify no survivors**

```bash
grep -rn -i "currency\|functionality\|module-coherence\|modularity\|locality" \
  --include="*.md" --include="*.py" --include="*.json" . \
  | grep -v "^./corpora\|^./evidence\|__pycache__\|superpowers/plans"
```
Expected: **no output.** (`docs/superpowers/plans/` holds this plan and the previous one and
is excluded -- those are historical records, not live rules.)

- [x] **Step 6: Verify the suite and gate**

```bash
python -m unittest discover -s tests -v
ruff check . && ruff format . && python scripts/check_shipped_syntax.py
```
Expected: 167 passing, gate clean. `tests/test_verdicts.py` asserts on angle names, so a
missed rename fails here.

- [x] **Step 7: Commit**

```bash
git add -A
git commit -m "refactor(angles): name each angle for the scope it checks

locality -> ownership-context, currency -> block-context,
functionality -> function-context, module-coherence -> module-context.

The old names described where the classification came from. The new ones
state what each angle checks a claim against, which makes the series and
its ordering visible: ownership decides where a claim belongs, the other
three check it against the code at their scope.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

## Task 2: Define `truthy`, and split the duplication rule

**Landed:** `9dc1874` -- 23 lines added to `reviewer-brief.md`: the `truthy` definition
and the `One claim, several sites -- who owns it` table.

**Why:** Two vocabulary problems block tasks 3-6. `truthy` is about to carry weight in two
angles and appears **zero times** in the plugin today -- measured. And "the same rule stated in
several places" is currently owned entirely by module-coherence, while Ownership-context is
gaining a duplicates-across-the-codebase check. Both angles would own it and drift.

**Files:**
- Modify: `plugins/comment-review/skills/comment-review/references/reviewer-brief.md`

- [x] **Step 1: Define `truthy` once, in the brief**

The brief already holds the shared vocabulary (the nine verdicts, the acquittal list). Add
`truthy` beside them:

```markdown
### `truthy`

A sentence is **truthy** when it states one checkable proposition about the code it is
attached to -- a subject, a referent, and a claim that some line, symbol or run can settle.

! Truthy is a property of FORM, not of truth. *"The retry budget is 40"* is truthy and false;
*"this is robust"* is neither. A sentence that is not truthy cannot be `correct`ed, because
there is nothing to correct it against -- it is `drop` or `query`.
```

- [x] **Step 2: Write the duplication split, in the brief, where both angles read it**

```markdown
### One claim, several sites -- who owns it

Both `ownership-context` and `module-context` see a claim stated in more than one place, and
they draw different conclusions. The split is fixed:

| angle | asks | verdict shape |
|---|---|---|
| `ownership-context` | which of these sites is this claim's HOME? | `reanchor`/`move` the claim to its owner, `drop` the copies |
| `module-context` | does the rule have no OWNING FUNCTION, so each site re-explains it? | `add` the rule to the function that should hold it, and name that function |

! Same observation, different finding. A claim with a home in the wrong place is
`ownership-context`'s; a rule with no home in the CODE is `module-context`'s. Neither may
emit the other's verdict.
```

- [x] **Step 3: Verify and commit**

```bash
python -m unittest discover -s tests && ruff check .
git add plugins && git commit -m "docs(brief): define truthy, and split the duplication rule between two angles

\`truthy\` was about to carry weight in two angles with zero occurrences in
the plugin. It is a property of FORM: one checkable proposition, so a
non-truthy sentence cannot be corrected because there is nothing to correct
it against.

The duplication split is written where both angles read it: ownership-context
asks which site is the claim's home; module-context asks whether the rule has
no owning function. Same observation, different finding.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

## Task 3: Ownership-context -- the checks that make it the dispatcher

**Landed:** `0cac2b9` -- the assessability handoff, the claim-home check and
`Is it load-bearing where it sits`, 38 insertions against 23 deletions (the
`prose about something ELSE` section was folded into the new material, which is the
budget payment step 4 asked for). `785dd56` then cut the argument-for-the-rule clause
in `Formatting`.

**Why:** `README.md` gives this angle three sub-bullets, and the agent implements placement
only. It is also gaining the two checks that make it prior to the other three: whether a claim
is stated in several places, and whether the claim is even assessable where it sits.

**Files:**
- Modify: `plugins/comment-review/agents/comment-review-ownership-context.md` (81 lines; at budget)

- [x] **Step 1: Add the assessability handoff, directly after "Your question"**

```markdown
## !! You run BEFORE the other three, and this is why

`block-context`, `function-context` and `module-context` each check a claim against the code
at their scope. A claim attached to the wrong scope gets measured against the wrong code -- a
comment about `parse()` sitting above `render()` is checked against `render()`, found false,
and CORRECTED into a falsehood. Your verdict decides which code the other three read.

So for every block ask, in this order:

1. **Would this be TRUTHY where it sits** (`reviewer-brief.md` defines it) -- one checkable
   proposition about *this* code? If not, say so and stop; there is nothing here for the
   others to settle.
2. **If it were in the right place, would it be truthy THERE?** A sentence that only becomes
   checkable once relocated is a `reanchor`, not a `drop`.

! You do not rule on whether the claim is TRUE. That is the other three angles', at their
scope. You rule on whether truth is assessable here at all.
```

- [x] **Step 2: Add the duplication check**

```markdown
## A claim stated at several sites has ONE home

Grep the claim, not the wording -- prose paraphrases. Where the same proposition appears at
several sites, name which site is its HOME (the code that cannot be changed without changing
the claim) and `drop` the rest, or `reanchor` the claim to that home.

! **This is not `module-context`'s restatement rule** -- see the split in `reviewer-brief.md`.
You decide where a claim lives; that angle decides whether the CODE is missing a function to
hold it. If the copies exist because no function owns the rule, it is theirs, not yours.
```

- [x] **Step 3: Add load-bearing, replacing nothing -- it belongs here**

```markdown
## Is it load-bearing where it sits

A block is load-bearing at a site when someone changing THAT code would make a worse decision
without it. A block that would be equally useful anywhere in the file is not anchored to
anything, and its home is the declaration it actually constrains.
```

- [x] **Step 4: Pay the budget**

The file is at budget. Read it whole and apply `docs/limitations.md`'s rule: if two rules are
instances of one generalization, write the generalization and delete both. Candidate: the five
"prose about something ELSE" shapes and the new assessability check overlap -- a block that
narrates what came before is a block whose claim is not truthy where it sits. Report what you
merged or replaced, and why, in your report.

- [x] **Step 5: Verify and commit**

```bash
python -m unittest discover -s tests && ruff check .
git add plugins && git commit -m "feat(ownership-context): claim homes, duplication, and the assessability gate

Adds the two checks that make this angle prior to the other three: whether a
claim is truthy where it sits, and which of several sites is a claim's home.
A claim attached to the wrong scope is measured against the wrong code and
corrected into a falsehood.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

## Task 4: Block-context -- constraints and worked examples

**Landed:** `b64f920` -- the widened question, the constraint section and the
worked-example section; four argument-for-the-rule paragraphs deleted for them
(79 -> 98 lines). `d144c41` cut two more (-> 94). ! The budget was paid in prose but
not in size: the file is 15 lines larger than before the task.

**Why:** `README.md` asks only "does it state what the code is doing now", but the angle's real
job is every claim checkable at block scope. Today it owns tense, obituaries and counts;
constraint accuracy is owned by nobody, and worked examples get one line.

**Files:**
- Modify: `plugins/comment-review/agents/comment-review-block-context.md` (79 lines)

- [x] **Step 1: Widen the angle's question**

Replace `**Your question: does this describe the program as it is NOW?**` with:

```markdown
**Your question: is every claim in this block true of the code it sits with?**

Three kinds of claim, and all three are yours:

- **State** -- does it describe the program as it is NOW, not as it was or will be.
- **Constraint** -- does it state the bound the code actually enforces: the same number, the
  same direction, the same units, the same inclusivity. A constraint stated loosely is wrong,
  not vague. *"Must be positive"* against `if x > 10` is a finding.
- **Worked example** -- does the example still produce what it claims. Run it.
```

- [x] **Step 2: Add the constraint check**

```markdown
## A constraint is checked against the code that enforces it

Find the line that enforces the bound and compare four things: the VALUE, the DIRECTION
(`>` vs `>=`), the UNITS, and what happens at the boundary. Report the enforcing line as your
`QUOTE`.

! **An off-by-one in prose reads as correct to every other angle.** Nothing else here compares
a stated bound against the comparison that implements it, so a wrong `>=` survives every pass.
```

- [x] **Step 3: Promote the worked-example rule to a section**

The current single line is `A worked example is current or it is a lie. Run it.` Replace with:

```markdown
## A worked example is executed, never read

Run it. An example that no longer produces its stated output is `correct`, and the
replacement carries the real output.

! **If it cannot be run from the checkout -- it needs network, a fixture that is gitignored, or
state from another machine -- it is `query`, not `clean`.** An example nobody can execute is
indistinguishable from one that works.
```

- [x] **Step 4: Pay the budget, verify, commit**

Apply `docs/limitations.md`'s budget rule as in Task 3, and report what you replaced.

```bash
python -m unittest discover -s tests && ruff check .
git add plugins && git commit -m "feat(block-context): own constraints and worked examples, not only tense

The angle checked whether prose described the program NOW; the README also
asks for accurate constraints and worked examples, which no angle owned. A
constraint stated loosely is wrong, not vague, and nothing else compares a
stated bound against the comparison implementing it.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

## Task 5: Function-context -- one function, and comment order

**Landed:** `72aefcc` -- the one-function and comment-order checks, and the whole
`abs()` treatment (the bullet, both ! paragraphs and the 11-calls/1-finding sweep)
deleted and replaced by the seven-line generalization step 3 specifies.
114 -> 120 lines.

**Why:** Two `README.md` sub-bullets are unimplemented, confirmed by grep: *"Is this one
function with an appropriate name or is it more than one function"* and *"Are the comments in
the function in the correct order."*

**Files:**
- Modify: `plugins/comment-review/agents/comment-review-function-context.md` (114 lines -- the largest, firmly at budget)

- [x] **Step 1: Add the one-function check**

```markdown
## Does the documentation describe ONE function

A docstring that needs "and" to be accurate -- *"parses the row and updates the ledger"* -- is
describing two functions sharing a name. The prose finding is that the summary line cannot
summarise; the code finding is that the function should split.

! **Report the prose, name the split in `CODE CONCERNS`.** Splitting the function is a
behaviour change and is not yours.
```

- [x] **Step 2: Add the comment-order check**

```markdown
## Comments in the body are read IN ORDER

Read them as a sequence. A comment that describes a step the body performs later, or that
still describes a step an edit moved above it, is `reanchor` -- the claim is true and belongs
to a different line in this function.
```

- [x] **Step 3: Pay the budget -- replace the `abs()` material with its generalization**

At 114 lines this is the largest agent and the budget rule bites hardest here. The `abs()`
material runs to roughly twenty lines and most of it is one repository's story: a sweep of 11
calls yielding 1 finding, an enumeration of the ten false positives, and a paragraph on
well-factored code. `README.md` already names this class -- the mechanical detectors "were
fitted to the codebase the tool grew up in", firing ~70 times across seven corpora for about
two real findings -- and `docs/limitations.md` says a tight budget exists precisely to force a
generalization instead of one rule per incident.

**Delete the whole `abs()` treatment -- the bullet, both ! paragraphs and the measured sweep --
and replace it with this:**

```markdown
- **A policy wearing arithmetic.** A threshold, a tolerance, a default, or a symmetry: the
  code *is* the decision, so nothing in it can say why that number and not another. The prose
  owes the why.

! **Flag it only where the comparison yields a JUDGEMENT a human reads** -- a deviation, a
flag, a warning -- not a NUMBER the code consumes, such as a distance, a sort key or an
equality epsilon.

! **Find the layer that owns the asymmetry before flagging.** Where the direction question is
decided and documented one layer up, the arithmetic below it is not the finding. Where it is
decided nowhere, that is.
```

Seven lines replacing about twenty, and nothing in it is about one language or one repo.
Report the exact line count before and after in your report.

- [x] **Step 4: Verify and commit**

```bash
python -m unittest discover -s tests && ruff check .
git add plugins && git commit -m "feat(function-context): one-function and comment-order checks

Two README criteria the agent never implemented: a docstring needing \"and\"
to be accurate describes two functions, and body comments are read in order
so a step described out of sequence is a reanchor.

Pays the per-file budget by replacing ~20 lines of abs() material with a
7-line generalization. The deleted part was one repository's story -- a
sweep of 11 calls for 1 finding, an enumeration of its false positives --
which is the overfitting README.md already names in the mechanical
detectors, and which the per-file budget exists to force out.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

## Task 6: Module-context -- cover the exposed surface

**Landed:** `e77fe99` -- `The module's own surface is a CHECKLIST`,
`Module-level state is documented or it is a trap`, and the cross-reference ceding the
placement half (the `establish the owner BEFORE trimming` paragraph went for it).
! 24 insertions against 4 deletions: 96 -> 116 lines, so the budget was paid only in
part.

**Why:** The biggest measured gap. `README.md` requires *"Does it cover all of the functions
and constants that the module exposes"* and *"Does the documentation support what the module's
state uses are"*; grep confirms the agent checks neither.

**Files:**
- Modify: `plugins/comment-review/agents/comment-review-module-context.md` (96 lines)

- [x] **Step 1: Add the coverage checklist**

The agent already holds the rule that a universal is a checklist. This applies it to the
module's own surface:

```markdown
## The module's own surface is a CHECKLIST

Enumerate what the module exposes -- its public functions, classes and constants -- from the
file's own definitions. Then walk the module docstring against that list.

- A name in the surface that the docstring never accounts for is a gap: `add`, naming it.
- A name in the docstring that is not in the surface is an obituary: `correct` or `drop`.

! **State which you enumerated -- public, private, or both -- and the count.** *"Covers the
module"* is the claim an existence check passes; the number and the population are the
finding.

! **Coverage is not one line per name.** A docstring accounts for a name when a reader can
tell why it exists -- a paragraph naming the module's one job can cover several names at once.
```

- [x] **Step 2: Add the module-state check**

```markdown
## Module-level state is documented or it is a trap

For each module-level mutable binding, ask whether the docstring says who writes it, when, and
what depends on it having been written. Import-order dependencies and caches are the shapes
that break silently -- an undocumented one is `add`, not `clean`.
```

- [x] **Step 3: Cede the ownership half of the restatement rule**

The existing "rule stated in several places" section keeps its conclusion (the rule has no
owning function; name that function) and gives up the placement half. Add the cross-reference:

```markdown
! **Where the copies exist because the claim is in the wrong place rather than because no
function owns the rule, it is `ownership-context`'s** -- the split is in `reviewer-brief.md`.
```

- [x] **Step 4: Pay the budget, verify, commit**

```bash
python -m unittest discover -s tests && ruff check .
git add plugins && git commit -m "feat(module-context): walk the module's exposed surface as a checklist

The README requires the module docstring to cover what the module exposes and
to account for module-level state; the agent checked neither. Enumerate the
surface from the file's own definitions, report the count and the population,
and cede the placement half of the restatement rule to ownership-context.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

## Task 7: Put Ownership-context in `fact-check`

**Landed:** `3518be3` -- `ownership-context` added to the `fact-check` row, the
`line` row reduced to verdicts, the two rationale paragraphs beneath the table, and
the `--angles` list at `fact-check` widened to three. `67d49b3` followed on
`reanchor`'s level dependency.

!! **DELIVERED, THEN REMOVED WHOLESALE at `f1b20d7` (2026-08-16), one day later.**
Roy: *"I am 100% certain there are not 'levels' allowed anymore."* The level ladder,
`proof` row included, has no provenance and was invented during the 2026-08-14 port;
all four roles now run every time and every instruction is admissible on every run.
The boxes stay `[x]` because the work landed and was committed -- what is gone is the
artifact, not the act.

**Why:** The level ladder runs `block-context` and `function-context` at `fact-check` without
`ownership-context`. Those two check a claim against its scope; without the angle that decides
whether the claim is attached to the right scope, a misplaced comment is measured against the
wrong code and `correct`ed into a falsehood. `fact-check`'s verdict set is `correct`/`query`/
`clean`, so `ownership-context` cannot `reanchor` there -- but it can emit the `query` that says
the claim may not belong here, which is what `query` is for.

**Files:**
- Modify: `plugins/comment-review/skills/comment-review/SKILL.md` (the level table and the paragraph beneath it)

- [x] **Step 1: Change the level table**

```markdown
| level | angles | verdicts available |
|---|---|---|
| `fact-check` | ownership-context, block-context, function-context | `correct` * `query` * `clean` |
| `line` | the same three | + `drop` * `move` * `reanchor` * `split` * `add` |
| `full` | + module-context | + `patch` |
| `proof` | none -- stage 8 (REVIEW) only, over files a previous pass edited. ! It has no 7b to complete, so it loads `review.md` directly | -- |
```

! **The ladder changes shape and that is the point.** It used to add an ANGLE at each rung;
now `line` adds only VERDICTS, because `ownership-context` already ran at `fact-check` and was
holding its placement findings as `query`. Reaching `line` is what lets those become
`reanchor` and `split`. Keep the `proof` row exactly as it stands today -- copy it across
unchanged.

- [x] **Step 2: State why, immediately beneath the table**

```markdown
!! **`ownership-context` runs at every level, including `fact-check`.** The other three check
a claim against the code at their scope; a claim attached to the wrong scope is measured
against the wrong code and `correct`ed into a falsehood. At `fact-check` it cannot `reanchor`
-- it emits `query`, which is exactly the verdict for a claim that cannot be settled where it
sits.
```

- [x] **Step 3: Update the `--angles` invocation**

`SKILL.md` and `CLAUDE.md` both carry `--angles locality,currency,functionality,module-coherence`.
Both become the four new names. Confirm the `fact-check` guidance names three angles, not two,
wherever the level is described.

- [x] **Step 4: Verify and commit**

```bash
python -m unittest discover -s tests && ruff check .
git add plugins CLAUDE.md && git commit -m "fix(skill): run ownership-context at fact-check too

fact-check ran the two angles that check a claim against its scope without
the angle that decides whether it is attached to the right scope, so a
comment about one function sitting above another was measured against the
wrong code and corrected into a falsehood. It cannot reanchor at that level;
it emits the query that says the claim cannot be settled where it sits.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

## Task 8: Sync the spec and the vocabulary

**Landed:** `e38343e` -- README's four criteria rewritten (76 lines) with the
placement dependency stated in the opening sentence, `CLAUDE.md`'s `clean` reservation
carrying the four new per-angle meanings, and all four agents' frontmatter
`description:` fields. `git grep -i` for the old names at that commit returns nothing
live. `ff15bf2` and `2a5c91c` closed the fix-round Minors. The plan shipped as **0.1.2**
(`c76f238`), merged at `a3c200a`.

**Why:** `README.md`'s "## What" section is the specification tasks 3-6 implement, and it still
lists the old names and the old sub-bullets. `CLAUDE.md`'s `clean` reservation names all four
angles' per-angle meanings and every one is now wrong.

**Files:**
- Modify: `README.md` (the four criteria, and the four-angle mentions elsewhere)
- Modify: `CLAUDE.md` (the four-angle list and the `clean` reservation)
- Modify: `plugins/comment-review/.claude-plugin/plugin.json` (description names the angles)
- Modify: `evals/discriminators.md` (references angles)

- [x] **Step 1: Rewrite `README.md`'s four criteria to match what the agents now check**

Each criterion's sub-bullets must be a check some agent performs. Where tasks 3-6 added a
check, the bullet stays; where a bullet was dropped as out of budget, remove it rather than
leave the README claiming it. **State the dependency**: ownership-context resolves placement
first because the other three measure a claim against the code at their scope.

- [x] **Step 2: Rewrite `CLAUDE.md`'s `clean` reservation**

The four per-angle meanings become:

```markdown
`clean` is reserved, not a synonym for "vaguely good": it is one of the nine verdicts named
under "The skill's 8 stages" above and must not be used as a loose adjective for code or prose
anywhere in this repo. As a verdict it means nothing to report from that angle, and each
angle's `clean` asserts something specific -- ownership-context: this claim's home is where it
sits; block-context: every claim in the block is true of the code it sits with; function-context:
name, signature, docstring, comments and body all support what the function does;
module-context: the module documentation accounts for what the module exposes and reads as one
set of ideas.
```

- [x] **Step 3: Verify no stale angle name survives anywhere live**

```bash
grep -rn -i "currency\|functionality\|module-coherence\|modularity\|locality" \
  --include="*.md" --include="*.py" --include="*.json" . \
  | grep -v "^./corpora\|^./evidence\|__pycache__\|superpowers/plans"
```
Expected: no output.

- [x] **Step 4: Verify and commit**

```bash
python -m unittest discover -s tests -v
ruff check . && ruff format --check . && python scripts/check_shipped_syntax.py
git add -A && git commit -m "docs: sync the spec to the four scope-named angles

README's four criteria are the specification the agents implement; every
sub-bullet is now a check some agent performs, and one that is not was
removed rather than left claiming it. CLAUDE.md's clean reservation carries
the four new per-angle meanings.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

## Task 9: Define what each angle's `clean` asserts

**Landed:** `08e0212` -- the `clean`-is-reachable-by-not-deciding note and the reframed
`query` paragraph in `reviewer-brief.md`, plus a "What your `clean` asserts" section
in each of the four agents. `2d72eaa` then dropped function-context's stale query
clause.

**Why:** `clean` is the only verdict reachable by **not deciding**. The other eight are actions
(`drop`, `correct`, `patch`, `add`, `move`, `reanchor`, `split`) or an explicit statement that
you could not settle the claim (`query`) -- none can be emitted passively. `clean` can be
arrived at by leaving a block alone, and is then indistinguishable from a checked acquittal.

Measured across the four agents before this task:

| angle | mentions of the `clean` verdict |
|---|---|
| `function-context` | **0** -- 120 lines, never mentions it |
| `ownership-context` | 2, both negative -- *"`query`, not `clean`"* |
| `block-context` | 2, both negative -- *"never `clean`"* |
| `module-context` | 7, including a dedicated section |

Three of four say only when `clean` would be *wrong*, never what it *claims*. `module-context`
is the exception because it already paid for this: a reviewer facing 548 blocks outside its
angle invented the word `derivation` rather than say `clean`, publishing a 95% acquittal rate.

The consequence is mechanical, not stylistic: `verdicts.py`'s clean-arithmetic blesses a block
when **every angle that ran** returns `clean`. A passive `clean` does not merely fail to find
something -- it certifies the block.

**Files:**
- Modify: `plugins/comment-review/skills/comment-review/references/reviewer-brief.md`
- Modify: all four `plugins/comment-review/agents/comment-review-*-context.md`

- [x] **Step 1: Fix the two verdicts that change no text -- in the brief, where shared facts belong**

`clean` and `query` are the pair that leave the prose untouched. One certifies the block, the
other escalates it. Getting `query` wrong pushes reviewers into `clean`, so both are fixed here.

**1a. `clean` -- add the general fact that makes the per-angle definitions necessary.**
`reviewer-brief.md` already says `clean` is scoped to you and cannot bless a block. Immediately
after that, add:

```markdown
!! **`clean` is the only verdict you can reach by NOT deciding.** Every other verdict is an
action or an explicit `query`; this one can be arrived at by leaving a block alone, and a
block left alone is indistinguishable from a block checked and acquitted. Your angle file
states what your `clean` asserts -- emit it as that claim, or emit `query`.
```

**1b. `query` -- replace a trigger that contradicts its own payload row.**

The payload row says `query` means *"you cannot settle the claim"*. Four lines below, the !!
headline says *"If you did not read BOTH SIDES, the verdict is `query`."* Those are different
triggers, and the second is the harmful one: a reviewer who **did** read both sides and still
cannot tell concludes `query` is not for them, and reaches for `clean` instead. **A mis-framed
`query` is a direct cause of the passive `clean` this task exists to prevent.**

Replace that whole !! paragraph -- from *"If you did not read BOTH SIDES"* through *"soften a
verdict with."* -- with:

```markdown
!! **`query` is for a claim you could not settle -- not one you did not try to settle.** You are
still required to open the code that would settle it; on every other verdict your `QUOTE` proves
you did. `query` is what you emit when you did and it was still not enough.

Three shapes reach it, and all three are findings rather than admissions:

- **outside your angle** -- what settles it belongs to another scope. Another angle may settle
  it, and the task agent rules on all four together.
- **outside the checkout** -- generated, gitignored, remote, or on one machine. No reviewer in a
  fresh checkout can settle it.
- **outside the code** -- settling it needs someone who knows the system or how it is operated.
  It reaches the author at 7a as a question.

! **A claim you could not settle and marked `clean` is worse than the same claim marked
`query`.** `clean` certifies; `query` asks. There is no confidence tag to soften a verdict with.
```

! Leave the paragraph *after* it unchanged -- the one stating a `query` carries no `EVIDENCE`
and no `QUOTE` by construction, and must not be downgraded to `clean` to escape the gate. It is
already correct and it is what the gate enforces.

- [x] **Step 2: `ownership-context` -- state its assertion**

```markdown
## What your `clean` asserts

**Emitting `clean` here asserts that EVERY SENTENCE in the block belongs to the line it sits
on** -- each is about that code, no other site states it, and someone changing that code would
decide worse without it. A block whose sentences belong to different code is `split`, not
`clean`.
```

- [x] **Step 3: `block-context` -- state its assertion**

```markdown
## What your `clean` asserts

**Emitting `clean` here asserts that EVERY SENTENCE in the block is true of the code beside
it** -- each one's state, its constraints against the line that enforces them, and any worked
example, run. A block holding one true sentence and one false one is not `clean`: the false
sentence is `correct`, the true one is `clean`. Two sentences, two verdicts.
```

- [x] **Step 4: `function-context` -- state its assertion**

This file mentions the verdict nowhere; it gains the section outright.

```markdown
## What your `clean` asserts

**Emitting `clean` here asserts that name, signature, docstring, comments and body agree, and
that nothing the signature cannot express is missing from the prose.** A docstring you read
but did not check against the body is `query`.
```

- [x] **Step 5: `module-context` -- add the positive assertion to what it already has**

This file already tells a reviewer to return `clean` naming "outside my angle" rather than
invent a word. That is the *scope* case. It is missing the *checked* case:

```markdown
**Emitting `clean` here asserts that the module docstring accounts for the exposed surface and
reads as one set of ideas** -- you enumerated the surface and walked it. `clean` because a block
is outside your angle is a different statement, and must name that reason.
```

Place it inside the existing acquittal-rate section so the two readings of `clean` sit
together, rather than adding a competing section.

- [x] **Step 6: Verify and commit**

```bash
python -m unittest discover -s tests -v
ruff check . && ruff format . && python scripts/check_shipped_syntax.py
```

Then confirm the four assertions differ from each other -- if two angles' `clean` say the same
thing, one of them is describing the wrong scope.

```bash
git add plugins && git commit -m "feat(angles): state what each angle's clean asserts

clean is the only verdict reachable by not deciding: the other eight are
actions or an explicit query. Three of the four agents said only when clean
would be WRONG and never what it CLAIMS, and function-context never mentioned
it across 120 lines.

The consequence is mechanical -- verdicts.py blesses a block when every angle
that ran returns clean, so a passive clean certifies rather than abstains.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

## After the plan: re-measure

The angles changed what they check, so any finding rate taken before this is not comparable --
the same discipline the corpus manifest applies to refs, and the same marking `README.md`
already carries for the pre-hardening instrument.

!! **BOTH BOXES ARE SUPERSEDED, not done.** `evals/grade_hazards.py` and the twelve
planted hazards exist at NO commit in this repository -- `git log --all --
evals/grade_hazards.py` is empty, and `b196f88`, the commit whose message announces
*"planted hazards, a grader, and the authorship split"*, added `generator_split.py`
alone. They were tied to a corpus this repo cannot ship. There is therefore no
end-to-end grade to re-run and no results file to annotate; rebuilding one is
[`TODO/the-harness-cannot-run-the-system-it-grades.md`](../../../TODO/the-harness-cannot-run-the-system-it-grades.md).
! The instrument these two boxes would measure has also moved: `angle` is retired,
the level ladder is gone (`f1b20d7`), and `verdict` is struck for `instruction`
(`3e47286`).

- [-] Re-run `python evals/grade_hazards.py <worktree>` against the twelve planted hazards.
      **Expect D7 and D12 to move**: D7 is a module single-source overclaim (module-context's
      new surface walk should reach it) and D12 is an orphaned block (ownership-context's
      assessability check should now name it rather than leaving it to a reviewer's reading).
- [-] Note in the results that the instrument changed between measurements.

---

## Self-review

**Spec coverage.** Every unimplemented `README.md` sub-bullet maps to a task: "more than one
function" and "comments in correct order" -> Task 5; "covers all functions and constants" and
"module's state uses" -> Task 6; constraint accuracy and worked examples -> Task 4; the
duplication and assessability checks -> Tasks 2 and 3. The rename is Task 1; the ladder
consequence is Task 7; the spec sync is Task 8.

**Deliberately not done.** `README.md`'s Functionality bullet *"Do the comments indicate the
function's use changed over time"* is **not** implemented by any task. It is a tense question,
which is `block-context`'s, and adding it to `function-context` would duplicate a rule across
two angles -- the antipattern this plugin exists to find. Task 8 removes the bullet rather than
leaving the README claiming it.

**Ordering.** Task 1 must precede everything (files must exist under their new names). Task 2
must precede Tasks 3 and 6 (both cite the split and the `truthy` definition). Tasks 3-6 are
independent of each other. Task 7 must precede Task 8's `--angles` check. Task 8 last.

**Budget risk.** Tasks 3-6 all add prose to files already at budget, and `docs/limitations.md`
says a new rule replaces one. Each task carries an explicit pay-the-budget step, and Task 5
carries a ruling on what to cut. If an implementer cannot pay the budget without losing a rule
that is still earning its place, that is a finding to report, not a licence to grow the file.
