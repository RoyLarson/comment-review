# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A Claude Code **plugin** (`comment-review`) plus the machinery used to develop and measure it.
The plugin is an editorial board for the comments and docstrings a change touched: four
read-only reviewer agents walk one page, a task agent (the `/comment-review` skill)
synthesizes verdicts, the human approves the exact replacement text, and WRITE puts it on disk and
proves the executable code byte-identical.

### !! WHY IT EXISTS: A GREEN GATE IS NOT EVIDENCE OF A GOOD RESULT

Roy, 2026-08-18: *"Just because the code passes -- even if it has gone through multiple rounds of
simplify and code-review -- doesn't mean that the code is good, that it has the right structure,
the right documentation and the right reasons why things are the way they are."*

!! **MEASURED, on a real run.** `evidence/redacted-corpus-full-v0_2/` records a tree carrying **31
reader-visible defects** while every mechanical gate was green: `prove_unchanged` 23/23, the
hygiene guard 19/19, **2,413 tests passing**, every citation resolving, the residue check clean.
Stage 8 -- a reader, not a checker -- is what found them.

! **The gates were not wrong; they were answering a different question.** Each says the code still
parses, still runs, still says what it said. None can say whether the prose beside it is TRUE, or
whether a reader would learn the reason a thing is the way it is. That gap is the whole remit of
the four editorial roles, and it is why this is a reviewer rather than a linter.

! **Corroborated on this repo, 2026-08-18**, with 519-534 tests green throughout: the join admitted
a citation whose `verbatim` was `null`, because it rendered as the word "None" and the cited line
happened to contain it; `payload_problem` admitted a claim key that was present and empty, and
every check that would have caught it then skipped; the brief generator imported a table from a
module that no longer defined it, passing only on an accidental re-export; and the backlog index
listed eight finished TODOs as open. **Every one was found by reading, and none by a gate.**

The repo root is **not** the plugin. Only `plugins/comment-review/` ships to a user's
`.claude/`; everything else (`docs/`, `evidence/`, `evals/`, `corpora/`, `scripts/`) is
development and measurement tooling that stays behind.

## Commands

!! **RUN EVERYTHING THROUGH `uv run`.** The project is pinned to **Python 3.11**, the floor
`plugins/` ships against, in `.python-version` and `[project] requires-python`. Measured
2026-08-17: with 3.14 as the ambient interpreter, four of the eight shipped scripts raised
`NameError` at IMPORT on 3.11 while every test and the shipped-syntax gate passed -- PEP 649
makes annotations lazy from 3.14, so the break was invisible locally. Roy: *"the floor will not
fail if we are using the floor to evaluate the code."* Substituting a bare `python` re-opens
exactly that gap.

```bash
# Run the census (stages 2-3 of the skill) over one or more files
uv run python plugins/comment-review/skills/comment-review/scripts/census.py --repo . <paths...>
uv run python plugins/comment-review/skills/comment-review/scripts/census.py --languages   # list known languages

# Materialise the pinned corpora (git worktrees / clones into corpora/<name>/, gitignored)
uv run python scripts/fetch_corpora.py                 # fetch everything missing
uv run python scripts/fetch_corpora.py --list          # print the manifest only
uv run python scripts/fetch_corpora.py --only numpy pymc
uv run python scripts/fetch_corpora.py --clean sentry --only sentry   # refetch one

# Grade a comment-review run against the twelve planted hazards, from the diff (never the report)
uv run python evals/grade_hazards.py <worktree> [<worktree> ...]

# Split a corpus's prose defects by whether the introducing commit carries an assistant trailer
uv run python evals/generator_split.py <corpus-dir> [paths...]

# Survey GitHub for assistant-authored repos to extend the corpus
uv run python scripts/find_llm_repos.py --pages 3 --min-hits 2

# Run the test suite (stdlib unittest; there are no third-party test deps)
uv run python -m unittest discover -s tests -v

# ONE file, one class, one test -- `-k` matches any of the three, and NOTHING
# else runs a subset. There is no `python tests/test_x.py`: a `__main__` runner
# adds nothing discovery cannot do, and its POSITION is load-bearing in a way
# nothing checks. Measured 2026-08-19, after a class was cut from above one:
# `test_addresser.py` ran 18 tests directly and 67 under discovery, and five
# more files had the same shape. 20 runners deleted, 184 lines with them.
uv run python -m unittest discover -s tests -k test_addresser
uv run python -m unittest discover -s tests -k TestEachFoliatorCountsItsOwnSteps
uv run python -m unittest discover -s tests -k test_the_MODULE_has_an_a_and_NEVER_a_c

# Stage 3 inbound: which tracked files NAME the files under review
uv run python plugins/comment-review/skills/comment-review/scripts/referrers.py --repo . <paths...>

# Stage 5 gate: join reviewer reports against the census, check every citation.
# Each report file is NAMED FOR ITS ROLE -- the tool takes the role name from
# the file stem, and --reviewers compares against those stems.
uv run python plugins/comment-review/skills/comment-review/scripts/verdicts.py \
  --census <census>.json --repo . \
  --reviewers ownership-context,block-context,function-context,module-context \
  ownership-context.md block-context.md function-context.md module-context.md

# Stage 4 gate: the dispatch packet
uv run python plugins/comment-review/skills/comment-review/scripts/run_context.py --template
uv run python plugins/comment-review/skills/comment-review/scripts/run_context.py --check <file>

# Stage 7b gate: prove WRITE changed no executable code
uv run python plugins/comment-review/skills/comment-review/scripts/prove_unchanged.py \
  --base <merge-base> --repo . <paths...>

# The TODO backlog is WRITTEN BY A TOOL, not by hand -- see "The TODO backlog" below.
# `.claude/skills/todo-tool/SKILL.md` holds every command; these are the two run most.
uv run python scripts/todo_tool.py list [--owner T] [--status S] [--requires-roy]
uv run python scripts/todo_tool.py resync     # after a merge, before trusting any count

# Lint (ruff config lives in pyproject.toml; corpora/** is excluded from linting)
ruff check .
ruff format .

# Gate check: refuse to ship a plugins/ file that won't parse on the floor interpreter (py3.11).
# Run AFTER `ruff format`.
uv run python scripts/check_shipped_syntax.py

# The SHIPPED vocabulary holds: every key a role is given has a definition, no definition is
# written for nobody, and no role is given a term its own text never uses. Run after any edit
# to an agent file or a reference.
uv run python scripts/check_vocabulary.py

# What one agent is GIVEN. The task agent runs this at stage 4 and pastes the output verbatim.
uv run python plugins/comment-review/skills/comment-review/scripts/vocabulary.py --reviewer block-context
uv run python plugins/comment-review/skills/comment-review/scripts/vocabulary.py --roles

# Terms of art in the shipped tree the inventory does not list. An INPUT, not a gate:
# every row needs a human to say whether it is a term.
uv run python scripts/vocabulary_sweep.py

# Release gate no test replaces: the parser the RUNTIME uses on every frontmatter.
# Run it before tagging -- see "Cutting a release" below.
claude plugin validate plugins/comment-review
```

Tests are stdlib `unittest` with per-language fixtures under `tests/fixtures/`;
there are no third-party test dependencies, matching the plugin's own
stdlib-only rule. `evals/grade_hazards.py` remains the end-to-end grade, and
`scripts/check_shipped_syntax.py` the shipped-syntax floor.

## Architecture

### The skill's 8 stages

`plugins/comment-review/skills/comment-review/SKILL.md` is the task agent's own instructions --
read it before touching the skill. The pipeline:

```
1 PROJECT      2 COLLATE    3 FIND      4 MARK   5 APPLY  6 COMPACT   7a PRESENT   8 REVIEW
  DETERMINATION             REFERENCES               |                    7b WRITE
                                                      +---- no cap --------^
```

1. **PROJECT DETERMINATION** (task agent) -- scope from the merge base, find the repo's cap/width
   conventions, doc style, `move` destination, style sheet, verify reviewer agents resolve, probe
   for a language server, decide the name-corpus source.
2. **COLLATE** (`page.py` builds each page, `census.py` stacks them) -- every line classified, in order -- code, part-code, comment, docstring. Each paragraph is addressed by the subject its prose answers to: a gap between two lines of code, a declaration's documentation, or the room beside a line.
3. **FIND REFERENCES** (`census.py`) -- every reference each node makes, resolved (paths, symbols,
   counts).
4. **MARK** (4 reviewer agents, read-only) -- findings on the nodes. **SERIAL in two rounds:
   `ownership-context` alone at 4a, the other three in one message at 4c against its
   resolved placement.** One role REQUIRED, three OPTIONAL -- a claim attached to the wrong
   scope is measured against the wrong code, and the other three cannot notice.
5. **APPLY** (task agent) -- one verdict per block, full-length replacement text.
6. **COMPACT** (task agent) -- cut to the cap; skipped entirely if there is no cap.
7. **APPROVAL** -- present the final text and stop (7a); on approval, apply verbatim (7b).
8. **REVIEW** (task agent) -- read the finished page against itself.

The seven verdicts (`clean`, `query`, `drop`, `correct`, `patch`, `add`,
`move`) and the checkable/necessary matrix that resolves them are defined in SKILL.md -- read it
rather than re-deriving the rules here, since it is the single source and this file must not
restate it.

### The four editorial roles

Each is a separate namespaced plugin agent (`comment-review:comment-review-*`) under
`plugins/comment-review/agents/`. **`ownership-context` runs ALONE and FIRST**; the other
three go in one message so they run concurrently and see nothing of each other:

- **ownership-context** -- does this comment belong to the ANCHOR it sits on?
- **block-context** -- is every claim in this block true of the code it sits with -- its state
  (not past, not future), its constraints (value, direction, units, boundary), its worked
  examples?
- **function-context** -- does the commentary match what the function is for?
- **module-context** -- do the comments say this module is one set of ideas?

Reviewers are read-only and never see SKILL.md directly; they read the shared
`references/reviewer-brief.md`. Fixing what you find destroys the finding -- MARK and APPLY are
deliberately separate stages/actors.

### The census -- the only thing the reviewers depend on

It is built from the stdlib alone (no third-party dependency), at a per-language tier,
across four modules that each announce ONE subject:

| module | owns |
| --- | --- |
| `addresser.py` | names places -- the foliators walk out, `Foliation` reads back. The LEAF: it knows nothing about a paragraph |
| `page.py` | ONE FILE -- its paragraphs tied to the places on it. `page_for()` builds one; a page names its own places |
| `census.py` | every page in scope, formatted for the agents |
| `repo.py` | what the checkout says: git, the filesystem, the exception tuples |

`annotate.py` is stage 3, the resolution a reviewer would otherwise do by hand.
Each announces ONE subject, which is what `module-context` asks of any module:

| tier        | needs                                 | answers                         | cannot answer     |
| ----------- | ------------------------------------- | ------------------------------- | ----------------- |
| `tokenized` | a lexer + AST (Python, stdlib)        | blocks, marks, docstring owners | a comment's owner |
| `lexical`   | a comment-syntax record, nothing else | blocks, marks                   | any owner         |

A language with no record is named and the census EXITS NONZERO: every file handed in is
censused or the run stops. Adding a language is a data row, not new code. Only a STRUCTURAL doc
carries an anchor, and only Python has one; every other anchor comes from a reviewer reading
the file, or from an LSP `documentSymbol` enrichment when a language server answered stage 1.7's
probe. Every ownership-context verdict therefore rests on a reviewer reading the file.

`references/` under the skill directory (`write.md`, `compact.md`, `residue-check.md`,
`review.md`, `reviewer-brief.md`) are each single-sourced for one stage -- nothing pastes their
content elsewhere, and a change to a rule belongs in exactly one of these files (or in
`docs/limitations.md` for orchestration-level rules).

### Repo layout

| path                              | what                                                                                                                                                                       |
| --------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `plugins/comment-review/`         | the shipped plugin -- `skills/`, `agents/`, manifests                                                                                                                       |
| `docs/`                           | how this system behaves today, and the rules for changing it: `addressing.md` (how a place is NAMED -- the crux, and what the line-numbered form got wrong), `parsing.md` (where census structure could come from), `limitations.md` (rules for changing the skill itself -- budget-constrained, no invented examples), `vocabulary.md` (the settled terms, and every word this system stopped using) |
| `docs/plans/`                     | RELEASE SCOPES -- what one version ships, what it does not, and which TODOs it works. !! **NOT `docs/superpowers/plans/`**, and the split is deliberate: Roy, 2026-08-19, *"I don't want to conflate the rigorous one for the less rigorous one."* A superpowers plan is written for an engineer with no context -- exact files, TDD steps, a commit per task. ! **A PLAN IS NOT A TODO**: *"Todos can remain open an indefinite amount of time and make progress as we see fit. Plans are scopes of work to be complete in one run."* Anything in a plan that does not get done is filed in `TODO/` before the plan closes |
| `evidence/`                       | the prose defects the system is measured against, and the searches scored on them: per-module probe reports over a real codebase, the triage that ranked them, `ga/ground_truth.py` and the candidate rewrites it scores. ! Nothing here describes this system's own behavior -- that is `docs/`                                                    |
| `evals/`                          | the twelve planted hazards (`evals.json`, `discriminators.md`), `grade_hazards.py`, and `generator_split.py` (the authorship split)                                        |
| `corpora/`                        | `corpora.toml` MANIFEST of pinned corpora; the trees themselves are fetched, never vendored (gitignored)                                                                   |
| `scripts/`                        | `fetch_corpora.py`, `find_llm_repos.py`, `check_shipped_syntax.py` -- none of this ships with the plugin                                                                    |
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

!! **NO HEREDOCS. NOT FOR ANYTHING.** Ruled by Roy, 2026-08-19. A heredoc (`<<'EOF'`, `<<EOF`,
`@'...'@`) puts the text through the shell before the program that needs it, and this repo's work
is almost entirely text that the shell eats: an f-string's `{}`, a regex's `\s` or `\|`, a
Windows path's `\U`, an escape sequence, a `!`. It has broken every one of those in a single
session -- including a `sed` that silently produced `[\w./\-]+` from `[\w.:/\\-]+`, which is the
worst kind, because the command SUCCEEDED.

**What to do instead:**

| the job | the tool |
| --- | --- |
| change a file | `Edit` / `Write` |
| a multi-step or repeated edit | `Write` a `.py` script under the job's tmp dir, then `uv run python` it |
| a commit message | `Write` it to a file, then `git commit -F <file>` |
| file content in a test fixture | `Write` |

! **The rule is about the SHELL, not about scripting.** A Python script that does the same edits
is fine and is usually better -- it fails loudly on a bad assumption (`assert old in t`) where a
`sed` writes something plausible and moves on.

- Grade a comment-review run from its **diff**, never from its own report -- self-reported
  confidence has been measured to not discriminate real from fabricated findings.
- `docs/limitations.md` governs changes to the skill's prose/rules themselves: every example
  used there must be invented (never a real quotation), each new rule should replace an
  existing one at budget rather than accumulate, and a rule belongs in exactly one file.
- If you are **preparing making edits to code and not in a branch "ASK"** if you should be.
  The git history on main contains work that should have been branch work because we decided
  to start implementing before realizing we were corrections to code that belongs on a branch
  first.

### !! THE TODOs ARE THE JOB BOARD. PLANS ARE HOW WE MARK THEM OFF.

Roy, 2026-08-19: *"the todos are the job board -- plans are how we mark them off."*

| | `TODO/` | `docs/plans/` |
| --- | --- | --- |
| holds | every piece of work known to be wanted | one release's scope |
| lifetime | **indefinite.** Progress as we see fit | **one run.** It closes |
| answers | *what is there to do* | *what is this version doing about it* |

!! **EVERY FINDING GETS A TODO -- an existing one it fits, or its own.** A finding recorded only
in a plan dies when the plan closes, and one recorded only in a session transcript was never
recorded at all. **The plan then NAMES the TODOs it works**, so the two can see each other.

!! **A PLAN THAT NAMES NO TODO CANNOT BE CLOSED FROM EITHER END** -- the backlog cannot see the
work scheduled against it, and the plan cannot see the work already filed. Audited 2026-08-19 on
`two-live-runs-proposed-fifteen-changes.md`: **0 of 15 tasks named the TODO they close**, three
were named in a `Related` section only, and one of those was already completed -- so the scope
pointed at finished work as though it were pending.

!! **AND THIS IS TWO TRACKERS THAT CAN DRIFT, KNOWINGLY.** Roy: *"I know this is two ways of
tracking work which can get them out of sync."* The rule that keeps them honest is one-directional
-- **a plan cites TODOs; a TODO never cites a plan** -- so a closed plan leaves the backlog intact
and no TODO is left pointing at something that no longer exists.

!! **A PLAN CARRIES CHECKBOXES, THE SAME AS A TODO.** Roy, 2026-08-19: *"Just because they are
not todos doesn't mean they are freeform either."* **The release gate is every box on the plan
ticked** -- *"we will get to the release readiness at the time when it is ready to be released"*,
which sounds ontological and is not. It says readiness is **COUNTABLE** and **VERIFIABLE BY
ANYONE**, not self-defining:

- nobody has to JUDGE whether a version is ready
- nobody can DECIDE that it is
- and **anyone can check that it is** -- including someone who did none of the work

! **The third is what makes the first two hold.** A box that only its author can verify is a
judgement wearing a checkbox. Each box therefore NAMES the TODO it works, the TODO names the
work, and the work is in the tree -- so a ticked box is re-derivable by a stranger, which is the
same standard this repo applies to a comment: *if a sentence cannot be falsified by reading the
code or re-running a command, it does not belong.*

!! **AND THIS IS WHAT LETS AN AGENT STOP ASKING "IS IT READY".** Roy, 2026-08-19: *"even though
I knew the scope of work I wanted and I thought you had the information on the scope of work, you
didn't -- and so would ask, because you didn't have access to what done looked like."*

! **That question is a SYMPTOM, not politeness.** *"Should we release it now?"* and *"are you
ready to release it?"* are what an agent asks when DONE exists only in someone's head. It cannot
be answered from the tree, so it gets asked of the person -- repeatedly, and usually at the worst
moment, because the agent has no way to tell whether the answer has changed since last time.
**The plan externalises DONE**, so the state is read rather than requested.

!! **IT DOES NOT REMOVE THE RULINGS, AND MUST NOT.** A `*` box is a decision only Roy can make --
whether the galley splices within a line, what `address:lines` does with a code range. Those are
asked because they are genuinely his. **Asking for a ruling is work; asking whether the work is
finished is a missing artifact.** An agent that cannot tell the two apart will either interrupt
constantly or guess at a decision that was never its own.

! **Prose in a plan is EVIDENCE for a box, never a second list of work.** A section that restates
what a box says is a place for the two to disagree.

! **`scripts/todo_tool.py` manages `TODO/` and not `docs/plans/`**, so a plan carries no
`Progress:` line -- a hand-maintained count is the arithmetic the tool exists to prevent. **The
boxes are the state.**

! **`docs/plans/` is NOT `docs/superpowers/plans/`.** The second is written for an engineer with
no context -- exact files, TDD steps, a commit per task. The first is a release scope. Roy:
*"I don't want to conflate the rigorous one for the less rigorous one."*

### The TODO backlog, and who writes it

**`scripts/todo_tool.py` writes `TODO/`. Do not hand-edit a `Progress:` line or a README row.**
Every command recomputes the counts from the boxes it just wrote, which is the thing a hand edit
gets wrong. The full command table is
[`.claude/skills/todo-tool/SKILL.md`](.claude/skills/todo-tool/SKILL.md) and is not restated
here; `resync` is what fixes drift after a merge.

! **The tool is VENDORED from `redacted_corpus` at `todo-requires-roy` REDACTED_SHA_D** and is
re-grabbed rather than maintained here, so ruff excludes it. One local patch -- the stdout
encoding guard -- says so at the patch.

!! **TWO WRITING METHODS COEXIST AND ROY KNOWS.** 2026-08-18: *"I know this is two methods of
writing the todos but right now I don't want to fix that."* The tool owns counts, rows and
status; the prose inside a file is still written by hand. Do not spend a session reconciling
them.

#### A box is a claim about whether work remains

!! **AN UNCHECKED BOX SAYS THE WORK IS STILL TO DO, and something automated now reads it.** Roy,
2026-08-18: *"a check box not-marked is left as something todo, even if it was superseded and no
longer necessary."* Measured the same day: five RESOLVED proposals held in a prose table with no
boxes made `resync` generate a README row reading `0/9` on a file a third finished.

!! **A TODO IS NEVER DELETED. IT IS SUPERSEDED AND CHECKED.** Roy, 2026-08-19: *"todos don't get
deleted they get SUPERSEDED and checked. That is going to be an addition to the tool soon."*

! **A deleted box leaves no trace that it was ever there, or why it went.** A superseded one
keeps the error legible -- which is the same reason a superseded RULING is kept beside the one
that replaced it rather than rewritten away. ! The tool has no delete command and is not getting
one; what it is getting is a way to mark this.

! It applies to a task filed in error as much as to one overtaken by better work. Removing a
mistake removes the record that it was made.

| the task is | the box | the file's `Status:` |
| --- | --- | --- |
| **done** | `[x]` | -- |
| **superseded** -- overtaken, no longer necessary | `[x]` | -- |
| **superseded IN PART**, remainder still wanted | `[ ]`, tracking the remainder | -- |
| **deferred** -- waiting on a named event | `[ ]` | say what it waits on |
| not started | `[ ]` | -- |

! **Deferred is not done.** Roy, 2026-08-18: *"Deferred is not done - just waiting so its status
is still correct."* Waiting on an event is work not started, which is what an unchecked box
already says.

! **`in-progress` means some boxes are ticked** -- not blocked, not waiting on a ruling. A file
where only a RULING has landed is `in-progress`, because a ruling is work.

! **A superseded ARGUMENT is not a superseded task.** Reasoning kept so an error stays legible
carries no box at all; only work does.

### Cutting a release, and the version number

!! **PROPOSING A TAG IS THE MOMENT TO CHECK WHICH BRANCH YOU ARE ON.** A tag is a main-only act,
so wanting one means the work has been accumulating somewhere -- and if that somewhere is main,
it went there without the branch question ever being asked.

! **It is a better checkpoint than the rule above it**, which fires when editing STARTS. The
start is where this goes wrong: a one-line fix becomes a migration with no moment that announces
itself. Roy, 2026-08-17, after 26 commits reached main: *"your repeated asking to tag the commits
with a new version should have cued me in that you were on main."* ! Both of us had the signal
and neither read it, which is why it is written down rather than remembered.

!! **THE VERSION IS STATED THREE TIMES AND `tests/test_release.py` HOLDS THEM EQUAL.** Bump all
three in one commit, or the gate fails:

| file | field |
| --- | --- |
| `pyproject.toml` | `[project] version` |
| `CHANGELOG.md` | the newest `## [x.y.z]` heading (`[Unreleased]` is skipped -- it carries no number) |
| `plugins/comment-review/.claude-plugin/plugin.json` | `version` |

!! **ANY CHANGE UNDER `plugins/` AFTER A TAG NEEDS A NEW VERSION.** The plugin cache keys its
directory on that `version` field -- `~/.claude/plugins/cache/roy-local/comment-review/0.2.1/`
-- so a second, different tree installed under the same number overwrites the first and
`claude plugin list` reports both as the same release. Measured 2026-08-17: three commits after
`v0.2.1` was tagged and pushed, `plugins/` held a block-context whose frontmatter parsed where
the tag's did not. **Two materially different reviewers, one version number**, while another
session had already pinned an evidence package to the tag. **Never move a tag someone has
measured against; cut the next number instead.** ! The version field exists precisely to make a
run attributable, so shipping two trees under one number returns the repo to the state the
field was added to end.

! **A tag here is ANNOTATED, so `git rev-parse vX.Y.Z` returns the TAG OBJECT, not the commit.**
Use `vX.Y.Z^{}` wherever a commit is wanted -- `git diff "v0.2.1^{}" HEAD`, `git show
"v0.2.0^{}:<path>"`. This is the trap anyone re-deriving which code produced a measurement hits
first.

! **Run `claude plugin validate plugins/comment-review` before tagging.** No test replaces it:
it is the parser the runtime actually uses, and it caught a YAML frontmatter failure that had
shipped through every release to date, silently dropping a skill's whole metadata and an agent's
description. `tests/test_frontmatter.py` gates the one cause that is known; the validator is
what finds the next one.

! To publish the cut: `git tag -a vX.Y.Z -m "..."`, `git push origin main`, `git push origin
vX.Y.Z`, then `claude plugin marketplace update roy-local` and `claude plugin update
comment-review@roy-local`. **The install reads COMMITTED state**, so commit before updating, and
a session already open keeps the old agents until it restarts.

## The metaphor is EDITORIAL, and it is a rule, not decoration

**This is an editorial board.** Four **editorial roles** read a manuscript and write **editorial
marks** on it; a **PROOFREADER** reads the finished **proof** and says whether the document
deserves more marks. Think about the work that way, and take a new term from publishing -- what
would an editor, a copy desk or a proofreader call this? -- before reaching anywhere else.

! **Check a candidate against the register before proposing it, not after.** Three words entered
from LAW and each named something publishing already had a word for: `acquittal` and
`suppression` arrived with the initial plugin import and are deleted; `jurisdiction` was added
2026-08-16 by a session that checked it for collisions and never checked it for register, and is
now `remit`.

! **The register is itself an instruction, and that is the point.** Roy, 2026-08-16: *"I bet it
helps the LLM focus in on what it is doing. Because of locality and other context items the llm
will return words and phrases and comment suggestions based upon 'being' an editor better."* An
agent reads these files and then writes in them, so one consistent register is a role it can
occupy rather than a glossary it has to consult. A reader who knows the metaphor can also predict
what an unfamiliar term means instead of guessing. ! Recorded as the REASON for the rule, not as
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
- `clean` is reserved, not a synonym for "vaguely good": it is one of the seven verdicts named
  under "The skill's 8 stages" above and must not be used as a loose adjective for code or
  prose anywhere in this repo. As a verdict it means nothing to report from that role, and
  each role's `clean` asserts something specific -- read what, in that role's own file under
  `plugins/comment-review/agents/`, which states it.

## Exploration Budget

- Before a long read/grep sweep, state a one-line plan and the files you intend to inspect,
  then stop and confirm.
- Cap initial exploration at ~10 tool calls; if you still lack context, report what you
  found and ask rather than continuing to browse.
- Prefer dispatching a Task agent for open-ended codebase exploration so the main context
  stays uncluttered by the subagent's intermediate output.