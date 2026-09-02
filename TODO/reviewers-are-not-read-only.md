# The reviewers are called read-only and are granted every tool

```
Status:   open
Progress: 0 of 4 tasks closed
Owner:    agents
Requires-Roy: false
Raised:   2026-08-25 (backend, 2026-08-25, while planning the write chain of command)
```

## Objective

The reviewers are called read-only and are granted every tool.

## Tasks

- [ ] T1 | Measure it: list every agent file with no tools: key, and state what
      each is granted today
- [ ] T2 | Decide the grant per role -- the four reviewers and
      comment-review-review read; comment-review-compact rewrites text but
      writes no file
- [ ] T3 | Declare tools: in each agent frontmatter. Verify: claude plugin
      validate passes and a role cannot Edit
- [ ] T4 | A gate that fails when a shipped agent file grants a write tool.
      Verify: adding Edit to one role turns it red
