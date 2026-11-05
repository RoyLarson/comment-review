# The address lookup reads the page

```
Status:   closed
Progress: 22 of 22 TODO tasks closed
Plan-tasks: 11 of 11 plan tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-11-04 (founded by move-t from 2026-10-11-lexical-readers)
```

## Objective

Looking up a place by line reads the page from the repo and never uses the
binder, as rulings #96 and #111 require

## TODO tasks this plan closes

### A - [an-empty-place-is-not-citable](../../TODO/completed/an-empty-place-is-not-citable.md)

- [x] T2 | Implement it. Verify: asking for the empty b place above a line of
      code answers its address
- [x] T3 | Make bind's docstring true -- either the mechanism works, or the
      sentence stops promising it
- [x] T5 | Make addresser --line read the page from the repo and a path, with no
      binder. Verify: a file with no prose answers its b place
- [x] T6 | Move --check out of the address lookup command
- [-] T7 | Rename commands/addresser to commands/look_up_address
- [x] T8 | Update the reviewer brief's lookup command to the binderless form
- [x] T9 | Remove HELD and ABSENT from the reviewer brief's lookup output
- [x] T10 | Decide the lookup's subcommand names, per #279
- [x] T11 | Split the lookup command into one subcommand per question, per #279
- [x] T12 | Move the lookup's logic into a flow sharing gather's page reading,
      per #279
- [-] T13 | Update SKILL.md so stage 1 records reading settings for gather and
      the lookup, per #279
- [x] T14 | Make resolve print an empty place as its address and anchor at exit
      0, per #281
- [x] T15 | Correct the prose and docstrings that still name addresser,
      --resolve or --check
- [x] T16 | Define <stage-root> in SKILL.md's placeholder legend
- [x] T17 | Add lookup tests for a subdirectory, relative and absolute roots,
      and an escaping path
- [x] T18 | Fix the skill-commands gate reading a subcommand on a continuation
      line
- [x] T19 | Correct the false docstrings on unaddressed and page_in
- [x] T20 | Make the addresses lookup read its page through page_named, per #281
- [x] T21 | Make page_in return a page or the reason there is none
- [x] T22 | Remove the duplicated work in lines_of and the command's re-dispatch

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
- [-] P4 | SUPERSEDED by #279: subcommands, not a rename | bd77199a | Rename the
      command to look_up_address
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
- [-] P10 | Moved last as P11, after the #279 work | bd77199a | Verify the full
      suite and the gates
- [x] P11 | Suite 5804 passed, 1 skipped; ruff, format, ty, syntax, vocabulary pass | ebfe7256 | Verify
      the full suite and the gates
