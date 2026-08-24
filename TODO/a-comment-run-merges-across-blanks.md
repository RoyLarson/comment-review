# A licence header and a doc comment become one paragraph with one address

```
Status:   decision-needed
Progress: 4 of 5 tasks done
Owner:    backend
Requires-Roy: true
Raised:   2026-08-21 (the /code-review xhigh of 2026-08-21, focused on the file-to-
          census route)
TRIAGED:  2026-08-23 — four of five were records and are ticked. ! THE ONE LIVE TASK IS
          NOW DONE: re-measured through `paragraphs_lexical`, a Rust file opening
          `// Copyright` / `// MIT` / blank / `/// Returns the name.` splits into
          `matter` 1-2 and `docstring` 4-4, which is exactly what the ruling required.
          What is left is the MIDDLE of a file, where the same merge still happens and
          the ruling does not reach -- so the file's remaining box is a RULING OWED, not
          the build it was.
```

## Objective

A licence header and a doc comment become one paragraph with one address -- **at the top and foot
of a file, no longer; in the MIDDLE of a file, still.**

!! **RE-MEASURED 2026-08-23** through `lexer.paragraphs_lexical` on a `.rs` page:

| source | paragraphs |
| --- | --- |
| `// Copyright` / `// MIT` / blank / `/// Returns the name.` / `fn name()` | `matter` 1-2, `docstring` 4-4 -- **split** |
| `fn a() {}` / blank / `// Copyright` / `// MIT` / blank / `/// Returns the name.` / `fn b() {}` | `comment` **3-6** -- one paragraph, one address |
| `fn a() {}` / blank / `// note one` / blank / `// note two` / blank / `fn b() {}` | `comment` **3-5** -- one paragraph, one address |

**The cause is unchanged and is one line.** `flush()` decides the kind from `raw[0]` alone --
`lexer.py:1099`, `if _is_doc(raw[0], lang)` -- and only CODE ends a run, so blanks go to
`pending`. Mid-file, a `///` doc comment whose run opened with `// Copyright` is typed `comment`
and absorbed.

**The two consequences the file recorded still follow, wherever the merge happens:**

- `compact.md` routes on KIND, so a crate doc merged into a plain comment run is cut to the
  COMMENT cap.
- `ownership-context` is handed a licence header plus a function's documentation as one
  indivisible paragraph at one address, which no verdict can act on correctly.

! **AND THE FIX MOVES A PARAGRAPH BOUNDARY, NOT AN ANNOTATION.** `text` is the run with its
comment markers stripped, so a split has to go through the lexer's own construction rather than
re-deriving it afterwards. That is what made the top-of-file half real work, and it is what makes
the middle-of-file half real work too.

## Tasks

- [x] **T1 -- MEASURED 2026-08-21, and it is the finding.** Only CODE ends a run; blank lines go
      to `pending`. On a Rust file the licence header, the `//!` crate doc and the `///` item doc
      censused as ONE paragraph, lines 1-6, `kind=comment` -- because `flush()` decides from
      `raw[0]` alone. Moved to the objective as the record it is.

- [x] **T2 -- MEASURED. `compact.md` routes on KIND, so a crate doc is cut to the COMMENT cap.**
      A consequence, not a checkpoint. Recorded in the objective.

- [x] **T3 -- MEASURED. `ownership-context` is handed a licence header plus a function's
      documentation as one indivisible paragraph at one address**, which no verdict can act on
      correctly. A consequence, not a checkpoint. Recorded in the objective.

- [x] **T4 -- DONE. The top-of-file split ships.** Filed as the one live task -- *"a Rust file
      opening `// Copyright` / `// MIT` / blank / `/// Returns the name.` censuses as ONE
      paragraph over lines 1-4 ... under the ruling it must split: `f0` = 1-2, and line 4 is the
      declaration's own documentation."* VERIFIED 2026-08-23 by reading that exact source through
      `paragraphs_lexical`: `matter` 1-2 and `docstring` 4-4, two addresses. ! It went through the
      lexer's construction, as the box required.

- [ ] * **T5 -- RULE whether a blank line ends a comment run in the MIDDLE of a file.** Roy's
      2026-08-21 ruling reaches the top and foot only -- *"if the opening/closing line is a
      comment then the matter continues down/up until there is an empty line or the start/end of a
      docstring"* -- and says nothing about a run between two functions. MEASURED 2026-08-23, two
      shapes, both still one paragraph at one address: table in the objective. ! The same two
      consequences follow there, so the answer decides whether this file closes or grows a build
      task. It finishes the day Roy answers; record it in `docs/decision-log.md`.
