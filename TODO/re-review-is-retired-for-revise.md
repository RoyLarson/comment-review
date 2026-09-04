# re-review is retired for revise

```
Status:   open
Progress: 0 of 5 tasks closed
Owner:    agents
Requires-Roy: false
Raised:   2026-09-04 (Vocabulary 32, 2026-09-04 -- Roy: the re-review should be retired
          for revise)
```

## Objective

re-review is retired for revise.

## Tasks

- [ ] T1 | Update SKILL.md so stages 5b and 6b are named revises, not
      re-reviews. Verify: grep -c re-review SKILL.md is 0
- [ ] T2 | Rename references/re-review.md to revise.md and its six uses. Verify:
      no file under references/ names re-review
- [ ] T3 | Update write.md's one re-review to revise. Verify: grep re-review
      write.md is empty
- [ ] T4 | Update results/galley.py and docs/addressing.md, one use each.
      Verify: grep -rn re-review src/ docs/addressing.md is empty
        > 2026-09-04 backend lane; T1-T3 are agents; T5 is systems
- [ ] T5 | Add re-review to check_vocabulary.py RETIRED, mapped to revise, LAST.
      Verify: the gate is green the commit it lands in
        > 2026-09-04 lands last -- the gate must not go red on another lane's files
