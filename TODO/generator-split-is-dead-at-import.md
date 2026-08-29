# generator_split has been dead at import since the package move

```
Status:   open
Progress: 0 of 4 tasks done
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

- [ ] T1 -- Port the eight `census.*` uses to their current homes: `_walk`,
      `tracked_paths`, `code_names`, `NO_HARVESTER`, `WALKED_TREE`, `path_index`,
      `language_for`, `page_for`, `PARSE_ERRORS`. Verify: `uv run python
      evals/generator_split.py --help` exits 0.
- [ ] T2 -- Drop the `sys.path` insert pointing into `plugins/`, now that the
      package is importable. Verify: no `sys.path` line remains in `evals/`.
- [ ] T3 -- Run it over a fetched corpus and confirm the split still reports.
      Verify: one corpus produces a trailer/non-trailer count.
- [ ] T4 -- Add `evals/` to a type gate, since `ty check src/comment_review/`
      could never have seen this. Verify: the gate fails on a reverted T1.
