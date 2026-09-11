---
name: cut-a-release
description: "Cut a comment-review release -- bump the version in its three files, assemble plugins/ with scripts/release.py, validate the plugin, then tag and publish. Use when proposing a tag, bumping the version, or publishing the plugin."
---

# Cutting a comment-review release

The prohibitions that govern a release stay in the repo's `CLAUDE.md`, under *Cutting a release,
and the version number*. This is the procedure and the reasons behind it.

## Why the branch check comes at the tag

It is a better checkpoint than the rule that fires when editing starts. The start is where this
goes wrong: a one-line fix becomes a migration with no moment that announces itself. Roy,
2026-08-17, after 26 commits reached main: *"your repeated asking to tag the commits with a new
version should have cued me in that you were on main."* Both of us had the signal and neither
read it, which is why it is written down rather than remembered.

## The version is stated three times

`tests/test_release.py` holds them equal. Bump all three in one commit, or the gate fails:

| file | field |
| --- | --- |
| `pyproject.toml` | `[project] version` |
| `CHANGELOG.md` | the newest `## [x.y.z]` heading (`[Unreleased]` is skipped -- it carries no number) |
| `src/plugin/.claude-plugin/plugin.json` | `version` |

## Why a change after a tag needs a new number

The plugin cache keys its directory on that `version` field --
`~/.claude/plugins/cache/roy-local/comment-review/0.2.1/` -- so a second, different tree installed
under the same number overwrites the first and `claude plugin list` reports both as the same
release. Measured 2026-08-17: three commits after `v0.2.1` was tagged and pushed, `plugins/` held a
block-context whose frontmatter parsed where the tag's did not. **Two materially different
reviewers, one version number**, while another session had already pinned an evidence package to
the tag. The version field exists precisely to make a run attributable, so shipping two trees
under one number returns the repo to the state the field was added to end.

## A tag here is annotated

So `git rev-parse vX.Y.Z` returns the tag object, not the commit. Use `vX.Y.Z^{}` wherever a
commit is wanted -- `git diff "v0.2.1^{}" HEAD`, `git show "v0.2.0^{}:<path>"`. This is the trap
anyone re-deriving which code produced a measurement hits first.

## Assemble, then commit what it writes

`plugins/` is a copy of `src/`, so a release cut without `uv run python scripts/release.py` ships
whatever the last run left behind -- and every gate reads `src/`, so nothing fails on a stale copy.

| | |
| --- | --- |
| assemble | `uv run python scripts/release.py` |
| then commit | `plugins/` stays tracked -- the marketplace install reads committed state |

`tests/gates/test_release_assembles.py` is what proves the command rebuilds, over a temporary
tree: a file the source dropped is removed, and bytecode does not ship.

## Validate before tagging

Run `claude plugin validate plugins/comment-review`. No test replaces it: it is the parser the
runtime actually uses, and it caught a frontmatter parse failure that had shipped through every
release to date, silently dropping a skill's whole metadata and an agent's description.
`tests/test_frontmatter.py` gates the one cause that is known; the validator is what finds the
next one.

## Publish

`git tag -a vX.Y.Z -m "..."`, `git push origin main`, `git push origin vX.Y.Z`, then
`claude plugin marketplace update roy-local` and `claude plugin update comment-review@roy-local`.
The install reads committed state, so commit before updating, and a session already open keeps
the old agents until it restarts.

-> `docs/decision-log.md`, *Process*.
