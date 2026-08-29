# generator_split has been dead at import since the package move

```
Status:   in-progress
Progress: 3 of 4 tasks done
Owner:    testing
Requires-Roy: false
Raised:   2026-08-29 (2026-08-29, `ty check evals/` while wiring the harness workspace)
```

## Objective

**`evals/generator_split.py` raises before it reads an argument, and `CLAUDE.md` documents it as a
working command.** MEASURED 2026-08-29:

```
uv run python evals/generator_split.py --help
  File ".../evals/generator_split.py", line 35, in <module>
    import census
ModuleNotFoundError: No module named 'census'
```

The 2026-08-24 move put the Python in `src/comment_review/` and split the flat `census.py` across
four areas. `generator_split.py` still inserts
`plugins/comment-review/skills/comment-review/scripts` on `sys.path` and imports `census` from it
-- a path that now holds the package, not the module.

!! **IT IS A PORT, NOT A PATH FIX.** Eight names are used and they did not move together:
`_walk`, `tracked_paths`, `code_names`, `NO_HARVESTER`, `WALKED_TREE`, `path_index`,
`language_for`, `page_for`, `PARSE_ERRORS`. Some are `binder/`'s, some `concordance/`'s, and
whether each still exists under that name has to be checked one at a time.

!! **THE SAME COMMIT BROKE `scripts/vocabulary_sweep.py` THE SAME WAY** --
`vocabulary-sweep-reads-a-moved-path`, owner `systems`. **Two files, one cause, and neither was
noticed for five days.** ! Both are things nobody runs on a schedule: one is an INPUT that always
exits 0 by design, the other is used only when a corpus is being split. **A tool you reach for
occasionally is exactly the tool a reorg breaks silently.**

! **NO GATE COULD HAVE SEEN IT.** `ty check` is run against `src/comment_review/` alone -- the
command in `CLAUDE.md` names that path -- so `evals/` has never been type-checked. Pointing `ty`
at `evals/` is what found it, and is T4.

! **`ruff check .` DOES cover `evals/`, and passes**, because an import that resolves at lint time
to nothing is still syntactically fine. Linting answers a different question, which is
`docs/gates.md`'s subject.

## Tasks

- [x] T1 -- DONE 2026-08-29: TEN sites ported, not eight -- `annotate` and
      `READ_ERRORS` were missed when this was filed. Verify: `uv run python
      evals/generator_split.py . evals/workspace.py` reports a bucket table.
- [x] T2 -- CORRECTED AND DONE 2026-08-29. It read *"drop the `sys.path` insert,
      now that the package is importable"* and **the package is NOT importable**:
      `pyproject.toml` declares no build backend, so nothing is installed and
      `tests/conftest.py:63` reaches for `src/` the same way. The insert stays;
      what changed is WHICH TREE -- `src/`, not a built copy under `plugins/`.
      Verify: no `sys.path` insert in `evals/` points into `plugins/`. ! Not
      *"no file names `plugins/`"* -- `snapshot_plugin.py` names it as its whole
      subject, and `test-cases.jsonl` records pre-move paths as history.
- [ ] T3 -- Run it over a FETCHED corpus and confirm the split still reports.
      Verify: one corpus produces a trailer/non-trailer count. ! Waits on a
      corpus existing -- `corpora/` holds only `corpora.toml` today, and
      `generator_split` needs `depth = 0` because it blames.
- [x] T4 -- DONE 2026-08-29: `tests/harness/test_evals_resolve.py`, two checks --
      `ty check evals/`, and every module in `evals/` actually importing.
      Verify: MEASURED to fail -- a module with one unresolvable import turned
      both red, naming it, and both went green when it was removed.
