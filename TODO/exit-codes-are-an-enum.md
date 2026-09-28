# Exit codes are written in thirteen places

```
Status:   open
Progress: 0 of 5 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-09-26 (Roy 2026-09-26)
```

## Objective

Exit codes are written in thirteen places.

## Tasks

- [ ] T1 | Implement one IntEnum of exit codes in a module under commands/,
      naming what each code means and which commands return it
        > 2026-09-26 Measured: 3 files define OK/BROKEN/UNREADABLE, 10 return bare ints
        > 2026-09-26 3 files define OK/BROKEN/UNREADABLE; 10 return bare ints
        > 2026-09-26 ASKS_THE_HUMAN = 5 lands in collate.py first (Process 197)
- [ ] T2 | Update check, collate, mark, turn and disposition to return the enum,
      deleting their own OK, BROKEN and UNREADABLE constants
- [ ] T3 | Update the ten commands that return bare 0, 1 and 2 to return the
      enum members
- [ ] T4 | Update the exits to pass the member, with .value only where
      SystemExit needs the int
- [ ] T5 | Implement a gate that fails when a command returns a bare integer or
      defines its own exit-code constant
