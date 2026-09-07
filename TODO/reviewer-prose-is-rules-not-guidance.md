# The reviewer prose is rules and punishments, not guidance toward a good result

```
Status:   open
Progress: 1 of 9 tasks closed
Owner:    agents
Requires-Roy: false
Raised:   2026-09-06 (Roy, 2026-09-06, on reading the ownership-context agent file and
          the brief as dispatched in a live run over src/: it is so uselessly verbose it
          is disgusting; full of comments and commands about what it should not do that
          distract from the things that matter to accomplishing the goal; written as
          rules and punishments, not as something to guide towards a good result)
```

## Objective

The reviewer prose is rules and punishments, not guidance toward a good result.

## Tasks

- [ ] T1 | Measure the brief and the four role files: lines, marked lines, and
      sentences that prohibit against sentences that describe a good mark.
        > 2026-09-06 The 2026-09-06 prompt was 47,000 characters per role.
- [ ] T2 | Rewrite reviewer-brief.md to guide a role toward a good mark: what to
      read, what a finding is, then the format; each gate stated once.
- [ ] T3 | Rewrite comment-review-ownership-context.md the same way, then the
      other three role files.
- [ ] T4 | Measure the rewrite on the same target as the 2026-09-06 run: the
      same binder, the four copies compared to that run's.
        > 2026-09-06 Copies of that run: the scratchpad run-2026-09-06 directory.
        > 2026-09-07 The Sonnet ownership copy is all clean; compare to the forks' parts
- [ ] T5 | Update the brief so a role does not fork itself into sub-agents
      writing part files outside its one copy.
        > 2026-09-07 2026-09-06: all four roles forked; 0 of 3,552 slots reached a copy.
        > 2026-09-07 Sonnet run: two roles wrote 60 and 35 scripts under the scratchpad
- [ ] T6 | Measure the Sonnet ownership-context copy: clean x888 against 64
      places the Fable forks marked, two verified by grep
        > 2026-09-07 compare_oc.py lists the 64; docket_of and the #12 paste verified
- [ ] T7 | Update the clean row so it owes a reason naming what the role checked
      under its remit, so a clean certifies a read
        > 2026-09-07 Roy 2026-09-07: the system encourages skipping paragraphs
- [x] T8 | The brief says a role RETURNS one file; the script clause is gone | 51977c79 | Update
      the brief so the one-file rule governs what a role RETURNS, not every file
      it writes anywhere
        > 2026-09-07 Roy: the rule was for the source code, extended for no reason
- [ ] T9 | Update the brief's return paragraph to state the consequence plainly,
      without the shouting markers
