# Nothing gates a module-level name that no code reads

```
Status:   open
Progress: 5 of 5 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-20 (four instances found in one session, none by a gate, 2026-08-20)
Ruled:    2026-08-21 — 2026-08-21 -- INPUT, not a gate. Roy: 'I don't think it deserves
          a gating. I do think it is a genuinely good idea to run every now and then.'
          Written to scripts/dead_sweep.py, always exits 0, registered in CLAUDE.md's
          command table beside vocabulary_sweep.py which it is modelled on. ! The gate
          case was argued and lost on its own evidence: precision depended on a grep
          confirmation step, and the two versions before it reported 32 and then 4 false
          positives. What it does have is one-sided error -- a name MENTIONED in a
          comment reads as used, so it under-reports and never invents.
```

## Objective

!! **FOUR MODULE-LEVEL NAMES WENT DEAD IN THIS REPO AND NO GATE SAID SO.** Ruff flags an unused import and an unused local; a constant or function nobody reads is invisible to it. `record.ANCHOR_SIDE` survived long enough to be found by a code-review agent READING the file, and three more died inside one session -- `OPENER`, `CODE_CONCERNS` and `PATHISH` -- each when the last thing that read it was deleted. `foliator.line_address()` was 63 lines with zero callers anywhere.

! **A dead name is not merely tidy-up.** Each of these was a claim: the file still said what the constant was FOR, so a reader -- human or agent -- learned a rule the system no longer had. That is the same defect class this plugin exists to catch, in the one place its four editorial roles cannot look.

## Tasks

- [x] T1 | FINISHED | unknown | !! RUFF CANNOT SEE THEM. It flags an unused
      IMPORT (F401) and an unused LOCAL (F841); a module-level constant or
      function that nobody reads is invisible to it. Four went dead in this repo
      -- `record.ANCHOR_SIDE` (found by a code-review agent READING the file,
      not by a gate), `record.OPENER`, `record.CODE_CONCERNS` and
      `record.PATHISH`, plus `foliator.line_address()` at 63 lines with zero
      callers anywhere.
- [x] T2 | FINISHED | unknown | The sweep that found them ran off the CodeGraph
      index: for each shipped function/class/constant, are there any
      `calls`/`references`/`instantiates` edges from outside its own file, and
      does the name appear anywhere in the tree beyond its definition. It lives
      in a scratch directory; making it a gate means writing it into `scripts/`
      beside `check_vocabulary.py`.
- [x] T3 | FINISHED | unknown | ! IT MUST COUNT SAME-FILE CALLERS. The first
      pass discounted them and reported 32 false positives -- a function reached
      only by its own module's `main` IS live, because the CLI is a consumer.
- [x] T4 | FINISHED | unknown | ! AND IT MUST GREP BEFORE BELIEVING. CodeGraph
      does not resolve a dataclass used as a type annotation, so four live
      symbols looked dead until each was grepped. A gate that cries wolf on
      `Language` and `Verdict` will be turned off.
- [x] T5 | FINISHED | unknown | * RULING WANTED: gate or input?
      `check_vocabulary.py` is a gate and `vocabulary_sweep.py` is an INPUT --
      every row needs a human to say whether it is a term. A dead-name sweep has
      the same shape: the answer is usually right and sometimes a false
      positive, which is what `vocabulary_sweep` exists to handle rather than
      refuse.
