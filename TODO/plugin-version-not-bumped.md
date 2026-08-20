# plugin.json still says 0.2.3 after a branch that rewrote plugins/

```
Status:   open
Progress: 0 of 3 tasks done
Owner:    session
Requires-Roy: true
Raised:   2026-08-20 (the /code-review high of 2026-08-20)
```

## Objective

plugin.json still says 0.2.3 after a branch that rewrote plugins/.

## Tasks

- [ ] `plugins/comment-review/.claude-plugin/plugin.json` is `0.2.3` while
      `plugins/` changed heavily after the `v0.2.3` tag. CLAUDE.md: the plugin
      cache keys its directory on that field, so a second, different tree
      installed under the same number OVERWRITES the first and `claude plugin
      list` reports both as the same release.
- [ ] ! CLAUDE.md also records that this exact failure happened before, three
      commits after v0.2.1 was tagged: two materially different reviewers, one
      version number, while another session had pinned an evidence package to the
      tag.
- [ ] * RULING: which number this branch cuts. The version is stated in three
      files and `tests/test_release.py` holds them equal.
