# The stage-5 gate certifies a census nobody could have reviewed

```
Status:   open
Progress: 0 of 2 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-20 (the /code-review high of 2026-08-20)
```

## Objective

The stage-5 gate certifies a census nobody could have reviewed.

## Tasks

- [ ] `verdicts.py:357` `all_blocks` silently drops any paragraph whose `address`
      is falsy, so an unaddressed census yields an EMPTY accountability set. With
      a zero-record report the stage-5 gate prints `0 findings ... over 0 prose
      paragraphs` and *"Every finding is admissible. Stage 5 may rule."* at exit
      0.
- [ ] ! `galley.unanswerable` refuses that identical census BY NAME. The stage-5
      gate has no equivalent, so a census built via `page_for` -- which does not
      stamp addresses -- certifies a file nobody reviewed.
