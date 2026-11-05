# The address lookup reads the page

```
Status:   in-progress
Progress: 8 of 9 TODO tasks closed
Plan-tasks: 8 of 10 plan tasks closed
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
- [x] T3 | Make bind's docstring true -- either the mechanism works, or the
      sentence stops promising it
- [x] T5 | Make addresser --line read the page from the repo and a path, with no
      binder. Verify: a file with no prose answers its b place
- [x] T6 | Move --check out of the address lookup command
- [ ] T7 | Rename commands/addresser to commands/look_up_address
- [x] T8 | Update the reviewer brief's lookup command to the binderless form
- [x] T9 | Remove HELD and ABSENT from the reviewer brief's lookup output

### B - [the-cue-legend-was-never-written](../../TODO/completed/the-cue-legend-was-never-written.md)

- [x] T4 | Say how a role asks for an absent place it wants to add to

### C - [agents-files-name-the-new-cli](../../TODO/agents-files-name-the-new-cli.md)

- [x] T14 | Update SKILL.md and the brief to say absent places are filtered out
      of the binder and are looked up with addresser. Verify: both say so

## Plan Tasks

- [x] P1 | addresser --line reads the page from --repo; suite 5806 passed | c43d6fca | Make
      the lookup read the page from the repo and a path, with no binder
- [x] P2 | Ruled #278: --check is deleted, not moved | c572fb52 | Decide where
      the --check verification moves
- [x] P3 | --check and its two tests deleted | 3a1f14c7 | Move --check out of
      the lookup command
        > 2026-11-04 Ruled #278: delete --check and its two tests
- [ ] P4 | Rename the command to look_up_address
- [x] P5 | The brief asks with --repo; HELD and ABSENT are gone | 3a1f14c7 | Update
      the reviewer brief for the binderless lookup
- [x] P6 | bind's docstring: an empty place answers from the page | 3a1f14c7 | Make
      bind's docstring true
- [-] P7 | Moved last as P10, after the two steps Roy added | 356ea695 | Verify
      the full suite and the gates
- [x] P8 | --resolve reads the page from --repo | 3a1f14c7 | Make --resolve read
      the page from the repo, with no binder
- [x] P9 | The listing mode and --binder are deleted | 3a1f14c7 | Delete the
      listing mode and the --binder flag
- [ ] P10 | Verify the full suite and the gates
