# Does stripping a file's prose produce better comments than editing them

```
Status:   open
Progress: 0 of 5 tasks closed
Owner:    agents
Requires-Roy: true
Raised:   2026-08-30 (2026-08-30, Roy, after the collator experiment: run tests on
          whether showing a stripped version of the code leads to better comments about
          the current state)
Related:  2026-08-30 — the collator rewrite that prompted this file is at commit
          e4feba0; its report named two things the code could not say, which is the list
          task 4 asks for
```

## Objective

Does stripping a file's prose produce better comments than editing them.

## Tasks

- [ ] T1 | Define what BETTER means before running anything. Verify: the measure
      is written down first -- candidates are defects found, false claims
      avoided, and whether a reader can answer a question about the code from
      the prose alone.
- [ ] T2 | Run both arms over the same file. Verify: one agent edits the
      existing prose in place, one writes it back from a stripped file with no
      access to the original, neither sees the other's output, and both work
      from the same commit.
- [ ] T3 | Score them from the DIFF, never from either agent's own report.
      Verify: the grade names each finding and whether it is real --
      self-reported confidence has been measured in this repo not to
      discriminate a real finding from a fabricated one.
- [ ] T4 | Record what the stripped arm could NOT say. Verify: the list exists.
      On `collator.py` it was two items -- why `escalations` outranks `rereads`,
      and why `verify_report` takes one edit_copy -- and that list is what prose
      is for.
- [?] T5 | Rule whether this becomes a step in the review flow. Verify: either a
      stage names it with the conditions it runs under, or this file records why
      it stays a one-off.
