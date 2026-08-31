# A UTF-8 BOM is censused as a line of code

```
Status:   open
Progress: 2 of 4 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-21 (the /code-review xhigh of 2026-08-21, focused on the file-to-
          census route)
TRIAGED:  2026-08-23 -- one of three boxes is a task; the other two were a measurement
          and a statement about where BOMs come from, and are ticked into the Objective.
          The defect was RE-MEASURED live today and is unchanged.
SPLIT:    2026-08-23 -- the one open box held a LEXICAL outcome and a PYTHON outcome,
          which degrade differently, and is now two. Three boxes became four.
Measured: 2026-08-29 — 2026-08-29 -- NOT FIXED, but no longer SILENT. A BOM'd .py still
          reaches ast.parse with the BOM in it and still produces no censused paragraph;
          what changed is that commands/census.py now names the file and exits 1 instead
          of reporting a complete census at exit 0. MEASURED: before, a BOM'd copy of a
          nine-line control censused 0 paragraphs at exit 0 while the control censused
          11. T1 and T2 are unchanged -- the readers still open with utf-8, not
          utf-8-sig, and reading the BOM correctly is what closes this file.
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
is why it is filed as a defect rather than as an exotic input. It is true the day it was written
and every day after, which is why it is here and not in a box.

! **THE PYTHON HALF IS FILED SEPARATELY AND IS WORSE.**
[`census-degrades-silently`](census-degrades-silently.md) T2 and T7 cover it: the BOM reaches
`ast.parse`, the file comes back as one `unparsed` paragraph with an EMPTY address, and the run
exits 0. ! One encoding change fixes both; two files record the two costs, because a lexical
language degrades quietly and Python degrades to nothing. **That is also why the fix is two boxes
here: the two halves are observed on different files and fail differently.**

! **What the lexical fix must show**, kept out of the box: on a BOM'd `.c` holding a copyright
header and two statements, `code_lines` answers two, the header censuses as the paragraph ABOVE
the first statement rather than as a `trailing-comment`, and no anchor is the BOM.

## Tasks

- [ ] T1 | T1 -- Read with `utf-8-sig` at `repo.py:52` and `census.py:336`, the
      lexical route. Verify: the BOM'd `.c` shows all three results named just
      above the task list.
- [ ] T2 | T2 -- Read with `utf-8-sig` at `census.py:177`, which feeds
      `ast.parse`. Verify: a BOM'd `.py` censuses its module docstring, not one
      `unparsed` paragraph.
- [x] T3 | FINISHED | unknown | T3 -- MEASUREMENT, not a checkpoint. The `@b0
      interval` / `@c0 trailing-comment` result, both anchored on the BOM, is in
      the Objective, re-measured 2026-08-23.
- [x] T4 | FINISHED | unknown | T4 -- A statement about the platform, in the
      Objective: BOM is the Visual Studio and Windows PowerShell default for
      `.c`, `.cs`, `.cpp` and `.ps1`.
