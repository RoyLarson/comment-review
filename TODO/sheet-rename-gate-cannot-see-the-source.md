# the sheet-rename gate reads four .md files and none of the source it was landed for

```
Status:   open
Progress: 0 of 2 tasks done
Owner:    systems
Requires-Roy: false
Raised:   2026-08-29 (the final review of feat/the-mark-and-the-collator, 2026-08-29
          (F4), filed by backend: tests/gates/test_vocabulary.py's
          test_no_agent_facing_file_calls_the_per_role_container_a_sheet scans four .md
          files, and the review ran its own regex over src/comment_review/ and the built
          copy and got 10 lines -- 5 in src/, the same 5 in plugins/. The gate was
          scoped after measuring zero offenders inside it, so it landed having never had
          one; the five in src/ were fixed by the same review's F4 and the gate still
          cannot see the next one)
```

## Objective

the sheet-rename gate reads four .md files and none of the source it was landed for.

## Tasks

- [ ] T1 | Decide what the gate reads. Verify: the decision names each root and
      says why the shipped Python is in or out, given plugins/ is BUILT from
      src/ and would report every offender twice
- [ ] T2 | Widen the gate to the roots decided. Verify: it goes RED on a file
      re- introducing the retired sense under a newly covered root, and green
      once that file is corrected
