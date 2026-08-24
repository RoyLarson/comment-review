# A UTF-8 BOM is censused as a line of code

```
Status:   open
Progress: 2 of 3 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-21 (the /code-review xhigh of 2026-08-21, focused on the file-to-
          census route)
TRIAGED:  2026-08-23 — one of three boxes is a task; the other two were a measurement
          and a statement about where BOMs come from, and are ticked into the Objective.
          The defect was RE-MEASURED live today and is unchanged.
```

## Objective

A UTF-8 BOM is censused as a line of code.

**Every reader in the file-to-census route opens with `utf-8` where it needs `utf-8-sig`:**
`repo.py:52` (`read_raw`, the one door), `census.py:336`, and `census.py:177` which hands the
text straight to `ast.parse`. `'\ufeff'.strip()` is truthy, so `code_lines` keeps the BOM as a
phantom code line.

!! **MEASURED 2026-08-23** on `'\ufeff/* Copyright 2024 */\nint x = 1;\nint y = 2;\n'` as `m.c`:

| what comes back | |
| --- | --- |
| code lines | `[1, 2, 3]` -- three, for two real ones |
| `b` places | `b0..b3`, and `b0`'s anchor is `'\ufeff'` |
| the copyright header | `c0 trailing-comment`, anchored on `'\ufeff'` -- **beside** code, not above it |

! `record.py --seed` therefore hands `block-context` a slot whose anchor is the BOM character.

! **BOM is the Visual Studio and Windows PowerShell default for `.c`, `.cs`, `.cpp` and `.ps1`**,
so this is the common case on Roy's own platform -- which is where this repo is developed. That
is why it is filed as a defect rather than as an exotic input.

! **THE PYTHON HALF IS FILED SEPARATELY AND IS WORSE.**
[`census-degrades-silently`](census-degrades-silently.md) T2 and T7 cover it: the BOM reaches
`ast.parse`, the file comes back as one `unparsed` paragraph with an EMPTY address, and the run
exits 0. ! One encoding change fixes both; two files record the two costs, because a lexical
language degrades quietly and Python degrades to nothing.

## Tasks

- [ ] T1 -- Read with `utf-8-sig` wherever the census reads source: `repo.py:52`,
      `census.py:336` and `census.py:177`. Verify, on a BOM'd `.c` holding a
      copyright header and two statements: `code_lines` answers two lines, the
      header censuses as the paragraph ABOVE the first statement and not as a
      `trailing-comment`, and no anchor is `'\ufeff'`. ! And on a BOM'd `.py`, the
      module docstring appears in the census -- the Python half, filed on
      `census-degrades-silently`.
- [x] T2 -- MEASUREMENT, not a checkpoint. The `@b0 interval ('\ufeff')` /
      `@c0 trailing-comment ('\ufeff')` result is in the Objective, re-measured
      2026-08-23.
- [x] T3 -- A statement about the platform: BOM is the Visual Studio and Windows
      PowerShell default for `.c`, `.cs`, `.cpp` and `.ps1`. True the day it was
      written and every day after; kept in the Objective as the reason this is
      the common case here.
