# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A Claude Code **plugin** (`comment-review`) plus the machinery used to develop and measure it.
The plugin is an editorial board for the comments and docstrings a change touched: four
read-only reviewer agents walk one pCST, a task agent (the `/comment-review` skill)
synthesizes verdicts, the human approves the exact replacement text, and WRITE puts it on disk and
proves the executable code byte-identical.

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
2. **COLLATE** (`census.py`) -- every interval between two lines of code gathered into one numbered tree, each comment run and docstring a node on it.
3. **FIND REFERENCES** (`census.py`) -- every reference each node makes, resolved (paths, symbols,
   counts).
4. **MARK** (4 reviewer agents, dispatched in parallel, read-only) -- findings on the nodes.
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
`plugins/comment-review/agents/`, dispatched in one message so they run concurrently:

- **ownership-context** -- does this comment belong to the ANCHOR it sits on?
- **block-context** -- is every claim in this block true of the code it sits with -- its state
  (not past, not future), its constraints (value, direction, units, boundary), its worked
  examples?
- **function-context** -- does the commentary match what the function is for?
- **module-context** -- do the comments say this module is one set of ideas?

Reviewers are read-only and never see SKILL.md directly; they read the shared
`references/reviewer-brief.md`. Fixing what you find destroys the finding -- MARK and APPLY are
deliberately separate stages/actors.

### `census.py` -- the only thing the reviewers depend on

`plugins/comment-review/skills/comment-review/scripts/census.py` builds the pCST from the
stdlib alone (no third-party dependency), at a per-language tier. It is one of three: `repo.py`
answers what the checkout says (git, the filesystem, the exception tuples) and is imported by
four scripts; `annotate.py` is stage 3, the resolution a reviewer would otherwise do by hand.
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
| `docs/`                           | how this system behaves today, and the rules for changing it: `parsing.md` (where census structure could come from), `limitations.md` (rules for changing the skill itself -- budget-constrained, no invented examples), `vocabulary.md` (the settled terms, and every word this system stopped using) |
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

- Grade a comment-review run from its **diff**, never from its own report -- self-reported
  confidence has been measured to not discriminate real from fabricated findings.
- `docs/limitations.md` governs changes to the skill's prose/rules themselves: every example
  used there must be invented (never a real quotation), each new rule should replace an
  existing one at budget rather than accumulate, and a rule belongs in exactly one file.
- If you are **preparing making edits to code and not in a branch "ASK"** if you should be.
  The git history on main contains work that should have been branch work because we decided
  to start implementing before realizing we were corrections to code that belongs on a branch
  first.

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