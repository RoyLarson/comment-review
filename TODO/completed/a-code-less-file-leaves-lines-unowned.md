# A code-less file leaves lines owned by no paragraph

```
Status:   open
Progress: 3 of 3 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-20 (the /code-review high of 2026-08-20)
Corroborated: 2026-08-21 — the xhigh review reached the splitlines task independently and
              measured the consequence: splitlines() splits on form feed, \x85 and
              U+2028/2029, so census line numbers disagree with the file's real lines.
TRIAGED:  2026-08-23 — RE-MEASURED IN PLACE, and BOTH defects are fixed. Every line of a
          code-less file is owned; `splitlines` is gone from the reading path and
          replaced by `constants.text_lines`. The third box was never a task -- it says
          so itself -- and the work it points at belongs to `census-degrades-silently`.
          ! NOTHING IS LEFT OPEN HERE. The owner moves it to `completed/`.
```

## Objective

A code-less file leaves lines owned by no paragraph -- **and no longer does.**

!! **RE-MEASURED 2026-08-23** through `page.page_for`, counting the lines no paragraph spans:

| source | paragraphs | unowned lines |
| --- | --- | --- |
| `"""Doc."""\n\n` | `f0`/`f1` dark-matter, `b0` interval, `a0` docstring 1-1, leading 2-2 | **0** |
| `   \n\n` (whitespace only) | `f0`/`f1` dark-matter, `a0` undocumented, `b0` interval, leading 1-2 | **0** |
| `# just a note\n` | `f0` matter 1-1, `f1` dark-matter, `a0` undocumented, `b0` interval | **0** |

! **`leading` is what closed it.** The blank run is a paragraph with no address, so Roy's
invariant of 2026-08-20 -- *"every line belongs to 1 paragraph"* -- holds on a file with no code
the same way it holds on one with code.

!! **AND `splitlines` NO LONGER DECIDES WHAT A LINE IS.** `constants.text_lines`
(`constants.py:28-62`) splits on CRLF, CR and LF and nothing else, and its own docstring records
why: *"`str.splitlines()` SPLITS ON ELEVEN THINGS, and eight of them are not line endings"*, and
the 2026-08-22 measurement of a file that passed both gates and no longer compiled. Measured
2026-08-23: `splitlines` occurs nowhere in `lexer.py`; the four remaining calls are on git and
prompt output (`repo.py:122`, `referrers.py:89`, `run_context.py:239`) and in that docstring.

! **THE BARE `except Exception` IS STILL THERE and is not this file's work.** `census.py:385`
catches it under the comment *"a parse failure is REPORTED, as a gap"*, so any bug in the page
route degrades to a per-file gap rather than raising -- which is WHY the front-matter destruction
stayed quiet. That is a diagnosis, not a checkpoint: nothing states the end state, and the
degradation class is filed and owned in
[`census-degrades-silently`](census-degrades-silently.md), which carries four measured inputs and
the checkable work for each.

## Tasks

- [x] **T1 -- DONE. Every line of a code-less file is owned.** Filed against `addresser.py:426` on
      `"""Doc."""\n\n` and on a whitespace-only file. VERIFIED 2026-08-23 by running
      `page.page_for` over three code-less shapes: 0 unowned lines in each, the blanks carried by
      `leading` -- table in the objective.

- [x] **T2 -- DONE. `splitlines` is out of the reading path.** Filed against `lexer.py:1160`,
      where it split on form feed and yielded empty, uncitable addresses. `constants.text_lines`
      is now the one split (`constants.py:31`), on CRLF/CR/LF only. VERIFIED 2026-08-23:
      `grep -n splitlines` over `scripts/` returns no hit in `lexer.py` and none in any file that
      reads source.

- [x] **T3 -- NOT A TASK, and the box said so: *"Not a defect alone."*** `census.py:385` catching
      bare `Exception` is a diagnosis of why other defects stay quiet, with no state in which
      anyone ticks it. Moved to the objective above; the checkable work lives in
      `census-degrades-silently`.
