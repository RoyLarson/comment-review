# 31 relative links resolve nowhere, and two of them are in a live TODO

```
Status:   open
Progress: 0 of 4 tasks done
Owner:    systems
Requires-Roy: false
Raised:   2026-08-23 (2026-08-23, from scripts/dead_sweep.py --links after the history
          purge; Roy: 'not important right now')
```

## Objective

`scripts/dead_sweep.py --links` reports **31** relative markdown links that resolve to
nothing. The count is not the finding; the split is.

!! **TWO ARE NEW, AND THEY ARE IN A LIVE FILE.**
[`the-harness-cannot-run-the-system-it-grades`](the-harness-cannot-run-the-system-it-grades.md)
links `../evidence/todo-tool-full-run/` and `../evidence/todo-tool-full-v0_2/`, both removed
2026-08-23. That TODO names them as *"two complete packages, same subject, same hash"* -- the
evidence a graded case was to be built from -- so the links are load-bearing rather than
decorative, and the work they point at has to be re-described or declared gone.

! **THE OTHER 29 ARE PRE-EXISTING AND MOSTLY ARCHIVAL**: 14 in `docs/plans/0.2.4-*` naming
TODOs that have since moved into `completed/`, 11 inside `TODO/completed/*`, 4 in superpowers
plans pointing at `references/`. None was caused by the purge.

!! **AND THE REPO ALREADY HAS A STANCE ON THOSE**, stated in `dead_sweep.py` itself: *"Most of
these are a completed TODO citing a sibling that was completed after it. Fixing one means
rewriting an archived file, which this repo does not do -- read them, do not repair them."* A
completed TODO citing a sibling that later moved is not WRONG about anything; the file moved.

! **SO THE QUESTION IS NOT "FIX 31 LINKS".** It is whether the stance still holds, and what
replaces the two that the purge broke. Repairing an archived file to keep a link green is the
failure this repo names elsewhere -- editing the record so a check passes.

! `dead_sweep.py` is an INPUT and always exits 0. The pass criterion is a person reading the
list, not a green run.

## Tasks

- [ ] !! THE TWO THAT ARE NOT ARCHIVAL ROT. `the-harness-cannot-run-the-system-it-
      grades.md` links `../evidence/todo-tool-full-run/` and `../evidence/todo-
      tool-full-v0_2/`, both removed 2026-08-23. It is a LIVE todo and the links
      are load-bearing -- they were the evidence a case was to be built from. Say
      what replaces them, or say the packages are gone.
- [ ] The other 29 are PRE-EXISTING and mostly archival: 14 in
      `docs/plans/0.2.4-*` naming TODOs that have since moved to `completed/`, 11
      inside `TODO/completed/*`, 4 in superpowers plans. ! `dead_sweep.py` already
      states the stance -- 'fixing one means rewriting an archived file, which
      this repo does not do'. Confirm that stance still holds, or narrow it.
- [ ] * If archived links ARE to be repaired, rule how. A completed TODO citing a
      sibling that was completed later is not wrong about anything -- the file
      moved. A rule that rewrites the record to keep a link green is the failure
      this repo names elsewhere.
- [ ] Re-run `uv run python scripts/dead_sweep.py --links` as the check. It exits
      0 always and is an INPUT, so the pass criterion is a human reading the list,
      not a green run.
