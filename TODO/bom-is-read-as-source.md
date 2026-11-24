# A UTF-8 BOM is censused as a line of code

```
Status:   open
Progress: 8 of 12 tasks closed
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

- [-] T1 | Superseded by #259: its language or reader left the system | e2b34a22ad36b0919b9d01cfd05bb74e80e76db9 | T1
      -- Read with `utf-8-sig` at `repo.py:52` and `census.py:336`, the lexical
      route. Verify: the BOM'd `.c` shows all three results named just above the
      task list.
- [-] T2 | SUPERSEDED by T8: concordance is shelved from the lexical plan | c0b5b211 | T2
      -- Read with `utf-8-sig` at `census.py:177`, which feeds `ast.parse`.
      Verify: a BOM'd `.py` censuses its module docstring, not one `unparsed`
      paragraph.
- [x] T3 | FINISHED | unknown | T3 -- MEASUREMENT, not a checkpoint. The `@b0
      interval` / `@c0 trailing-comment` result, both anchored on the BOM, is in
      the Objective, re-measured 2026-08-23.
- [x] T4 | FINISHED | unknown | T4 -- A statement about the platform, in the
      Objective: BOM is the Visual Studio and Windows PowerShell default for
      `.c`, `.cs`, `.cpp` and `.ps1`.
- [x] T5 | Head edits on a marked page set the mark at byte 0 and prove in the lexical, Rust and Python readers; a lost or moved mark is protected-source-changed; full suite 6432 passed | dd155ab83501f5ff98b7772a98a79094a1e89929 | Write
      the byte-order mark ahead of f0, a0 or b0 when the head is set
        > 2026-10-27 compositor.py:96, galley.py:99; proof passes a lost mark
        > 2026-10-30 Final review 3 M5: mark moves to line 2 on add f0; 338 dockets
        > 2026-10-30 Outcome 2026-10-30: edits moving the mark stay refused until T5, T6
        > 2026-10-31 Code review: a head add over a marked code line still lands
        > 2026-10-31 Code review: a head add over a marked code line still lands
- [x] T6 | BOM'd line-1 declarations have a1 and set and prove in Python and Rust (probe bom_a1.py); verified at HEAD | 67184ac1 | Give
      a declaration on a marked line 1 its a
        > 2026-10-30 A7: \ufeffclass A {} gets no a; same at 0abe0010
- [ ] T7 | Test the mark in the docstring branch at `python/projection.py:150`
- [-] T8 | SUPERSEDED by T10: the read moved to flows/gather.py:259 (parse code_names.py:66); referrers.py:62 too | 22c3a0abcbc86509c74296319ce5b719a43338ca | Read
      with utf-8-sig at concordance/code_names.py:85, which feeds ast.parse.
      Verify: a BOM'd .py is not listed as SyntaxError
- [ ] T9 | Strip the byte-order mark from a Rust line-1 doc's text, as the
      Python reader does
        > 2026-11-22 Check: a BOM'd .rs file's line-1 doc text has no U+FEFF
- [x] T10 | BOM stripped before the name harvest; test fails without it | 9cb865b1 | Read
      Python source with utf-8-sig before ast.parse at flows/gather.py:259,
      commands/referrers.py:62
        > 2026-11-22 Check: a BOM'd .py harvests its names; no SyntaxError gap row
- [ ] T11 | Strip the BOM from line-1 raw_lines before flows/proof_setter.py:598
      _reread compares them
        > 2026-11-22 Check (M19): BOM + f0 '# licence' change drafts, exit 0
- [ ] T12 | Index a derived drop on a BOM file's line 1 against BOM-free text at
      reading/comment.py:383
        > 2026-11-22 Check (M20): drop 'beta' at f0 derives '# Licence: alpha gamma'
