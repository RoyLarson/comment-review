# Lanes -- the map

**Four lanes, and a TODO's `Owner:` is one of them.** This file is the MAP; the reasoning and
the crossing rules are in [`conventions.md`](conventions.md).

| lane | owns, in one line |
| --- | --- |
| **`agents`** | **What an agent is TOLD, and how the roles hand off** |
| **`backend`** | **What the Python actually does** |
| **`testing`** | **How well the running system does, and what that is scored against** |
| **`systems`** | **Whether it installs, and whether the gates still bite** |

## Path -> lane

| path | lane |
| --- | --- |
| `plugins/comment-review/agents/**` | `agents` |
| `plugins/comment-review/skills/comment-review/SKILL.md` | `agents` |
| `plugins/comment-review/skills/comment-review/references/*.md` | `agents` |
| `docs/limitations.md` | `agents` |
| `src/comment_review/**`, `src/comment-review.py` | `backend` |
| `plugins/**/scripts/**` -- BUILT OUTPUT, edit `src/` instead | `backend` |
| `docs/addressing.md`, `docs/parsing.md` | `backend` |
| `docs/the-mark.md` -- the SOURCE for the mark's fields and classifiers | `backend` |
| `docs/the-turn.md` -- the SOURCE for what a TURN is and what closes the editorial roles | `backend` |
| `evals/**`, `evidence/**`, `corpora/**` | `testing` |
| `scripts/**` | `systems` |
| `docs/gates.md` | `systems` |
| `pyproject.toml`, `.claude-plugin/**`, `plugins/**/plugin.json` | `systems` |
| `.gitignore`, `CHANGELOG.md`, release tagging | `systems` |
| **`TODO/` as a BOARD** -- owners, splits, merges | `systems` |

## `tests/**` -> the lane that owns what the test ASKS

!! **THERE IS NO `tests/** -> testing` ROW, and there was one until 2026-08-24.** Roy:
*"if it is backend testing that is on you. If it is vocabulary and system gating tests that is
systems. Running the tests for the agents is the agents responsibility, it is testing's lane to
make the grader and keep the grades."* A test is owned by whatever it makes a claim about --
`decision-log.md Process: #5`.

| the test asks | lane | e.g. |
| --- | --- | --- |
| does this Python do what it says | `backend` | `test_record.py`, `test_page.py` |
| does a gate still bite | `systems` | `test_vocabulary.py`, `test_release.py` |
| does a role behave when run | `agents` | running the four reviewers |
| how well did the system do, scored against what | `testing` | the grader and the grades |

! **`testing`'s work is the harness branch**, not this tree's unit suite. Sending a `record.py`
regression test there is how a backend defect ends up waiting on a lane that owns the grader.

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
