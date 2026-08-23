# scripts

Tooling for the corpora. Neither of these is part of the plugin -- the plugin
ships only what is under `plugins/comment-review/`.

## `fetch_corpora.py`

Materialises everything in `corpora/corpora.toml` at its pinned ref.

```bash
python scripts/fetch_corpora.py                 # fetch everything missing
python scripts/fetch_corpora.py --list          # the manifest, and nothing else
python scripts/fetch_corpora.py --only numpy pymc
python scripts/fetch_corpora.py --clean sentry --only sentry   # refetch one
```

Runs from any directory -- it anchors on the repo root, not on its own location
or your shell's.

**Nothing is copied into this repository.** A `local` corpus becomes a `git
worktree` of a repo already on the machine; a `public` one is a clone at a tag,
sparse where the manifest says so. Both land in `corpora/<name>/`, which is
gitignored.

! **A pin that does not land is a hard failure, not a warning.** The script
re-resolves each checkout against the ref the manifest names, because `--branch`
silently accepts a branch and a tag can move. A corpus that drifts makes a
regression indistinguishable from the corpus having changed underneath the
measurement.

! **`depth` matters, and `0` means full.** A shallow clone gives a tree with no
history, which is enough to census but makes `git blame` impossible -- so any
corpus used by `evals/generator_split.py` must declare `depth = 0`. Measured: a
depth-2000 fetch of sentry put **96% of blamed lines on the graft commit**, which
happened to carry an assistant trailer, so the entire pre-assistant codebase was
labelled assisted. The numbers were clean, plausible and meaningless.

## `find_llm_repos.py`

Surveys GitHub for public Python repositories whose history carries assistant
trailers (`Co-authored-by: Claude` and similar), to fill the corpus cell that is
otherwise empty: **assistant-written code that a review culture actually saw.**

```bash
python scripts/find_llm_repos.py --pages 3 --min-hits 2
GITHUB_TOKEN=... python scripts/find_llm_repos.py --pages 10
```

! **Search commits for trailers and you get the wrong answer.** Sorted by date it
returns whatever was committed most recently, which skews to solo projects making
many small commits -- the corner the corpus set already occupies. Searching
*popular repos* and asking whether each uses an assistant is the query that
works, and it found sentry (2451 trailer commits, 44.5k stars) immediately.

! A trailer proves **involvement, not authorship**. Anything this returns is a
shortlist for reading, not a corpus.

Unauthenticated GitHub search allows roughly ten requests a minute, so this is
deliberately small and slow. Set `GITHUB_TOKEN` to go faster.

## `check_shipped_syntax.py`

Refuses to ship a `plugins/` file that will not parse on Python 3.9.

```bash
python scripts/check_shipped_syntax.py    # run it AFTER `ruff format`
```

! **`pyproject.toml`'s `target-version` cannot protect the shipped file, and
believing it could is what let this through.** The plugin is copied into other
people's `.claude/` and formatted by **their** ruff config. A repo targeting
3.14 rewrites `except (A, B):` into PEP 758's unparenthesised form -- valid for
them, a `SyntaxError` for everyone on an older interpreter. The author never
sees it and the formatter never reports it; it lands on a third party.

Two things follow, and both are load-bearing:

- **Shipped code must contain nothing worth rewriting.** Every exception tuple in
  a shipped file is bound to a NAME (`GIT_ERRORS`, `READ_ERRORS`,
  `PARSE_ERRORS`, `PATH_ERRORS`), so no `except` clause holds a literal;
  `census.py` declares the ones its importers share. A `noqa` was tried first
  and did not hold -- it suppresses the report, not the rewrite.
- **The floor is asserted, not assumed.** Measured 2026-08-14: three files were
  already in the unparenthesised form, one of them the census script this skill
  hands to strangers. Confirmed by mutant -- reintroduce the construct and this
  check goes red.

## What is NOT here

Grading lives in `evals/` -- `generator_split.py` for the trailer split. It reads
a corpus; it does not fetch one. ! There is no hazard grader: it was tied to a
corpus this repo cannot ship, and rebuilding it is
`TODO/the-harness-cannot-run-the-system-it-grades.md`.
