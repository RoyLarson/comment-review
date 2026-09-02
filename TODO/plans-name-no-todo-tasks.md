# Six 0.2.4 plans carry no heading naming the TODO tasks they close

```
Status:   open
Progress: 0 of 4 tasks closed
Owner:    systems
Requires-Roy: true
Raised:   2026-08-31 (2026-08-31, job-board audit run WITH --plans-dir for the first
          time: it reported 6 integrity issues where the same command without the flag
          reported 0, because the tool defaults to plans/ and this repo keeps them in
          docs/plans/)
```

## Objective

Six 0.2.4 plans carry no heading naming the TODO tasks they close.

## Tasks

- [ ] T1 | Add the `## TODO tasks this plan closes` heading to the six 0.2.4
      plans that carry none
        > 2026-08-31 Verify: audit with --plans-dir reports INTEGRITY ISSUES 0
- [ ] T2 | Add `--plans-dir docs/plans` to every `job-board` invocation in a
      tracked file
        > 2026-08-31 Verify: no tracked job-board invocation omits the flag
- [?] T3 | Decide whether a tick map belongs in a plan's own heading rather than
      in gitignored scratch
        > 2026-08-31 Two maps under .superpowers/ would be lost; it is gitignored
- [ ] T4 | Reconcile the 0.2.4 plan with the work that has landed, or supersede
      it if it cannot be
        > 2026-08-31 Roy: fixing 0.2.4 is its own task, may not be reconcilable
        > 2026-08-31 the container conversion, T26-T28, has no P step in 0.2.4
