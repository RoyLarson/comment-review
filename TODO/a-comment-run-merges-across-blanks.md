# A licence header and a doc comment become one paragraph with one address

```
Status:   decision-needed
Progress: 5 of 6 tasks closed
Owner:    backend
Requires-Roy: true
Raised:   2026-08-21 (the /code-review xhigh of 2026-08-21, focused on the file-to-
          census route)
TRIAGED:  2026-08-23 -- four of five were records and are ticked. ! THE ONE LIVE TASK IS
          NOW DONE: re-measured through `paragraphs_lexical`, a Rust file opening
          `// Copyright` / `// MIT` / blank / `/// Returns the name.` splits into
          `matter` 1-2 and `docstring` 4-4, which is exactly what the ruling required.
          What is left is the MIDDLE of a file, where the same merge still happens and
          the ruling does not reach -- so the file's remaining box is a RULING OWED, not
          the build it was.
```

## Objective

Same-type comments between code lines form one addressable section, including
intervening blank lines. Each a place holds one documentation section, each b
place one section in its code gap, and each c place one section beside its code
line. A blank line supplies no code anchor for another address. Line-control
requirements apply to the whole section.

Roy reaffirmed the existing rule:

> Together - without keeping them together the address system breaks because there is not code anchor to tie it together. It also doesn't conform to the line control requirements if they are split. Finally, this has been decided so many times now I do not understand why it keeps coming up as an option. The blocks go from one code line to the next code line where they are the same type of comment. All `a` series gets one, all `b` series gets one all `c` series gets one section per code line

T5 records this settled rule. The previous objective conflated same-type
comments separated by blank lines with comments of different types or
documentation ownership. Keeping the former together is required behavior. The
lexical-reader design handles form and ownership recognition separately.

T6 remains the question of whether Paragraph.lines is needed and what it counts.
It does not reopen the address or comment-section boundary rule.

## Tasks

- [x] T1 | FINISHED | unknown | T1 -- MEASURED 2026-08-21, and it is the
      finding: only CODE ends a run, so a Rust licence header, crate doc and
      item doc censused as one paragraph. In the Objective.
- [x] T2 | FINISHED | unknown | T2 -- MEASURED. `compact.md` routes on KIND, so
      a crate doc merged into a plain comment run is cut to the COMMENT cap. A
      consequence, recorded in the Objective.
- [x] T3 | FINISHED | unknown | T3 -- MEASURED. `ownership-context` gets a
      licence header plus a function's documentation as one indivisible
      paragraph at one address. In the Objective.
- [x] T4 | FINISHED | unknown | T4 -- DONE. The top-of-file split ships:
      `matter` 1-2 and `docstring` 4-4, verified 2026-08-23 through
      `paragraphs_lexical`. The filed wording is in the Objective.
- [x] T5 | Settled rule recorded in the objective and lexer spec: same-type comments stay together across blank lines | 89a6a4bb | T5
      -- * RULE whether a blank line ends a comment run in the MIDDLE of a file.
      Verify: the ruling is recorded in `docs/decision-log.md`.
        > 2026-08-31 3 in this repo's own Python -- page.py b28, mark.py b27
        > 2026-09-05 FitPlan 09-05: two places each held two paragraphs; no mark fits
        > 2026-10-11 Roy: same-type comments stay together; blank lines add no anchor.
- [?] T6 | Decide whether Paragraph.lines still has a place, given the mark changes and
      the address system carrying the text properly?
        > 2026-08-31 11 writes, 1 read -- a debug print in commands/census.py
        > 2026-08-31 == len(raw_lines) filled, 0 empty, wrong on the 3 merged runs
