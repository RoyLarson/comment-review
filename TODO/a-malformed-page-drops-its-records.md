# A page entry that is not an object loses every record under it, silently

```
Status:   open
Progress: 1 of 3 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-21 (the /code-review xhigh of 2026-08-21, focused on the file-to-
          census route)
TRIAGED:  2026-08-23 — VERIFIED LIVE at `record.py:829`, and the inconsistency is now
          plainer than when it was filed: the same function's own docstring says it
          yields a malformed RECORD on purpose, three lines above the line that drops a
          malformed PAGE in silence. The third box ended by saying the behaviour it
          described is fine, so it was never a task.
```

## Objective

A page entry that is not an object loses every record under it, silently.

!! **VERIFIED 2026-08-23.** `record.every_record` (`record.py:816-833`) does
`if not isinstance(page, dict): continue` at `:829` -- no `malformed` entry, no `--check` line,
no exit code. `verdicts.py` then has no record from that page at all, so it reports the whole
page as that reviewer's coverage gap: **the diagnostic points at the reviewer, who did the
work, instead of at the file that ate it.**

!! **THE FUNCTION ALREADY KNOWS THE RULE AND APPLIES IT ONE LEVEL DOWN.** Its own docstring,
`record.py:823-826`: *"IT YIELDS WHAT IS THERE, INCLUDING AN ENTRY THAT IS NOT AN OBJECT.
Filtering those out here made a malformed record VANISH instead of being reported."* That is the
argument for T1, written by the function against itself -- a malformed RECORD is yielded and
reported at `held.py:136`; a malformed PAGE is skipped.

! **A record under a page missing its `page` key is already handled correctly, and needs
nothing.** `held.held_records` yields `("", rec)` and the caller reports *"a record names the
place ... which is no place"* (`held.py:144`), because `addresser.address_for` returns `""` when
either half is empty -- BOTH HALVES OR NOTHING, `addresser.py:883-885`. The message sends the
fixer to the record's `place` field, which is where the fix goes.

## Tasks

- [ ] **T1 -- A page entry that is not an object is REPORTED, not skipped.** `record.py:829`
      drops it and everything under it. Verify: a seeded report holding a non-object page entry
      makes `record.py --check` print a named line and exit nonzero, `verdicts.py` names the PAGE
      rather than charging the reviewer a coverage gap, and a test pins both -- the same treatment
      `held.py:136` already gives a non-object RECORD.

- [ ] **T2 -- `held.held_records`' docstring accounts for the PAGE level.** MEASURED 2026-08-23:
      `held.py:44-46` claims *"IT YIELDS WHAT IS THERE, INCLUDING AN ENTRY THAT IS NOT AN
      OBJECT"*, which is true of a record and false of a page, since it walks `every_record` and
      inherits the skip. Verify: the docstring states what the function does at BOTH levels, and
      matches whatever T1 lands.

- [x] **T3 -- NOT A TASK.** The box described a record under a page with no `page` key and ended
      *"which is fine"* -- an observation of correct behaviour, with no state in which anyone
      ticks it. Moved to the objective, with the file:lines that make it checkable.
