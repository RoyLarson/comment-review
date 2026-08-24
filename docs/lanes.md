# Lanes -- the map

**Four lanes, and a TODO's `Owner:` is one of them.** This file is the MAP; the reasoning and
the crossing rules are in [`conventions.md`](conventions.md).

| lane | owns, in one line |
| --- | --- |
| **`agents`** | **What an agent is TOLD, and how the roles hand off** |
| **`backend`** | **What the Python actually does** |
| **`testing`** | **Whether any of it is true** |
| **`systems`** | **Whether it installs, and whether the gates still bite** |

## Path -> lane

| path | lane |
| --- | --- |
| `plugins/comment-review/agents/**` | `agents` |
| `plugins/comment-review/skills/comment-review/SKILL.md` | `agents` |
| `plugins/comment-review/skills/comment-review/references/*.md` | `agents` |
| `docs/limitations.md` | `agents` |
| `plugins/comment-review/skills/comment-review/scripts/*.py` | `backend` |
| `docs/addressing.md`, `docs/parsing.md` | `backend` |
| `tests/**` | `testing` |
| `evals/**`, `evidence/**`, `corpora/**` | `testing` |
| `scripts/**` | `systems` |
| `docs/gates.md` | `systems` |
| `pyproject.toml`, `.claude-plugin/**`, `plugins/**/plugin.json` | `systems` |
| `.gitignore`, `CHANGELOG.md`, release tagging | `systems` |
| **`TODO/` as a BOARD** -- owners, splits, merges | `systems` |

## Owned by no lane

| path | why |
| --- | --- |
| `plugins/comment-review/skills/comment-review/references/vocabulary.toml` | **shared** -- see conventions, *The vocabulary is shared* |
| `docs/vocabulary.md` | shared, same rule |
| `docs/history.md`, `docs/decision-log.md` | written by whoever received the ruling |
| `TODO/**` -- FILING one | filed by whoever found the thing, in whatever lane owns it |
| `CLAUDE.md`, `README.md`, `docs/lanes.md`, `docs/conventions.md` | repo-wide; changing a rule is a decision, not a lane's edit |

! **`docs/plans/` belongs to the release it scopes**, and a plan names the TODOs it works --
so its boxes are ticked by whichever lane owns each of those.
