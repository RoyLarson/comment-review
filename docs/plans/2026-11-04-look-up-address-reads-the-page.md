# The address lookup reads the page

```
Status:   decision-needed
Progress: 0 of 7 TODO tasks closed
Plan-tasks: 0 of 7 plan tasks closed
Owner:    backend
Requires-Roy: true
Raised:   2026-11-04 (founded by move-t from 2026-10-11-lexical-readers)
```

## Objective

Looking up a place by line reads the page from the repo and never uses the
binder, as rulings #96 and #111 require

## TODO tasks this plan closes

### A - [an-empty-place-is-not-citable](../../TODO/an-empty-place-is-not-citable.md)

- [ ] T2 | Implement it. Verify: asking for the empty b place above a line of
      code answers its address
- [ ] T3 | Make bind's docstring true -- either the mechanism works, or the
      sentence stops promising it
- [ ] T5 | Make addresser --line read the page from the repo and a path, with no
      binder. Verify: a file with no prose answers its b place
- [ ] T6 | Move --check out of the address lookup command
- [ ] T7 | Rename commands/addresser to commands/look_up_address
- [ ] T8 | Update the reviewer brief's lookup command to the binderless form
- [ ] T9 | Remove HELD and ABSENT from the reviewer brief's lookup output

## Plan Tasks

- [ ] P1 | Make the lookup read the page from the repo and a path, with no
      binder
- [?] P2 | Decide where the --check verification moves
- [ ] P3 | Move --check out of the lookup command
- [ ] P4 | Rename the command to look_up_address
- [ ] P5 | Update the reviewer brief for the binderless lookup
- [ ] P6 | Make bind's docstring true
- [ ] P7 | Verify the full suite and the gates
