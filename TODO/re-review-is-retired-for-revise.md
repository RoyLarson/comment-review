# re-review is retired for revise

```
Status:   open
Progress: 4 of 6 tasks closed
Owner:    agents
Requires-Roy: false
Raised:   2026-09-04 (Vocabulary 32, 2026-09-04 -- Roy: the re-review should be retired
          for revise)
```

## Objective

re-review is retired for revise.

## Tasks

- [-] T1 | SUPERSEDED -- stages 5b and 6b are gone from SKILL.md, Process 94; nothing to rename | c1b7268a | Update
      SKILL.md so stages 5b and 6b are named revises, not re-reviews. Verify:
      grep -c re-review SKILL.md is 0
- [-] T2 | SUPERSEDED -- references/re-review.md is deleted; no file under references/ names it | c1b7268a | Rename
      references/re-review.md to revise.md and its six uses. Verify: no file
      under references/ names re-review
- [-] T3 | SUPERSEDED -- write.md's line reads 'a question for the author'; no revise step exists to name | c1b7268a | Update
      write.md's one re-review to revise. Verify: grep re-review write.md is
      empty
- [ ] T4 | Update results/galley.py and docs/addressing.md, one use each.
      Verify: grep -rn re-review src/ docs/addressing.md is empty
        > 2026-09-04 backend lane; T1-T3 are agents; T5 is systems
- [ ] T5 | Add re-review to check_vocabulary.py RETIRED, mapped to revise, LAST.
      Verify: the gate is green the commit it lands in
        > 2026-09-04 lands last -- the gate must not go red on another lane's files
- [x] T6 | FINISHED -- every census in the shipped prose takes its sense; check_vocabulary reports 0 census after the build | 717a35cb | Update
      the shipped prose so every census takes its sense, gather or binder.
      Verify: check_vocabulary RETIRED counts 0 after a build
        > 2026-09-04 Vocabulary 34; commands spell gather since 68bfc548, 24b73424
        > 2026-09-04 78 uses in 10 files: SKILL.md 43, reviewer-brief 14, re-review 7
