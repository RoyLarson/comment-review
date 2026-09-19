# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development and review

Help Roy accomplish the agreed goals and improve the systems involved. Success
means useful working results, clear design, and evidence that the result serves
its purpose.

Actively look for Broken code while working in a project. Examine whether
behavior, responsibilities, interfaces, and design serve the project's purpose.
Pursue improvements that make the system work correctly and coherently,
including problems that passing tests leave undetected. Looking for Broken
code takes priority over looking for ways to make tests fail. Use tests to
evaluate behavior and verify repairs.

Use the global definition of Broken and the applicable scope, planning, and
review procedures. Trace suspected edge cases to supported inputs, reachable
states, or actual callers; investigate uncertain reachability before
recommending a repair.

## What this repo is

A Claude Code **plugin** (`comment-review`) plus the machinery used to develop and measure it.
The plugin is an editorial board for the comments and docstrings a change touched: four
read-only reviewer agents walk one page, a task agent (the `/comment-review` skill)
synthesizes instructions, the human approves the exact replacement text, and WRITE puts it on disk and
proves the executable code byte-identical.

**And the subject is the design as much as the wording.** A comment says what code is FOR,
so checking it against what the code DOES is a check on the structure. Where the two disagree
and the code is right, the comment is corrected; where the CODE is what is wrong, the role
raises a code concern and does not bend the prose to fit.

**A role cannot propose the code change, and that costs something MEASURED.** Roy,
2026-08-23: *"we can't tell the agents to review all of this and not give them an out for
properly resolving the issues. Several times they were overly restricted by what they could do
and that caused tension in the recommendations."* The harness records the shape:
`module-context` found a module announcing one subject while holding four, had no instruction for
*split this module*, and widened the docstring to announce TWO -- the defect its own trigger is
named for.

!! **Two lanes, and they are sequenced because of the measurement, not the filing.** Roy,
2026-08-23: *"it has to be landed in the code, tested that the effectiveness didn't change, and
then change the agents to tell them they can use it. Verify that it improved the
recommendations."*

**Shipping both at once destroys the attribution.** A movement in the output could be the
SHAPE or the INSTRUCTION, and nothing separates them after the fact -- so the question the
second half exists to answer cannot be asked. Both comparisons need a grader.

-> [docs/decision-log.md](docs/decision-log.md), *Metaphor and its limits*.

### Why it exists: A green gate is not evidence of a good result

**A gate says the code still parses, still runs, still says what it said.** None can say
whether the prose beside it is true, or whether a reader would learn the reason a thing is the
way it is. That gap is the whole remit of the four editorial roles, and it is why this is a
reviewer rather than a linter.

**[`docs/gates.md`](docs/gates.md) holds the measured cases**, the three ways a green run means
nothing, and what to ask before trusting a new check.

The repo root is **not** the plugin. Only `plugins/comment-review/` ships to a user's
`.claude/`; everything else (`docs/`, `evidence/`, `evals/`, `corpora/`, `scripts/`) is
development and measurement tooling that stays behind.

**And `plugins/` is assembled, not written.** `scripts/release.py` deletes it and rebuilds it
from two sources, WHOLESALE -- sub-packages intact, because Roy ruled the shipped tree takes
the same shape as the source: the Python in **`src/comment_review/`** with its launcher, and
the prose an agent reads in **`src/plugin/`** -- `agents/*.md`, `SKILL.md`, `references/*.md`
and `plugin.json`, laid out as the plugin is. **Edit `src/`; all of `plugins/` is output.** It
is rebuilt at release only, so between releases it lags and nothing reddens over that. The
gate that held the two equal per change went on 2026-09-05; Roy: *"It is just noise in the
development."*

## Commands

!! **Run everything through `uv run`.** The project is pinned to Python 3.11, the
floor `plugins/` ships against, in `.python-version` and `[project]
requires-python`. Substituting a bare `python` re-opens the gap that pinning
closed.

-> [docs/history.md](docs/history.md), 2026-08-17.

```bash
# The gather -- stages 2-3 of the skill -- over one or more files
uv run python src/comment-review.py gather --repo . <paths...>
uv run python src/comment-review.py gather --languages

# Stage 3 inbound: which tracked files NAME the files under review
uv run python src/comment-review.py referrers --repo . <paths...>

# Stage 7b gate: prove WRITE changed no executable code
uv run python src/comment-review.py prove_unchanged --base <merge-base> --repo . <paths...>

# The write chain: a docket -> a REVISE. `--out` must not exist yet; the chain's
# own shutil.copytree requires it fresh. The order lives in flows/revise.py.
uv run python src/comment-review.py proof --docket <docket>.json --repo . --out <dir>

# What one stage's revise changed, against the tree it was pulled from
uv run python src/comment-review.py taken_in --original <root> --revise <root> [paths...]

# The pinned corpora: git worktrees / clones into corpora/<name>/, gitignored
uv run python scripts/fetch_corpora.py [--list] [--only numpy pymc] [--clean sentry]
uv run python evals/generator_split.py <corpus-dir> [paths...]
uv run python scripts/find_llm_repos.py --pages 3 --min-hits 2

# Tests. PYTEST, and only pytest.
uv run pytest -q
uv run pytest -q -k galley

# Gates
uv run ruff check .
uv run ruff format .
uv run ty check
uv run python scripts/check_shipped_syntax.py     # AFTER ruff format; reads src/
uv run python scripts/release.py                  # assemble plugins/ from src/; at release
uv run python scripts/check_vocabulary.py
claude plugin validate plugins/comment-review     # release gate; before tagging

# Inputs, not gates -- each always exits 0 and wants a human to rule on its rows
uv run python scripts/vocabulary_sweep.py         # terms of art the inventory misses
uv run python scripts/dead_sweep.py [--names] [--links]
uv run python scripts/render_page.py <paths...> [--show margin|prose|rows]
```

### The board

**The vendored `scripts/todo_tool.py` is the older copy** and writes the
pre-2026-08-31 format. The board was migrated to the five marks on 2026-08-31;
use `job-board`.

### The suite

A skip that needs symlinks runs only where they exist.

**Tests are written in plain pytest and build their inputs from the code** --
pages from `page_for` over real source, binders from `bind`, with a literal only
where malformed *is* the input. `tests/gates/` is the exception and is still
`unittest.TestCase`, which is what `unittest discover` finds; it survived the
replacement because it asks a different question, whether a gate still bites.

-> [docs/history.md](docs/history.md), 2026-08-25.

!! **The stdlib-only rule is about `plugins/` alone.** Only `plugins/` is copied
into someone else's `.claude/`, and it imports nothing but the standard library.
`tests/` never leaves this repo, and `pytest`, `ruff` and `ty` are pinned dev
dependencies that run against it. **What the rule forbids is a third-party import
in a shipped file**, enforced by `tests/test_shipped_imports.py` -- including
`TestTheCheckItselfFires`, which proves the check can fail.

!! **There is no end-to-end grade.** `grade_hazards.py` and the twelve planted
hazards are not in this tree; they were tied to a corpus this repo cannot ship.
**The rule they enforced stands and has nowhere to run: grade from the diff,
never from the run's own report** -- self-reported confidence was measured not to
discriminate a real finding from a fabricated one. Rebuilding it means restating
each hazard, naming the failure precisely without copying the code it was found
in, and planting the set on one of the public corpora.

### The gates

!! **`ruff` and `ty` run through `uv run`, like everything else.** Both are pinned
dev dependencies. A bare `ruff` is whatever the machine has, and `ruff format`
rewrites source. Ruff config lives in `pyproject.toml`, and `corpora/**` is
excluded from linting.

!! **`ty` runs bare, covering both trees.** `[tool.ty]` in `pyproject.toml` sets
the scope, not a path typed on the command line. Before that, `tests/` sat outside
every ty run and four real `invalid-argument-type` errors there passed a green
suite, `ruff check`, `ty check` and the floor gate, because nothing was ever
pointed at `tests/`.

!! **`plugins/` is assembled from `src/`, not edited.** Edit `src/`; at release run
`scripts/release.py` and commit what it writes. `scripts/check_shipped_syntax.py`
reads `src/` because that is what the formatter rewrites; whether `plugins/` matches
is not asked between releases.

**`src/comment-review.py vocabulary` moved to `prototype/` on 2026-08-25 and does
not run.**

## Architecture

### The skill's 8 stages

`src/plugin/skills/comment-review/SKILL.md` is the task agent's own instructions --
read it before touching the skill.

!! **The middle touches no files. Stages 4-6 read and write JSON AND MEMORY, NOTHING ELSE.** Roy,
2026-08-30: *"the middle doesn't care if the pages have changed - it is not reading or writing to
the pages at all. The edit process moves data in json files or memory nothing in the actual
files."* Its inputs are a binder and the returned `edit_copy`s; its output is the copy chief's
`edit_copy` and, downstream, a docket. **Pages are opened at the ENDS of the chain only** --
`gather` at one, the write chain at the other.

**So nothing in the middle asks whether a page changed.** No drift check, at any granularity: a
`raw_text` comparison and a `sha` comparison are the same question, and the middle has no stake in
the answer because it is not editing the tree. **The idea is inherited from a prototype that
edited as it went** -- it could not address or compose a page, so it had to care. Nothing in the
current design does. `decision-log.md Process: #62`.

**It keeps being re-derived, which is why it is here and not only in the log.** Roy, the same
day: *"I don't know how many times i have to say this because you forget to write it down."*
MEASURED: a review correctly found that `drift` never affected an exit code, and the fix round it
prompted GAVE it one (`ac8cbbd`) -- entrenching a check that should not exist. **The finding was
real and the repair pointed the wrong way**, because nothing in the tree said this.

The seven instructions (`clean`, `query`, `drop`, `correct`, `patch`, `add`,
`move`) and the checkable/necessary matrix that resolves them are defined in SKILL.md -- read it
rather than re-deriving the rules here, since it is the single source and this file must not
restate it.

-> [docs/decision-log.md](docs/decision-log.md), *Process*.

### The four editorial roles

Reviewers are read-only and never see SKILL.md directly; they read the shared
`references/reviewer-brief.md`. Fixing what you find destroys the finding -- MARK and APPLY are
deliberately separate stages/actors.

### The binder -- the only thing the reviewers depend on

It is built from the standard library alone, at a per-language tier:

| tier        | needs                                 | answers                         | cannot answer     |
| ----------- | ------------------------------------- | ------------------------------- | ----------------- |
| `tokenized` | a lexer + AST (Python, stdlib)        | blocks, marks, docstring owners | a comment's owner |
| `lexical`   | a comment-syntax record, nothing else | blocks, marks                   | any owner         |

A language with no record is named and the gather exits nonzero: every file handed in is
gathered or the run stops. Adding a LEXICAL language is a data row, not new code.

**AND A tokenized one is not, which this said otherwise until 2026-08-22.** It read *"adding
a language is a data row"* flat. MEASURED: `language.py` decides the tier as `return "tokenized"
if lang.name == "python" else "lexical"`, and `page.py` dispatches the READER on that same name
test while the same file STAMPS the tier from `tier_for` -- so a second tokenized language is
three edits in two modules, and half a fix leaves a file **read at one tier and labelled at the
other**. Three more sites decide *is this Python* three more ways.

**IT IS A claim about the cost of a change, which is the kind that invites someone to make the
change and discover the cost.**

**The row becomes true again when the AST goes.** Roy, 2026-08-22: *"as much because we are
going to remove the ast system from python coming up as it is not an accurate statement."* With
Python read lexically there
is one tier, the name test has nothing to answer, and adding any language is a row again. **The
sentence is not being corrected toward permanence; it is being made honest until the thing it
describes is rebuilt.**

**Which lines declare something documentable is a keyword list on the language row**, per
language, since 2026-08-20. Roy: *"the easy way is to supply the lexer with the list of keywords
that a language/practice uses to say this can get a docstring. Then the lexer matches on that
instead of having to have independent tooling."* So an `a` place resolves for Rust, Go, Java,
C#, Swift, Kotlin, JS, TS, Ruby, Lua and shell -- not Python alone.

!! **Every language carries every definition it needs, and no language ever inherits one.** Roy,
2026-08-22, restating it *explicitly* after a session read the weaker form below and assumed he
could not have meant literally every language: *"every language gets its own definition
requirements in the file. No language ever inherits from the `a` family. The file can be grouped
or sorted to make it easier to understand what is happening, but every language gets all of the
definitions necessary to parse it specifically, because anything else is failing the SRP rules."*

**Grouping is presentation; sharing is the defect.** Rows may sit together so a reader can see
the family. What they may not do is take a rule from a neighbour.

!! **The machinery is shared; the definition is not.** A two-word entry, an empty keyword list, a
`spanning_quotes` tuple -- every row may use any of them. What goes IN one comes from that
language's grammar and from nothing else. Roy, 2026-08-22: *"I am not against a two word entry
`data class`. I just wanted to make certain that it wasn't assumed you could assemble two
different definition systems together to get a correct one."*

**The tell is reasoning from a neighbour, and it is in the prose rather than the row.** Measured
2026-08-22: `data class` is right because KOTLIN'S grammar says so; `local function` is right
because LUA'S does. Neither is evidence about the other. The failure was arguing *"Kotlin solved
it this way, so Java should"* -- and Java's second word is the record's NAME, which varies, so the
same shape broke a real declaration. **A row is wrong the moment its justification cites another
row**, whether or not the value it lands on happens to be correct.

**And the rule was already here, with its operative sentence cut off.** This file carried
two-thirds of the 2026-08-20 ruling. The full quotation, recovered from `9ee38ea`:

> *"don't try to make the list generic -- that is a failure of the single responsibility
> principle. Each language could change on a new version invalidating the list for all of them.
> **Better an explicit precise list with duplicated words than an implicit word set hoping to
> catch each.**"*

**The third sentence is the one that decides anything**, and it is the one that went. The first
two say a generic list is a risk; only the third says which way to resolve it -- **explicit and
duplicated beats implicit and shared** -- which is the sentence that forbids borrowing a
neighbour's rule. The `c-family` and `js-family` rows were split under it.

!! **A shortened quotation is not a shorter rule; it is a different ONE.** Roy, 2026-08-22:
*"I am pretty certain that the session cut out the important part when it shortened it."* And
nothing marks a cut: this tree writes `--` for an em-dash because of the ASCII rule, so an
elision and a dash are spelled the same. **When a ruling is quoted here, quote all of it** -- the
commit that first recorded it is the source, and `git log -S` finds it.

**An empty list means the language has no `a` series at all** -- not an empty one. `yaml`,
`toml`, `ini` and `sql` have no docstring practice, and carried an `a0` no instruction could fill until
this landed.

**C and C++ sit in that group for A different reason, and it is deferral rather than
IMPOSSIBILITY.** A C declaration opens with its return type, and the matcher reads a line's FIRST
word -- so no keyword ever matches and a spurious `a` would renumber every `a` below it. **That
is a fact about the MATCHER, not about C.** Roy, 2026-08-23: *"assumes you don't create a slightly
smarter parser that looks for the correct keyword in the line instead of just the 'first' word. It
is a simple fix."* Both languages plainly have documentable declarations; the list is empty until
that lands.

**This sentence previously read *"the list could never be complete"***, which is the shape this
file warns about two sections up -- a claim about the COST of a change, which invites someone to
make the change and discover the cost.

Only Python's doc sits INSIDE the declaration, so Python alone needs a parser to say WHERE the
prose goes; everywhere else it goes on the declaring line's own line. An LSP `documentSymbol`
enrichment still refines this when a language server answered stage 1.7's probe, and a reviewer
reading the file is what supplies an anchor no keyword names.

`references/` under the skill directory (`write.md`, `compact.md`, `residue-check.md`,
`review.md`, `reviewer-brief.md`) are each single-sourced for one stage -- nothing pastes their
content elsewhere, and a change to a rule belongs in exactly one of these files (or in
`docs/limitations.md` for orchestration-level rules).

-> [docs/decision-log.md](docs/decision-log.md), *Addressing*.

### Repo layout

| path                              | what                                                                                                                                                                       |
| --------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `src/comment_review/`             | **the Python, and the only place to edit it.** Eight areas -- `machine`, `reading`, `binder`, `concordance`, `desk`, `docket`, `results`, `flows` -- plus `commands/`, which holds every `main()` and argparse, `references/`, the package data, and `__main__.py`, the dispatcher. **`desk/` is sub-packaged**: `marks/`, `answers/` and `dispositions/` are the three tables, `evaluate/` the place and its passes, `work/` the Unit of Work. `release.py` copies sub-packages intact, so the shipped tree takes the same shape. `src/comment-review.py` beside it is the launcher, the one file allowed to touch `sys.path` |
| `src/plugin/`                     | **the prose an agent reads, and the only place to edit it** -- `agents/*.md`, `SKILL.md`, `references/*.md` and `plugin.json`, in the plugin's own shape |
| `plugins/comment-review/`         | the shipped plugin -- OUTPUT of `scripts/release.py`, all of it, rebuilt at release from `src/plugin/` and `src/comment_review/` |
| `docs/`                           | how this system behaves today, and the rules for changing it: `addressing.md` (how a place is NAMED -- the crux, and what the line-numbered form got wrong), `parsing.md` (where a page's structure could come from), `limitations.md` (rules for changing the skill itself -- budget-constrained, no invented examples), `vocabulary.md` (the settled terms, and every word this system stopped using), `the-turn.md` (the SOURCE for what a TURN is, what a DiffMark answers, and what closes the editorial roles -- the loop lived only in chat until 2026-09-02 and was reconstructed wrong twice), `history.md` (what the system used to DO and stopped doing -- a retired format or mechanism, with the commit that removed it, so an OLD artifact can still be read), `decision-log.md` (WHAT was decided and WHEN -- the dated chain of rulings, retractions and supersessions; the commentary on WHY is `history.md`'s. Cited as `decision-log.md TOPIC: #N`) |
| `docs/plans/`                     | release scopes -- what one version ships, what it does not, and which TODOs it works. !! **NOT `docs/superpowers/plans/`**, and the split is deliberate: Roy, 2026-08-19, *"I don't want to conflate the rigorous one for the less rigorous one."* A superpowers plan is written for an engineer with no context -- exact files, TDD steps, a commit per task. **A plan is not A TODO**: *"Todos can remain open an indefinite amount of time and make progress as we see fit. Plans are scopes of work to be complete in one run."* Anything in a plan that does not get done is filed in `TODO/` before the plan closes |
| `evidence/`                       | the prose defects the system is measured against, and the searches scored on them: per-module probe reports over a real codebase, the triage that ranked them, `ga/ground_truth.py` and the candidate rewrites it scores. Nothing here describes this system's own behavior -- that is `docs/`                                                    |
| `evals/`                          | `generator_split.py` (the authorship split) and `test-cases.jsonl`. The twelve planted hazards and their grader are NOT here -- there is no end-to-end grade, see Commands |
| `corpora/`                        | `corpora.toml` MANIFEST of pinned corpora; the trees themselves are fetched, never vendored (gitignored)                                                                   |
| `scripts/`                        | `release.py` (which assembles `plugins/`), `fetch_corpora.py`, `find_llm_repos.py`, `check_shipped_syntax.py` -- none of this ships with the plugin                        |
| `prototype/`                      | **REFERENCE, not source.** The middle of the chain -- the desk, the verdicts, the record -- moved here 2026-08-25. Nothing imports it, nothing ships it, it does not run. Kept to be read, not to be run; the middle it prototyped was rebuilt 2026-09-18 -- `docs/decision-log.md Process: #183`. See `prototype/README.md` |
| `.claude-plugin/marketplace.json` | lets this checkout be installed as a plugin marketplace in the same session (`claude plugin marketplace add <path>` then `claude plugin install comment-review`)           |

### Shipped-code constraint that shapes how every `plugins/` script is written

Anything under `plugins/` is copied into other people's `.claude/` and formatted by **their**
ruff config, not this repo's -- a repo targeting a newer `target-version` can rewrite valid
syntax (e.g. `except (A, B):` -> PEP 758 unparenthesised form) into a `SyntaxError` on an older
interpreter, and the author of this repo never sees the failure. Consequences enforced in this
codebase:

- No `except` clause in a shipped file holds a tuple literal -- every exception tuple is bound to
  a name (e.g. `READ_ERRORS`, `PARSE_ERRORS`) so there is nothing for a formatter to rewrite.
  A `noqa` was tried and does not hold, because it suppresses the report, not the rewrite.
- `pyproject.toml`'s `target-version = "py311"` protects *this repo's own* formatting only; it
  cannot protect a file after it has been copied elsewhere -- `scripts/check_shipped_syntax.py`
  is the actual floor check, and it must be run after `ruff format`.

### Corpora are fetched, never vendored

`corpora/corpora.toml` pins nine repositories at specific refs (seven third-party, plus two
personal projects used as an over-fitting control), chosen for variety of prose convention. A
`local` corpus becomes a `git worktree` of a repo already on the machine; a `public` one is a
sparse clone at a tag. `corpora/*/` is gitignored -- only the manifest and the fetch script are
tracked. Corpora used with `evals/generator_split.py` must be fetched with `depth = 0` (full
history) since it depends on `git blame`.

## Working on this repo

**A heredoc here includes PowerShell's here-string, `@'...'@`.** A multi-step or repeated edit
is a `.py` script written under the job's tmp dir and run with `uv run python`.

- Grade a comment-review run from its **diff**, never from its own report -- self-reported
  confidence has been measured to not discriminate real from fabricated findings.
- Changing the agent files or the skill's prose follows [`docs/limitations.md`](docs/limitations.md).

-> [docs/decision-log.md](docs/decision-log.md), *Process*.

### THE TODOs are the job board. Plans are how we mark them off.

Roy, 2026-08-19: *"the todos are the job board -- plans are how we mark them off."*

| | `TODO/` | `docs/plans/` |
| --- | --- | --- |
| holds | every piece of work known to be wanted | one release's scope |
| lifetime | **indefinite.** Progress as we see fit | **one run.** It closes |
| answers | *what is there to do* | *what is this version doing about it* |

**And this is two trackers that can drift, knowingly.** Roy: *"I know this is two ways of
tracking work which can get them out of sync."* The rule that keeps them honest is one-directional
-- **a plan cites TODOs; a TODO never cites a plan** -- so a closed plan leaves the backlog intact
and no TODO is left pointing at something that no longer exists.

**A plan carries checkboxes, the same as a TODO.** Roy, 2026-08-19: *"Just because they are
not todos doesn't mean they are freeform either."* **The release gate is every box on the plan
ticked** -- *"we will get to the release readiness at the time when it is ready to be released"*,
which sounds ontological and is not. It says readiness is **COUNTABLE** and **verifiable by
ANYONE**, not self-defining:

- nobody has to JUDGE whether a version is ready
- nobody can DECIDE that it is
- and **anyone can check that it is** -- including someone who did none of the work

**The third is what makes the first two hold.** A box that only its author can verify is a
judgement wearing a checkbox. Each box therefore NAMES the TODO it works, the TODO names the
work, and the work is in the tree -- so a ticked box is re-derivable by a stranger, which is the
same standard this repo applies to a comment: *if a sentence cannot be falsified by reading the
code or re-running a command, it does not belong.*

**And this is what lets an agent stop asking "is it ready".** Roy, 2026-08-19: *"even though
I knew the scope of work I wanted and I thought you had the information on the scope of work, you
didn't -- and so would ask, because you didn't have access to what done looked like."*

**That question is a SYMPTOM, not politeness.** *"Should we release it now?"* and *"are you
ready to release it?"* are what an agent asks when DONE exists only in someone's head. It cannot
be answered from the tree, so it gets asked of the person -- repeatedly, and usually at the worst
moment, because the agent has no way to tell whether the answer has changed since last time.
**The plan externalises DONE**, so the state is read rather than requested.

**It does not remove the rulings, and must not.** A ruling is asked because it is genuinely
Roy's. **Asking for a ruling is work; asking whether the work is finished is a missing
artifact.** An agent that cannot tell the two apart will either interrupt
constantly or guess at a decision that was never its own.

**Prose in a plan is EVIDENCE for a box, never a second list of work.** A section that restates
what a box says is a place for the two to disagree.

**`docs/plans/` is NOT `docs/superpowers/plans/`.** The second is written for an engineer with
no context -- exact files, TDD steps, a commit per task. The first is a release scope. Roy:
*"I don't want to conflate the rigorous one for the less rigorous one."*

-> [docs/decision-log.md](docs/decision-log.md), *Process*.

#### A box is a claim about whether work remains

!! **A box is a verifiable checkpoint and nothing else gets one.** A task names something a
stranger can look at and call done or not done -- a command that must come back empty, a file
that must exist, a test that must fail first. **A ruling, a measurement, a naming decision or a
line of reasoning is not a task**, however much it matters: it belongs in the **Objective**, or
in a dated `note`.

**The tell is that it cannot be finished.** *"The trade word is `leading`"* is true the day it
is written and every day after -- there is no state in which someone ticks it. If ticking would
be a JUDGEMENT rather than an observation, it is not a task.

**An unchecked box says the work is still to do, and something automated now reads it.** Roy,
2026-08-18: *"a check box not-marked is left as something todo, even if it was superseded and no
longer necessary."* Measured the same day: five RESOLVED proposals held in a prose table with no
boxes made `resync` generate a README row reading `0/9` on a file a third finished.

!! **A TODO is never deleted. It is SUPERSEDED and checked.** Roy, 2026-08-19: *"todos don't get
deleted they get SUPERSEDED and checked. That is going to be an addition to the tool soon."*

**A deleted box leaves no trace that it was ever there, or why it went.** A superseded one
keeps the error legible -- which is the same reason a superseded RULING is kept beside the one
that replaced it rather than rewritten away.

It applies to a task filed in error as much as to one overtaken by better work. Removing a
mistake removes the record that it was made.

| the task is | the box | the file's `Status:` |
| --- | --- | --- |
| **done** | `[x]` | -- |
| **superseded** -- overtaken, no longer necessary | `[-]` | -- |
| **partly delivered** | `[-]` on the original; the pieces filed as new tasks, the finished one `[x]` | -- |
| **deferred** -- waiting on a named event | `[ ]` | say what it waits on |
| not started | `[ ]` | -- |

**Deferred is not done.** Roy, 2026-08-18: *"Deferred is not done - just waiting so its status
is still correct."* Waiting on an event is work not started, which is what an unchecked box
already says.

**`in-progress` means some boxes are ticked** -- not blocked, not waiting on a ruling. A file
where only a RULING has landed is `in-progress`, because a ruling is work.

**A superseded ARGUMENT is not a superseded task.** Reasoning kept so an error stays legible
carries no box at all; only work does.

-> [docs/decision-log.md](docs/decision-log.md), *Process*.

### Cutting a release, and the version number

**Proposing a tag is the moment to check which branch you are on.** A tag is a main-only act,
so wanting one means the work has been accumulating somewhere -- and if that somewhere is main,
it went there without the branch question ever being asked.

**Any change under `plugins/` after a tag needs a new version, and a tag someone has measured
against is never moved -- cut the next number instead.** The plugin cache keys its directory on
the `version` field, so a second tree installed under the same number overwrites the first.

**The procedure is the `cut-a-release` skill**,
[`.claude/skills/cut-a-release/SKILL.md`](.claude/skills/cut-a-release/SKILL.md): the version
stated three times, assembling `plugins/`, validating, and publishing, with the reasons for each.

-> [docs/decision-log.md](docs/decision-log.md), *Process*.

## The metaphor is EDITORIAL, and it is a rule, not decoration

**This is an editorial board.** Four **editorial roles** read a manuscript and write **editorial
marks** on it; a **PROOFREADER** reads the finished **proof** and says whether the document
deserves more marks. Think about the work that way, and take a new term from publishing -- what
would an editor, a copy desk or a proofreader call this? -- before reaching anywhere else.

**Check a candidate against the register before proposing it, not after.** Three words entered
from LAW and each named something publishing already had a word for: `acquittal` and
`suppression` arrived with the initial plugin import and are deleted; `jurisdiction` was added
2026-08-16 by a session that checked it for collisions and never checked it for register, and is
now `remit`.

**And it supplies categories, not only names.** Roy, 2026-08-21: *"this is twice now that we
have realized we were categorically wrong about something that the publishing industry already
knew and uses actively."* Both times the tell was the same sentence -- **"it had to belong to
something"** -- said about a category that was straining to hold a second job:

| what was straining | what it was missing | measured cost |
| --- | --- | --- |
| `b0` held the file's own matter as well as the first gap | **front/back matter**, its own series | one address for two places; a licence header reviewed as ordinary work |
| `b` held the blanks on both sides of an `a` | **leading**, the space between lines of type | 16 of 185 files in one corpus could not be set back |
| `galley.py` both EDITED the page and SET it | **the compositor**, who sets type and decides nothing | the whole module was line arithmetic; three plan boxes were held for it |

**The third is the one where the method is on the record**, 2026-08-21, in four messages:

| Roy, verbatim | what it does |
| --- | --- |
| *"first what is a galley or what does it do in the publishing world?"* | asks what the thing IS -- **before** proposing anything |
| *"So right now what the problem is - is actually galley doing two things, creating an updated page and page-setting the text. Those are two different roles and two different sets of rules."* | reads the two jobs OUT of that answer |
| *"So my proposal is galley gets the old page - updates the old page with the verdict/record/marks and then a page-setter sets the page to rewrite the output text."* | names the missing half **from what it does**, in plain English |
| *"compositor works"* | takes the trade's word for the role he had already isolated |

**The name came last, and it came from the function first.** `page-setter` is Roy's own
coinage and is what the module was called for the whole diagnosis; `compositor` arrived afterward
and was ratified in two words. So the method is not *ask publishing what to call things*. It is
**ask what the thing is, find the second job in the answer, and name that job by what it does**
-- and only then look for the trade's word for it. A term reached the other way names a category
nobody has yet shown to exist.

**And the payoff is stated as a test, not as tidiness**: *"Then we can compare the round trip
directly page in page out, page in, comments removed, page out no comments... No ambiguity about
how the page gets written. No this got lost this wasn't done right."* The split is what made the
identity able to fail -- which is [`docs/gates.md`](docs/gates.md)'s rule arriving from the other
direction, and Roy said so at the time: this header *"is referencing this exact error even though
it was masked by so many other things."*

**And it says when to ask -- it was a refusal, not a schedule.** Roy, 2026-08-21: *"This
page-setter idea is what I was thinking about a lot when you stated this and how it to do it. It
is also why I have refused every galley update to this point. The galley was always broken and on
this commit is still broken."* Every proposed galley fix was declined while the category error
stood, because a fix to a module that is about to stop existing is chosen for nothing.

**When a category is doing two jobs, ask what a compositor would call the half that does not
fit** -- before inventing a rule to make one category cover both. Publishing has spent five
centuries naming the parts of a page; a part this system keeps tripping over probably has a name
already, and the name usually arrives with the rule attached.

**And a third is open, found the same way.** Roy, 2026-08-21: *"There is no stet. -- we called
this 'clean' we were incorrect."* `clean` records two different facts -- *a role read this and had
nothing to report*, and *a mark WAS proposed here and the original stands*. The second is
publishing's **stet** ("let it stand"), written in the margin with dots under the text so the
refused correction stays visible underneath. Recorded as `clean`, a declined proposal says
nothing was found, so a re-run raises it again and stage 8 cannot know it was already refused.

**The register is itself an instruction, and that is the point.** Roy, 2026-08-16: *"I bet it
helps the LLM focus in on what it is doing. Because of locality and other context items the llm
will return words and phrases and comment suggestions based upon 'being' an editor better."* An
agent reads these files and then writes in them, so one consistent register is a role it can
occupy rather than a glossary it has to consult. A reader who knows the metaphor can also predict
what an unfamiliar term means instead of guessing. Recorded as the REASON for the rule, not as
a measurement: nothing in this repo tests it.

## Documentation Rules

- Do not write prose rules, thresholds, or assumptions into docs unless something in the code
  actually consumes them. If nothing reads it, delete it.
- Never attribute assumptions about Q unless they stated them in this session or they are
  recorded in a cited file. Cite the source inline.
- Prefer a glossary entry over repeated inline definitions.
- Do not write subjective statements about properties of the project -- "robust", "elegant",
  "carefully designed", "solid", "maintainable", "intuitive", "works well" -- in comments,
  docstrings, README prose, or commit messages. A false *measurement* can be re-derived and
  corrected; a claim that something is "robust" has no oracle. Nothing can check it, so it
  survives every review and every rewrite regardless of whether it was ever true -- it is the
  one class of prose this repo's four editorial roles cannot catch, because both block-context and
  function-context need something to resolve the claim against. Write what is measured, what is
  enforced, or what was observed, and let the reader judge. If a sentence cannot be falsified
  by reading the code or re-running a command, it does not belong.
- `clean` is reserved, not a synonym for "vaguely good": it is one of the seven instructions named
  under "The skill's 8 stages" above and must not be used as a loose adjective for code or
  prose anywhere in this repo. As an instruction it means nothing to report from that role, and
  each role's `clean` asserts something specific -- read what, in that role's own file under
  `src/plugin/agents/`, which states it.

## Exploration Budget

- Cap initial exploration at ~10 tool calls; if you still lack context, report what you
  found and ask rather than continuing to browse.
- Prefer dispatching a Task agent for open-ended codebase exploration so the main context
  stays uncluttered by the subagent's intermediate output.

## Lanes -- "You are the ..."

**Four lanes own this repo, and a TODO's `Owner:` is one of them.** Roy runs sessions in
parallel, each opened as *"You are the `backend` -- I need you to ..."*, and **the lane scopes
what you may change.** If a task touches a file another lane owns, **name the lane and ask**.

| lane | owns, in one line |
| --- | --- |
| `agents` | **What an agent is TOLD, and how the roles hand off** |
| `backend` | **What the Python actually does** |
| `testing` | **How well the running system does, and what that is scored against** |
| `systems` | **Whether it installs, and whether the gates still bite** |

!! **The vocabulary is shared and crossing is the point.** Roy, 2026-08-23: *"any side can and
should update the vocab on the other side as soon as a split or modification is noticed."* It is
the ONE standing exception to *name the lane and ask*, and the cost of waiting is measured --
`evidence/rename-left-history-in-the-comments/`.

**And a lane that trips A gate fixes its own code**, never the gate. A gate edited to pass is
indistinguishable afterwards from one that always passed.

The full roles, the crossing rules and the path map are in the two files loaded below.

-> [docs/decision-log.md](docs/decision-log.md), *Process*.

## Always resident -- loaded by the `@` lines below

The two `@` lines at the end of this file are what put `conventions.md` and `lanes.md` in
context, in full. **An ordinary markdown link does not** -- it makes a file findable, not
present. Keep both lines; if they are somehow not in context, read the two files before changing
rules or crossing lanes.

@docs/conventions.md
@docs/lanes.md
