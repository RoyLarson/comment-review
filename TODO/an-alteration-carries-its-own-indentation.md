# An alteration carries its own indentation and nothing says so

```
Status:   open
Progress: 0 of 3 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-25 (a Task 12 review observation, 2026-08-25, reproduced on the write-
          chain branch)
```

## Objective

An alteration carries its own indentation and nothing says so.

## Tasks

- [ ] T1 | Say it in docket/docket.py's docstring: the replacement carries its
      own leading whitespace, and the galley adds none
- [ ] T2 | Decide whether the desk supplies the indentation or the agent does.
      Requires-Roy, and it decides what an alteration looks like
- [ ] T3 | A test that pins the measured behaviour -- an unindented replacement
      lands at column 0, an indented one does not. Verify: it fails if the
      galley starts adding whitespace
