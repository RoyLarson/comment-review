# render_page.py imports flat module names the 2026-08-24 reorg removed

```
Status:   open
Progress: 0 of 4 tasks done
Owner:    systems
Requires-Roy: false
Raised:   2026-08-25 (backend, 2026-08-25, while giving Page a sha during the write-
          chain branch)
```

## Objective

render_page.py imports flat module names the 2026-08-24 reorg removed.

## Tasks

- [ ] Reproduce: uv run python scripts/render_page.py <any path> and record the
      failing import
- [ ] Point its imports at comment_review.reading.lexer,
      comment_review.binder.page and comment_review.reading.addresser
- [ ] Verify the three --show modes named in CLAUDE.md still render: margin,
      prose, rows
- [ ] A gate that runs every script under scripts/ far enough to prove it imports.
      Verify: breaking one import turns it red
