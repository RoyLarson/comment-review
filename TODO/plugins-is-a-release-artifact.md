# plugins/ is a release artifact, not a per-change gate

```
Status:   open
Progress: 4 of 7 tasks closed
Owner:    systems
Requires-Roy: false
Raised:   2026-09-05 (Roy, 2026-09-05: the build test is noise in development; a release
          command instead, and the agents and briefs in their own folder it also copies)
```

## Objective

plugins/ is a release artifact, not a per-change gate.

## Tasks

- [x] T1 | FINISHED; the suite no longer reads plugins/ against src/, its one failure is the inherited --anchor gate | 8f4be1ac | Delete
      tests/gates/test_build.py and the --check flag of scripts/build_plugin.py.
        > 2026-09-05 Verify: pytest green over an unbuilt plugins/ tree.
- [x] T2 | FINISHED; 13 renames, git log --follow reaches each | 8594f60b | Move
      the agent files, SKILL.md, references/*.md and plugin.json into
      src/plugin/, in the plugin's own shape, by git mv.
        > 2026-09-05 Verify: git log --follow reaches each moved file's history.
- [x] T3 | FINISHED; deleted and rebuilt, git status is empty | 0f9fc697 | Implement
      scripts/release.py, which rebuilds plugins/comment-review/ wholesale from
      src/plugin/ and src/comment_review/.
        > 2026-09-05 Verify: rm plugins/comment-review/, run it, git status is clean.
- [-] T4 | Roy retracted it 2026-09-05: version bumping in a command would cause issues; the release command copies and nothing else | afd3ef57 | Update
      scripts/release.py so it runs every documented release step: version,
      rebuild, validate, commit, tag, push, marketplace update.
        > 2026-09-05 Verify: --dry-run lists the steps in order and writes nothing.
        > 2026-09-05 Refuses off main or on a dirty tree, before any write.
        > 2026-09-05 Version: pyproject, plugin.json, and CHANGELOG's [Unreleased].
- [ ] T5 | Repoint every test and script that reads the shipped prose or
      plugin.json under plugins/ at src/plugin/.
        > 2026-09-05 Verify: only release.py opens a path under plugins/.
- [ ] T6 | Update CLAUDE.md, docs/lanes.md and scripts/README.md so src/plugin/
      holds the written prose and only the release command writes plugins/.
        > 2026-09-05 Verify: 'written in place' is gone from CLAUDE.md.
        > 2026-09-05 lanes.md maps src/plugin/agents/** to agents; Roy approves first.
- [ ] T7 | Supersede build-check-reads-the-working-tree T1-T4 and T6 and
      build-gate-crlf-fragile T1-T2 into this file, in one pass.
        > 2026-09-05 Verify: both files closed, each statement naming this file.
