# render_page.py imports flat module names the 2026-08-24 reorg removed

```
Status:   open
Progress: 0 of 6 tasks done
Owner:    systems
Requires-Roy: false
Raised:   2026-08-25 (backend, 2026-08-25, while giving Page a sha during the write-
          chain branch)
Updated:  2026-08-25 — A SECOND BUG, MEASURED 2026-08-25, and fixing the imports alone
          would not reveal it. rows() at :162 shells out to plugins/comment-
          review/skills/comment-review/scripts/census.py, a path the 2026-08-24 build
          move deleted. The subprocess exits 2 with cannot open file, stdout is empty,
          and rows() returns done.stdout WITHOUT CHECKING THE RETURN CODE. The tool then
          prints rows 0 bytes 0 percent of the file. THAT IS THE ARM THE OTHER TWO ARE
          MEASURED AGAINST, so the whole comparison reads against zero. Confirmed by
          repairing the imports in a scratch COPY and running it: margin and prose
          rendered correctly at 343 and 313 bytes, rows reported 0. ! THE SHELL-OUT
          ITSELF IS RIGHT AND ITS DOCSTRING SAYS WHY -- reproducing the census format
          here would be a second implementation of the artifact being measured, and the
          untested one would be ours. Fix the path and the silence, not the approach. !
          AND THE SCRIPT ALWAYS EXITS 0 BY DESIGN because it is an input to a ruling
          rather than a gate. That governs the SCRIPT's exit code. It does not license
          printing a measurement that did not happen.
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
- [ ] rows() checks the census subprocess return code and reports the measurement
      as MISSING rather than printing 0 bytes. Verify: pointing it at a bad path
      prints a failure, not a number
- [ ] Point rows() at how the census is invoked now. Verify: all three renderings
      report non-zero bytes over a real file
