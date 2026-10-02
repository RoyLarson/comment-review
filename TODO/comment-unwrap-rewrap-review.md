# Repair comment wrapping review findings

```
Status:   open
Progress: 0 of 5 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-02 (review)
```

## Objective

Repair comment wrapping review findings.

## Tasks

- [ ] T1 | Fix mixed-form paragraph wrapping in reading/lexer.py:196; test
      adjacent block and line comments remain comments
- [ ] T2 | Fix empty removal in reading/comment.py:23 to retain code after a
      block closer; test trailing moves and drops preserve code
- [ ] T3 | Fix decoration stripping in reading/lexer.py:196 to retain literal
      opening-line stars; test retained *ptr prose
- [ ] T4 | Rewrite reading/comment.py:23 wrap docstring to state width is a
      target; verify it describes intact long words
- [ ] T5 | Rewrite reading/comment.py:60 without_once docstring to state unique
      matching and wrapped returns; verify success and refusal paths
