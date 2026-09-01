# Sixteen defects in `commands/collate.py`, measured by running it

```
Status:   open
Progress: 1 of 19 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-30 (2026-08-30, a code review of `commands/collate.py` driven by
          sixteen recorded runs of the command -- no TODO on the board is a home for
          that module)
```

## Objective

Sixteen defects in `commands/collate.py`, measured on 2026-08-30 by running the
command -- sixteen recorded invocations, not a reading.

!! **THESE LAND TOGETHER, AND THE DEPENDENCY IS THE EXIT CODE.** Four of the tasks
each change what an exit code MEANS, and an exit code is the one thing the task agent
branches on -- so landing any of them alone leaves the code table half-true and the
docstring's `Returns:` list wrong in a different way than it is wrong today. The prose
and argparse tasks state that same contract, so correcting the behaviour without them
ships a module whose own description contradicts it.

## What was measured, by running it

- a run whose `--out` parent directory does not exist, and one whose `--out` names an
  existing directory, each leave `main` by `FileNotFoundError` and `PermissionError`
  with exit `None`, stdout and stderr both empty. The agent reads CPython's 1 as
  `BROKEN`, which is a different outcome
- one malformed `claim` on one place exits 1 and writes nothing: the other roles'
  reconciliation was computed and thrown away. The same run prints the address twice
  -- `block-context m.py@b1: m.py@b1: correct needs ...` -- because `Problem.message`
  already carries the `where` prefix and line 144 prefixes it again
- a run refused for `got.problems` and one refused for a missing `read_from` both
  write to stdout while the docstring says stderr; stderr was empty on both. Inherited
  rather than introduced -- `git show ac8cbbd^:src/comment_review/commands/collate.py`
- one `move` from `m.py@b1` to `m.py@b2`, both ends settled, prints `1 places
  resolved`: line 153 counts marks, calls them places, and gets the plural wrong at 1
- a synthetic `KeyError("to")` raised under `collate()` prints `REFUSED: ... a copy
  carries no 'to'` -- a false sentence about the copies, naming a key no copy carries
  at top level, with the raising frame discarded
- a copy with no `read_from` prints `REFUSED: the proof could not be reconciled -- a
  copy carries no 'read_from'` with no index and no role, where the sibling
  `MismatchedRoot` names both values
- the same copy handed to `--edit-copy` twice exits 3 with `0 places resolved` and two
  spurious re-reads, where handing it once exits 0: `action="append"` has no dedup,
  `flows.collate` overwrites `left[role]`, and `places()` groups both copies at one
  address
- `--stage` reaches nothing observable: `stage affects chief bytes: False`, `stage
  affects exit code: False`, and the module imports nothing from `desk.stages`
- `re-read m.py@b1: block-context, function-context` names a role that wrote nothing
  at that place, because `desk.collator._outcome` widens an `add`'s roles to every
  role holding a sheet for the page
- `collate --help` collapses the module docstring's worked example onto one line
  carrying a literal double backslash, and advertises `[--edit-copy PATH]` as optional
  while the code exits `UNREADABLE` without it. `collate` with no `--edit-copy` and
  `collate` over a copy that is not JSON both exit 2

! **AND THE EXIT-CODE BLOCK CONTRADICTS ITS OWN `strongest first` CLAIM**: `OK=0,
BROKEN=1, UNREADABLE=2, REREADS=3, ESCALATIONS=4, DRIFT=5` -- `DRIFT` is the weakest
outcome and holds the largest number, so `if code > 3` or any ordered comparison on
the code is wrong.

! **FIVE PROSE CLAIMS IN THIS MODULE WERE CHECKED AND HOLD**: the escalation/re-read/
drift ordering, `problems_in` reporting a missing `read_from`, `gather` raising by
design, the `DRIFT` history claim against `ac8cbbd^`, and `RECONCILE_ERRORS` bound to
a name. Everything else on the collate path was checked and cannot escape as a
traceback -- `_load`, the binder read, `json.dumps` over parsed data, and the `print`s
under `utf8_console()`.

## Tasks

- [ ] T1 | Implement a guard around the `--out` write in `commands/collate.py`,
      so a filesystem failure returns an exit code the function's own `Returns:`
      list names and a stderr line naming the path, instead of escaping as a
      traceback. Verify: a run whose `--out` parent directory does not exist,
      and a run whose `--out` names an existing directory, each return a listed
      exit code; `commands/distribute.py`'s write carries the same guard or a
      sentence saying why not. Both return NO exit code today.
- [ ] T2 | Update `commands/collate.py` so a non-empty `got.problems` does not
      discard the fold: write the chief AND report the per-role problems, which
      is the discipline `flows/collate.py:_reconcilable` exists for and records
      by name. Verify: a stage where one role's mark is malformed and three
      roles settle 30 places writes the chief and names the bad mark; the test
      goes red today, where the run exits 1 and writes nothing.
- [ ] T3 | Update the problem line `commands/collate.py` prints so the address
      appears once: `Problem.message` already carries the `where` prefix
      `desk.mark.parse` put on it, and line 144 prefixes it again. Verify: a
      malformed mark at `m.py@b1` prints the address once, not `block-context
      m.py@b1: m.py@b1: correct needs ...`.
- [ ] T4 | Update `commands/collate.py` so every `BROKEN` cause lands on the
      stream its own docstring names, or update the docstring to say which cause
      uses which. Verify: with stdout and stderr captured separately, a run
      refused for `got.problems` and one refused for a missing `read_from` each
      write their reason to the stream the `Returns:` prose states; today the
      first is on stdout and the docstring says stderr.
- [ ] T5 | Update the resolved-place count in `commands/collate.py` so it counts
      PLACES rather than marks, and does not print `1 places`. Verify: a stage
      holding one resolved `move` between two addresses prints 2, and the
      singular is used at 1; today line 153 counts marks, calls them places, and
      under-states by one per resolved move.
- [ ] T6 | Update the `RECONCILE_ERRORS` handling in `commands/collate.py` so
      only a `KeyError` naming `read_from` is reported as a copy defect and any
      other key is re-raised with its traceback intact. Verify: a
      `KeyError("to")` raised anywhere under `collate()` no longer prints
      `REFUSED: ... a copy carries no 'to'`, and a genuinely missing `read_from`
      still prints its own message.
- [ ] T7 | Implement naming the offending copy in the missing-`read_from`
      refusal, using the `args.edit_copy` paths and the loaded copies already in
      scope at that handler. Verify: a four-copy run whose third copy has no
      `read_from` prints that copy's path and its `role` field; today the
      message names no copy and a caller can only open all four.
        > 2026-09-01 MEASURED 2026-09-01 through the CLI: 'block-context m.py@b1:
        > 2026-09-01 m.py@b1: correct needs a reason'. _report prints Problem.address,
        > 2026-09-01 and the message opens with it because the assembler passed where.
- [ ] T8 | Implement a duplicate guard on `--edit-copy`, so the same path twice
      or two copies naming the same role is refused rather than folded twice.
      Verify: handing one copy holding a settled `move` twice is refused by
      name; today that run exits 3 with `0 places resolved` and two spurious
      re-reads, while the same copy handed once exits 0.
- [ ] T9 | Update `--stage` in `commands/collate.py` so its value reaches
      something observable -- validated against `desk.stages`, or carried onto
      the chief so a later step can tell a 4a fold from a 4c one. Verify:
      `--stage not-a-stage` is refused by name, or two runs differing only in
      the stage produce different chief bytes; today neither the bytes nor the
      exit code move.
- [ ] T10 | Update the docstring sentence in `commands/collate.py` claiming it
      extends `distribute`'s own 0/1/2, which is false of the sibling it names.
      Verify: `grep -n "return" src/comment_review/commands/distribute.py` gives
      `0, 2, 2, 2, 2, 0, 2` and no 1, so the sentence names a convention a grep
      confirms or names `commands/mark.py`, which carried it until `6187f71`
      renamed it and dropped the 1.
- [ ] T11 | Update the `A-T2` citation in `commands/collate.py` so it names
      something the cited file carries. Verify: `grep -rn "A-T2" TODO/` is
      non-empty and resolves, or the citation is removed; today the id lives
      only in a superpowers spec and plan, and
      `TODO/no-command-for-the-middle.md`'s boxes are unnumbered.
- [ ] T12 | Update the re-read printout prose in `commands/collate.py`, which
      says the line names every role that ruled there while
      `desk.collator._outcome` deliberately widens an `add`'s roles to every
      role holding a sheet for that page. Verify: the prose says which roles the
      line can name, and a test builds an `add` at one place and a ruling at
      another and asserts the printed set.
- [ ] T13 | Update `commands/collate.py`'s argparse so the module docstring's
      worked example survives `--help` -- `RawDescriptionHelpFormatter`, or a
      short `description=`. Verify: `collate --help` renders the example across
      lines with one backslash at each break, and a user copying it gets a
      command that runs; today the default `HelpFormatter` collapses it to one
      line carrying a literal double backslash.
- [ ] T14 | Update `--edit-copy` so argparse's usage line agrees with the code.
      Verify: `collate --help` does not advertise `[--edit-copy PATH]` as
      optional while the code exits `UNREADABLE` when none is given, or the code
      no longer refuses without it.
- [ ] T15 | Update the exit-code block in `commands/collate.py` so the numbers
      match its `strongest first` claim, or delete the claim. Verify: no
      sentence claims an ordering the numbers do not carry -- `DRIFT=5` is the
      weakest outcome and holds the largest number, so `if code > 3` or any
      ordered comparison on the code is wrong.
- [ ] T16 | Update `UNREADABLE=2` so it stops doubling as the usage-error code,
      or so its prose says it covers both. Verify: `collate` with no
      `--edit-copy` and `collate` over a copy that is not JSON are
      distinguishable by the caller, or the constant's comment states that one
      code covers an unreadable input and a usage error.
- [x] T17 | CannotCollate carries the problems out; the CLI prints them before REFUSED | 26538d2 | Update
      the refusal at `commands/collate.py:135` so it prints the problems the
      fold already computed before it exits
        > 2026-08-31 measured: one stripped read_from blocked routing for the other role
- [ ] T18 | Extend the run() helper in tests/test_collate_command.py so the
      seven tests that hand-roll its plumbing can use it
        > 2026-08-31 needs a pre-built copy list, extra argv, and the out path returned
- [ ] T19 | Update _report or the Problem builders so an address is printed
      once, not twice
