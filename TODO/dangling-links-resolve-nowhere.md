# Relative links that resolve nowhere, and three of them are in live TODOs

```
Status:   open
Progress: 0 of 5 tasks done
Owner:    systems
Requires-Roy: false
Raised:   2026-08-23 (2026-08-23, from scripts/dead_sweep.py --links after the history
          purge; Roy: 'not important right now')
GROWING:  2026-08-23 — 2026-08-23: 31 at filing, 40 after two closures, 41 re-measured the
          same day. The count is not a stable target -- the tool defect is.
TRIAGED:  2026-08-23 — 2026-08-23. RE-MEASURED with `uv run python scripts/dead_sweep.py
          --links`: 41 links, 16 in `docs/plans/0.2.4-*`, 4 in superpowers plans, 18 in
          `TODO/completed/`, 3 in LIVE `TODO/` files. ! The live count is THREE now, not two:
          `TODO/the-census-is-mostly-intervals-nobody-rules-on.md` cites
          `verdicts-py-announces-one-subject-and-holds-four.md`, which has since moved to
          `completed/`. That is mechanism (b) happening while this file sat open. ! The old
          task 4 was the VERIFICATION METHOD rather than work and is folded into the tasks
          that use it.
```

## Objective

`scripts/dead_sweep.py --links` reports relative markdown links that resolve to nothing.
**41 as of 2026-08-23.** The count is not the finding; the split is.

MEASURED 2026-08-23, by directory of the citing file:

| where the link is written | links | what it is |
| --- | ---: | --- |
| `docs/plans/0.2.4-*` | 16 | plans naming TODOs that later moved into `completed/` |
| `TODO/completed/*` | 18 | a completed TODO citing a sibling completed after it |
| `docs/superpowers/plans/*` | 4 | pointing at `references/` |
| LIVE `TODO/*` | 3 | see below |

!! **THE THREE IN LIVE FILES ARE THE FINDING.**
[`the-harness-cannot-run-the-system-it-grades`](the-harness-cannot-run-the-system-it-grades.md)
links `../evidence/todo-tool-full-run/` and `../evidence/todo-tool-full-v0_2/` at its lines 151
and 152, both removed 2026-08-23. That TODO describes them as the first and second complete
packages -- the evidence a graded case was to be built from -- so the links are load-bearing
rather than decorative. ! And `TODO/the-census-is-mostly-intervals-nobody-rules-on.md` links
`verdicts-py-announces-one-subject-and-holds-four.md`, which is now under `completed/`.

! **THE OTHER 38 ARE PRE-EXISTING AND ARCHIVAL.** None was caused by the purge.

!! **AND THE REPO ALREADY HAS A STANCE ON THOSE**, stated in `dead_sweep.py:288-289`: *"Most of
these are a completed TODO citing a sibling that was completed after it. Fixing one means
rewriting an archived file, which this repo does not do -- read them, do not repair them."* A
completed TODO citing a sibling that later moved is not WRONG about anything; the file moved.

! **SO THE QUESTION IS NOT "FIX 41 LINKS".** It is whether the stance still holds, and what
replaces the two that the purge broke. Repairing an archived file to keep a link green is the
failure this repo names elsewhere -- editing the record so a check passes.

! `dead_sweep.py --links` is an INPUT and always exits 0 (confirmed 2026-08-23). The pass
criterion is a person reading the list, not a green run -- so every task below names what the
list must show, not that the command succeeded.

## Two mechanisms keep making these

MEASURED 2026-08-23: closing two TODOs took the count 31 -> 40.

**(a) `complete_todo` renames and rewrites nothing.** `scripts/todo_tool.py:1021` is
`src.rename(dest)`; no link in the moved file is adjusted, so every sibling it cites now needs a
`../`. ! That is a TOOL DEFECT and is fixable once, for all future closures.

**(b) live files that cited the closed one now point one directory too high.** That is the
archival pattern the stance already covers, and it is what produced the third live link above.

## Tasks

- [ ] T1 -- SAY what replaces the two evidence packages, or say they are gone.
      `TODO/the-harness-cannot-run-the-system-it-grades.md:151-152` links
      `../evidence/todo-tool-full-run/` and `../evidence/todo-tool-full-v0_2/`, both removed
      2026-08-23, and the file's line 168 quotes a number out of one of them. Verify:
      `uv run python scripts/dead_sweep.py --links` names no path under
      `TODO/the-harness-cannot-run-the-system-it-grades.md`.

- [ ] T2 -- FIX the third live link. `TODO/the-census-is-mostly-intervals-nobody-rules-on.md`
      cites `verdicts-py-announces-one-subject-and-holds-four.md`, now in `completed/`. It is a
      LIVE file citing a moved one, which the stance does not cover. Verify: `--links` names no
      path under a live `TODO/*.md`.

- [ ] * T3 -- RULE (systems) whether the stance in `dead_sweep.py:288-289` still holds for the
      38 archival links, or narrows. It finishes the day the answer is written into
      `dead_sweep.py` beside the sentence it revises.

- [ ] * T4 -- IF archived links ARE to be repaired, rule HOW. A completed TODO citing a sibling
      that was completed later is not wrong about anything -- the file moved. A rule that
      rewrites the record to keep a link green is the failure this repo names elsewhere. ! Only
      reachable if T3 narrows the stance.

- [ ] T5 -- MAKE `complete_todo` REWRITE the moved file's own relative links.
      `scripts/todo_tool.py:1021` renames and adjusts nothing, so each closure manufactures new
      dangling links from inside `completed/`. Verify: close a TODO that cites a live sibling,
      then `--links` reports no new path under `TODO/completed/<that file>`.
