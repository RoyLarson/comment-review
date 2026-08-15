# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A Claude Code **plugin** (`comment-review`) plus the machinery used to develop and measure it.
The plugin is an editorial board for the comments and docstrings a change touched: four
read-only reviewer agents walk one prose tree, a task agent (the `/comment-review` skill)
synthesizes verdicts, the human approves the exact replacement text, and a sweep applies it and
proves the executable code byte-identical.

The repo root is **not** the plugin. Only `plugins/comment-review/` ships to a user's
`.claude/`; everything else (`docs/`, `evidence/`, `evals/`, `corpora/`, `scripts/`) is
development and measurement tooling that stays behind.

## Commands

```bash
# Run the census (stages 2-3 of the skill) over one or more files
python plugins/comment-review/skills/comment-review/scripts/census.py --repo . <paths...>
python plugins/comment-review/skills/comment-review/scripts/census.py --cap 6 --width 88 --repo . <paths...>
python plugins/comment-review/skills/comment-review/scripts/census.py --languages   # list known languages

# Materialise the pinned corpora (git worktrees / clones into corpora/<name>/, gitignored)
python scripts/fetch_corpora.py                 # fetch everything missing
python scripts/fetch_corpora.py --list          # print the manifest only
python scripts/fetch_corpora.py --only numpy pymc
python scripts/fetch_corpora.py --clean sentry --only sentry   # refetch one

# Grade a comment-review run against the twelve planted hazards, from the diff (never the report)
python evals/grade_hazards.py <worktree> [<worktree> ...]

# Split a corpus's prose defects by whether the introducing commit carries an assistant trailer
python evals/generator_split.py <corpus-dir> [paths...]

# Survey GitHub for assistant-authored repos to extend the corpus
python scripts/find_llm_repos.py --pages 3 --min-hits 2

# Lint (ruff config lives in pyproject.toml; corpora/** is excluded from linting)
ruff check .
ruff format .

# Gate check: refuse to ship a plugins/ file that won't parse on the floor interpreter (py3.9).
# Run AFTER `ruff format`.
python scripts/check_shipped_syntax.py
```

There is no test suite (`pytest` etc.) in this repo. Correctness is validated by
`evals/grade_hazards.py` against planted hazards and by `scripts/check_shipped_syntax.py` for
the shipped-syntax floor.

## Architecture

### The skill's 8 stages

`plugins/comment-review/skills/comment-review/SKILL.md` is the task agent's own instructions —
read it before touching the skill. The pipeline:

```
1 PROJECT      2 ANNOTATE   3 FIND      4 MARK   5 EDIT   6 COMPACT   7a PRESENT   8 REVIEW
  DETERMINATION             REFERENCES               │                    7b APPLY
                                                      └──── no cap ────────▲
```

1. **PROJECT DETERMINATION** (task agent) — scope from the merge base, find the repo's cap/width
   conventions, doc style, `move` destination, style sheet, verify reviewer agents resolve, probe
   for a language server, decide the name-corpus source.
2. **ANNOTATE** (`census.py`) — every comment run and docstring located as a node on a prose tree.
3. **FIND REFERENCES** (`census.py`) — every reference each node makes, resolved (paths, symbols,
   counts).
4. **MARK** (4 reviewer agents, dispatched in parallel, read-only) — findings on the nodes.
5. **EDIT** (task agent) — one verdict per block, full-length replacement text.
6. **COMPACT** (task agent) — cut to the cap; skipped entirely if there is no cap.
7. **APPROVAL** — present the final text and stop (7a); on approval, apply verbatim (7b).
8. **REVIEW** (task agent) — read the finished page against itself.

The nine verdicts (`clean`, `query`, `drop`, `correct`, `patch`, `add`, `move`, `reanchor`,
`split`) and the checkable/necessary matrix that resolves them are defined in SKILL.md — read it
rather than re-deriving the rules here, since it is the single source and this file must not
restate it.

### The four reviewer angles

Each is a separate namespaced plugin agent (`comment-review:comment-review-*`) under
`plugins/comment-review/agents/`, dispatched in one message so they run concurrently:

- **locality** — does this comment belong to the line it sits on?
- **currency** — does it describe the program as it is now (not past, not future)?
- **functionality** — does the commentary match what the function is for?
- **module-coherence** — do the comments say this module is one set of ideas?

Reviewers are read-only and never see SKILL.md directly; they read the shared
`references/reviewer-brief.md`. Fixing what you find destroys the finding — MARK and EDIT are
deliberately separate stages/actors.

### `census.py` — the only thing the reviewers depend on

`plugins/comment-review/skills/comment-review/scripts/census.py` builds the prose tree from the
stdlib alone (no third-party dependency), at a per-language tier:

| tier        | needs                                 | answers                         | cannot answer     |
| ----------- | ------------------------------------- | ------------------------------- | ----------------- |
| `tokenized` | a lexer + AST (Python, stdlib)        | blocks, marks, docstring owners | a comment's owner |
| `lexical`   | a comment-syntax record, nothing else | blocks, marks                   | any owner         |

A language with no record is reported as unreviewable, never silently skipped. Adding a language
is a data row, not new code. No comment (as opposed to docstring) carries an owner at either
tier — every locality verdict rests on a reviewer reading the file, or on an LSP `documentSymbol`
enrichment when a language server answered stage 1.7's probe.

`references/` under the skill directory (`apply.md`, `compact.md`, `residue-check.md`,
`review.md`, `reviewer-brief.md`) are each single-sourced for one stage — nothing pastes their
content elsewhere, and a change to a rule belongs in exactly one of these files (or in
`docs/limitations.md` for orchestration-level rules).

### Repo layout

| path                              | what                                                                                                                                                                       |
| --------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `plugins/comment-review/`         | the shipped plugin — `skills/`, `agents/`, manifests                                                                                                                       |
| `docs/`                           | durable guidance: `parsing.md` (where census structure could come from), `limitations.md` (rules for changing the skill itself — budget-constrained, no invented examples) |
| `evidence/`                       | why each rule exists: probe reports, a genetic search over candidate rewrites, and the triage that ranked what survived                                                    |
| `evals/`                          | the twelve planted hazards (`evals.json`, `discriminators.md`), `grade_hazards.py`, and `generator_split.py` (the authorship split)                                        |
| `corpora/`                        | `corpora.toml` MANIFEST of pinned corpora; the trees themselves are fetched, never vendored (gitignored)                                                                   |
| `scripts/`                        | `fetch_corpora.py`, `find_llm_repos.py`, `check_shipped_syntax.py` — none of this ships with the plugin                                                                    |
| `.claude-plugin/marketplace.json` | lets this checkout be installed as a plugin marketplace in the same session (`claude plugin marketplace add <path>` then `claude plugin install comment-review`)           |

### Shipped-code constraint that shapes how `census.py` and `sweep.py`-like files are written

Anything under `plugins/` is copied into other people's `.claude/` and formatted by **their**
ruff config, not this repo's — a repo targeting a newer `target-version` can rewrite valid
syntax (e.g. `except (A, B):` → PEP 758 unparenthesised form) into a `SyntaxError` on an older
interpreter, and the author of this repo never sees the failure. Consequences enforced in this
codebase:

- No `except` clause in a shipped file holds a tuple literal — every exception tuple is bound to
  a name (e.g. `READ_ERRORS`, `PARSE_ERRORS`) so there is nothing for a formatter to rewrite.
  A `noqa` was tried and does not hold, because it suppresses the report, not the rewrite.
- `pyproject.toml`'s `target-version = "py39"` protects *this repo's own* formatting only; it
  cannot protect a file after it has been copied elsewhere — `scripts/check_shipped_syntax.py`
  is the actual floor check, and it must be run after `ruff format`.

### Corpora are fetched, never vendored

`corpora/corpora.toml` pins nine repositories at specific refs (seven third-party, plus two
personal projects used as an over-fitting control), chosen for variety of prose convention. A
`local` corpus becomes a `git worktree` of a repo already on the machine; a `public` one is a
sparse clone at a tag. `corpora/*/` is gitignored — only the manifest and the fetch script are
tracked. Corpora used with `evals/generator_split.py` must be fetched with `depth = 0` (full
history) since it depends on `git blame`.

## Working on this repo

- Grade a comment-review run from its **diff**, never from its own report — self-reported
  confidence has been measured to not discriminate real from fabricated findings.
- `docs/limitations.md` governs changes to the skill's prose/rules themselves: every example
  used there must be invented (never a real quotation), each new rule should replace an
  existing one at budget rather than accumulate, and a rule belongs in exactly one file.

## Documentation Rules

- Do not write prose rules, thresholds, or assumptions into docs unless something in the code
  actually consumes them. If nothing reads it, delete it.
- Never attribute assumptions about Q unless they stated them in this session or they are
  recorded in a cited file. Cite the source inline.
- Prefer a glossary entry over repeated inline definitions.

## Exploration Budget

- Before a long read/grep sweep, state a one-line plan and the files you intend to inspect,
  then stop and confirm.
- Cap initial exploration at ~10 tool calls; if you still lack context, report what you
  found and ask rather than continuing to browse.
- Prefer dispatching a Task agent for open-ended codebase exploration so the main context
  stays clean.