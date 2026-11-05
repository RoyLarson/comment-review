# The address lookup reads the page

```
Status:   in-progress
Progress: 2 of 9 TODO tasks closed
Plan-tasks: 2 of 7 plan tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-11-04 (founded by move-t from 2026-10-11-lexical-readers)
```

## Objective

Looking up a place by line reads the page from the repo and never uses the
binder, as rulings #96 and #111 require

## TODO tasks this plan closes

### A - [an-empty-place-is-not-citable](../../TODO/an-empty-place-is-not-citable.md)

- [x] T2 | Implement it. Verify: asking for the empty b place above a line of
      code answers its address
- [ ] T3 | Make bind's docstring true -- either the mechanism works, or the
      sentence stops promising it
- [x] T5 | Make addresser --line read the page from the repo and a path, with no
      binder. Verify: a file with no prose answers its b place
- [ ] T6 | Move --check out of the address lookup command
- [ ] T7 | Rename commands/addresser to commands/look_up_address
- [ ] T8 | Update the reviewer brief's lookup command to the binderless form
- [ ] T9 | Remove HELD and ABSENT from the reviewer brief's lookup output

### B - [the-cue-legend-was-never-written](../../TODO/the-cue-legend-was-never-written.md)

- [ ] T4 | Say how a role asks for an absent place it wants to add to

### C - [agents-files-name-the-new-cli](../../TODO/agents-files-name-the-new-cli.md)

- [ ] T14 | Update SKILL.md and the brief to say absent places are filtered out
      of the binder and are looked up with addresser. Verify: both say so

## Plan Tasks

- [x] P1 | addresser --line reads the page from --repo; suite 5806 passed | c43d6fca | Make
      the lookup read the page from the repo and a path, with no binder
- [x] P2 | Ruled #278: --check is deleted, not moved | c572fb52 | Decide where
      the --check verification moves
- [ ] P3 | Move --check out of the lookup command
        > 2026-11-04 Ruled #278: delete --check and its two tests
- [ ] P4 | Rename the command to look_up_address
- [ ] P5 | Update the reviewer brief for the binderless lookup
- [ ] P6 | Make bind's docstring true
- [ ] P7 | Verify the full suite and the gates
