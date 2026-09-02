# dead_sweep skips every _private name, so a dead module constant is invisible to it and to ruff

```
Status:   decision-needed
Progress: 4 of 5 tasks closed
Owner:    systems
Requires-Roy: true
Raised:   2026-08-22 (found while collapsing the Cues fields 2026-08-22:
          page._SHEBANG and page._CODING are dead and neither gate reports them)
RE-CHECKED: 2026-08-23 -- 2026-08-23. Tasks 2, 4 and 5 were resolved by other work:
            page._SHEBANG and page._CODING are deleted, and Cues.first_code_line /
            last_code_line are gone from the scripts -- the only surviving hits are the
            two test METHOD NAMES the task itself identified as prose about a gap rather
            than callers. Task 1 is a measurement and still true (dead_sweep.py:217
            skips every _private name); it belongs to the Objective, which now states
            it. ! WHAT IS LEFT IS THE RULING in task 3, and nothing else.
RE-CHECKED: 2026-08-23 -- 2026-08-23, second pass. Re-ran the greps rather than trusting
            the note: `grep -rn "_SHEBANG\|_CODING" --include=*.py plugins/ scripts/
            tests/` returns NOTHING, and `first_code_line`/`last_code_line` return only
            `tests/test_galley.py:210` and `:217`, both method NAMES. `dead_sweep.py:217`
            still reads exactly as measured. The file is well formed; only the T labels
            changed.
Split:    2026-08-23 -- no box held two tasks; the four settled boxes were shortened to
          what was settled and the ruling gained the Verify clause it was missing
```

## Objective

`dead_sweep` skips every `_private` name, so a dead module constant is invisible to it and to
ruff.

MEASURED 2026-08-22 and RE-CHECKED 2026-08-23: `dead_sweep.py:217` reads
`if name.startswith("_") or name == "main": continue`, documented at `:194-196` as deliberate --
*"`main` and any `_private` name are skipped: the first is an entry point every CLI defines and
nothing imports, the second is ruff's to see within its own file."* So no `_private` name is
ever reported by the sweep, and ruff does not see a module-level constant either -- which is
the exact gap `CLAUDE.md` cites the sweep as covering.

! **THE RULING THE SKIP NEEDS.** A `_private` name is by definition read only inside its own
module, which is what makes it CHEAPER to check, not harder -- the opposite of the reason given
for skipping `main`.

! **A SECOND BLIND SPOT, SAME CAUSE.** The sweep matches a name TEXTUALLY, so a name appearing
inside an unrelated identifier counts as a use. Measured 2026-08-22 on
`Cues.first_code_line` / `Cues.last_code_line`: their only hits were the test method names
`test_the_gap_ABOVE_the_first_code_line_inserts_above_it` and
`test_the_gap_BELOW_the_last_code_line_appends`, which are prose about a gap and never call
either method -- and the sweep reported them as held by a test. ! Both methods have since been
deleted; the two test names survive (`tests/test_galley.py:210`, `:217`) and the sweep behaviour
that mis-read them has not changed.

## Tasks

- [x] T1 | FINISHED | unknown | T1 -- MEASURED 2026-08-22, re-checked 2026-08-23
      and moved to the Objective: the sweep skips every `_private` name and
      `main`.
- [x] T2 | FINISHED | unknown | T2 -- FINISHED. `page._SHEBANG` and
      `page._CODING` are deleted; the grep over `plugins/`, `scripts/` and
      `tests/` returns nothing (2026-08-23).
- [?] T3 | T3 -- * Rule whether the `_private` skip is right, since such a name
      is cheaper to check. Verify: `dead_sweep.py:194-196` states the answer.
- [x] T4 | FINISHED | unknown | T4 -- FINISHED. The two constants were deleted
      rather than kept; see T2.
- [x] T5 | FINISHED | unknown | T5 -- MEASURED 2026-08-22 and moved to the
      Objective: the sweep matches a name TEXTUALLY, so a test METHOD NAME holds
      it.
