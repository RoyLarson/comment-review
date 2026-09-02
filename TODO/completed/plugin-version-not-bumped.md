# plugin.json still says 0.2.3 after a branch that rewrote plugins/

```
Status:   open
Progress: 3 of 3 tasks closed
Owner:    session
Requires-Roy: false
Raised:   2026-08-20 (the /code-review high of 2026-08-20)
Ruled:    2026-08-21 — 2026-08-21 -- 0.2.4-alpha, ruled by Roy: 'I don't plan to run the
          update until I release the full version, but that would keep it from colliding
          with 0.2.3 and seems like a good practice.' ! The spelling was checked rather
          than assumed: claude plugin validate accepts 0.2.4-alpha, 0.2.4alpha and
          0.2.4a0 alike, and so does uv, so neither tool was the constraint. -alpha is
          the one form BOTH semver and PEP 440 read as a pre-release, and it sorts
          before 0.2.4 in both. ! tests/test_release.py's changelog regex matched three
          numeric components only, so it would have skipped the new heading and compared
          the release below it -- widened to carry a pre-release suffix.
```

## Objective

plugin.json still says 0.2.3 after a branch that rewrote plugins/.

## Tasks

- [x] T1 | FINISHED | unknown | `plugins/comment-review/.claude-plugin/plugin.json`
      is `0.2.3` while `plugins/` changed heavily after the `v0.2.3` tag.
      CLAUDE.md: the plugin cache keys its directory on that field, so a second,
      different tree installed under the same number OVERWRITES the first and
      `claude plugin list` reports both as the same release.
- [x] T2 | FINISHED | unknown | ! CLAUDE.md also records that this exact failure
      happened before, three commits after v0.2.1 was tagged: two materially
      different reviewers, one version number, while another session had pinned
      an evidence package to the tag.
- [x] T3 | FINISHED | unknown | * RULING: which number this branch cuts. The
      version is stated in three files and `tests/test_release.py` holds them
      equal.
