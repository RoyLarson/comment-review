# the docket names one role per page, so two roles settling one page names neither

```
Status:   open
Progress: 0 of 3 tasks closed
Owner:    backend
Requires-Roy: true
Raised:   2026-08-29 (the final review of feat/the-mark-and-the-collator, 2026-08-29
          (F3): docket_from wrote one role per page, last-wins, so a page block-context
          and module-context each settled a place on mapped BOTH to module-context -- a
          FALSE attribution, and set_by is what a later phase (P6) routes a reversal on.
          Fixed by omitting the field on such a page, which is absent rather than wrong;
          carrying the role per ALTERATION is a change to the docket format and is this
          file)
```

## Objective

the docket names one role per page, so two roles settling one page names neither.

## Tasks

- [?] T1 | Rule whether an alteration carries its own role. Verify: the ruling
      is recorded in docs/decision-log.md, naming what docket.read requires and
      what flows.revise.pull._set_by reads
- [ ] T2 | Carry the role per alteration, if that is the ruling. Verify: a
      docket built from two roles' settled places on ONE page maps each address
      to the role that actually settled it, and docket.read refuses an
      alteration whose role is present and empty
- [ ] T3 | Retire docket_from's omission once the format carries it. Verify: no
      page a settled place reached is missing a provenance, and the test
      asserting an absent role is replaced by one asserting the right one
