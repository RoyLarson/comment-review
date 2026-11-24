# Freeform is a second pipeline run only by prose, sharing rules with no source

```
Status:   open
Progress: 1 of 3 tasks closed
Owner:    agents
Requires-Roy: false
Raised:   2026-11-23 (broken review, 2026-11-23)
```

## Objective

From the broken review of comment-review at 6a81c7b0
(feat/0.2.4-what-a-reviewer-is-handed), 2026-11-23. Evidence codes cite the
review's perspective outputs (W workflow, A architecture, D domain, I
implementation, N names, V vocabulary). The solution phase has not run; nothing
below is a recommendation.

Problem 7. Freeform is a second pipeline run only by prose, sharing rules with
no source [A-F5, W-F6, D-D6; V33]

- The split is ruled (#259-#264, #268). The shared rules already differ: five instructions vs
  seven, `source` vs `sources`, chief precedence and cap stated separately; `drop`/`add` mean
  different things at different granularity; no Python reads the freeform records.
- Executed (W): a check of a role that ignored its freeform file exited 0. A page-to-freeform
  relocation is two records linked only by free-text reasons, where page-to-page is one record.

## Tasks

- [ ] T1 | Determine one source for the rules page and freeform reviews share
        > 2026-11-23 Related: freeform-run-findings.md
- [ ] T2 | Make a page-to-freeform relocation one record, as page-to-page is
- [-] T3 | Not wanted: #411 excludes a freeform-read check | 52ca7d9bb89ade8f8f05e427420286480890f17d | Make
      check report a role that left its freeform file unread
        > 2026-11-23 check is backend Python; owner set to agents for the prose rules
